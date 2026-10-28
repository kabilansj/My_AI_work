import { ClinicalDocument, ExtractionDetail, AuditLog } from '../types/clinical';

const BASE_URL = '/api';

export const api = {
  async fetchDocuments(): Promise<ClinicalDocument[]> {
    const res = await fetch(`${BASE_URL}/documents`);
    if (!res.ok) throw new Error('Failed to fetch documents');
    return res.json();
  },

  async fetchDocument(id: string): Promise<ClinicalDocument> {
    const res = await fetch(`${BASE_URL}/documents/${id}`);
    if (!res.ok) throw new Error('Failed to fetch document');
    return res.json();
  },

  async loadSample(sampleName: 'discharge' | 'diabetes'): Promise<ClinicalDocument> {
    const res = await fetch(`${BASE_URL}/documents/sample/${sampleName}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to load sample document');
    return res.json();
  },

  async uploadFile(file: File): Promise<ClinicalDocument> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${BASE_URL}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Failed to upload file');
    return res.json();
  },

  async triggerExtraction(documentId: string, engine?: string): Promise<ExtractionDetail> {
    const url = engine
      ? `${BASE_URL}/documents/${documentId}/extract?engine=${engine}`
      : `${BASE_URL}/documents/${documentId}/extract`;
    const res = await fetch(url, { method: 'POST' });
    if (!res.ok) throw new Error('Extraction failed');
    return res.json();
  },

  async fetchExtraction(documentId: string): Promise<ExtractionDetail> {
    const res = await fetch(`${BASE_URL}/documents/${documentId}/extraction`);
    if (!res.ok) throw new Error('No extractions found');
    return res.json();
  },

  async acceptEntity(
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy',
    id: string,
    reviewedBy = 'Dr. Reviewer',
    notes?: string
  ) {
    const res = await fetch(`${BASE_URL}/review/${type}/${id}/accept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonBody({ reviewed_by: reviewedBy, notes }),
    });
    if (!res.ok) throw new Error('Failed to accept entity');
    return res.json();
  },

  async modifyEntity(
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy',
    id: string,
    updates: Record<string, any>,
    reviewedBy = 'Dr. Reviewer',
    notes?: string
  ) {
    const res = await fetch(`${BASE_URL}/review/${type}/${id}/modify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonBody({ reviewed_by: reviewedBy, notes, updates }),
    });
    if (!res.ok) throw new Error('Failed to modify entity');
    return res.json();
  },

  async rejectEntity(
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy',
    id: string,
    reason: string,
    reviewedBy = 'Dr. Reviewer'
  ) {
    const res = await fetch(`${BASE_URL}/review/${type}/${id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: jsonBody({ reviewed_by: reviewedBy, reason }),
    });
    if (!res.ok) throw new Error('Failed to reject entity');
    return res.json();
  },

  async fetchAuditLogs(documentId?: string): Promise<AuditLog[]> {
    const url = documentId
      ? `${BASE_URL}/audit-logs?document_id=${documentId}`
      : `${BASE_URL}/audit-logs`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch audit logs');
    return res.json();
  },
};

function jsonBody(obj: any): string {
  return JSON.stringify(obj);
}
