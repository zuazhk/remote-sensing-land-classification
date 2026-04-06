"""
模型定义 - EfficientNet (CNN) 和 Swin Transformer
"""

import os
import timm
import torch
import torch.nn as nn

from .config import PRETRAINED_WEIGHTS_DIR

# 设置预训练权重缓存目录到项目文件夹
os.environ["TORCH_HOME"] = str(PRETRAINED_WEIGHTS_DIR)


def create_model(model_name: str, num_classes: int, pretrained: bool = False):
    model = timm.create_model(
        model_name, pretrained=pretrained, num_classes=num_classes
    )
    return model


class CNNModel(nn.Module):
    def __init__(self, model_name: str = "efficientnet_b0", num_classes: int = 10):
        super().__init__()
        self.model = create_model(model_name, num_classes, pretrained=False)
        self.model_type = "cnn"

    def forward(self, x):
        return self.model(x)


class TransformerModel(nn.Module):
    def __init__(
        self, model_name: str = "swin_tiny_patch4_window7_224", num_classes: int = 10
    ):
        super().__init__()
        self.model = create_model(model_name, num_classes, pretrained=False)
        self.model_type = "transformer"

    def forward(self, x):
        return self.model(x)


class SwinTinyFeatureExtractor(nn.Module):
    def __init__(
        self, model_name: str = "swin_tiny_patch4_window7_224", num_classes: int = 10
    ):
        super().__init__()
        self.base_model = timm.create_model(
            model_name, pretrained=False, num_classes=1000
        )

        # 冻结所有参数
        for param in self.base_model.parameters():
            param.requires_grad = False

        # 替换分类头
        in_features = self.base_model.head.in_features
        self.base_model.head = nn.Linear(in_features, num_classes)
        # 仅分类头的参数需要训练
        for param in self.base_model.head.parameters():
            param.requires_grad = True

        self.model_type = "transformer_feature_extractor"
        # 添加全局平均池化层，将空间维度池化为1x1
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))

    def forward(self, x):
        # Swin Transformer输出形状为 [batch, height, width, num_classes]
        # 需要转换为 [batch, num_classes]
        x = self.base_model(x)
        # 如果x是4D张量且最后一维是类别数，需要重新排列维度
        if x.dim() == 4:
            # 假设形状为 [batch, height, width, channels]
            # 转换为 [batch, channels, height, width] 以进行池化
            x = x.permute(0, 3, 1, 2)
            x = self.global_pool(x)
            x = x.squeeze(-1).squeeze(-1)  # 移除空间维度
        return x


def get_model(model_key: str, num_classes: int = 10):
    models = {
        "efficientnet_b0": ("efficientnet_b0", CNNModel),
        "swin_tiny": ("swin_tiny_patch4_window7_224", TransformerModel),
        "swin_tiny_feature": ("swin_tiny_patch4_window7_224", SwinTinyFeatureExtractor),
    }

    if model_key not in models:
        raise ValueError(
            f"Unknown model: {model_key}. Available: {list(models.keys())}"
        )

    model_name, model_class = models[model_key]
    return model_class(model_name, num_classes)


def count_parameters(model: nn.Module):
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
