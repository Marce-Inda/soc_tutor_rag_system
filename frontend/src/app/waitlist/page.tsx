'use client'

import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ShieldAlert, Loader2, Cpu, Zap, Eye, AlertCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { getQueueStatus, QueueStatus } from '@/utils/api';
import { audioSystem } from '@/utils/audio';
import { musicManager } from '@/utils/ambientAudio';

export default function WaitlistPage() {
  const router = useRouter();
  const [status, setStatus] = useState<QueueStatus | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Inicializar o recuperar UserID
    let savedId = localStorage.getItem('soc_tutor_user_id');
    if (!savedId) {
      savedId = `user_${Math.random().toString(36).substring(2, 9)}`;
      localStorage.setItem('soc_tutor_user_id', savedId);
    }
    setUserId(savedId);

    const checkStatus = async () => {
      try {
        const data = await getQueueStatus(savedId!);
        const prevStatus = status?.status;
        setStatus(data);
        
        if (data.status === 'ACTIVE') {
          audioSystem.playSuccess();
          router.push('/');
        } else if (data.status === 'WAITING' && prevStatus !== 'WAITING') {
          audioSystem.playAlert();
        }
      } catch (err) {
        setError('FALLA DE ENLACE CON EL SERVIDOR CENTRAL');
      }
    };

    checkStatus();
    musicManager.start(); // Iniciar ambiente (Submerged_Systems) por defecto
    const interval = setInterval(checkStatus, 5000);
    return () => {
      clearInterval(interval);
      musicManager.stopAll();
    };
  }, [router]);

  if (!status) {
    return (
      <div className="h-screen bg-black flex items-center justify-center font-mono">
        <div className="flex flex-col items-center gap-4 text-amber-500">
          <Loader2 className="animate-spin" size={48} />
          <span className="text-[10px] tracking-[0.5em] font-black uppercase">Enlazando con sistema NERV...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen bg-black text-amber-500 font-mono overflow-hidden relative flex flex-col items-center justify-center p-6 select-none">
      
      {/* DECORATIVE BACKGROUND (KANJI & LINES) */}
      <div className="absolute inset-0 opacity-10 pointer-events-none">
        <div className="absolute top-10 left-10 text-[100px] font-black">警告</div>
        <div className="absolute bottom-10 right-10 text-[100px] font-black">作戦</div>
        <div className="grid grid-cols-12 h-full w-full">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="border-r border-amber-500/20 h-full" />
          ))}
        </div>
      </div>

      {/* TOP DECORATION: ALERT BANNER */}
      <div className="absolute top-0 w-full bg-amber-500 text-black py-1 overflow-hidden flex whitespace-nowrap z-50">
        {Array.from({ length: 10 }).map((_, i) => (
          <span key={i} className="text-[10px] font-black mx-10 tracking-[0.3em]">
            SYSTEM OVERLOAD // CONCURRENCY LIMIT REACHED // ACCESS RESTRICTED // 警告: システム飽和
          </span>
        ))}
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-xl w-full relative z-10"
      >
        {/* MAIN HUD CONTAINER */}
        <div className="border-[4px] border-amber-500 p-8 relative bg-black shadow-[0_0_50px_rgba(245,158,11,0.2)]">
          
          {/* CORNER ACCENTS */}
          <div className="absolute -top-1 -left-1 w-10 h-10 border-t-[8px] border-l-[8px] border-amber-500" />
          <div className="absolute -bottom-1 -right-1 w-10 h-10 border-b-[8px] border-r-[8px] border-amber-500" />

          {/* TITLE SECTION */}
          <div className="flex items-center gap-4 mb-10 border-b-2 border-amber-500 pb-4">
            <AlertCircle size={32} className="animate-pulse" />
            <div>
              <h1 className="text-2xl font-black italic tracking-tighter uppercase leading-none">Status: Standby</h1>
              <p className="text-[10px] font-bold tracking-widest opacity-70">MAGI-01 BALTHAZAR DECISION: PENDING</p>
            </div>
          </div>

          {/* QUEUE POSITION (HEXAGON STYLE) */}
          <div className="flex flex-col items-center justify-center mb-12">
            <div className="relative">
              <svg width="120" height="120" viewBox="0 0 100 100" className="animate-spin-slow">
                <polygon points="50,5 95,25 95,75 50,95 5,75 5,25" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="10 5" />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-sm font-black opacity-50 uppercase">Pos</span>
                <span className="text-5xl font-black leading-none">{status.position}</span>
              </div>
            </div>
            <p className="text-[11px] mt-6 font-black uppercase tracking-[0.4em] text-center">
              Puesto en la lista de espera
            </p>
          </div>

          {/* CODENAME ASSIGNMENT */}
          <div className="bg-amber-500/10 border border-amber-500 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Eye size={16} />
                <span className="text-[10px] font-black uppercase tracking-widest">Codename Assigned</span>
              </div>
              <div className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
            </div>
            
            <div className="text-center py-2 px-4 bg-amber-500 text-black font-black text-2xl tracking-[0.2em] relative overflow-hidden group">
              <motion.div 
                animate={{ x: ['-100%', '200%'] }}
                transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                className="absolute top-0 left-0 w-1/3 h-full bg-white/30 skew-x-12"
              />
              {status.codename}
            </div>
            
            <p className="text-[9px] text-center italic font-bold">
              * Memoriza tu nombre clave. Será tu único ID dentro del sistema.
            </p>
          </div>

          {/* FOOTER METRICS */}
          <div className="mt-10 grid grid-cols-2 gap-4">
            <MetricBox icon={<Cpu size={14} />} label="System Load" value="CRITICAL" color="text-red-500" />
            <MetricBox icon={<Zap size={14} />} label="Link Integrity" value="98.2%" color="text-amber-500" />
          </div>
        </div>

        {/* LOADING INDICATOR (EVANGELION STYLE) */}
        <div className="mt-8 flex items-center justify-between px-2">
          <div className="flex gap-1">
            {Array.from({ length: 8 }).map((_, i) => (
              <motion.div 
                key={i}
                animate={{ opacity: [0.2, 1, 0.2] }}
                transition={{ repeat: Infinity, duration: 1, delay: i * 0.1 }}
                className="w-4 h-1 bg-amber-500" 
              />
            ))}
          </div>
          <span className="text-[9px] font-black uppercase italic tracking-widest animate-pulse">
            Waiting for slot availability...
          </span>
        </div>
      </motion.div>

      {/* ERROR OVERLAY */}
      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 z-50 bg-red-950/90 backdrop-blur-md flex items-center justify-center p-10"
          >
            <div className="max-w-sm border-2 border-red-500 p-6 text-red-500 flex flex-col items-center gap-4 text-center">
              <AlertCircle size={48} />
              <h2 className="text-xl font-black uppercase">Critical Communication Error</h2>
              <p className="text-xs font-bold leading-relaxed">{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="mt-4 px-6 py-2 bg-red-500 text-black font-black text-xs uppercase hover:bg-white transition-colors"
              >
                Retry Link
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}

function MetricBox({ icon, label, value, color }: { icon: React.ReactNode, label: string, value: string, color: string }) {
  return (
    <div className="border border-amber-500/30 p-3 flex flex-col gap-1">
      <div className="flex items-center gap-2 opacity-60">
        {icon}
        <span className="text-[8px] font-black uppercase tracking-widest">{label}</span>
      </div>
      <span className={`text-xs font-black ${color}`}>{value}</span>
    </div>
  );
}
