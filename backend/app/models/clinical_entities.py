"""Database models for clinical entities with HITL review tracking."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Text, DateTime, ForeignKey
from ..database import Base


class DbMedication(Base):
    __tablename__ = "medications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    extraction_id = Column(String(36), ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)
    route = Column(String(100), nullable=True)
    status = Column(String(50), default="active")
    indication = Column(String(255), nullable=True)

    evidence_span = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)

    # HITL Review tracking
    review_status = Column(String(50), default="pending")  # pending, accepted, modified, rejected
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)


class DbDiagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    extraction_id = Column(String(36), ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    condition_name = Column(String(255), nullable=False)
    assertion = Column(String(50), default="confirmed")  # confirmed, ruled_out, suspected, historical, family_history
    acuity = Column(String(50), nullable=True)
    icd10_hint = Column(String(50), nullable=True)

    evidence_span = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)

    # HITL Review tracking
    review_status = Column(String(50), default="pending")
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)


class DbInvestigation(Base):
    __tablename__ = "investigations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    extraction_id = Column(String(36), ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    test_name = Column(String(255), nullable=False)
    category = Column(String(50), default="laboratory")
    value = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    flag = Column(String(50), default="unknown")  # normal, high, low, abnormal, pending

    evidence_span = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)

    # HITL Review tracking
    review_status = Column(String(50), default="pending")
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)


class DbAllergy(Base):
    __tablename__ = "allergies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    extraction_id = Column(String(36), ForeignKey("extractions.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)

    allergen = Column(String(255), nullable=False)
    reaction = Column(String(255), nullable=True)
    severity = Column(String(50), default="unknown")
    allergy_type = Column(String(50), default="drug")
    status = Column(String(50), default="active")

    evidence_span = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0)

    # HITL Review tracking
    review_status = Column(String(50), default="pending")
    reviewed_by = Column(String(100), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    reviewer_notes = Column(Text, nullable=True)
