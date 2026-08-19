import React, { useState } from 'react';
import {
  Brain,
  Sparkles,
  CheckSquare,
  Square,
  ShieldAlert,
  Wrench,
  CheckCircle,
  FileCheck,
  Zap,
  ChevronDown,
  ChevronUp,
  Clock,
} from 'lucide-react';
import { complaintApi } from '../api/api';

export default function RootCauseRecommendationCard({ formData, complaintId, onApplied }) {
  const [rcaResult, setRcaResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(true);
  const [completedSteps, setCompletedSteps] = useState({});
  const [isApplying, setIsApplying] = useState(false);
  const [appliedSuccess, setAppliedSuccess] = useState(false);

  const handleRunRca = async () => {
    setIsLoading(true);
    setError(null);
    setAppliedSuccess(false);

    const hasEnoughData =
      formData?.product_name?.trim() ||
      formData?.description?.trim() ||
      formData?.title?.trim() ||
      formData?.batch_number?.trim();

    if (!hasEnoughData && !complaintId) {
      setIsLoading(false);
      setError('Form is empty. Please enter a Product Name or Complaint Description before running Root Cause Analysis.');
      return;
    }

    try {
      let data;
      if (complaintId) {
        data = await complaintApi.recommendSavedRootCause(complaintId);
      } else {
        data = await complaintApi.recommendRootCause(formData);
      }
      setRcaResult(data);
      setIsExpanded(true);
    } catch (err) {
      console.error('Failed to analyze root cause:', err);
      setError(err.message || 'Failed to generate root cause analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  const toggleStep = (stepNo) => {
    setCompletedSteps((prev) => ({ ...prev, [stepNo]: !prev[stepNo] }));
  };

  const handleApplyRca = async () => {
    if (!complaintId || !rcaResult) return;
    setIsApplying(true);
    try {
      const capaText = rcaResult.capa_recommendations
        .map((c) => `[${c.action_type}] ${c.title}: ${c.description} (Target: ${c.target_timeline_days}d)`)
        .join('\n\n');

      const checklistText = rcaResult.investigation_checklist
        .map((s) => `Step ${s.step_number} [${s.department}] (${s.priority}): ${s.action}`)
        .join('\n');

      const findingsText = `${rcaResult.summary_assessment}\n\nRecommended Investigation Checklist:\n${checklistText}`;

      await complaintApi.updateComplaintRcaCapa(complaintId, {
        root_cause_category: rcaResult.suggested_root_cause_category,
        investigation_findings: findingsText,
        capa_required: rcaResult.capa_recommendations.length > 0,
        capa_details: capaText,
      });

      setAppliedSuccess(true);
      if (onApplied) onApplied();
    } catch (err) {
      console.error('Failed to apply RCA to complaint:', err);
      alert(err.message || 'Failed to apply RCA details to complaint');
    } finally {
      setIsApplying(false);
    }
  };

  const getConfidenceBadge = (confidence) => {
    switch (confidence?.toUpperCase()) {
      case 'HIGH':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
      case 'MEDIUM':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      default:
        return 'bg-slate-100 text-slate-700 border-slate-300';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
      {/* Header Bar */}
      <div className="px-6 py-4 bg-gradient-to-r from-slate-900 via-teal-950 to-slate-900 text-white flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-teal-500/20 text-teal-300 border border-teal-500/30">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="font-bold text-sm text-white">AI Root Cause Analysis & CAPA Advisor</h3>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-teal-500/20 text-teal-300 border border-teal-500/30">
                Ishikawa 5M+E
              </span>
            </div>
            <p className="text-xs text-teal-200/70">
              Predict failure modes, investigation steps & CAPA timelines
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={handleRunRca}
            disabled={isLoading}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold bg-teal-500 text-slate-950 hover:bg-teal-400 transition-all shadow-xs cursor-pointer disabled:opacity-50"
          >
            <Sparkles className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{isLoading ? 'Analyzing...' : rcaResult ? 'Re-Analyze RCA' : 'Run Root Cause Analysis'}</span>
          </button>

          {rcaResult && (
            <button
              type="button"
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1.5 text-teal-200 hover:text-white rounded-lg hover:bg-white/10 transition-colors"
            >
              {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
          )}
        </div>
      </div>

      {/* Main Body */}
      {rcaResult && isExpanded && (
        <div className="p-6 space-y-6 bg-slate-50/50">
          {/* Executive Summary & Suggested Category */}
          <div className="p-4 bg-white rounded-xl border border-teal-200 shadow-2xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-teal-800 flex items-center gap-1.5">
                <Zap className="h-4 w-4 text-teal-600" /> Executive RCA Assessment
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-extrabold bg-teal-100 text-teal-900 border border-teal-300">
                Primary Cause: {rcaResult.suggested_root_cause_category}
              </span>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed font-medium">
              {rcaResult.summary_assessment}
            </p>
          </div>

          {/* Root Cause Hypotheses */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
              <ShieldAlert className="h-4 w-4 text-amber-600" /> Ishikawa Root Cause Hypotheses
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {rcaResult.hypotheses?.map((h, idx) => (
                <div
                  key={idx}
                  className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs flex flex-col justify-between space-y-2.5"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wide">
                        {h.category}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getConfidenceBadge(h.confidence_level)}`}>
                        {h.confidence_level} ({h.likelihood_score}%)
                      </span>
                    </div>
                    <h5 className="text-xs font-bold text-slate-800">{h.title}</h5>
                    <p className="text-[11px] text-slate-600 mt-1 leading-snug">{h.description}</p>
                  </div>

                  {/* Likelihood Bar */}
                  <div>
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-teal-500 h-full rounded-full transition-all"
                        style={{ width: `${h.likelihood_score}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recommended Investigation Checklist */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
              <FileCheck className="h-4 w-4 text-sky-600" /> Recommended QA Investigation Checklist
            </h4>
            <div className="bg-white rounded-xl border border-slate-200 overflow-hidden divide-y divide-slate-100">
              {rcaResult.investigation_checklist?.map((step) => {
                const isChecked = !!completedSteps[step.step_number];
                return (
                  <div
                    key={step.step_number}
                    onClick={() => toggleStep(step.step_number)}
                    className={`p-3 flex items-center justify-between text-xs cursor-pointer transition-colors ${
                      isChecked ? 'bg-emerald-50/50 text-slate-400 line-through' : 'hover:bg-slate-50 text-slate-800'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      {isChecked ? (
                        <CheckSquare className="h-4 w-4 text-emerald-600 shrink-0" />
                      ) : (
                        <Square className="h-4 w-4 text-slate-400 shrink-0" />
                      )}
                      <div>
                        <span className="font-semibold mr-1.5 text-slate-900">
                          Step {step.step_number}:
                        </span>
                        <span>{step.action}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0 ml-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                        {step.department}
                      </span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          step.priority === 'CRITICAL'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {step.priority}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* CAPA Recommendations */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
              <Wrench className="h-4 w-4 text-teal-600" /> Suggested CAPA Plan
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {rcaResult.capa_recommendations?.map((capa, idx) => (
                <div key={idx} className="bg-white p-3.5 rounded-xl border border-slate-200 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wide ${
                        capa.action_type === 'CORRECTIVE'
                          ? 'bg-rose-100 text-rose-800 border border-rose-200'
                          : 'bg-teal-100 text-teal-800 border border-teal-200'
                      }`}
                    >
                      {capa.action_type}
                    </span>
                    <span className="text-[10px] text-slate-500 flex items-center gap-1 font-mono">
                      <Clock className="h-3 w-3 text-slate-400" />
                      Target: {capa.target_timeline_days} days
                    </span>
                  </div>
                  <h5 className="text-xs font-bold text-slate-800">{capa.title}</h5>
                  <p className="text-[11px] text-slate-600 leading-relaxed">{capa.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Apply Action Button for saved complaint */}
          {complaintId && (
            <div className="pt-2 flex items-center justify-between border-t border-slate-200">
              <span className="text-xs text-slate-500">
                Apply RCA & CAPA directly to saved record #{complaintId}
              </span>
              <button
                type="button"
                onClick={handleApplyRca}
                disabled={isApplying}
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold bg-teal-600 text-white hover:bg-teal-700 transition-colors shadow-xs cursor-pointer disabled:opacity-50"
              >
                {appliedSuccess ? (
                  <>
                    <CheckCircle className="h-4 w-4" />
                    <span>Applied to Complaint Record!</span>
                  </>
                ) : (
                  <>
                    <FileCheck className="h-4 w-4" />
                    <span>{isApplying ? 'Applying...' : 'Apply Recommendations to Record'}</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-50 border-t border-rose-200 text-xs text-rose-700">
          <strong>RCA Error:</strong> {error}
        </div>
      )}
    </div>
  );
}
