"""
训练功能路由
支持CNN和Transformer分类头训练
提供训练状态查询和历史查看
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ..lib.config import (
    MODELS,
    NEW_TRAINING_HISTORY_DIR,
    DEFAULT_EPOCHS,
    DEFAULT_BATCH_SIZE,
    DEFAULT_LEARNING_RATE,
)
from ..training.train import train_cnn_model, train_transformer_feature_model
from ..training.history import load_training_history

router = APIRouter()

# 全局训练状态跟踪
training_status: Dict[str, Dict[str, Any]] = {}
executor = ThreadPoolExecutor(max_workers=1)  # 一次只运行一个训练任务


# Pydantic模型
class TrainRequest(BaseModel):
    """训练请求模型"""

    model_key: str = Field(
        ...,
        description="模型标识符: 'efficientnet_b0' (CNN) 或 'swin_tiny_feature' (Transformer分类头)",
        examples=["efficientnet_b0", "swin_tiny_feature"],
    )
    epochs: int = Field(DEFAULT_EPOCHS, description="训练轮次", ge=1, le=100)
    batch_size: int = Field(DEFAULT_BATCH_SIZE, description="批次大小", ge=1, le=128)
    learning_rate: float = Field(
        DEFAULT_LEARNING_RATE, description="学习率", gt=0, le=1
    )
    data_dir: Optional[str] = Field(
        None, description="数据目录路径 (默认使用原始项目数据)"
    )
    image_size: int = Field(224, description="输入图像尺寸", ge=32, le=512)
    evaluate_after_training: bool = Field(True, description="训练完成后是否进行评估")


class TrainingStatus(BaseModel):
    """训练状态响应模型"""

    model_key: str = Field(..., description="模型标识符")
    status: str = Field(
        ..., description="训练状态: pending, running, completed, failed"
    )
    start_time: Optional[str] = Field(None, description="开始时间 (ISO格式)")
    end_time: Optional[str] = Field(None, description="结束时间 (ISO格式)")
    progress: Optional[Dict[str, Any]] = Field(None, description="训练进度信息")
    result: Optional[Dict[str, Any]] = Field(None, description="训练结果")
    error: Optional[str] = Field(None, description="错误信息")


class TrainingHistoryItem(BaseModel):
    """训练历史项目模型"""

    model_key: str = Field(..., description="模型标识符")
    history_path: str = Field(..., description="历史文件路径")
    best_val_accuracy: float = Field(..., description="最佳验证准确率")
    test_accuracy: float = Field(..., description="测试准确率")
    epochs_trained: int = Field(..., description="训练的轮次数")
    training_date: str = Field(..., description="训练日期")
    evaluation_available: bool = Field(False, description="是否有评估结果")
    evaluation_path: Optional[str] = Field(None, description="评估结果路径")


def run_training_task(model_key: str, train_config: Dict[str, Any]) -> Dict[str, Any]:
    """在后台线程中运行训练任务"""
    try:
        if model_key == "efficientnet_b0":
            result = train_cnn_model(**train_config)
        elif model_key == "swin_tiny_feature":
            result = train_transformer_feature_model(**train_config)
        else:
            raise ValueError(f"不支持的模型: {model_key}")
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e), "result": None}


async def train_in_background(
    model_key: str, task_id: str, train_config: Dict[str, Any]
):
    """后台训练任务"""
    training_status[task_id]["status"] = "running"

    # 在线程池中运行训练（避免阻塞事件循环）
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(
            executor, run_training_task, model_key, train_config
        )

        if result["success"]:
            training_status[task_id]["status"] = "completed"
            training_status[task_id]["result"] = result["result"]
            training_status[task_id]["end_time"] = datetime.now().isoformat()
        else:
            training_status[task_id]["status"] = "failed"
            training_status[task_id]["error"] = result["error"]
            training_status[task_id]["end_time"] = datetime.now().isoformat()

    except Exception as e:
        training_status[task_id]["status"] = "failed"
        training_status[task_id]["error"] = str(e)
        training_status[task_id]["end_time"] = datetime.now().isoformat()


@router.post("/train/start", response_model=TrainingStatus)
async def start_training(request: TrainRequest, background_tasks: BackgroundTasks):
    """启动模型训练任务"""
    if request.model_key not in ["efficientnet_b0", "swin_tiny_feature"]:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的模型。支持: efficientnet_b0 (CNN), swin_tiny_feature (Transformer分类头)",
        )

    # 检查是否已有相同模型的训练任务在运行
    for task_id, status in training_status.items():
        if status["model_key"] == request.model_key and status["status"] in [
            "pending",
            "running",
        ]:
            raise HTTPException(
                status_code=409,
                detail=f"{request.model_key} 的训练任务已在运行 (任务ID: {task_id})",
            )

    # 生成任务ID
    task_id = f"{request.model_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 准备训练配置
    train_config = {
        "model_key": request.model_key,
        "epochs": request.epochs,
        "batch_size": request.batch_size,
        "lr": request.learning_rate,
        "image_size": request.image_size,
        "data_dir": request.data_dir,
        "evaluate_after_training": request.evaluate_after_training,
    }

    # 初始化训练状态
    training_status[task_id] = {
        "model_key": request.model_key,
        "status": "pending",
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "progress": None,
        "result": None,
        "error": None,
    }

    # 启动后台任务
    background_tasks.add_task(
        train_in_background, request.model_key, task_id, train_config
    )

    return TrainingStatus(
        model_key=request.model_key,
        status="pending",
        start_time=training_status[task_id]["start_time"],
        task_id=task_id,
    )


@router.get("/train/status/{task_id}", response_model=TrainingStatus)
async def get_training_status(task_id: str):
    """获取训练任务状态"""
    if task_id not in training_status:
        raise HTTPException(status_code=404, detail="训练任务不存在")

    status = training_status[task_id]
    return TrainingStatus(**status)


@router.get("/train/status", response_model=List[TrainingStatus])
async def list_training_status():
    """列出所有训练任务状态"""
    return [TrainingStatus(**status) for status in training_status.values()]


@router.get("/train/history", response_model=List[TrainingHistoryItem])
async def get_training_history():
    """获取训练历史记录"""
    history_items = []

    if not NEW_TRAINING_HISTORY_DIR.exists():
        return []

    # 查找所有历史文件
    history_files = list(NEW_TRAINING_HISTORY_DIR.glob("*_history.json"))

    for history_file in history_files:
        try:
            history_data = load_training_history(str(history_file))

            # 从文件名提取模型名称
            filename = history_file.stem
            model_key = filename.replace("_history", "")

            # 获取最佳验证准确率和测试准确率
            best_val_acc = 0.0
            test_acc = 0.0
            if history_data.get("epochs"):
                best_val_acc = max(
                    epoch["val_accuracy"] for epoch in history_data["epochs"]
                )
                test_acc = history_data.get("final_test_accuracy", 0.0)

            # 计算训练日期
            training_date = "未知"
            if history_data.get("epochs") and len(history_data["epochs"]) > 0:
                first_epoch = history_data["epochs"][0]
                if "timestamp" in first_epoch:
                    training_date = first_epoch["timestamp"]

            history_items.append(
                TrainingHistoryItem(
                    model_key=model_key,
                    history_path=str(history_file),
                    best_val_accuracy=best_val_acc,
                    test_accuracy=test_acc,
                    epochs_trained=len(history_data.get("epochs", [])),
                    training_date=training_date,
                    evaluation_available=history_data.get(
                        "evaluation_available", False
                    ),
                    evaluation_path=history_data.get("evaluation_path"),
                )
            )
        except Exception as e:
            print(f"加载训练历史文件 {history_file} 时出错: {e}")
            continue

    return history_items


@router.get("/train/history/{model_key}", response_model=Dict[str, Any])
async def get_training_history_detail(model_key: str):
    """获取特定模型的训练历史详情"""
    history_file = NEW_TRAINING_HISTORY_DIR / f"{model_key}_history.json"

    if not history_file.exists():
        raise HTTPException(status_code=404, detail=f"{model_key} 的训练历史不存在")

    try:
        history_data = load_training_history(str(history_file))
        return history_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载训练历史失败: {str(e)}")


@router.delete("/train/cancel/{task_id}")
async def cancel_training(task_id: str):
    """取消训练任务（注意：当前实现中无法真正取消运行中的训练）"""
    if task_id not in training_status:
        raise HTTPException(status_code=404, detail="训练任务不存在")

    status = training_status[task_id]["status"]
    if status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail=f"无法取消状态为 '{status}' 的任务")

    # 标记为已取消
    training_status[task_id]["status"] = "cancelled"
    training_status[task_id]["end_time"] = datetime.now().isoformat()
    training_status[task_id]["error"] = "用户取消"

    return {"message": f"训练任务 {task_id} 已标记为取消"}


@router.get("/train/models")
async def get_trainable_models():
    """获取可训练的模型列表"""
    trainable_models = {
        "efficientnet_b0": {
            "name": "EfficientNet-B0",
            "type": "cnn",
            "description": "高效的CNN模型，适合快速训练和良好性能",
            "trainable": True,
            "default_epochs": DEFAULT_EPOCHS,
        },
        "swin_tiny_feature": {
            "name": "Swin Transformer (分类头)",
            "type": "transformer_feature",
            "description": "使用预训练的Swin Transformer，仅训练分类头，训练速度快",
            "trainable": True,
            "default_epochs": DEFAULT_EPOCHS,
        },
    }
    return trainable_models
