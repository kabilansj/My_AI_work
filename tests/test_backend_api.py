"""End-to-end integration tests for FastAPI backend, HITL review, and audit logging."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.database import Base, get_db

# Use an isolated in-memory SQLite database with StaticPool so all connections share the memory DB
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_health_check():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


def test_full_document_extraction_and_hitl_workflow():
    # 1. Load sample document
    resp_doc = client.post("/api/documents/sample/discharge")
    assert resp_doc.status_code == 200
    doc = resp_doc.json()
    doc_id = doc["id"]
    assert "Furosemide" in doc["raw_text"]

    # 2. Run extraction (using local engine for deterministic speed)
    resp_extract = client.post(f"/api/documents/{doc_id}/extract?engine=local")
    assert resp_extract.status_code == 200
    extraction = resp_extract.json()
    assert len(extraction["medications"]) >= 3
    assert len(extraction["diagnoses"]) >= 3
    assert len(extraction["allergies"]) >= 1

    # Check pending initial review status
    med = extraction["medications"][0]
    assert med["review_status"] == "pending"

    # 3. HITL Action: Accept Medication
    resp_accept = client.post(
        f"/api/review/medications/{med['id']}/accept",
        json={"reviewed_by": "Dr. House", "notes": "Verified against patient discharge list."},
    )
    assert resp_accept.status_code == 200
    assert resp_accept.json()["review_status"] == "accepted"

    # 4. HITL Action: Modify Diagnosis
    dx = extraction["diagnoses"][0]
    resp_modify = client.post(
        f"/api/review/diagnoses/{dx['id']}/modify",
        json={
            "reviewed_by": "Dr. House",
            "notes": "Refined diagnosis classification",
            "updates": {"acuity": "chronic", "icd10_hint": "I50.9"},
        },
    )
    assert resp_modify.status_code == 200
    assert resp_modify.json()["review_status"] == "modified"

    # 5. HITL Action: Reject an Investigation
    inv = extraction["investigations"][0]
    resp_reject = client.post(
        f"/api/review/investigations/{inv['id']}/reject",
        json={"reviewed_by": "Dr. House", "reason": "Artifact or duplicate entry"},
    )
    assert resp_reject.status_code == 200
    assert resp_reject.json()["review_status"] == "rejected"

    # 6. Verify Updated Extraction State
    resp_updated = client.get(f"/api/documents/{doc_id}/extraction")
    assert resp_updated.status_code == 200
    updated_data = resp_updated.json()

    updated_med = next(m for m in updated_data["medications"] if m["id"] == med["id"])
    assert updated_med["review_status"] == "accepted"
    assert updated_med["reviewed_by"] == "Dr. House"

    updated_dx = next(d for d in updated_data["diagnoses"] if d["id"] == dx["id"])
    assert updated_dx["review_status"] == "modified"
    assert updated_dx["icd10_hint"] == "I50.9"

    updated_inv = next(i for i in updated_data["investigations"] if i["id"] == inv["id"])
    assert updated_inv["review_status"] == "rejected"

    # 7. Verify Immutable Audit Logs
    resp_audit = client.get(f"/api/audit-logs?document_id={doc_id}")
    assert resp_audit.status_code == 200
    audit_logs = resp_audit.json()
    actions = [a["action"] for a in audit_logs]

    assert "AUTO_EXTRACTED" in actions
    assert "ACCEPTED" in actions
    assert "MODIFIED" in actions
    assert "REJECTED" in actions
