#!/bin/bash
# 遥感图像分类系统 - 部署脚本
# 用于生产环境部署和开发环境启动

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "命令 '$1' 未找到，请先安装"
        exit 1
    fi
}

# 显示使用说明
show_help() {
    cat << EOF
遥感图像分类系统部署脚本

使用方法: $0 [命令]

可用命令:
  build         构建Docker镜像
  start         启动服务 (docker-compose up)
  stop          停止服务 (docker-compose down)
  restart       重启服务
  logs          查看日志
  status        查看服务状态
  test          运行测试
  clean         清理构建缓存和镜像
  help          显示此帮助信息

环境变量:
  创建 .env 文件并设置以下变量:
  - MODELS_PATH: 模型目录路径 (默认: /home/zhouh/biye/models)
  - DATA_PATH: 数据目录路径 (默认: /home/zhouh/biye/data)
  - VITE_API_BASE_URL: 前端API基础URL

示例:
  $0 build      # 构建镜像
  $0 start      # 启动服务
  $0 logs       # 查看日志
EOF
}

# 构建Docker镜像
build_images() {
    print_info "构建Docker镜像..."
    
    # 检查后端依赖
    if [ ! -f "backend/pyproject.toml" ]; then
        print_error "后端依赖文件不存在: backend/pyproject.toml"
        exit 1
    fi
    
    # 检查前端依赖
    if [ ! -f "frontend/package.json" ]; then
        print_error "前端依赖文件不存在: frontend/package.json"
        exit 1
    fi
    
    # 构建后端镜像
    print_info "构建后端镜像..."
    docker build -t remote-sensing-api:latest ./backend
    
    # 构建前端镜像
    print_info "构建前端镜像..."
    docker build -t remote-sensing-frontend:latest ./frontend
    
    print_info "镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."
    
    # 检查.env文件
    if [ ! -f ".env" ]; then
        print_warning "未找到 .env 文件，使用示例配置"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_info "已创建 .env 文件，请根据实际情况修改"
        fi
    fi
    
    # 检查模型和数据目录
    if [ ! -d "${MODELS_PATH:-/home/zhouh/biye/models}" ]; then
        print_warning "模型目录不存在: ${MODELS_PATH:-/home/zhouh/biye/models}"
        print_warning "服务可能无法正常启动"
    fi
    
    if [ ! -d "${DATA_PATH:-/home/zhouh/biye/data}" ]; then
        print_warning "数据目录不存在: ${DATA_PATH:-/home/zhouh/biye/data}"
        print_warning "服务可能无法正常启动"
    fi
    
    # 启动服务
    docker-compose up -d
    
    # 等待服务启动
    sleep 5
    
    # 检查服务状态
    check_services_status
    
    print_info "服务启动完成"
    print_info "前端访问地址: http://localhost"
    print_info "后端API地址: http://localhost:8000"
    print_info "API文档: http://localhost:8000/docs"
}

# 停止服务
stop_services() {
    print_info "停止服务..."
    docker-compose down
}

# 重启服务
restart_services() {
    stop_services
    sleep 2
    start_services
}

# 查看日志
show_logs() {
    local service=$1
    if [ -z "$service" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f $service
    fi
}

# 检查服务状态
check_services_status() {
    print_info "服务状态检查..."
    
    # 检查后端健康状态
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_info "后端API: 运行正常"
    else
        print_error "后端API: 无法访问"
    fi
    
    # 检查前端健康状态
    if curl -s http://localhost > /dev/null 2>&1; then
        print_info "前端应用: 运行正常"
    else
        print_error "前端应用: 无法访问"
    fi
    
    # 显示容器状态
    echo ""
    docker-compose ps
}

# 运行测试
run_tests() {
    print_info "运行系统测试..."
    
    # 检查后端API
    print_info "测试后端API健康检查..."
    if curl -s http://localhost:8000/api/v1/health | grep -q "status.*ok"; then
        print_info "✓ 后端健康检查通过"
    else
        print_error "✗ 后端健康检查失败"
    fi
    
    # 测试模型列表
    print_info "测试模型列表API..."
    if curl -s http://localhost:8000/api/v1/models | grep -q "efficientnet_b0"; then
        print_info "✓ 模型列表API通过"
    else
        print_error "✗ 模型列表API失败"
    fi
    
    # 测试前端访问
    print_info "测试前端访问..."
    if curl -s http://localhost | grep -q "<!DOCTYPE html>"; then
        print_info "✓ 前端访问通过"
    else
        print_error "✗ 前端访问失败"
    fi
    
    print_info "测试完成"
}

# 清理构建缓存
clean_build() {
    print_info "清理构建缓存..."
    
    # 停止并删除容器
    docker-compose down
    
    # 删除Docker镜像
    docker rmi remote-sensing-api:latest remote-sensing-frontend:latest 2>/dev/null || true
    
    # 清理前端node_modules
    if [ -d "frontend/node_modules" ]; then
        rm -rf frontend/node_modules
        print_info "已删除 frontend/node_modules"
    fi
    
    # 清理前端构建目录
    if [ -d "frontend/dist" ]; then
        rm -rf frontend/dist
        print_info "已删除 frontend/dist"
    fi
    
    # 清理后端虚拟环境
    if [ -d "backend/.venv" ]; then
        rm -rf backend/.venv
        print_info "已删除 backend/.venv"
    fi
    
    # 清理日志目录
    if [ -d "logs" ]; then
        rm -rf logs
        print_info "已删除 logs 目录"
    fi
    
    print_info "清理完成"
}

# 主函数
main() {
    local command=$1
    
    # 检查必要命令
    check_command docker
    check_command docker-compose
    
    case $command in
        build)
            build_images
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs $2
            ;;
        status)
            check_services_status
            ;;
        test)
            run_tests
            ;;
        clean)
            clean_build
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知命令: $command"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

main "$@"