import React, { useState } from 'react';
import { X, Save } from 'lucide-react';

interface EditEntityModalProps {
  isOpen: boolean;
  type: 'medication' | 'diagnosis' | 'investigation' | 'allergy';
  entity: any;
  onClose: () => void;
  onSave: (updates: Record<string, any>, notes: string) => void;
}

export const EditEntityModal: React.FC<EditEntityModalProps> = ({
  isOpen,
  type,
  entity,
  onClose,
  onSave,
}) => {
  if (!isOpen || !entity) return null;

  const [formData, setFormData] = useState<Record<string, any>>(() => {
    if (type === 'medication') {
      return {
        name: entity.name || '',
        dosage: entity.dosage || '',
        frequency: entity.frequency || '',
        route: entity.route || '',
        status: entity.status || 'active',
      };
    } else if (type === 'diagnosis') {
      return {
        condition_name: entity.condition_name || '',
        assertion: entity.assertion || 'confirmed',
        acuity: entity.acuity || '',
        icd10_hint: entity.icd10_hint || '',
      };
    } else if (type === 'investigation') {
      return {
        test_name: entity.test_name || '',
        value: entity.value || '',
        unit: entity.unit || '',
        flag: entity.flag || 'unknown',
      };
    } else {
      return {
        allergen: entity.allergen || '',
        reaction: entity.reaction || '',
        severity: entity.severity || 'unknown',
        status: entity.status || 'active',
      };
    }
  });

  const [notes, setNotes] = useState('');

  const handleChange = (field: string, val: string) => {
    setFormData((prev) => ({ ...prev, [field]: val }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData, notes);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full shadow-2xl overflow-hidden">
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-800">
          <h3 className="text-sm font-semibold text-slate-100 capitalize">
            Edit & Correct {type}
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-5 space-y-3.5 text-xs">
          {type === 'medication' && (
            <>
              <div>
                <label className="block text-slate-400 mb-1">Medication Name</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleChange('name', e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Dosage</label>
                  <input
                    type="text"
                    value={formData.dosage}
                    onChange={(e) => handleChange('dosage', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Frequency</label>
                  <input
                    type="text"
                    value={formData.frequency}
                    onChange={(e) => handleChange('frequency', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Route</label>
                  <input
                    type="text"
                    value={formData.route}
                    onChange={(e) => handleChange('route', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Status</label>
                  <select
                    value={formData.status}
                    onChange={(e) => handleChange('status', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  >
                    <option value="active">Active</option>
                    <option value="discontinued">Discontinued</option>
                    <option value="prn">PRN (As Needed)</option>
                    <option value="historical">Historical</option>
                  </select>
                </div>
              </div>
            </>
          )}

          {type === 'diagnosis' && (
            <>
              <div>
                <label className="block text-slate-400 mb-1">Condition Name</label>
                <input
                  type="text"
                  value={formData.condition_name}
                  onChange={(e) => handleChange('condition_name', e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Assertion</label>
                  <select
                    value={formData.assertion}
                    onChange={(e) => handleChange('assertion', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  >
                    <option value="confirmed">Confirmed</option>
                    <option value="ruled_out">Ruled Out (Negated)</option>
                    <option value="suspected">Suspected</option>
                    <option value="historical">Historical</option>
                    <option value="family_history">Family History</option>
                  </select>
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Acuity</label>
                  <input
                    type="text"
                    value={formData.acuity}
                    onChange={(e) => handleChange('acuity', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  />
                </div>
              </div>
            </>
          )}

          {type === 'investigation' && (
            <>
              <div>
                <label className="block text-slate-400 mb-1">Test Name</label>
                <input
                  type="text"
                  value={formData.test_name}
                  onChange={(e) => handleChange('test_name', e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Value / Result</label>
                  <input
                    type="text"
                    value={formData.value}
                    onChange={(e) => handleChange('value', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Flag</label>
                  <select
                    value={formData.flag}
                    onChange={(e) => handleChange('flag', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  >
                    <option value="unknown">Unknown</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="low">Low</option>
                    <option value="abnormal">Abnormal</option>
                  </select>
                </div>
              </div>
            </>
          )}

          {type === 'allergy' && (
            <>
              <div>
                <label className="block text-slate-400 mb-1">Allergen</label>
                <input
                  type="text"
                  value={formData.allergen}
                  onChange={(e) => handleChange('allergen', e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  required
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-slate-400 mb-1">Reaction</label>
                  <input
                    type="text"
                    value={formData.reaction}
                    onChange={(e) => handleChange('reaction', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Severity</label>
                  <select
                    value={formData.severity}
                    onChange={(e) => handleChange('severity', e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
                  >
                    <option value="unknown">Unknown</option>
                    <option value="mild">Mild</option>
                    <option value="moderate">Moderate</option>
                    <option value="severe">Severe</option>
                    <option value="life_threatening">Life-Threatening</option>
                  </select>
                </div>
              </div>
            </>
          )}

          <div>
            <label className="block text-slate-400 mb-1">Clinician Justification / Notes</label>
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g., corrected dosage based on pharmacy discharge summary"
              className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-slate-100 focus:outline-none focus:border-sky-500"
            />
          </div>

          <div className="pt-2 flex justify-end space-x-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-3 py-1.5 bg-sky-600 hover:bg-sky-500 text-white rounded font-medium flex items-center gap-1.5 transition-colors"
            >
              <Save className="w-3.5 h-3.5" /> Save & Approve
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
