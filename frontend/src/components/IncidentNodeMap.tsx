'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Server, Monitor, Shield, Zap, Lock } from 'lucide-react';

export default function IncidentNodeMap() {
  return (
    <div className="relative w-full h-full flex items-center justify-center p-10 overflow-hidden">
      {/* Background Grid */}
      <div className="absolute inset-0 opacity-10 bg-[linear-gradient(to_right,#808080_1px,transparent_1px),linear-gradient(to_bottom,#808080_1px,transparent_1px)] bg-[size:40px_40px]" />

      <div className="relative z-10 flex flex-col items-center gap-16">
        {/* EXTERNAL NETWORK / ATTACK SOURCE */}
        <div className="flex flex-col items-center">
          <motion.div 
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="w-16 h-16 rounded-full bg-danger/20 border-2 border-danger flex items-center justify-center relative shadow-[0_0_20px_rgba(239,68,68,0.3)]"
          >
            <Zap className="text-danger" size={32} />
            <motion.div 
              animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ repeat: Infinity, duration: 2 }}
              className="absolute inset-0 rounded-full border border-danger"
            />
          </motion.div>
          <span className="text-[10px] mt-2 font-bold text-danger uppercase tracking-tighter">Origen: Externo (Blocklisted)</span>
        </div>

        {/* CONNECTION LINE 1 */}
        <motion.div 
          initial={{ height: 0 }}
          animate={{ height: 40 }}
          className="w-0.5 bg-gradient-to-b from-danger to-warning relative"
        >
          <motion.div 
            animate={{ top: ['0%', '100%'] }}
            transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
            className="absolute left-[-2px] w-1.5 h-1.5 rounded-full bg-warning"
          />
        </motion.div>

        {/* COMPROMISED SERVER */}
        <div className="flex flex-col items-center relative">
          <motion.div 
            animate={{ borderColor: ['rgba(251,191,36,0.5)', 'rgba(251,191,36,1)'] }}
            transition={{ repeat: Infinity, duration: 1 }}
            className="w-24 h-24 rounded-lg bg-card border-2 border-warning flex flex-col items-center justify-center gap-2 shadow-[0_0_30px_rgba(251,191,36,0.2)]"
          >
            <Server className="text-warning" size={32} />
            <span className="text-[10px] font-bold text-warning uppercase">SRV-SWIFT-01</span>
          </motion.div>
          
          <div className="absolute top-0 right-0 -mr-4 -mt-4">
             <motion.div 
               animate={{ rotate: 360 }}
               transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
               className="p-1 rounded-full border border-danger/50"
             >
                <div className="h-4 w-4 rounded-full bg-danger animate-pulse" />
             </motion.div>
          </div>
        </div>

        {/* INTERNAL NETWORK / TARGETS */}
        <div className="flex gap-12 mt-4">
           <Node icon={<Monitor size={20}/>} label="WKS-ADMIN-04" status="safe" />
           <Node icon={<Shield size={20}/>} label="DB-CORE-PRD" status="safe" />
        </div>
      </div>

      {/* FLOATING DATA PACKETS (Random decoration) */}
      {[...Array(5)].map((_, i) => (
        <motion.div
          key={i}
          animate={{ 
            x: [Math.random() * 500 - 250, Math.random() * 500 - 250],
            y: [Math.random() * 400 - 200, Math.random() * 400 - 200],
            opacity: [0, 0.4, 0]
          }}
          transition={{ duration: 5 + Math.random() * 5, repeat: Infinity }}
          className="absolute w-1 h-1 bg-primary rounded-full shadow-[0_0_8px_cyan]"
        />
      ))}
    </div>
  );
}

function Node({ icon, label, status }: { icon: React.ReactNode, label: string, status: 'safe' | 'warning' | 'compromised' }) {
  const color = status === 'safe' ? 'text-success' : status === 'warning' ? 'text-warning' : 'text-danger';
  const borderColor = status === 'safe' ? 'border-success/30' : status === 'warning' ? 'border-warning/30' : 'border-danger/30';

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`w-14 h-14 rounded-md border ${borderColor} bg-card/50 flex items-center justify-center ${color}`}>
        {icon}
      </div>
      <span className="text-[8px] font-mono opacity-60 uppercase">{label}</span>
    </div>
  );
}
