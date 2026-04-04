import argparse
import sys
from pathlib import Path

from ..lib.config import (
    NEW_MODELS_DIR,
    NEW_TRAINING_HISTORY_DIR,
    ORIGINAL_DATA_DIR,
    DEFAULT_EPOCHS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_LEARNING_RATE,
)


def main():
    parser = argparse.ArgumentParser(
        description="遥感图像分类模型训练工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 训练 EfficientNet-B0 (CNN)
  uv run python -m backend.training.train_cli --model efficientnet_b0 --epochs 30

  # 训练 Swin Transformer (完整训练)
  uv run python -m backend.training.train_cli --model swin_tiny --epochs 50

  # 训练 Swin Transformer (仅分类头)
  uv run python -m backend.training.train_cli --model swin_tiny_feature --epochs 30

  # 自定义参数训练
  uv run python -m backend.training.train_cli --model efficientnet_b0 --epochs 20 --batch-size 16 --lr 0.0001

可用模型:
  efficientnet_b0      - EfficientNet-B0 (CNN完整训练)
  swin_tiny            - Swin Transformer (完整训练)
  swin_tiny_feature    - Swin Transformer (仅训练分类头)
        """,
    )

    parser.add_argument(
        "--model",
        type=str,
        required=True,
        choices=["efficientnet_b0", "swin_tiny", "swin_tiny_feature"],
        help="要训练的模型",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=DEFAULT_EPOCHS,
        help=f"训练轮数 (默认: {DEFAULT_EPOCHS})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help=f"批次大小 (默认: {DEFAULT_BATCH_SIZE})",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=DEFAULT_LEARNING_RATE,
        help=f"学习率 (默认: {DEFAULT_LEARNING_RATE})",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(ORIGINAL_DATA_DIR),
        help=f"数据目录 (默认: {ORIGINAL_DATA_DIR})",
    )
    parser.add_argument(
        "--image-size",
        type=int,
        default=224,
        help="输入图像尺寸 (默认: 224)",
    )
    parser.add_argument(
        "--skip-eval",
        action="store_true",
        help="跳过训练后的评估",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        choices=["cpu", "cuda"],
        help="指定设备 (默认: 自动检测)",
    )
    parser.add_argument(
        "--weight-decay",
        type=float,
        default=0.01,
        help="权重衰减/正则化强度 (默认: 0.01)",
    )
    parser.add_argument(
        "--patience",
        type=int,
        default=10,
        help="早停耐心值: 验证准确率不提升的最大轮数 (默认: 10, 0=禁用)",
    )

    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("  遥感图像分类模型训练工具")
    print("=" * 60)
    print(f"\n模型: {args.model}")
    print(f"轮数: {args.epochs}")
    print(f"批次大小: {args.batch_size}")
    print(f"学习率: {args.lr}")
    print(f"权重衰减: {args.weight_decay}")
    print(f"早停耐心值: {args.patience}")
    print(f"图像尺寸: {args.image_size}")
    print(f"数据目录: {args.data_dir}")
    print(f"模型保存目录: {NEW_MODELS_DIR}")
    print(f"训练历史目录: {NEW_TRAINING_HISTORY_DIR}")
    print("=" * 60)

    from .train import train_model

    try:
        result = train_model(
            model_key=args.model,
            data_dir=args.data_dir,
            epochs=args.epochs,
            batch_size=args.batch_size,
            lr=args.lr,
            weight_decay=args.weight_decay,
            patience=args.patience,
            image_size=args.image_size,
            device=args.device,
            save_history=True,
            evaluate_after_training=not args.skip_eval,
        )

        if result.get("interrupted"):
            print("\n" + "=" * 60)
            print("  训练被中断 - 结果已保存")
            print("=" * 60)
            print(f"\n完成轮数: {result['completed_epochs']}/{args.epochs}")
            print(f"最佳验证准确率: {result['best_val_accuracy']:.2f}%")
            print(f"测试准确率: {result['test_accuracy']:.2f}%")
            if result.get("model_path"):
                print(f"模型保存路径: {result['model_path']}")
            print("\n提示: 你可以稍后继续训练，或使用已保存的模型")
        else:
            print("\n" + "=" * 60)
            print("  训练完成!")
            print("=" * 60)
            print(f"\n最佳验证准确率: {result['best_val_accuracy']:.2f}%")
            print(f"测试准确率: {result['test_accuracy']:.2f}%")
            print(f"模型保存路径: {result['model_path']}")
            if result.get("history"):
                print(f"训练历史: {NEW_TRAINING_HISTORY_DIR / args.model}_history.json")
        print()

    except KeyboardInterrupt:
        print("\n\n训练被用户中断")
        print("提示: 已保存的结果不会丢失")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n训练失败: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
