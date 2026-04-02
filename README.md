# 遥感图像土地利用分类系统 - 前后端分离版本

现代前后端分离版本的遥感图像分类系统，基于原始毕业设计项目重构，专为求职作品集设计。

## 项目概述

本项目将原始前后端不分离的毕业设计项目重构为现代前后端分离架构，保留所有核心功能，采用最新的技术栈重新实现。

### 核心特性

- **前后端分离架构**: RESTful API + SPA前端，清晰的责任分离
- **现代化技术栈**: 
  - 后端: FastAPI + PyTorch + Python 3.12
  - 前端: React + TypeScript + Vite 6.2.0
- **完整的功能迁移**:
  - 图像分类预测 (单图/批量)
  - 多模型对比分析
  - 可视化分析 (混淆矩阵、ROC曲线、训练历史)
  - 模型性能评估
- **开发者友好**: 完整的API文档，清晰的代码结构，易于扩展

## 项目结构

```
remote-sensing-spa/
├── backend/                 # FastAPI后端
│   ├── lib/                # 原始项目模块（只读引用）
│   ├── routes/             # API路由模块
│   ├── config.py           # 配置文件
│   ├── main.py             # FastAPI主应用
│   ├── shared.py           # 共享状态和配置
│   └── pyproject.toml      # Python项目配置
├── frontend/               # React前端
│   ├── src/
│   │   ├── pages/          # 页面组件
│   │   ├── components/     # 可复用组件
│   │   └── App.tsx         # 主应用组件
│   └── package.json        # 前端依赖
├── scripts/                # 启动脚本
├── shared/                 # 共享资源
├── docs/                   # 项目文档
└── README.md               # 本文件
```

## 快速开始

### 前提条件

- Python 3.12+ 和 Node.js 18+
- Git

### 1. 启动后端服务

```bash
cd remote-sensing-spa/backend
uv venv .venv                # 创建虚拟环境
source .venv/bin/activate    # 激活虚拟环境
pip install -e .             # 安装依赖
uvicorn backend.main:app --host 127.0.0.1 --port 8001 --reload
```

或者使用脚本:
```bash
./scripts/start-backend.sh
```

后端服务将在 http://127.0.0.1:8001 启动，API文档:
- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc

### 2. 启动前端开发服务器

```bash
cd remote-sensing-spa/frontend
npm install                  # 安装依赖
npm run dev                  # 启动开发服务器
```

或者使用脚本:
```bash
./scripts/start-frontend.sh
```

前端服务将在 http://localhost:5173 启动。

## API接口

### 主要端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/health` | GET | 服务健康检查 |
| `/api/v1/models` | GET | 获取可用模型列表 |
| `/api/v1/predict` | POST | 单图像分类预测 |
| `/api/v1/predict/batch` | POST | 批量图像分类预测 (最多50张) |
| `/api/v1/predict/compare` | POST | 多模型对比预测 |
| `/api/v1/visualization/model-comparison` | GET | 获取模型对比数据 |
| `/api/v1/visualization/confusion-matrix/{model_key}` | GET | 获取混淆矩阵数据 |
| `/api/v1/visualization/roc-curves/{model_key}` | GET | 获取ROC曲线数据 |
| `/api/v1/visualization/training-history/{model_key}` | GET | 获取训练历史数据 |
| `/api/v1/visualization/feature-visualization/{model_key}` | GET | 获取特征可视化数据 |
| `/api/v1/visualization/feature-map/{model_key}/{layer}/{channel}` | GET | 获取特征图图像 (SVG格式) |
| `/api/v1/evaluation/metrics/{model_key}` | GET | 获取模型评估指标 |
| `/api/v1/evaluation/detailed/{model_key}` | GET | 获取详细评估报告 |

完整的API文档请访问 http://127.0.0.1:8001/docs。

## 前端功能

### 页面导航

1. **首页**: 项目介绍和功能概览
2. **图像分类**: 上传图像进行单图或批量分类预测
3. **模型对比**: 可视化比较不同模型的性能指标
4. **可视化分析**: 深入分析模型性能，包括混淆矩阵、ROC曲线、训练历史等

### 技术特点

- **响应式设计**: 适配桌面和移动设备
- **实时交互**: 基于React Query的状态管理
- **图表可视化**: 使用Recharts库展示数据
- **类型安全**: TypeScript全面类型检查
- **现代化构建**: Vite快速构建和热重载

## 部署指南

### 环境变量配置

项目使用环境变量进行配置。复制 `.env.example` 为 `.env` 并根据实际情况修改:

