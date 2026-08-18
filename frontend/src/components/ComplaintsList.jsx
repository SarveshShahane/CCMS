import React, { useState, useEffect, useMemo } from 'react';
import { useDispatch } from 'react-redux';
import {
  Search,
  RefreshCw,
  Plus,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Filter,
  Eye,
  X,
  Building2,
  Package,
  Calendar,
  FileText,
  User,
  Mail,
  Phone,
  ShieldAlert,
  Sparkles,
  Inbox,
  ArrowRight,
  ChevronLeft,
  ChevronRight,
  Layers,
} from 'lucide-react';
import { complaintApi } from '../api/api';
import { setActiveView } from '../store/slices/appSlice';

export default function ComplaintsList() {
  const dispatch = useDispatch();
  const [complaints, setComplaints] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  // Pagination
  const [page, setPage] = useState(0);
  const limit = 20;

  // Selected Complaint for Modal
  const [selectedComplaint, setSelectedComplaint] = useState(null);

  // Fetch complaints from API
  const fetchComplaints = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await complaintApi.listComplaints(page * limit, limit);
      setComplaints(data.items || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error('Failed to fetch complaints:', err);
      setError(err.message || 'Failed to load complaints list');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, [page]);

  // Derived filtered complaints
  const filteredComplaints = useMemo(() => {
    return complaints.filter((item) => {
      // Search query matching
      const query = searchQuery.toLowerCase().trim();
      const matchesSearch =
        !query ||
        item.complaint_number?.toLowerCase().includes(query) ||
        item.product_name?.toLowerCase().includes(query) ||
        item.title?.toLowerCase().includes(query) ||
        item.customer_name?.toLowerCase().includes(query) ||
        item.batch_number?.toLowerCase().includes(query) ||
        item.complaint_category?.toLowerCase().includes(query);

      // Severity matching
      const matchesSeverity =
        severityFilter === 'ALL' ||
        item.initial_severity?.toUpperCase() === severityFilter.toUpperCase();

      // Category matching
      const matchesCategory =
        categoryFilter === 'ALL' ||
        item.complaint_category?.toUpperCase() === categoryFilter.toUpperCase();

      return matchesSearch && matchesSeverity && matchesCategory;
    });
  }, [complaints, searchQuery, severityFilter, categoryFilter]);

  // Stats calculation
  const stats = useMemo(() => {
    const critical = complaints.filter((c) => c.initial_severity?.toUpperCase() === 'CRITICAL').length;
    const major = complaints.filter((c) => c.initial_severity?.toUpperCase() === 'MAJOR').length;
    const minor = complaints.filter((c) => c.initial_severity?.toUpperCase() === 'MINOR').length;
    return { total: totalCount || complaints.length, critical, major, minor };
  }, [complaints, totalCount]);

  // Helper function for severity badge colors
  const getSeverityBadge = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'CRITICAL':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-600 animate-pulse"></span>
            Critical
          </span>
        );
      case 'MAJOR':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <span className="h-1.5 w-1.5 rounded-full bg-amber-500"></span>
            Major
          </span>
        );
      case 'MINOR':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-sky-50 text-sky-700 border border-sky-200">
            <span className="h-1.5 w-1.5 rounded-full bg-sky-500"></span>
            Minor
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
            {severity || 'Unassigned'}
          </span>
        );
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-4 lg:p-6 space-y-6">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold text-slate-900 tracking-tight">Quality Intake Registry</h2>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-50 text-teal-700 border border-teal-200">
              {stats.total} Records
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Browse, filter, and inspect submitted pharmaceutical complaint records and AI risk triage evaluations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchComplaints}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors cursor-pointer border border-slate-200 disabled:opacity-50"
            title="Refresh list"
          >
            <RefreshCw className={`h-3.5 w-3.5 text-slate-500 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>

          <button
            onClick={() => dispatch(setActiveView('form'))}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 shadow-md shadow-teal-600/20 transition-all cursor-pointer"
          >
            <Plus className="h-4 w-4" />
            <span>New Complaint</span>
          </button>
        </div>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-slate-500">Total Registered</p>
            <p className="text-2xl font-extrabold text-slate-900 mt-0.5">{stats.total}</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-teal-50 border border-teal-100 flex items-center justify-center text-teal-600">
            <Layers className="h-5 w-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-rose-600">Critical Risk</p>
            <p className="text-2xl font-extrabold text-rose-700 mt-0.5">{stats.critical}</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center text-rose-600">
            <AlertTriangle className="h-5 w-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-amber-600">Major Priority</p>
            <p className="text-2xl font-extrabold text-amber-700 mt-0.5">{stats.major}</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-600">
            <ShieldAlert className="h-5 w-5" />
          </div>
        </div>

        <div className="bg-white p-4 rounded-xl border border-slate-200/80 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-medium text-sky-600">Minor Priority</p>
            <p className="text-2xl font-extrabold text-sky-700 mt-0.5">{stats.minor}</p>
          </div>
          <div className="h-10 w-10 rounded-xl bg-sky-50 border border-sky-100 flex items-center justify-center text-sky-600">
            <CheckCircle2 className="h-5 w-5" />
          </div>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex flex-col md:flex-row gap-4 items-center justify-between">
        {/* Search Input */}
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by Complaint #, Product, Title, Customer, Batch..."
            className="w-full pl-10 pr-10 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-teal-500/20 focus:border-teal-500 transition-all text-slate-900 placeholder-slate-400"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-0.5 text-slate-400 hover:text-slate-600 cursor-pointer"
            >
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {/* Severity Filter Tabs */}
        <div className="flex items-center gap-1.5 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
          {['ALL', 'CRITICAL', 'MAJOR', 'MINOR'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
                severityFilter === sev
                  ? 'bg-slate-900 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200/70'
              }`}
            >
              {sev === 'ALL' ? 'All Severities' : sev.charAt(0) + sev.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content Table / List */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <RefreshCw className="h-8 w-8 text-teal-600 animate-spin mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-700">Loading complaints registry...</p>
            <p className="text-xs text-slate-400 mt-1">Connecting to secure database</p>
          </div>
        ) : error ? (
          <div className="p-12 text-center">
            <AlertTriangle className="h-8 w-8 text-rose-500 mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-800">Failed to load complaints</p>
            <p className="text-xs text-rose-600 mt-1">{error}</p>
            <button
              onClick={fetchComplaints}
              className="mt-4 px-4 py-2 text-xs font-semibold bg-slate-100 text-slate-700 hover:bg-slate-200 rounded-lg border border-slate-300 transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : filteredComplaints.length === 0 ? (
          <div className="p-12 text-center">
            <Inbox className="h-10 w-10 text-slate-300 mx-auto mb-3" />
            <p className="text-sm font-semibold text-slate-800">No complaints found</p>
            <p className="text-xs text-slate-500 mt-1">
              {searchQuery || severityFilter !== 'ALL'
                ? 'Try adjusting your search filters.'
                : 'No complaint records have been logged in the system yet.'}
            </p>
            {searchQuery || severityFilter !== 'ALL' ? (
              <button
                onClick={() => {
                  setSearchQuery('');
                  setSeverityFilter('ALL');
                }}
                className="mt-4 px-4 py-2 text-xs font-semibold text-teal-700 bg-teal-50 hover:bg-teal-100 rounded-lg border border-teal-200 transition-colors cursor-pointer"
              >
                Clear Filters
              </button>
            ) : (
              <button
                onClick={() => dispatch(setActiveView('form'))}
                className="mt-4 px-4 py-2 text-xs font-semibold text-white bg-teal-600 hover:bg-teal-700 rounded-lg shadow-sm transition-colors cursor-pointer inline-flex items-center gap-1.5"
              >
                <Plus className="h-3.5 w-3.5" />
                Submit First Complaint
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/80 border-b border-slate-200/80 text-xs font-bold text-slate-600 uppercase tracking-wider">
                  <th className="py-3.5 px-4">Complaint #</th>
                  <th className="py-3.5 px-4">Product & Batch</th>
                  <th className="py-3.5 px-4">Title / Category</th>
                  <th className="py-3.5 px-4">Customer / Source</th>
                  <th className="py-3.5 px-4">Severity</th>
                  <th className="py-3.5 px-4">Date</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200/70 text-xs text-slate-700">
                {filteredComplaints.map((item) => (
                  <tr
                    key={item.id}
                    className="hover:bg-slate-50/80 transition-colors cursor-pointer group"
                    onClick={() => setSelectedComplaint(item)}
                  >
                    <td className="py-3.5 px-4 font-mono font-bold text-teal-700 whitespace-nowrap">
                      {item.complaint_number}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-900">{item.product_name || 'N/A'}</div>
                      <div className="text-[11px] text-slate-400 font-mono">
                        Batch: {item.batch_number || 'N/A'}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 max-w-xs">
                      <div className="font-medium text-slate-800 truncate">{item.title || 'Untitled Complaint'}</div>
                      <div className="text-[11px] text-slate-500 font-medium">
                        {item.complaint_category || 'General'}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="font-medium text-slate-800">{item.customer_name || 'Anonymous'}</div>
                      <div className="text-[11px] text-slate-400">{item.complaint_source || 'Direct'}</div>
                    </td>
                    <td className="py-3.5 px-4 whitespace-nowrap">{getSeverityBadge(item.initial_severity)}</td>
                    <td className="py-3.5 px-4 whitespace-nowrap text-slate-500">
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="py-3.5 px-4 text-right whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedComplaint(item);
                        }}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold text-teal-700 bg-teal-50 hover:bg-teal-100 border border-teal-200 transition-colors cursor-pointer"
                      >
                        <Eye className="h-3.5 w-3.5" />
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Footer / Pagination */}
        {totalCount > limit && (
          <div className="p-4 border-t border-slate-200/80 bg-slate-50/50 flex items-center justify-between text-xs text-slate-600">
            <div>
              Showing <span className="font-semibold">{page * limit + 1}</span> to{' '}
              <span className="font-semibold">{Math.min((page + 1) * limit, totalCount)}</span> of{' '}
              <span className="font-semibold">{totalCount}</span> entries
            </div>

            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 cursor-pointer"
              >
                <ChevronLeft className="h-4 w-4 text-slate-600" />
              </button>
              <span className="font-semibold">Page {page + 1}</span>
              <button
                disabled={(page + 1) * limit >= totalCount}
                onClick={() => setPage((p) => p + 1)}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 cursor-pointer"
              >
                <ChevronRight className="h-4 w-4 text-slate-600" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* COMPLAINT DETAIL MODAL */}
      {selectedComplaint && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto animate-fade-in">
          <div className="bg-white w-full max-w-3xl rounded-2xl shadow-2xl border border-slate-200 overflow-hidden my-8 max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 rounded-xl bg-teal-500/20 border border-teal-500/30 text-teal-400 flex items-center justify-center">
                  <FileText className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-teal-300 text-sm">
                      {selectedComplaint.complaint_number}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-semibold uppercase bg-slate-800 text-slate-300 border border-slate-700">
                      {selectedComplaint.status}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-slate-100 truncate max-w-md">
                    {selectedComplaint.title || 'Pharmaceutical Quality Complaint Record'}
                  </h3>
                </div>
              </div>

              <button
                onClick={() => setSelectedComplaint(null)}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-800 text-xs">
              {/* Header Badges & Quick Meta */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                <div>
                  <span className="text-[11px] text-slate-400 font-medium block">Initial Severity</span>
                  <div className="mt-1">{getSeverityBadge(selectedComplaint.initial_severity)}</div>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400 font-medium block">Category</span>
                  <span className="font-semibold text-slate-800 block mt-1">
                    {selectedComplaint.complaint_category || 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400 font-medium block">Complaint Date</span>
                  <span className="font-semibold text-slate-800 block mt-1">
                    {selectedComplaint.complaint_date || 'N/A'}
                  </span>
                </div>
                <div>
                  <span className="text-[11px] text-slate-400 font-medium block">Sample Received</span>
                  <span
                    className={`font-semibold block mt-1 ${
                      selectedComplaint.sample_received ? 'text-emerald-700' : 'text-slate-500'
                    }`}
                  >
                    {selectedComplaint.sample_received ? 'Yes (Physical)' : 'No Sample'}
                  </span>
                </div>
              </div>

              {/* AI Triage & Risk Assessment Box */}
              {(selectedComplaint.ai_risk_assessment || selectedComplaint.ai_suggested_next_action) && (
                <div className="p-4 rounded-xl bg-gradient-to-r from-teal-900/5 to-slate-900/5 border border-teal-500/20 space-y-3">
                  <div className="flex items-center gap-2 text-teal-800 font-bold text-xs">
                    <Sparkles className="h-4 w-4 text-teal-600" />
                    <span>AI Copilot Triage Summary</span>
                  </div>

                  {selectedComplaint.ai_risk_assessment && (
                    <div>
                      <span className="font-semibold text-slate-700 block mb-1">Risk Evaluation:</span>
                      <p className="text-slate-600 bg-white/80 p-2.5 rounded-lg border border-teal-100 leading-relaxed">
                        {selectedComplaint.ai_risk_assessment}
                      </p>
                    </div>
                  )}

                  {selectedComplaint.ai_suggested_next_action && (
                    <div>
                      <span className="font-semibold text-slate-700 block mb-1">Recommended Next Actions:</span>
                      <p className="text-slate-600 bg-white/80 p-2.5 rounded-lg border border-teal-100 leading-relaxed">
                        {selectedComplaint.ai_suggested_next_action}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Product & Batch Section */}
              <div className="space-y-3">
                <h4 className="font-bold text-slate-900 border-b border-slate-200 pb-1.5 flex items-center gap-2">
                  <Package className="h-4 w-4 text-teal-600" />
                  Product & Batch Identification
                </h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 bg-white p-3 rounded-xl border border-slate-200/80">
                  <div>
                    <span className="text-slate-400 block text-[11px]">Product Name</span>
                    <span className="font-bold text-slate-900">{selectedComplaint.product_name || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Product Code / SKU</span>
                    <span className="font-mono text-slate-800">{selectedComplaint.product_code || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Batch / Lot Number</span>
                    <span className="font-mono font-bold text-teal-700">
                      {selectedComplaint.batch_number || 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Dosage Form & Strength</span>
                    <span className="text-slate-800">
                      {selectedComplaint.dosage_form || 'N/A'}{' '}
                      {selectedComplaint.product_strength ? `(${selectedComplaint.product_strength})` : ''}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[11px]">Affected Quantity</span>
                    <span className="text-slate-800 font-semibold">
                      {selectedComplaint.affected_quantity} {selectedComplaint.affected_quantity_unit}
                    </span>
                  </div>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <h4 className="font-bold text-slate-900 border-b border-slate-200 pb-1.5 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-teal-600" />
                  Detailed Problem Description
                </h4>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-slate-700 leading-relaxed font-sans whitespace-pre-wrap">
                  {selectedComplaint.description || 'No detailed description provided.'}
                </div>
              </div>

              {/* Dates & Customer Details */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {/* Dates */}
                <div className="space-y-2">
                  <h4 className="font-bold text-slate-900 border-b border-slate-200 pb-1.5 flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-teal-600" />
                    Important Timestamps
                  </h4>
                  <div className="space-y-1.5 p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Incident Date:</span>
                      <span className="font-semibold">{selectedComplaint.incident_date || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Mfg Date:</span>
                      <span className="font-semibold">{selectedComplaint.manufacturing_date || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Expiry Date:</span>
                      <span className="font-semibold">{selectedComplaint.expiry_date || 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Customer Details */}
                <div className="space-y-2">
                  <h4 className="font-bold text-slate-900 border-b border-slate-200 pb-1.5 flex items-center gap-2">
                    <User className="h-4 w-4 text-teal-600" />
                    Customer & Source Info
                  </h4>
                  <div className="space-y-1.5 p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Customer Name:</span>
                      <span className="font-semibold">{selectedComplaint.customer_name || 'Anonymous'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Source Type:</span>
                      <span className="font-semibold">{selectedComplaint.complaint_source || 'Pharmacy'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Email:</span>
                      <span className="font-mono text-slate-700">{selectedComplaint.customer_contact_email || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Phone:</span>
                      <span className="font-mono text-slate-700">{selectedComplaint.customer_contact_phone || 'N/A'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="px-6 py-3 bg-slate-50 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => setSelectedComplaint(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-slate-900 text-white hover:bg-slate-800 transition-colors cursor-pointer"
              >
                Close Window
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
