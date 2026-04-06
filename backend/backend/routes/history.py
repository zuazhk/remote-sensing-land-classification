from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..db_models.prediction_record import PredictionRecord
from ..db_models.user import User
from ..auth import get_current_user

router = APIRouter(prefix="/history", tags=["预测历史"])


@router.get("")
async def get_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = (
        select(PredictionRecord)
        .where(PredictionRecord.user_id == current_user.id)
        .order_by(desc(PredictionRecord.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    return [
        {
            "id": r.id,
            "model_key": r.model_key,
            "predicted_class": r.predicted_class,
            "confidence": r.confidence,
            "all_probabilities": r.all_probabilities,
            "image_filename": r.image_filename,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
