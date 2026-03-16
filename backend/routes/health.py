"""
健康检查路由
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查端点"""
    from backend.shared import classifiers

    return {
        "status": "ok",
        "models_loaded": len(classifiers),
        "service": "remote-sensing-api",
        "version": "2.0.0",
    }
