/**
 * IDENTIFY Dilemmas for ar-fintech-idor
 * Generated for NIST CSF 2.0 - IDENTIFY Function
 * Country: Argentina | Industry: Fintech
 */

import { IdentifyDilemma } from '../../../types/IdentifyTypes';

export const ar_fintech_idorIdentifyDilemmas: IdentifyDilemma[] = [
  {
    id: 'ar-fintech-identify-01',
    category: 'ID.AM',
    subcategory: 'ID.AM-01',
    title: '📋 ¿Cómo inventariamos los activos de Fintech?',
    scenario: 'En Argentina, necesitamos un inventario completo de activos IT. No sabemos qué sistemas existen en producción.',
    options: [
      {
        id: 'A',
        text: 'Inventario manual en Excel',
        impact: -20,
        explanation: 'No escalable ni mantenible'
      },
      {
        id: 'B',
        text: 'Herramienta CMDB automatizada (ServiceNow/Jira)',
        impact: 15,
        explanation: '✅ NIST ID.AM-01: Inventario automatizado y actualizado'
      },
      {
        id: 'C',
        text: 'Solo inventariar sistemas críticos',
        impact: -15,
        explanation: 'Deja gaps de seguridad'
      },
      {
        id: 'D',
        text: 'No hacer inventario (confiar en memoria institucional)',
        impact: -25,
        explanation: 'Riesgo crítico'
      }
    ]
  },
  {
    id: 'ar-fintech-identify-02',
    category: 'ID.RA',
    subcategory: 'ID.RA-01',
    title: '🔍 ¿Cómo identificamos vulnerabilidades en Fintech?',
    scenario: 'Sistema de Fintech en Argentina nunca tuvo escaneo de vulnerabilidades. ¿Cómo empezamos?',
    options: [
      {
        id: 'A',
        text: 'Contratar pentesters externos ad-hoc',
        impact: -10,
        explanation: 'Solo puntual, no continuo'
      },
      {
        id: 'B',
        text: 'Implementar Nessus/Qualys + escaneo mensual',
        impact: 15,
        explanation: '✅ NIST ID.RA-01: Vulnerability management continuo'
      },
      {
        id: 'C',
        text: 'Solo buscar CVEs en Google',
        impact: -25,
        explanation: 'Manual e incompleto'
      },
      {
        id: 'D',
        text: 'Esperar a que haya un incidente',
        impact: -30,
        explanation: 'Reactivo y riesgoso'
      }
    ]
  },
  {
    id: 'ar-fintech-identify-03',
    category: 'ID.RA',
    subcategory: 'ID.RA-06',
    title: '📊 ¿Qué metodología de riesgo usamos en Fintech?',
    scenario: 'Empresa de Fintech en Argentina necesita calcular riesgo ciber. No tienen framework definido.',
    options: [
      {
        id: 'A',
        text: 'Scoring ad-hoc por área (subjetivo)',
        impact: -20,
        explanation: 'Inconsistente'
      },
      {
        id: 'B',
        text: 'NIST RMF + ISO 27005',
        impact: 15,
        explanation: '✅ NIST ID.RA: Metodología estándar reconocida'
      },
      {
        id: 'C',
        text: 'Solo considerar impacto financiero',
        impact: -15,
        explanation: 'Ignora riesgos no monetarios'
      },
      {
        id: 'D',
        text: 'Copiar matriz de riesgo de otra empresa',
        impact: -10,
        explanation: 'No considera contexto propio'
      }
    ]
  },
  {
    id: 'ar-fintech-identify-04',
    category: 'ID.SC',
    subcategory: 'ID.SC-02',
    title: '🔗 ¿Cómo gestionamos proveedores en Fintech?',
    scenario: 'Fintech en Argentina tiene 50+ proveedores cloud. No hay inventario de proveedores críticos.',
    options: [
      {
        id: 'A',
        text: 'Lista en Excel sin clasificar',
        impact: -20,
        explanation: 'No identifica criticidad'
      },
      {
        id: 'B',
        text: 'Vendor Risk Management con scoring (critical/high/low)',
        impact: 15,
        explanation: '✅ NIST ID.SC-02: Proveedores identificados y categorizados'
      },
      {
        id: 'C',
        text: 'Solo trackear proveedores >100K USD/año',
        impact: -10,
        explanation: 'Ignora proveedores críticos pequeños'
      },
      {
        id: 'D',
        text: 'Confiar en que todos los proveedores son seguros',
        impact: -25,
        explanation: 'Asunción peligrosa'
      }
    ]
  },
  {
    id: 'ar-fintech-identify-05',
    category: 'ID.BE',
    subcategory: 'ID.BE-04',
    title: '⚙️ ¿Qué funciones son críticas en Fintech?',
    scenario: 'Empresa de Fintech en Argentina debe identificar procesos críticos para BCP/DR. No hay documentación.',
    options: [
      {
        id: 'A',
        text: 'Preguntar a cada área qué es crítico',
        impact: -15,
        explanation: 'Todos dirán que su área es crítica'
      },
      {
        id: 'B',
        text: 'Business Impact Analysis (BIA) formal',
        impact: 15,
        explanation: '✅ NIST ID.BE-04: Identificar dependencias críticas'
      },
      {
        id: 'C',
        text: 'Asumir que todo es crítico',
        impact: -20,
        explanation: 'No prioriza recursos'
      },
      {
        id: 'D',
        text: 'Solo considerar funciones de revenue',
        impact: -10,
        explanation: 'Ignora compliance y soporte'
      }
    ]
  }
];
