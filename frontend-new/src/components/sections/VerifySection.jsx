import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  CheckCircle2, 
  XCircle, 
  AlertCircle, 
  Loader2, 
  Search, 
  ClipboardCheck, 
  FileCheck,
  Zap,
  ShieldCheck,
  ArrowRight,
  Database,
  FileBadge
} from 'lucide-react';
import { useApi } from '../../hooks/useApi';

const VerifySection = () => {
  const [extractionId, setExtractionId] = useState('');
  const [formData, setFormData] = useState({
    full_name: '',
    document_number: '',
    date_of_birth: ''
  });
  const [result, setResult] = useState(null);
  const { request, loading, error } = useApi();

  const onVerify = async () => {
    if (!extractionId) return;
    try {
      const data = await request('/api/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ extraction_id: extractionId, form_data: formData })
      });
      setResult(data);
    } catch (err) {
      console.error('Reconciliation Error:', err);
    }
  };

  return (
    <div className="space-y-10">
      <div className="flex flex-col gap-1">
        <h2 className="text-3xl font-bold tracking-tight text-app-text">Record Reconciliation Service</h2>
        <p className="text-app-text-muted">Final verification stage of matching physical document data with institutional records.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <div className="card space-y-10 shadow-lg">
            <div className="space-y-4">
               <div>
                  <label className="label">Verification Reference / Extraction ID</label>
                  <input 
                    type="text" 
                    placeholder="Enter the unique Extraction ID"
                    value={extractionId} 
                    onChange={(e) => setExtractionId(e.target.value)}
                    className="input font-mono"
                  />
               </div>
            </div>

            <div className="pt-10 border-t border-slate-100 grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <label className="label">Applicant Full Name</label>
                <input 
                  type="text" 
                  value={formData.full_name} 
                  onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                  className="input"
                />
              </div>
              <div>
                <label className="label">Reference / Document Number</label>
                <input 
                  type="text" 
                  value={formData.document_number} 
                  onChange={(e) => setFormData({...formData, document_number: e.target.value})}
                  className="input"
                />
              </div>
              <div>
                <label className="label">Date of Birth (YYYY-MM-DD)</label>
                <input 
                  type="text" 
                  placeholder="e.g. 1990-01-01"
                  value={formData.date_of_birth} 
                  onChange={(e) => setFormData({...formData, date_of_birth: e.target.value})}
                  className="input"
                />
              </div>
            </div>

            <button 
              disabled={!extractionId || loading}
              onClick={onVerify}
              className="btn btn-primary h-14 w-full mt-6 shadow-xl text-base"
            >
              {loading ? <Loader2 className="animate-spin" size={20} /> : <ClipboardCheck size={20} />}
              {loading ? 'Reconciling Data...' : 'Finalize Reconciliation Audit'}
            </button>
          </div>
        </div>

        <div className="space-y-6">
           <div className="card bg-slate-50 border-dashed border-2 flex flex-col gap-6">
              <div className="flex items-center gap-3 text-app-primary">
                 <ShieldCheck size={24} />
                 <h4 className="text-sm font-bold uppercase tracking-widest">Audit Protocol</h4>
              </div>
              <p className="text-xs text-app-text-muted leading-relaxed font-medium">
                 This reconciliation step is mandatory for all high-value identity verifications. 
                 <br/><br/>
                 Mismatch in any of the core fields will result in the suspension of the digital certificate until manual review.
              </p>
              
              <div className="p-4 rounded border border-slate-200 bg-white shadow-sm">
                 <div className="flex items-center gap-2 mb-2">
                    <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">System Status</span>
                 </div>
                 <p className="text-[11px] font-bold text-slate-800">Connection to UIDAI / NSDL Stable</p>
              </div>
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
            <div className={`card border-l-8 shadow-2xl ${result.overall_match ? 'border-l-emerald-600' : 'border-l-red-600'}`}>
              <div className="flex items-center justify-between mb-8 pb-6 border-b border-slate-100">
                  <div className="flex items-center gap-4">
                     <div className={`w-12 h-12 rounded flex items-center justify-center ${result.overall_match ? 'bg-emerald-50 text-emerald-600' : 'bg-red-50 text-red-600'}`}>
                        {result.overall_match ? <FileCheck size={26} /> : <AlertCircle size={26} />}
                     </div>
                     <div>
                        <h3 className="text-lg font-bold text-app-text leading-none uppercase tracking-tight">Reconciliation Audit Report</h3>
                        <p className="text-xs text-app-text-muted mt-1 font-bold tracking-widest uppercase">Verified via Digital Audit Engine</p>
                     </div>
                  </div>
                  <div className="text-right">
                     <p className="label mb-0">Verdict</p>
                     <p className={`text-3xl font-bold tracking-tighter uppercase ${result.overall_match ? 'text-emerald-600' : 'text-red-600'}`}>
                        {result.overall_match ? 'Match Verified' : 'Discrepancy Found'}
                     </p>
                  </div>
              </div>

              <div className="space-y-4">
                {Object.entries(result.field_matches).map(([key, match]) => (
                  <div key={key} className="flex items-center justify-between p-5 rounded border border-slate-100 bg-slate-50/50">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-[0.15em]">{key.replace(/_/g, ' ')}</span>
                    <div className="flex items-center gap-6">
                       <div className="text-right">
                          <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Submitted Value</p>
                          <span className="text-sm font-bold text-app-text">{match.submitted_value}</span>
                       </div>
                       <ArrowRight size={16} className="text-slate-300" />
                       <div className={`flex items-center gap-2 px-4 py-2 rounded font-bold text-[11px] tracking-widest border ${match.is_match ? 'bg-emerald-50 text-emerald-700 border-emerald-100' : 'bg-red-50 text-red-700 border-red-100'}`}>
                          {match.is_match ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                          {match.is_match ? 'VERIFIED' : 'MISMATCH'}
                       </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default VerifySection;
