"""
特征图预生成脚本
为每个模型生成代表性特征图并保存为 PNG
"""

import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import numpy as np
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.lib.model import get_model
from backend.lib.config import (
    MODELS_DIR,
    ORIGINAL_DATA_DIR,
    EuroSAT_CLASSES,
    DEFAULT_IMAGE_SIZE,
)


FEATURE_MAP_DIR = Path(__file__).parent.parent / "models"


def normalize_feature_map(feature_map: np.ndarray) -> np.ndarray:
    """归一化特征图到 0-255"""
    f_min = feature_map.min()
    f_max = feature_map.max()
    if f_max - f_min < 1e-6:
        return np.zeros_like(feature_map, dtype=np.uint8)
    return ((feature_map - f_min) / (f_max - f_min) * 255).astype(np.uint8)


def get_sample_image():
    """获取一张代表性样本图像"""
    # 尝试从数据集中找一张图
    data_dirs = [ORIGINAL_DATA_DIR, ORIGINAL_DATA_DIR / "eurosat" / "2750"]
    for data_dir in data_dirs:
        if not data_dir.exists():
            continue
        for cls in EuroSAT_CLASSES[:3]:
            cls_dir = data_dir / cls
            if cls_dir.exists():
                img_files = list(cls_dir.glob("*.jpg")) + list(cls_dir.glob("*.png"))
                if img_files:
                    return img_files[0]
    return None


def generate_feature_maps_for_model(model_key: str):
    """为指定模型生成特征图"""
    print(f"\n{'=' * 60}")
    print(f"  生成特征图: {model_key}")
    print(f"{'=' * 60}")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = get_model(model_key, num_classes=10).to(device)
    model.eval()

    # 加载模型权重
    model_path = MODELS_DIR / model_key / "best_model.pth"
    if model_path.exists():
        model.load_state_dict(
            torch.load(model_path, map_location=device, weights_only=True)
        )
        print(f"✅ 加载模型权重: {model_path}")
    else:
        print(f"⚠️  模型权重不存在: {model_path}，使用随机权重")

    # 获取样本图像
    sample_path = get_sample_image()
    if sample_path is None:
        print("❌ 找不到样本图像")
        return

    print(f"📷 使用样本图像: {sample_path}")

    # 图像预处理
    transform = transforms.Compose(
        [
            transforms.Resize((DEFAULT_IMAGE_SIZE, DEFAULT_IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ]
    )

    image = Image.open(sample_path).convert("RGB")
    input_tensor = transform(image).unsqueeze(0).to(device)

    # 创建保存目录
    save_dir = FEATURE_MAP_DIR / model_key / "feature_maps"
    save_dir.mkdir(parents=True, exist_ok=True)

    # 注册 Hook 提取特征
    feature_maps = {}

    def make_hook(name):
        def hook(module, input, output):
            if isinstance(output, tuple):
                output = output[0]
            feature_maps[name] = output.detach().cpu()

        return hook

    # 根据模型类型注册 Hook
    if model_key == "efficientnet_b0":
        model.model.conv_stem.register_forward_hook(make_hook("conv_stem"))
        for i in range(7):
            blocks = getattr(model.model, f"blocks{i}", None)
            if blocks is not None:
                blocks.register_forward_hook(make_hook(f"blocks_{i}"))
        model.model.conv_head.register_forward_hook(make_hook("conv_head"))
    elif model_key in ("swin_tiny", "swin_tiny_feature"):
        if model_key == "swin_tiny_feature":
            base = model.base_model
        else:
            base = model.model
        base.patch_embed.register_forward_hook(make_hook("patch_embed"))
        for i in range(4):
            layer = getattr(base.layers, f"layers{i}", None)
            if layer is None:
                layer = base.layers[i]
            layer.register_forward_hook(make_hook(f"layers_{i}"))

    # 前向传播
    print("🔄 进行前向传播...")
    with torch.no_grad():
        _ = model(input_tensor)

    print(f"✅ 提取了 {len(feature_maps)} 个层的特征")

    # 保存特征图
    layer_info = []
    for layer_name, features in feature_maps.items():
        # features shape: [batch, channels, height, width] or [batch, height, width, channels]
        if features.dim() == 4:
            if features.shape[-1] < 100:  # 判断是否是 [B, C, H, W]
                features = features[0]  # [C, H, W]
            else:  # [B, H, W, C]
                features = features[0].permute(2, 0, 1)  # [C, H, W]
        else:
            continue

        num_channels = features.shape[0]
        layer_dir = save_dir / layer_name
        layer_dir.mkdir(parents=True, exist_ok=True)

        print(f"  📁 {layer_name}: {num_channels} 个通道")

        channel_urls = []
        # 限制保存的通道数（太多会占用空间）
        max_channels = min(num_channels, 64)
        step = max(1, num_channels // max_channels)

        for c in range(0, num_channels, step):
            if len(channel_urls) >= max_channels:
                break
            channel_map = features[c].numpy()
            normalized = normalize_feature_map(channel_map)
            img = Image.fromarray(normalized, mode="L")
            # 上采样到 112x112 以便查看
            if img.size[0] < 112:
                img = img.resize((112, 112), Image.NEAREST)
            filename = f"channel_{c:03d}.png"
            img.save(layer_dir / filename)
            channel_urls.append(
                f"/visualization/feature-maps/{model_key}/{layer_name}/{filename}"
            )

        layer_info.append(
            {
                "layer": layer_name,
                "channels": num_channels,
                "feature_map_urls": channel_urls,
            }
        )

    # 保存层信息元数据
    meta_path = save_dir / "layers.json"
    import json

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({"layers": layer_info}, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 特征图已保存到: {save_dir}")
    print(f"📄 元数据: {meta_path}")


def main():
    models = ["efficientnet_b0", "swin_tiny", "swin_tiny_feature"]
    for model_key in models:
        generate_feature_maps_for_model(model_key)
    print("\n🎉 所有特征图生成完成!")


if __name__ == "__main__":
    main()
