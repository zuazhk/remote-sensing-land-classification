"""
API 响应模型定义
用于确保响应数据结构和类型安全
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import numpy as np


class EvaluationResults(BaseModel):
    """模型评估结果响应模型"""

    model: str = Field(..., description="模型名称")
    accuracy: float = Field(..., description="总体准确率", ge=0, le=1)
    confusion_matrix: List[List[int]] = Field(..., description="混淆矩阵 (10x10)")
    classes: List[str] = Field(..., description="类别标签列表")
    class_accuracy: Dict[str, float] = Field(..., description="各类别准确率")
    inference_time_ms: float = Field(..., description="推理时间(毫秒)", ge=0)
    model_info: Dict[str, Any] = Field(..., description="模型信息")
    roc_curves: Optional[Dict[str, Any]] = Field(None, description="ROC曲线数据")


class ConfusionMatrixResponse(BaseModel):
    """混淆矩阵响应模型"""

    model: str = Field(..., description="模型名称")
    classes: List[str] = Field(..., description="类别标签列表")
    confusion_matrix: List[List[int]] = Field(..., description="混淆矩阵 (10x10)")
    accuracy: float = Field(..., description="总体准确率", ge=0, le=1)
    class_accuracy: Dict[str, float] = Field(..., description="各类别准确率")


class ROCResponse(BaseModel):
    """ROC曲线响应模型"""

    model: str = Field(..., description="模型名称")
    fpr: Dict[str, List[float]] = Field(..., description="各类别假正率列表")
    tpr: Dict[str, List[float]] = Field(..., description="各类别真正率列表")
    auc: Dict[str, float] = Field(..., description="各类别AUC值")
    macro: Optional[Dict[str, Any]] = Field(None, description="宏观平均ROC数据")
    micro: Optional[Dict[str, Any]] = Field(None, description="微观平均ROC数据")
    classes: List[str] = Field(..., description="类别标签列表")
    sampled_curves: Optional[Dict[str, Dict[str, List[float]]]] = Field(
        None, description="采样后的ROC曲线数据"
    )


class ModelInfo(BaseModel):
    """模型信息响应模型"""

    model: str = Field(..., description="模型名称")
    accuracy: Optional[float] = Field(None, description="验证准确率", ge=0, le=1)
    inference_time_ms: Optional[float] = Field(None, description="推理时间(毫秒)", ge=0)
    total_params: Optional[int] = Field(None, description="总参数量", ge=0)
    trainable_params: Optional[int] = Field(None, description="可训练参数量", ge=0)
    trained: bool = Field(..., description="是否已训练")


class ModelComparisonResponse(BaseModel):
    """模型对比响应模型"""

    models: List[ModelInfo] = Field(..., description="模型信息列表")
    classes: List[str] = Field(..., description="类别标签列表")
    comparison_time: str = Field(..., description="对比时间")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    detail: str = Field(..., description="错误详情")


# 健康检查响应
class HealthResponse(BaseModel):
    status: str = Field(..., description="服务状态")
    models_loaded: int = Field(..., description="已加载模型数量")
    device: str = Field(..., description="计算设备")


# 预测响应
class PredictResult(BaseModel):
    """单类别预测结果"""

    class_name: str = Field(..., description="类别名称")
    confidence: float = Field(..., description="置信度", ge=0, le=1)


class PredictResponse(BaseModel):
    """图像预测响应"""

    model: str = Field(..., description="模型名称")
    result: Dict[str, Any] = Field(..., description="预测结果详情")


# 批量预测响应
class BatchResult(BaseModel):
    filename: str = Field(..., description="文件名")
    model: str = Field(..., description="模型名称")
    result: Dict[str, Any] = Field(..., description="预测结果")


class BatchPredictResponse(BaseModel):
    model: str = Field(..., description="模型名称")
    total_images: int = Field(..., description="总图像数", ge=0)
    results: List[BatchResult] = Field(..., description="预测结果列表")
