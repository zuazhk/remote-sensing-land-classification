"""
预测功能路由
支持单图预测、多模型对比、批量预测
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from pathlib import Path
import tempfile
import shutil
import csv
import io
import json
from typing import List, Optional

from backend.shared import classifiers, validate_model_key
from backend.config import ALLOWED_MIME_TYPES, MAX_FILE_SIZE, ALLOWED_EXTENSIONS
from backend.cache import cached_prediction, prediction_cache
from backend.cache_integration import create_image_signature

router = APIRouter()


# Pydantic响应模型
class PredictResponse(BaseModel):
    model: str
    result: dict


class CompareResponse(BaseModel):
    image: str
    results: dict


class BatchResult(BaseModel):
    filename: str
    result: dict


class BatchPredictResponse(BaseModel):
    model: str
    results: List[BatchResult]
    total: int
    successful: int


# 缓存辅助函数
def get_prediction_cache_key(model: str, image_path: Path) -> str:
    """生成预测缓存键"""
    # 使用图像签名函数创建基于图像内容的缓存键
    return f"pred:{model}:{create_image_signature(image_path, model)}"


def cached_predict(model: str, image_path: Path) -> dict:
    """带缓存的预测函数"""
    cache_key = get_prediction_cache_key(model, image_path)

    # 尝试从缓存获取
    cached_result = prediction_cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    # 执行预测
    result = classifiers[model].predict(str(image_path))

    # 缓存结果
    prediction_cache.set(cache_key, result)

    return result


# 文件验证函数
def validate_upload_file(file: UploadFile):
    """验证上传文件的安全性"""
    # 1. 检查文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 重置文件指针
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 ({file_size / 1024 / 1024:.1f}MB > {MAX_FILE_SIZE / 1024 / 1024}MB)",
        )

    # 2. 检查MIME类型
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}. 仅支持: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # 3. 验证文件扩展名
    filename = file.filename or "upload.jpg"
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件扩展名: {suffix}. 仅支持: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    return filename, suffix


@router.post("/predict", response_model=PredictResponse)
async def predict_image(model: str, file: UploadFile = File(...)):
    """使用指定模型对单张图像进行预测"""
    # 验证模型
    validate_model_key(model)

    # 验证文件
    filename, suffix = validate_upload_file(file)

    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # 进行预测（使用缓存）
        result = cached_predict(model, Path(tmp_path))
        return PredictResponse(model=model, result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")
    finally:
        # 清理临时文件
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


@router.post("/predict/compare", response_model=CompareResponse)
async def compare_prediction(file: UploadFile = File(...)):
    """使用所有可用模型对图像进行预测并对比结果"""
    if not classifiers:
        raise HTTPException(status_code=503, detail="模型未加载")

    # 验证文件
    filename, suffix = validate_upload_file(file)

    # 保存到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        results = {}
        for model_name in classifiers.keys():
            results[model_name] = cached_predict(model_name, Path(tmp_path))

        return CompareResponse(image=filename, results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"预测失败: {str(e)}")
    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)


@router.post("/predict/batch")
async def batch_predict(
    model: str,
    files: List[UploadFile] = File(...),
    export_format: Optional[str] = "json",
):
    """批量图像预测（最多50张）"""
    # 验证模型
    validate_model_key(model)

    # 检查文件数量
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="最多支持50个文件")

    if len(files) == 0:
        raise HTTPException(status_code=400, detail="至少需要一个文件")

    classifier = classifiers[model]
    batch_results = []
    successful = 0

    # 处理每个文件
    for file in files:
        try:
            # 验证文件
            filename, suffix = validate_upload_file(file)

            # 保存到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                tmp_path = tmp.name

            try:
                # 进行预测（使用缓存）
                result = cached_predict(model, Path(tmp_path))
                batch_results.append(BatchResult(filename=filename, result=result))
                successful += 1
            finally:
                if tmp_path:
                    Path(tmp_path).unlink(missing_ok=True)

        except Exception as e:
            # 记录失败但继续处理其他文件
            batch_results.append(
                BatchResult(
                    filename=file.filename or "unknown",
                    result={"error": str(e), "success": False},
                )
            )

    # 根据请求格式返回结果
    if export_format == "csv":
        # 生成CSV响应
        output = io.StringIO()
        writer = csv.writer(output)

        # 写入表头
        writer.writerow(
            ["filename", "predicted_class", "confidence", "all_probabilities"]
        )

        # 写入数据
        for result in batch_results:
            if "error" not in result.result:
                class_name = result.result.get("class", "unknown")
                confidence = result.result.get("confidence", 0)
                probs = json.dumps(result.result.get("all_probabilities", {}))
                writer.writerow([result.filename, class_name, confidence, probs])
            else:
                writer.writerow([result.filename, "ERROR", 0, result.result["error"]])

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=batch_results.csv"},
        )
    else:
        # 默认返回JSON
        return BatchPredictResponse(
            model=model, results=batch_results, total=len(files), successful=successful
        )
