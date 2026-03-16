#!/bin/bash

# 启动遥感图像分类API后端服务

cd "$(dirname "$0")/../backend"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建Python虚拟环境..."
    uv venv .venv
fi

# 激活虚拟环境并安装依赖
source .venv/bin/activate
pip install -e . > /dev/null 2>&1

# 启动FastAPI服务
echo "启动遥感图像分类API服务 (http://127.0.0.1:8001)..."
echo "API文档: http://127.0.0.1:8001/docs"
echo "按 Ctrl+C 停止服务"
uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload