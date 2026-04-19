import { create } from 'zustand';

export interface LogEntry {
  id: string;
  timestamp: string;
  message: string;
  type: 'info' | 'success' | 'warning' | 'error';
}

export interface EvaluacionGobernanza {
  compliant: boolean;
  risks: string[];
  recommendations: string[];
  frameworks: string[];
  strategic_score: number;
}

export interface MentorFeedback {
  evaluacion: string;
  explicacion: string;
  mejor_practica: string;
  fuentes_citadas: string[];
  score_tecnico: number;
  persona_role: string;
  evaluacion_gobernanza?: EvaluacionGobernanza;
}

export interface IncidentState {
  level: number;
  phase: string;
  score: number;
  logs: LogEntry[];
  currentFeedback: MentorFeedback | null;
  isAnalyzing: boolean;
  isCompleted: boolean;
  showTechnicalReport: boolean;
  
  // Actions
  addLog: (message: string, type?: LogEntry['type']) => void;
  setFeedback: (feedback: MentorFeedback) => void;
  setAnalyzing: (status: boolean) => void;
  updateScore: (points: number) => void;
  setPhase: (phase: string) => void;
  completeIncident: () => void;
  toggleTechnicalReport: (status?: boolean) => void;
  resetIncident: () => void;
}

export const useIncidentStore = create<IncidentState>((set) => ({
  level: 1,
  phase: 'Detección',
  score: 8500,
  logs: [
    { id: '1', timestamp: '10:42:01', message: 'SEC-CORE INITIALIZED', type: 'info' },
    { id: '2', timestamp: '10:42:05', message: 'ESPERANDO ACCIÓN DEL ANALISTA...', type: 'info' },
  ],
  currentFeedback: null,
  isAnalyzing: false,
  isCompleted: false,
  showTechnicalReport: false,

  addLog: (message, type = 'info') => set((state) => ({
    logs: [
      ...state.logs,
      {
        id: Math.random().toString(36).substr(2, 9),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        message,
        type,
      }
    ]
  })),

  setFeedback: (feedback) => set({ currentFeedback: feedback, isAnalyzing: false }),
  
  setAnalyzing: (status) => set({ isAnalyzing: status }),

  updateScore: (points) => set((state) => ({ score: state.score + points })),

  setPhase: (phase) => set({ phase }),

  completeIncident: () => set({ isCompleted: true, phase: 'Finalizado' }),

  toggleTechnicalReport: (status) => set((state) => ({ 
    showTechnicalReport: status !== undefined ? status : !state.showTechnicalReport 
  })),

  resetIncident: () => set({
    score: 8500,
    phase: 'Detección',
    currentFeedback: null,
    isCompleted: false,
    showTechnicalReport: false,
    logs: [
      { id: '1', timestamp: '10:42:01', message: 'SEC-CORE RESET', type: 'info' },
      { id: '2', timestamp: '10:42:05', message: 'ESPERANDO ACCIÓN DEL ANALISTA...', type: 'info' },
    ]
  }),
}));
