/**
 * DETECT Dilemmas for ar-fintech-idor
 * Generated for NIST CSF 2.0 - DETECT Function
 * Country: Argentina | Industry: Fintech
 */

import { DetectDilemma } from '../../../types/DetectTypes';

export const ar_fintech_idorDetectDilemmas: DetectDilemma[] = [
  {
    id: 'ar-fintech-detect-01',
    category: 'DE.CM',
    subcategory: 'DE.CM-01',
    title: '👁️ ¿Cómo monitoreamos la red de Fintech?',
    scenario: 'Fintech en Argentina no tiene visibilidad de tráfico de red. No saben qué está pasando.',
    options: [
      {
        id: 'A',
        text: 'No monitorear (confiar en firewall)',
        impact: -25,
        explanation: 'Ceguera total'
      },
      {
        id: 'B',
        text: 'SIEM + IDS/IPS + NetFlow analysis',
        impact: 15,
        explanation: '✅ NIST DE.CM-01: Monitoreo continuo de red'
      },
      {
        id: 'C',
        text: 'Solo revisar logs cuando hay incidente',
        impact: -20,
        explanation: 'Reactivo, no preventivo'
      },
      {
        id: 'D',
        text: 'Monitorear solo perímetro (no tráfico interno)',
        impact: -15,
        explanation: 'Ignora amenazas internas'
      }
    ]
  },
  {
    id: 'ar-fintech-detect-02',
    category: 'DE.AE',
    subcategory: 'DE.AE-02',
    title: '🔍 ¿Cómo analizamos eventos en Fintech?',
    scenario: 'SIEM de Fintech en Argentina genera 10,000 alertas/día. Nadie las revisa.',
    options: [
      {
        id: 'A',
        text: 'Ignorar alertas (ruido)',
        impact: -25,
        explanation: 'Incidentes reales se pierden'
      },
      {
        id: 'B',
        text: 'Tuning de alertas + playbooks automatizados + SOC',
        impact: 15,
        explanation: '✅ NIST DE.AE-02: Eventos analizados efectivamente'
      },
      {
        id: 'C',
        text: 'Solo revisar alertas "critical"',
        impact: -10,
        explanation: 'Medium/High también son importantes'
      },
      {
        id: 'D',
        text: 'Outsourcing de análisis (sin contexto)',
        impact: -15,
        explanation: 'Vendor no conoce el negocio'
      }
    ]
  },
  {
    id: 'ar-fintech-detect-03',
    category: 'DE.AE',
    subcategory: 'DE.AE-08',
    title: '🚨 ¿Cuándo declaramos un incidente en Fintech?',
    scenario: 'Fintech en Argentina tiene eventos sospechosos pero no hay criterio para declarar incidente.',
    options: [
      {
        id: 'A',
        text: 'Solo declarar si hay pérdida confirmada de datos',
        impact: -20,
        explanation: 'Muy tarde'
      },
      {
        id: 'B',
        text: 'Criterios claros documentados (severidad + impacto + IOCs)',
        impact: 15,
        explanation: '✅ NIST DE.AE-08: Incidentes declarados según criterios'
      },
      {
        id: 'C',
        text: 'Declarar todo como incidente (falsos positivos)',
        impact: -15,
        explanation: 'Fatiga de alertas'
      },
      {
        id: 'D',
        text: 'Que el CEO decida caso por caso',
        impact: -25,
        explanation: 'No escalable'
      }
    ]
  },
  {
    id: 'ar-fintech-detect-04',
    category: 'DE.DP',
    subcategory: 'DE.DP-03',
    title: '🧪 ¿Cómo testeamos detección en Fintech?',
    scenario: 'Fintech en Argentina nunca probó si sus controles de detección funcionan.',
    options: [
      {
        id: 'A',
        text: 'No testear (asumir que funciona)',
        impact: -25,
        explanation: 'Falsa sensación de seguridad'
      },
      {
        id: 'B',
        text: 'Red Team exercises + MITRE ATT&CK emulation (Atomic Red Team)',
        impact: 15,
        explanation: '✅ NIST DE.DP-03: Procesos de detección testeados'
      },
      {
        id: 'C',
        text: 'Solo testear cuando hay audit',
        impact: -15,
        explanation: 'No continuo'
      },
      {
        id: 'D',
        text: 'Testear en producción sin avisar',
        impact: -20,
        explanation: 'Riesgo de falsos positivos y pánico'
      }
    ]
  },
  {
    id: 'ar-fintech-detect-05',
    category: 'DE.CM',
    subcategory: 'DE.CM-09',
    title: '💻 ¿Monitoreamos endpoints en Fintech?',
    scenario: 'Laptops de empleados de Fintech en Argentina no tienen agente de seguridad.',
    options: [
      {
        id: 'A',
        text: 'Solo antivirus tradicional',
        impact: -20,
        explanation: 'Insuficiente contra malware moderno'
      },
      {
        id: 'B',
        text: 'EDR (CrowdStrike/SentinelOne) + behavioral analysis',
        impact: 15,
        explanation: '✅ NIST DE.CM-09: Hardware/software monitoreado'
      },
      {
        id: 'C',
        text: 'Solo monitorear servers, no endpoints',
        impact: -15,
        explanation: 'Endpoints son vector de ataque común'
      },
      {
        id: 'D',
        text: 'No monitorear (confiar en usuarios)',
        impact: -25,
        explanation: 'Riesgo crítico'
      }
    ]
  }
];
