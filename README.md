# 遥感图像土地利用分类系统

基于深度学习的遥感图像分类 Web 系统。本项目为毕业设计的前后端分离重构版本，采用现代化技术栈重新实现。

## ✨ 核心特性

- **多模型支持**: EfficientNet-B0 (CNN), Swin Transformer (ViT), 以及轻量级特征提取器
- **可视化分析**: 混淆矩阵、ROC 曲线、训练历史、特征图可视化、模型架构展示
- **容器化部署**: 基于 Podman 的一键部署方案，镜像托管于 GitHub Container Registry
- **工程化规范**: 类型安全 (TypeScript/Pydantic)、早停机制、梯度裁剪、学习率预热
- **真实基准测试**: 提供 `benchmark_inference` 脚本，获取真实推理耗时数据
- **测试覆盖**: 后端 pytest + 前端 Vitest，GitHub Actions 自动 CI

## 📊 模型性能指标 (RTX 3050 Laptop)

| 模型 | 参数量 | 最佳验证准确率 | 平均推理时间 |
| :--- | :--- | :--- | :--- |
| **EfficientNet-B0** | ~5.3M | 98.47% | 5.76 ms |
| **Swin Transformer** | ~28.3M | 98.50% | 8.17 ms |
| **Swin Feature** | ~7.7K (可训练) | 91.90% | 8.38 ms |

## 🚀 快速开始

### 方式一：容器化部署（推荐）

```bash
git clone https://github.com/zuazhk/remote-sensing-land-classification.git
cd remote-sensing-land-classification
podman-compose up -d
```

**服务地址**:
- 前端: http://localhost:8080
- 后端 API: http://localhost:8000

### 方式二：本地开发

**启动后端**:
```bash
cd backend
uv run python -m backend
```
*   **API 文档**: http://localhost:8000/docs
*   **硬件要求**: NVIDIA GPU (推荐 RTX 3050 及以上，4GB+ 显存)

**启动前端**:
```bash
cd frontend
npm install  # 首次运行
vp dev
```
*   **访问地址**: http://localhost:5173

## 🧪 测试

### 后端测试
```bash
cd backend
uv run pytest              # 运行所有测试
uv run pytest --cov        # 生成覆盖率报告
```

### 前端测试
```bash
cd frontend
npm test                   # 运行所有测试
npm run test:watch         # 监听模式（开发时使用）
```

## 📚 文档索引

| 文档 | 描述 |
| :--- | :--- |
| **[模型训练指南](TRAINING_GUIDE.md)** | 如何训练模型、参数调优、硬件适配 |
| **[里程碑报告](REPORT.md)** | 项目架构演进、技术栈、测试数据、部署方案 |

## 🛠️ 技术栈

-   **后端**: FastAPI, PyTorch, Timm
-   **前端**: React, TypeScript, Recharts, Vite Plus
-   **部署**: Podman, Nginx, GitHub Container Registry
-   **测试**: pytest + pytest-cov (后端), Vitest + Testing Library (前端)
-   **CI/CD**: GitHub Actions (push/PR 自动测试 + 构建检查)

## 📜 更新日志

### v1.1.0 (2026-04-07) - 数据库与鉴权
-   **数据库**: 引入 PostgreSQL + SQLAlchemy + Alembic
-   **鉴权**: 用户注册/登录/JWT 鉴权系统
-   **历史**: 预测记录自动持久化，支持登录用户查询历史记录
-   **前端**: 新增登录/注册页面，导航栏显示登录状态
-   **修复**: 预测页面 Token 缺失导致历史记录未保存

### v1.0.0 (2026-04-06) - 正式发布
-   **发布**: v1.0.0 稳定版本，核心功能完整
-   **部署**: 前后端镜像推送至 ghcr.io，提供 podman-compose.yml 一键启动
-   **测试**: 引入后端 pytest 和前端 Vitest 测试框架
-   **CI**: GitHub Actions 自动化测试和构建检查
-   **修复**: 准确率显示错误、容器网络不可达、模块导入缺失等多项 Bug
-   **文档**: 整合历史报告为 v1.0.0 里程碑报告
-   **协议**: MIT License 开源许可证

---

**注意**: 本项目为毕业设计的前后端分离重构版本。生产环境部署前请进行充分测试。
