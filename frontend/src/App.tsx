import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { DocumentViewer } from './components/DocumentViewer';
import { CategorySection } from './components/CategorySection';
import { EditEntityModal } from './components/EditEntityModal';
import { AuditDrawer } from './components/AuditDrawer';
import { api } from './api/client';
import { ClinicalDocument, ExtractionDetail, AuditLog } from './types/clinical';

export const App: React.FC = () => {
  const [engine, setEngine] = useState<string>('auto');
  const [currentDoc, setCurrentDoc] = useState<ClinicalDocument | null>(null);
  const [extraction, setExtraction] = useState<ExtractionDetail | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [auditOpen, setAuditOpen] = useState<boolean>(false);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);

  // Edit Modal State
  const [editModal, setEditModal] = useState<{
    isOpen: boolean;
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy';
    entity: any;
  }>({
    isOpen: false,
    type: 'medication',
    entity: null,
  });

  // Load sample heart failure note on initial load
  useEffect(() => {
    handleLoadSample('discharge');
  }, []);

  const handleLoadSample = async (sampleName: 'discharge' | 'diabetes') => {
    try {
      setIsProcessing(true);
      const doc = await api.loadSample(sampleName);
      setCurrentDoc(doc);
      setSelectedEvidence(null);

      // Auto trigger extraction
      const ext = await api.triggerExtraction(doc.id, engine);
      setExtraction(ext);
      refreshAuditLogs(doc.id);
    } catch (err) {
      console.error('Failed to load sample note:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setIsProcessing(true);
      const doc = await api.uploadFile(file);
      setCurrentDoc(doc);
      setSelectedEvidence(null);

      const ext = await api.triggerExtraction(doc.id, engine);
      setExtraction(ext);
      refreshAuditLogs(doc.id);
    } catch (err) {
      console.error('Failed to upload file:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTriggerExtract = async () => {
    if (!currentDoc) return;
    try {
      setIsProcessing(true);
      const ext = await api.triggerExtraction(currentDoc.id, engine);
      setExtraction(ext);
      refreshAuditLogs(currentDoc.id);
    } catch (err) {
      console.error('Extraction failed:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const refreshAuditLogs = async (docId?: string) => {
    try {
      const logs = await api.fetchAuditLogs(docId);
      setAuditLogs(logs);
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
    }
  };

  // HITL Action: Accept
  const handleAccept = async (type: 'medication' | 'diagnosis' | 'investigation' | 'allergy', id: string) => {
    try {
      await api.acceptEntity(type, id);
      updateEntityStatus(type, id, 'accepted');
      if (currentDoc) refreshAuditLogs(currentDoc.id);
    } catch (err) {
      console.error(`Failed to accept ${type}:`, err);
    }
  };

  // HITL Action: Open Edit Modal
  const handleOpenEdit = (type: 'medication' | 'diagnosis' | 'investigation' | 'allergy', entity: any) => {
    setEditModal({ isOpen: true, type, entity });
  };

  // HITL Action: Save Edit
  const handleSaveEdit = async (updates: Record<string, any>, notes: string) => {
    if (!editModal.entity) return;
    try {
      await api.modifyEntity(editModal.type, editModal.entity.id, updates, 'Dr. Reviewer', notes);
      updateEntityFields(editModal.type, editModal.entity.id, { ...updates, review_status: 'modified', reviewer_notes: notes });
      if (currentDoc) refreshAuditLogs(currentDoc.id);
    } catch (err) {
      console.error(`Failed to modify ${editModal.type}:`, err);
    }
  };

  // HITL Action: Reject
  const handleReject = async (type: 'medication' | 'diagnosis' | 'investigation' | 'allergy', id: string) => {
    const reason = window.prompt('Enter reason for rejection (clinical justification):', 'Not clinically relevant or negated');
    if (!reason) return;

    try {
      await api.rejectEntity(type, id, reason);
      updateEntityStatus(type, id, 'rejected', reason);
      if (currentDoc) refreshAuditLogs(currentDoc.id);
    } catch (err) {
      console.error(`Failed to reject ${type}:`, err);
    }
  };

  const updateEntityStatus = (
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy',
    id: string,
    status: 'accepted' | 'modified' | 'rejected',
    notes?: string
  ) => {
    if (!extraction) return;
    const key = type === 'medication' ? 'medications' : type === 'diagnosis' ? 'diagnoses' : type === 'investigation' ? 'investigations' : 'allergies';
    const updatedList = (extraction[key] as any[]).map((item) =>
      item.id === id ? { ...item, review_status: status, reviewer_notes: notes || item.reviewer_notes } : item
    );
    setExtraction({ ...extraction, [key]: updatedList });
  };

  const updateEntityFields = (
    type: 'medication' | 'diagnosis' | 'investigation' | 'allergy',
    id: string,
    fields: Record<string, any>
  ) => {
    if (!extraction) return;
    const key = type === 'medication' ? 'medications' : type === 'diagnosis' ? 'diagnoses' : type === 'investigation' ? 'investigations' : 'allergies';
    const updatedList = (extraction[key] as any[]).map((item) =>
      item.id === id ? { ...item, ...fields } : item
    );
    setExtraction({ ...extraction, [key]: updatedList });
  };

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950">
      <Header
        engine={engine}
        onEngineChange={setEngine}
        onLoadSample={handleLoadSample}
        onOpenAudit={() => setAuditOpen(true)}
        onFileUpload={handleFileUpload}
        isProcessing={isProcessing}
      />

      {/* Main Split-Pane Workspace */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Pane: Clinical Document Viewer with Evidence Grounding */}
        <div className="w-1/2 h-full flex flex-col">
          <DocumentViewer
            document={currentDoc}
            selectedEvidence={selectedEvidence}
            isProcessing={isProcessing}
            onTriggerExtract={handleTriggerExtract}
          />
        </div>

        {/* Right Pane: HITL Review & Extracted Entities */}
        <div className="w-1/2 h-full flex flex-col border-l border-slate-800">
          <CategorySection
            medications={extraction?.medications || []}
            diagnoses={extraction?.diagnoses || []}
            investigations={extraction?.investigations || []}
            allergies={extraction?.allergies || []}
            selectedEvidence={selectedEvidence}
            onSelectEvidence={setSelectedEvidence}
            onAccept={handleAccept}
            onEdit={handleOpenEdit}
            onReject={handleReject}
          />
        </div>
      </main>

      {/* Edit Modal */}
      <EditEntityModal
        isOpen={editModal.isOpen}
        type={editModal.type}
        entity={editModal.entity}
        onClose={() => setEditModal({ isOpen: false, type: 'medication', entity: null })}
        onSave={handleSaveEdit}
      />

      {/* Audit Drawer */}
      <AuditDrawer
        isOpen={auditOpen}
        logs={auditLogs}
        onClose={() => setAuditOpen(false)}
      />
    </div>
  );
};
export default App;
