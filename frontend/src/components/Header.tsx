import React from 'react';
import { Activity, ShieldCheck, History, Upload, FileText, Cpu } from 'lucide-react';

interface HeaderProps {
  engine: string;
  onEngineChange: (engine: string) => void;
  onLoadSample: (sample: 'discharge' | 'diabetes') => void;
  onOpenAudit: () => void;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  isProcessing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  engine,
  onEngineChange,
  onLoadSample,
  onOpenAudit,
  onFileUpload,
  isProcessing,
}) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-sky-500/10 border border-sky-500/20 rounded-lg text-sky-400">
          <Activity className="w-6 h-6 animate-pulse" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            Clinical Intelligence Platform
            <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <ShieldCheck className="w-3 h-3" /> HITL Verified
            </span>
          </h1>
          <p className="text-xs text-slate-400">Evidence Grounding & Clinician Audit Trail</p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Engine Selector */}
        <div className="flex items-center space-x-2 bg-slate-800/80 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs">
          <Cpu className="w-4 h-4 text-sky-400" />
          <span className="text-slate-400">Engine:</span>
          <select
            value={engine}
            onChange={(e) => onEngineChange(e.target.value)}
            disabled={isProcessing}
            aria-label="Extraction Engine Selection"
            className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer"
          >
            <option value="auto" className="bg-slate-800 text-slate-200">Auto (Gemini / Local)</option>
            <option value="local" className="bg-slate-800 text-slate-200">Local Rules (Offline)</option>
            <option value="llm" className="bg-slate-800 text-slate-200">Gemini LLM</option>
          </select>
        </div>

        {/* Load Samples */}
        <div className="flex items-center bg-slate-800 border border-slate-700 rounded-lg overflow-hidden text-xs">
          <button
            onClick={() => onLoadSample('discharge')}
            disabled={isProcessing}
            className="px-3 py-1.5 text-slate-300 hover:text-white hover:bg-slate-700/80 transition-colors flex items-center gap-1.5 border-r border-slate-700"
          >
            <FileText className="w-3.5 h-3.5 text-sky-400" /> Sample: Heart Failure
          </button>
          <button
            onClick={() => onLoadSample('diabetes')}
            disabled={isProcessing}
            className="px-3 py-1.5 text-slate-300 hover:text-white hover:bg-slate-700/80 transition-colors flex items-center gap-1.5"
          >
            <FileText className="w-3.5 h-3.5 text-emerald-400" /> Sample: Diabetes
          </button>
        </div>

        {/* Upload File */}
        <label className="cursor-pointer px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded-lg text-xs font-medium flex items-center gap-1.5 transition-colors shadow-sm shadow-sky-900/30">
          <Upload className="w-3.5 h-3.5" />
          <span>Upload PDF / TXT</span>
          <input
            type="file"
            accept=".pdf,.txt"
            onChange={onFileUpload}
            disabled={isProcessing}
            className="hidden"
          />
        </label>

        {/* Audit Log Drawer Toggle */}
        <button
          onClick={onOpenAudit}
          className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 rounded-lg transition-colors"
          title="View Audit Trail"
        >
          <History className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
};
