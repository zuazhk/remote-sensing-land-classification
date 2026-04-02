#!/bin/bash
# 遥感图像分类系统 - 后端启动脚本
# 使用 uv run 管理虚拟环境和依赖

set -e

SCRIPT_DIR="$(dirname "$0")"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# 检查 uv 是否安装
if ! command -v uv &> /dev/null; then
    echo "错误: 未找到 uv，请先安装: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# 自动同步依赖（uv sync 会自动创建 .venv 并安装依赖）
echo "同步依赖..."
uv sync --project "$BACKEND_DIR" --dev

# 启动 FastAPI 服务
echo ""
echo "启动遥感图像分类 API 服务..."
echo "  地址: http://0.0.0.0:8001"
echo "  文档: http://0.0.0.0:8001/docs"
echo "  按 Ctrl+C 停止服务"
echo ""

cd "$PROJECT_ROOT" && uv run --project "$BACKEND_DIR" uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
