#!/bin/bash
# 遥感图像分类系统 - Podman Pod 部署脚本

set -e

POD_NAME="remote-sensing-pod"
BACKEND_NAME="rs-backend"
FRONTEND_NAME="rs-frontend"
BACKEND_IMAGE="rs-backend"
FRONTEND_IMAGE="rs-frontend"

print_info() { echo -e "\033[0;32m[INFO]\033[0m $1"; }
print_warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }
print_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }

show_help() {
    cat << EOF
遥感图像分类系统 - Podman Pod 部署脚本

使用方法: $0 [命令]

可用命令:
  build         构建后端和前端镜像
  start         启动服务 (创建 Pod + 容器)
  stop          停止服务
  restart       重启服务
  logs          查看日志
  status        查看服务状态
  clean         清理 Pod、容器和镜像
  help          显示此帮助信息

示例:
  $0 build      # 构建镜像
  $0 start      # 启动服务
  $0 status     # 查看状态
EOF
}

# 构建镜像
build_images() {
    print_info "构建后端镜像..."
    podman build -t $BACKEND_IMAGE ./backend

    print_info "构建前端镜像..."
    podman build -t $FRONTEND_IMAGE ./frontend

    print_info "镜像构建完成"
}

# 启动服务
start_services() {
    # 检查 Pod 是否存在
    if podman pod exists $POD_NAME 2>/dev/null; then
        print_info "Pod 已存在，重建中..."
        podman pod rm -f $POD_NAME
    fi

    # 创建 Pod
    if ! podman pod exists $POD_NAME 2>/dev/null; then
        print_info "创建 Pod (端口: 80->前端, 8000->后端)..."
        podman pod create --name $POD_NAME -p 8080:80 -p 8000:8000
    fi


    # 启动后端
    if ! podman ps -a --format '{{.Names}}' | grep -q "^${BACKEND_NAME}$"; then
        print_info "启动后端..."
        podman run -d --pod $POD_NAME --name $BACKEND_NAME $BACKEND_IMAGE
    else
        print_info "后端已存在，启动中..."
        podman start $BACKEND_NAME 2>/dev/null || true
    fi

    # 启动前端
    if ! podman ps -a --format '{{.Names}}' | grep -q "^${FRONTEND_NAME}$"; then
        print_info "启动前端..."
        podman run -d --pod $POD_NAME --name $FRONTEND_NAME $FRONTEND_IMAGE
    else
        print_info "前端已存在，启动中..."
        podman start $FRONTEND_NAME 2>/dev/null || true
    fi

    print_info "服务启动完成！"
    print_info "前端: http://localhost:8080"
    print_info "后端 API: http://localhost:8000"
    print_info "API 文档: http://localhost:8000/docs"
}

# 停止服务
stop_services() {
    print_info "停止 Pod..."
    podman pod stop $POD_NAME 2>/dev/null || true
    print_info "服务已停止"
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
        podman pod logs $POD_NAME
    else
        podman logs -f $service
    fi
}

# 查看状态
check_status() {
    print_info "Pod 状态:"
    podman pod ps --filter "name=$POD_NAME"
    echo ""
    print_info "容器状态:"
    podman ps --pod --filter "pod=$POD_NAME"
    echo ""
    # 健康检查
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        print_info "✓ 后端 API 正常"
    else
        print_error "✗ 后端 API 无法访问"
    fi
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        print_info "✓ 前端正常"
    else
        print_error "✗ 前端无法访问"
    fi
}

# 清理
clean_all() {
    print_info "清理 Pod 和容器..."
    podman pod rm -f $POD_NAME 2>/dev/null || true
    podman rm -f $BACKEND_NAME $FRONTEND_NAME 2>/dev/null || true
    podman rmi $BACKEND_IMAGE $FRONTEND_IMAGE 2>/dev/null || true
    podman volume rm pg_data 2>/dev/null || true
    print_info "清理完成"
}

# 主函数
case "${1:-help}" in
    build) build_images ;;
    start) start_services ;;
    stop) stop_services ;;
    restart) restart_services ;;
    logs) show_logs "$2" ;;
    status) check_status ;;
    clean) clean_all ;;
    help|--help|-h) show_help ;;
    *) print_error "未知命令: $1"; show_help; exit 1 ;;
esac
