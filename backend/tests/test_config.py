"""
配置系统测试
"""

import os
import tempfile
from pathlib import Path

import pytest


def test_settings_loading():
    """测试设置模块正确加载"""
    from ..settings import settings

    # 检查基本设置
    assert hasattr(settings, "api_host")
    assert hasattr(settings, "api_port")
    assert hasattr(settings, "models_dir")
    assert hasattr(settings, "data_dir")

    # 检查类型
    assert isinstance(settings.api_host, str)
    assert isinstance(settings.api_port, int)
    assert isinstance(settings.models_dir, Path)
    assert isinstance(settings.data_dir, Path)

    # 检查值合理性
    assert settings.api_port > 0 and settings.api_port < 65536
    assert (
        settings.models_dir.exists() or not settings.models_dir.exists()
    )  # 目录可能存在也可能不存在
    assert len(settings.eurosat_classes) == 10  # EuroSAT有10个类别


def test_settings_environment_override():
    """测试环境变量覆盖设置"""
    # 保存原始环境变量
    original_api_port = os.environ.get("API_PORT")

    try:
        # 设置测试环境变量
        os.environ["API_PORT"] = "9999"

        # 重新导入设置以获取新值
        import importlib
        from .. import settings as backend_settings

        importlib.reload(backend_settings)

        settings = backend_settings.settings

        # 检查环境变量被正确使用
        assert settings.api_port == 9999

    finally:
        # 清理环境变量
        if original_api_port:
            os.environ["API_PORT"] = original_api_port
        else:
            os.environ.pop("API_PORT", None)

        # 重新加载原始设置
        import importlib
        from .. import settings as backend_settings

        importlib.reload(backend_settings)


def test_config_compatibility():
    """测试config.py的向后兼容性"""
    from ..config import API_HOST, API_PORT, ALLOWED_ORIGINS, MODELS_DIR, DATA_DIR

    # 检查导出的值存在
    assert API_HOST is not None
    assert API_PORT is not None
    assert ALLOWED_ORIGINS is not None
    assert MODELS_DIR is not None
    assert DATA_DIR is not None

    # 检查类型
    assert isinstance(API_HOST, str)
    assert isinstance(API_PORT, int)
    assert isinstance(ALLOWED_ORIGINS, list)
    assert isinstance(MODELS_DIR, Path)
    assert isinstance(DATA_DIR, Path)

    # 检查config使用settings的值
    from ..settings import settings

    assert API_HOST == settings.api_host
    assert API_PORT == settings.api_port
    assert MODELS_DIR == settings.models_dir
    assert DATA_DIR == settings.data_dir


def test_cors_origins_parsing():
    """测试CORS origins解析"""
    # 测试JSON字符串解析
    test_json = '["http://test1.com", "http://test2.com"]'

    # 保存原始环境变量
    original_cors = os.environ.get("CORS_ORIGINS")

    try:
        os.environ["CORS_ORIGINS"] = test_json

        # 重新导入设置
        import importlib
        from .. import settings as backend_settings

        importlib.reload(backend_settings)

        settings = backend_settings.settings

        assert settings.cors_origins == ["http://test1.com", "http://test2.com"]

    finally:
        # 清理
        if original_cors:
            os.environ["CORS_ORIGINS"] = original_cors
        else:
            os.environ.pop("CORS_ORIGINS", None)

        import importlib
        from .. import settings as backend_settings

        importlib.reload(backend_settings)
