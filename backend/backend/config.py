"""
配置模块 - 现代前后端分离版本
引用原始biye项目的模型和数据资源

注意：此模块现在基于pydantic-settings的settings.py模块
提供向后兼容的接口
"""

from pathlib import Path

# 导入新的设置模块
try:
    from settings import settings
except ImportError:
    # 回退到原始配置（用于测试或初始化）
    from pathlib import Path

    # 原始项目目录（只读，不修改）
    ORIGINAL_PROJECT_ROOT = Path("/home/zhouh/biye")

    # 数据目录（指向原始项目）
    DATA_DIR = ORIGINAL_PROJECT_ROOT / "data"
    MODELS_DIR = ORIGINAL_PROJECT_ROOT / "models"

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
            "model_path": MODELS_DIR / "efficientnet_b0" / "best_model.pth",
        },
        "swin_tiny": {
            "name": "swin_tiny_patch4_window7_224",
            "type": "transformer",
            "description": "Swin Transformer Tiny - 视觉 Transformer 模型",
            "model_path": MODELS_DIR / "swin_tiny" / "best_model.pth",
        },
        "swin_tiny_feature": {
            "name": "swin_tiny_patch4_window7_224",
            "type": "transformer_feature",
            "description": "Swin Transformer Tiny 特征提取器 - 仅训练分类头",
            "model_path": MODELS_DIR / "swin_tiny_feature" / "best_model.pth",
        },
    }

    # API 配置
    API_HOST = "0.0.0.0"
    API_PORT = 8000

    # CORS配置（前端开发服务器）
    FRONTEND_DEV_URL = "http://localhost:5173"
    ALLOWED_ORIGINS = [
        FRONTEND_DEV_URL,
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # 文件上传配置
    ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/jpg"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
else:
    # 从settings模块提供兼容接口
    # 原始项目目录（只读，不修改）
    ORIGINAL_PROJECT_ROOT = Path("/home/zhouh/biye")

    # 数据目录（指向原始项目） - 使用settings中的路径
    DATA_DIR = settings.data_dir
    MODELS_DIR = settings.models_dir

    # EuroSAT 数据集配置
    EuroSAT_CLASSES = settings.eurosat_classes
    NUM_CLASSES = settings.num_classes

    # 训练配置
    DEFAULT_IMAGE_SIZE = settings.training.default_image_size
    DEFAULT_BATCH_SIZE = settings.training.default_batch_size
    DEFAULT_EPOCHS = settings.training.default_epochs
    DEFAULT_LEARNING_RATE = settings.training.default_learning_rate

    # 模型配置 - 转换为旧格式
    MODELS = {}
    for key, model_config in settings.models.items():
        MODELS[key] = {
            "name": model_config.name,
            "type": model_config.type,
            "description": model_config.description,
            "model_path": model_config.model_path,
        }

    # API 配置
    API_HOST = settings.api_host
    API_PORT = settings.api_port

    # CORS配置
    ALLOWED_ORIGINS = settings.cors_origins

    # 文件上传配置
    ALLOWED_MIME_TYPES = settings.allowed_mime_types
    MAX_FILE_SIZE = settings.max_file_size
    ALLOWED_EXTENSIONS = settings.allowed_extensions

    # 为了兼容性保留FRONTEND_DEV_URL
    FRONTEND_DEV_URL = "http://localhost:5173"
