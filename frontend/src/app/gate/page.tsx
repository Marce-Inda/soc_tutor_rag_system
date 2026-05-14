'use client'

import React from 'react';
import { motion } from 'framer-motion';
import { Terminal, Zap, ShieldAlert } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { audioSystem } from '@/utils/audio';

export default function GatePage() {
  const router = useRouter();

  const handleStartSequence = () => {
    audioSystem.playClick();
    router.push('/waitlist');
  };

  return (
    <div className="h-screen bg-black text-primary font-mono overflow-hidden relative flex flex-col items-center justify-center p-6 select-none">
      <div className="crt-overlay" />
      <div className="scanline" />
      
      {/* BACKGROUND DECORATIONS (NERV STYLE) */}
      <div className="absolute inset-0 opacity-5 pointer-events-none">
        <div className="absolute top-10 left-1/2 -translate-x-1/2 text-[180px] font-black opacity-10 tracking-tighter">ACCESS</div>
        <div className="absolute bottom-10 left-1/2 -translate-x-1/2 text-[180px] font-black opacity-10 tracking-tighter">DENIED</div>
        <div className="grid grid-cols-12 h-full w-full">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="border-r border-primary/10 h-full" />
          ))}
        </div>
      </div>

      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-3xl w-full z-10 flex flex-col items-center"
      >
        {/* HEADER SECTION */}
        <div className="text-center mb-20 relative">
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="flex flex-col items-center gap-4"
          >
            <div className="p-3 border-2 border-primary shadow-[0_0_20px_rgba(34,211,238,0.3)]">
              <ShieldAlert size={48} className="text-primary animate-pulse" />
            </div>
            <div>
              <h1 className="text-6xl font-black italic tracking-tighter uppercase leading-none glow-text-primary">
                SOC Tutor <span className="text-primary/60 font-medium not-italic">Workstation</span>
              </h1>
              <div className="mt-4 flex items-center justify-center gap-4">
                <div className="h-[2px] w-20 bg-gradient-to-r from-transparent via-primary to-transparent" />
                <p className="text-xs font-black tracking-[0.6em] text-primary/80 uppercase">
                  Terminal de Acceso NERV-MAGI
                </p>
                <div className="h-[2px] w-20 bg-gradient-to-r from-transparent via-primary to-transparent" />
              </div>
            </div>
          </motion.div>
        </div>

        {/* CENTRAL ACCESS MODULE (THE BUTTON) */}
        <div className="w-full relative px-10">
          {/* Decorative Framing */}
          <div className="absolute -top-4 -left-4 w-12 h-12 border-t-2 border-l-2 border-primary/40" />
          <div className="absolute -top-4 -right-4 w-12 h-12 border-t-2 border-r-2 border-primary/40" />
          <div className="absolute -bottom-4 -left-4 w-12 h-12 border-b-2 border-l-2 border-primary/40" />
          <div className="absolute -bottom-4 -right-4 w-12 h-12 border-b-2 border-r-2 border-primary/40" />

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={handleStartSequence}
            className="group relative w-full p-16 border-2 border-primary bg-primary/5 transition-all flex flex-col items-center gap-8 overflow-hidden shadow-[0_0_50px_rgba(34,211,238,0.15)]"
          >
            {/* Animated Laser Scan Line */}
            <motion.div 
              animate={{ top: ['-10%', '110%'] }}
              transition={{ repeat: Infinity, duration: 3, ease: "linear" }}
              className="absolute left-0 w-full h-[2px] bg-primary shadow-[0_0_15px_#22d3ee] z-20 opacity-50"
            />
            
            <div className="relative z-10 flex flex-col items-center gap-6">
              <div className="h-20 w-20 rounded-full border-2 border-primary/30 flex items-center justify-center relative">
                 <motion.div 
                   animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
                   transition={{ repeat: Infinity, duration: 2 }}
                   className="absolute inset-0 bg-primary rounded-full"
                 />
                 <Zap size={40} className="text-primary relative z-10" />
              </div>

              <div className="text-center">
                <h2 className="text-3xl font-black uppercase tracking-widest mb-3">Iniciar Secuencia de Acceso</h2>
                <div className="flex items-center justify-center gap-3">
                   <div className="h-1.5 w-1.5 rounded-full bg-success animate-pulse" />
                   <p className="text-[10px] text-primary font-bold tracking-[0.3em] uppercase opacity-60 group-hover:opacity-100 transition-opacity">
                     Sincronización de Biometría y Malla Neural
                   </p>
                </div>
              </div>
            </div>

            {/* Background Glitch Elements on Hover */}
            <div className="absolute inset-0 bg-primary/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
          </motion.button>
        </div>

        {/* SYSTEM STATS FOOTER */}
        <div className="mt-24 w-full flex flex-col items-center gap-8 border-t border-primary/10 pt-12">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3 text-primary/40">
              <Terminal size={14} />
              <span className="text-[9px] font-black uppercase tracking-[0.4em]">Auth Core.v4.2.0</span>
            </div>
            <div className="h-4 w-[1px] bg-primary/20" />
            <div className="flex items-center gap-3 text-success/60">
              <div className="h-1.5 w-1.5 rounded-full bg-success shadow-[0_0_8px_currentColor]" />
              <span className="text-[9px] font-black uppercase tracking-[0.4em]">Malla Estable</span>
            </div>
          </div>

          <div className="flex justify-between w-full max-w-2xl opacity-20">
            {[
              { label: "LOGIC CORE", id: "MELCHIOR" },
              { label: "NEURAL MATRIX", id: "BALTHASAR" },
              { label: "INTEL BASE", id: "CASPER" }
            ].map((magi, i) => (
              <div key={i} className="flex flex-col items-center border-l border-primary/30 pl-4">
                <span className="text-[8px] font-black uppercase tracking-tighter mb-1">{magi.label}</span>
                <span className="text-[10px] font-bold tracking-widest">MAGI-0{i+1}: {magi.id}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </div>
  );
}
