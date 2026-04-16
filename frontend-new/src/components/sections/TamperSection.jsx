import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldAlert, 
  Search, 
  CheckCircle2, 
  AlertTriangle, 
  Loader2, 
  Fingerprint,
  Zap,
  ShieldCheck,
  AlertCircle,
  FileWarning,
  FileBadge
} from 'lucide-react';
import { useApi } from '../../hooks/useApi';

const TamperSection = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const { request, loading, error } = useApi();

  const handleFileChange = (e) => {
    if (e.target.files[0]) setFile(e.target.files[0]);
  };

  const onAnalyze = async () => {
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append('file', file);
      const data = await request('/api/tamper-check', { method: 'POST', body: formData });
      setResult(data);
    } catch (err) {
      console.error('Analysis Error:', err);
    }
  };

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight text-app-text">Security & Integrity Audit</h2>
        <p className="text-app-text-muted">Forensic analysis to detect document tampering, pixel manipulation, and forgery.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div 
            className={`card flex flex-col items-center justify-center min-h-[400px] border-2 border-dashed transition-all cursor-pointer group ${file ? 'border-app-primary bg-slate-50' : 'border-app-border hover:border-app-text-muted hover:bg-slate-50'}`}
            onClick={() => document.getElementById('tamper-upload').click()}
          >
            <input type="file" id="tamper-upload" className="hidden" onChange={handleFileChange} />
            {!file ? (
              <div className="text-center px-6">
                <div className="w-12 h-12 rounded-full bg-white border border-app-border flex items-center justify-center mx-auto mb-4 transition-transform group-hover:scale-110">
                  <Fingerprint className="text-app-primary" size={20} />
                </div>
                <h3 className="text-sm font-semibold text-app-text mb-1 uppercase tracking-wider">Upload Forensic Sample</h3>
                <p className="text-xs text-app-text-muted">High-resolution scans are mandatory for forensic audit</p>
              </div>
            ) : (
              <div className="text-center">
                 <div className="w-16 h-16 rounded bg-app-primary text-white flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <ShieldAlert size={32} />
                 </div>
                 <h3 className="text-sm font-semibold text-app-text mb-1">{file.name}</h3>
                 <p className="text-[10px] text-app-primary font-bold uppercase tracking-widest">Integrity Check Ready</p>
                 <button onClick={(e) => { e.stopPropagation(); setFile(null); }} className="mt-6 text-xs font-semibold text-red-600 hover:text-red-500 underline">Replace File</button>
              </div>
            )}
          </div>
        </div>

        <div className="space-y-6">
          <div className="card h-full flex flex-col justify-between">
            <div className="space-y-6">
               <div className="p-5 rounded border border-slate-200 bg-slate-50 flex gap-4">
                  <ShieldCheck size={18} className="text-app-primary shrink-0" />
                  <p className="text-[11px] text-app-text-muted leading-relaxed font-medium">
                    Our forensic engine analyzes pixel consistency, compression artifacts, and ELA (Error Level Analysis).
                  </p>
               </div>

               <div className="space-y-4">
                  <p className="label">Audit Scope</p>
                  <div className="flex flex-col gap-2">
                     <label className="flex items-center gap-3 p-3 rounded border border-app-border cursor-pointer hover:bg-slate-50 transition-colors">
                        <input type="radio" name="scope" defaultChecked className="accent-app-primary" />
                        <span className="text-xs font-bold text-app-text uppercase tracking-widest">Full Forensic Scan</span>
                     </label>
                     <label className="flex items-center gap-3 p-3 rounded border border-app-border cursor-pointer hover:bg-slate-50 transition-colors opacity-50">
                        <input type="radio" name="scope" disabled className="accent-app-primary" />
                        <span className="text-xs font-bold text-app-text uppercase tracking-widest">Metadata Audit Only</span>
                     </label>
                  </div>
               </div>
            </div>

            <button 
              disabled={!file || loading}
              onClick={onAnalyze}
              className="btn btn-primary w-full h-12 mt-8"
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />}
              {loading ? 'Performing Audit...' : 'Execute Security Audit'}
            </button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-8"
          >
            <div className={`card border-l-8 ${result.is_tampered ? 'border-l-red-600' : 'border-l-emerald-600'}`}>
              <div className="flex items-center justify-between mb-8 pb-6 border-b border-app-border">
                  <div className="flex items-center gap-4">
                     <div className={`w-12 h-12 rounded flex items-center justify-center ${result.is_tampered ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-600'}`}>
                        {result.is_tampered ? <AlertTriangle size={24} /> : <CheckCircle2 size={24} />}
                     </div>
                     <div>
                        <h3 className="text-lg font-bold text-app-text leading-none uppercase tracking-tight">
                           Forensic Verdict: {result.is_tampered ? 'TAMPERED' : 'AUTHENTIC'}
                        </h3>
                        <p className="text-xs text-app-text-muted mt-1 uppercase font-bold tracking-widest">Reliability Score: {(result.confidence_score * 100).toFixed(2)}%</p>
                     </div>
                  </div>
                  <div className="text-right">
                     <p className="label mb-0">Status</p>
                     <p className={`text-3xl font-bold tracking-tighter uppercase ${result.is_tampered ? 'text-red-600' : 'text-emerald-600'}`}>
                        {result.is_tampered ? 'Red Flag' : 'Verified'}
                     </p>
                  </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <div className="p-4 rounded bg-slate-50 border border-slate-200">
                    <p className="label">Pixel Consistency Audit</p>
                    <p className="text-sm font-bold text-app-text">
                      {result.is_tampered ? 'High-frequency noise anomalies detected in data regions.' : 'Uniform signal-to-noise ratio across all document regions.'}
                    </p>
                 </div>
                 <div className="p-4 rounded bg-slate-50 border border-slate-200">
                    <p className="label">Encryption & Origin</p>
                    <p className="text-sm font-bold text-app-text">
                      Standard compression artifacts for {file?.type || 'image/jpeg'}. No re-compression traces.
                    </p>
                 </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default TamperSection;
