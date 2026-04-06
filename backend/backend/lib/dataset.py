import os
from pathlib import Path

import torch
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms
from torchvision.datasets import ImageFolder

# 数据目录配置 - 指向原始项目数据
from .config import ORIGINAL_DATA_DIR

NUM_WORKERS = min(4, os.cpu_count() or 1)


def get_eurosat_transforms(image_size: int = 224, is_training: bool = True):
    if is_training:
        return transforms.Compose(
            [
                transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
                transforms.RandomHorizontalFlip(),
                transforms.RandomVerticalFlip(),
                transforms.RandomRotation(20),
                transforms.ColorJitter(
                    brightness=0.3, contrast=0.3, saturation=0.3, hue=0.1
                ),
                transforms.RandomGrayscale(p=0.1),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )
    else:
        return transforms.Compose(
            [
                transforms.Resize((image_size, image_size)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )


class TransformDataset(Dataset):
    def __init__(self, subset, transform):
        self.subset = subset
        self.transform = transform

    def __len__(self):
        return len(self.subset)

    def __getitem__(self, idx):
        img, label = self.subset[idx]
        if self.transform:
            img = self.transform(img)
        return img, label


def load_eurosat_dataset(data_dir: str, image_size: int = 224, batch_size: int = 32):
    data_path = Path(data_dir)

    train_dir = data_path / "train"
    val_dir = data_path / "val"
    test_dir = data_path / "test"

    if train_dir.exists() and val_dir.exists() and test_dir.exists():
        train_transform = get_eurosat_transforms(image_size, is_training=True)
        val_transform = get_eurosat_transforms(image_size, is_training=False)

        train_dataset = ImageFolder(train_dir, transform=train_transform)
        val_dataset = ImageFolder(val_dir, transform=val_transform)
        test_dataset = ImageFolder(test_dir, transform=val_transform)
        classes = train_dataset.classes
    else:
        eurosat_dir = data_path / "eurosat" / "2750"
        if eurosat_dir.exists():
            print(f"检测到原始 EuroSAT 数据，正在划分数据集...")
            full_dataset = ImageFolder(eurosat_dir, transform=None)

            total_size = len(full_dataset)
            train_size = int(0.7 * total_size)
            val_size = int(0.15 * total_size)
            test_size = total_size - train_size - val_size

            train_ds, val_ds, test_ds = random_split(
                full_dataset,
                [train_size, val_size, test_size],
                generator=torch.Generator().manual_seed(42),
            )

            print(f"  训练集: {train_size}, 验证集: {val_size}, 测试集: {test_size}")

            train_transform = get_eurosat_transforms(image_size, is_training=True)
            val_transform = get_eurosat_transforms(image_size, is_training=False)

            train_dataset = TransformDataset(train_ds, train_transform)
            val_dataset = TransformDataset(val_ds, val_transform)
            test_dataset = TransformDataset(test_ds, val_transform)
            classes = full_dataset.classes
        else:
            raise FileNotFoundError(f"未找到数据目录: {eurosat_dir}")

    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True, num_workers=NUM_WORKERS
    )
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False, num_workers=NUM_WORKERS
    )
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False, num_workers=NUM_WORKERS
    )

    return train_loader, val_loader, test_loader, classes
