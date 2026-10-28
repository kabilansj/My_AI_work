import React, { useState } from 'react';
import { Pill, Stethoscope, FlaskConical, ShieldAlert, Filter } from 'lucide-react';
import { EntityCard } from './EntityCard';
import { Medication, Diagnosis, Investigation, Allergy } from '../types/clinical';

interface CategorySectionProps {
  medications: Medication[];
  diagnoses: Diagnosis[];
  investigations: Investigation[];
  allergies: Allergy[];
  selectedEvidence: string | null;
  onSelectEvidence: (evidence: string | null) => void;
  onAccept: (type: 'medication' | 'diagnosis' | 'investigation' | 'allergy', id: string) => void;
  onEdit: (type: 'medication' | 'diagnosis' | 'investigation' | 'allergy', entity: any) => void;
  onReject: (type: 'medication' | 'diagnosis' | 'investigation' | 'allergy', id: string) => void;
}

type TabType = 'medications' | 'diagnoses' | 'investigations' | 'allergies';

export const CategorySection: React.FC<CategorySectionProps> = ({
  medications,
  diagnoses,
  investigations,
  allergies,
  selectedEvidence,
  onSelectEvidence,
  onAccept,
  onEdit,
  onReject,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('medications');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'accepted' | 'rejected'>('all');

  const tabs = [
    { key: 'medications', label: 'Medications', icon: Pill, count: medications.length, color: 'text-sky-400' },
    { key: 'diagnoses', label: 'Diagnoses', icon: Stethoscope, count: diagnoses.length, color: 'text-indigo-400' },
    { key: 'investigations', label: 'Investigations', icon: FlaskConical, count: investigations.length, color: 'text-amber-400' },
    { key: 'allergies', label: 'Allergies', icon: ShieldAlert, count: allergies.length, color: 'text-rose-400' },
  ];

  const getFilteredItems = () => {
    let items: any[] = [];
    let type: 'medication' | 'diagnosis' | 'investigation' | 'allergy' = 'medication';

    if (activeTab === 'medications') {
      items = medications;
      type = 'medication';
    } else if (activeTab === 'diagnoses') {
      items = diagnoses;
      type = 'diagnosis';
    } else if (activeTab === 'investigations') {
      items = investigations;
      type = 'investigation';
    } else {
      items = allergies;
      type = 'allergy';
    }

    if (statusFilter !== 'all') {
      items = items.filter((item) => item.review_status === statusFilter);
    }

    return { items, type };
  };

  const { items, type } = getFilteredItems();

  return (
    <div className="flex-1 flex flex-col bg-slate-900 h-full overflow-hidden">
      {/* Category Navigation Bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-4 pt-2 flex items-center justify-between">
        <div className="flex space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.key;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as TabType)}
                className={`px-3 py-2 text-xs font-semibold rounded-t-lg flex items-center gap-2 border-b-2 transition-all ${
                  isActive
                    ? 'border-sky-500 text-sky-400 bg-slate-800/60'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${tab.color}`} />
                <span>{tab.label}</span>
                <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800 text-slate-300">
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Status Filter */}
        <div className="flex items-center space-x-1 mb-2">
          <Filter className="w-3 h-3 text-slate-500 mr-1" />
          {(['all', 'pending', 'accepted', 'rejected'] as const).map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-2 py-0.5 text-[11px] rounded capitalize font-medium ${
                statusFilter === s
                  ? 'bg-slate-700 text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Entity List */}
      <div className="flex-1 p-4 overflow-y-auto space-y-2.5">
        {items.length === 0 ? (
          <div className="h-64 flex flex-col items-center justify-center text-slate-500 text-xs">
            <p>No entities found matching the current filter.</p>
          </div>
        ) : (
          items.map((entity) => (
            <EntityCard
              key={entity.id}
              type={type}
              entity={entity}
              isSelected={selectedEvidence === entity.evidence_span}
              onSelect={() => onSelectEvidence(entity.evidence_span || null)}
              onAccept={() => onAccept(type, entity.id)}
              onEdit={() => onEdit(type, entity)}
              onReject={() => onReject(type, entity.id)}
            />
          ))
        )}
      </div>
    </div>
  );
};
