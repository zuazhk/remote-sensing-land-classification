"""
缓存集成示例 - 展示如何在现有代码中使用缓存
"""

import hashlib
from typing import Dict, Any
from pathlib import Path

# 导入缓存模块
from .cache import cached_prediction, model_cache, prediction_cache, get_cache_stats


class CachedModelPredictor:
    """缓存感知的模型预测器"""

    def __init__(self, model_loader):
        """
        初始化缓存预测器

        Args:
            model_loader: 模型加载函数
        """
        self.model_loader = model_loader
        self._models = {}

    def load_model(self, model_key: str):
        """
        加载模型（带缓存）

        Args:
            model_key: 模型键

        Returns:
            加载的模型
        """
        cache_key = f"model:{model_key}"

        # 尝试从缓存获取
        cached_model = model_cache.get(cache_key)
        if cached_model is not None:
            return cached_model

        # 加载模型
        model = self.model_loader(model_key)

        # 缓存模型
        model_cache.set(cache_key, model)

        return model

    @cached_prediction(cache_key_prefix="pred", ttl=300)
    def predict(self, model_key: str, image_data, metadata: Dict[str, Any] = None):
        """
        预测函数（带缓存）

        注意：实际实现需要根据具体预测函数调整
        """
        # 加载模型
        model = self.load_model(model_key)

        # 执行预测（这里只是示例）
        # result = model.predict(image_data)
        result = {"prediction": "example", "confidence": 0.95}

        return result

    def clear_model_cache(self, model_key: str = None):
        """
        清除模型缓存

        Args:
            model_key: 模型键，如果为None则清除所有模型缓存
        """
        if model_key:
            cache_key = f"model:{model_key}"
            model_cache.delete(cache_key)
        else:
            model_cache.clear()


def create_image_signature(image_path: Path, model_key: str) -> str:
    """
    创建图像签名，用于缓存键

    Args:
        image_path: 图像路径
        model_key: 模型键

    Returns:
        缓存键
    """
    # 读取图像文件前几个字节和元数据
    try:
        with open(image_path, "rb") as f:
            # 读取文件大小和部分内容
            file_size = image_path.stat().st_size
            first_bytes = f.read(1024)  # 读取前1KB

        # 创建签名
        signature_data = (
            f"{model_key}:{file_size}:{hashlib.md5(first_bytes).hexdigest()}"
        )
        return hashlib.md5(signature_data.encode()).hexdigest()
    except Exception:
        # 如果无法读取文件，使用路径和模型键
        return hashlib.md5(f"{model_key}:{image_path}".encode()).hexdigest()


# 使用示例
if __name__ == "__main__":
    print("缓存集成示例")
    print("=" * 50)

    # 创建模拟模型加载器
    def mock_model_loader(model_key):
        print(f"加载模型: {model_key}")
        return f"model_{model_key}"

    # 创建缓存预测器
    predictor = CachedModelPredictor(mock_model_loader)

    # 测试模型加载缓存
    print("\n1. 测试模型加载缓存:")
    model1 = predictor.load_model("efficientnet_b0")
    print(f"   第一次加载: {model1}")

    model2 = predictor.load_model("efficientnet_b0")
    print(f"   第二次加载（应该从缓存）: {model2}")

    # 测试预测缓存
    print("\n2. 测试预测缓存:")
    result1 = predictor.predict("efficientnet_b0", "image_data_1")
    print(f"   第一次预测: {result1}")

    result2 = predictor.predict("efficientnet_b0", "image_data_1")
    print(f"   第二次预测（应该从缓存）: {result2}")

    # 显示缓存统计
    print("\n3. 缓存统计:")
    stats = get_cache_stats()
    print(f"   模型缓存大小: {stats['model_cache']['size']}")
    print(f"   预测缓存大小: {stats['prediction_cache']['size']}")

    # 清理缓存
    print("\n4. 清理缓存:")
    predictor.clear_model_cache("efficientnet_b0")
    print("   已清理efficientnet_b0模型缓存")

    stats_after = get_cache_stats()
    print(f"   清理后模型缓存大小: {stats_after['model_cache']['size']}")
