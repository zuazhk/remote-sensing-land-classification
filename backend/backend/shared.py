"""
共享全局状态和配置 - 现代前后端分离版本
"""

from pathlib import Path

# 直接使用 lib/config 中的新路径（指向 backend/models/）
from .lib.config import MODELS_DIR, EuroSAT_CLASSES

print(f"✅ 模型加载路径: {MODELS_DIR}")

# 现在导入load_all_models，它将使用正确的MODELS_DIR
from .lib.inference import load_all_models

# 模型分类器
classifiers = load_all_models()


# 模型键验证
def validate_model_key(model_key: str):
    """验证模型键是否存在"""
    if model_key not in classifiers:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail=f"模型 '{model_key}' 不存在。可用模型: {list(classifiers.keys())}",
        )
    return model_key


# 导出
__all__ = [
    "classifiers",
    "MODELS_DIR",
    "EuroSAT_CLASSES",
    "validate_model_key",
]
