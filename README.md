# 遥感图像土地利用分类系统

基于深度学习的遥感图像分类 Web 系统，采用现代化前后端分离架构，专为求职作品集和毕业设计展示设计。

## ✨ 核心特性

- **多模型支持**: EfficientNet-B0 (CNN), Swin Transformer (ViT), 以及轻量级特征提取器
- **可视化分析**: 混淆矩阵、ROC 曲线、训练历史、特征图可视化、模型架构展示
- **容器化部署**: 基于 Podman Pod 的一键部署方案 (前端+后端+数据库)
- **工程化规范**: 类型安全 (TypeScript/Pydantic)、早停机制、梯度裁剪、学习率预热
- **真实基准测试**: 提供 `benchmark_inference` 脚本，获取真实推理耗时数据

## 📊 模型性能指标 (RTX 3050 Laptop)

| 模型 | 参数量 | 最佳验证准确率 | 平均推理时间 |
| :--- | :--- | :--- | :--- |
| **EfficientNet-B0** | ~5.3M | 98.47% | 5.76 ms |
| **Swin Transformer** | ~28.3M | 98.50% | 8.17 ms |
| **Swin Feature** | ~7.7K (可训练) | 91.90% | 8.38 ms |

## 🚀 快速开始

### 1. 启动后端

```bash
cd backend
uv run python -m backend
```
*   **API 文档**: http://localhost:8000/docs
*   **硬件要求**: NVIDIA GPU (推荐 RTX 3050 及以上，4GB+ 显存)

### 2. 启动前端

```bash
cd frontend
npm install  # 首次运行
vp dev
```
*   **访问地址**: http://localhost:5173

## 📦 容器化部署 (推荐)

使用 Podman 一键启动完整服务栈：

```bash
./deploy.sh build   # 构建镜像
./deploy.sh start   # 启动服务
```

**服务地址**:
-   前端: http://localhost:8080
-   后端 API: http://localhost:8000
-   数据库: localhost:5432

## 📚 文档索引

| 文档 | 描述 |
| :--- | :--- |
| **[模型训练指南](TRAINING_GUIDE.md)** | 如何训练模型、参数调优、硬件适配 |
| **[里程碑报告](REPORT-v0.3.0.md)** | 项目技术演进、架构设计、测试数据 |

## 🛠️ 技术栈

-   **后端**: FastAPI, PyTorch, Timm, PostgreSQL (待集成)
-   **前端**: React, TypeScript, Recharts, Vite Plus
-   **部署**: Podman, Nginx
-   **测试**: pytest (后端), 基准测试脚本 (`benchmark_inference.py`)

## 📜 更新日志

### v0.3.1 (2026-04-05)
-   **修复**: 解决 `SwinTinyFeatureExtractor` 预训练权重加载失败问题
-   **修复**: 修正首次训练时错误触发防覆盖逻辑导致测试准确率为 0 的 Bug
-   **优化**: 抑制 `timm` 和 `httpx` 的冗余 INFO 日志，保持控制台整洁
-   **优化**: 更新模型对比数据为真实基准测试结果
-   **优化**: 增强 EfficientNet Block 块的差异化功能描述
-   **新增**: 添加 `benchmark_inference.py` 脚本，支持真实推理耗时测试

### v0.3.0 (2026-04-04)
-   **架构**: 调整为 `backend/backend/` 标准双层包结构
-   **容器化**: 新增 Podman Pod 部署支持
-   **训练优化**: 增加学习率预热 (Warmup)、梯度裁剪、数据增强
-   **可视化**: 新增模型架构展示、特征图预生成
-   **修复**: 修正早停逻辑与训练历史覆盖问题

### v0.2.0 (2026-04-02)
-   **前端**: API 配置中心化，批量处理优化，ROC 曲线修复
-   **后端**: 相对导入重构，训练 CLI 工具

---

**注意**: 本项目为毕业设计重构版本。生产环境部署前请进行充分测试。
