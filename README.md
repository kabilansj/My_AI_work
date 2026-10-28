# Clinical Intelligence & Extraction Platform

An enterprise-grade, human-in-the-loop (HITL) clinical NLP platform designed to extract, ground, and review **Medications**, **Diagnoses**, **Investigations**, and **Allergies** from unstructured clinical text, transcripts, and PDF discharge summaries.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons |
| **Backend** | Python 3.9+, FastAPI, Pydantic v2, Uvicorn |
| **Database & ORM** | PostgreSQL / SQLite fallback, SQLAlchemy 2.0 |
| **AI / NLP** | Dual-Engine: Google Gemini API + Offline Deterministic Rule/Regex Lexicon Engine |
| **Document Ingestion** | PyMuPDF (`fitz`), `pdfplumber` |
| **Governance & Audit** | Immutable event sourcing audit log stream |
| **Testing** | Pytest (24 unit and integration tests passing) |

---

## Local Development & Live Services

Both services are configured to run seamlessly side-by-side:

### 1. Backend Server (FastAPI)
- **Local URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Command to run manually**:
  ```bash
  PYTHONPATH="src:." ./.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
  ```

### 2. Frontend Application (React + Vite)
- **Local URL**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **Command to run manually**:
  ```bash
  cd frontend
  npm run dev -- --host 127.0.0.1
  ```

---

## Core Capabilities & UI Features

### 1. Split-Pane Workspace & Evidence Grounding
- **Left Pane (Document Viewer)**: Displays verbatim clinical notes with instant text search. Clicking any extracted entity in the right pane highlights its exact `evidence_span` in yellow/amber within the original text.
- **Right Pane (Entity Review Stream)**: Tabbed categories for **Medications**, **Diagnoses**, **Investigations**, and **Allergies** with status filters (*All, Pending, Accepted, Rejected*).

### 2. Human-in-the-Loop (HITL) Actions
Every extracted entity supports 1-click clinical sign-off:
- **Approve (Check)**: Marks entity as `accepted` with reviewer ID and timestamp.
- **Edit (Pencil)**: Opens an editing modal to adjust dosage, frequency, condition name, or flags with reviewer rationale.
- **Reject (Cross)**: Prompts for clinical justification and marks entity as `rejected`.

### 3. Immutable Audit Trail
Clicking the history icon in the header opens a slide-over **Audit & Governance Drawer** detailing every automated extraction and human modification with diffs and timestamps.

### 4. Sample Clinical Notes
The UI includes one-click buttons to load realistic sample notes:
- **Sample: Heart Failure**: Complex discharge summary featuring multiple medications, cardiac labs, CXR imaging, and drug allergies.
- **Sample: Diabetes**: Outpatient clinic note featuring active vs negated findings (*"denies chest pain"*), lab panels (*HbA1c 7.8%*), and explicit **NKDA** documentation.

---

## API Endpoints Reference

### Documents
- `POST /api/documents/upload`: Upload PDF or text file (parsed via PyMuPDF/pdfplumber).
- `POST /api/documents/text`: Ingest raw clinical text.
- `POST /api/documents/sample/{discharge|diabetes}`: Load pre-configured sample note.
- `GET /api/documents`: List uploaded documents.
- `GET /api/documents/{id}`: Fetch document details and text.

### Extractions
- `POST /api/documents/{id}/extract?engine=auto|local|llm`: Run clinical NLP extraction and persist entities.
- `GET /api/documents/{id}/extraction`: Retrieve extraction results with review statuses.

### Human-in-the-Loop Review
- `POST /api/review/{type}/{id}/accept`: Approve extracted entity.
- `POST /api/review/{type}/{id}/modify`: Update entity fields with clinician notes.
- `POST /api/review/{type}/{id}/reject`: Reject entity with clinical reason.
- `GET /api/audit-logs`: Fetch chronological audit event stream.

---

## Running Automated Tests

```bash
PYTHONPATH="src:." ./.venv/bin/pytest
# ======================== 24 passed in 0.60s ========================
```
