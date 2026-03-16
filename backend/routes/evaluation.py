"""
评估分析路由
提供模型评估结果
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import numpy as np
import time

from backend.shared import validate_model_key, EuroSAT_CLASSES

router = APIRouter()


# 响应模型
class EvaluationResponse(BaseModel):
    model: str
    accuracy: float
    confusion_matrix: List[List[int]]
    classes: List[str]
    class_accuracy: Dict[str, float]
    inference_time_ms: float
    model_info: Dict[str, Any]
    roc_curves: Dict[str, Any]


# 模拟评估数据（实际项目中应从文件加载）
def load_simulated_evaluation_data(model_key: str):
    """加载模拟评估数据"""

    # 基于模型类型设置不同的参数
    if model_key == "efficientnet_b0":
        accuracy = 0.9874
        inference_time = 15.2
        total_params = 5288548
        trainable_params = 5288548
        model_type = "cnn"
    elif model_key == "swin_tiny_feature":
        accuracy = 0.9168
        inference_time = 45.6
        total_params = 27500000
        trainable_params = 512000
        model_type = "transformer_feature"
    elif model_key == "swin_tiny":
        accuracy = 0.0  # 未训练
        inference_time = 0.0
        total_params = 28000000
        trainable_params = 28000000
        model_type = "transformer"
    else:
        raise ValueError(f"未知模型: {model_key}")

    # 生成混淆矩阵（模拟数据）
    num_classes = len(EuroSAT_CLASSES)
    np.random.seed(hash(model_key) % 1000)  # 基于模型名生成确定性的随机数

    # 创建对角占优的混淆矩阵
    confusion_matrix = np.zeros((num_classes, num_classes), dtype=int)
    for i in range(num_classes):
        for j in range(num_classes):
            if i == j:
                # 对角线：正确分类
                confusion_matrix[i][j] = int(100 * accuracy + np.random.randint(0, 20))
            else:
                # 非对角线：错误分类
                confusion_matrix[i][j] = np.random.randint(0, 5)

    # 类别准确率
    class_accuracy = {}
    for i, class_name in enumerate(EuroSAT_CLASSES):
        total = np.sum(confusion_matrix[i, :])
        correct = confusion_matrix[i, i]
        class_accuracy[class_name] = correct / total if total > 0 else 0.0

    # ROC曲线数据（简化）
    roc_curves = {
        "fpr": {},
        "tpr": {},
        "auc": {},
        "macro": {"fpr": [], "tpr": []},
        "micro": {"fpr": [], "tpr": []},
    }

    # 为每个类别生成简化的ROC数据
    for class_name in EuroSAT_CLASSES:
        fpr = np.linspace(0, 1, 10)
        tpr = accuracy + (np.random.random(10) * 0.1 - 0.05)
        tpr = np.clip(tpr, 0, 1)
        auc = np.trapz(tpr, fpr)

        roc_curves["fpr"][class_name] = fpr.tolist()
        roc_curves["tpr"][class_name] = tpr.tolist()
        roc_curves["auc"][class_name] = float(auc)

    # 生成宏平均和微平均ROC
    roc_curves["macro"]["fpr"] = np.linspace(0, 1, 10).tolist()
    roc_curves["macro"]["tpr"] = [accuracy + (x * 0.05) for x in np.linspace(0, 1, 10)]
    roc_curves["micro"]["fpr"] = np.linspace(0, 1, 10).tolist()
    roc_curves["micro"]["tpr"] = [accuracy - (x * 0.03) for x in np.linspace(0, 1, 10)]

    return EvaluationResponse(
        model=model_key,
        accuracy=accuracy,
        confusion_matrix=confusion_matrix.tolist(),
        classes=EuroSAT_CLASSES,
        class_accuracy=class_accuracy,
        inference_time_ms=inference_time,
        model_info={
            "type": model_type,
            "total_params": total_params,
            "trainable_params": trainable_params,
            "description": f"{model_key} - {'CNN' if model_type == 'cnn' else 'Transformer'}模型",
        },
        roc_curves=roc_curves,
    )


@router.get("/evaluation/{model_key}", response_model=EvaluationResponse)
async def get_evaluation(model_key: str):
    """获取模型评估结果"""
    # 验证模型
    validate_model_key(model_key)

    try:
        # 在实际项目中，这里应该从文件加载真实的评估结果
        # 为了简化，我们返回模拟数据
        return load_simulated_evaluation_data(model_key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评估结果失败: {str(e)}")
