export interface ClinicalDocument {
  id: string;
  filename: string;
  mime_type: string;
  raw_text: string;
  created_at: string;
}

export interface Medication {
  id: string;
  name: string;
  dosage?: string | null;
  frequency?: string | null;
  route?: string | null;
  status: string;
  indication?: string | null;
  evidence_span?: string | null;
  confidence: number;
  review_status: 'pending' | 'accepted' | 'modified' | 'rejected';
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  reviewer_notes?: string | null;
}

export interface Diagnosis {
  id: string;
  condition_name: string;
  assertion: 'confirmed' | 'ruled_out' | 'suspected' | 'historical' | 'family_history';
  acuity?: string | null;
  icd10_hint?: string | null;
  evidence_span?: string | null;
  confidence: number;
  review_status: 'pending' | 'accepted' | 'modified' | 'rejected';
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  reviewer_notes?: string | null;
}

export interface Investigation {
  id: string;
  test_name: string;
  category: string;
  value?: string | null;
  unit?: string | null;
  reference_range?: string | null;
  flag: string;
  evidence_span?: string | null;
  confidence: number;
  review_status: 'pending' | 'accepted' | 'modified' | 'rejected';
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  reviewer_notes?: string | null;
}

export interface Allergy {
  id: string;
  allergen: string;
  reaction?: string | null;
  severity: string;
  allergy_type: string;
  status: string;
  evidence_span?: string | null;
  confidence: number;
  review_status: 'pending' | 'accepted' | 'modified' | 'rejected';
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  reviewer_notes?: string | null;
}

export interface ExtractionDetail {
  id: string;
  document_id: string;
  engine: string;
  model_name?: string | null;
  processing_time_ms: number;
  status: string;
  created_at: string;
  medications: Medication[];
  diagnoses: Diagnosis[];
  investigations: Investigation[];
  allergies: Allergy[];
}

export interface AuditLog {
  id: string;
  document_id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  prior_state?: string | null;
  new_state?: string | null;
  user_id: string;
  reason?: string | null;
  created_at: string;
}
