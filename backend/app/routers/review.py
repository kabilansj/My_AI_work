"""Router for Human-in-the-Loop (HITL) review actions and audit logs."""

from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.clinical_entities import (
    DbMedication,
    DbDiagnosis,
    DbInvestigation,
    DbAllergy,
)
from ..models.audit import AuditLog
from ..schemas.review import (
    ReviewActionRequest,
    RejectRequest,
    ModifyEntityRequest,
    AuditLogSchema,
)
from ..services.audit_service import AuditService

router = APIRouter(prefix="/api", tags=["HITL Review & Audit"])

ENTITY_MODELS = {
    "medication": DbMedication,
    "medications": DbMedication,
    "diagnosis": DbDiagnosis,
    "diagnoses": DbDiagnosis,
    "investigation": DbInvestigation,
    "investigations": DbInvestigation,
    "allergy": DbAllergy,
    "allergies": DbAllergy,
}


def _get_entity(db: Session, entity_type: str, entity_id: str):
    norm_type = entity_type.lower()
    model = ENTITY_MODELS.get(norm_type)
    if not model:
        raise HTTPException(status_code=400, detail=f"Invalid entity type '{entity_type}'.")

    entity = db.query(model).filter(model.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail=f"{entity_type.title()} entity not found.")
    return entity, norm_type


@router.post("/review/{entity_type}/{entity_id}/accept")
def accept_entity(
    entity_type: str,
    entity_id: str,
    payload: ReviewActionRequest,
    db: Session = Depends(get_db),
):
    """Clinician accepts/approves an extracted entity."""
    entity, norm_type = _get_entity(db, entity_type, entity_id)

    prior_state = {"review_status": entity.review_status}
    entity.review_status = "accepted"
    entity.reviewed_by = payload.reviewed_by
    entity.reviewed_at = datetime.now(timezone.utc)
    if payload.notes:
        entity.reviewer_notes = payload.notes

    AuditService.log(
        db=db,
        document_id=entity.document_id,
        entity_type=norm_type,
        entity_id=entity.id,
        action="ACCEPTED",
        prior_state=prior_state,
        new_state={"review_status": "accepted", "notes": payload.notes},
        user_id=payload.reviewed_by,
        reason=payload.notes,
    )
    return {"status": "success", "entity_id": entity.id, "review_status": "accepted"}


@router.post("/review/{entity_type}/{entity_id}/modify")
def modify_entity(
    entity_type: str,
    entity_id: str,
    payload: ModifyEntityRequest,
    db: Session = Depends(get_db),
):
    """Clinician updates/corrects an entity's fields and approves it."""
    entity, norm_type = _get_entity(db, entity_type, entity_id)

    prior_state = {k: getattr(entity, k) for k in payload.updates.keys() if hasattr(entity, k)}
    prior_state["review_status"] = entity.review_status

    # Apply updates
    for field, val in payload.updates.items():
        if hasattr(entity, field):
            setattr(entity, field, val)

    entity.review_status = "modified"
    entity.reviewed_by = payload.reviewed_by
    entity.reviewed_at = datetime.now(timezone.utc)
    if payload.notes:
        entity.reviewer_notes = payload.notes

    AuditService.log(
        db=db,
        document_id=entity.document_id,
        entity_type=norm_type,
        entity_id=entity.id,
        action="MODIFIED",
        prior_state=prior_state,
        new_state=payload.updates,
        user_id=payload.reviewed_by,
        reason=payload.notes,
    )
    return {"status": "success", "entity_id": entity.id, "review_status": "modified"}


@router.post("/review/{entity_type}/{entity_id}/reject")
def reject_entity(
    entity_type: str,
    entity_id: str,
    payload: RejectRequest,
    db: Session = Depends(get_db),
):
    """Clinician rejects a hallucinated or erroneous entity with a clinical reason."""
    entity, norm_type = _get_entity(db, entity_type, entity_id)

    prior_state = {"review_status": entity.review_status}
    entity.review_status = "rejected"
    entity.reviewed_by = payload.reviewed_by
    entity.reviewed_at = datetime.now(timezone.utc)
    entity.reviewer_notes = payload.reason

    AuditService.log(
        db=db,
        document_id=entity.document_id,
        entity_type=norm_type,
        entity_id=entity.id,
        action="REJECTED",
        prior_state=prior_state,
        new_state={"review_status": "rejected", "reason": payload.reason},
        user_id=payload.reviewed_by,
        reason=payload.reason,
    )
    return {"status": "success", "entity_id": entity.id, "review_status": "rejected"}


@router.get("/audit-logs", response_model=List[AuditLogSchema])
def get_audit_logs(
    document_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    """Retrieve immutable chronological audit events."""
    query = db.query(AuditLog)
    if document_id:
        query = query.filter(AuditLog.document_id == document_id)
    return query.order_by(AuditLog.created_at.desc()).limit(100).all()
