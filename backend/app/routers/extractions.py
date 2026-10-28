"""Router for running and fetching clinical extractions."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.extraction import Extraction
from ..models.clinical_entities import (
    DbMedication,
    DbDiagnosis,
    DbInvestigation,
    DbAllergy,
)
from ..schemas.review import ExtractionDetailResponse
from ..services.extraction_service import ExtractionService

router = APIRouter(prefix="/api/documents", tags=["Extractions"])


@router.post("/{document_id}/extract", response_model=ExtractionDetailResponse)
def run_extraction(
    document_id: str,
    engine: Optional[str] = Query(default=None, description="local, llm, or auto"),
    db: Session = Depends(get_db),
):
    """Trigger entity extraction for a document and return the structured entities."""
    try:
        extraction = ExtractionService.run_extraction(db=db, document_id=document_id, engine=engine)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    return get_document_extraction(document_id, db)


@router.get("/{document_id}/extraction", response_model=ExtractionDetailResponse)
def get_document_extraction(
    document_id: str,
    db: Session = Depends(get_db),
):
    """Fetch the latest extraction and all associated entities for a document."""
    extraction = (
        db.query(Extraction)
        .filter(Extraction.document_id == document_id)
        .order_by(Extraction.created_at.desc())
        .first()
    )
    if not extraction:
        raise HTTPException(status_code=404, detail="No extractions found for this document.")

    meds = db.query(DbMedication).filter(DbMedication.extraction_id == extraction.id).all()
    dxs = db.query(DbDiagnosis).filter(DbDiagnosis.extraction_id == extraction.id).all()
    invs = db.query(DbInvestigation).filter(DbInvestigation.extraction_id == extraction.id).all()
    allergies = db.query(DbAllergy).filter(DbAllergy.extraction_id == extraction.id).all()

    return ExtractionDetailResponse(
        id=extraction.id,
        document_id=extraction.document_id,
        engine=extraction.engine,
        model_name=extraction.model_name,
        processing_time_ms=extraction.processing_time_ms,
        status=extraction.status,
        created_at=extraction.created_at,
        medications=meds,
        diagnoses=dxs,
        investigations=invs,
        allergies=allergies,
    )
