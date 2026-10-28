"""Unit tests for clinical data models and validation."""

import pytest
from clinical_extractor.models import (
    Medication,
    Diagnosis,
    Investigation,
    Allergy,
    ClinicalExtractionResult,
    ExtractionMetadata,
    MedicationStatus,
    AssertionStatus,
    InvestigationCategory,
    InvestigationFlag,
    AllergySeverity,
    AllergyStatus,
)


def test_medication_model_valid():
    med = Medication(
        name="Metformin",
        dosage="500 mg",
        frequency="BID",
        route="PO",
        status=MedicationStatus.ACTIVE,
        indication="Type 2 Diabetes Mellitus",
        evidence_span="Metformin 500 mg BID PO for T2DM",
    )
    assert med.name == "Metformin"
    assert med.dosage == "500 mg"
    assert med.status == MedicationStatus.ACTIVE
    assert med.confidence == 1.0


def test_diagnosis_assertion_status():
    dx_confirmed = Diagnosis(
        condition_name="Hypertension",
        assertion=AssertionStatus.CONFIRMED,
        acuity="chronic",
    )
    assert dx_confirmed.assertion == AssertionStatus.CONFIRMED

    dx_negated = Diagnosis(
        condition_name="Chest pain",
        assertion=AssertionStatus.RULED_OUT,
        evidence_span="Patient denies chest pain",
    )
    assert dx_negated.assertion == AssertionStatus.RULED_OUT


def test_investigation_model():
    inv = Investigation(
        test_name="Hemoglobin A1c",
        category=InvestigationCategory.LABORATORY,
        value="8.4",
        unit="%",
        flag=InvestigationFlag.HIGH,
        evidence_span="HbA1c was 8.4%",
    )
    assert inv.test_name == "Hemoglobin A1c"
    assert inv.value == "8.4"
    assert inv.flag == InvestigationFlag.HIGH


def test_allergy_nkda_model():
    allergy = Allergy(
        allergen="NKDA",
        status=AllergyStatus.NKDA_REPORTED,
        evidence_span="Allergies: NKDA",
    )
    assert allergy.status == AllergyStatus.NKDA_REPORTED

    result = ClinicalExtractionResult(allergies=[allergy])
    assert result.has_nkda() is True


def test_extraction_result_markdown_report():
    result = ClinicalExtractionResult(
        medications=[
            Medication(name="Lisinopril", dosage="10 mg", frequency="daily", route="PO")
        ],
        diagnoses=[
            Diagnosis(condition_name="Essential Hypertension", assertion=AssertionStatus.CONFIRMED),
            Diagnosis(condition_name="Myocardial Infarction", assertion=AssertionStatus.RULED_OUT),
        ],
        investigations=[
            Investigation(test_name="Serum Potassium", value="4.2", unit="mEq/L", flag=InvestigationFlag.NORMAL)
        ],
        allergies=[
            Allergy(allergen="Penicillin", reaction="Urticaria", severity=AllergySeverity.MODERATE)
        ],
        metadata=ExtractionMetadata(engine="test_engine", word_count=45, processing_time_ms=12.5),
    )

    assert len(result.confirmed_diagnoses()) == 1
    assert len(result.ruled_out_diagnoses()) == 1
    assert len(result.active_medications()) == 1

    report = result.to_markdown_report()
    assert "# Clinical Extraction Summary" in report
    assert "Lisinopril" in report
    assert "Essential Hypertension" in report
    assert "Serum Potassium" in report
    assert "Penicillin" in report
