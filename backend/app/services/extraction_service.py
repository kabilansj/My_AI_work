"""Service orchestrating clinical entity extraction with DB persistence and audit logs."""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from clinical_extractor.core import ClinicalNLP
from ..models.document import Document
from ..models.extraction import Extraction
from ..models.clinical_entities import (
    DbMedication,
    DbDiagnosis,
    DbInvestigation,
    DbAllergy,
)
from .audit_service import AuditService
from ..config import settings


class ExtractionService:
    """Manages execution and persistence of clinical entity extractions."""

    @classmethod
    def run_extraction(
        cls,
        db: Session,
        document_id: str,
        engine: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> Extraction:
        """Execute clinical NLP extraction and persist entities to the database."""
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise ValueError(f"Document with ID {document_id} not found.")

        active_engine = engine or settings.default_engine
        nlp = ClinicalNLP(engine=active_engine, model_name=model_name)
        extraction_result = nlp.extract(doc.raw_text)

        # 1. Create Extraction Job Record
        extraction = Extraction(
            document_id=doc.id,
            engine=extraction_result.metadata.engine,
            model_name=extraction_result.metadata.model_name,
            processing_time_ms=extraction_result.metadata.processing_time_ms,
            status="completed",
        )
        db.add(extraction)
        db.commit()
        db.refresh(extraction)

        # 2. Persist Medications
        for m in extraction_result.medications:
            db_med = DbMedication(
                extraction_id=extraction.id,
                document_id=doc.id,
                name=m.name,
                dosage=m.dosage,
                frequency=m.frequency,
                route=m.route,
                status=m.status.value,
                indication=m.indication,
                evidence_span=m.evidence_span,
                confidence=m.confidence,
                review_status="pending",
            )
            db.add(db_med)
            db.flush()

            AuditService.log(
                db=db,
                document_id=doc.id,
                entity_type="medication",
                entity_id=db_med.id,
                action="AUTO_EXTRACTED",
                new_state={"name": m.name, "dosage": m.dosage, "status": m.status.value},
                user_id="ai_extractor",
            )

        # 3. Persist Diagnoses
        for d in extraction_result.diagnoses:
            db_dx = DbDiagnosis(
                extraction_id=extraction.id,
                document_id=doc.id,
                condition_name=d.condition_name,
                assertion=d.assertion.value,
                acuity=d.acuity,
                icd10_hint=d.icd10_hint,
                evidence_span=d.evidence_span,
                confidence=d.confidence,
                review_status="pending",
            )
            db.add(db_dx)
            db.flush()

            AuditService.log(
                db=db,
                document_id=doc.id,
                entity_type="diagnosis",
                entity_id=db_dx.id,
                action="AUTO_EXTRACTED",
                new_state={"condition_name": d.condition_name, "assertion": d.assertion.value},
                user_id="ai_extractor",
            )

        # 4. Persist Investigations
        for inv in extraction_result.investigations:
            db_inv = DbInvestigation(
                extraction_id=extraction.id,
                document_id=doc.id,
                test_name=inv.test_name,
                category=inv.category.value,
                value=inv.value,
                unit=inv.unit,
                reference_range=inv.reference_range,
                flag=inv.flag.value,
                evidence_span=inv.evidence_span,
                confidence=inv.confidence,
                review_status="pending",
            )
            db.add(db_inv)
            db.flush()

            AuditService.log(
                db=db,
                document_id=doc.id,
                entity_type="investigation",
                entity_id=db_inv.id,
                action="AUTO_EXTRACTED",
                new_state={"test_name": inv.test_name, "value": inv.value, "flag": inv.flag.value},
                user_id="ai_extractor",
            )

        # 5. Persist Allergies
        for a in extraction_result.allergies:
            db_all = DbAllergy(
                extraction_id=extraction.id,
                document_id=doc.id,
                allergen=a.allergen,
                reaction=a.reaction,
                severity=a.severity.value,
                allergy_type=a.allergy_type.value,
                status=a.status.value,
                evidence_span=a.evidence_span,
                confidence=a.confidence,
                review_status="pending",
            )
            db.add(db_all)
            db.flush()

            AuditService.log(
                db=db,
                document_id=doc.id,
                entity_type="allergy",
                entity_id=db_all.id,
                action="AUTO_EXTRACTED",
                new_state={"allergen": a.allergen, "reaction": a.reaction, "status": a.status.value},
                user_id="ai_extractor",
            )

        db.commit()
        return extraction
