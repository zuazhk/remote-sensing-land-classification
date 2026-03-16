"""
共享全局状态和配置 - 现代前后端分离版本
引用原始biye项目的模型和数据资源
"""

import sys
from pathlib import Path

# 首先导入新的config模块获取正确的路径
from backend.config import MODELS_DIR as CORRECT_MODELS_DIR, EuroSAT_CLASSES

# 导出这些名称以保持兼容性
MODELS_DIR = CORRECT_MODELS_DIR

# 导入lib.config并修改其MODELS_DIR指向正确路径
import backend.lib.config
backend.lib.config.MODELS_DIR = Path(CORRECT_MODELS_DIR)

# 现在导入load_all_models，它将使用已修补的MODELS_DIR
from backend.lib.inference import load_all_models

# 模型分类器 - 使用原始项目的模型加载函数
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
