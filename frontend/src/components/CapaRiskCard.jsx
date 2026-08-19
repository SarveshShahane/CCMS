import React, { useState } from 'react';
import {
  ShieldAlert,
  Sparkles,
  FileText,
  AlertOctagon,
  CheckCircle2,
  Clock,
  Building,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Zap,
  Activity,
  Layers,
} from 'lucide-react';
import { complaintApi } from '../api/api';

export default function CapaRiskCard({ formData, complaintId, onSynced }) {
  const [capaRes, setCapaRes] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleEvaluate = async () => {
    setIsLoading(true);
    setError(null);
    setSyncSuccess(false);

    const hasEnoughData =
      formData?.product_name?.trim() ||
      formData?.description?.trim() ||
      formData?.title?.trim() ||
      formData?.batch_number?.trim();

    if (!hasEnoughData && !complaintId) {
      setIsLoading(false);
      setError('Form is empty. Please enter a Product Name or Complaint Description before evaluating CAPA & Risk.');
      return;
    }

    try {
      let data;
      if (complaintId) {
        data = await complaintApi.getSavedComplaintCapaRisk(complaintId);
      } else {
        data = await complaintApi.evaluateCapaRisk(formData);
      }
      setCapaRes(data);
      setIsExpanded(true);
    } catch (err) {
      console.error('CAPA Risk evaluation error:', err);
      setError(err.message || 'Failed to evaluate CAPA & Risk Classification');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSyncToRecord = async () => {
    if (!complaintId || !capaRes) return;
    setIsSyncing(true);
    try {
      const riskSummary =
        `[Severity: ${capaRes.risk_classification.severity_level}] ` +
        `[Health Hazard: ${capaRes.risk_classification.health_hazard_class}] ` +
        `[RPN: ${capaRes.risk_classification.rpn_score}]\n` +
        `${capaRes.complaint_summary.executive_summary}\n` +
        `Risk Note: ${capaRes.risk_classification.risk_explanation}`;

      const capaText = capaRes.capa_plan
        .map(
          (c) =>
            `[${c.action_type}] ${c.title}: ${c.description}\n` +
            `Owner: ${c.owner_department} | Target: ${c.target_timeline_days}d | Effectiveness Verification: ${c.effectiveness_verification_plan}`
        )
        .join('\n\n');

      await complaintApi.updateComplaintRcaCapa(complaintId, {
        root_cause_category: capaRes.risk_classification.severity_level,
        investigation_findings: riskSummary,
        capa_required: capaRes.capa_plan.length > 0,
        capa_details: capaText,
      });

      setSyncSuccess(true);
      if (onSynced) onSynced();
    } catch (err) {
      console.error('Failed to sync CAPA to record:', err);
      alert(err.message || 'Error syncing CAPA details to complaint record');
    } finally {
      setIsSyncing(false);
    }
  };

  const handleCopyReport = () => {
    if (!capaRes) return;
    const report =
      `===================================================\n` +
      `PHARMACEUTICAL COMPLAINT CAPA & RISK ASSESSMENT REPORT\n` +
      `===================================================\n\n` +
      `1. COMPLAINT EXECUTIVE SUMMARY:\n` +
      `${capaRes.complaint_summary.executive_summary}\n` +
      `- Defect Impact: ${capaRes.complaint_summary.defect_impact}\n` +
      `- Batch Scope: ${capaRes.complaint_summary.batch_scope}\n\n` +
      `2. AI RISK CLASSIFICATION:\n` +
      `- Initial Severity: ${capaRes.risk_classification.severity_level}\n` +
      `- Health Hazard Class: ${capaRes.risk_classification.health_hazard_class}\n` +
      `- Risk Priority Number (RPN): ${capaRes.risk_classification.rpn_score}/100\n` +
      `- Occurrence Probability: ${capaRes.risk_classification.occurrence_probability}\n` +
      `- Detection Difficulty: ${capaRes.risk_classification.detection_difficulty}\n` +
      `- Risk Rationale: ${capaRes.risk_classification.risk_explanation}\n\n` +
      `3. CORRECTIVE & PREVENTIVE ACTION (CAPA) PLAN:\n` +
      capaRes.capa_plan
        .map(
          (c, idx) =>
            `${idx + 1}. [${c.action_type}] ${c.title} (Dept: ${c.owner_department}, Target: ${c.target_timeline_days} days)\n` +
            `   Description: ${c.description}\n` +
            `   Effectiveness Metric: ${c.effectiveness_verification_plan}\n`
        )
        .join('\n') +
      `\nGMP Notes: ${capaRes.gmp_audit_readiness_notes}\n`;

    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getHazardBadge = (hhClass) => {
    switch (hhClass?.toUpperCase()) {
      case 'CLASS_I':
      case 'CLASS 1':
        return 'bg-rose-100 text-rose-900 border-rose-300';
      case 'CLASS_II':
      case 'CLASS 2':
        return 'bg-amber-100 text-amber-900 border-amber-300';
      default:
        return 'bg-emerald-100 text-emerald-900 border-emerald-300';
    }
  };

  const getSeverityBadge = (sev) => {
    switch (sev?.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-600 text-white';
      case 'MAJOR':
        return 'bg-amber-500 text-white';
      default:
        return 'bg-sky-600 text-white';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
      {/* Header Bar */}
      <div className="px-6 py-4 bg-gradient-to-r from-teal-950 via-slate-900 to-teal-950 text-white flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-teal-500/20 text-teal-300 border border-teal-500/30">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-sm text-white">CAPA Plan & AI Risk Classification Engine</h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">
                21 CFR 211 / ICH Q9
              </span>
            </div>
            <p className="text-xs text-teal-200/70">
              Complaint summary, multi-dimensional risk classification & effectiveness metrics
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleEvaluate}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-teal-500 text-slate-950 hover:bg-teal-400 transition-all shadow-xs cursor-pointer disabled:opacity-50"
          >
            <Sparkles className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{isLoading ? 'Evaluating...' : capaRes ? 'Re-Evaluate CAPA & Risk' : 'Evaluate CAPA & Risk'}</span>
          </button>

          {capaRes && (
            <button
              type="button"
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1.5 text-teal-200 hover:text-white rounded-lg hover:bg-white/10 transition-colors cursor-pointer"
            >
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
          )}
        </div>
      </div>

      {/* Main Body */}
      {capaRes && isExpanded && (
        <div className="p-6 space-y-6 bg-slate-50/50">
          {/* SECTION 1: Complaint Technical Summary */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 space-y-3 shadow-2xs">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
              <FileText className="h-4 w-4 text-teal-600" /> Executive Complaint Technical Summary
            </h4>

            <p className="text-xs text-slate-800 font-medium leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200">
              {capaRes.complaint_summary?.executive_summary}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-[11px]">
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/80">
                <span className="font-semibold text-slate-500 block text-[10px] uppercase">Defect Impact:</span>
                <span className="text-slate-800 font-medium">{capaRes.complaint_summary?.defect_impact}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/80">
                <span className="font-semibold text-slate-500 block text-[10px] uppercase">Batch Scope:</span>
                <span className="text-slate-800 font-medium">{capaRes.complaint_summary?.batch_scope}</span>
              </div>
              <div className="p-2.5 bg-slate-50 rounded-lg border border-slate-200/80">
                <span className="font-semibold text-slate-500 block text-[10px] uppercase">Customer Risk:</span>
                <span className="text-slate-800 font-medium">{capaRes.complaint_summary?.customer_risk}</span>
              </div>
            </div>
          </div>

          {/* SECTION 2: AI Risk Classification Dashboard */}
          <div className="bg-white p-4 rounded-xl border border-teal-200 space-y-4 shadow-2xs">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 flex items-center gap-1.5">
                <Activity className="h-4 w-4 text-teal-600" /> AI Risk Matrix Classification
              </h4>
              <div className="flex items-center gap-2">
                <span className={`px-2.5 py-1 rounded-full text-xs font-black uppercase ${getSeverityBadge(capaRes.risk_classification?.severity_level)}`}>
                  {capaRes.risk_classification?.severity_level} Severity
                </span>
                <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${getHazardBadge(capaRes.risk_classification?.health_hazard_class)}`}>
                  Health Hazard: {capaRes.risk_classification?.health_hazard_class}
                </span>
              </div>
            </div>

            {/* RPN Score Gauge & Matrix Indicators */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <div className="text-center sm:text-left border-b sm:border-b-0 sm:border-r border-slate-200 pb-2 sm:pb-0 sm:pr-3">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Risk Priority Score</span>
                <div className="text-2xl font-black text-slate-900 mt-0.5">
                  {capaRes.risk_classification?.rpn_score} <span className="text-xs text-slate-400 font-normal">/ 100</span>
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Occurrence Prob.</span>
                <div className="font-bold text-slate-800 text-xs mt-1">
                  {capaRes.risk_classification?.occurrence_probability}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Detection Difficulty</span>
                <div className="font-bold text-slate-800 text-xs mt-1">
                  {capaRes.risk_classification?.detection_difficulty}
                </div>
              </div>

              <div>
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wide">Health Hazard Class</span>
                <div className="font-bold text-slate-800 text-xs mt-1">
                  {capaRes.risk_classification?.health_hazard_class}
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed font-sans">
              <strong>Risk Justification:</strong> {capaRes.risk_classification?.risk_explanation}
            </p>
          </div>

          {/* SECTION 3: Actionable CAPA Plan */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
              <Zap className="h-4 w-4 text-teal-600" /> Actionable CAPA Plan & Effectiveness Metrics
            </h4>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {capaRes.capa_plan?.map((capa) => (
                <div
                  key={capa.capa_id}
                  className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs space-y-2.5 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span
                        className={`px-2.5 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wide ${
                          capa.action_type === 'CORRECTIVE'
                            ? 'bg-rose-100 text-rose-800 border border-rose-200'
                            : 'bg-teal-100 text-teal-800 border border-teal-200'
                        }`}
                      >
                        {capa.capa_id} • {capa.action_type}
                      </span>
                      <span className="text-[10px] font-semibold text-slate-500 flex items-center gap-1">
                        <Clock className="h-3 w-3 text-slate-400" />
                        Target: {capa.target_timeline_days} days
                      </span>
                    </div>

                    <h5 className="text-xs font-bold text-slate-900">{capa.title}</h5>
                    <p className="text-[11px] text-slate-600 leading-relaxed">{capa.description}</p>
                  </div>

                  <div className="pt-2 border-t border-slate-100 space-y-1.5 text-[10px]">
                    <div className="flex items-center justify-between text-slate-500 font-medium">
                      <span>Owner Dept:</span>
                      <span className="font-bold text-slate-800">{capa.owner_department}</span>
                    </div>
                    <div className="p-2 bg-emerald-50/70 rounded-lg border border-emerald-200/80 text-emerald-900">
                      <span className="font-bold block text-[9px] uppercase tracking-wide text-emerald-800">
                        GMP Effectiveness Metric:
                      </span>
                      <span className="text-[10px] leading-snug">{capa.effectiveness_verification_plan}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Controls */}
          <div className="pt-3 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <span className="text-[11px] text-slate-500 font-mono">
              {capaRes.gmp_audit_readiness_notes}
            </span>

            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={handleCopyReport}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs cursor-pointer"
              >
                {copied ? <Check className="h-3.5 w-3.5 text-emerald-600" /> : <Copy className="h-3.5 w-3.5 text-slate-500" />}
                <span>{copied ? 'Copied Audit Summary!' : 'Copy Audit Summary'}</span>
              </button>

              {complaintId && (
                <button
                  type="button"
                  onClick={handleSyncToRecord}
                  disabled={isSyncing}
                  className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-teal-600 text-white hover:bg-teal-700 transition-colors shadow-xs cursor-pointer disabled:opacity-50"
                >
                  {syncSuccess ? (
                    <>
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span>Synced to Record!</span>
                    </>
                  ) : (
                    <>
                      <ShieldAlert className="h-3.5 w-3.5" />
                      <span>{isSyncing ? 'Syncing...' : 'Sync Risk & CAPA to Record'}</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-50 border-t border-rose-200 text-xs text-rose-700">
          <strong>Evaluation Error:</strong> {error}
        </div>
      )}
    </div>
  );
}
