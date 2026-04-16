import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileSearch, 
  ShieldAlert, 
  UserCheck, 
  ClipboardCheck, 
  Server, 
  History,
  Activity,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

const VaultLayout = ({ children, activeSection, setActiveSection, user }) => {
  const navItems = [
    { id: 'extract', label: 'Extraction', icon: FileSearch },
    { id: 'tamper', label: 'Forensics', icon: ShieldAlert },
    { id: 'face', label: 'Biometrics', icon: UserCheck },
    { id: 'verify', label: 'Cross-Ref', icon: ClipboardCheck },
  ];

  return (
    <div className="flex h-screen w-full bg-vault-bg text-vault-text overflow-hidden">
      {/* Left Pane: Archive Explorer (Collapsible) */}
      <aside className="w-64 border-r border-vault-border flex flex-col bg-vault-bg z-30">
        <div className="h-16 flex items-center px-6 border-b border-vault-border">
          <div className="w-6 h-6 bg-vault-accent rounded flex items-center justify-center mr-3 shadow-[0_0_10px_rgba(212,175,55,0.3)]">
            <Server className="text-vault-bg" size={14} />
          </div>
          <span className="font-display font-bold text-lg tracking-tight">VAULT CORES</span>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="p-4">
             <div className="flex items-center gap-2 mb-4 px-2">
                <History size={14} className="text-vault-accent" />
                <span className="forensic-text">System Archive</span>
             </div>
             <div className="space-y-1">
                {[1, 2, 3].map(i => (
                  <div key={i} className="px-3 py-2 rounded text-[11px] text-vault-text-dim hover:bg-white/5 transition-colors cursor-pointer border border-transparent hover:border-vault-border group">
                    <p className="font-mono text-vault-text group-hover:text-vault-accent transition-colors">7f32-session-{i}</p>
                    <p className="opacity-50 mt-0.5">Detected: Aadhaar Card</p>
                  </div>
                ))}
             </div>
          </div>
        </div>

        <div className="p-4 border-t border-vault-border bg-black/20">
            <div className="flex items-center justify-between mb-3 px-2">
                <span className="forensic-text text-white/50">Core Ops</span>
                <Activity size={12} className="text-gov-saffron animate-pulse" />
            </div>
            {navItems.map((item) => (
                <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded mb-1 transition-all text-xs ${activeSection === item.id ? 'bg-vault-accent text-vault-bg font-bold' : 'text-vault-text-dim hover:text-white hover:bg-white/5'}`}
                >
                <item.icon size={14} />
                <span>{item.label}</span>
                </button>
            ))}
        </div>
      </aside>

      {/* Center Pane: The Interaction Stage */}
      <section className="flex-1 flex flex-col min-w-0 bg-[#0d110f] relative overflow-hidden">
        {/* Subtle Background Markings */}
        <div className="absolute inset-0 guilloche-pattern opacity-10 pointer-events-none" />
        <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-vault-accent/20 to-transparent" />
        
        <header className="h-16 flex items-center justify-between px-8 z-10 bg-vault-bg/60 backdrop-blur border-b border-vault-border">
          <div className="flex items-center gap-4">
             <span className="forensic-text opacity-30">Security Terminal</span>
             <ChevronRight size={10} className="text-vault-accent" />
             <h2 className="font-display text-xl font-bold tracking-tight text-white capitalize">
                {activeSection.replace('-', ' ')}
             </h2>
          </div>
          <div className="flex items-center gap-6">
             <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-gov-saffron" />
                <span className="forensic-text">Active Link</span>
             </div>
             {user && (
                <div className="text-[11px] font-mono text-vault-accent border-l border-vault-border pl-6 flex items-center gap-2">
                    <span className="opacity-50">Auth:</span> {user.username}
                </div>
             )}
          </div>
        </header>

        <div className="flex-1 relative overflow-y-auto p-12 custom-scrollbar">
           <div className="max-w-4xl mx-auto w-full relative z-10">
              {children}
           </div>
        </div>
      </section>

      {/* Right Pane: Intel Deck (High Density Info) */}
      <aside className="w-80 border-l border-vault-border flex flex-col bg-vault-bg z-30">
        <div className="h-16 flex items-center px-6 border-b border-vault-border">
          <span className="forensic-text">Intelligence Deck</span>
        </div>
        
        <div className="flex-1 p-6 space-y-8 overflow-y-auto text-[11px]">
           <div>
              <p className="forensic-text mb-4 text-vault-accent/60">Live Metadata</p>
              <div className="space-y-2 font-mono text-vault-text-dim">
                 <div className="flex justify-between border-b border-vault-border pb-1"><span>Target:</span> <span>Unassigned</span></div>
                 <div className="flex justify-between border-b border-vault-border pb-1"><span>Format:</span> <span>—</span></div>
                 <div className="flex justify-between border-b border-vault-border pb-1"><span>Size:</span> <span>—</span></div>
              </div>
           </div>

           <div className="bg-black/40 p-4 rounded-lg etched-border">
              <p className="forensic-text mb-3 text-red-500/80">Anomaly Alerts</p>
              <p className="text-vault-text-dim italic leading-relaxed">No pending alerts. System monitoring active at full capacity.</p>
           </div>

           <div className="space-y-4">
              <p className="forensic-text mb-2 text-vault-accent/60">Neural Engine Status</p>
              <div className="space-y-3">
                 {['OCR Engine', 'Forensic ELA', 'Facial Recognition'].map(proc => (
                    <div key={proc} className="flex items-center gap-3">
                       <div className="w-full h-1 bg-white/5 rounded-full overflow-hidden">
                          <motion.div 
                            initial={{ width: 0 }}
                            animate={{ width: '92%' }}
                            className="h-full bg-vault-accent"
                          />
                       </div>
                       <span className="opacity-50 min-w-[30px]">92%</span>
                    </div>
                 ))}
              </div>
           </div>
        </div>
        
        <div className="p-6 border-t border-vault-border">
           <button className="w-full py-3 bg-white/5 hover:bg-white/10 etched-border rounded text-[10px] font-bold uppercase tracking-widest transition-all">
              Initialize Self-Audit
           </button>
        </div>
      </aside>
    </div>
  );
};

export default VaultLayout;
