/**
 * RESPOND Dilemmas for ar-fintech-idor
 * Generated for NIST CSF 2.0 - RESPOND Function
 * Country: Argentina | Industry: Fintech
 */

import { RespondDilemma } from '../../../types/RespondTypes';

export const ar_fintech_idorRespondDilemmas: RespondDilemma[] = [
  {
    id: 'ar-fintech-respond-01',
    category: 'RS.MA',
    subcategory: 'RS.MA-01',
    title: '📋 ¿Cómo ejecutamos respuesta a incidentes en Fintech?',
    scenario: 'Fintech en Argentina detectó ransomware. No tienen plan de respuesta documentado.',
    options: [
      {
        id: 'A',
        text: 'Improvisar (reunir a todos y decidir)',
        impact: -25,
        explanation: 'Caos y demora'
      },
      {
        id: 'B',
        text: 'Ejecutar Incident Response Plan documentado (NIST 800-61)',
        impact: 15,
        explanation: '✅ NIST RS.MA-01: Plan de respuesta ejecutado'
      },
      {
        id: 'C',
        text: 'Esperar a que vendor responda',
        impact: -20,
        explanation: 'Tiempo crítico perdido'
      },
      {
        id: 'D',
        text: 'Apagar todo y rezar',
        impact: -30,
        explanation: 'Destruye evidencia forense'
      }
    ]
  },
  {
    id: 'ar-fintech-respond-02',
    category: 'RS.AN',
    subcategory: 'RS.AN-03',
    title: '🔬 ¿Cómo analizamos el incidente en Fintech?',
    scenario: 'Incidente en Fintech en Argentina. Necesitan entender qué pasó y alcance.',
    options: [
      {
        id: 'A',
        text: 'Asumir alcance sin investigar',
        impact: -25,
        explanation: 'Puede haber más compromiso oculto'
      },
      {
        id: 'B',
        text: 'Forensics digital + threat hunting + IOC analysis',
        impact: 15,
        explanation: '✅ NIST RS.AN-03: Análisis forense completo'
      },
      {
        id: 'C',
        text: 'Solo revisar logs de firewall',
        impact: -15,
        explanation: 'Visión parcial'
      },
      {
        id: 'D',
        text: 'Esperar a que atacante se manifieste',
        impact: -30,
        explanation: 'Reactivo y peligroso'
      }
    ]
  },
  {
    id: 'ar-fintech-respond-03',
    category: 'RS.MI',
    subcategory: 'RS.MI-01',
    title: '🛑 ¿Cómo contenemos el incidente en Fintech?',
    scenario: 'Malware se está propagando en red de Fintech en Argentina. ¿Acción inmediata?',
    options: [
      {
        id: 'A',
        text: 'Apagar toda la red (nuclear option)',
        impact: -20,
        explanation: 'Detiene negocio innecesariamente'
      },
      {
        id: 'B',
        text: 'Contención quirúrgica: aislar hosts infectados + segmentar red',
        impact: 15,
        explanation: '✅ NIST RS.MI-01: Incidentes contenidos efectivamente'
      },
      {
        id: 'C',
        text: 'Solo desconectar internet',
        impact: -15,
        explanation: 'Malware puede propagarse internamente'
      },
      {
        id: 'D',
        text: 'No contener (observar qué hace el malware)',
        impact: -30,
        explanation: 'Permite daño masivo'
      }
    ]
  },
  {
    id: 'ar-fintech-respond-04',
    category: 'RS.RP',
    subcategory: 'RS.RP-01',
    title: '📢 ¿Cómo comunicamos el incidente en Fintech?',
    scenario: 'Data breach en Fintech en Argentina. Medios empiezan a preguntar.',
    options: [
      {
        id: 'A',
        text: 'Silencio total (ocultar)',
        impact: -25,
        explanation: 'Viola regulaciones y genera desconfianza'
      },
      {
        id: 'B',
        text: 'Comunicación coordinada: interno → regulador → clientes → prensa',
        impact: 15,
        explanation: '✅ NIST RS.RP-01: Plan de comunicación ejecutado'
      },
      {
        id: 'C',
        text: 'Solo comunicar si hay fuga a prensa',
        impact: -20,
        explanation: 'Reactivo y tardío'
      },
      {
        id: 'D',
        text: 'Culpar a proveedor públicamente',
        impact: -30,
        explanation: 'Genera litigios y daña relaciones'
      }
    ]
  },
  {
    id: 'ar-fintech-respond-05',
    category: 'RS.MI',
    subcategory: 'RS.MI-02',
    title: '🔧 ¿Cómo mitigamos el impacto del incidente en Fintech?',
    scenario: 'Fintech en Argentina con incidente activo. ¿Cómo reducimos el impacto?',
    options: [
      {
        id: 'A',
        text: 'Solo restaurar sistemas sin investigar causa',
        impact: -20,
        explanation: 'Reinfección probable'
      },
      {
        id: 'B',
        text: 'Erradicación completa + hardening + monitoreo aumentado',
        impact: 15,
        explanation: '✅ NIST RS.MI-02: Incidentes mitigados efectivamente'
      },
      {
        id: 'C',
        text: 'Parchar solo la vulnerabilidad explotada',
        impact: -10,
        explanation: 'Puede haber backdoors'
      },
      {
        id: 'D',
        text: 'Formatear todo sin análisis',
        impact: -25,
        explanation: 'Destruye evidencia forense'
      }
    ]
  }
];