```bash
cp .env.example .env
```

主要环境变量:
- `MODEL_PATH_PREFIX`: 模型目录路径 (默认: `/home/zhouh/biye/models`)
- `DATA_PATH_PREFIX`: 数据目录路径 (默认: `/home/zhouh/biye/data`)
- `VITE_API_BASE_URL`: 前端API基础URL (开发: `http://localhost:8000/api/v1`, 生产: `/api/v1`)
- `API_HOST`/`API_PORT`: 后端服务绑定地址和端口

### 使用部署脚本 (推荐)

项目提供了完整的部署脚本 `deploy.sh`，支持多种操作:

```bash
# 查看帮助
./deploy.sh help

# 构建Docker镜像
./deploy.sh build

# 启动服务 (使用Docker Compose)
./deploy.sh start

# 查看服务状态
./deploy.sh status

# 查看日志
./deploy.sh logs

# 运行系统测试
./deploy.sh test

# 停止服务
./deploy.sh stop

# 清理构建缓存
./deploy.sh clean
```

### Docker Compose 部署 (推荐)

使用 Docker Compose 可以一键启动完整的服务栈:

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务访问地址:
- 前端应用: http://localhost
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 手动部署

#### 后端部署

1. 安装生产依赖:
   ```bash
   cd backend
   pip install -e . --no-dev
   ```

2. 使用Gunicorn启动服务:
   ```bash
   gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
   ```

3. 配置反向代理 (Nginx):
   ```nginx
   location /api/ {
       proxy_pass http://127.0.0.1:8000;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

#### 前端部署

1. 构建生产版本:
   ```bash
   cd frontend
   npm run build
   ```

2. 配置静态文件服务 (Nginx):
   ```nginx
   location / {
       root /path/to/frontend/dist;
       try_files $uri $uri/ /index.html;
   }
   ```

## 开发指南

### 代码规范

- **Python**: 使用Ruff进行代码格式化和linting
- **TypeScript**: 使用ESLint和Prettier
- **Git提交**: 遵循Conventional Commits规范

### 添加新功能

1. **后端API**:
   - 在 `backend/routes/` 添加新的路由模块
   - 在 `backend/routes/schemas.py` 定义请求/响应模型
   - 更新 `backend/main.py` 注册新路由

2. **前端页面**:
   - 在 `frontend/src/pages/` 添加新页面组件
   - 在 `frontend/src/App.tsx` 添加路由配置
   - 在 `frontend/src/components/` 添加可复用组件

### 测试

```bash
# 后端测试
cd backend
pytest tests/

# 前端测试
cd frontend
npm test
```

## 项目背景

本项目基于原始毕业设计项目 `/home/zhouh/biye` 重构，保留了所有核心功能:
- 遥感图像分类 (EuroSAT数据集)
- 多模型支持 (EfficientNet-B0, Swin Transformer)
- 完整的训练和评估流程
- 丰富的可视化功能

重构原则:
1. **不修改原始项目**: 原始项目作为只读参考，所有文件保持不变
2. **现代技术栈**: 采用当前主流的前后端分离架构
3. **求职作品集导向**: 展示全栈开发能力和深度学习应用经验
4. **完整功能迁移**: 确保所有原始功能在新架构中可用

## 更新日志

### v0.2.0 (2026-04-02)

#### 后端改进
- **导入系统重构**: 所有导入改为相对导入，移除 `sys.path` hack
- **启动方式优化**: 支持 `uv run python -m backend` 启动
- **批量处理增强**: 新增 `failed` 字段，返回失败文件数量

#### 前端改进
- **API配置中心化**: 创建 `src/config/api.ts`，统一管理API端点
- **环境变量支持**: 使用 `VITE_API_BASE_URL` 环境变量配置API地址
- **批量处理优化**: 
  - 添加加载动画和禁用状态
  - 显示成功/失败统计
  - 失败文件列表展示
  - 导出CSV按钮

#### 新增文件
- `backend/__main__.py` - Python模块入口
- `frontend/.env` - 前端环境变量配置
- `frontend/.env.example` - 环境变量示例
- `frontend/src/config/api.ts` - API配置模块

#### 配置说明
- 后端默认端口: `8000`
- 前端API地址: 通过 `VITE_API_BASE_URL` 环境变量配置

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过GitHub Issues提交反馈。

---

**注意**: 本项目为毕业设计重构版本，主要用于技术演示和求职作品集展示。生产环境部署前请进行充分测试和安全评估。