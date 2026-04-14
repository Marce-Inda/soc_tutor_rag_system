'use client'

import React from 'react';
import { 
  ShieldAlert, 
  Terminal, 
  Search, 
  Database, 
  Lock, 
  AlertTriangle,
  Activity,
  UserCheck
} from 'lucide-react';

export default function WorkstationPage() {
  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-foreground font-mono">
      {/* 1. TOP NAV / LEVEL SELECTOR */}
      <header className="h-14 border-b border-card-border glass flex items-center justify-between px-6 z-50">
        <div className="flex items-center gap-2">
          <ShieldAlert className="text-primary animate-pulse" />
          <span className="font-bold tracking-widest glow-text-primary uppercase">The Responder</span>
          <span className="text-[10px] text-muted-foreground ml-2 border-l border-card-border pl-2 uppercase">[Analista SOC]</span>
        </div>
        
        <nav className="flex items-center gap-4">
          <button className="px-3 py-1 rounded border border-primary text-primary text-xs hover:bg-primary/10 transition-all">LEVEL 01</button>
          <button className="px-3 py-1 rounded border border-muted text-muted text-xs hover:border-primary/50 hover:text-primary transition-all">LEVEL 02</button>
          <button className="px-3 py-1 rounded border border-muted text-muted text-xs hover:border-primary/50 hover:text-primary transition-all">LEVEL 03</button>
        </nav>

        <div className="flex items-center gap-4 text-xs">
          <div className="flex flex-col items-end">
            <span className="text-muted text-[10px]">FASE ACTUAL</span>
            <span className="text-secondary font-bold uppercase tracking-tighter">Detección</span>
          </div>
          <div className="h-8 w-[1px] bg-card-border" />
          <div className="flex flex-col items-end">
            <span className="text-muted text-[10px]">DESEMPEÑO</span>
            <span className="text-primary font-bold">8500 / 10000</span>
          </div>
        </div>
      </header>

      {/* 2. MAIN WORKSTATION GRID */}
      <main className="flex-1 flex overflow-hidden">
        
        {/* LEFT SIDEBAR: TACTICAL TOOLS */}
        <aside className="w-64 border-r border-card-border bg-card p-4 flex flex-col gap-6">
          <div>
            <h3 className="text-[10px] text-muted mb-3 uppercase tracking-widest font-bold">Investigación</h3>
            <div className="grid grid-cols-1 gap-2">
              <ToolButton icon={<Search size={16}/>} label="NetScan" risk="Medio" />
              <ToolButton icon={<Database size={16}/>} label="Log Analyzer" risk="Bajo" />
              <ToolButton icon={<Terminal size={16}/>} label="Dir Walk" risk="Bajo" />
            </div>
          </div>

          <div>
            <h3 className="text-[10px] text-muted mb-3 uppercase tracking-widest font-bold">Contención</h3>
            <div className="grid grid-cols-1 gap-2">
              <ToolButton icon={<Lock size={16}/>} label="Isolate Host" risk="Alto" />
              <ToolButton icon={<AlertTriangle size={16}/>} label="Block IP" risk="Medio" />
            </div>
          </div>

          <div className="mt-auto">
             <div className="p-3 rounded bg-primary/5 border border-primary/20">
                <p className="text-[10px] text-primary/70 mb-1 font-bold">SYSTEM STATUS</p>
                <div className="flex items-center gap-2">
                   <div className="h-2 w-2 rounded-full bg-success animate-ping" />
                   <span className="text-xs">Agents Engaged</span>
                </div>
             </div>
          </div>
        </aside>

        {/* CENTER: INCIDENT VISUALIZER (NODE GRAPH AREA) */}
        <section className="flex-1 relative bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:24px_24px] overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center">
             <div className="text-center">
                <Activity size={64} className="mx-auto text-muted/30 mb-4" />
                <p className="text-muted/50 text-xs tracking-widest uppercase">Initializing Node Map...</p>
             </div>
          </div>
          
          {/* ACTION CONSOLE (FLOATING BOTTOM) */}
          <div className="absolute bottom-6 left-6 right-6 h-40 glass rounded-lg border border-card-border p-4 flex flex-col">
             <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] text-muted uppercase font-bold tracking-widest">Logs de Ejecución Táctica</span>
                <span className="text-[10px] text-success">LISTO {'>'}</span>
             </div>
             <div className="flex-1 font-mono text-xs text-primary/80 overflow-y-auto space-y-1">
                <p>[10:42:01] SEC-CORE INITIALIZED</p>
                <p>[10:42:05] WAITING FOR ANALYST INPUT...</p>
             </div>
          </div>
        </section>

        {/* RIGHT SIDEBAR: AI MENTOR CONSOLE */}
        <aside className="w-80 border-l border-card-border bg-card/50 backdrop-blur-md flex flex-col overflow-hidden">
           <div className="p-4 border-b border-card-border bg-primary/10">
              <div className="flex items-center gap-3">
                 <div className="h-10 w-10 rounded-full border border-primary flex items-center justify-center bg-background glow-primary">
                    <UserCheck className="text-primary" size={20} />
                 </div>
                 <div>
                    <h4 className="text-sm font-bold text-primary tracking-tight">MENTOR IA</h4>
                    <span className="text-[10px] text-muted uppercase">Asesor Táctico</span>
                 </div>
              </div>
           </div>

           <div className="flex-1 p-6 overflow-y-auto">
              <div className="space-y-6">
                 <div>
                    <h5 className="text-[10px] text-secondary font-bold uppercase mb-2">Resumen de Misión (Briefing)</h5>
                    <p className="text-sm leading-relaxed text-foreground/80">
                      Bienvenido a la Operación Ghost-Bank. Hemos detectado conexiones sospechosas (beaconing) desde el servidor SRV-SWIFT-01. 
                      Tu objetivo es contener la amenaza mientras preservas la evidencia forense. No tomes acciones de alto riesgo sin suficientes datos.
                    </p>
                 </div>

                 <div className="p-3 rounded border border-card-border bg-background/50 italic text-xs text-muted leading-relaxed">
                    "Piensa como un atacante para defender como un analista."
                 </div>
              </div>
           </div>
        </aside>

      </main>
    </div>
  );
}

function ToolButton({ icon, label, risk }: { icon: React.ReactNode, label: string, risk: string }) {
  const riskColor = risk === 'Alto' ? 'text-danger' : risk === 'Medio' ? 'text-secondary' : 'text-success';
  return (
    <button className="flex items-center gap-3 px-3 py-2.5 rounded-md hover:bg-primary/10 border border-transparent hover:border-primary/20 transition-all text-left group">
      <span className="text-muted group-hover:text-primary transition-colors">{icon}</span>
      <div className="flex-1">
        <div className="text-xs font-bold">{label}</div>
        <div className={`text-[9px] uppercase font-bold ${riskColor}`}>Riesgo: {risk}</div>
      </div>
    </button>
  );
}
