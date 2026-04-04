"""
训练模块 - 新项目训练功能
支持CNN完整训练和Transformer分类头训练
记录训练历史，保存评估结果
"""

import torch
import torch.nn as nn
import torch.optim as optim
from pathlib import Path
import time
import json
import shutil
from typing import Optional, Dict, Any, List
import sys

# 使用相对导入
from ..lib.model import get_model, count_parameters
from ..lib.dataset import load_eurosat_dataset
from ..lib.config import (
    NEW_MODELS_DIR,
    NEW_TRAINING_HISTORY_DIR,
    ORIGINAL_DATA_DIR,
    DEFAULT_IMAGE_SIZE,
    DEFAULT_BATCH_SIZE,
    DEFAULT_EPOCHS,
    DEFAULT_LEARNING_RATE,
    EuroSAT_CLASSES,
    NUM_CLASSES,
)
from .history import TrainingHistory, save_training_history
from .evaluation import evaluate_model, save_evaluation_results


def train_one_epoch(
    model, train_loader, criterion, optimizer, device, epoch
) -> tuple[float, float]:
    """训练一个epoch"""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    num_batches = len(train_loader)

    for batch_idx, (inputs, targets) in enumerate(train_loader):
        inputs, targets = inputs.to(device), targets.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

    accuracy = 100.0 * correct / total
    avg_loss = running_loss / num_batches
    return avg_loss, accuracy


def validate(model, val_loader, criterion, device) -> tuple[float, float]:
    """验证模型"""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    with torch.no_grad():
        for inputs, targets in val_loader:
            inputs, targets = inputs.to(device), targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)

            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += targets.size(0)
            correct += predicted.eq(targets).sum().item()

    accuracy = 100.0 * correct / total
    avg_loss = running_loss / len(val_loader)
    return avg_loss, accuracy


