"""
pytest配置和fixtures
"""

import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """创建事件循环fixture，用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_client() -> AsyncGenerator[TestClient, None]:
    """创建FastAPI测试客户端"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_settings():
    """测试设置fixture"""
    # 可以在这里覆盖测试环境变量
    import os

    original_env = os.environ.copy()

    # 设置测试环境变量
    os.environ.update(
        {
            "API_HOST": "127.0.0.1",
            "API_PORT": "9999",  # 测试端口
            "LOG_LEVEL": "DEBUG",
        }
    )

    yield

    # 恢复原始环境变量
    os.environ.clear()
    os.environ.update(original_env)
