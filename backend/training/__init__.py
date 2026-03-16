"""
训练模块 - 新项目训练功能
支持CNN完整训练和Transformer分类头训练
"""

from .train import train_model, train_cnn_model, train_transformer_feature_model
from .history import save_training_history, load_training_history, TrainingHistory
from .evaluation import evaluate_model, save_evaluation_results

__all__ = [
    "train_model",
    "train_cnn_model",
    "train_transformer_feature_model",
    "save_training_history",
    "load_training_history",
    "TrainingHistory",
    "evaluate_model",
    "save_evaluation_results",
]
