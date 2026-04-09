/**
 * PROTECT Dilemmas for ar-fintech-idor
 * Generated for NIST CSF 2.0 - PROTECT Function
 * Country: Argentina | Industry: Fintech
 */

import { ProtectDilemma } from '../../../types/ProtectTypes';

export const ar_fintech_idorProtectDilemmas: ProtectDilemma[] = [
  {
    id: 'ar-fintech-protect-01',
    category: 'PR.AA',
    subcategory: 'PR.AA-01',
    title: '🔐 ¿Cómo gestionamos identidades en Fintech?',
    scenario: 'Fintech en Argentina tiene usuarios con passwords compartidas y sin MFA.',
    options: [
      {
        id: 'A',
        text: 'Mantener passwords compartidas (más fácil)',
        impact: -25,
        explanation: 'Riesgo crítico'
      },
      {
        id: 'B',
        text: 'Implementar SSO + MFA + gestión de identidades (Okta/Azure AD)',
        impact: 15,
        explanation: '✅ NIST PR.AA-01: Identidades gestionadas centralmente'
      },
      {
        id: 'C',
        text: 'Solo MFA para administradores',
        impact: -10,
        explanation: 'Usuarios normales siguen en riesgo'
      },
      {
        id: 'D',
        text: 'Cambiar passwords cada 90 días (sin MFA)',
        impact: -15,
        explanation: 'Insuficiente según estándares modernos'
      }
    ]
  },
  {
    id: 'ar-fintech-protect-02',
    category: 'PR.DS',
    subcategory: 'PR.DS-01',
    title: '💾 ¿Cómo protegemos datos en reposo en Fintech?',
    scenario: 'Base de datos de Fintech en Argentina almacena datos sensibles sin cifrado.',
    options: [
      {
        id: 'A',
        text: 'No cifrar (mejor performance)',
        impact: -25,
        explanation: 'Viola compliance y NIST'
      },
      {
        id: 'B',
        text: 'Cifrado AES-256 at rest + key management (AWS KMS/Vault)',
        impact: 15,
        explanation: '✅ NIST PR.DS-01: Datos en reposo protegidos'
      },
      {
        id: 'C',
        text: 'Cifrar solo datos de tarjetas de crédito',
        impact: -10,
        explanation: 'Otros datos sensibles quedan expuestos'
      },
      {
        id: 'D',
        text: 'Ofuscación en vez de cifrado',
        impact: -20,
        explanation: 'No es cifrado real'
      }
    ]
  },
  {
    id: 'ar-fintech-protect-03',
    category: 'PR.AT',
    subcategory: 'PR.AT-01',
    title: '🎓 ¿Cómo capacitamos al personal de Fintech?',
    scenario: 'Empleados de Fintech en Argentina nunca recibieron training de ciberseguridad.',
    options: [
      {
        id: 'A',
        text: 'Video de 10 min anual (checkbox compliance)',
        impact: -15,
        explanation: 'Insuficiente'
      },
      {
        id: 'B',
        text: 'Programa continuo: phishing simulations + workshops trimestrales',
        impact: 15,
        explanation: '✅ NIST PR.AT-01: Personal capacitado continuamente'
      },
      {
        id: 'C',
        text: 'Solo capacitar a IT, no al resto',
        impact: -20,
        explanation: 'Todos son targets de phishing'
      },
      {
        id: 'D',
        text: 'No capacitar (confiar en sentido común)',
        impact: -25,
        explanation: 'Factor humano es el más débil'
      }
    ]
  },
  {
    id: 'ar-fintech-protect-04',
    category: 'PR.PS',
    subcategory: 'PR.PS-01',
    title: '⚙️ ¿Cómo gestionamos configuraciones en Fintech?',
    scenario: 'Servidores de Fintech en Argentina tienen configuraciones inconsistentes y no documentadas.',
    options: [
      {
        id: 'A',
        text: 'Cada admin configura a su criterio',
        impact: -25,
        explanation: 'Configuration drift y riesgo'
      },
      {
        id: 'B',
        text: 'Infrastructure as Code (Terraform/Ansible) + CIS Benchmarks',
        impact: 15,
        explanation: '✅ NIST PR.PS-01: Configuraciones gestionadas y seguras'
      },
      {
        id: 'C',
        text: 'Documentar configuraciones en wiki',
        impact: -10,
        explanation: 'Manual, no enforced'
      },
      {
        id: 'D',
        text: 'Usar configuraciones default del vendor',
        impact: -20,
        explanation: 'Defaults suelen ser inseguros'
      }
    ]
  },
  {
    id: 'ar-fintech-protect-05',
    category: 'PR.IR',
    subcategory: 'PR.IR-04',
    title: '🔒 ¿Implementamos least privilege en Fintech?',
    scenario: 'Todos los empleados de Fintech en Argentina tienen permisos de admin "por si acaso".',
    options: [
      {
        id: 'A',
        text: 'Mantener todos admin (más fácil)',
        impact: -25,
        explanation: 'Viola principio de least privilege'
      },
      {
        id: 'B',
        text: 'RBAC + JIT (Just-In-Time) access + logging',
        impact: 15,
        explanation: '✅ NIST PR.IR-04: Acceso basado en roles mínimos'
      },
      {
        id: 'C',
        text: 'Solo quitar admin a nuevos empleados',
        impact: -15,
        explanation: 'Los antiguos siguen con riesgo'
      },
      {
        id: 'D',
        text: 'Permisos admin solo durante horario laboral',
        impact: -10,
        explanation: 'Insuficiente, ventana de 8h de riesgo'
      }
    ]
  }
];
