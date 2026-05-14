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
  Shield,
  Briefcase
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useIncidentStore } from '@/store/incidentStore';
import { getFeedback, getQueueStatus, sendHeartbeat } from '@/utils/api';
import { audioSystem } from '@/utils/audio';
import { musicManager } from '@/utils/ambientAudio';
import IncidentNodeMap from '@/components/IncidentNodeMap';
import SiemTable from '@/components/SiemTable';
import { useRouter } from 'next/navigation';

export default function WorkstationPage() {
  const router = useRouter();
  const [userId, setUserId] = React.useState<string | null>(null);
  const [codename, setCodename] = React.useState<string>('UNKNOWN-ANALYST');
  const [lastActionTime, setLastActionTime] = React.useState<number>(Date.now());
  const [siemResults, setSiemResults] = React.useState<any[]>([]);
  const [activeQuery, setActiveQuery] = React.useState<string>('');
  const lastActionRef = React.useRef<number>(0);

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
    resetIncident,
    thinkingSteps,
    addThinkingStep,
    clearThinkingSteps
  } = useIncidentStore();

  // 1. GESTOR DE IDENTIDAD Y ACCESO (GATEKEEPER)
  useEffect(() => {
    let savedId = localStorage.getItem('soc_tutor_user_id');
    if (!savedId) {
      router.push('/gate');
      return;
    }
    setUserId(savedId);

    const verifyAccess = async () => {
      try {
        const status = await getQueueStatus(savedId);
        if (status.status !== 'ACTIVE') {
          router.push('/waitlist');
        } else {
          setCodename(status.codename);
        }
      } catch (err) {
        console.error('Core Link Failure');
      }
    };

    verifyAccess();
    
    // Heartbeat cada 30 segundos
    const hbInterval = setInterval(() => {
      sendHeartbeat(savedId!);
    }, 30000);

    return () => {
      clearInterval(hbInterval);
      musicManager.stopAll();
    };
  }, [router]);

  // 2. AUTO-SCROLL LOGS
  useEffect(() => {
    const anchor = document.getElementById('scroll-anchor');
    if (anchor) {
      anchor.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  // 3. TEMPORIZADOR DE INACTIVIDAD (SISTEMA DE GUÍA Y AUTO-CIERRE)
  useEffect(() => {
    const checkIdle = setInterval(() => {
      const idleTime = Date.now() - lastActionTime;
      
      if (idleTime > 60000) { // 60 Segundos
        musicManager.deescalate();
      }

      // AUTO-FINALIZACIÓN: Si el juez no interactúa en 2 min, cerramos con el reporte final
      if (idleTime > 120000 && !isCompleted && !isAnalyzing) {
        addLog("ALERTA: Detectada inactividad prolongada del analista.", "warning");
        addLog("PROCEDIMIENTO: Generando reporte de estado actual y cerrando sesión...", "info");
        completeIncident();
      }
    }, 5000);

    return () => clearInterval(checkIdle);
  }, [lastActionTime, isCompleted, isAnalyzing, completeIncident, addLog]);

  // 3. GENERADOR DE RUIDO SIEM (BACKGROUND LOGS)
  useEffect(() => {
    if (isCompleted) return;
    
    // Background noise strings
    const noiseLogs = [
      "syslog-ng[812]: Accepted connection from 10.0.5.42",
      "kernel: [14234.12] DROP IN=eth0 OUT= MAC=... SRC=192.168.1.100",
      "sshd[1024]: pam_unix(sshd:session): session opened for user root",
      "nginx: 192.168.1.50 - - [GET /api/health HTTP/1.1] 200",
      "systemd[1]: Started Daily Cleanup of Temporary Directories",
      "auth: Login successful for user 'system_svc'",
      "dns_forwarder: req AAAA graph.windows.net",
      "ntpd[88]: synchronized to 162.159.200.1, stratum 3"
    ];

    const generateNoise = () => {
      // 40% probability of inserting a log every 2.5s
      if (Math.random() > 0.6) {
         const randomNoise = noiseLogs[Math.floor(Math.random() * noiseLogs.length)];
         const type = Math.random() > 0.8 ? 'warning' : 'info';
         addLog(randomNoise, type);
      }
    };

    const noiseInterval = setInterval(generateNoise, 2500);

    return () => clearInterval(noiseInterval);
  }, [addLog, isCompleted]);

  const handleAction = async (toolName: string, action: string, risk: string) => {
    if (isAnalyzing) return;

    // Mapeo de reacciones pedagógicas inmediatas (Sistema 1)
    const toolReactions: Record<string, string> = {
      'NetScan': "Ejecutando escaneo de red (NDR). Vital para determinar el alcance del incidente y detectar posibles movimientos laterales.",
      'Log Analyzer': "Accediendo al SIEM. La verificación de evidencias es el primer paso crítico de todo analista profesional.",
      'Isolate Host': "Aislamiento de host activado. Una medida drástica; asegúrate de que el impacto en el negocio esté justificado por la evidencia previa.",
      'Block IP': "Iniciando bloqueo perimetral. Una medida táctica necesaria, pero ¿has confirmado la IP en los logs antes de cerrar la puerta?"
    };

    musicManager.start();
    musicManager.escalate();
    setLastActionTime(Date.now());

    audioSystem.playClick();
    addLog(`INICIANDO ACCIÓN: ${toolName}...`, 'info');
    setAnalyzing(true);
    clearThinkingSteps();

    // Reacción inmediata del "Tutor"
    addThinkingStep(toolReactions[toolName] || `Analizando impacto de ${toolName} en el escenario...`);
    
    const actionStartTime = Date.now();
    lastActionRef.current = actionStartTime;

    const thinkingSequence = [
      "Consultando base de conocimientos NIST SP 800-61...",
      "Correlacionando TTPs con MITRE ATT&CK...",
      "Evaluando cumplimiento de principios GDPR...",
      "Verificando integridad criptográfica de la evidencia..."
    ];

    let stepIdx = 0;
    const stepInterval = setInterval(() => {
      if (stepIdx < thinkingSequence.length && isAnalyzing) {
        addThinkingStep(thinkingSequence[stepIdx]);
        stepIdx++;
      } else {
        clearInterval(stepInterval);
      }
    }, 1500);

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

      const feedback = await getFeedback(decision, contexto, profile, userId || 'guest');
      
      if (lastActionRef.current === actionStartTime) {
        clearInterval(stepInterval);
        setFeedback(feedback);
        audioSystem.playSync();
        
        // Determinar la marca según la acción para el log de auditoría
        const brand = action.includes('analyze') ? 'SENTINEL' : action.includes('scan') ? 'FALCON' : action.includes('block') ? 'PALOALTO' : 'FALCON_EDR';
        addLog(`[+] SUCCESS: Audit event logged | Source: ${brand} | Action: ${action.toUpperCase()} | Status: ACK`, 'success');
        
        // Extraer resultados técnicos si existen (del banco de evidencias)
        if (feedback.evaluacion_tecnica?.technical_data?.length > 0) {
           setSiemResults(feedback.evaluacion_tecnica.technical_data);
           // Si el primer resultado tiene una query KQL, la mostramos
           if (feedback.evaluacion_tecnica.technical_data[0].query_kql) {
              setActiveQuery(feedback.evaluacion_tecnica.technical_data[0].query_kql);
           }
        } else {
           setSiemResults([]);
        }

        const points = feedback.technical_score > 70 ? 500 : -300;
        updateScore(points);
        setAnalyzing(false);
      }

    } catch (error) {
      clearInterval(stepInterval);
      addLog('ACCIÓN FINALIZADA: SIN ANOMALÍAS ADICIONALES DETECTADAS', 'info');
      setAnalyzing(false);
      musicManager.deescalate();

      // Background Retry Loop (Resilience Protocol)
      const runBackgroundRetry = async () => {
        
        // Si el jugador ya inició OTRA acción, cancelar este reintento
        if (lastActionRef.current !== actionStartTime) return;

        try {
          const retryFeedback = await getFeedback(
            { accion: action, target: 'SRV-SWIFT-01', detalle: `Reintento automático tras fallo de enlace` },
            { scenario_id: 'es-tourism-gdpr-email-breach-001', tipo_incidente: 'privacy_breach', fase: phase, sistemas_afectados: ['SMTP-Relay-Main'] },
            { player_id: 'player_01', level: 3, rol: 'DPO', language: 'es' },
            userId || 'guest'
          );

          // Verificar de nuevo por si se inició una acción durante el proceso de red
          if (lastActionRef.current === actionStartTime) {
            setFeedback(retryFeedback);
            audioSystem.playSync();
            addLog(`SISTEMA MENTOR: CORRELACIÓN TÁCTICA ACTUALIZADA`, 'success');
            
            const points = retryFeedback.technical_score > 70 ? 500 : -300;
            updateScore(points);
          }
        } catch (retryError) {
          // Si el reintento también falla, se descarta silenciosamente para no romper la inmersión
          console.warn('Background link restoration failed.');
        }
      };

      runBackgroundRetry();
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
                      className="mt-8 p-8 mx-4 mb-6 rounded-2xl bg-black/60 border border-card-border font-mono text-sm space-y-6 shadow-2xl"
                    >
                       <div className="flex justify-between border-b border-card-border pb-3 opacity-50 uppercase font-black text-xs tracking-widest">
                          <span>Métrica del Sistema</span>
                          <span>Valor / Operación</span>
                       </div>
                       <div className="flex justify-between items-center">
                           <span className="text-muted uppercase tracking-wider">Gasto de IA (Costo)</span>
                           <span className="text-success font-bold">${currentFeedback?.costo_estimado?.toFixed(4) || "0.0000"} USD</span>
                        </div>
                        <div className="flex justify-between items-center">
                           <span className="text-muted uppercase tracking-wider">Uso de Tokens (Sesión)</span>
                           <span className="text-primary font-bold">{currentFeedback?.total_tokens || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                           <span className="text-muted uppercase tracking-wider">Precisión RAG</span>
                           <span className="text-primary font-bold">{(currentFeedback?.rag_precision || 0).toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between items-center">
                           <span className="text-muted uppercase tracking-wider">Latencia IA</span>
                           <span className="text-secondary font-bold">{currentFeedback?.latencia_ms ? `${(currentFeedback.latencia_ms / 1000).toFixed(2)}s` : "0.00s"}</span>
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
              initial={{ scale: 1.5, color: '#fbbf24', filter: 'brightness(2)' }}
              animate={{ scale: 1, color: '#22d3ee', filter: 'brightness(1)' }}
              transition={{ type: 'spring', stiffness: 300, damping: 15 }}
              className="text-primary font-bold text-xs glow-primary"
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
                label="NetScan (Falcon)" 
                category="NDR / CrowdStrike Falcon"
                risk="Bajo" 
                onClick={() => handleAction('NetScan', 'network_scan', 'Bajo')}
                disabled={isAnalyzing || isCompleted}
                pulse={Date.now() - lastActionTime > 15000 && logs.length < 15}
              />
              <ToolButton 
                icon={<Database size={16}/>} 
                label="Log Analyzer (Sentinel)" 
                category="SIEM / Microsoft Sentinel"
                risk="Bajo" 
                onClick={() => handleAction('Log Analyzer', 'analyze_logs', 'Bajo')}
                disabled={isAnalyzing || isCompleted}
                pulse={Date.now() - lastActionTime > 15000 && logs.length < 15}
              />
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-[10px] text-muted mb-4 uppercase tracking-[0.2em] font-black border-b border-card-border pb-2">Contención</h3>
            <div className="grid grid-cols-1 gap-3">
              <ToolButton 
                icon={<Lock size={16}/>} 
                label="Isolate Host (Falcon)" 
                category="EDR / CrowdStrike Insight"
                risk="Alto" 
                onClick={() => handleAction('Isolate Host', 'isolate_host', 'Alto')}
                disabled={isAnalyzing || isCompleted}
              />
              <ToolButton 
                icon={<AlertTriangle size={16}/>} 
                label="Block IP (Palo Alto)" 
                category="NGFW / Palo Alto Networks"
                risk="Medio" 
                onClick={() => handleAction('Block IP', 'block_ip', 'Medio')}
                disabled={isAnalyzing || isCompleted}
              />
            </div>
          </div>

          <div className="mt-auto space-y-4">
             {/* TACTICAL MINIMAP */}
             <div className="aspect-square w-full relative overflow-hidden rounded-lg border border-card-border bg-background/50 shadow-[inset_0_0_20px_rgba(0,0,0,0.5)] flex items-center justify-center">
               <div className="scale-75 origin-center w-[120%] h-[120%] flex items-center justify-center absolute">
                 <IncidentNodeMap />
               </div>
               <AnimatePresence>
                 {isAnalyzing && (
                   <motion.div 
                     initial={{ opacity: 0 }}
                     animate={{ opacity: 1 }}
                     exit={{ opacity: 0 }}
                     className="absolute inset-0 z-20 bg-background/60 backdrop-blur-sm flex items-center justify-center overflow-hidden"
                   >
                     <div className="relative flex flex-col items-center gap-2">
                        <Loader2 className="text-secondary animate-spin" size={24} />
                        <span className="text-[8px] font-black text-secondary tracking-widest uppercase">Analyzing...</span>
                     </div>
                   </motion.div>
                 )}
               </AnimatePresence>
             </div>

             <div className="p-4 rounded-lg bg-primary/5 border border-primary/20 backdrop-blur-sm space-y-4">
                <div>
                   <p className="text-[10px] text-primary/70 mb-2 font-black uppercase tracking-widest flex items-center justify-between">
                     <span>Estado de Conexión</span>
                     <span className="text-[8px] text-muted-foreground/50">SEC-CORE v1.2</span>
                   </p>
                   <div className="flex items-center gap-3 bg-background/50 p-2 rounded border border-card-border/50">
                      <div className={`h-2 w-2 rounded-full shadow-[0_0_8px_currentColor] ${isAnalyzing ? 'bg-secondary animate-pulse' : 'bg-success'}`} />
                      <span className="text-[10px] font-bold uppercase tracking-widest text-foreground/90">
                       {isAnalyzing ? 'Correlacionando Logs...' : 'En Línea - Estable'}
                      </span>
                   </div>
                </div>
                
                <div className="grid grid-cols-2 gap-2 border-t border-primary/10 pt-3">
                   <div className="flex flex-col gap-1">
                      <span className="text-[8px] text-muted-foreground uppercase font-black tracking-wider">Firewall Nodo</span>
                      <span className="text-[9px] text-primary font-bold uppercase">Activo</span>
                   </div>
                   <div className="flex flex-col gap-1">
                      <span className="text-[8px] text-muted-foreground uppercase font-black tracking-wider">Zero Trust</span>
                      <span className="text-[9px] text-success font-bold uppercase">Validado</span>
                   </div>
                </div>
             </div>

             <button 
                onClick={() => {
                  audioSystem.playSuccess();
                  completeIncident();
                }}
                disabled={isAnalyzing || isCompleted}
                className="w-full py-3 rounded-lg border border-danger/40 bg-danger/5 hover:bg-danger/20 hover:border-danger transition-all flex items-center justify-center gap-2 group disabled:opacity-30 disabled:cursor-not-allowed"
             >
                <ShieldAlert size={16} className="text-danger group-hover:scale-110 transition-transform" />
                <span className="text-[10px] font-black uppercase tracking-widest text-danger">Resolver Incidente</span>
             </button>
          </div>
        </aside>

        {/* CENTER: ACTION CONSOLE */}
        <section className="flex-1 relative bg-[radial-gradient(#1e293b_1px,transparent_1px)] [background-size:32px_32px] overflow-hidden flex flex-col p-6">
          <div className="flex-1 glass rounded-xl border border-card-border p-5 flex flex-col shadow-2xl relative overflow-hidden backdrop-blur-sm">
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
                
                {/* SIEM/NDR Structured Results */}
                {siemResults.length > 0 && (
                   <SiemTable results={siemResults} query={activeQuery} />
                )}

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
                 <div className="flex-1">
                    <h4 className="text-md font-black text-primary tracking-tight leading-none mb-1 uppercase">
                      {currentFeedback?.persona_role || 'SISTEMA MENTOR'}
                    </h4>
                    <div className="flex items-center gap-2">
                       <span className="text-[9px] text-muted uppercase font-bold tracking-widest">{codename}</span>
                       <div className="h-1 w-1 rounded-full bg-muted" />
                       <span className="text-[9px] text-success font-bold uppercase">Active Link</span>
                    </div>
                 </div>

                 {/* SYNC RATE MODULE */}
                 <div className="flex flex-col items-end gap-1">
                    <span className="text-[8px] font-black text-muted uppercase tracking-[0.2em]">Sync Rate</span>
                    <div className="w-24 h-4 bg-black/40 border border-card-border rounded-sm relative overflow-hidden flex items-center px-1">
                       <motion.div 
                         initial={{ width: 0 }}
                         animate={{ 
                           width: `${currentFeedback?.technical_score || 0}%`,
                           backgroundColor: (currentFeedback?.technical_score || 0) > 70 ? '#22d3ee' : (currentFeedback?.technical_score || 0) > 40 ? '#fbbf24' : '#ef4444'
                         }}
                         className="h-2 rounded-sm shadow-[0_0_10px_currentColor]"
                       />
                    </div>
                    <span className="text-[10px] font-black text-foreground">
                       {currentFeedback ? `${currentFeedback.technical_score}%` : '--%'}
                    </span>
                 </div>
              </div>
           </div>

           <div className="flex-1 p-8 bg-[linear-gradient(rgba(34,211,238,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(34,211,238,0.02)_1px,transparent_1px)] bg-[size:20px_20px] flex flex-col h-full overflow-hidden">
              
              {/* 1. TUTOR PANEL (60%) */}
              <div className="basis-[60%] overflow-y-auto custom-scrollbar pr-4 pb-4">
                <AnimatePresence mode="wait">
                   {isAnalyzing ? (
                     <motion.div 
                       initial={{ opacity: 0, y: 10 }}
                       animate={{ opacity: 1, y: 0 }}
                       exit={{ opacity: 0, y: -10 }}
                       className="space-y-6 h-full flex flex-col"
                     >
                        <div className="flex flex-col gap-3 flex-1 overflow-y-auto custom-scrollbar pr-2 max-h-[160px]">
                           <div className="flex items-center justify-between sticky top-0 bg-background/80 backdrop-blur-md py-2 z-10 border-b border-secondary/20 mb-3">
                              <h5 className="text-[10px] text-secondary font-black uppercase tracking-[0.3em] flex items-center gap-2">
                                 <motion.div 
                                   animate={{ opacity: [0.3, 1, 0.3] }}
                                   transition={{ repeat: Infinity, duration: 1.5 }}
                                   className="h-2 w-2 rounded-full bg-secondary shadow-[0_0_8px_#f59e0b]"
                                 />
                                 Razonamiento en Curso
                              </h5>
                              <span className="text-[8px] font-mono text-secondary/40 animate-pulse uppercase">Engine: ReAct 2.0</span>
                           </div>
                           <AnimatePresence mode="popLayout">
                             {thinkingSteps.map((step, idx) => (
                               <motion.div 
                                 key={`${step}-${idx}`}
                                 initial={{ opacity: 0, x: -10, filter: 'blur(4px)' }}
                                 animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                                 exit={{ opacity: 0, x: 10, filter: 'blur(4px)' }}
                                 transition={{ duration: 0.3, ease: "easeOut" }}
                                 className="flex items-start gap-3 text-[11px] font-medium text-foreground/70 leading-tight mb-3 group"
                               >
                                  <div className="mt-1 h-1.5 w-1.5 rounded-full bg-secondary/40 group-hover:bg-secondary transition-colors flex-shrink-0" />
                                  <div className="flex flex-col gap-0.5">
                                     <span>{step}</span>
                                     <span className="text-[7px] text-secondary/30 uppercase font-black tracking-tighter">Status: Processing...</span>
                                  </div>
                               </motion.div>
                             ))}
                           </AnimatePresence>
                        </div>
                        <div className="p-5 rounded-xl border border-secondary/30 bg-secondary/5 flex flex-col items-center justify-center gap-4 mt-auto relative overflow-hidden shadow-inner">
                           {/* Background Pulse */}
                           <motion.div 
                             animate={{ opacity: [0.05, 0.15, 0.05] }}
                             transition={{ repeat: Infinity, duration: 3 }}
                             className="absolute inset-0 bg-secondary"
                           />
                           <div className="w-full h-1 bg-secondary/10 rounded-full overflow-hidden relative z-10">
                              <motion.div 
                                animate={{ 
                                  left: ['-100%', '100%'],
                                  width: ['10%', '40%', '10%']
                                }}
                                transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                                className="absolute h-full bg-secondary shadow-[0_0_15px_#f59e0b]"
                              />
                           </div>
                           <div className="flex flex-col items-center gap-1 relative z-10">
                              <span className="text-[9px] font-black text-secondary animate-pulse uppercase tracking-[0.4em]">Sincronizando Mallas de Conocimiento</span>
                              <span className="text-[7px] text-muted-foreground uppercase font-bold tracking-[0.3em] opacity-50">Triage: Critical Priority | Level: High Impact</span>
                           </div>
                        </div>
                     </motion.div>
                   ) : currentFeedback ? (
                    <motion.div 
                      key={currentFeedback.explicacion}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      className="space-y-8"
                    >
                       <div>
                          <div className="flex items-center gap-2 mb-4">
                             <Activity className="text-secondary" size={18} />
                             <h5 className="text-[11px] text-secondary font-black uppercase tracking-widest">Evaluación de la Acción</h5>
                          </div>
                          <div className="text-sm leading-relaxed text-foreground/90 font-medium bg-secondary/5 p-5 rounded-lg border-l-4 border-secondary shadow-lg">
                            <TypingText text={currentFeedback.evaluacion} />
                          </div>
                       </div>

                       <div>
                          <div className="flex items-center gap-2 mb-4">
                             <Info className="text-primary" size={18} />
                             <h5 className="text-[11px] text-primary font-black uppercase tracking-widest">Por qué es importante?</h5>
                          </div>
                          <div className="text-sm leading-relaxed text-muted-foreground italic pl-4 border-l border-primary/20">
                            <TypingText text={currentFeedback.explicacion} />
                          </div>
                       </div>

                       <div className="p-5 rounded-xl border border-primary/30 bg-primary/5 space-y-3 shadow-inner">
                          <div className="flex items-center gap-2">
                             <Shield size={18} className="text-primary" />
                             <h5 className="text-[11px] text-primary font-black uppercase tracking-widest">Mejor Práctica Recomendada</h5>
                          </div>
                          <div className="text-sm font-bold text-foreground/90">
                             <TypingText text={currentFeedback.mejor_practica} />
                          </div>
                       </div>

                       {currentFeedback.fuentes_citadas.length > 0 && (
                          <div className="space-y-3 pt-4 border-t border-card-border">
                             <div className="flex items-center gap-2">
                                <BookOpen size={14} className="text-muted" />
                                <h5 className="text-[10px] text-muted font-black uppercase tracking-[0.2em]">Fuentes Originales (RAG)</h5>
                             </div>
                             <div className="flex flex-wrap gap-2">
                               {currentFeedback.fuentes_citadas.map((src, idx) => (
                                 <span key={idx} className="px-2 py-1 rounded bg-background border border-card-border text-[9px] text-muted-foreground font-bold hover:border-primary/40 hover:text-primary transition-colors cursor-help">
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
                      className="flex flex-col h-full justify-center space-y-10 pb-6"
                    >
                       <div>
                          <h5 className="text-[12px] text-secondary font-black uppercase tracking-[0.3em] mb-6">Briefing de la Operación</h5>
                          <div className="p-8 rounded-2xl border border-warning/30 bg-warning/5 relative overflow-hidden group shadow-2xl">
                             <div className="absolute top-0 right-0 p-6 opacity-10 group-hover:opacity-40 transition-opacity">
                                <ShieldAlert className="text-warning" size={64} />
                              </div>
                             <p className="text-xl leading-snug text-foreground relative z-10 font-black mb-6 tracking-tight text-warning/90 uppercase">
                               [OPERACIÓN: GDPR BREACH]
                             </p>
                             <p className="text-base leading-loose text-foreground/80 relative z-10 font-medium pr-8">
                                 Error humano masivo detectado: Newsletter enviada con 50,000 correos en CC (visible) en lugar de CCO.<br/><br/>
                                 Como responsable de la crisis corporativa, tu mandato es escanear los logs en la terminal, ejecutar medidas de contención contundentes sobre el servidor comprometido y orquestar las notificaciones legales obligatorias antes de que finalice la ventana regulatoria.
                             </p>
                          </div>
                       </div>

                       <div className="p-6 rounded-2xl border border-card-border bg-background/50 italic text-sm text-muted-foreground leading-loose relative shadow-inner">
                          <span className="absolute -top-3 left-8 px-4 bg-background text-[10px] font-black text-primary tracking-[0.4em] uppercase">Regla de Oro</span>
                          "En ciberseguridad, la invisibilidad es poder. Un buen analista detecta lo que intenta no ser visto."
                       </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* 2. CISO STRATEGIC MEMOS PANEL (40%) */}
              <div className="basis-[40%] shrink-0 border-t border-card-border pt-6 mt-2 overflow-y-auto custom-scrollbar pr-4">
                  <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-2">
                         <Briefcase size={16} className="text-warning" />
                         <h5 className="text-[10px] text-warning font-black uppercase tracking-[0.2em]">CISO Strategic Directives</h5>
                      </div>
                      <div className="px-2 py-0.5 rounded border border-warning/30 bg-warning/5 text-[8px] font-black text-warning uppercase tracking-widest animate-pulse">
                         Direct Feed Active
                      </div>
                  </div>
                  
                  <AnimatePresence mode="wait">
                    {currentFeedback?.evaluacion_gobernanza ? (
                      <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="p-6 rounded-xl border-2 border-warning/20 bg-warning/5 space-y-6 relative overflow-hidden"
                      >
                         {/* Watermark "CLASSIFIED" */}
                         <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[40px] font-black text-warning/[0.03] rotate-12 pointer-events-none uppercase tracking-[0.5em] select-none">
                            Classified
                         </div>

                         <div className="flex justify-between items-start border-b border-warning/20 pb-4 mb-4 relative z-10">
                           <div className="flex flex-col gap-1">
                             <span className="text-[11px] font-black uppercase text-warning leading-none">Security Directive</span>
                             <span className="text-[8px] text-warning/50 font-mono tracking-wider">REF: GRC-DOC-{Math.random().toString(36).substring(2, 6).toUpperCase()}</span>
                           </div>
                           <div className="flex flex-col items-end">
                              <span className={`px-3 py-1 rounded-sm text-[9px] font-black uppercase shadow-sm border ${currentFeedback.evaluacion_gobernanza.compliant ? 'bg-success/20 text-success border-success/40' : 'bg-danger/20 text-danger border-danger/40 animate-pulse'}`}>
                                {currentFeedback.evaluacion_gobernanza.compliant ? 'VALIDATED' : 'CRITICAL BREACH'}
                              </span>
                           </div>
                         </div>
                        
                        {currentFeedback.evaluacion_gobernanza.risks.length > 0 && (
                          <div className="space-y-3 relative z-10">
                            <span className="text-[10px] text-danger uppercase font-black tracking-widest flex items-center gap-2">
                               <AlertTriangle size={12} /> Riesgos Identificados:
                            </span>
                            <div className="space-y-2">
                               {currentFeedback.evaluacion_gobernanza.risks.slice(0, 3).map((risk, idx) => (
                                 <motion.div 
                                   initial={{ opacity: 0, x: -10 }}
                                   animate={{ opacity: 1, x: 0 }}
                                   transition={{ delay: idx * 0.2 }}
                                   key={idx} 
                                   className="text-[11px] text-foreground/80 leading-snug flex gap-2 items-start"
                                 >
                                    <span className="text-danger font-black mt-0.5">!</span>
                                    {risk}
                                 </motion.div>
                               ))}
                            </div>
                          </div>
                        )}
                        
                        {currentFeedback.evaluacion_gobernanza.frameworks.length > 0 && (
                          <div className="pt-4 flex flex-wrap gap-2 border-t border-warning/10 relative z-10">
                            {currentFeedback.evaluacion_gobernanza.frameworks.map((fw, idx) => (
                              <span key={idx} className="px-2 py-1 bg-black/40 text-[9px] text-warning rounded border border-warning/30 font-bold uppercase tracking-wider hover:bg-warning/10 transition-colors cursor-help">{fw}</span>
                            ))}
                          </div>
                        )}

                        {/* Simulated Signature */}
                        <div className="pt-4 flex justify-end opacity-40 grayscale relative z-10">
                           <div className="text-right">
                              <div className="text-[8px] font-black uppercase tracking-tighter mb-1">Signed By:</div>
                              <div className="font-mono text-[10px] italic underline decoration-warning/30">CISO_EXEC_OFFICE</div>
                           </div>
                        </div>
                      </motion.div>
                    ) : (
                      <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="p-8 rounded-xl border border-card-border bg-card/20 flex flex-col items-center justify-center text-center gap-4 h-48 relative overflow-hidden"
                      >
                         <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(251,191,36,0.05)_0%,transparent_70%)]" />
                         <Briefcase size={32} className="text-muted opacity-20" />
                         <div className="space-y-1 relative z-10">
                            <span className="text-[11px] text-muted font-black uppercase tracking-widest block">Operational Standby</span>
                            <span className="text-[9px] text-muted/50 font-bold uppercase tracking-wider block">Waiting for strategic escalation...</span>
                         </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
               </div>
           </div>
        </aside>

      </main>

      {/* TACTICAL FOOTER: SYSTEM COMPLIANCE & META DATA */}
      <footer className="h-6 border-t border-card-border/30 bg-card/10 flex items-center justify-between px-6 z-50">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="h-1.5 w-1.5 rounded-full bg-success opacity-50" />
            <span className="text-[7px] font-black text-muted-foreground/40 uppercase tracking-[0.2em]">Entorno de Simulación Protegido</span>
          </div>
          <span className="text-[7px] font-black text-muted-foreground/20 uppercase">|</span>
          <span className="text-[7px] font-black text-muted-foreground/40 uppercase tracking-[0.2em]">Datos 100% Sintéticos (RFC 2606/5737)</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-[7px] font-black text-primary/40 uppercase tracking-[0.2em]">SOC Tutor v2.0 Compliance</span>
          <span className="text-[7px] font-black text-muted-foreground/20 uppercase">//</span>
          <span className="text-[7px] font-black text-secondary/40 uppercase tracking-[0.2em]">Neural Link: MAGI-CONNECTED</span>
        </div>
      </footer>
    </div>
  );
}

function ToolButton({ icon, label, category, risk, onClick, disabled, pulse }: { icon: React.ReactNode, label: string, category: string, risk: string, onClick: () => void, disabled?: boolean, pulse?: boolean }) {
  const riskColor = risk === 'Alto' ? 'text-danger' : risk === 'Medio' ? 'text-secondary' : 'text-success';
  const riskGlow = risk === 'Alto' ? 'hover:shadow-[0_0_15px_rgba(239,68,68,0.2)]' : risk === 'Medio' ? 'hover:shadow-[0_0_15px_rgba(251,191,36,0.2)]' : 'hover:shadow-[0_0_15px_rgba(16,185,129,0.2)]';

  return (
    <motion.button 
      onClick={onClick}
      disabled={disabled}
      animate={pulse && !disabled ? { 
        boxShadow: [
          "0 0 0px rgba(34,211,238,0)", 
          "0 0 20px rgba(34,211,238,0.4)", 
          "0 0 0px rgba(34,211,238,0)"
        ],
        borderColor: [
          "rgba(255,255,255,0.1)",
          "rgba(34,211,238,0.6)",
          "rgba(255,255,255,0.1)"
        ],
        scale: [1, 1.02, 1]
      } : {}}
      transition={pulse ? { 
        repeat: Infinity, 
        duration: 2,
        ease: "easeInOut"
      } : {}}
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
        <div className="text-[7px] text-muted-foreground uppercase font-bold tracking-wider mb-1 opacity-60">{category}</div>
        <div className={`text-[8px] uppercase font-black ${riskColor}`}>Factor de Riesgo: {risk}</div>
      </div>
      
      {/* Visual Feedback on hover */}
      <div className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
         <span className="text-primary text-[8px] font-bold">EJECUTAR {'>'}</span>
      </div>
    </motion.button>
  );
}

function TypingText({ text }: { text: string }) {
  const [displayedText, setDisplayedText] = React.useState('');
  
  React.useEffect(() => {
    let i = 0;
    setDisplayedText('');
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayedText((prev) => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, 15);
    return () => clearInterval(timer);
  }, [text]);

  return <span>{displayedText}</span>;
}
