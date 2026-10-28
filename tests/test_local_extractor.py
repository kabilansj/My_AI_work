"""Unit tests for the local rule-based clinical extractor."""

import pytest
from clinical_extractor.extractors.local_extractor import LocalClinicalExtractor
from clinical_extractor.models.entities import (
    AssertionStatus,
    MedicationStatus,
    AllergyStatus,
    AllergySeverity,
    InvestigationFlag,
)


@pytest.fixture
def extractor():
    return LocalClinicalExtractor()


def test_medication_extraction_details(extractor):
    note = "Patient was started on Metformin 500 mg BID PO and Lisinopril 10 mg daily PO."
    result = extractor.extract(note)

    med_names = [m.name for m in result.medications]
    assert "Metformin" in med_names
    assert "Lisinopril" in med_names

    metformin = next(m for m in result.medications if m.name == "Metformin")
    assert metformin.dosage == "500 mg"
    assert metformin.frequency == "BID"
    assert metformin.route == "PO"
    assert metformin.status == MedicationStatus.ACTIVE


def test_assertion_and_negation_detection(extractor):
    note = (
        "Chief Complaint: Follow up.\n"
        "Assessment: Patient has hypertension and type 2 diabetes mellitus. "
        "Patient denies chest pain and denies shortness of breath. "
        "History of resolved asthma in childhood. "
        "Family history of coronary artery disease."
    )
    result = extractor.extract(note)

    dx_map = {d.condition_name.lower(): d.assertion for d in result.diagnoses}

    # Confirmed
    assert dx_map.get("hypertension") == AssertionStatus.CONFIRMED
    assert dx_map.get("type 2 diabetes mellitus") == AssertionStatus.CONFIRMED

    # Negated / Ruled out
    assert dx_map.get("chest pain") == AssertionStatus.RULED_OUT
    assert dx_map.get("shortness of breath") == AssertionStatus.RULED_OUT

    # Historical & Family
    assert dx_map.get("asthma") == AssertionStatus.HISTORICAL
    assert dx_map.get("coronary artery disease") == AssertionStatus.FAMILY_HISTORY


def test_investigations_extraction(extractor):
    note = "Labs: HbA1c was 8.4%. Serum Creatinine 1.2 mg/dL. Potassium 4.2 mEq/L. CXR clear."
    result = extractor.extract(note)

    test_names = [inv.test_name for inv in result.investigations]
    assert any("HBA1C" in t.upper() for t in test_names)
    assert any("CREATININE" in t.upper() for t in test_names)
    assert any("POTASSIUM" in t.upper() for t in test_names)
    assert any("CXR" in t.upper() or "CHEST" in t.upper() for t in test_names)

    cxr = next(inv for inv in result.investigations if "CXR" in inv.test_name.upper())
    assert cxr.flag == InvestigationFlag.NORMAL


def test_allergies_extraction_and_nkda(extractor):
    # Note with specific drug allergies
    note_with_allergies = "ALLERGIES: Penicillin causing hives. Sulfa with anaphylaxis."
    res1 = extractor.extract(note_with_allergies)
    allergens = {a.allergen.lower(): a for a in res1.allergies}
    assert "penicillin" in allergens
    assert allergens["penicillin"].reaction == "hives"
    assert "sulfa" in allergens
    assert allergens["sulfa"].severity == AllergySeverity.SEVERE

    # Note with NKDA
    note_nkda = "ALLERGIES: NKDA. Patient has no known drug allergies."
    res2 = extractor.extract(note_nkda)
    assert res2.has_nkda() is True
