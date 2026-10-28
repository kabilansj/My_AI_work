"""Unit tests for preprocessing and entity validation."""

from clinical_extractor.pipeline.preprocessor import ClinicalPreprocessor
from clinical_extractor.pipeline.validator import EntityValidator
from clinical_extractor.models.entities import (
    Medication,
    Diagnosis,
    AssertionStatus,
    MedicationStatus,
)


def test_clinical_preprocessor_segmentation():
    sample_note = (
        "CHIEF COMPLAINT: Chest tightness.\n\n"
        "HISTORY OF PRESENT ILLNESS:\n"
        "Patient is a 65yo female presenting with intermittent chest discomfort.\n\n"
        "PAST MEDICAL HISTORY:\n"
        "1. Hypertension\n2. Type 2 Diabetes\n\n"
        "MEDICATIONS:\n"
        "- Lisinopril 20mg daily\n"
        "- Metformin 1000mg BID\n\n"
        "ALLERGIES:\n"
        "Penicillin (rash)\n\n"
        "ASSESSMENT AND PLAN:\n"
        "Stable angina, continue home meds."
    )

    doc = ClinicalPreprocessor.process(sample_note)
    assert doc.word_count > 0
    assert len(doc.sections) >= 5

    meds_section = doc.get_section_text("medications")
    assert meds_section is not None
    assert "Lisinopril" in meds_section

    allergies_sec = doc.get_section_text("allergies")
    assert allergies_sec is not None
    assert "Penicillin" in allergies_sec


def test_evidence_span_verification():
    source_text = "Patient was prescribed Atorvastatin 40 mg daily for hyperlipidemia."

    assert EntityValidator.verify_evidence_span(source_text, "Atorvastatin 40 mg daily") is True
    assert EntityValidator.verify_evidence_span(source_text, "Atorvastatin") is True
    # Non-existent / hallucinated span
    assert EntityValidator.verify_evidence_span(source_text, "Aspirin 81 mg daily") is False


def test_medication_deduplication():
    meds = [
        Medication(name="Metformin", dosage=None, frequency=None),
        Medication(name="Metformin", dosage="500 mg", frequency="BID", route="PO"),
    ]
    deduped = EntityValidator.deduplicate_medications(meds)
    assert len(deduped) == 1
    assert deduped[0].name == "Metformin"
    assert deduped[0].dosage == "500 mg"
    assert deduped[0].frequency == "BID"


def test_diagnosis_deduplication():
    dxs = [
        Diagnosis(condition_name="Hypertension", assertion=AssertionStatus.CONFIRMED),
        Diagnosis(condition_name="Hypertension", assertion=AssertionStatus.CONFIRMED, acuity="chronic"),
        Diagnosis(condition_name="Hypertension", assertion=AssertionStatus.RULED_OUT),  # distinct assertion
    ]
    deduped = EntityValidator.deduplicate_diagnoses(dxs)
    assert len(deduped) == 2
    confirmed_item = next(d for d in deduped if d.assertion == AssertionStatus.CONFIRMED)
    assert confirmed_item.acuity == "chronic"
