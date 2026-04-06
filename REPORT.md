# 遥感图像土地利用分类系统 - v1.0.0 里程碑报告

## 项目概述

本项目旨在开发一个基于深度学习的遥感图像土地利用分类 Web 系统。系统采用现代化的前后端分离架构，集成了 EfficientNet-B0 (CNN) 和 Swin Transformer (ViT) 等多种深度学习模型，提供从模型训练、推理预测到可视化分析的全流程功能。

**当前版本**: v1.1.0  
**更新日期**: 2026-04-07  
**项目状态**: ✅ v1.1.0 发布，新增数据库与用户鉴权系统

---

## 📊 架构演进 (v0.1.0 → v1.0.0)

| 模块 | v0.1.0 (初始重构) | v0.2.0 (功能完善) | v0.3.0 (容器化) | v1.0.0 (正式发布) |
| :--- | :--- | :--- | :--- | :--- |
| **包结构** | 扁平结构 | 相对导入重构 | 标准双层结构 | 核心 lib 模块纳入版本控制 |
| **部署方式** | Docker Compose | 脚本辅助 | Podman Pod | ghcr.io 镜像仓库 + podman-compose |
| **训练系统** | 基础训练循环 | CLI 工具、安全中断 | Warmup、梯度裁剪、早停修复 | 稳定可用 |
| **前端配置** | 硬编码 API | 环境变量支持 | 容器自适应 | Vite Plus 统一工具链 |
| **可视化** | 基础图表 | ROC 修复、特征图 | 模型架构展示、特征图预生成 | 准确率显示修复 |
| **测试覆盖** | 无 | 无 | 无 | 后端 pytest + 前端 Vitest |
| **CI/CD** | 无 | 无 | 无 | GitHub Actions 自动化 |
| **开源协议** | 无 | 无 | 无 | MIT License |

---

## 🛠️ 技术栈

### 后端 (Python)
- **框架**: FastAPI (高性能异步 API)
- **深度学习**: PyTorch 2.5 + Timm (模型库)
- **包管理**: uv (极速 Python 包管理器)
- **容器化**: Podman + Nginx (反向代理)

### 前端 (TypeScript)
- **框架**: React 19 + TypeScript
- **构建工具**: Vite Plus (统一工具链)
- **可视化**: Recharts (图表库)
- **状态管理**: TanStack Query (服务端状态)
- **测试**: Vitest + Testing Library

### 基础设施
- **CI/CD**: GitHub Actions (push/PR 自动测试 + 构建检查)
- **镜像仓库**: GitHub Container Registry (ghcr.io)
- **开源协议**: MIT License

---

## 🧪 测试与验证数据

### 1. 模型性能指标
在 EuroSAT 数据集上进行了完整训练与评估：

| 模型 | 参数量 | 训练轮数 | 最佳验证准确率 | 测试准确率 | 平均推理时间 (RTX 3050) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **EfficientNet-B0** | ~5.3M | 30 | 98.47% | 98.72% | 5.76 ms |
| **Swin Transformer** | ~28.3M | 50 | 98.50% | 98.20% | 8.17 ms |
| **Swin Feature** | ~7.7K (可训练) | 30 | 91.90% | 91.50% | 8.38 ms |

> 注：推理时间通过 `benchmark_inference.py` 脚本进行 50 次推理取平均值获得，数据真实可信。

### 2. 系统稳定性测试
- ✅ **并发预测**: 支持多用户同时上传图像，缓存系统有效降低重复计算。
- ✅ **批量处理**: 成功处理 50 张图像批量预测，具备错误隔离能力。
- ✅ **异常恢复**: 训练过程中断 (Ctrl+C) 后，模型权重与历史记录均完整保存。
- ✅ **基准测试**: 提供 `benchmark_inference.py` 脚本，支持 GPU 预热、多次推理取平均、统计标准差。

### 3. 测试覆盖
- **后端**: pytest + pytest-cov，覆盖健康检查、模型端点、预测端点、训练端点、配置系统
- **前端**: Vitest + Testing Library，覆盖 Button/Card 核心组件
- **CI**: GitHub Actions 自动运行前后端测试和构建检查

---

## 🚀 部署方案

### 方案一：一键启动（推荐）

```bash
git clone https://github.com/zuazhk/remote-sensing-land-classification.git
cd remote-sensing-land-classification
podman-compose up -d
```

**服务地址**:
- 前端: http://localhost:8080
- 后端 API: http://localhost:8000

### 方案二：单独拉取镜像

```bash
# 后端（包含模型权重，约 500MB）
podman pull ghcr.io/zuazhk/remote-sensing-land-classification/backend:v1.0.0

# 前端
podman pull ghcr.io/zuazhk/remote-sensing-land-classification/frontend:v1.0.0
```

### 方案三：本地开发

```bash
# 启动后端
cd backend && uv run python -m backend

# 启动前端
cd frontend && npm install && vp dev
```

---

## 📅 下一步计划 (v2.0.0)

1. **容器化增强** — 将 PostgreSQL 纳入 podman-compose，实现全栈容器化
2. **前端功能完善** — 预测历史记录页面、用户个人中心
3. **权限管理** — 管理员/普通用户角色区分
4. **性能优化** — 推理接口异步化、缓存策略优化

---

**报告人**: zuazhk  
**日期**: 2026-04-07
