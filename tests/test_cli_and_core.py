"""Unit and integration tests for ClinicalNLP core orchestrator and CLI."""

import json
from pathlib import Path
import pytest
from clinical_extractor.core import ClinicalNLP
from clinical_extractor.cli import main, parse_args, SAMPLE_CLINICAL_NOTE
from clinical_extractor.models.entities import AssertionStatus


def test_clinical_nlp_facade_local():
    nlp = ClinicalNLP(engine="local")
    note = "Patient has essential hypertension. Takes Lisinopril 10 mg daily. Denies chest pain. NKDA."
    result = nlp.extract(note)

    assert len(result.medications) >= 1
    assert result.medications[0].name == "Lisinopril"
    assert result.has_nkda() is True

    # Check negated diagnosis
    negated_dx = result.ruled_out_diagnoses()
    assert any(d.condition_name.lower() == "chest pain" for d in negated_dx)


def test_clinical_nlp_extract_file(tmp_path):
    note_file = tmp_path / "patient_note.txt"
    note_file.write_text("Patient diagnosed with type 2 diabetes. Started on Metformin 500 mg BID.")

    nlp = ClinicalNLP(engine="local")
    result = nlp.extract_file(note_file)

    assert any(m.name == "Metformin" for m in result.medications)
    assert any("diabetes" in d.condition_name.lower() for d in result.diagnoses)


def test_clinical_nlp_file_not_found():
    nlp = ClinicalNLP(engine="local")
    with pytest.raises(FileNotFoundError):
        nlp.extract_file("non_existent_note_12345.txt")


def test_cli_sample_run(capsys):
    # Test --sample with default summary format
    main(["--sample", "--engine", "local"])
    captured = capsys.readouterr()
    assert "CLINICAL ENTITY EXTRACTION RESULTS" in captured.out
    assert "Metformin" in captured.out
    assert "Type 2 Diabetes" in captured.out


def test_cli_sample_json_output(capsys):
    main(["--sample", "--engine", "local", "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "medications" in data
    assert "diagnoses" in data
    assert "investigations" in data
    assert "allergies" in data
    assert len(data["medications"]) > 0


def test_cli_output_to_file(tmp_path):
    out_file = tmp_path / "output_report.md"
    main(["--sample", "--engine", "local", "--format", "markdown", "--output", str(out_file)])
    assert out_file.exists()
    content = out_file.read_text()
    assert "# Clinical Extraction Summary" in content
    assert "Metformin" in content
