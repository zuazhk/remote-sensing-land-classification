#!/bin/bash

# 启动遥感图像分类前端开发服务器

cd "$(dirname "$0")/../frontend"

# 检查node_modules
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动Vite开发服务器
echo "启动前端开发服务器 (http://localhost:5173)..."
echo "按 Ctrl+C 停止服务"
npm run dev