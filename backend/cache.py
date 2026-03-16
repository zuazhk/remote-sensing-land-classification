"""
缓存模块 - 提供内存缓存功能
支持TTL和LRU策略
"""

import time
from collections import OrderedDict
from typing import Any, Optional, Dict, Tuple
from threading import Lock


class TTLCache:
    """带TTL的内存缓存"""

    def __init__(self, maxsize: int = 100, ttl: int = 3600):
        """
        初始化TTL缓存

        Args:
            maxsize: 最大缓存项数
            ttl: 缓存生存时间（秒）
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在或已过期则返回None
        """
        with self._lock:
            if key not in self._cache:
                return None

            value, timestamp = self._cache[key]

            # 检查是否过期
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                return None

            return value

    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        with self._lock:
            # 如果达到最大大小，删除最旧的项
            if len(self._cache) >= self.maxsize and key not in self._cache:
                # 删除第一个（最旧的）项
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]

            self._cache[key] = (value, time.time())

    def delete(self, key: str) -> bool:
        """
        删除缓存项

        Args:
            key: 缓存键

        Returns:
            是否成功删除
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()

    def cleanup(self) -> int:
        """
        清理过期项

        Returns:
            清理的项数
        """
        with self._lock:
            now = time.time()
            expired_keys = [
                key
                for key, (_, timestamp) in self._cache.items()
                if now - timestamp > self.ttl
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    def size(self) -> int:
        """获取缓存当前大小"""
        with self._lock:
            return len(self._cache)

    def keys(self) -> list[str]:
        """获取所有缓存键"""
        with self._lock:
            return list(self._cache.keys())


class LRUCache:
    """LRU（最近最少使用）缓存"""

    def __init__(self, maxsize: int = 100):
        """
        初始化LRU缓存

        Args:
            maxsize: 最大缓存项数
        """
        self.maxsize = maxsize
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._lock = Lock()

    def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值，并将项移到最近使用的位置

        Args:
            key: 缓存键

        Returns:
            缓存值，如果不存在则返回None
        """
        with self._lock:
            if key not in self._cache:
                return None

            # 移到最近使用的位置
            value = self._cache.pop(key)
            self._cache[key] = value
            return value

    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        with self._lock:
            if key in self._cache:
                # 如果已存在，先删除
                self._cache.pop(key)
            elif len(self._cache) >= self.maxsize:
                # 如果达到最大大小，删除最旧的项
                self._cache.popitem(last=False)

            self._cache[key] = value

    def delete(self, key: str) -> bool:
        """
        删除缓存项

        Args:
            key: 缓存键

        Returns:
            是否成功删除
        """
        with self._lock:
            if key in self._cache:
                self._cache.pop(key)
                return True
            return False

    def clear(self) -> None:
        """清空缓存"""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """获取缓存当前大小"""
        with self._lock:
            return len(self._cache)

    def keys(self) -> list[str]:
        """获取所有缓存键"""
        with self._lock:
            return list(self._cache.keys())


# 全局缓存实例
# 预测结果缓存（短期缓存，TTL较短）
prediction_cache = TTLCache(maxsize=1000, ttl=300)  # 5分钟TTL

# 模型缓存（长期缓存）
model_cache = TTLCache(maxsize=10, ttl=3600)  # 1小时TTL

# 图像特征缓存（中等期限）
feature_cache = TTLCache(maxsize=500, ttl=1800)  # 30分钟TTL


def cached_prediction(cache_key_prefix: str = "pred", ttl: int = 300):
    """
    预测结果缓存装饰器

    Args:
        cache_key_prefix: 缓存键前缀
        ttl: 缓存生存时间（秒）
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 生成缓存键
            import hashlib
            import pickle

            # 将参数序列化为缓存键
            key_data = pickle.dumps((args, kwargs))
            key_hash = hashlib.md5(key_data).hexdigest()
            cache_key = f"{cache_key_prefix}:{key_hash}"

            # 尝试从缓存获取
            cached_result = prediction_cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # 执行函数
            result = func(*args, **kwargs)

            # 缓存结果
            prediction_cache.set(cache_key, result)

            return result

        return wrapper

    return decorator


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    return {
        "prediction_cache": {
            "size": prediction_cache.size(),
            "keys": prediction_cache.keys(),
        },
        "model_cache": {
            "size": model_cache.size(),
            "keys": model_cache.keys(),
        },
        "feature_cache": {
            "size": feature_cache.size(),
            "keys": feature_cache.keys(),
        },
    }


def clear_all_caches() -> Dict[str, int]:
    """清空所有缓存并返回清理的项数"""
    prediction_size = prediction_cache.size()
    model_size = model_cache.size()
    feature_size = feature_cache.size()

    prediction_cache.clear()
    model_cache.clear()
    feature_cache.clear()

    return {
        "prediction_cache_cleared": prediction_size,
        "model_cache_cleared": model_size,
        "feature_cache_cleared": feature_size,
    }
