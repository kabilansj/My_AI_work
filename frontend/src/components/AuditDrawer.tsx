import React from 'react';
import { X, History, UserCheck, Cpu, ArrowRight } from 'lucide-react';
import { AuditLog } from '../types/clinical';

interface AuditDrawerProps {
  isOpen: boolean;
  logs: AuditLog[];
  onClose: () => void;
}

export const AuditDrawer: React.FC<AuditDrawerProps> = ({ isOpen, logs, onClose }) => {
  if (!isOpen) return null;

  const actionBadge = (action: string) => {
    switch (action) {
      case 'ACCEPTED':
        return <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold px-2 py-0.5 rounded">ACCEPTED</span>;
      case 'MODIFIED':
        return <span className="bg-sky-500/10 text-sky-400 border border-sky-500/20 text-[10px] font-bold px-2 py-0.5 rounded">MODIFIED</span>;
      case 'REJECTED':
        return <span className="bg-rose-500/10 text-rose-400 border border-rose-500/20 text-[10px] font-bold px-2 py-0.5 rounded">REJECTED</span>;
      default:
        return <span className="bg-purple-500/10 text-purple-400 border border-purple-500/20 text-[10px] font-bold px-2 py-0.5 rounded">AUTO EXTRACTED</span>;
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-950/70 backdrop-blur-sm">
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-slate-900 border-l border-slate-800 shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <History className="w-4 h-4 text-sky-400" />
              <h2 className="text-sm font-bold text-slate-100">Audit & Governance Trail</h2>
            </div>
            <button onClick={onClose} className="text-slate-400 hover:text-white p-1">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Audit Event Stream */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {logs.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-xs">
                No audit events recorded for this session yet.
              </div>
            ) : (
              logs.map((log) => {
                const isAI = log.user_id === 'ai_extractor';
                return (
                  <div key={log.id} className="bg-slate-800/60 border border-slate-700/80 rounded-lg p-3 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-1.5 font-medium text-slate-300">
                        {isAI ? <Cpu className="w-3.5 h-3.5 text-purple-400" /> : <UserCheck className="w-3.5 h-3.5 text-emerald-400" />}
                        <span>{log.user_id}</span>
                      </div>
                      {actionBadge(log.action)}
                    </div>

                    <div className="text-[11px] text-slate-400 flex items-center justify-between">
                      <span className="capitalize font-semibold text-slate-300">{log.entity_type}</span>
                      <time className="text-slate-500">
                        {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </time>
                    </div>

                    {/* Diff view */}
                    {log.action === 'MODIFIED' && log.new_state && (
                      <div className="bg-slate-900/80 rounded p-2 text-[11px] font-mono border border-slate-800 text-slate-300">
                        <span className="text-sky-400">Updates:</span> {log.new_state}
                      </div>
                    )}

                    {log.reason && (
                      <div className="text-[11px] text-amber-300/90 italic">
                        &ldquo;{log.reason}&rdquo;
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
