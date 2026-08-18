import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Sparkles, RefreshCw, Activity, PlusCircle, ClipboardList } from 'lucide-react';
import { clearForm } from '../store/slices/complaintSlice';
import { resetChatSession, initChatSessionThunk } from '../store/slices/chatSlice';
import { setActiveView } from '../store/slices/appSlice';

export default function Navbar() {
  const dispatch = useDispatch();
  const { activeChatId } = useSelector((state) => state.chat);
  const activeView = useSelector((state) => state.app?.activeView || 'form');

  const handleResetSession = () => {
    dispatch(clearForm());
    dispatch(resetChatSession());
    dispatch(initChatSessionThunk());
    dispatch(setActiveView('form'));
  };

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-slate-200/80 shadow-xs px-4 lg:px-8 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* Brand & System Title */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-teal-600 to-teal-400 flex items-center justify-center shadow-md shadow-teal-500/20 text-white shrink-0">
            <Sparkles className="h-5.5 w-5.5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-bold tracking-tight text-slate-900">CCMS Copilot</h1>
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-teal-50 text-teal-700 border border-teal-200">
                AI-First
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium hidden sm:block">
              Pharmaceutical Complaint & Quality Intake Engine
            </p>
          </div>
        </div>

        {/* Central Navigation Tabs */}
        <nav className="flex items-center p-1 bg-slate-100/80 rounded-xl border border-slate-200/80">
          <button
            onClick={() => dispatch(setActiveView('form'))}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeView === 'form'
                ? 'bg-white text-teal-700 shadow-xs border border-slate-200/60'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            <PlusCircle className={`h-4 w-4 ${activeView === 'form' ? 'text-teal-600' : 'text-slate-500'}`} />
            <span>Intake Form</span>
          </button>

          <button
            onClick={() => dispatch(setActiveView('list'))}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              activeView === 'list'
                ? 'bg-white text-teal-700 shadow-xs border border-slate-200/60'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/50'
            }`}
          >
            <ClipboardList className={`h-4 w-4 ${activeView === 'list' ? 'text-teal-600' : 'text-slate-500'}`} />
            <span>All Complaints</span>
          </button>
        </nav>

        {/* System Status & Actions */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 font-medium">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <Activity className="h-3.5 w-3.5 text-teal-600" />
            Backend Connected
            {activeChatId && <span className="text-slate-400">• Session #{activeChatId}</span>}
          </div>

          <button
            onClick={handleResetSession}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors cursor-pointer border border-slate-200"
            title="Start new fresh complaint session"
          >
            <RefreshCw className="h-3.5 w-3.5 text-slate-500" />
            <span className="hidden sm:inline">New Session</span>
          </button>
        </div>
      </div>
    </header>
  );
}
