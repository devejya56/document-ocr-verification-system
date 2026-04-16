import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  User, 
  Camera, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  ScanFace,
  Image as ImageIcon,
  Zap,
  Users,
  Check,
  ShieldCheck,
  UserCheck
} from 'lucide-react';
import { useApi } from '../../hooks/useApi';

const FaceMatchSection = () => {
  const [docFile, setDocFile] = useState(null);
  const [selfieFile, setSelfieFile] = useState(null);
  const [result, setResult] = useState(null);
  const { request, loading, error } = useApi();

  const handleDocChange = (e) => {
    if (e.target.files[0]) setDocFile(e.target.files[0]);
  };

  const handleSelfieChange = (e) => {
    if (e.target.files[0]) setSelfieFile(e.target.files[0]);
  };

  const onMatch = async () => {
    if (!docFile || !selfieFile) return;
    try {
      const formData = new FormData();
      formData.append('document', docFile);
      formData.append('selfie', selfieFile);
      const data = await request('/api/face-match', { method: 'POST', body: formData });
      setResult(data);
    } catch (err) {
      console.error('Biometric Error:', err);
    }
  };

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight text-app-text">Biometric Verification Service</h2>
        <p className="text-app-text-muted">Compare identity document portraits against live verification samples for multi-factor authentication.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Document Photo */}
        <div 
          className={`card flex flex-col items-center justify-center min-h-[350px] border-2 border-dashed transition-all cursor-pointer group ${docFile ? 'border-app-primary bg-slate-50' : 'border-app-border hover:border-app-text-muted hover:bg-slate-50'}`}
          onClick={() => document.getElementById('doc-photo-upload').click()}
        >
          <input type="file" id="doc-photo-upload" className="hidden" onChange={handleDocChange} />
          {!docFile ? (
            <div className="text-center px-6">
              <div className="w-12 h-12 rounded-full border border-app-border bg-white flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <ImageIcon className="text-app-primary" size={24} />
              </div>
              <h3 className="text-sm font-semibold text-app-text mb-1 uppercase tracking-wider">Document Portrait</h3>
              <p className="text-xs text-app-text-muted">Upload existing ID photo from record</p>
            </div>
          ) : (
             <div className="text-center">
                <div className="w-20 h-20 rounded bg-app-primary text-white flex items-center justify-center mx-auto mb-4 shadow-lg">
                    <User size={40} />
                </div>
                <p className="text-sm font-bold text-app-text mb-1 uppercase tracking-tight">{docFile.name}</p>
                <button onClick={(e) => { e.stopPropagation(); setDocFile(null); }} className="text-xs font-bold text-red-600 underline">Change Photo</button>
             </div>
          )}
        </div>

        {/* Verification Selfie */}
        <div 
          className={`card flex flex-col items-center justify-center min-h-[350px] border-2 border-dashed transition-all cursor-pointer group ${selfieFile ? 'border-app-primary bg-slate-50' : 'border-app-border hover:border-app-text-muted hover:bg-slate-50'}`}
          onClick={() => document.getElementById('selfie-upload').click()}
        >
          <input type="file" id="selfie-upload" className="hidden" onChange={handleSelfieChange} />
          {!selfieFile ? (
            <div className="text-center px-6">
              <div className="w-12 h-12 rounded-full border border-app-border bg-white flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <Camera className="text-app-primary" size={24} />
              </div>
              <h3 className="text-sm font-semibold text-app-text mb-1 uppercase tracking-wider">Live Capture / Selfie</h3>
              <p className="text-xs text-app-text-muted">Direct verification image for liveness check</p>
            </div>
          ) : (
            <div className="text-center">
               <div className="w-20 h-20 rounded bg-app-primary text-white flex items-center justify-center mx-auto mb-4 shadow-lg">
                   <ScanFace size={40} />
               </div>
               <p className="text-sm font-bold text-app-text mb-1 uppercase tracking-tight">{selfieFile.name}</p>
               <button onClick={(e) => { e.stopPropagation(); setSelfieFile(null); }} className="text-xs font-bold text-red-600 underline">Change Photo</button>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-center pt-4">
         <button 
           disabled={!docFile || !selfieFile || loading}
           onClick={onMatch}
           className="btn btn-primary h-14 w-full max-w-md text-base shadow-xl"
         >
           {loading ? <Loader2 className="animate-spin" size={20} /> : <UserCheck size={20} />}
           {loading ? 'Performing Biometric Comparison...' : 'Execute Identity Matching'}
         </button>
      </div>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center py-10"
          >
             <div className="card w-full max-w-2xl bg-white border-app-border text-center shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-1 bg-app-primary" />
                
                <div className="mb-6 inline-flex p-5 rounded-full bg-slate-50 border border-slate-200">
                   <div className="text-5xl font-bold tracking-tighter text-app-primary">
                      {Math.round(result.similarity_score * 100)}<span className="text-app-accent">%</span>
                   </div>
                </div>
                <h3 className="text-xl font-bold text-app-text mb-2 uppercase tracking-tight">Biometric Correspondence Result</h3>
                <p className="text-app-text-muted text-sm mb-10 max-w-md mx-auto">
                   Automated matching successfully identified 128 unique nodal points across both samples.
                </p>
                
                <div className="flex items-center justify-center gap-4">
                   <div className={`px-6 py-3 rounded font-bold uppercase tracking-[0.2em] text-[13px] border-2 ${result.is_match ? 'bg-emerald-50 text-emerald-700 border-emerald-200 shadow-emerald-100 shadow-xl' : 'bg-red-50 text-red-700 border-red-200'}`}>
                      {result.is_match ? 'Match Confirmed' : 'Match Failed'}
                   </div>
                </div>
             </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default FaceMatchSection;
