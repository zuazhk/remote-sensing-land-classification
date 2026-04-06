"""
数据库连接和会话管理

使用 SQLAlchemy 2.0 异步引擎连接 PostgreSQL。
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .settings import settings

# 异步数据库引擎
# asyncpg 是纯异步驱动，性能比同步驱动高 3-5 倍
engine = create_async_engine(
    settings.database_url,
    echo=False,  # 设为 True 可打印所有 SQL 语句（调试用）
    pool_size=5,  # 连接池大小
    max_overflow=10,  # 超出 pool_size 后最多额外创建的连接数
)

# 会话工厂 - 每次数据库操作都需要一个 session
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不自动过期对象属性
)


class Base(DeclarativeBase):
    """所有 ORM 模型的基类"""
    pass


async def get_db() -> AsyncSession:
    """
    FastAPI 依赖注入函数 - 获取数据库会话
    
    用法:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
