"""
配置模块
"""

from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# 模型保存目录
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)

# EuroSAT 数据集配置
EuroSAT_URL = "https://github.com/phelber/EuroSAT"
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

# API 配置
API_HOST = "0.0.0.0"
API_PORT = 8000