def format_time(seconds: float) -> str:
    """格式化时间显示"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m{secs:02d}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h{minutes:02d}m"


def train_model(
    model_key: str,
    data_dir: Optional[str] = None,
    epochs: int = DEFAULT_EPOCHS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    lr: float = DEFAULT_LEARNING_RATE,
    weight_decay: float = 0.01,
    patience: int = 10,
    image_size: int = DEFAULT_IMAGE_SIZE,
    device: Optional[str] = None,
    save_history: bool = True,
    evaluate_after_training: bool = True,
) -> Dict[str, Any]:
    """训练模型主函数"""
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"

    if data_dir is None:
        data_dir = str(ORIGINAL_DATA_DIR)

    print(f"\n{'=' * 60}")
    print(f"  模型训练: {model_key}")
    print(f"{'=' * 60}")
    print(f"设备: {device}")
    print(f"数据目录: {data_dir}")
    print(f"训练轮数: {epochs}")
    print(f"批次大小: {batch_size}")
    print(f"学习率: {lr}")
    print(f"权重衰减: {weight_decay}")
    print(f"早停耐心值: {patience if patience > 0 else '禁用'}")
    print(f"图像尺寸: {image_size}")
    print(f"{'=' * 60}\n")

    # 加载模型
    print("正在加载模型...")
    model = get_model(model_key, num_classes=NUM_CLASSES)
    model = model.to(device)

    total_params = count_parameters(model)
    print(f"模型参数总量: {total_params:,}")

    # 如果是Transformer特征提取器（仅训练分类头），冻结基础模型
    if model_key == "swin_tiny_feature":
        print("\n模式: 仅训练分类头 (Feature Extractor)")
        for name, param in model.named_parameters():
            if not name.startswith("head") and not name.startswith("base_model.head"):
                param.requires_grad = False
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(
            f"可训练参数: {trainable_params:,} ({trainable_params / total_params * 100:.2f}%)"
        )
    else:
        print(f"\n模式: 完整训练")

    # 加载数据集
    print("\n正在加载数据集...")
    train_loader, val_loader, test_loader, classes = load_eurosat_dataset(
        data_dir, image_size, batch_size
    )
    print(f"训练集: {len(train_loader.dataset)} 张图像")
    print(f"验证集: {len(val_loader.dataset)} 张图像")
    print(f"测试集: {len(test_loader.dataset)} 张图像")

    # 训练设置
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)

    # 学习率预热 + 余弦退火
    warmup_epochs = 5
    scheduler = optim.lr_scheduler.SequentialLR(
        optimizer,
        schedulers=[
            optim.lr_scheduler.LinearLR(
                optimizer, start_factor=0.1, total_iters=warmup_epochs
            ),
            optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=epochs - warmup_epochs
            ),
        ],
        milestones=[warmup_epochs],
    )

    # 早停机制
    early_stop_counter = 0
    best_current_val_acc = 0.0

    # 创建保存目录
    save_dir = NEW_MODELS_DIR / model_key
    save_dir.mkdir(parents=True, exist_ok=True)

    # 训练历史记录
    history = TrainingHistory(model_key=model_key)

    best_val_acc = 0.0
    best_model_path = save_dir / "best_model.pth"
    existing_model_path = save_dir / "existing_model_backup.pth"

    # 检查是否已有最佳模型
    if best_model_path.exists():
        print(f"\n检测到已有模型: {best_model_path}")
        print("正在评估现有模型性能...")
        existing_model = get_model(model_key, num_classes=NUM_CLASSES).to(device)
        existing_model.load_state_dict(
            torch.load(best_model_path, map_location=device, weights_only=True)
        )
        existing_model.eval()
        _, existing_best_val_acc = validate(
            existing_model, val_loader, criterion, device
        )
        best_val_acc = existing_best_val_acc
        print(f"现有模型最佳验证准确率: {best_val_acc:.2f}%")
        print(f"训练目标: 超过 {best_val_acc:.2f}%\n")
        del existing_model
    else:
        print(f"\n未检测到已有模型，从头开始训练\n")

    print(f"\n{'=' * 60}")
    print(f"  开始训练")
    print(f"{'=' * 60}\n")

    # 训练循环
    total_start_time = time.time()
    training_interrupted = False

    try:
        for epoch in range(epochs):
            epoch_start_time = time.time()

            # 显示进度
            progress = (epoch + 1) / epochs * 100
            print(f"[{epoch + 1}/{epochs}] ({progress:.1f}%)")

            train_loss, train_acc = train_one_epoch(
                model, train_loader, criterion, optimizer, device, epoch
            )
            val_loss, val_acc = validate(model, val_loader, criterion, device)

            scheduler.step()
            epoch_elapsed = time.time() - epoch_start_time
            total_elapsed = time.time() - total_start_time

            # 计算预估剩余时间
            if epoch > 0:
                avg_epoch_time = total_elapsed / (epoch + 1)
                eta = avg_epoch_time * (epochs - epoch - 1)
                eta_str = format_time(eta)
            else:
                eta_str = "计算中..."

            # 记录历史
            history.add_epoch(
                epoch=epoch + 1,
                train_loss=train_loss,
                train_accuracy=train_acc,
                val_loss=val_loss,
                val_accuracy=val_acc,
                learning_rate=optimizer.param_groups[0]["lr"],
                time_elapsed=epoch_elapsed,
            )

            # 打印详细信息
            print(f"  训练 - 损失: {train_loss:.4f}  准确率: {train_acc:.2f}%")
            print(f"  验证 - 损失: {val_loss:.4f}  准确率: {val_acc:.2f}%")
            print(f"  学习率: {optimizer.param_groups[0]['lr']:.6f}")
            print(f"  耗时: {format_time(epoch_elapsed)}  预估剩余: {eta_str}")

            # 保存最佳模型
            if val_acc > best_val_acc:
                # 如果已有旧模型，先备份
                if best_model_path.exists():
                    shutil.copy2(str(best_model_path), str(existing_model_path))
                best_val_acc = val_acc
                torch.save(model.state_dict(), best_model_path)
                print(f"  ✓ 保存最佳模型 (验证准确率: {val_acc:.2f}%)")
                best_current_val_acc = val_acc
                early_stop_counter = 0
            elif val_acc > best_current_val_acc:
                # 本轮训练的新最佳
                best_current_val_acc = val_acc
                early_stop_counter = 0
            else:
                early_stop_counter += 1

            # 早停检查
            if patience > 0 and early_stop_counter >= patience:
                print(f"\n  ⏹ 早停触发! 本轮训练最佳验证准确率连续 {patience} 轮未提升")
                break

            print()

    except KeyboardInterrupt:
        training_interrupted = True
        print(f"\n\n{'!' * 60}")
        print(f"  训练被用户中断")
        print(f"{'!' * 60}")

    total_time = time.time() - total_start_time

    # 计算完成的轮数
    completed_epochs = len(history.epochs)

    if training_interrupted:
        print(f"\n{'=' * 60}")
        print(f"  训练中断 - 保存已完成的结果")
        print(f"{'=' * 60}")
    else:
        print(f"\n{'=' * 60}")
        print(f"  训练完成")
        print(f"{'=' * 60}")

    print(f"完成轮数: {completed_epochs}/{epochs}")
    print(f"总耗时: {format_time(total_time)}")
    print(f"最佳验证准确率: {best_val_acc:.2f}%")

    # 检查是否有最佳模型
    if not best_model_path.exists():
        print("\n警告: 没有保存最佳模型，无法进行评估")
        if save_history:
            history.final_test_accuracy = 0.0
            history.best_val_accuracy = best_val_acc
            history.best_epoch = history.get_best_epoch()
            history_path = NEW_TRAINING_HISTORY_DIR / f"{model_key}_history.json"
            save_training_history(history, str(history_path))
            print(f"训练历史已保存: {history_path}")

        return {
            "model_key": model_key,
            "best_val_accuracy": best_val_acc,
            "test_accuracy": 0.0,
            "history": history.to_dict() if save_history else None,
            "model_path": str(best_model_path) if best_model_path.exists() else None,
            "save_dir": str(save_dir),
            "interrupted": training_interrupted,
            "completed_epochs": completed_epochs,
        }

    # 检查新模型是否超过旧模型
    model_surpassed = True
    if existing_model_path.exists():
        # 加载当前模型进行评估
        current_model = get_model(model_key, num_classes=NUM_CLASSES).to(device)
        current_model.load_state_dict(
            torch.load(best_model_path, map_location=device, weights_only=True)
        )
        current_model.eval()
        _, current_val_acc = validate(current_model, val_loader, criterion, device)
        del current_model

        if current_val_acc <= best_val_acc and not training_interrupted:
            model_surpassed = False
            print(
                f"\n新模型验证准确率 ({current_val_acc:.2f}%) 未超过现有模型 ({best_val_acc:.2f}%)"
            )
            print("保留现有模型和训练历史，不覆盖")
            # 恢复原有模型
            shutil.move(str(existing_model_path), str(best_model_path))
        else:
            # 新模型更好，删除备份
            existing_model_path.unlink(missing_ok=True)
            print(f"\n新模型验证准确率 ({current_val_acc:.2f}%) 超过或等于现有模型")
            print("已更新最佳模型")

    # 只有新模型超过旧模型时才保存训练历史
    if not model_surpassed:
        print("\n注意: 新模型未超过旧模型，保留原有训练历史")
        return {
            "model_key": model_key,
            "best_val_accuracy": best_val_acc,
            "test_accuracy": 0.0,
            "history": None,
            "model_path": str(best_model_path),
            "save_dir": str(save_dir),
            "interrupted": training_interrupted,
            "completed_epochs": completed_epochs,
            "model_surpassed": False,
        }

    # 加载最佳模型进行评估
    print("\n正在加载最佳模型进行测试...")
    model.load_state_dict(
        torch.load(best_model_path, map_location=device, weights_only=True)
    )

    # 测试集评估
    test_loss, test_acc = validate(model, test_loader, criterion, device)
    print(f"测试准确率: {test_acc:.2f}%")

    # 记录最终测试结果
    history.final_test_accuracy = test_acc
    history.best_val_accuracy = best_val_acc
    history.best_epoch = history.get_best_epoch()

    # 保存训练历史
    if save_history:
        history_path = NEW_TRAINING_HISTORY_DIR / f"{model_key}_history.json"
        save_training_history(history, str(history_path))
        print(f"\n训练历史已保存: {history_path}")

    # 进行全面评估（仅在训练完成时）
    if evaluate_after_training and not training_interrupted:
        print("\n正在生成评估报告...")
        eval_results = evaluate_model(model, test_loader, device, EuroSAT_CLASSES)

        # 保存评估结果
        eval_path = save_dir / "evaluation_results.json"
        save_evaluation_results(eval_results, str(eval_path))
        print(f"评估结果已保存: {eval_path}")

        # 更新历史记录中的评估信息
        history.evaluation_available = True
        history.evaluation_path = str(eval_path)
        if save_history:
            save_training_history(history, str(history_path))
    elif training_interrupted:
        print("\n注意: 训练被中断，跳过完整评估")
        print("提示: 你可以稍后使用评估脚本单独生成评估报告")

    if training_interrupted:
        print(f"\n{'!' * 60}")
        print(f"  已保存中断前的结果")
        print(f"  完成轮数: {completed_epochs}/{epochs}")
        print(f"  最佳验证准确率: {best_val_acc:.2f}%")
        print(f"  模型路径: {best_model_path}")
        print(f"{'!' * 60}")

    return {
        "model_key": model_key,
        "best_val_accuracy": best_val_acc,
        "test_accuracy": test_acc,
        "history": history.to_dict() if save_history else None,
        "model_path": str(best_model_path),
        "save_dir": str(save_dir),
        "interrupted": training_interrupted,
        "completed_epochs": completed_epochs,
    }


def train_cnn_model(model_key: str = "efficientnet_b0", **kwargs) -> Dict[str, Any]:
    """训练CNN模型（完整训练）"""
    return train_model(model_key, **kwargs)


def train_transformer_feature_model(
    model_key: str = "swin_tiny_feature", **kwargs
) -> Dict[str, Any]:
    """训练Transformer特征提取器（仅训练分类头）"""
    return train_model(model_key, **kwargs)
