import React, { useMemo } from 'react';
import { FileText, Search, Sparkles } from 'lucide-react';
import { ClinicalDocument } from '../types/clinical';

interface DocumentViewerProps {
  document: ClinicalDocument | null;
  selectedEvidence: string | null;
  isProcessing: boolean;
  onTriggerExtract: () => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  document,
  selectedEvidence,
  isProcessing,
  onTriggerExtract,
}) => {
  const [searchTerm, setSearchTerm] = React.useState('');

  // Highlight selected evidence and optional search terms
  const highlightedContent = useMemo(() => {
    if (!document?.raw_text) return null;
    const text = document.raw_text;

    const highlightTarget = selectedEvidence?.trim();
    if (!highlightTarget && !searchTerm.trim()) {
      return <span>{text}</span>;
    }

    const target = highlightTarget || searchTerm.trim();
    const regex = new RegExp(`(${escapeRegExp(target)})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, index) => {
      const isMatch = part.toLowerCase() === target.toLowerCase();
      if (!isMatch) return <span key={index}>{part}</span>;

      return (
        <mark
          key={index}
          className={`${
            highlightTarget
              ? 'bg-amber-400/30 text-amber-200 border-b-2 border-amber-400 font-medium px-1 rounded'
              : 'bg-sky-500/30 text-sky-200 px-1 rounded'
          }`}
        >
          {part}
        </mark>
      );
    });
  }, [document?.raw_text, selectedEvidence, searchTerm]);

  return (
    <div className="flex-1 flex flex-col bg-slate-900 border-r border-slate-800 h-full overflow-hidden">
      {/* Document Toolbar */}
      <div className="bg-slate-900/90 border-b border-slate-800 px-4 py-2.5 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2 text-slate-300">
          <FileText className="w-4 h-4 text-sky-400" />
          <span className="font-semibold text-slate-100 truncate max-w-xs">
            {document ? document.filename : 'No document selected'}
          </span>
          {document && (
            <span className="text-slate-500 text-[11px]">
              ({document.raw_text.split(/\s+/).filter(Boolean).length} words)
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {/* Quick Filter */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2 top-2" />
            <input
              type="text"
              placeholder="Find in note..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-md pl-7 pr-2 py-1 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500 w-36"
            />
          </div>

          {document && (
            <button
              onClick={onTriggerExtract}
              disabled={isProcessing}
              className="px-2.5 py-1 bg-sky-600/90 hover:bg-sky-500 text-white rounded text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isProcessing ? 'Extracting...' : 'Extract Entities'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Evidence Notification Banner */}
      {selectedEvidence && (
        <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-1.5 text-xs text-amber-300 flex items-center justify-between">
          <span className="truncate">
            <strong className="text-amber-200">Evidence Grounding:</strong> &ldquo;{selectedEvidence}&rdquo;
          </span>
        </div>
      )}

      {/* Clinical Text Viewer */}
      <div className="flex-1 p-6 overflow-y-auto font-mono text-sm leading-relaxed text-slate-300 whitespace-pre-wrap select-text">
        {document ? (
          highlightedContent
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <FileText className="w-12 h-12 mb-3 stroke-1 text-slate-600" />
            <p className="text-sm">Select a sample or upload a clinical note to begin review.</p>
          </div>
        )}
      </div>
    </div>
  );
};

function escapeRegExp(string: string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
