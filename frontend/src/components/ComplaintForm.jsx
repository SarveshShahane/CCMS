import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  FileText,
  User,
  Package,
  AlertTriangle,
  Calendar,
  CheckCircle2,
  Save,
  Trash2,
  Sparkles,
  Bot,
  ShieldAlert,
} from 'lucide-react';
import {
  updateFormField,
  saveComplaintThunk,
  clearForm,
  resetSaveStatus,
} from '../store/slices/complaintSlice';
import { setActiveView } from '../store/slices/appSlice';

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const { form, autoFilledFields, isSaving, saveSuccess, saveError, lastSavedNumber } = useSelector(
    (state) => state.complaint
  );

  const handleChange = (field, value) => {
    dispatch(updateFormField({ field, value }));
  };

  const handleSave = (e) => {
    e.preventDefault();
    dispatch(saveComplaintThunk());
  };

  const handleClear = () => {
    if (window.confirm('Are you sure you want to clear all form entries?')) {
      dispatch(clearForm());
    }
  };

  const isAutoFilled = (fieldName) => autoFilledFields.includes(fieldName);

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs flex flex-col h-full overflow-hidden">
      {/* Form Header */}
      <div className="px-6 py-4 bg-slate-50/80 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-teal-100/70 text-teal-700 rounded-lg">
            <FileText className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800">Complaint Intake Form</h2>
            <p className="text-xs text-slate-500">Editable form • Auto-populated by AI Copilot</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {autoFilledFields.length > 0 && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-teal-100 text-teal-800 animate-pulse">
              <Sparkles className="h-3 w-3" />
              {autoFilledFields.length} AI Extracted
            </span>
          )}
          <button
            type="button"
            onClick={handleClear}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/60 transition-colors cursor-pointer"
            title="Clear form fields"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Success Notification Alert */}
      {saveSuccess && (
        <div className="mx-6 mt-4 p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl flex items-start justify-between text-emerald-800 text-xs shadow-xs">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
            <div>
              <p className="font-bold text-emerald-900">Complaint Successfully Saved & Logged!</p>
              <p className="text-emerald-700 font-mono text-[11px] mt-0.5">
                Reference ID: <span className="font-bold">{lastSavedNumber}</span> • Form reset for new entry.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                dispatch(resetSaveStatus());
                dispatch(setActiveView('list'));
              }}
              className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-emerald-600 text-white hover:bg-emerald-700 transition-colors cursor-pointer shadow-xs"
            >
              View All Complaints
            </button>
            <button
              onClick={() => dispatch(resetSaveStatus())}
              className="text-emerald-600 hover:text-emerald-900 font-bold ml-2 cursor-pointer"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Error Notification Alert */}
      {saveError && (
        <div className="mx-6 mt-4 p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-2.5 text-rose-800 text-xs">
          <AlertTriangle className="h-5 w-5 text-rose-600 shrink-0" />
          <div>
            <p className="font-bold text-rose-900">Failed to Save Complaint</p>
            <p className="text-rose-700">{saveError}</p>
          </div>
        </div>
      )}

      {/* Form Content Scrollable Body */}
      <form id="complaintForm" onSubmit={handleSave} className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Section 1: Customer & Source Info */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
            <User className="h-4 w-4 text-teal-600" />
            <span>Customer & Source Details</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Customer / Entity Name</label>
              <input
                type="text"
                placeholder="e.g. Apollo Pharmacy / City Hospital"
                value={form.customer_name}
                onChange={(e) => handleChange('customer_name', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 transition-all ${
                  isAutoFilled('customer_name') ? 'ai-highlight' : ''
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Complaint Source</label>
              <select
                value={form.complaint_source}
                onChange={(e) => handleChange('complaint_source', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 transition-all ${
                  isAutoFilled('complaint_source') ? 'ai-highlight' : ''
                }`}
              >
                <option value="Pharmacy">Pharmacy</option>
                <option value="Hospital">Hospital</option>
                <option value="Patient">Patient / Consumer</option>
                <option value="Distributor">Wholesaler / Distributor</option>
                <option value="Regulatory">Regulatory Body</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Contact Email</label>
              <input
                type="email"
                placeholder="customer@domain.com"
                value={form.customer_contact_email}
                onChange={(e) => handleChange('customer_contact_email', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                  isAutoFilled('customer_contact_email') ? 'ai-highlight' : ''
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Contact Phone</label>
              <input
                type="text"
                placeholder="+1 (555) 000-0000"
                value={form.customer_contact_phone}
                onChange={(e) => handleChange('customer_contact_phone', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                  isAutoFilled('customer_contact_phone') ? 'ai-highlight' : ''
                }`}
              />
            </div>
          </div>
        </div>

        <hr className="border-slate-100" />

        {/* Section 2: Product Specifications */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
            <Package className="h-4 w-4 text-teal-600" />
            <span>Product Specifications</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">Product Name</label>
              <input
                type="text"
                placeholder="e.g. Amoxicillin Capsules 500 mg"
                value={form.product_name}
                onChange={(e) => handleChange('product_name', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 font-medium ${
                  isAutoFilled('product_name') ? 'ai-highlight' : ''
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Dosage Form</label>
              <select
                value={form.dosage_form}
                onChange={(e) => handleChange('dosage_form', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                  isAutoFilled('dosage_form') ? 'ai-highlight' : ''
                }`}
              >
                <option value="Capsules">Capsules</option>
                <option value="Tablets">Tablets</option>
                <option value="Ointment">Ointment / Cream</option>
                <option value="Injection">Injection / Injectable</option>
                <option value="Oral Liquid">Oral Liquid / Syrup</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Product Strength</label>
              <input
                type="text"
                placeholder="e.g. 500 mg / 10 mg/ml"
                value={form.product_strength}
                onChange={(e) => handleChange('product_strength', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                  isAutoFilled('product_strength') ? 'ai-highlight' : ''
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Batch / Lot Number</label>
              <input
                type="text"
                placeholder="e.g. AMX240602"
                value={form.batch_number}
                onChange={(e) => handleChange('batch_number', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                  isAutoFilled('batch_number') ? 'ai-highlight' : ''
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Product Code / SKU</label>
              <input
                type="text"
                placeholder="e.g. SKU-88392"
                value={form.product_code}
                onChange={(e) => handleChange('product_code', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                  isAutoFilled('product_code') ? 'ai-highlight' : ''
                }`}
              />
            </div>
          </div>
        </div>

        <hr className="border-slate-100" />

        {/* Section 3: Defect & Quantity Details */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
            <AlertTriangle className="h-4 w-4 text-amber-600" />
            <span>Defect & Quantity Information</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-700 mb-1">Complaint Title</label>
              <input
                type="text"
                placeholder="Short summary title of issue"
                value={form.title}
                onChange={(e) => handleChange('title', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                  isAutoFilled('title') ? 'ai-highlight' : ''
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Complaint Category</label>
              <select
                value={form.complaint_category}
                onChange={(e) => handleChange('complaint_category', e.target.value)}
                className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                  isAutoFilled('complaint_category') ? 'ai-highlight' : ''
                }`}
              >
                <option value="Packaging / Labeling">Packaging / Labeling</option>
                <option value="Discoloration / Appearance">Discoloration / Appearance</option>
                <option value="Contamination / Foreign Matter">Contamination / Foreign Matter</option>
                <option value="Sub-potency / Lack of Efficacy">Sub-potency / Lack of Efficacy</option>
                <option value="Adverse Reaction">Adverse Event / Safety</option>
                <option value="Broken Seal / Leakage">Broken Seal / Leakage</option>
                <option value="Other">Other Defect</option>
              </select>
            </div>

            <div className="flex gap-2">
              <div className="w-1/2">
                <label className="block text-xs font-semibold text-slate-700 mb-1">Affected Qty</label>
                <input
                  type="number"
                  min="1"
                  value={form.affected_quantity}
                  onChange={(e) => handleChange('affected_quantity', e.target.value)}
                  className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                    isAutoFilled('affected_quantity') ? 'ai-highlight' : ''
                  }`}
                />
              </div>

              <div className="w-1/2">
                <label className="block text-xs font-semibold text-slate-700 mb-1">Unit</label>
                <select
                  value={form.affected_quantity_unit}
                  onChange={(e) => handleChange('affected_quantity_unit', e.target.value)}
                  className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                    isAutoFilled('affected_quantity_unit') ? 'ai-highlight' : ''
                  }`}
                >
                  <option value="units">Units</option>
                  <option value="boxes">Boxes</option>
                  <option value="packs">Packs</option>
                  <option value="bottles">Bottles</option>
                  <option value="vials">Vials</option>
                  <option value="cartons">Cartons</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <hr className="border-slate-100" />

        {/* Section 4: Relevant Dates */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
            <Calendar className="h-4 w-4 text-teal-600" />
            <span>Dates & Batches</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Incident Date</label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="e.g. 2026-08-15, Aug 2026, 2026"
                  value={form.incident_date || ''}
                  onChange={(e) => handleChange('incident_date', e.target.value)}
                  className={`w-full pl-3 pr-8 py-2 rounded-lg border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                    isAutoFilled('incident_date') ? 'ai-highlight' : ''
                  }`}
                />
                <Calendar className="h-3.5 w-3.5 text-slate-400 absolute right-2.5 top-2.5 pointer-events-none" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Manufacturing Date</label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="e.g. March 2026, 03/2026, 2026"
                  value={form.manufacturing_date || ''}
                  onChange={(e) => handleChange('manufacturing_date', e.target.value)}
                  className={`w-full pl-3 pr-8 py-2 rounded-lg border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                    isAutoFilled('manufacturing_date') ? 'ai-highlight' : ''
                  }`}
                />
                <Calendar className="h-3.5 w-3.5 text-slate-400 absolute right-2.5 top-2.5 pointer-events-none" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Expiry Date</label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="e.g. Feb 2028, 02/2028, 2028"
                  value={form.expiry_date || ''}
                  onChange={(e) => handleChange('expiry_date', e.target.value)}
                  className={`w-full pl-3 pr-8 py-2 rounded-lg border border-slate-300 text-xs focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 ${
                    isAutoFilled('expiry_date') ? 'ai-highlight' : ''
                  }`}
                />
                <Calendar className="h-3.5 w-3.5 text-slate-400 absolute right-2.5 top-2.5 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>

        <hr className="border-slate-100" />

        {/* Section 5: AI Risk Assessment & Next Actions */}
        <div className="p-4 bg-teal-50/50 rounded-xl border border-teal-200/80 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-teal-800">
              <Bot className="h-4 w-4 text-teal-600" />
              <span>AI Risk Assessment & Guidance</span>
            </div>

            <div>
              <select
                value={form.initial_severity}
                onChange={(e) => handleChange('initial_severity', e.target.value)}
                className="px-2.5 py-1 rounded-md bg-white border border-teal-300 text-xs font-bold text-teal-900 focus:outline-none"
              >
                <option value="Critical">🔴 Severity: Critical</option>
                <option value="Major">🟠 Severity: Major</option>
                <option value="Minor">🟢 Severity: Minor</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-teal-900 mb-1">AI Risk Summary</label>
            <textarea
              rows={3}
              placeholder="AI generated risk assessment..."
              value={form.ai_risk_assessment}
              onChange={(e) => handleChange('ai_risk_assessment', e.target.value)}
              className={`w-full px-3 py-2 rounded-lg border border-teal-200 bg-white text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-teal-500 resize-y min-h-[90px] leading-relaxed ${
                isAutoFilled('ai_risk_assessment') ? 'ai-highlight' : ''
              }`}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-teal-900 mb-1">Suggested Next Action</label>
            <textarea
              rows={2}
              placeholder="Recommended QA/QC next action..."
              value={form.ai_suggested_next_action}
              onChange={(e) => handleChange('ai_suggested_next_action', e.target.value)}
              className={`w-full px-3 py-2 rounded-lg border border-teal-200 bg-white text-xs text-slate-700 focus:outline-none focus:ring-2 focus:ring-teal-500 resize-y min-h-[70px] leading-relaxed ${
                isAutoFilled('ai_suggested_next_action') ? 'ai-highlight' : ''
              }`}
            />
          </div>
        </div>

        {/* Section 6: Detailed Description */}
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Detailed Description</label>
          <textarea
            rows={5}
            placeholder="Full narrative description of the reported issue..."
            value={form.description}
            onChange={(e) => handleChange('description', e.target.value)}
            className={`w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500/50 focus:border-teal-500 resize-y min-h-[120px] leading-relaxed ${
              isAutoFilled('description') ? 'ai-highlight' : ''
            }`}
          />
        </div>
      </form>

      {/* Form Footer Action Bar with Save Complaint Button */}
      <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
        <div className="text-xs text-slate-500">
          Click <span className="font-semibold text-slate-700">Save Complaint</span> to log record and reset form.
        </div>

        <button
          type="submit"
          form="complaintForm"
          disabled={isSaving}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-teal-600 to-teal-700 hover:from-teal-700 hover:to-teal-800 active:scale-[0.98] shadow-md shadow-teal-600/20 disabled:opacity-50 transition-all cursor-pointer"
        >
          {isSaving ? (
            <>
              <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Saving...</span>
            </>
          ) : (
            <>
              <Save className="h-4 w-4" />
              <span>Save Complaint</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
