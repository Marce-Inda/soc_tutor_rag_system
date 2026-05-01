/**
 * RECOVER Dilemmas for ar-fintech-idor
 * Generated for NIST CSF 2.0 - RECOVER Function
 * Country: Argentina | Industry: Fintech
 */

import { RecoverDilemma } from '../../../types/RecoverTypes';

export const ar_fintech_idorRecoverDilemmas: RecoverDilemma[] = [
  {
    id: 'ar-fintech-recover-01',
    category: 'RC.RP',
    subcategory: 'RC.RP-01',
    title: '🔄 ¿Cómo ejecutamos recovery en Fintech?',
    scenario: 'Fintech en Argentina después de ransomware. Necesitan recuperar operaciones.',
    options: [
      {
        id: 'A',
        text: 'Restaurar backups sin validar integridad',
        impact: -20,
        explanation: 'Riesgo de reinfección'
      },
      {
        id: 'B',
        text: 'Recovery Plan: validar backups + sanitizar + restaurar por prioridad',
        impact: 15,
        explanation: '✅ NIST RC.RP-01: Plan de recuperación ejecutado'
      },
      {
        id: 'C',
        text: 'Reconstruir todo desde cero',
        impact: -15,
        explanation: 'Demora innecesaria si hay backups'
      },
      {
        id: 'D',
        text: 'Pagar rescate y esperar decryptor',
        impact: -25,
        explanation: 'No garantiza recuperación'
      }
    ]
  },
  {
    id: 'ar-fintech-recover-02',
    category: 'RC.CO',
    subcategory: 'RC.CO-01',
    title: '📢 ¿Cómo manejamos relaciones públicas post-incidente en Fintech?',
    scenario: 'Después de breach en Fintech en Argentina, reputación dañada en redes sociales.',
    options: [
      {
        id: 'A',
        text: 'Ignorar críticas (se olvidarán)',
        impact: -25,
        explanation: 'Daño permanente a marca'
      },
      {
        id: 'B',
        text: 'Campaña de transparencia + lecciones aprendidas + compensación',
        impact: 15,
        explanation: '✅ NIST RC.CO-01: RRPP gestionadas proactivamente'
      },
      {
        id: 'C',
        text: 'Contratar bots para contrarrestar críticas',
        impact: -30,
        explanation: 'Antiético y contraproducente'
      },
      {
        id: 'D',
        text: 'Amenazar legalmente a críticos',
        impact: -35,
        explanation: 'Efecto Streisand'
      }
    ]
  },
  {
    id: 'ar-fintech-recover-03',
    category: 'RC.RP',
    subcategory: 'RC.RP-06',
    title: '💪 ¿Cómo mejoramos resiliencia post-incidente en Fintech?',
    scenario: 'Fintech en Argentina se recuperó de incidente. ¿Cómo prevenir recurrencia?',
    options: [
      {
        id: 'A',
        text: 'No hacer nada (lightning doesn\'t strike twice)',
        impact: -30,
        explanation: 'Garantiza reincidencia'
      },
      {
        id: 'B',
        text: 'Lessons Learned + remediation plan + chaos engineering',
        impact: 15,
        explanation: '✅ NIST RC.RP-06: Resiliencia mejorada basado en lecciones'
      },
      {
        id: 'C',
        text: 'Solo parchear la vulnerabilidad específica',
        impact: -15,
        explanation: 'No aborda causas raíz'
      },
      {
        id: 'D',
        text: 'Culpar y despedir responsables',
        impact: -20,
        explanation: 'Cultura de miedo, no aprendizaje'
      }
    ]
  },
  {
    id: 'ar-fintech-recover-04',
    category: 'RC.RP',
    subcategory: 'RC.RP-04',
    title: '📊 ¿Cómo medimos efectividad de recovery en Fintech?',
    scenario: 'Fintech en Argentina se recuperó en 72h. ¿Fue suficientemente rápido?',
    options: [
      {
        id: 'A',
        text: 'No medir (al menos nos recuperamos)',
        impact: -20,
        explanation: 'No hay baseline para mejorar'
      },
      {
        id: 'B',
        text: 'Métricas: RTO/RPO actual vs objetivo + post-mortem',
        impact: 15,
        explanation: '✅ NIST RC.RP-04: Efectividad de recuperación evaluada'
      },
      {
        id: 'C',
        text: 'Comparar con tiempo de otros incidentes',
        impact: -10,
        explanation: 'Cada incidente es diferente'
      },
      {
        id: 'D',
        text: 'Preguntar al CEO si está satisfecho',
        impact: -15,
        explanation: 'Subjetivo, no basado en datos'
      }
    ]
  },
  {
    id: 'ar-fintech-recover-05',
    category: 'RC.CO',
    subcategory: 'RC.CO-03',
    title: '🤝 ¿Cómo coordinamos comunicaciones de recuperación en Fintech?',
    scenario: 'Fintech en Argentina recuperándose. Múltiples stakeholders piden actualizaciones.',
    options: [
      {
        id: 'A',
        text: 'Cada área comunica por su cuenta',
        impact: -20,
        explanation: 'Mensajes inconsistentes'
      },
      {
        id: 'B',
        text: 'War room con comunicaciones centralizadas + updates regulares',
        impact: 15,
        explanation: '✅ NIST RC.CO-03: Comunicaciones coordinadas'
      },
      {
        id: 'C',
        text: 'Solo comunicar cuando todo esté resuelto',
        impact: -25,
        explanation: 'Stakeholders ansiosos y especulación'
      },
      {
        id: 'D',
        text: 'Delegar a PR externo sin contexto técnico',
        impact: -15,
        explanation: 'Información imprecisa'
      }
    ]
  }
];
