"""
模型信息路由
提供模型列表和类别信息
"""

from fastapi import APIRouter
from pathlib import Path

from backend.shared import MODELS_DIR, EuroSAT_CLASSES, classifiers

router = APIRouter()


@router.get("/models")
async def list_models():
    """获取所有模型信息及训练状态"""
    model_info = {}

    model_keys = ["efficientnet_b0", "swin_tiny", "swin_tiny_feature"]

    for model_key in model_keys:
        model_path = MODELS_DIR / model_key / "best_model.pth"
        trained = model_path.exists()

        model_type = "cnn" if "efficientnet" in model_key else "transformer"
        if "feature" in model_key:
            model_type = "transformer_feature"

        model_info[model_key] = {
            "type": model_type,
            "trained": trained,
            "path": str(model_path),
            "loaded": model_key in classifiers,
            "description": {
                "efficientnet_b0": "EfficientNet-B0 - 高效 CNN 模型",
                "swin_tiny": "Swin Transformer Tiny - 视觉 Transformer 模型",
                "swin_tiny_feature": "Swin Transformer Tiny 特征提取器 - 仅训练分类头",
            }.get(model_key, "未知模型"),
        }

    return model_info


@router.get("/classes")
async def list_classes():
    """获取所有分类类别"""
    return {
        "classes": EuroSAT_CLASSES,
        "num_classes": len(EuroSAT_CLASSES),
        "description": "EuroSAT遥感图像数据集，包含10个土地利用类别",
    }
