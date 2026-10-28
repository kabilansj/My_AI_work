"""Extraction job database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from ..database import Base


class Extraction(Base):
    __tablename__ = "extractions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    engine = Column(String(50), default="auto")
    model_name = Column(String(100), nullable=True)
    processing_time_ms = Column(Float, default=0.0)
    status = Column(String(50), default="completed")  # "processing", "completed", "failed"
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
