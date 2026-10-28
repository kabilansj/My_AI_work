"""Audit logging database model."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from ..database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(36), nullable=False)
    entity_type = Column(String(50), nullable=False)  # medication, diagnosis, investigation, allergy, document
    entity_id = Column(String(36), nullable=False)
    action = Column(String(50), nullable=False)  # AUTO_EXTRACTED, ACCEPTED, MODIFIED, REJECTED
    prior_state = Column(Text, nullable=True)  # JSON-serialized prior state
    new_state = Column(Text, nullable=True)  # JSON-serialized updated state
    user_id = Column(String(100), default="clinician_user")
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
