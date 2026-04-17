'use client'

import React, { useEffect } from 'react';
import { 
  ShieldAlert, 
  Terminal, 
  Search, 
  Database, 
  Lock, 
  AlertTriangle,
  Activity,
  UserCheck,
  Loader2,
  BookOpen,
  Info,
  Shield
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useIncidentStore } from '@/store/incidentStore';
import { getFeedback } from '@/utils/api';
import IncidentNodeMap from '@/components/IncidentNodeMap';

export default function WorkstationPage() {
  const { 
    logs, 
    score, 
    phase, 
    addLog, 
    currentFeedback, 
    setFeedback, 
    isAnalyzing, 
    setAnalyzing,
    updateScore,
    isCompleted,
    completeIncident,
    showTechnicalReport,
    toggleTechnicalReport,
    resetIncident
  } = useIncidentStore();

  const handleAction = async (toolName: string, action: string, risk: string) => {
    if (isAnalyzing) return;

    addLog(`INICIANDO ACCIÓN: ${toolName}...`, 'info');
    setAnalyzing(true);

    try {
      const decision = {
        accion: action,
        target: 'SRV-SWIFT-01',
        detalle: `Ejecutado con riesgo ${risk}`
      };

      const contexto = {
        scenario_id: 'es-tourism-gdpr-email-breach-001',
        tipo_incidente: 'privacy_breach',
        fase: phase,
        sistemas_afectados: ['SMTP-Relay-Main']
      };

      const profile = {
        player_id: 'player_01',
        level: 3,
        rol: 'DPO',
        language: 'es'
      };

      const feedback = await getFeedback(decision, contexto, profile);
      
      setFeedback(feedback);
      addLog(`RESPUESTA RECIBIDA [${feedback.persona_role}]`, 'success');
      
      // Actualizar score basado en la evaluación (ejemplo: proporcional a score_tecnico)
      const points = feedback.score_tecnico > 70 ? 500 : -300;
      updateScore(points);

    } catch (error) {
      addLog('ERROR DE CONEXIÓN CON EL MOTOR DE IA', 'error');
      setAnalyzing(false);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-background text-foreground font-mono selection:bg-primary/30 relative">
      
      {/* 0. FINAL REPORT OVERLAY (CLOSURE) */}
      <AnimatePresence>
        {isCompleted && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="absolute inset-0 z-[100] bg-background/90 backdrop-blur-xl flex items-center justify-center p-12"
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              className="max-w-4xl w-full glass rounded-3xl border border-primary/30 p-10 shadow-[0_0_100px_rgba(34,211,238,0.1)] relative overflow-hidden"
            >
              {/* Decorative Background for Repoert */}
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent" />
              
              <div className="flex justify-between items-start mb-12">
                <div>
                  <h2 className="text-4xl font-black text-primary tracking-tighter uppercase mb-2">Relatorio de Cierre</h2>
                  <p className="text-muted-foreground text-sm tracking-[.2em] font-bold uppercase">Incidente: GDPR-ES-2026-003</p>
                </div>
                <div className="text-right">
                   <div className="text-[10px] text-muted font-bold uppercase mb-1">Status Final</div>
                   <div className="px-4 py-1 rounded-full bg-success/20 border border-success text-success font-black text-xs uppercase shadow-[0_0_15px_rgba(16,185,129,0.3)]">Resuelto</div>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-8 mb-12">
                 <div className="p-6 rounded-2xl bg-white/5 border border-card-border">
                    <span className="text-[10px] text-muted font-black uppercase mb-2 block">Score Táctico</span>
                    <span className="text-3xl font-black text-secondary">{score.toLocaleString()}</span>
                 </div>
                 <div className="p-6 rounded-2xl bg-white/5 border border-card-border">
                    <span className="text-[10px] text-muted font-black uppercase mb-2 block">Precisión Legal</span>
                    <span className="text-3xl font-black text-primary">94%</span>
                 </div>
                 <div className="p-6 rounded-2xl bg-white/5 border border-card-border">
                    <span className="text-[10px] text-muted font-black uppercase mb-2 block">Tiempo de Respuesta</span>
                    <span className="text-3xl font-black text-foreground">14m 22s</span>
                 </div>
              </div>

              <div className="space-y-6 mb-12">
                 <h3 className="text-xs font-black text-primary tracking-widest uppercase border-b border-card-border pb-2">Conclusiones del Mentor</h3>
                 <p className="text-lg leading-relaxed text-foreground/80 italic">
                    "Has gestionado la crisis de privacidad con el rigor técnico necesario. Tu decisión de aislar el servidor SMTP evitó una fuga mayor, cumpliendo con los principios de limitación del tratamiento del GDPR."
                 </p>
              </div>

              <div className="flex flex-col gap-4">
                 <div className="flex gap-4">
                    <button 
                      onClick={resetIncident}
                      className="flex-1 py-4 rounded-xl border border-primary/40 bg-primary/5 hover:bg-primary/20 text-primary font-black uppercase tracking-widest transition-all"
                    >
                      Reiniciar Simulación
                    </button>
                    {!showTechnicalReport && (
                      <button 
                        onClick={() => toggleTechnicalReport(true)}
                        className="flex-1 py-4 rounded-xl border border-secondary/40 bg-secondary/5 hover:bg-secondary/20 text-secondary font-black uppercase tracking-widest transition-all flex items-center justify-center gap-2"
                      >
                        <Database size={18} />
                        Consultar Métricas de IA
                      </button>
                    )}
                 </div>

                 {showTechnicalReport && (
                   <motion.div 
                     initial={{ opacity: 0, height: 0 }}
                     animate={{ opacity: 1, height: 'auto' }}
                     className="mt-4 p-6 rounded-2xl bg-black/40 border border-card-border font-mono text-[10px] space-y-4"
                   >
                      <div className="flex justify-between border-b border-card-border pb-2 opacity-50 uppercase font-black">
                         <span>Métrica del Sistema</span>
                         <span>Valor / Operación</span>
                      </div>
                      <div className="flex justify-between items-center">
                         <span className="text-muted">Orquestación Multiagente</span>
                         <span className="text-success">[OK] 4 Agentes en Paralelo</span>
                      </div>
                      <div className="flex justify-between items-center">
                         <span className="text-muted">RAG Retrieval Precision (ChromaDB)</span>
                         <span className="text-primary">853 Docs Indexados / 0.892 Cosine Sim</span>
                      </div>
                      <div className="flex justify-between items-center">
                         <span className="text-muted">Latencia de Inferencia (Groq/Llama3)</span>
                         <span className="text-secondary">avg 1.2s / total 45 tokens/sec</span>
                      </div>
                   </motion.div>
                 )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 1. TOP NAV / LEVEL SELECTOR */}
      <header className="h-14 border-b border-card-border glass flex items-center justify-between px-6 z-50">
        <div className="flex items-center gap-2">
          <ShieldAlert className="text-primary animate-pulse" />
          <span className="font-bold tracking-widest glow-text-primary uppercase text-sm">The Responder</span>
          <span className="text-[10px] text-muted-foreground ml-2 border-l border-card-border pl-2 uppercase">[Workstation v1.0]</span>
        </div>
        
        <nav className="flex items-center gap-4">
          <button className="px-3 py-1 rounded border border-secondary text-secondary text-[10px] font-bold bg-secondary/5 uppercase">LEVEL 03: GDPR CRISIS</button>
          <button className="px-3 py-1 rounded border border-muted text-muted text-[10px] hover:border-primary/50 hover:text-primary transition-all cursor-not-allowed uppercase">LEVEL 01</button>
          <button className="px-3 py-1 rounded border border-muted text-muted text-[10px] hover:border-primary/50 hover:text-primary transition-all cursor-not-allowed uppercase">LEVEL 02</button>
        </nav>

        <div className="flex items-center gap-8">
          <div className="flex flex-col items-end">
            <span className="text-muted text-[9px] font-bold uppercase tracking-widest">Fase del Incidente</span>
            <span className="text-secondary font-bold uppercase text-xs">{phase}</span>
          </div>
          <div className="h-8 w-[1px] bg-card-border" />
          <div className="flex flex-col items-end min-w-[100px]">
            <span className="text-muted text-[9px] font-bold uppercase tracking-widest">Score Táctico</span>
            <motion.span 
              key={score}
              initial={{ scale: 1.2, color: '#fbbf24' }}
              animate={{ scale: 1, color: '#22d3ee' }}
              className="text-primary font-bold text-xs"
            >
              {score.toLocaleString()} / 10,000
            </motion.span>
          </div>
        </div>
      </header>

      {/* 2. MAIN WORKSTATION GRID */}
      <main className="flex-1 flex overflow-hidden">
        
        {/* LEFT SIDEBAR: TACTICAL TOOLS */}
        <aside className="w-64 border-r border-card-border bg-card/80 p-5 flex flex-col gap-8">
          <div className="space-y-4">
            <h3 className="text-[10px] text-muted mb-4 uppercase tracking-[0.2em] font-black border-b border-card-border pb-2">Investigación</h3>
            <div className="grid grid-cols-1 gap-3">
              <ToolButton 
                icon={<Search size={16}/>} 
                label="NetScan" 
                risk="Bajo" 
                onClick={() => handleAction('NetScan', 'network_scan', 'Bajo')}
                disabled={isAnalyzing || isCompleted}
              />
              <ToolButton 
                icon={<Database size={16}/>} 
                label="Log Analyzer" 
                risk="Bajo" 
                onClick={() => handleAction('Log Analyzer', 'analyze_logs', 'Bajo')}
                disabled={isAnalyzing || isCompleted}
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-[10px] text-muted mb-4 uppercase tracking-[0.2em] font-black border-b border-card-border pb-2">Contención</h3>
            <div className="grid grid-cols-1 gap-3">
              <ToolButton 
                icon={<Lock size={16}/>} 
                label="Isolate Host" 
                risk="Alto" 
                onClick={() => handleAction('Isolate Host', 'isolate_host', 'Alto')}
                disabled={isAnalyzing || isCompleted}
              />
              <ToolButton 
                icon={<AlertTriangle size={16}/>} 
                label="Block IP" 
                risk="Medio" 
                onClick={() => handleAction('Block IP', 'block_ip', 'Medio')}
                disabled={isAnalyzing || isCompleted}
              />
            </div>
          </div>

          <div className="mt-auto space-y-4">
             <div className="p-4 rounded-lg bg-primary/5 border border-primary/20 backdrop-blur-sm">
                <p className="text-[10px] text-primary/70 mb-2 font-black uppercase tracking-widest">System Status</p>
                <div className="flex items-center gap-3">
                   <div className={`h-2 w-2 rounded-full ${isAnalyzing ? 'bg-secondary animate-pulse' : 'bg-success'}`} />
                   <span className="text-[10px] font-bold uppercase tracking-tighter">
                    {isAnalyzing ? 'Engine Work...' : 'Online'}
                   </span>
                </div>
             </div>

             <button 
                onClick={completeIncident}
                disabled={isAnalyzing || isCompleted}
                className="w-full py-3 rounded-lg border border-danger/40 bg-danger/5 hover:bg-danger/20 hover:border-danger transition-all flex items-center justify-center gap-2 group disabled:opacity-30 disabled:cursor-not-allowed"
             >
                <ShieldAlert size={16} className="text-danger group-hover:scale-110 transition-transform" />
                <span className="text-[10px] font-black uppercase tracking-widest text-danger">Resolver Incidente</span>
             </button>
          </div>
        </aside>

        {/* CENTER: INCIDENT VISUALIZER */}
        <section className="flex-1 relative bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:32px_32px] overflow-hidden flex flex-col">
          <div className="flex-1 relative">
             <IncidentNodeMap />
             
             {/* OVERLAY DE CARGA */}
             <AnimatePresence>
               {isAnalyzing && (
                 <motion.div 
                   initial={{ opacity: 0 }}
                   animate={{ opacity: 1 }}
                   exit={{ opacity: 0 }}
                   className="absolute inset-0 z-20 bg-background/40 backdrop-blur-[2px] flex items-center justify-center"
                 >
                   <div className="flex flex-col items-center gap-4">
                      <Loader2 className="text-primary animate-spin" size={48} />
                      <span className="text-[10px] font-bold text-primary animate-pulse tracking-[.3em] uppercase">IA Mentor Consultando RAG...</span>
                   </div>
                 </motion.div>
               )}
             </AnimatePresence>
          </div>
          
          {/* ACTION CONSOLE (FLOATING BOTTOM) */}
          <div className="h-48 glass m-6 rounded-xl border border-card-border p-5 flex flex-col shadow-2xl relative overflow-hidden">
             <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-primary/30 to-transparent" />
             <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                   <Terminal className="text-primary" size={14} />
                   <span className="text-[10px] text-muted uppercase font-black tracking-widest">Logs de Ejecución Táctica</span>
                </div>
                <div className="flex items-center gap-2">
                   <div className="h-1.5 w-1.5 rounded-full bg-success" />
                   <span className="text-[10px] text-success font-bold uppercase">Conectado : API Core v1.2</span>
                </div>
             </div>
             <div className="flex-1 font-mono text-[11px] text-primary/70 overflow-y-auto space-y-1.5 custom-scrollbar">
                {logs.map((log) => (
                  <div key={log.id} className="flex gap-4 group">
                    <span className="text-muted w-16 opacity-50">[{log.timestamp}]</span>
                    <span className={`
                      ${log.type === 'success' ? 'text-success' : log.type === 'error' ? 'text-danger' : 'text-primary/90'}
                    `}>
                      {log.message}
                    </span>
                  </div>
                ))}
                <div id="scroll-anchor" />
             </div>
          </div>
        </section>

        {/* RIGHT SIDEBAR: AI MENTOR CONSOLE */}
        <aside className="w-[500px] border-l border-card-border bg-card/30 backdrop-blur-xl flex flex-col overflow-hidden transition-all duration-300">
           <div className="p-6 border-b border-card-border bg-primary/5">
              <div className="flex items-center gap-4">
                 <div className="h-12 w-12 rounded-full border-2 border-primary flex items-center justify-center bg-background glow-primary relative overflow-hidden group">
                    <UserCheck className="text-primary group-hover:scale-110 transition-transform" size={24} />
                    <motion.div 
                      animate={{ y: ['-100%', '200%'] }}
                      transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                      className="absolute left-0 w-full h-1/2 bg-gradient-to-b from-primary/20 to-transparent pointer-events-none"
                    />
                 </div>
                 <div>
                    <h4 className="text-md font-black text-primary tracking-tight leading-none mb-1 uppercase">
                      {currentFeedback?.persona_role || 'SISTEMA MENTOR'}
                    </h4>
                    <div className="flex items-center gap-2">
                       <span className="text-[9px] text-muted uppercase font-bold tracking-widest">Asesor Táctico de Ciberseguridad</span>
                       <div className="h-1 w-1 rounded-full bg-muted" />
                       <span className="text-[9px] text-success font-bold uppercase">Online</span>
                    </div>
                 </div>
              </div>
           </div>

           <div className="flex-1 p-8 overflow-y-auto custom-scrollbar bg-[linear-gradient(rgba(34,211,238,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(34,211,238,0.02)_1px,transparent_1px)] bg-[size:20px_20px] flex flex-col">
              <div className="flex-1">
                <AnimatePresence mode="wait">
                  {currentFeedback ? (
                    <motion.div 
                      key={currentFeedback.explicacion}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="space-y-10"
                    >
                       <div>
                          <div className="flex items-center gap-2 mb-4">
                             <Activity className="text-secondary" size={18} />
                             <h5 className="text-[11px] text-secondary font-black uppercase tracking-widest">Evaluación de la Acción</h5>
                          </div>
                          <p className="text-base leading-relaxed text-foreground/90 font-medium bg-secondary/5 p-6 rounded-lg border-l-4 border-secondary shadow-lg">
                            {currentFeedback.evaluacion}
                          </p>
                       </div>

                       <div>
                          <div className="flex items-center gap-2 mb-4">
                             <Info className="text-primary" size={18} />
                             <h5 className="text-[11px] text-primary font-black uppercase tracking-widest">Por qué es importante?</h5>
                          </div>
                          <p className="text-base leading-relaxed text-muted-foreground italic pl-4 border-l border-primary/20">
                            {currentFeedback.explicacion}
                          </p>
                       </div>

                       <div className="p-6 rounded-xl border border-primary/30 bg-primary/5 space-y-4 shadow-inner">
                          <div className="flex items-center gap-2">
                             <Shield size={20} className="text-primary" />
                             <h5 className="text-[11px] text-primary font-black uppercase tracking-widest">Mejor Práctica Recomendada</h5>
                          </div>
                          <p className="text-base font-bold text-foreground/90">
                             {currentFeedback.mejor_practica}
                          </p>
                       </div>

                       {currentFeedback.fuentes_citadas.length > 0 && (
                          <div className="space-y-4 pt-6 border-t border-card-border">
                             <div className="flex items-center gap-2">
                                <BookOpen size={16} className="text-muted" />
                                <h5 className="text-[10px] text-muted font-black uppercase tracking-[0.2em]">Fuentes Originales (RAG)</h5>
                             </div>
                             <div className="flex flex-wrap gap-3">
                               {currentFeedback.fuentes_citadas.map((src, idx) => (
                                 <span key={idx} className="px-3 py-1.5 rounded bg-background border border-card-border text-[10px] text-muted-foreground font-bold hover:border-primary/40 hover:text-primary transition-colors cursor-help">
                                   {src}
                                 </span>
                               ))}
                             </div>
                          </div>
                       )}
                    </motion.div>
                  ) : (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex flex-col h-full justify-between pb-10"
                    >
                       <div className="space-y-10">
                          <div>
                             <h5 className="text-[11px] text-secondary font-black uppercase tracking-widest mb-6">Briefing de la Operación</h5>
                             <div className="p-8 rounded-xl border border-warning/30 bg-warning/5 relative overflow-hidden group shadow-2xl">
                                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-40 transition-opacity">
                                   <ShieldAlert className="text-warning" size={48} />
                                 </div>
                                <p className="text-xl leading-tight text-foreground relative z-10 font-black mb-6 tracking-tight text-warning/90 uppercase">
                                  [OPERACIÓN: GDPR BREACH]
                                </p>
                                <p className="text-base leading-relaxed text-foreground/80 relative z-10 font-medium">
                                    Error humano masivo detectado: Newsletter enviada con 50,000 correos en CC (visible) en lugar de CCO. 
                                    Como DPO, debes gestionar la contención del servidor SMTP y la notificación obligatoria a la AEPD antes de 72 horas.
                                </p>
                             </div>
                          </div>

                          <div className="p-8 rounded-2xl border border-card-border bg-background/50 italic text-sm text-muted-foreground leading-relaxed relative shadow-inner">
                             <span className="absolute -top-3 left-6 px-3 bg-background text-[10px] font-black text-primary tracking-[0.4em] uppercase">Regla de Oro</span>
                             "En ciberseguridad, la invisibilidad es poder. Un buen analista detecta lo que intenta no ser visto."
                          </div>
                       </div>
                       
                       <div className="mt-12 p-6 border border-card-border rounded-xl bg-card/20 backdrop-blur-sm">
                          <div className="flex items-center gap-3 mb-2">
                            <Activity size={14} className="text-success animate-pulse" />
                            <span className="text-[10px] font-black text-muted uppercase tracking-widest">Mentor Status</span>
                          </div>
                          <p className="text-[11px] text-muted-foreground">Analizando tráfico de red y comparando con normativas RAG locales e internacionales.</p>
                       </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
           </div>
        </aside>

      </main>
    </div>
  );
}

function ToolButton({ icon, label, risk, onClick, disabled }: { icon: React.ReactNode, label: string, risk: string, onClick: () => void, disabled?: boolean }) {
  const riskColor = risk === 'Alto' ? 'text-danger' : risk === 'Medio' ? 'text-secondary' : 'text-success';
  const riskGlow = risk === 'Alto' ? 'hover:shadow-[0_0_15px_rgba(239,68,68,0.2)]' : risk === 'Medio' ? 'hover:shadow-[0_0_15px_rgba(251,191,36,0.2)]' : 'hover:shadow-[0_0_15px_rgba(16,185,129,0.2)]';

  return (
    <button 
      onClick={onClick}
      disabled={disabled}
      className={`
        flex items-center gap-4 px-4 py-3 rounded-lg border border-card-border bg-background/40
        hover:bg-primary/5 hover:border-primary/40 transition-all text-left group relative overflow-hidden
        disabled:opacity-40 disabled:cursor-not-allowed
        ${riskGlow}
      `}
    >
      <div className={`
        h-10 w-10 rounded shadow-inner bg-card-border/20 flex items-center justify-center
        group-hover:text-primary transition-colors
      `}>
        {icon}
      </div>
      <div className="flex-1">
        <div className="text-[11px] font-black uppercase tracking-widest mb-0.5">{label}</div>
        <div className={`text-[8px] uppercase font-black ${riskColor}`}>Factor de Riesgo: {risk}</div>
      </div>
      
      {/* Visual Feedback on hover */}
      <div className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
         <span className="text-primary text-[8px] font-bold">EJECUTAR {'>'}</span>
      </div>
    </button>
  );
}
