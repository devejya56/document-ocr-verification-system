import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileSearch, 
  ShieldCheck, 
  User, 
  Activity, 
  ShieldAlert, 
  Cpu,
  ChevronRight,
  ExternalLink,
  Info,
  Globe
} from 'lucide-react';

const VantageLayout = ({ children, activeSection, setActiveSection, user }) => {
  const navItems = [
    { id: 'extract', label: 'E-Extraction Service', icon: FileSearch },
    { id: 'tamper', label: 'Security & Integrity Audit', icon: ShieldAlert },
    { id: 'face', label: 'Biometric Verification', icon: Cpu },
    { id: 'verify', label: 'Record Reconciliation', icon: Activity },
  ];

  return (
    <div className="h-screen flex flex-col bg-app-bg text-app-text antialiased font-sans">
      {/* Official Government Bar */}
      <div className="tricolour-bar">
        <div className="tricolour-saffron" />
        <div className="tricolour-white" />
        <div className="tricolour-green" />
      </div>

      {/* Main Header */}
      <header className="h-20 border-b border-app-border bg-app-primary flex items-center justify-between px-10 z-50 text-white shadow-md">
        <div className="flex items-center gap-12">
          <div className="flex flex-col">
            <h1 className="text-xl font-serif font-bold tracking-tight leading-tight">
              Government of India
            </h1>
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-white/70">
              Department of National Identity Services
            </p>
          </div>
          <div className="h-10 w-px bg-white/20 hidden lg:block" />
          <div className="hidden lg:block">
            <h2 className="text-lg font-serif font-medium opacity-90 leading-none">Online Document Verification Service</h2>
            <p className="text-[10px] uppercase font-bold tracking-widest mt-1 opacity-50">Ministry of Electronics & IT</p>
          </div>
        </div>

        <div className="flex items-center gap-8">
           <div className="hidden xl:flex items-center gap-6 text-[11px] font-bold uppercase tracking-widest text-white/60">
              <span className="hover:text-white transition-colors cursor-pointer flex items-center gap-2 border-b border-transparent hover:border-white">
                India.gov.in <ExternalLink size={10} />
              </span>
              <span className="hover:text-white transition-colors cursor-pointer flex items-center gap-2 border-b border-transparent hover:border-white">
                Digital India <ExternalLink size={10} />
              </span>
           </div>
           
           <div className="h-8 w-px bg-white/10" />

           <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded bg-white/10 flex items-center justify-center border border-white/20">
                <User size={20} className="text-white" />
              </div>
              <div className="hidden sm:block">
                <p className="text-xs font-bold leading-none">Officer {user?.username || 'ADMIN'}</p>
                <p className="text-[9px] uppercase font-bold tracking-widest mt-1 opacity-50">Level 4 Clearance</p>
              </div>
           </div>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        {/* Navigation Sidebar */}
        <nav className="w-72 border-r border-app-border flex flex-col bg-white shadow-sm">
          <div className="p-6 border-b border-app-border bg-slate-50/50">
             <div className="flex items-center gap-3 text-app-primary">
                <Info size={16} />
                <span className="text-[10px] font-bold uppercase tracking-widest">Official Portal Section</span>
             </div>
          </div>

          <div className="flex-1 py-4 px-3 space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center justify-between px-5 py-4 rounded-md transition-all group ${activeSection === item.id ? 'bg-app-primary text-white shadow-lg shadow-app-primary/20' : 'text-slate-600 hover:text-app-primary hover:bg-slate-50'}`}
              >
                <div className="flex items-center gap-4">
                    <item.icon size={18} strokeWidth={2} />
                    <span className="text-[13px] font-bold tracking-wide">{item.label}</span>
                </div>
                {activeSection === item.id && <ChevronRight size={14} />}
              </button>
            ))}
          </div>
          
          <div className="p-8 m-4 rounded-lg bg-emerald-50 border border-emerald-100">
             <div className="flex items-center gap-3 text-emerald-700 mb-3">
                <ShieldCheck size={18} />
                <span className="text-[11px] font-bold tracking-widest uppercase">Safe & Secure</span>
             </div>
             <p className="text-[11px] text-emerald-600/80 leading-relaxed font-medium">
               This is a secure government portal. All data is encrypted using 256-bit AES protocol.
             </p>
          </div>

          <div className="p-6 border-t border-app-border text-center text-[9px] text-slate-400 font-bold uppercase tracking-[0.2em]">
             National Informatics Centre
          </div>
        </nav>

        {/* Main Workspace Area */}
        <main className="flex-1 flex flex-col overflow-hidden bg-app-bg relative">
          <div className="flex-1 overflow-y-auto p-12 custom-scrollbar">
             <div className="max-w-5xl mx-auto w-full">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeSection}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                  >
                    {children}
                  </motion.div>
                </AnimatePresence>
             </div>
          </div>
          
          {/* Subtle Footer Bar */}
          <footer className="h-12 border-t border-app-border bg-white px-10 flex items-center justify-between text-[10px] text-slate-500 font-bold uppercase tracking-widest">
             <div className="flex items-center gap-8">
                <span>Terms of Service</span>
                <span>Privacy Policy</span>
                <span>Accessibility</span>
             </div>
             <div className="flex items-center gap-4">
                <Globe size={14} className="text-app-primary" />
                <span>© 2026 Government of India</span>
             </div>
          </footer>
        </main>
      </div>
    </div>
  );
};

export default VantageLayout;


