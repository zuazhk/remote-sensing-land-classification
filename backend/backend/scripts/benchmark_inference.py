"""
模型推理性能基准测试脚本
对每个模型进行多次推理，计算平均耗时和标准差
"""

import torch
import time
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.lib.model import get_model
from backend.lib.config import NUM_CLASSES

# 测试配置
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
INPUT_SHAPE = (1, 3, 224, 224)  # 模拟一张 224x224 的 RGB 图像
WARMUP_RUNS = 10  # 预热次数（让 GPU 进入状态）
BENCHMARK_RUNS = 50  # 正式测试次数


def benchmark_model(model_key):
    print(f"\n{'=' * 50}")
    print(f"测试模型: {model_key}")
    print(f"{'=' * 50}")

    # 1. 加载模型
    model = get_model(model_key, num_classes=NUM_CLASSES).to(DEVICE)
    model.eval()

    # 2. 准备随机输入数据
    dummy_input = torch.randn(INPUT_SHAPE).to(DEVICE)

    # 3. 预热 (Warmup)
    print(f"正在进行 {WARMUP_RUNS} 次预热...")
    with torch.no_grad():
        for _ in range(WARMUP_RUNS):
            _ = model(dummy_input)
    if DEVICE == "cuda":
        torch.cuda.synchronize()

    # 4. 正式基准测试
    print(f"正在进行 {BENCHMARK_RUNS} 次推理测试...")
    times = []
    with torch.no_grad():
        for _ in range(BENCHMARK_RUNS):
            start = time.perf_counter()
            _ = model(dummy_input)
            if DEVICE == "cuda":
                torch.cuda.synchronize()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # 转换为毫秒

    # 5. 统计结果
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)

    print(f"✅ 测试结果:")
    print(f"   平均耗时: {avg_time:.2f} ms")
    print(f"   最快耗时: {min_time:.2f} ms")
    print(f"   最慢耗时: {max_time:.2f} ms")

    return avg_time


def main():
    models = ["efficientnet_b0", "swin_tiny", "swin_tiny_feature"]
    results = {}

    print(f"🚀 开始模型推理基准测试 (设备: {DEVICE})")
    for model in models:
        results[model] = benchmark_model(model)

    print(f"\n{'=' * 50}")
    print(f"📊 最终汇总 (平均推理时间):")
    print(f"{'=' * 50}")
    for model, time_ms in results.items():
        print(f"  {model:<25} : {time_ms:.2f} ms")


if __name__ == "__main__":
    main()
