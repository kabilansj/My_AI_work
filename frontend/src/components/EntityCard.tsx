import React from 'react';
import { Check, X, Edit3, Eye, ShieldAlert, CheckCircle2, AlertCircle } from 'lucide-react';

interface EntityCardProps {
  type: 'medication' | 'diagnosis' | 'investigation' | 'allergy';
  entity: any;
  isSelected: boolean;
  onSelect: () => void;
  onAccept: () => void;
  onEdit: () => void;
  onReject: () => void;
}

export const EntityCard: React.FC<EntityCardProps> = ({
  type,
  entity,
  isSelected,
  onSelect,
  onAccept,
  onEdit,
  onReject,
}) => {
  // Color styling based on review status
  const statusBadge = () => {
    switch (entity.review_status) {
      case 'accepted':
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <CheckCircle2 className="w-2.5 h-2.5" /> Accepted
          </span>
        );
      case 'modified':
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30 flex items-center gap-1">
            <Edit3 className="w-2.5 h-2.5" /> Modified
          </span>
        );
      case 'rejected':
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 flex items-center gap-1">
            <AlertCircle className="w-2.5 h-2.5" /> Rejected
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
            Pending Review
          </span>
        );
    }
  };

  // Assertion Badge for Diagnoses
  const renderAssertionBadge = () => {
    if (type !== 'diagnosis' || !entity.assertion) return null;
    const colors: Record<string, string> = {
      confirmed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      ruled_out: 'bg-rose-500/10 text-rose-400 border-rose-500/20 line-through',
      suspected: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      historical: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      family_history: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    };
    const badgeClass = colors[entity.assertion] || 'bg-slate-800 text-slate-300';
    return (
      <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded border ${badgeClass}`}>
        {entity.assertion.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div
      onClick={onSelect}
      className={`rounded-lg border p-3.5 transition-all cursor-pointer ${
        isSelected
          ? 'bg-slate-800/90 border-amber-400 shadow-md shadow-amber-950/20'
          : 'bg-slate-800/40 border-slate-700/60 hover:bg-slate-800/80 hover:border-slate-600'
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="text-sm font-semibold text-slate-100">
              {entity.name || entity.condition_name || entity.test_name || entity.allergen}
            </h4>
            {renderAssertionBadge()}
            {statusBadge()}
          </div>

          {/* Category Attributes */}
          <div className="mt-1 text-xs text-slate-400 flex flex-wrap gap-x-3 gap-y-1">
            {/* Medication details */}
            {type === 'medication' && (
              <>
                {entity.dosage && <span><strong>Dose:</strong> {entity.dosage}</span>}
                {entity.frequency && <span><strong>Freq:</strong> {entity.frequency}</span>}
                {entity.route && <span><strong>Route:</strong> {entity.route}</span>}
                <span><strong>Status:</strong> {entity.status}</span>
              </>
            )}

            {/* Diagnosis details */}
            {type === 'diagnosis' && (
              <>
                {entity.acuity && <span><strong>Acuity:</strong> {entity.acuity}</span>}
                {entity.icd10_hint && <span><strong>ICD-10:</strong> {entity.icd10_hint}</span>}
              </>
            )}

            {/* Investigation details */}
            {type === 'investigation' && (
              <>
                <span><strong>Result:</strong> {entity.value || 'N/A'} {entity.unit || ''}</span>
                {entity.flag && entity.flag !== 'unknown' && (
                  <span className={`font-semibold uppercase ${
                    entity.flag === 'high' || entity.flag === 'abnormal' ? 'text-rose-400' : 'text-emerald-400'
                  }`}>
                    [{entity.flag}]
                  </span>
                )}
                <span><strong>Category:</strong> {entity.category}</span>
              </>
            )}

            {/* Allergy details */}
            {type === 'allergy' && (
              <>
                {entity.reaction && <span><strong>Reaction:</strong> {entity.reaction}</span>}
                {entity.severity && entity.severity !== 'unknown' && (
                  <span><strong>Severity:</strong> {entity.severity}</span>
                )}
                <span><strong>Status:</strong> {entity.status}</span>
              </>
            )}
          </div>

          {/* Evidence snippet */}
          {entity.evidence_span && (
            <div className="mt-2 text-[11px] text-slate-400 italic bg-slate-900/60 rounded px-2 py-1 border border-slate-800 flex items-center gap-1.5">
              <Eye className="w-3 h-3 text-amber-400 flex-shrink-0" />
              <span className="truncate">&ldquo;{entity.evidence_span}&rdquo;</span>
            </div>
          )}

          {/* Reviewer Note if any */}
          {entity.reviewer_notes && (
            <div className="mt-1.5 text-[11px] text-sky-300">
              <strong>Note:</strong> {entity.reviewer_notes} (by {entity.reviewed_by || 'Reviewer'})
            </div>
          )}
        </div>

        {/* 1-Click HITL Actions */}
        <div className="flex items-center space-x-1 pl-2 flex-shrink-0" onClick={(e) => e.stopPropagation()}>
          <button
            onClick={onAccept}
            title="Approve / Accept Entity"
            className="p-1 rounded bg-slate-700/50 hover:bg-emerald-600/80 text-slate-400 hover:text-white transition-colors"
          >
            <Check className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onEdit}
            title="Edit / Correct Entity"
            className="p-1 rounded bg-slate-700/50 hover:bg-sky-600/80 text-slate-400 hover:text-white transition-colors"
          >
            <Edit3 className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={onReject}
            title="Reject Entity"
            className="p-1 rounded bg-slate-700/50 hover:bg-rose-600/80 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
};
