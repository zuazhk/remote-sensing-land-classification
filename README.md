# 遥感图像土地利用分类系统 - 前后端分离版本

现代前后端分离版本的遥感图像分类系统，基于原始毕业设计项目重构，专为求职作品集设计。

## 项目概述

本项目将原始前后端不分离的毕业设计项目重构为现代前后端分离架构，保留所有核心功能，采用最新的技术栈重新实现。

### 核心特性

- **前后端分离架构**: RESTful API + SPA前端，清晰的责任分离
- **现代化技术栈**: 
  - 后端: FastAPI + PyTorch + Python 3.12 + uv
  - 前端: React + TypeScript + vite-plus v0.1.15
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
│   ├── backend/             # Python包（标准双层结构）
│   │   ├── lib/             # 模型定义、配置、推理模块
│   │   ├── routes/          # API路由模块
│   │   ├── training/        # 模型训练模块
│   │   ├── scripts/         # 工具脚本
│   │   ├── models/          # 模型权重文件（不提交到git）
│   │   ├── main.py          # FastAPI主应用
│   │   └── __main__.py      # 模块入口
│   ├── pyproject.toml       # Python项目配置
│   ├── Containerfile        # Podman容器构建文件
│   └── .dockerignore        # 容器构建排除文件
├── frontend/                # React前端
│   ├── src/
│   │   ├── pages/           # 页面组件
│   │   ├── components/      # 可复用组件
│   │   └── config/          # 配置文件
│   ├── Containerfile        # Podman容器构建文件
│   └── .dockerignore        # 容器构建排除文件
├── deploy.sh                # Podman Pod一键部署脚本
└── README.md                # 本文件
```

## 快速开始

### 前提条件

- Python 3.12+ 和 Node.js 18+
- Git
- uv（Python 包管理器）

### 1. 启动后端服务

```bash
cd remote-sensing-spa/backend
uv run python -m backend
```

后端服务将在 http://0.0.0.0:8000 启动，API文档:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 2. 启动前端开发服务器

```bash
cd remote-sensing-spa/frontend
npm install                  # 安装依赖（首次运行）
vp dev                       # 启动开发服务器
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
| `/api/v1/visualization/feature-map/{model_key}/{layer}/{channel}` | GET | 获取特征图图像 (PNG格式) |
| `/api/v1/visualization/architecture/{model_key}` | GET | 获取模型架构信息 |
| `/api/v1/evaluation/metrics/{model_key}` | GET | 获取模型评估指标 |

完整的API文档请访问 http://localhost:8000/docs。

## 前端功能

### 页面导航

1. **模型架构**: 查看模型层结构、超参数、性能指标（默认标签页）
2. **图像分类**: 上传图像进行单图或批量分类预测
3. **模型对比**: 可视化比较不同模型的性能指标
4. **混淆矩阵**: 查看模型分类混淆矩阵
5. **ROC曲线**: 查看模型ROC曲线和AUC指标
6. **训练历史**: 查看训练/验证损失和准确率曲线
7. **特征可视化**: 查看模型各层特征图激活模式

### 技术特点

- **响应式设计**: 适配桌面和移动设备
- **实时交互**: 基于React Query的状态管理
- **图表可视化**: 使用Recharts库展示数据
- **类型安全**: TypeScript全面类型检查
- **现代化构建**: Vite快速构建和热重载

## 部署指南

### Podman Pod 一键部署（推荐）

项目使用 Podman Pod 进行容器化部署，将前端、后端、数据库放在同一个网络组中。

```bash
# 构建镜像
./deploy.sh build

# 启动服务（自动创建 Pod + 3个容器）
./deploy.sh start

# 查看状态
./deploy.sh status

# 查看日志
./deploy.sh logs rs-backend

# 停止服务
./deploy.sh stop

# 清理所有
./deploy.sh clean
```

服务访问地址:
- 前端应用: http://localhost:8080
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 数据库: localhost:5432

### 容器架构

```
Pod: remote-sensing-pod
├── 端口 8080 → 前端 (Nginx，代理 /api/ 到后端)
├── 端口 8000 → 后端 (FastAPI + PyTorch)
├── 端口 5432 → PostgreSQL 16
│
├── 容器: rs-db (PostgreSQL)
├── 容器: rs-backend (FastAPI)
└── 容器: rs-frontend (Nginx)
```

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

### v0.3.0 (2026-04-04)

#### 架构改进
- **标准包结构**: 调整为 `backend/backend/` 双层目录结构，符合 Python 包规范
- **统一启动命令**: 本地和容器都使用 `uv run python -m backend`
- **预训练权重优化**: 改为 `pretrained=False`，直接加载 `best_model.pth`，启动无需联网

#### 容器化部署
- **Podman Pod 部署**: 新增 `deploy.sh` 一键部署脚本
- **Containerfile**: 后端和前端容器构建文件
- **Nginx 代理配置**: 前端容器自动代理 `/api/` 到后端
- **PostgreSQL 集成**: 数据库容器已就绪（待鉴权功能开发）

#### 前端优化
- **容器适配**: 开发环境用完整 URL，生产环境用相对路径 `/api/v1`
- **模型架构展示**: 新增"模型架构"标签页（默认），展示层结构、超参数、性能指标
- **层卡片颜色区分**: 卷积层(蓝)、注意力层(紫)、池化层(橙)、分类头(绿)
- **CNN 分组折叠**: EfficientNet 按 Stage 分组，点击展开查看详情
- **ROC 曲线修复**: 使用线性插值解决数据点长度不一致导致的显示异常
- **特征可视化**: 预生成特征图，支持层选择和通道浏览

#### 后端优化
- **训练系统**: 新增 `train_cli.py` 命令行训练工具
- **训练保护**: 支持安全中断（Ctrl+C），自动保存最佳模型和训练历史
- **训练输出优化**: 显示进度百分比、每轮耗时、预估剩余时间
- **防覆盖逻辑**: 新模型未超过旧模型时不覆盖
- **特征图生成**: 新增 `generate_feature_maps.py` 脚本

### v0.2.0 (2026-04-02)

#### 后端改进
- **导入系统重构**: 所有导入改为相对导入，移除 `sys.path` hack
- **启动方式优化**: 支持 `uv run python -m backend` 启动
- **批量处理增强**: 新增 `failed` 字段，返回失败文件数量

#### 前端改进
- **API配置中心化**: 创建 `src/config/api.ts`，统一管理API端点
- **环境变量支持**: 使用 `VITE_API_BASE_URL` 环境变量配置API地址
- **vite-plus 升级**: 从 v0.1.11 升级到 v0.1.15
  - vite: 8.0.0 → 8.0.3
  - rolldown: 1.0.0-rc.9 → 1.0.0-rc.12
  - vitest: 4.1.0 → 4.1.2
  - oxfmt: 0.40.0 → 0.43.0
  - oxlint: 1.55.0 → 1.58.0
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
- 构建工具: vite-plus v0.1.15（包含 vite v8.0.3）

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过GitHub Issues提交反馈。

---

**注意**: 本项目为毕业设计重构版本，主要用于技术演示和求职作品集展示。生产环境部署前请进行充分测试和安全评估。