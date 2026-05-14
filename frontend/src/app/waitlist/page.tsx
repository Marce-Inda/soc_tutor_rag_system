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
  const [diagnosis, setDiagnosis] = useState<string[]>([]);

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
    // Simulación de Diagnóstico de Sistema
    const diagnosisLogs = [
      "CHECKING NEURAL LINK...",
      "VERIFYING VECTOR DATABASE INTEGRITY...",
      "SYNCING WITH MAGI-01 BALTHAZAR...",
      "ALLOCATING MEMORY SLOTS...",
      "CALIBRATING REAC-T CYCLE...",
      "STABILIZING COGNITIVE OVERLAY...",
      "VALIDATING ZERO-TRUST PROTOCOLS...",
      "UPDATING PEDAGOGICAL HARNESS...",
      "ENCRYPTING SESSION FRAGMENTS...",
      "INITIALIZING RAG RETRIEVAL MESH...",
      "ESTABLISHING SECURE TUNNEL TO CORE...",
      "CALCULATING SYNC PARAMETERS..."
    ];

    let diagIdx = 0;
    const diagInterval = setInterval(() => {
      setDiagnosis(prev => [...prev.slice(-7), diagnosisLogs[diagIdx % diagnosisLogs.length]]);
      diagIdx++;
    }, 1800);

    return () => {
      clearInterval(interval);
      clearInterval(diagInterval);
      musicManager.stopAll();
    };
  }, [router]);

  if (!status && !error) {
    return (
      <div className="h-screen bg-black flex items-center justify-center font-mono relative">
        <div className="crt-overlay" />
        <div className="scanline" />
        <div className="flex flex-col items-center gap-4 text-amber-500 z-10">
          <Loader2 className="animate-spin" size={48} />
          <span className="text-[10px] tracking-[0.5em] font-black uppercase">Enlazando con sistema NERV...</span>
        </div>
      </div>
    );
  }

  if (error && !status) {
    return (
      <div className="h-screen bg-black flex items-center justify-center font-mono relative">
        <div className="crt-overlay" />
        <div className="absolute inset-0 z-50 bg-red-950/90 backdrop-blur-md flex items-center justify-center p-10">
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
        </div>
      </div>
    );
  }

  if (!status) return null;

  return (
    <div className="h-screen bg-black text-amber-500 font-mono overflow-hidden relative flex flex-col items-center justify-center p-6 select-none">
      <div className="crt-overlay" />
      <div className="scanline" />
      
      {/* DECORATIVE BACKGROUND (KANJI & LINES) */}
      <div className="absolute inset-0 opacity-10 pointer-events-none">
        <div className="absolute top-10 left-10 text-[100px] font-black">ALERTA</div>
        <div className="absolute bottom-10 right-10 text-[100px] font-black">MISIÓN</div>
        <div className="grid grid-cols-12 h-full w-full">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="border-r border-amber-500/20 h-full" />
          ))}
        </div>
      </div>

      {/* TOP DECORATION: ALERT BANNER */}
      <div className="absolute top-0 w-full bg-amber-500 text-black py-1 overflow-hidden flex whitespace-nowrap z-50">
        {Array.from({ length: 10 }).map((_, i) => (
          <span key={i} className="text-[10px] font-black mx-10 tracking-[0.3em] animate-pulse">
            SYSTEM OVERLOAD // CONCURRENCY LIMIT REACHED // ACCESS RESTRICTED // ALERTA: SISTEMA SATURADO
          </span>
        ))}
      </div>

      <div className="flex gap-10 items-start justify-center relative z-10 max-w-6xl w-full">
        {/* LEFT: MAIN HUD (User Card) */}
        <motion.div 
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          className="max-w-xl w-full"
        >
          <div className="border-[4px] border-amber-500 p-8 relative bg-black/90 shadow-[0_0_50px_rgba(245,158,11,0.2)]">
            
            {/* CORNER ACCENTS */}
            <div className="absolute -top-1 -left-1 w-10 h-10 border-t-[8px] border-l-[8px] border-amber-500" />
            <div className="absolute -bottom-1 -right-1 w-10 h-10 border-b-[8px] border-r-[8px] border-amber-500" />

            {/* TITLE SECTION */}
            <div className="flex items-center gap-4 mb-10 border-b-2 border-amber-500 pb-4">
              <ShieldAlert size={32} className="animate-pulse" />
              <div>
                <h1 className="text-2xl font-black italic tracking-tighter uppercase leading-none">Status: Standby</h1>
                <p className="text-[10px] font-bold tracking-widest opacity-70">MAGI-01 BALTHAZAR DECISION: PENDING</p>
              </div>
            </div>

            {/* QUEUE POSITION (IMPROVED CLARITY) */}
            <div className="flex flex-col items-center justify-center mb-12">
              <div className="relative group">
                <svg width="140" height="140" viewBox="0 0 100 100" className="animate-spin-slow text-amber-500/20">
                  <polygon points="50,5 95,25 95,75 50,95 5,75 5,25" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="10 5" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-[10px] font-black text-amber-500/60 uppercase tracking-widest mb-1">Tu Posición</span>
                  <span className="text-6xl font-black leading-none glow-text-amber">{status.position}</span>
                  <div className="mt-1 px-2 py-0.5 bg-amber-500 text-black text-[8px] font-black uppercase">En Cola</div>
                </div>
              </div>
              <p className="text-[11px] mt-6 font-black uppercase tracking-[0.4em] text-center max-w-[200px]">
                Acceso restringido por capacidad máxima
              </p>
            </div>

            {/* CODENAME ASSIGNMENT (THE CARD) */}
            <div className="bg-amber-500/10 border-2 border-amber-500 p-6 space-y-4 relative overflow-hidden group">
               <div className="absolute top-0 right-0 p-2 opacity-10">
                  <Eye size={40} />
               </div>
               <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-black uppercase tracking-[0.3em]">Codename Assigned</span>
                </div>
                <div className="h-2 w-2 rounded-full bg-amber-500 animate-ping" />
              </div>
              
              <div className="text-center py-3 px-4 bg-amber-500 text-black font-black text-3xl tracking-[0.2em] relative overflow-hidden z-10 shadow-[0_0_20px_rgba(245,158,11,0.4)]">
                {status.codename}
              </div>
              
              <p className="text-[9px] text-center italic font-bold relative z-10 opacity-70">
                * Este es tu identificador táctico único para esta misión.
              </p>
            </div>

            {/* FOOTER METRICS */}
            <div className="mt-10 grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <MetricBox icon={<Cpu size={14} />} label="System Load" value="CRITICAL" color="text-red-500" />
                <MetricBox icon={<Zap size={14} />} label="Est. Wait Time" value={`${status.position * 2}s`} color="text-amber-500" />
              </div>
              
              <div className="border border-amber-500/20 bg-amber-500/5 p-4 rounded-sm flex flex-col gap-2 min-h-[110px]">
                <span className="text-[8px] font-black uppercase tracking-widest text-amber-500/60 flex items-center gap-2">
                  <Loader2 size={10} className="animate-spin" /> Diagnosis Terminal
                </span>
                <div className="flex flex-col gap-1 font-mono text-[9px] text-amber-500/80">
                  {diagnosis.map((log, idx) => (
                    <span key={idx} className="truncate border-l border-amber-500/30 pl-2 opacity-60 group-hover:opacity-100 transition-opacity">
                      {`> ${log}`}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* RIGHT: TACTICAL QUEUE FEED */}
        <motion.div 
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          className="w-80 flex flex-col gap-4"
        >
          <div className="flex items-center justify-between border-b-2 border-amber-500/30 pb-2">
            <h3 className="text-xs font-black uppercase tracking-[0.3em] flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-amber-500" />
              Queue Feed
            </h3>
            <span className="text-[10px] font-bold opacity-50 uppercase">[{status.queue_list.length} Analysts]</span>
          </div>

          <div className="flex flex-col gap-3 overflow-hidden h-[480px]">
            <AnimatePresence mode="popLayout">
              {status.queue_list.map((name, idx) => {
                const isUser = name === status.codename;
                const pos = idx + 1;
                
                return (
                  <motion.div 
                    key={name}
                    layout
                    initial={{ opacity: 0, y: 20, filter: 'blur(10px)' }}
                    animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                    exit={{ opacity: 0, x: 20, filter: 'blur(10px)' }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                    className={`
                      relative p-4 border flex items-center justify-between group
                      ${isUser 
                        ? 'border-amber-500 bg-amber-500/20 shadow-[0_0_15px_rgba(245,158,11,0.2)]' 
                        : 'border-amber-500/30 bg-black/40 opacity-70'}
                    `}
                  >
                    <div className="flex items-center gap-4">
                      <span className={`text-[10px] font-black ${isUser ? 'text-amber-500' : 'text-amber-500/50'}`}>
                        {pos.toString().padStart(2, '0')}
                      </span>
                      <span className={`text-sm font-black tracking-widest ${isUser ? 'text-amber-500' : 'text-amber-500/80'}`}>
                        {name}
                      </span>
                    </div>
                    {isUser && (
                      <div className="flex items-center gap-1">
                        <div className="h-1 w-1 rounded-full bg-amber-500 animate-pulse" />
                        <span className="text-[8px] font-black uppercase tracking-tighter text-amber-500">YOU</span>
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </AnimatePresence>
            
            {status.queue_list.length === 0 && (
              <div className="flex-1 flex flex-col items-center justify-center border-2 border-dashed border-amber-500/20 rounded-xl">
                 <Loader2 className="animate-spin text-amber-500/20" size={32} />
                 <span className="text-[10px] font-black uppercase tracking-widest mt-4 opacity-20">Link Established</span>
              </div>
            )}
          </div>

          <div className="mt-auto p-4 border border-amber-500/20 bg-amber-500/5 rounded">
            <p className="text-[8px] leading-relaxed opacity-50 font-bold uppercase italic">
              * El sistema procesa los accesos basándose en la prioridad táctica y el tiempo de sincronización neural. No cierre esta ventana o perderá su lugar en la secuencia de entrada.
            </p>
          </div>
        </motion.div>
      </div>

      {/* EVANGELION STYLE LOADING BAR (BOTTOM) */}
      <div className="fixed bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-4">
        <div className="flex gap-2">
          {Array.from({ length: 12 }).map((_, i) => (
            <motion.div 
              key={i}
              animate={{ 
                opacity: [0.2, 1, 0.2],
                backgroundColor: i < (6 - status.position) * 2 ? '#f59e0b' : '#451a03'
              }}
              transition={{ repeat: Infinity, duration: 2, delay: i * 0.1 }}
              className="w-6 h-2 rounded-sm" 
            />
          ))}
        </div>
        <span className="text-[10px] font-black uppercase italic tracking-[0.5em] animate-pulse">
          Awaiting SOC Slot Availability...
        </span>
      </div>

      {/* ERROR OVERLAY */}
      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 z-50 bg-red-950/90 backdrop-blur-md flex items-center justify-center p-10 font-mono"
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
