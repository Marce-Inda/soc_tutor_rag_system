'use client'

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Database, Search, FileText, Copy, Check } from 'lucide-react';

interface EvidenceEntry {
  id: string;
  type: string;
  query_kql: string;
  data: any;
  is_malicious: boolean;
}

interface SiemTableProps {
  results: EvidenceEntry[];
  query: string;
}

export default function SiemTable({ results, query }: SiemTableProps) {
  const [copied, setCopied] = React.useState(false);
  const [isScanning, setIsScanning] = React.useState(true);

  React.useEffect(() => {
    const timer = setTimeout(() => setIsScanning(false), 1500);
    return () => clearTimeout(timer);
  }, [results]);

  if (!results || results.length === 0) return null;

  const copyToClipboard = () => {
    navigator.clipboard.writeText(query || results[0].query_kql);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const toolType = results[0].type || 'LOG_ANALYZER';
  const categoryLabel = toolType === 'NetworkScan' ? 'NDR / NETWORK TELEMETRY' : 'SIEM / AUDIT LOGS';
  const categoryColor = toolType === 'NetworkScan' ? 'border-secondary/40 bg-secondary/10 text-secondary' : 'border-primary/40 bg-primary/10 text-primary';
  const tableName = toolType === 'NetworkScan' ? 'NetworkConnections' : 'SecurityEvent';

  const columns = Object.keys(results[0].data);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="mt-6 border border-primary/30 bg-black/60 rounded-lg overflow-hidden flex flex-col shadow-[0_0_40px_rgba(34,211,238,0.1)] relative"
    >
      {/* Scanning Overlay Animation */}
      <AnimatePresence>
        {isScanning && (
          <motion.div 
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-20 bg-primary/5 pointer-events-none flex items-center justify-center"
          >
             <motion.div 
               animate={{ top: ['0%', '100%'] }}
               transition={{ repeat: Infinity, duration: 0.8, ease: "linear" }}
               className="absolute left-0 w-full h-[2px] bg-primary/40 shadow-[0_0_15px_#22d3ee]"
             />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Query Header */}
      <div className="bg-primary/10 border-b border-primary/20 p-3 flex items-center justify-between group/header relative z-10">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-2 py-1 bg-black/60 rounded border border-primary/30 shadow-inner">
            <Search size={10} className="text-primary" />
            <span className="text-[9px] font-black font-mono text-primary tracking-widest uppercase">KQL Query</span>
          </div>
          <div className="relative flex items-center gap-3">
            <code className="text-[11px] font-mono text-secondary/90 truncate max-w-[400px] bg-black/40 px-3 py-1 rounded border border-white/5">
              {query || results[0].query_kql}
            </code>
            <button 
              onClick={copyToClipboard}
              className="p-1.5 rounded bg-primary/10 border border-primary/30 hover:bg-primary/20 text-primary transition-all active:scale-95 group/copy"
              title="Copy Query"
            >
              {copied ? <Check size={12} className="text-success" /> : <Copy size={12} className="group-hover:rotate-12 transition-transform" />}
            </button>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-[10px] font-mono text-muted-foreground/60 hidden md:block">Table: {tableName}</span>
          <div className={`px-3 py-1 rounded-sm border text-[9px] font-black tracking-widest uppercase shadow-[0_0_15px_rgba(0,0,0,0.4)] ${categoryColor}`}>
             {categoryLabel}
          </div>
        </div>
      </div>

      {/* Table Body */}
      <div className="overflow-x-auto custom-scrollbar relative z-10">
        <table className="w-full text-left border-collapse min-w-[600px]">
          <thead>
            <tr className="bg-primary/5 border-b border-primary/20">
              <th className="px-4 py-3 text-[9px] font-black uppercase text-primary/60 tracking-widest w-10">#</th>
              {columns.map((col) => (
                <th key={col} className="px-4 py-3 text-[9px] font-black uppercase text-muted tracking-widest border-r border-primary/10 last:border-0">
                  {col.replace('_', ' ')}
                </th>
              ))}
              <th className="px-4 py-3 text-[9px] font-black uppercase text-primary/60 tracking-widest w-20 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {results.map((entry, idx) => (
              <motion.tr 
                key={entry.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.05 + 0.5 }}
                className={`group hover:bg-primary/10 transition-all border-b border-primary/5 last:border-0 cursor-pointer ${entry.is_malicious ? 'bg-danger/5' : ''}`}
              >
                <td className="px-4 py-3 text-[10px] font-mono text-muted/50 border-r border-primary/5">
                  {String(idx + 1).padStart(2, '0')}
                </td>
                {columns.map((col) => (
                  <td key={col} className="px-4 py-3 text-[10px] font-medium text-foreground/80 border-r border-primary/5 last:border-0 group-hover:text-primary transition-colors">
                    <span className="truncate block max-w-[220px]">
                      {String(entry.data[col])}
                    </span>
                  </td>
                ))}
                <td className="px-4 py-3 text-center">
                   {entry.is_malicious ? (
                     <div className="flex items-center justify-center">
                       <span className="px-2 py-0.5 rounded-full bg-danger/20 border border-danger/40 text-[8px] font-black text-danger uppercase animate-pulse">Malicious</span>
                     </div>
                   ) : (
                     <div className="flex items-center justify-center">
                       <span className="px-2 py-0.5 rounded-full bg-success/10 border border-success/30 text-[8px] font-black text-success/60 uppercase">Normal</span>
                     </div>
                   )}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Footer Status */}
      <div className="bg-black/40 p-2 border-t border-primary/20 flex justify-between items-center px-4 relative z-10">
        <div className="flex items-center gap-3">
          <Database size={10} className="text-primary/60" />
          <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest">
            Records: <span className="text-primary">{results.length}</span> | 
            Provider: <span className="text-foreground/70">{toolType === 'NetworkScan' ? 'Falcon NDR Engine' : 'Microsoft Sentinel Workspace'}</span>
          </span>
        </div>
        <div className="flex items-center gap-4">
           <div className="flex items-center gap-1.5">
              <div className="h-1.5 w-1.5 rounded-full bg-success shadow-[0_0_8px_#10b981]" />
              <span className="text-[8px] text-success font-black uppercase tracking-widest">Integrity Verified</span>
           </div>
        </div>
      </div>
    </motion.div>
  );
}
