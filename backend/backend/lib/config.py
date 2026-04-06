"""
配置模块 - 适配版本
指向原始biye项目的模型和数据资源
支持环境变量配置
"""

import os
from pathlib import Path

# 从环境变量读取路径前缀，支持容器化部署
MODEL_PATH_PREFIX = os.getenv("MODEL_PATH_PREFIX", "/home/zhouh/biye/models")
DATA_PATH_PREFIX = os.getenv("DATA_PATH_PREFIX", "/home/zhouh/biye/data")

# 原始项目模型和数据目录（只读）
ORIGINAL_MODELS_DIR = Path("/home/zhouh/biye/models")
ORIGINAL_DATA_DIR = Path("/home/zhouh/biye/data")

# 新项目模型和数据目录（可写）
NEW_PROJECT_ROOT = Path(__file__).parent.parent
NEW_MODELS_DIR = NEW_PROJECT_ROOT / "models"
NEW_TRAINING_HISTORY_DIR = NEW_PROJECT_ROOT / "training" / "history"
PRETRAINED_WEIGHTS_DIR = NEW_PROJECT_ROOT / "pretrained_weights"
NEW_MODELS_DIR.mkdir(parents=True, exist_ok=True)
NEW_TRAINING_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
PRETRAINED_WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)

# 模型和数据目录（兼容现有代码，优先使用新项目目录）
MODELS_DIR = NEW_MODELS_DIR  # 新训练的模型保存到这里
DATA_DIR = Path(DATA_PATH_PREFIX)  # 数据仍使用原始项目

# 验证目录是否存在
if not MODELS_DIR.exists():
    print(f"警告: 模型目录不存在: {MODELS_DIR}")
if not DATA_DIR.exists():
    print(f"警告: 数据目录不存在: {DATA_DIR}")

# EuroSAT 数据集配置
EuroSAT_CLASSES = [
    "AnnualCrop",
    "Forest",
    "HerbaceousVegetation",
    "Highway",
    "Industrial",
    "Pasture",
    "PermanentCrop",
    "Residential",
    "River",
    "SeaLake",
]
NUM_CLASSES = 10

# 训练配置
DEFAULT_IMAGE_SIZE = 224
DEFAULT_BATCH_SIZE = 32
DEFAULT_EPOCHS = 30
DEFAULT_LEARNING_RATE = 1e-4

# 模型配置
MODELS = {
    "efficientnet_b0": {
        "name": "efficientnet_b0",
        "type": "cnn",
        "description": "EfficientNet-B0 - 高效 CNN 模型",
    },
    "swin_tiny": {
        "name": "swin_tiny_patch4_window7_224",
        "type": "transformer",
        "description": "Swin Transformer Tiny - 视觉 Transformer 模型",
    },
    "swin_tiny_feature": {
        "name": "swin_tiny_patch4_window7_224",
        "type": "transformer_feature",
        "description": "Swin Transformer Tiny 特征提取器 - 仅训练分类头",
    },
}

# API 配置 - 从环境变量读取
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# 其他配置
MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
BATCH_PREDICT_MAX_FILES = int(os.getenv("BATCH_PREDICT_MAX_FILES", "50"))
