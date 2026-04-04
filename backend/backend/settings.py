"""
配置管理模块 - 基于pydantic-settings
统一管理环境变量配置，支持类型安全和验证
"""

import json
from pathlib import Path
from typing import List, Set, Optional, Dict, Any

from pydantic import BaseModel, Field, validator
from pydantic_settings import BaseSettings


class ModelConfig(BaseModel):
    """单个模型配置"""

    name: str
    type: str
    description: str
    model_path: Path


class TrainingConfig(BaseModel):
    """训练配置"""

    default_image_size: int = 224
    default_batch_size: int = 32
    default_epochs: int = 30
    default_learning_rate: float = 1e-4


class Settings(BaseSettings):
    """
    应用设置 - 从环境变量和.env文件加载
    优先级: 环境变量 > .env文件 > 默认值
    """

    # ========== 基本配置 ==========
    # FastAPI配置
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_reload: bool = False

    # 路径配置
    model_path_prefix: Path = Path("/home/zhouh/biye/models")
    data_path_prefix: Path = Path("/home/zhouh/biye/data")

    # 日志配置
    log_level: str = "INFO"
    log_format: str = "json"

    # CORS配置
    cors_origins: List[str] = [
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://frontend:80",
    ]

    # ========== 文件上传配置 ==========
    allowed_mime_types: Set[str] = {"image/jpeg", "image/png", "image/jpg"}
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: Set[str] = {".jpg", ".jpeg", ".png"}

    # ========== 性能配置 ==========
    max_image_size_mb: int = 10
    batch_predict_max_files: int = 50
    model_load_timeout: int = 30
    model_predict_timeout: int = 30

    # ========== 功能开关 ==========
    enable_batch_prediction: bool = True
    enable_model_comparison: bool = True
    enable_visualization: bool = True

    # ========== 缓存配置 ==========
    cache_ttl: int = 3600  # 缓存过期时间（秒）

    # ========== 静态配置（不从环境变量读取） ==========
    # EuroSAT数据集类别
    eurosat_classes: List[str] = [
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
    num_classes: int = 10

    # 训练配置对象
    training: TrainingConfig = Field(default_factory=TrainingConfig)

    # 模型配置
    models: Dict[str, ModelConfig] = Field(default_factory=dict)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            # 自定义源顺序：环境变量 > .env文件 > 默认值
            return env_settings, init_settings, file_secret_settings

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        """解析CORS_ORIGINS环境变量（可能是JSON字符串或列表）"""
        if isinstance(v, str):
            try:
                # 尝试解析JSON字符串
                return json.loads(v)
            except json.JSONDecodeError:
                # 如果不是JSON，可能是逗号分隔的字符串
                if "," in v:
                    return [origin.strip() for origin in v.split(",")]
                # 单个字符串
                return [v.strip()]
        return v

    @validator("model_path_prefix", "data_path_prefix", pre=True)
    def convert_paths(cls, v):
        """将字符串转换为Path对象"""
        if isinstance(v, str):
            return Path(v)
        return v

    def get_model_path(self, model_key: str) -> Optional[Path]:
        """获取指定模型的路径"""
        if model_key in self.models:
            return self.models[model_key].model_path
        return None

    @property
    def models_dir(self) -> Path:
        """模型目录（计算属性）"""
        return self.model_path_prefix

    @property
    def data_dir(self) -> Path:
        """数据目录（计算属性）"""
        return self.data_path_prefix


# 全局设置实例
settings = Settings()

# 预计算模型配置（从原始config.py迁移）
settings.models = {
    "efficientnet_b0": ModelConfig(
        name="efficientnet_b0",
        type="cnn",
        description="EfficientNet-B0 - 高效 CNN 模型",
        model_path=settings.models_dir / "efficientnet_b0" / "best_model.pth",
    ),
    "swin_tiny": ModelConfig(
        name="swin_tiny_patch4_window7_224",
        type="transformer",
        description="Swin Transformer Tiny - 视觉 Transformer 模型",
        model_path=settings.models_dir / "swin_tiny" / "best_model.pth",
    ),
    "swin_tiny_feature": ModelConfig(
        name="swin_tiny_patch4_window7_224",
        type="transformer_feature",
        description="Swin Transformer Tiny 特征提取器 - 仅训练分类头",
        model_path=settings.models_dir / "swin_tiny_feature" / "best_model.pth",
    ),
}


if __name__ == "__main__":
    # 测试配置加载
    print("配置加载测试:")
    print(f"API Host: {settings.api_host}:{settings.api_port}")
    print(f"Models Dir: {settings.models_dir}")
    print(f"Data Dir: {settings.data_dir}")
    print(f"CORS Origins: {settings.cors_origins}")
    print(f"Available Models: {list(settings.models.keys())}")
