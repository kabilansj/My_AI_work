"""Router for document upload and ingestion."""

import json
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.document import Document
from ..schemas.document import DocumentResponse, DocumentCreateText
from ..services.document_parser import DocumentParser
from ..config import UPLOAD_DIR
from clinical_extractor.cli import SAMPLE_CLINICAL_NOTE

router = APIRouter(prefix="/api/documents", tags=["Documents"])

SAMPLE_NOTES = {
    "discharge": {
        "filename": "discharge_summary_hf.txt",
        "content": """HOSPITAL DISCHARGE SUMMARY
PATIENT: John Doe | AGE: 64 | SEX: Male
ADMISSION DIAGNOSIS: Acute Decompensated Heart Failure
DISCHARGE DATE: 2026-10-25

CHIEF COMPLAINT:
Shortness of breath on exertion and bilateral lower extremity edema.

HISTORY OF PRESENT ILLNESS:
The patient is a 64-year-old male with a history of congestive heart failure (EF 35%) and hypertension.
In the emergency department, patient denied chest pain, denied fever, and denied cough.

PAST MEDICAL HISTORY:
1. Congestive Heart Failure (HFrEF)
2. Essential Hypertension
3. Hyperlipidemia
4. Chronic Kidney Disease Stage 3
5. Childhood history of resolved asthma
6. Family history of myocardial infarction (mother at 60)

DISCHARGE MEDICATIONS:
1. Furosemide 40 mg daily PO in the morning
2. Carvedilol 12.5 mg twice daily PO
3. Lisinopril 10 mg daily PO
4. Atorvastatin 40 mg PO at bedtime
5. Potassium chloride 20 mEq daily PO

ALLERGIES:
Penicillin (facial angioedema and urticaria).
Sulfa drugs (mild rash).

DISCHARGE LABS & DIAGNOSTICS:
- Blood Pressure: 118/74 mmHg
- Heart Rate: 68 bpm
- Serum Creatinine: 1.3 mg/dL
- Potassium: 4.4 mEq/L
- Sodium: 138 mEq/L
- BNP: 180 pg/mL
- CXR: Resolution of pulmonary congestion
- ECG: Normal sinus rhythm
"""
    },
    "diabetes": {
        "filename": "diabetes_clinic_progress.txt",
        "content": SAMPLE_CLINICAL_NOTE
    }
}


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a clinical file (.pdf, .txt) and extract content."""
    safe_name = file.filename or "uploaded_document.txt"
    dest_path = UPLOAD_DIR / safe_name

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    raw_text, meta = DocumentParser.parse_file(str(dest_path), safe_name)

    doc = Document(
        filename=safe_name,
        file_path=str(dest_path),
        mime_type=file.content_type or "application/octet-stream",
        raw_text=raw_text,
        layout_metadata=json.dumps(meta),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/text", response_model=DocumentResponse)
def create_text_document(
    payload: DocumentCreateText,
    db: Session = Depends(get_db),
):
    """Create a document directly from raw text."""
    doc = Document(
        filename=payload.filename,
        raw_text=payload.content,
        mime_type="text/plain",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/sample/{sample_name}", response_model=DocumentResponse)
def load_sample_document(
    sample_name: str,
    db: Session = Depends(get_db),
):
    """Load one of the predefined clinical samples ('discharge' or 'diabetes')."""
    if sample_name not in SAMPLE_NOTES:
        raise HTTPException(status_code=404, detail=f"Sample '{sample_name}' not found. Choose 'discharge' or 'diabetes'.")

    sample = SAMPLE_NOTES[sample_name]
    doc = Document(
        filename=sample["filename"],
        raw_text=sample["content"],
        mime_type="text/plain",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    return db.query(Document).order_by(Document.created_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """Retrieve document details and raw text."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc
