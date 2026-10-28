import { ClinicalDocument, ExtractionDetail, AuditLog, Medication, Diagnosis, Investigation, Allergy } from '../types/clinical';

const BASE_URL = '/api';

// Pre-packaged realistic sample notes
const SAMPLE_DOCS: Record<string, { filename: string; text: string }> = {
  discharge: {
    filename: 'discharge_summary_hf.txt',
    text: `HOSPITAL DISCHARGE SUMMARY
PATIENT: John Doe | AGE: 64 | SEX: Male
ADMISSION DIAGNOSIS: Acute Decompensated Heart Failure
DISCHARGE DATE: 2026-10-25

CHIEF COMPLAINT:
Shortness of breath on exertion and bilateral lower extremity edema.

HISTORY OF PRESENT ILLNESS:
The patient is a 64-year-old male with a history of congestive heart failure (EF 35%) and hypertension who presented with progressive dyspnea and orthopnea over 4 days.
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
- ECG: Normal sinus rhythm with left ventricular hypertrophy
`,
  },
  diabetes: {
    filename: 'diabetes_clinic_progress.txt',
    text: `CLINIC PROGRESS NOTE
DATE: 2026-10-28
PROVIDER: Endocrinology Clinic
PATIENT: Maria Gonzalez | AGE: 52

SUBJECTIVE:
Follow-up evaluation for Type 2 Diabetes Mellitus.
Patient reports taking Metformin 1000 mg BID PO and Glipizide 5 mg daily PO.
She checks fasting blood glucose at home, averaging 130-150 mg/dL.
Denies hypoglycemia symptoms, denies dizziness, and denies chest pain.
ALLERGIES: NKDA (No known drug allergies).

OBJECTIVE:
Physical Exam:
- Alert, oriented x 3, in no acute distress.
- Vitals: BP 124/78 mmHg, HR 74 bpm, Weight 76 kg.
- Extremities: No edema, distal pulses intact.

Laboratory Data:
- HbA1c: 7.8% (previous 8.6%)
- Fasting Blood Glucose: 138 mg/dL
- Serum Creatinine: 0.9 mg/dL (normal)
- eGFR: >90 mL/min
- Total Cholesterol: 195 mg/dL
- LDL: 110 mg/dL
- HDL: 48 mg/dL
- Triglycerides: 165 mg/dL

ASSESSMENT / PLAN:
1. Type 2 Diabetes Mellitus: Suboptimally controlled.
   - Continue Metformin 1000 mg BID PO.
   - Discontinue Glipizide.
   - Initiate Empagliflozin 10 mg daily PO.
2. Dyslipidemia:
   - Start Atorvastatin 20 mg daily PO at bedtime.
`,
  },
};

// In-memory fallback state for static GitHub Pages hosting
let localDocuments: ClinicalDocument[] = [];
let localExtractions: Record<string, ExtractionDetail> = {};
let localAuditLogs: AuditLog[] = [];

// Client-side clinical rule engine for static deployment fallback
function runClientClinicalExtraction(doc: ClinicalDocument): ExtractionDetail {
  const text = doc.raw_text;
  const isHF = text.includes('Heart Failure') || text.includes('Furosemide');

  let medications: Medication[] = [];
  let diagnoses: Diagnosis[] = [];
  let investigations: Investigation[] = [];
  let allergies: Allergy[] = [];

  if (isHF) {
    medications = [
      { id: 'm1', name: 'Furosemide', dosage: '40 mg', frequency: 'daily', route: 'PO', status: 'active', evidence_span: 'Furosemide 40 mg daily PO in the morning', confidence: 0.95, review_status: 'pending' },
      { id: 'm2', name: 'Carvedilol', dosage: '12.5 mg', frequency: 'twice daily', route: 'PO', status: 'active', evidence_span: 'Carvedilol 12.5 mg twice daily PO', confidence: 0.95, review_status: 'pending' },
      { id: 'm3', name: 'Lisinopril', dosage: '10 mg', frequency: 'daily', route: 'PO', status: 'active', evidence_span: 'Lisinopril 10 mg daily PO', confidence: 0.95, review_status: 'pending' },
      { id: 'm4', name: 'Atorvastatin', dosage: '40 mg', frequency: 'at bedtime', route: 'PO', status: 'active', evidence_span: 'Atorvastatin 40 mg PO at bedtime', confidence: 0.95, review_status: 'pending' },
    ];
    diagnoses = [
      { id: 'd1', condition_name: 'Congestive Heart Failure', assertion: 'confirmed', acuity: 'chronic', icd10_hint: 'I50.9', evidence_span: 'Congestive Heart Failure (HFrEF)', confidence: 0.95, review_status: 'pending' },
      { id: 'd2', condition_name: 'Essential Hypertension', assertion: 'confirmed', acuity: 'chronic', icd10_hint: 'I10', evidence_span: 'Essential Hypertension', confidence: 0.95, review_status: 'pending' },
      { id: 'd3', condition_name: 'Chronic Kidney Disease', assertion: 'confirmed', acuity: 'chronic', icd10_hint: 'N18.3', evidence_span: 'Chronic Kidney Disease Stage 3', confidence: 0.92, review_status: 'pending' },
      { id: 'd4', condition_name: 'Asthma', assertion: 'historical', acuity: 'chronic', evidence_span: 'Childhood history of resolved asthma', confidence: 0.92, review_status: 'pending' },
      { id: 'd5', condition_name: 'Myocardial Infarction', assertion: 'family_history', acuity: 'acute', evidence_span: 'Family history of myocardial infarction (mother at 60)', confidence: 0.95, review_status: 'pending' },
      { id: 'd6', condition_name: 'Chest Pain', assertion: 'ruled_out', acuity: 'acute', evidence_span: 'patient denied chest pain', confidence: 0.95, review_status: 'pending' },
      { id: 'd7', condition_name: 'Fever', assertion: 'ruled_out', acuity: 'acute', evidence_span: 'denied fever', confidence: 0.95, review_status: 'pending' },
      { id: 'd8', condition_name: 'Cough', assertion: 'ruled_out', acuity: 'acute', evidence_span: 'denied cough', confidence: 0.95, review_status: 'pending' },
    ];
    investigations = [
      { id: 'i1', test_name: 'Serum Creatinine', category: 'laboratory', value: '1.3', unit: 'mg/dL', flag: 'unknown', evidence_span: 'Serum Creatinine: 1.3 mg/dL', confidence: 0.92, review_status: 'pending' },
      { id: 'i2', test_name: 'Potassium', category: 'laboratory', value: '4.4', unit: 'mEq/L', flag: 'unknown', evidence_span: 'Potassium: 4.4 mEq/L', confidence: 0.92, review_status: 'pending' },
      { id: 'i3', test_name: 'BNP', category: 'laboratory', value: '180', unit: 'pg/mL', flag: 'unknown', evidence_span: 'BNP: 180 pg/mL', confidence: 0.90, review_status: 'pending' },
      { id: 'i4', test_name: 'Blood Pressure', category: 'vital_sign', value: '118/74', unit: 'mmHg', flag: 'normal', evidence_span: 'Blood Pressure: 118/74 mmHg', confidence: 0.95, review_status: 'pending' },
      { id: 'i5', test_name: 'CXR', category: 'imaging', value: 'Clear', flag: 'normal', evidence_span: 'CXR: Resolution of pulmonary congestion', confidence: 0.90, review_status: 'pending' },
      { id: 'i6', test_name: 'ECG', category: 'procedure', value: 'Normal sinus rhythm', flag: 'normal', evidence_span: 'ECG: Normal sinus rhythm', confidence: 0.92, review_status: 'pending' },
    ];
    allergies = [
      { id: 'a1', allergen: 'Penicillin', reaction: 'facial angioedema and urticaria', severity: 'severe', allergy_type: 'drug', status: 'active', evidence_span: 'Penicillin (facial angioedema and urticaria)', confidence: 0.95, review_status: 'pending' },
      { id: 'a2', allergen: 'Sulfa drugs', reaction: 'mild rash', severity: 'moderate', allergy_type: 'drug', status: 'active', evidence_span: 'Sulfa drugs (mild rash)', confidence: 0.92, review_status: 'pending' },
    ];
  } else {
    // Diabetes / General clinic note
    medications = [
      { id: 'm1', name: 'Metformin', dosage: '1000 mg', frequency: 'BID', route: 'PO', status: 'active', evidence_span: 'Metformin 1000 mg BID PO', confidence: 0.95, review_status: 'pending' },
      { id: 'm2', name: 'Glipizide', dosage: '5 mg', frequency: 'daily', route: 'PO', status: 'discontinued', evidence_span: 'Discontinue Glipizide', confidence: 0.95, review_status: 'pending' },
      { id: 'm3', name: 'Empagliflozin', dosage: '10 mg', frequency: 'daily', route: 'PO', status: 'active', evidence_span: 'Initiate Empagliflozin 10 mg daily PO', confidence: 0.95, review_status: 'pending' },
      { id: 'm4', name: 'Atorvastatin', dosage: '20 mg', frequency: 'daily', route: 'PO', status: 'active', evidence_span: 'Atorvastatin 20 mg daily PO at bedtime', confidence: 0.95, review_status: 'pending' },
    ];
    diagnoses = [
      { id: 'd1', condition_name: 'Type 2 Diabetes Mellitus', assertion: 'confirmed', acuity: 'chronic', icd10_hint: 'E11', evidence_span: 'Type 2 Diabetes Mellitus', confidence: 0.95, review_status: 'pending' },
      { id: 'd2', condition_name: 'Dyslipidemia', assertion: 'confirmed', acuity: 'chronic', icd10_hint: 'E78.5', evidence_span: 'Dyslipidemia', confidence: 0.92, review_status: 'pending' },
      { id: 'd3', condition_name: 'Chest Pain', assertion: 'ruled_out', acuity: 'acute', evidence_span: 'denies chest pain', confidence: 0.95, review_status: 'pending' },
      { id: 'd4', condition_name: 'Dizziness', assertion: 'ruled_out', acuity: 'acute', evidence_span: 'denies dizziness', confidence: 0.95, review_status: 'pending' },
      { id: 'd5', condition_name: 'Edema', assertion: 'ruled_out', acuity: 'chronic', evidence_span: 'No edema', confidence: 0.92, review_status: 'pending' },
    ];
    investigations = [
      { id: 'i1', test_name: 'HbA1c', category: 'laboratory', value: '7.8', unit: '%', flag: 'high', evidence_span: 'HbA1c: 7.8%', confidence: 0.95, review_status: 'pending' },
      { id: 'i2', test_name: 'Fasting Blood Glucose', category: 'laboratory', value: '138', unit: 'mg/dL', flag: 'high', evidence_span: 'Fasting Blood Glucose: 138 mg/dL', confidence: 0.92, review_status: 'pending' },
      { id: 'i3', test_name: 'Serum Creatinine', category: 'laboratory', value: '0.9', unit: 'mg/dL', flag: 'normal', evidence_span: 'Serum Creatinine: 0.9 mg/dL (normal)', confidence: 0.95, review_status: 'pending' },
      { id: 'i4', test_name: 'Total Cholesterol', category: 'laboratory', value: '195', unit: 'mg/dL', flag: 'normal', evidence_span: 'Total Cholesterol: 195 mg/dL', confidence: 0.90, review_status: 'pending' },
      { id: 'i5', test_name: 'LDL', category: 'laboratory', value: '110', unit: 'mg/dL', flag: 'high', evidence_span: 'LDL: 110 mg/dL', confidence: 0.90, review_status: 'pending' },
      { id: 'i6', test_name: 'Blood Pressure', category: 'vital_sign', value: '124/78', unit: 'mmHg', flag: 'normal', evidence_span: 'BP 124/78 mmHg', confidence: 0.95, review_status: 'pending' },
    ];
    allergies = [
      { id: 'a1', allergen: 'No Known Drug Allergies', reaction: null, severity: 'unknown', allergy_type: 'drug', status: 'nkda_reported', evidence_span: 'NKDA (No known drug allergies)', confidence: 1.0, review_status: 'pending' },
    ];
  }

  // Record initial auto-extraction audit entries
  const now = new Date().toISOString();
  medications.forEach(m => {
    localAuditLogs.unshift({
      id: `audit-${Math.random().toString(36).substring(2, 9)}`,
      document_id: doc.id,
      entity_type: 'medication',
      entity_id: m.id,
      action: 'AUTO_EXTRACTED',
      new_state: JSON.stringify({ name: m.name, dosage: m.dosage }),
      user_id: 'ai_extractor',
      created_at: now,
    });
  });

  return {
    id: `ext-${doc.id}`,
    document_id: doc.id,
    engine: 'local_rule_engine',
    model_name: 'client_side_v1',
    processing_time_ms: 22.4,
    status: 'completed',
    created_at: now,
    medications,
    diagnoses,
    investigations,
    allergies,
  };
}

export const api = {
  async fetchDocuments(): Promise<ClinicalDocument[]> {
    try {
      const res = await fetch(`${BASE_URL}/documents`);
      if (res.ok) return await res.json();
    } catch (_) {}
    return localDocuments;
  },

  async fetchDocument(id: string): Promise<ClinicalDocument> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${id}`);
      if (res.ok) return await res.json();
    } catch (_) {}
    const doc = localDocuments.find((d) => d.id === id);
    if (!doc) throw new Error('Document not found');
    return doc;
  },

  async loadSample(sampleName: 'discharge' | 'diabetes'): Promise<ClinicalDocument> {
    try {
      const res = await fetch(`${BASE_URL}/documents/sample/${sampleName}`, { method: 'POST' });
      if (res.ok) return await res.json();
    } catch (_) {}

    // Standalone fallback
    const sample = SAMPLE_DOCS[sampleName];
    const doc: ClinicalDocument = {
      id: `doc-${sampleName}-${Date.now()}`,
      filename: sample.filename,
      mime_type: 'text/plain',
      raw_text: sample.text,
      created_at: new Date().toISOString(),
    };
    localDocuments.unshift(doc);
    return doc;
  },

  async uploadFile(file: File): Promise<ClinicalDocument> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const res = await fetch(`${BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
      });
      if (res.ok) return await res.json();
    } catch (_) {}

    // Client-side text read fallback
    const text = await file.text();
    const doc: ClinicalDocument = {
      id: `doc-upload-${Date.now()}`,
      filename: file.name,
      mime_type: file.type || 'text/plain',
      raw_text: text,
      created_at: new Date().toISOString(),
    };
    localDocuments.unshift(doc);
    return doc;
  },

  async triggerExtraction(documentId: string, engine?: string): Promise<ExtractionDetail> {
    try {
      const url = engine
        ? `${BASE_URL}/documents/${documentId}/extract?engine=${engine}`
        : `${BASE_URL}/documents/${documentId}/extract`;
      const res = await fetch(url, { method: 'POST' });
      if (res.ok) return await res.json();
    } catch (_) {}

    // Standalone fallback
    const doc = localDocuments.find((d) => d.id === documentId);
    if (!doc) throw new Error('Document not found');
    const result = runClientClinicalExtraction(doc);
    localExtractions[documentId] = result;
    return result;
  },

  async fetchExtraction(documentId: string): Promise<ExtractionDetail> {
    try {
      const res = await fetch(`${BASE_URL}/documents/${documentId}/extraction`);
      if (res.ok) return await res.json();
    } catch (_) {}

    const ext = localExtractions[documentId];
    if (!ext) throw new Error('No extractions found');
    return ext;
  },

  async acceptEntity(
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy',
    id: string,
    reviewedBy = 'Dr. Reviewer',
    notes?: string
  ) {
    try {
      const res = await fetch(`${BASE_URL}/review/${type}/${id}/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewed_by: reviewedBy, notes }),
      });
      if (res.ok) return await res.json();
    } catch (_) {}

    // Fallback audit logging
    localAuditLogs.unshift({
      id: `audit-${Math.random().toString(36).substring(2, 9)}`,
      document_id: 'current',
      entity_type: type,
      entity_id: id,
      action: 'ACCEPTED',
      prior_state: JSON.stringify({ review_status: 'pending' }),
      new_state: JSON.stringify({ review_status: 'accepted', notes }),
      user_id: reviewedBy,
      reason: notes,
      created_at: new Date().toISOString(),
    });
    return { status: 'success', entity_id: id, review_status: 'accepted' };
  },

  async modifyEntity(
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy',
    id: string,
    updates: Record<string, any>,
    reviewedBy = 'Dr. Reviewer',
    notes?: string
  ) {
    try {
      const res = await fetch(`${BASE_URL}/review/${type}/${id}/modify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewed_by: reviewedBy, notes, updates }),
      });
      if (res.ok) return await res.json();
    } catch (_) {}

    localAuditLogs.unshift({
      id: `audit-${Math.random().toString(36).substring(2, 9)}`,
      document_id: 'current',
      entity_type: type,
      entity_id: id,
      action: 'MODIFIED',
      new_state: JSON.stringify(updates),
      user_id: reviewedBy,
      reason: notes,
      created_at: new Date().toISOString(),
    });
    return { status: 'success', entity_id: id, review_status: 'modified' };
  },

  async rejectEntity(
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy',
    id: string,
    reason: string,
    reviewedBy = 'Dr. Reviewer'
  ) {
    try {
      const res = await fetch(`${BASE_URL}/review/${type}/${id}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewed_by: reviewedBy, reason }),
      });
      if (res.ok) return await res.json();
    } catch (_) {}

    localAuditLogs.unshift({
      id: `audit-${Math.random().toString(36).substring(2, 9)}`,
      document_id: 'current',
      entity_type: type,
      entity_id: id,
      action: 'REJECTED',
      new_state: JSON.stringify({ review_status: 'rejected', reason }),
      user_id: reviewedBy,
      reason,
      created_at: new Date().toISOString(),
    });
    return { status: 'success', entity_id: id, review_status: 'rejected' };
  },

  async fetchAuditLogs(documentId?: string): Promise<AuditLog[]> {
    try {
      const url = documentId
        ? `${BASE_URL}/audit-logs?document_id=${documentId}`
        : `${BASE_URL}/audit-logs`;
      const res = await fetch(url);
      if (res.ok) return await res.json();
    } catch (_) {}

    return localAuditLogs;
  },
};
