import React, { useState } from 'react';
import { useSelector } from 'react-redux';
import {
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  Mail,
  Copy,
  Check,
  X,
  Sparkles,
  Info,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { complaintApi } from '../api/api';

export default function ComplaintCompletenessCard() {
  const { form } = useSelector((state) => state.complaint);
  const [isExpanded, setIsExpanded] = useState(false);
  const [emailModalOpen, setEmailModalOpen] = useState(false);
  const [isGeneratingEmail, setIsGeneratingEmail] = useState(false);
  const [emailDraft, setEmailDraft] = useState('');
  const [copied, setCopied] = useState(false);

  // Frontend Live Rules Evaluation
  const evaluateLocalCompleteness = () => {
    let score = 0;
    const missingCritical = [];
    const missingImportant = [];
    const missingOptional = [];

    // Critical (50 pts, 10 each)
    if (form.product_name?.trim()) score += 10;
    else missingCritical.push({ field: 'product_name', label: 'Product Name' });

    if (form.batch_number?.trim()) score += 10;
    else missingCritical.push({ field: 'batch_number', label: 'Batch / Lot #' });

    if (form.description?.trim()) score += 10;
    else missingCritical.push({ field: 'description', label: 'Complaint Description' });

    if (form.complaint_category?.trim()) score += 10;
    else missingCritical.push({ field: 'complaint_category', label: 'Complaint Category' });

    if (parseFloat(form.affected_quantity) > 0) score += 10;
    else missingCritical.push({ field: 'affected_quantity', label: 'Affected Quantity' });

    // Important (35 pts, 7 each)
    if (form.customer_name?.trim()) score += 7;
    else missingImportant.push({ field: 'customer_name', label: 'Customer Name' });

    if (form.customer_contact_email?.trim() || form.customer_contact_phone?.trim()) score += 7;
    else missingImportant.push({ field: 'customer_contact_email', label: 'Customer Contact (Email/Phone)' });

    if (form.dosage_form?.trim()) score += 7;
    else missingImportant.push({ field: 'dosage_form', label: 'Dosage Form' });

    if (form.product_strength?.trim()) score += 7;
    else missingImportant.push({ field: 'product_strength', label: 'Product Strength' });

    if (form.incident_date?.trim()) score += 7;
    else missingImportant.push({ field: 'incident_date', label: 'Incident Date' });

    // Optional (15 pts, 3 each)
    if (form.manufacturing_date?.trim()) score += 3;
    else missingOptional.push({ field: 'manufacturing_date', label: 'Mfg Date' });

    if (form.expiry_date?.trim()) score += 3;
    else missingOptional.push({ field: 'expiry_date', label: 'Expiry Date' });

    if (form.product_code?.trim()) score += 3;
    else missingOptional.push({ field: 'product_code', label: 'Product SKU Code' });

    if (form.complaint_source?.trim()) score += 3;
    else missingOptional.push({ field: 'complaint_source', label: 'Complaint Source' });

    if (form.sample_received) score += 3;
    else missingOptional.push({ field: 'sample_received', label: 'Physical Sample' });

    score = Math.min(100, Math.round(score));
    const isReady = score >= 80 && missingCritical.length === 0;

    let statusLabel = 'Incomplete';
    let statusBg = 'bg-rose-50 border-rose-200 text-rose-700';
    let progressBg = 'bg-rose-500';

    if (isReady) {
      statusLabel = 'Ready for Investigation';
      statusBg = 'bg-emerald-50 border-emerald-200 text-emerald-800';
      progressBg = 'bg-emerald-500';
    } else if (score >= 50) {
      statusLabel = 'Partially Complete';
      statusBg = 'bg-amber-50 border-amber-200 text-amber-800';
      progressBg = 'bg-amber-500';
    }

    return {
      score,
      isReady,
      statusLabel,
      statusBg,
      progressBg,
      missingCritical,
      missingImportant,
      missingOptional,
      totalMissing: missingCritical.length + missingImportant.length + missingOptional.length,
    };
  };

  const comp = evaluateLocalCompleteness();

  const handleGenerateEmail = async () => {
    setIsGeneratingEmail(true);
    setEmailModalOpen(true);
    try {
      const payload = { ...form };
      const res = await complaintApi.checkCompleteness(payload, true);
      setEmailDraft(res.suggested_followup_email || 'No email draft generated.');
    } catch (err) {
      setEmailDraft(
        `Dear ${form.customer_name || 'Customer'},\n\n` +
          `Thank you for submitting your complaint regarding ${form.product_name || 'our product'}.\n` +
          `To assist our QA team with the investigation, please provide:\n` +
          comp.missingCritical.map((m) => `- ${m.label}`).join('\n') +
          `\n\nBest regards,\nQuality Assurance Team`
      );
    } finally {
      setIsGeneratingEmail(false);
    }
  };

  const handleCopyEmail = () => {
    navigator.clipboard.writeText(emailDraft);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const scrollToField = (fieldName) => {
    const el = document.getElementsByName(fieldName)[0] || document.getElementById(fieldName);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.focus();
    }
  };

  return (
    <div className={`mx-6 mt-4 rounded-xl border transition-all duration-200 ${comp.statusBg}`}>
      {/* Header bar */}
      <div className="p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-white/80 shadow-xs border border-slate-200/50">
            {comp.isReady ? (
              <ShieldCheck className="h-5 w-5 text-emerald-600" />
            ) : comp.score >= 50 ? (
              <AlertTriangle className="h-5 w-5 text-amber-600" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-rose-600" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm text-slate-800">Complaint Completeness Checker</span>
              <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${comp.statusBg}`}>
                {comp.statusLabel}
              </span>
            </div>
            <p className="text-xs text-slate-600 mt-0.5">
              {comp.isReady
                ? 'All critical quality fields populated. Complaint is GMP-ready for QA investigation.'
                : `${comp.totalMissing} field(s) missing to reach investigation readiness.`}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Score Circle / Counter */}
          <div className="text-right">
            <span className="text-lg font-extrabold text-slate-900">{comp.score}%</span>
            <span className="text-[10px] text-slate-500 block uppercase font-semibold">Completeness</span>
          </div>

          {/* Followup Email Trigger */}
          {comp.totalMissing > 0 && (
            <button
              type="button"
              onClick={handleGenerateEmail}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 shadow-2xs transition-colors cursor-pointer"
              title="Generate clarification email for missing details"
            >
              <Mail className="h-3.5 w-3.5 text-teal-600" />
              <span>Request Info</span>
            </button>
          )}

          {/* Expand Toggle */}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 text-slate-500 hover:text-slate-700 rounded-md hover:bg-black/5 transition-colors cursor-pointer"
          >
            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-200/80 h-1.5 overflow-hidden">
        <div
          className={`h-full transition-all duration-500 ease-out ${comp.progressBg}`}
          style={{ width: `${comp.score}%` }}
        />
      </div>

      {/* Expanded Details Panel */}
      {isExpanded && (
        <div className="p-4 bg-white/70 border-t border-slate-200/60 rounded-b-xl space-y-3">
          {/* Missing Critical Fields */}
          {comp.missingCritical.length > 0 && (
            <div>
              <span className="text-[11px] font-bold text-rose-800 uppercase tracking-wide flex items-center gap-1 mb-1.5">
                <AlertTriangle className="h-3 w-3 text-rose-600" /> Missing Mandatory Critical Fields (Must fill):
              </span>
              <div className="flex flex-wrap gap-1.5">
                {comp.missingCritical.map((item) => (
                  <button
                    key={item.field}
                    type="button"
                    onClick={() => scrollToField(item.field)}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-rose-100/90 text-rose-800 border border-rose-300 hover:bg-rose-200 transition-colors cursor-pointer"
                  >
                    + Add {item.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Missing Important Fields */}
          {comp.missingImportant.length > 0 && (
            <div>
              <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wide flex items-center gap-1 mb-1.5">
                <Info className="h-3 w-3 text-amber-600" /> Missing Important Regulatory Details:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {comp.missingImportant.map((item) => (
                  <button
                    key={item.field}
                    type="button"
                    onClick={() => scrollToField(item.field)}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium bg-amber-100/90 text-amber-900 border border-amber-300 hover:bg-amber-200 transition-colors cursor-pointer"
                  >
                    + Add {item.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Missing Optional Fields */}
          {comp.missingOptional.length > 0 && (
            <div>
              <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide block mb-1">
                Supplementary / Optional Details:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {comp.missingOptional.map((item) => (
                  <button
                    key={item.field}
                    type="button"
                    onClick={() => scrollToField(item.field)}
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs text-slate-600 bg-slate-100 border border-slate-200 hover:bg-slate-200 transition-colors cursor-pointer"
                  >
                    + {item.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          {comp.totalMissing === 0 && (
            <div className="flex items-center gap-2 text-xs font-semibold text-emerald-700 bg-emerald-100/70 p-2.5 rounded-lg border border-emerald-200">
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
              <span>Excellent! All quality, product, batch, customer, and date details are fully specified.</span>
            </div>
          )}
        </div>
      )}

      {/* Clarification Email Modal */}
      {emailModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
          <div className="bg-white rounded-2xl border border-slate-200 shadow-xl max-w-xl w-full overflow-hidden flex flex-col max-h-[90vh]">
            <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mail className="h-5 w-5 text-teal-600" />
                <h3 className="font-bold text-slate-800 text-base">Customer Clarification Email Draft</h3>
              </div>
              <button
                onClick={() => setEmailModalOpen(false)}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-200/50 transition-colors cursor-pointer"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="p-6 overflow-y-auto space-y-4">
              {isGeneratingEmail ? (
                <div className="py-8 text-center text-slate-500 space-y-2">
                  <Sparkles className="h-6 w-6 text-teal-600 animate-spin mx-auto" />
                  <p className="text-xs font-medium">Generating AI customer clarification inquiry...</p>
                </div>
              ) : (
                <>
                  <p className="text-xs text-slate-500">
                    Use this pre-drafted email to request missing batch or product details from the customer or pharmacy partner.
                  </p>
                  <div className="relative">
                    <textarea
                      value={emailDraft}
                      onChange={(e) => setEmailDraft(e.target.value)}
                      rows={12}
                      className="w-full p-3.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-mono text-slate-800 focus:ring-2 focus:ring-teal-500 focus:border-teal-500 outline-none resize-y"
                    />
                  </div>
                </>
              )}
            </div>

            <div className="px-6 py-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
              <span className="text-[11px] text-slate-500">Editable preview</span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setEmailModalOpen(false)}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:bg-slate-200/70 transition-colors cursor-pointer"
                >
                  Close
                </button>
                <button
                  type="button"
                  onClick={handleCopyEmail}
                  disabled={isGeneratingEmail}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-teal-600 text-white hover:bg-teal-700 transition-colors shadow-xs cursor-pointer disabled:opacity-50"
                >
                  {copied ? (
                    <>
                      <Check className="h-3.5 w-3.5" />
                      <span>Copied to Clipboard!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span>Copy Email Text</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
