"""
训练历史记录模块
记录训练过程中的损失、准确率等指标
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TrainingHistory:
    """训练历史记录"""

    model_key: str
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    epochs: List[int] = field(default_factory=list)
    train_loss: List[float] = field(default_factory=list)
    train_accuracy: List[float] = field(default_factory=list)
    val_loss: List[float] = field(default_factory=list)
    val_accuracy: List[float] = field(default_factory=list)
    learning_rate: List[float] = field(default_factory=list)
    time_elapsed: List[float] = field(default_factory=list)

    # 最终结果
    best_val_accuracy: float = 0.0
    final_test_accuracy: float = 0.0
    best_epoch: int = 0

    # 评估信息
    evaluation_available: bool = False
    evaluation_path: Optional[str] = None

    def add_epoch(
        self,
        epoch: int,
        train_loss: float,
        train_accuracy: float,
        val_loss: float,
        val_accuracy: float,
        learning_rate: float,
        time_elapsed: float,
    ):
        """添加一个epoch的记录"""
        self.epochs.append(epoch)
        self.train_loss.append(train_loss)
        self.train_accuracy.append(train_accuracy)
        self.val_loss.append(val_loss)
        self.val_accuracy.append(val_accuracy)
        self.learning_rate.append(learning_rate)
        self.time_elapsed.append(time_elapsed)

    def get_best_epoch(self) -> int:
        """获取最佳epoch（基于验证准确率）"""
        if not self.val_accuracy:
            return 0
        best_idx = max(
            range(len(self.val_accuracy)), key=lambda i: self.val_accuracy[i]
        )
        return self.epochs[best_idx] if best_idx < len(self.epochs) else 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "model_key": self.model_key,
            "start_time": self.start_time,
            "end_time": datetime.now().isoformat(),
            "epochs": self.epochs,
            "train_loss": self.train_loss,
            "train_accuracy": self.train_accuracy,
            "val_loss": self.val_loss,
            "val_accuracy": self.val_accuracy,
            "learning_rate": self.learning_rate,
            "time_elapsed": self.time_elapsed,
            "best_val_accuracy": self.best_val_accuracy,
            "final_test_accuracy": self.final_test_accuracy,
            "best_epoch": self.best_epoch,
            "evaluation_available": self.evaluation_available,
            "evaluation_path": self.evaluation_path,
            "total_epochs": len(self.epochs),
            "total_training_time": sum(self.time_elapsed),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrainingHistory":
        """从字典创建"""
        history = cls(model_key=data["model_key"])
        history.start_time = data.get("start_time", history.start_time)
        history.epochs = data.get("epochs", [])
        history.train_loss = data.get("train_loss", [])
        history.train_accuracy = data.get("train_accuracy", [])
        history.val_loss = data.get("val_loss", [])
        history.val_accuracy = data.get("val_accuracy", [])
        history.learning_rate = data.get("learning_rate", [])
        history.time_elapsed = data.get("time_elapsed", [])
        history.best_val_accuracy = data.get("best_val_accuracy", 0.0)
        history.final_test_accuracy = data.get("final_test_accuracy", 0.0)
        history.best_epoch = data.get("best_epoch", 0)
        history.evaluation_available = data.get("evaluation_available", False)
        history.evaluation_path = data.get("evaluation_path")
        return history


def save_training_history(history: TrainingHistory, filepath: str):
    """保存训练历史到JSON文件"""
    data = history.to_dict()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_training_history(filepath: str) -> TrainingHistory:
    """从JSON文件加载训练历史"""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return TrainingHistory.from_dict(data)


def get_training_history_path(model_key: str) -> Path:
    """获取训练历史文件路径"""
    from ..lib.config import NEW_TRAINING_HISTORY_DIR

    return NEW_TRAINING_HISTORY_DIR / f"{model_key}_history.json"


def has_training_history(model_key: str) -> bool:
    """检查是否有训练历史记录"""
    history_path = get_training_history_path(model_key)
    return history_path.exists()
