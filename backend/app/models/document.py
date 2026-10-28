"""Document database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from ..database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=True)
    mime_type = Column(String(100), default="text/plain")
    raw_text = Column(Text, nullable=False)
    layout_metadata = Column(Text, nullable=True)  # JSON-encoded page/table metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
