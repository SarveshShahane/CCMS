import React from 'react';
import { useSelector } from 'react-redux';
import Navbar from './components/Navbar';
import ComplaintForm from './components/ComplaintForm';
import CopilotPanel from './components/CopilotPanel';
import ComplaintsList from './components/ComplaintsList';

export default function App() {
  const activeView = useSelector((state) => state.app?.activeView || 'form');

  return (
    <div className="min-h-screen flex flex-col bg-slate-100 font-sans text-slate-900">
      {/* Navbar */}
      <Navbar />

      {/* View Switcher */}
      {activeView === 'list' ? (
        <main className="flex-1 w-full overflow-y-auto">
          <ComplaintsList />
        </main>
      ) : (
        /* Dual Panel Intake Layout */
        <main className="flex-1 max-w-7xl w-full mx-auto p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden min-h-0">
          {/* Left Side: Complaint Form */}
          <section className="lg:col-span-7 h-[calc(100vh-100px)] min-h-[650px]">
            <ComplaintForm />
          </section>

          {/* Right Side: Copilot AI Chat Panel */}
          <section className="lg:col-span-5 h-[calc(100vh-100px)] min-h-[650px]">
            <CopilotPanel />
          </section>
        </main>
      )}
    </div>
  );
}
