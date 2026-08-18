import React, { useState, useEffect } from 'react';
import {
  CopyCheck,
  AlertTriangle,
  ExternalLink,
  Layers,
  ChevronDown,
  ChevronUp,
  Sparkles,
  CheckCircle,
} from 'lucide-react';
import { complaintApi } from '../api/api';

export default function DuplicateComplaintCard({ formData, complaintId, onSelectMatch }) {
  const [duplicateRes, setDuplicateRes] = useState(null);
  const [isChecking, setIsChecking] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  const batchNumber = formData?.batch_number;
  const productName = formData?.product_name;

  useEffect(() => {
    let isMounted = true;
    if (!batchNumber && !productName) {
      setDuplicateRes(null);
      return;
    }

    const timer = setTimeout(async () => {
      setIsChecking(true);
      try {
        let res;
        if (complaintId) {
          res = await complaintApi.getSavedComplaintDuplicates(complaintId);
        } else {
          res = await complaintApi.checkDuplicates(formData, complaintId);
        }
        if (isMounted) setDuplicateRes(res);
      } catch (err) {
        console.error('Duplicate check error:', err);
      } finally {
        if (isMounted) setIsChecking(false);
      }
    }, 400);

    return () => {
      isMounted = false;
      clearTimeout(timer);
    };
  }, [batchNumber, productName, complaintId]);

  if (!duplicateRes || !duplicateRes.has_duplicates) {
    return null;
  }

  const matches = duplicateRes.duplicate_matches || [];
  const topMatch = matches[0];
  const isHighConfidence = duplicateRes.highest_similarity_score >= 75;

  return (
    <div
      className={`rounded-xl border shadow-2xs transition-all ${
        isHighConfidence ? 'bg-rose-50/90 border-rose-200 text-rose-900' : 'bg-amber-50/90 border-amber-200 text-amber-900'
      }`}
    >
      {/* Header Bar */}
      <div className="p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className={`p-2 rounded-lg bg-white/80 shadow-2xs border ${
              isHighConfidence ? 'border-rose-300 text-rose-600' : 'border-amber-300 text-amber-600'
            }`}
          >
            <AlertTriangle className="h-5 w-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm">
                {isHighConfidence ? 'Possible Duplicate Complaint Detected!' : 'Potential Related Complaints Found'}
              </span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-extrabold ${
                  isHighConfidence ? 'bg-rose-200 text-rose-900' : 'bg-amber-200 text-amber-900'
                }`}
              >
                {duplicateRes.highest_similarity_score}% Match
              </span>
            </div>
            <p className="text-xs opacity-90 mt-0.5">{duplicateRes.recommended_action}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isChecking && <Sparkles className="h-4 w-4 animate-spin text-slate-500" />}
          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1.5 hover:bg-black/5 rounded-lg transition-colors cursor-pointer"
          >
            {isExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
        </div>
      </div>

      {/* Expanded Match Cards */}
      {isExpanded && (
        <div className="p-4 bg-white/70 border-t border-slate-200/60 rounded-b-xl space-y-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-600 block mb-2">
            Matching Complaints in Registry ({matches.length}):
          </span>

          <div className="space-y-2">
            {matches.map((item) => (
              <div
                key={item.complaint_id}
                className="bg-white p-3 rounded-xl border border-slate-200 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-teal-700">{item.complaint_number}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                      {item.status}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-teal-50 text-teal-800 border border-teal-200">
                      {item.similarity_score}% Match
                    </span>
                  </div>

                  <p className="font-semibold text-slate-900">{item.title || item.product_name}</p>

                  <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500 font-mono">
                    <span>Batch #: <strong>{item.batch_number || 'N/A'}</strong></span>
                    <span>Matched Attributes: <strong className="text-teal-700">{item.matched_fields.join(', ')}</strong></span>
                  </div>
                </div>

                {onSelectMatch && (
                  <button
                    type="button"
                    onClick={() => onSelectMatch(item)}
                    className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-teal-50 text-teal-800 hover:bg-teal-100 border border-teal-200 transition-colors cursor-pointer shrink-0"
                  >
                    <ExternalLink className="h-3.5 w-3.5" />
                    <span>View Sibling Record</span>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
