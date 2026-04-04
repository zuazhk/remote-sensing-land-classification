"""
模型评估模块
生成全面的评估结果：混淆矩阵、ROC曲线、分类报告等
"""

import torch
import numpy as np
from typing import Dict, Any, List, Tuple
import json
from pathlib import Path
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_curve,
    auc,
    roc_auc_score,
)
from sklearn.preprocessing import label_binarize
import warnings

warnings.filterwarnings("ignore")


def evaluate_model(
    model,
    test_loader,
    device: str,
    class_names: List[str],
    num_classes: int = 10,
) -> Dict[str, Any]:
    """全面评估模型"""
    model.eval()

    all_preds = []
    all_targets = []
    all_probs = []

    with torch.no_grad():
        for inputs, targets in test_loader:
            inputs = inputs.to(device)
            targets = targets.to(device)

            outputs = model(inputs)
            probs = torch.nn.functional.softmax(outputs, dim=1)

            _, preds = torch.max(outputs, 1)

            all_preds.extend(preds.cpu().numpy())
            all_targets.extend(targets.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())

    # 转换为numpy数组
    y_true = np.array(all_targets)
    y_pred = np.array(all_preds)
    y_probs = np.array(all_probs)

    # 基本指标
    accuracy = np.mean(y_true == y_pred)

    # 混淆矩阵
    cm = confusion_matrix(y_true, y_pred, labels=range(num_classes))

    # 各类别准确率
    class_accuracy = {}
    for i, class_name in enumerate(class_names):
        mask = y_true == i
        if np.sum(mask) > 0:
            class_acc = np.mean(y_pred[mask] == i)
            class_accuracy[class_name] = float(class_acc)
        else:
            class_accuracy[class_name] = 0.0

    # 分类报告
    report = classification_report(
        y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0
    )

    # ROC曲线和AUC
    roc_data = compute_roc_data(y_true, y_probs, class_names, num_classes)

    # 构建评估结果
    results = {
        "model": model.__class__.__name__,
        "accuracy": float(accuracy),
        "class_accuracy": class_accuracy,
        "confusion_matrix": cm.tolist(),
        "classification_report": report,
        "roc_curves": roc_data,
        "num_samples": len(y_true),
        "predictions": {
            "true_labels": y_true.tolist(),
            "predicted_labels": y_pred.tolist(),
            "probabilities": y_probs.tolist(),
        },
    }

    return results


def compute_roc_data(
    y_true: np.ndarray,
    y_probs: np.ndarray,
    class_names: List[str],
    num_classes: int,
) -> Dict[str, Any]:
    """计算ROC曲线数据"""
    # 二值化标签用于多类ROC
    y_true_bin = label_binarize(y_true, classes=range(num_classes))

    # 存储各类别的ROC数据
    fpr = {}
    tpr = {}
    roc_auc = {}

    # 计算每个类别的ROC
    for i, class_name in enumerate(class_names):
        fpr[class_name], tpr[class_name], _ = roc_curve(y_true_bin[:, i], y_probs[:, i])
        roc_auc[class_name] = auc(fpr[class_name], tpr[class_name])

    # 计算宏观平均ROC
    fpr["macro"], tpr["macro"], _ = roc_curve(y_true_bin.ravel(), y_probs.ravel())
    roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])

    # 计算微观平均ROC（加权平均）
    # 首先聚合所有假阳性率和真阳性率
    all_fpr = np.unique(np.concatenate([fpr[cls] for cls in class_names]))

    # 插值所有ROC曲线到公共点
    mean_tpr = np.zeros_like(all_fpr)
    for cls in class_names:
        mean_tpr += np.interp(all_fpr, fpr[cls], tpr[cls])

    # 平均
    mean_tpr /= num_classes
    fpr["micro"] = all_fpr.tolist()
    tpr["micro"] = mean_tpr.tolist()
    roc_auc["micro"] = auc(all_fpr, mean_tpr)

    return {
        "fpr": {
            k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in fpr.items()
        },
        "tpr": {
            k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in tpr.items()
        },
        "auc": {k: float(v) for k, v in roc_auc.items()},
    }


def save_evaluation_results(results: Dict[str, Any], filepath: str):
    """保存评估结果到JSON文件"""
    # 简化分类报告（只保留主要指标）
    if "classification_report" in results:
        report = results["classification_report"]
        simplified_report = {}
        for key, value in report.items():
            if isinstance(value, dict):
                simplified_report[key] = {
                    k: v
                    for k, v in value.items()
                    if k in ["precision", "recall", "f1-score", "support"]
                }
            else:
                simplified_report[key] = value
        results["classification_report"] = simplified_report

    # 保存到文件
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)


def load_evaluation_results(filepath: str) -> Dict[str, Any]:
    """从JSON文件加载评估结果"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_evaluation_results_path(model_key: str) -> Path:
    """获取评估结果文件路径"""
    from ..lib.config import NEW_MODELS_DIR

    return NEW_MODELS_DIR / model_key / "evaluation_results.json"


def has_evaluation_results(model_key: str) -> bool:
    """检查是否有评估结果"""
    eval_path = get_evaluation_results_path(model_key)
    return eval_path.exists()
