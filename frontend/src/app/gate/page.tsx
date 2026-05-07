'use client'

import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Users, Terminal, Zap, ShieldAlert } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { audioSystem } from '@/utils/audio';

export default function GatePage() {
  const router = useRouter();

  const handleEnterDirectly = () => {
    audioSystem.playClick();
    // Simular entrada directa - El root se encarga de verificar si hay cupo
    router.push('/');
  };

  const handleJoinWaitlist = () => {
    audioSystem.playClick();
    router.push('/waitlist');
  };

  return (
    <div className="h-screen bg-black text-primary font-mono overflow-hidden relative flex flex-col items-center justify-center p-6">
      <div className="crt-overlay" />
      <div className="scanline" />
      
      {/* Decorative Elements */}
      <div className="absolute inset-0 opacity-5 pointer-events-none">
        <div className="absolute top-20 left-20 text-[120px] font-black rotate-[-15deg]">ACCESS</div>
        <div className="absolute bottom-20 right-20 text-[120px] font-black rotate-[15deg]">DENIED</div>
        <div className="grid grid-cols-6 h-full w-full">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="border-r border-primary/20 h-full" />
          ))}
        </div>
      </div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl w-full z-10"
      >
        <div className="text-center mb-16">
          <motion.div
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', stiffness: 200, damping: 10 }}
            className="inline-block p-4 border-2 border-primary mb-6 shadow-[0_0_30px_rgba(34,211,238,0.2)]"
          >
            <ShieldAlert size={64} className="text-primary animate-pulse" />
          </motion.div>
          <h1 className="text-5xl font-black italic tracking-tighter uppercase mb-2 glow-text-primary">
            SOC Tutor Workstation
          </h1>
          <p className="text-xs font-bold tracking-[0.5em] text-muted-foreground uppercase">
            Protocolo de Acceso: NERV-MAGI-2026
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* OPTION 1: DIRECT ENTRY */}
          <motion.button
            whileHover={{ scale: 1.02, backgroundColor: 'rgba(34, 211, 238, 0.1)' }}
            whileTap={{ scale: 0.98 }}
            onClick={handleEnterDirectly}
            className="group relative p-10 border-2 border-primary bg-black transition-all flex flex-col items-center gap-6 overflow-hidden shadow-[0_0_20px_rgba(34,211,238,0.1)]"
          >
            <div className="absolute top-0 left-0 w-full h-1 bg-primary group-hover:h-full group-hover:opacity-10 transition-all duration-500" />
            <Shield size={48} className="text-primary group-hover:scale-110 transition-transform" />
            <div className="text-center">
              <h2 className="text-2xl font-black uppercase mb-2">Entrar al Juego</h2>
              <p className="text-[10px] text-muted-foreground font-bold tracking-widest uppercase">
                Acceso prioritario a la terminal de incidentes
              </p>
            </div>
            <div className="flex gap-2">
              <span className="text-[8px] border border-primary/40 px-2 py-0.5 rounded uppercase font-black">Status: Online</span>
              <span className="text-[8px] border border-primary/40 px-2 py-0.5 rounded uppercase font-black">Latencia: 12ms</span>
            </div>
          </motion.button>

          {/* OPTION 2: WAITLIST */}
          <motion.button
            whileHover={{ scale: 1.02, backgroundColor: 'rgba(251, 191, 36, 0.1)' }}
            whileTap={{ scale: 0.98 }}
            onClick={handleJoinWaitlist}
            className="group relative p-10 border-2 border-secondary bg-black transition-all flex flex-col items-center gap-6 overflow-hidden shadow-[0_0_20px_rgba(251,191,36,0.1)]"
          >
            <div className="absolute top-0 left-0 w-full h-1 bg-secondary group-hover:h-full group-hover:opacity-10 transition-all duration-500" />
            <Users size={48} className="text-secondary group-hover:scale-110 transition-transform" />
            <div className="text-center">
              <h2 className="text-2xl font-black uppercase mb-2 text-secondary">Lista de Espera</h2>
              <p className="text-[10px] text-muted-foreground font-bold tracking-widest uppercase">
                Sincronización de malla y diagnóstico previo
              </p>
            </div>
            <div className="flex gap-2">
              <span className="text-[8px] border border-secondary/40 text-secondary px-2 py-0.5 rounded uppercase font-black">Modo: Demo</span>
              <span className="text-[8px] border border-secondary/40 text-secondary px-2 py-0.5 rounded uppercase font-black">Posición: Ver</span>
            </div>
          </motion.button>
        </div>

        <div className="mt-20 flex flex-col items-center gap-4 border-t border-primary/20 pt-10">
          <div className="flex items-center gap-4 text-muted-foreground">
            <Terminal size={16} />
            <span className="text-[10px] font-bold uppercase tracking-[0.3em]">System.v4.0.0 // Ready for Ingress</span>
          </div>
          <div className="flex gap-10 opacity-30">
            <div className="flex flex-col items-center">
              <span className="text-[8px] font-black uppercase">Logic Core</span>
              <span className="text-[10px] font-bold">MAGI-01: MELCHIOR</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-[8px] font-black uppercase">Neural Matrix</span>
              <span className="text-[10px] font-bold">MAGI-02: BALTHASAR</span>
            </div>
            <div className="flex flex-col items-center">
              <span className="text-[8px] font-black uppercase">Intel Base</span>
              <span className="text-[10px] font-bold">MAGI-03: CASPER</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
