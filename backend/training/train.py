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

    for batch_idx, (inputs, targets) in enumerate(train_loader):
        inputs, targets = inputs.to(device), targets.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()
        _, predicted = outputs.max(1)
        total += targets.size(0)
        correct += predicted.eq(targets).sum().item()

    accuracy = 100.0 * correct / total
    avg_loss = running_loss / len(train_loader)
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


def train_model(
    model_key: str,
    data_dir: Optional[str] = None,
    epochs: int = DEFAULT_EPOCHS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    lr: float = DEFAULT_LEARNING_RATE,
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

    print(f"\n{'=' * 50}")
    print(f"Training {model_key}")
    print(f"Device: {device}")
    print(f"Data directory: {data_dir}")
    print(f"Epochs: {epochs}, Batch size: {batch_size}, LR: {lr}")
    print(f"{'=' * 50}\n")

    # 加载模型
    model = get_model(model_key, num_classes=NUM_CLASSES)
    model = model.to(device)

    print(f"Total parameters: {count_parameters(model):,}")

    # 如果是Transformer特征提取器（仅训练分类头），冻结基础模型
    if model_key == "swin_tiny_feature":
        print("Training only classification head (feature extractor mode)")
        for name, param in model.named_parameters():
            if not name.startswith("head"):
                param.requires_grad = False
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        print(
            f"Trainable parameters: {trainable_params:,} ({trainable_params / count_parameters(model) * 100:.2f}%)"
        )

    # 加载数据集
    train_loader, val_loader, test_loader, classes = load_eurosat_dataset(
        data_dir, image_size, batch_size
    )

    # 训练设置
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    # 创建保存目录
    save_dir = NEW_MODELS_DIR / model_key
    save_dir.mkdir(parents=True, exist_ok=True)

    # 训练历史记录
    history = TrainingHistory(model_key=model_key)

    best_val_acc = 0.0
    best_model_path = save_dir / "best_model.pth"

    # 训练循环
    for epoch in range(epochs):
        start_time = time.time()

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        val_loss, val_acc = validate(model, val_loader, criterion, device)

        scheduler.step()
        elapsed = time.time() - start_time

        # 记录历史
        history.add_epoch(
            epoch=epoch + 1,
            train_loss=train_loss,
            train_accuracy=train_acc,
            val_loss=val_loss,
            val_accuracy=val_acc,
            learning_rate=optimizer.param_groups[0]["lr"],
            time_elapsed=elapsed,
        )

        print(
            f"Epoch {epoch + 1}/{epochs} | "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}% | "
            f"Time: {elapsed:.1f}s | LR: {optimizer.param_groups[0]['lr']:.6f}"
        )

        # 保存最佳模型
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), best_model_path)
            print(f"  -> Saved best model (Val Acc: {val_acc:.2f}%)")

    print(f"\nTraining complete! Best Val Acc: {best_val_acc:.2f}%")

    # 加载最佳模型进行评估
    model.load_state_dict(
        torch.load(best_model_path, map_location=device, weights_only=True)
    )

    # 测试集评估
    test_loss, test_acc = validate(model, test_loader, criterion, device)
    print(f"Test Accuracy: {test_acc:.2f}%")

    # 记录最终测试结果
    history.final_test_accuracy = test_acc
    history.best_val_accuracy = best_val_acc
    history.best_epoch = history.get_best_epoch()

    # 保存训练历史
    if save_history:
        history_path = NEW_TRAINING_HISTORY_DIR / f"{model_key}_history.json"
        save_training_history(history, str(history_path))
        print(f"Training history saved to: {history_path}")

    # 进行全面评估
    if evaluate_after_training:
        print("\nRunning comprehensive evaluation...")
        eval_results = evaluate_model(model, test_loader, device, EuroSAT_CLASSES)

        # 保存评估结果
        eval_path = save_dir / "evaluation_results.json"
        save_evaluation_results(eval_results, str(eval_path))
        print(f"Evaluation results saved to: {eval_path}")

        # 更新历史记录中的评估信息
        history.evaluation_available = True
        history.evaluation_path = str(eval_path)
        if save_history:
            save_training_history(history, str(history_path))

    return {
        "model_key": model_key,
        "best_val_accuracy": best_val_acc,
        "test_accuracy": test_acc,
        "history": history.to_dict() if save_history else None,
        "model_path": str(best_model_path),
        "save_dir": str(save_dir),
    }


def train_cnn_model(model_key: str = "efficientnet_b0", **kwargs) -> Dict[str, Any]:
    """训练CNN模型（完整训练）"""
    return train_model(model_key, **kwargs)


def train_transformer_feature_model(
    model_key: str = "swin_tiny_feature", **kwargs
) -> Dict[str, Any]:
    """训练Transformer特征提取器（仅训练分类头）"""
    return train_model(model_key, **kwargs)
