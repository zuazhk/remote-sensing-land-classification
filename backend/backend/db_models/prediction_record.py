from datetime import datetime

from sqlalchemy import String, DateTime, Float, Integer, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
    model_key: Mapped[str] = mapped_column(String(50), nullable=False)
    predicted_class: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    all_probabilities: Mapped[dict] = mapped_column(JSON, nullable=True)
    image_filename: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
