"""
FastAPI 主入口 - 现代前后端分离版本
纯API服务，移除模板渲染，支持CORS

启动方式（在 backend/ 目录下执行）：
  uv run uvicorn backend.main:app --host 0.0.0.0 --port 8001
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# 使用相对导入
from .config import API_HOST, API_PORT, ALLOWED_ORIGINS

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# 抑制第三方库的冗余 INFO 日志（WARNING 及以上仍会显示）
logging.getLogger("timm").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    logger.info("启动遥感图像分类API服务...")

    # 导入共享状态（模型加载）
    global classifiers
    try:
        # 动态导入，避免启动失败
        from .shared import classifiers as loaded_classifiers

        classifiers = loaded_classifiers
        logger.info(f"成功加载 {len(classifiers)} 个模型")
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        classifiers = {}

    yield

    # 关闭时
    logger.info("关闭API服务...")


# 创建FastAPI应用
app = FastAPI(
    title="遥感图像土地利用分类 API (SPA版本)",
    description="基于深度学习的遥感图像分类服务 - 前后端分离架构",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 添加中间件

# 1. CORS中间件（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# 2. GZip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. 请求日志中间件
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000

        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {process_time:.2f}ms"
        )

        return response


app.add_middleware(RequestLoggingMiddleware)

# 导入路由
# 注意：由于循环导入问题，我们在lifespan之后导入
from .routes import (
    health,
    models,
    predict,
    evaluation,
    visualization,
    train,
    auth,
    history,
)

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["系统状态"])
app.include_router(models.router, prefix="/api/v1", tags=["模型信息"])
app.include_router(predict.router, prefix="/api/v1", tags=["预测功能"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["评估分析"])
app.include_router(visualization.router, prefix="/api/v1", tags=["可视化"])
app.include_router(train.router, prefix="/api/v1", tags=["训练功能"])
app.include_router(auth.router, prefix="/api/v1")
app.include_router(history.router, prefix="/api/v1")


# 根路径重定向到文档
@app.get("/")
async def root():
    return {"message": "遥感图像分类API服务", "docs": "/docs", "version": "2.0.0"}


# 全局错误处理器
from fastapi import HTTPException
from fastapi.responses import JSONResponse


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"},
    )
