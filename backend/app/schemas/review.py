"""Pydantic schemas for Human-in-the-Loop review and entities."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ReviewActionRequest(BaseModel):
    reviewed_by: str = "Dr. Reviewer"
    notes: Optional[str] = None


class RejectRequest(BaseModel):
    reviewed_by: str = "Dr. Reviewer"
    reason: str


class ModifyEntityRequest(BaseModel):
    reviewed_by: str = "Dr. Reviewer"
    notes: Optional[str] = None
    updates: Dict[str, Any]


class MedicationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    status: str
    indication: Optional[str] = None
    evidence_span: Optional[str] = None
    confidence: float
    review_status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class DiagnosisSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    condition_name: str
    assertion: str
    acuity: Optional[str] = None
    icd10_hint: Optional[str] = None
    evidence_span: Optional[str] = None
    confidence: float
    review_status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class InvestigationSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    test_name: str
    category: str
    value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    flag: str
    evidence_span: Optional[str] = None
    confidence: float
    review_status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class AllergySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    allergen: str
    reaction: Optional[str] = None
    severity: str
    allergy_type: str
    status: str
    evidence_span: Optional[str] = None
    confidence: float
    review_status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class ExtractionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    engine: str
    model_name: Optional[str] = None
    processing_time_ms: float
    status: str
    created_at: datetime
    medications: List[MedicationSchema]
    diagnoses: List[DiagnosisSchema]
    investigations: List[InvestigationSchema]
    allergies: List[AllergySchema]


class AuditLogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    entity_type: str
    entity_id: str
    action: str
    prior_state: Optional[str] = None
    new_state: Optional[str] = None
    user_id: str
    reason: Optional[str] = None
    created_at: datetime
