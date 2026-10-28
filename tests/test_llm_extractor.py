"""Unit tests for the LLM structured extractor."""

import json
import pytest
from clinical_extractor.extractors.llm_extractor import LLMClinicalExtractor
from clinical_extractor.models.entities import (
    AssertionStatus,
    MedicationStatus,
    InvestigationFlag,
    AllergySeverity,
)


def mock_llm_client(system_prompt: str, user_prompt: str) -> str:
    """Mock LLM response simulating a model adhering to schema."""
    data = {
        "medications": [
            {
                "name": "Metformin",
                "dosage": "500 mg",
                "frequency": "BID",
                "route": "oral",
                "status": "active",
                "indication": "Type 2 Diabetes",
                "evidence_span": "Metformin 500 mg BID oral",
            }
        ],
        "diagnoses": [
            {
                "condition_name": "Type 2 Diabetes Mellitus",
                "assertion": "confirmed",
                "acuity": "chronic",
                "icd10_hint": "E11",
                "evidence_span": "Type 2 Diabetes Mellitus",
            },
            {
                "condition_name": "Chest Pain",
                "assertion": "ruled_out",
                "acuity": "acute",
                "evidence_span": "denies chest pain",
            },
        ],
        "investigations": [
            {
                "test_name": "HbA1c",
                "category": "laboratory",
                "value": "8.1",
                "unit": "%",
                "flag": "high",
                "evidence_span": "HbA1c was 8.1%",
            }
        ],
        "allergies": [
            {
                "allergen": "Penicillin",
                "reaction": "Anaphylaxis",
                "severity": "severe",
                "allergy_type": "drug",
                "status": "active",
                "evidence_span": "Penicillin (anaphylaxis)",
            }
        ],
    }
    return json.dumps(data)


def test_llm_extractor_mock_flow():
    clinical_note = (
        "Patient has Type 2 Diabetes Mellitus. Denies chest pain. "
        "Started on Metformin 500 mg BID oral. "
        "HbA1c was 8.1%. ALLERGIES: Penicillin (anaphylaxis)."
    )

    extractor = LLMClinicalExtractor(
        client_fn=mock_llm_client,
        model_name="test-llm-model",
    )

    result = extractor.extract(clinical_note)

    # Validate medications
    assert len(result.medications) == 1
    assert result.medications[0].name == "Metformin"
    assert result.medications[0].dosage == "500 mg"
    assert result.medications[0].status == MedicationStatus.ACTIVE

    # Validate diagnoses
    assert len(result.diagnoses) == 2
    dx_confirmed = next(d for d in result.diagnoses if d.assertion == AssertionStatus.CONFIRMED)
    assert dx_confirmed.condition_name == "Type 2 Diabetes Mellitus"

    dx_negated = next(d for d in result.diagnoses if d.assertion == AssertionStatus.RULED_OUT)
    assert dx_negated.condition_name == "Chest Pain"

    # Validate investigations
    assert len(result.investigations) == 1
    assert result.investigations[0].test_name == "HbA1c"
    assert result.investigations[0].flag == InvestigationFlag.HIGH

    # Validate allergies
    assert len(result.allergies) == 1
    assert result.allergies[0].allergen == "Penicillin"
    assert result.allergies[0].severity == AllergySeverity.SEVERE


def test_llm_extractor_markdown_json_strip():
    """Verify that ```json ... ``` wrapped responses are handled cleanly."""
    def markdown_client(sys, user):
        return "```json\n{\"medications\": [{\"name\": \"Aspirin\", \"dosage\": \"81 mg\"}], \"diagnoses\": [], \"investigations\": [], \"allergies\": []}\n```"

    extractor = LLMClinicalExtractor(client_fn=markdown_client)
    result = extractor.extract("Patient takes Aspirin 81 mg.")
    assert len(result.medications) == 1
    assert result.medications[0].name == "Aspirin"


def test_llm_extractor_ungrounded_warning():
    """Check that hallucinations/ungrounded spans trigger warnings and confidence downgrade."""
    def hallucinating_client(sys, user):
        return json.dumps({
            "medications": [
                {
                    "name": "Digoxin",
                    "evidence_span": "patient takes digoxin 0.25 mg daily",
                }
            ],
            "diagnoses": [],
            "investigations": [],
            "allergies": [],
        })

    extractor = LLMClinicalExtractor(client_fn=hallucinating_client)
    # The note has NO mention of digoxin
    result = extractor.extract("Patient presents with hypertension.")
    assert len(result.medications) == 1
    assert result.medications[0].confidence == 0.5
    assert len(result.metadata.warnings) > 0
