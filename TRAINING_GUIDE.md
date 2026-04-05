# 模型训练指南

本文档介绍如何使用本项目训练遥感图像分类模型。

## 快速开始

在 `backend/` 目录下执行：

```bash
cd ~/remote-sensing-spa/backend
uv run python -m backend.training.train_cli --model efficientnet_b0 --epochs 30
```

## 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--model` | str | **必填** | 模型名称：`efficientnet_b0`, `swin_tiny`, `swin_tiny_feature` |
| `--epochs` | int | 30 | 训练轮数 |
| `--batch-size` | int | 32 | 批次大小 |
| `--lr` | float | 0.0001 | 学习率 |
| `--weight-decay` | float | 0.01 | 权重衰减（L2 正则化），防止过拟合 |
| `--patience` | int | 10 | 早停耐心值：验证准确率不提升的最大轮数（0=禁用） |
| `--image-size` | int | 224 | 输入图像尺寸 |
| `--device` | str | 自动 | 指定设备：`cpu` 或 `cuda` |
| `--skip-eval` | flag | False | 跳过训练后的评估 |
| `--data-dir` | str | 默认路径 | 数据集目录路径 |

## 硬件要求

| 硬件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| GPU | NVIDIA GPU (4GB 显存) | RTX 3050 / 3060 (6GB+) |
| CPU | 4 核 | 8 核+ |
| 内存 | 8GB | 16GB+ |
| 磁盘 | 10GB 可用空间 | SSD |

> **RTX 3050 (4GB 显存) 用户注意**：训练 Swin Transformer 时请将 `--batch-size` 降至 **16**，防止显存溢出 (OOM)。

## 预训练权重

项目使用 `timm` 库自动下载预训练权重。首次训练时会自动联网下载，后续训练直接复用本地缓存。

> **提示**：权重文件保存在 PyTorch 默认缓存目录，无需手动管理。
> **下载失败？** 设置国内镜像源：`export HF_ENDPOINT=https://hf-mirror.com`

## 基准测试 (Benchmark)

项目提供 `benchmark_inference.py` 脚本，用于获取模型的真实推理耗时。

```bash
cd ~/remote-sensing-spa/backend
uv run python -m backend.scripts.benchmark_inference
```

**脚本逻辑**：
1.  **预热 (Warmup)**: 先跑 10 次，让 GPU 进入最佳状态。
2.  **基准测试**: 跑 50 次，记录每次耗时。
3.  **统计**: 输出平均耗时、最快耗时和最慢耗时。

## 模型推荐配置

### EfficientNet-B0 (CNN)
适合快速训练和基线对比，参数量小（约 530 万）。

```bash
uv run python -m backend.training.train_cli \
    --model efficientnet_b0 \
    --epochs 30 \
    --lr 0.0001 \
    --weight-decay 0.01 \
    --patience 10
```
**预计时间**：30-45 分钟（GPU）

### Swin Transformer Tiny (完整训练)
适合追求更高精度，参数量大（约 2750 万）。

```bash
uv run python -m backend.training.train_cli \
    --model swin_tiny \
    --epochs 50 \
    --batch-size 16 \
    --lr 0.0005 \
    --weight-decay 0.05 \
    --patience 10
```
**预计时间**：2-4 小时（GPU）

> **显存不足？** 如果仍然 OOM，将 `--batch-size` 降至 **8**。

### Swin Transformer Tiny (仅训练分类头)
适合快速验证，仅训练最后的全连接层（7690 个参数）。

```bash
uv run python -m backend.training.train_cli \
    --model swin_tiny_feature \
    --epochs 30 \
    --lr 0.0001 \
    --weight-decay 0.01 \
    --patience 5
```
**预计时间**：15-20 分钟（GPU）

## 训练输出解读

训练过程中会显示以下信息：

```
[1/30] (3.3%)
  训练 - 损失: 0.5234  准确率: 85.23%
  验证 - 损失: 0.2156  准确率: 93.45%
  学习率: 0.000099
  耗时: 45.2s  预估剩余: 21m30s
  ✓ 保存最佳模型 (验证准确率: 93.45%)
```

- **训练准确率**：模型在训练集上的表现
- **验证准确率**：模型在验证集上的表现（决定是否保存模型）
- **学习率**：当前学习率（使用余弦退火调度逐渐降低）
- **耗时/预估剩余**：本轮用时和预计完成时间

## 常见问题

### 1. 过拟合（训练准确率高，验证准确率下降）
**症状**：训练准确率接近 100%，但验证准确率停滞或下降。
**解决**：
- 增加 `--weight-decay`（如 0.05 或 0.1）
- 减少 `--epochs`
- 使用 `--patience` 启用早停

### 2. 训练速度突然变慢
**原因**：笔记本锁屏导致 GPU 降频。
**解决**：训练时保持屏幕常亮，Windows 设置 → 电源 → 屏幕关闭设为"从不"。

### 3. 安全中断训练
按 `Ctrl+C` 可安全中断训练，系统会自动保存当前最佳模型和训练历史。

### 4. 下载预训练权重失败
**解决**：设置国内镜像源
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 5. 显存溢出 (OOM)
**症状**：训练开始后立即崩溃，提示 `CUDA out of memory`。
**解决**：
- 降低 `--batch-size`（Swin Transformer 从 32 降到 16 或 8）
- 关闭其他占用显存的程序

### 4. 下载预训练权重失败
**解决**：设置国内镜像源
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

## 文件保存位置

| 类型 | 路径 |
|------|------|
| 模型权重 | `backend/models/{model_key}/best_model.pth` |
| 训练历史 | `backend/training/history/{model_key}_history.json` |
| 评估结果 | `backend/models/{model_key}/evaluation_results.json` |
| 特征图 | `backend/models/{model_key}/feature_maps/` |

## 查看训练历史

训练完成后可在前端"可视化分析 → 训练历史"标签页查看曲线图。
