import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FileSearch, 
  Upload as UploadIcon, 
  CheckCircle2, 
  Loader2, 
  Info, 
  Layers, 
  Database,
  Search,
  ArrowRight,
  Cpu,
  FileText,
  ShieldCheck,
  Zap,
  Check,
  AlertCircle,
  Hash
} from 'lucide-react';
import { useApi } from '../../hooks/useApi';

const ExtractSection = () => {
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState('auto');
  const [result, setResult] = useState(null);
  const { request, loading, error } = useApi();

  const handleFileChange = (e) => {
    if (e.target.files[0]) setFile(e.target.files[0]);
  };

  const onExtract = async () => {
    if (!file) return;
    try {
      const formData = new FormData();
      formData.append('file', file);
      const data = await request(`/api/extract?document_type=${docType}`, {
        method: 'POST',
        body: formData
      });
      setResult(data);
    } catch (err) {
      console.error('Extraction Error:', err);
    }
  };

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight text-app-text">E-Extraction Service</h2>
        <p className="text-app-text-muted">Upload identity documents for automated digital extraction and verification.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Column */}
        <div className="lg:col-span-2 space-y-6">
          <div 
            className={`card flex flex-col items-center justify-center min-h-[400px] border-2 border-dashed transition-all cursor-pointer group ${file ? 'border-app-primary bg-app-primary/5' : 'border-app-border hover:border-app-text-muted'}`}
            onClick={() => document.getElementById('file-upload').click()}
          >
            <input type="file" id="file-upload" className="hidden" onChange={handleFileChange} />
            
            {!file ? (
              <div className="text-center px-6">
                <div className="w-12 h-12 rounded-full bg-app-surface border border-app-border flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <UploadIcon className="text-app-primary" size={20} />
                </div>
                <h3 className="text-sm font-semibold text-white mb-1">Upload Identity Document</h3>
                <p className="text-xs text-app-text-muted">PDF, JPG, or PNG up to 20MB</p>
              </div>
            ) : (
              <div className="text-center px-6">
                <div className="w-16 h-16 rounded-xl bg-app-primary/10 border border-app-primary/20 flex items-center justify-center mx-auto mb-4">
                  <FileText className="text-app-primary" size={32} />
                </div>
                <h3 className="text-sm font-semibold text-white mb-1">{file.name}</h3>
                <p className="text-[10px] text-app-primary font-bold uppercase tracking-widest">Document Ready</p>
                <button 
                  onClick={(e) => { e.stopPropagation(); setFile(null); }} 
                  className="mt-6 text-xs font-semibold text-red-500 hover:text-red-400"
                >
                  Remove file
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Config Column */}
        <div className="space-y-6">
          <div className="card h-full flex flex-col justify-between">
            <div className="space-y-6">
              <div>
                <label className="label">Document Type</label>
                <select 
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="input cursor-pointer"
                >
                  <option value="auto">Auto-Detect Type</option>
                  <option value="aadhaar">Aadhaar Card (UIDAI)</option>
                  <option value="pan_card">PAN Card (Income Tax Dept)</option>
                  <option value="voter_id">Voter ID (ECI)</option>
                  <option value="passport">Indian Passport</option>
                  <option value="driving_license">Driving License</option>
                  <option value="id_card">Other National ID</option>
                </select>
              </div>
              
              <div className="p-4 rounded-lg bg-white/5 border border-app-border flex gap-4">
                 <ShieldCheck size={18} className="text-app-primary shrink-0" />
                 <p className="text-[11px] text-app-text-muted leading-relaxed">
                   Privacy first: documents are processed in-memory and deleted immediately after extraction.
                 </p>
              </div>
            </div>

            <button 
              disabled={!file || loading}
              onClick={onExtract}
              className={`btn btn-primary w-full h-12 mt-8 ${!file && 'opacity-30'}`}
            >
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Check size={18} />}
              {loading ? 'Processing...' : 'Run Extraction'}
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
            <div className="card">
              <div className="flex items-center justify-between mb-8 pb-6 border-b border-app-border">
                <div className="flex items-center gap-4">
                   <div className="w-10 h-10 rounded bg-app-primary flex items-center justify-center text-white">
                      <FileSearch size={22} />
                   </div>
                   <div>
                      <h3 className="text-lg font-bold text-app-text leading-none uppercase tracking-tight">Official Record Extracted</h3>
                      <p className="text-xs text-app-text-muted mt-1 font-mono">ID: {result.extraction_id.toUpperCase()}</p>
                   </div>
                </div>
                <div className="text-right">
                   <p className="label mb-0">Extraction Confidence</p>
                   <p className="text-3xl font-bold text-app-primary tracking-tighter">
                      {Math.round(result.overall_confidence * 100)}<span className="text-app-accent">%</span>
                   </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(result.fields).map(([key, field]) => (
                  <div key={key} className="p-4 rounded-lg bg-app-bg border border-app-border flex flex-col gap-2">
                    <div className="flex justify-between items-center">
                        <span className="text-[10px] font-bold text-app-text-muted uppercase tracking-widest">
                           {key.replace(/_/g, ' ')}
                        </span>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${field.confidence > 0.8 ? 'bg-green-500/10 text-green-500' : 'bg-amber-500/10 text-amber-500'}`}>
                           {Math.round(field.confidence * 100)}%
                        </span>
                    </div>
                    <p className="text-sm font-medium text-white truncate">
                        {field.value === 'NOT_FOUND' ? <span className="opacity-30">Null</span> : field.value}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pb-20">
               <div className="card bg-white/5">
                  <p className="label">Processing time</p>
                  <p className="text-xl font-bold">{(result.processing_time || 0.45).toFixed(2)}s</p>
               </div>
               <div className="card bg-white/5">
                  <p className="label">Provider status</p>
                  <p className="text-xl font-bold text-green-500 flex items-center gap-2">
                     <CheckCircle2 size={18} /> Stable
                  </p>
               </div>
               <div className="card bg-white/5">
                  <p className="label">Verification</p>
                  <p className="text-xl font-bold flex items-center gap-2">
                     <AlertCircle size={18} className="text-amber-500" /> Pending
                  </p>
               </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ExtractSection;



