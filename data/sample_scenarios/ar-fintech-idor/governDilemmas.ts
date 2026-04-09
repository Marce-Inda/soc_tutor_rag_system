/**
 * GOVERN Dilemmas for ar-fintech-idor scenario
 * 
 * Escenario: Fintech Argentina (Buenos Aires)
 * Incidente: IDOR (Insecure Direct Object Reference) expone datos bancarios
 * Regulación: BCRA (Banco Central), Ley 25.326 (Protección de Datos), AFIP
 * 
 * Contexto: Una fintech argentina descubre que atacantes explotaron una 
 * vulnerabilidad IDOR para acceder a datos de cuentas de otros clientes.
 */

import { GovernDilemma } from '../../../types/GovernTypes';

export const AR_FINTECH_IDOR_GOVERN_DILEMMAS: GovernDilemma[] = [
    // ═══════════════════════════════════════════════════════════════
    // GV.RM-02: Risk Tolerance - Scope of Disclosure
    // ═══════════════════════════════════════════════════════════════
    {
        id: 'ar-fintech-govern-01',
        category: 'GV.RM',
        subcategoryId: 'GV.RM-02',
        title: '💳 ¿Cuántos clientes fueron realmente afectados?',
        description: `El equipo de seguridad detectó que la vulnerabilidad IDOR estuvo activa por 45 días.
Los logs muestran accesos sospechosos a 3,200 cuentas de clientes.

El CTO dice: "Solo 150 cuentas tuvieron transacciones no autorizadas, reportemos esas".
El CFO advierte: "Si reportamos 3,200, el BCRA nos va a auditar completos".
El CISO (tú) sabe: "Los 3,200 fueron potencialmente expuestos aunque solo 150 tuvieron fraude".

El BCRA (Comunicación A 6017) exige notificación de incidentes significativos.
¿Cuántos clientes reportás como afectados?`,
        options: [
            {
                id: 'A',
                text: 'Reportar solo los 150 con transacciones fraudulentas',
                impact: {
                    compliance: {
                        'GV.RM-02': -20,  // Subestima riesgo real
                        'GV.RR-01': -15,  // Liderazgo cuestionable
                        'GV.OC-03': -20   // Potencial violación regulatoria
                    },
                    operations: 5,
                    reputation: -30,       // Si se descubre, daño severo
                    financial: 0
                }
            },
            {
                id: 'B',
                text: 'Reportar los 3,200 con datos potencialmente expuestos',
                impact: {
                    compliance: {
                        'GV.RM-02': 15,   // Evalúa riesgo completo
                        'GV.RR-01': 10,   // Liderazgo responsable
                        'GV.OC-03': 15    // Cumple con transparencia
                    },
                    operations: -10,
                    reputation: -5,        // Impacto inicial pero honesto
                    financial: -5000000    // Costos de notificación en ARS
                }
            },
            {
                id: 'C',
                text: 'Reportar 500 (un número intermedio "razonable")',
                impact: {
                    compliance: {
                        'GV.RM-02': -15,
                        'GV.RR-01': -10,
                        'GV.PO-01': -10   // Viola principio de transparencia
                    },
                    operations: 0,
                    reputation: -20,
                    financial: -2000000
                }
            },
            {
                id: 'D',
                text: 'No reportar al BCRA (no hubo pérdida de fondos significativa)',
                impact: {
                    compliance: {
                        'GV.RM-02': -25,
                        'GV.OC-03': -25,  // Violación regulatoria clara
                        'GV.RR-01': -20
                    },
                    operations: 10,
                    reputation: -40,
                    financial: -50000000   // Multa potencial BCRA
                }
            }
        ],
        correctAnswer: 'B',
        explanation: `GV.RM-02 requiere evaluar y comunicar el riesgo de forma completa y honesta.
En Argentina, el BCRA (Comunicación A 6017) exige reportar "incidentes operacionales significativos" 
que afecten la seguridad de la información de clientes.

La opción B es correcta: los 3,200 clientes tuvieron sus datos potencialmente expuestos, 
independientemente de si hubo fraude. Ocultar el alcance real expone a la fintech a 
sanciones mayores si el BCRA descubre la discrepancia durante una auditoría.`,
        learningObjective: 'Reportar el alcance completo de un incidente, no minimizarlo para evitar escrutinio regulatorio.'
    },

    // ═══════════════════════════════════════════════════════════════
    // GV.RR-01: Leadership - Vulnerability Disclosure
    // ═══════════════════════════════════════════════════════════════
    {
        id: 'ar-fintech-govern-02',
        category: 'GV.RR',
        subcategoryId: 'GV.RR-01',
        title: '📢 ¿Comunicamos la vulnerabilidad a los clientes?',
        description: `La vulnerabilidad IDOR fue parcheada hace 6 horas. El equipo legal debate 
sobre cómo comunicar a los 3,200 clientes afectados.

La Ley 25.326 de Protección de Datos Personales exige notificar a titulares cuando 
sus datos fueron accedidos sin autorización.

El CEO quiere: "Email genérico de 'actualización de seguridad', sin detalles técnicos".
Legal recomienda: "Decir 'posible acceso no autorizado' pero no admitir la vulnerabilidad".
El CISO (tú) sugiere: "Transparencia completa con recomendaciones de acción para clientes".

Un periodista de Infobae ya contactó preguntando sobre "rumores de hackeo".`,
        options: [
            {
                id: 'A',
                text: 'Email genérico: "Mejoramos nuestra seguridad" (sin mencionar incidente)',
                impact: {
                    compliance: {
                        'GV.RR-01': -25,
                        'GV.OC-03': -20,
                        'GV.RM-05': -15
                    },
                    operations: 5,
                    reputation: -30,
                    financial: -10000000   // Multa Agencia de Acceso
                }
            },
            {
                id: 'B',
                text: 'Comunicado transparente: explicar qué pasó + qué datos + recomendaciones',
                impact: {
                    compliance: {
                        'GV.RR-01': 15,
                        'GV.OC-03': 15,
                        'GV.RM-05': 10
                    },
                    operations: -5,
                    reputation: 5,
                    financial: -3000000
                }
            },
            {
                id: 'C',
                text: 'Llamar individualmente a los 150 con fraude, ignorar a los otros 3,050',
                impact: {
                    compliance: {
                        'GV.RR-01': -10,
                        'GV.OC-03': -15,
                        'GV.RM-05': -5
                    },
                    operations: -15,
                    reputation: -15,
                    financial: -5000000
                }
            },
            {
                id: 'D',
                text: 'Esperar a que Infobae publique algo y luego responder',
                impact: {
                    compliance: {
                        'GV.RR-01': -20,
                        'GV.OC-03': -10,
                        'GV.RM-05': -20
                    },
                    operations: 0,
                    reputation: -25,
                    financial: -8000000
                }
            }
        ],
        correctAnswer: 'B',
        explanation: `GV.RR-01 exige que el liderazgo sea transparente y tome responsabilidad.
La Ley 25.326 y la Agencia de Acceso a la Información Pública requieren notificar a 
los titulares de datos cuando hay acceso no autorizado.

La opción B es correcta: comunicación proactiva, transparente y con acciones concretas. 
Esto mantiene la confianza de los clientes y cumple con obligaciones legales. Esperar 
a que la prensa publique rumores (D) siempre empeora la situación.`,
        learningObjective: 'Ejercer liderazgo proactivo en comunicación de incidentes, no reactivo ante presión mediática.'
    },

    // ═══════════════════════════════════════════════════════════════
    // GV.SC-07: Supply Chain - Third-party API Security
    // ═══════════════════════════════════════════════════════════════
    {
        id: 'ar-fintech-govern-03',
        category: 'GV.SC',
        subcategoryId: 'GV.SC-07',
        title: '🔗 ¿El proveedor de API de pagos tuvo la culpa?',
        description: `El análisis forense revela que la vulnerabilidad IDOR estaba en código 
desarrollado internamente, NO en el proveedor de API de pagos (MercadoPago Connect).

Sin embargo, el CTO descubre que MercadoPago no alertó sobre patrones de acceso 
anómalos que sus sistemas de monitoreo deberían haber detectado.

El contrato con MercadoPago incluye:
- "Monitoreo de patrones anómalos en endpoints de cliente"
- "Alertas por actividad sospechosa dentro de 4 horas"

MercadoPago dice: "La vulnerabilidad era de ustedes, nosotros no somos responsables".`,
        options: [
            {
                id: 'A',
                text: 'Culpar públicamente a MercadoPago para desviar atención',
                impact: {
                    compliance: {
                        'GV.SC-07': -25,
                        'GV.RR-01': -20,
                        'GV.SC-05': -15
                    },
                    operations: 0,
                    reputation: -20,
                    financial: -15000000   // Posible demanda de MP
                }
            },
            {
                id: 'B',
                text: 'Revisar contrato + solicitar logs de monitoreo de MP + evaluar incumplimiento',
                impact: {
                    compliance: {
                        'GV.SC-07': 15,
                        'GV.SC-05': 10,
                        'GV.OV-01': 10
                    },
                    operations: -5,
                    reputation: 0,
                    financial: -2000000    // Legal review
                }
            },
            {
                id: 'C',
                text: 'Asumir 100% responsabilidad interna sin revisar rol de proveedores',
                impact: {
                    compliance: {
                        'GV.SC-07': -10,
                        'GV.OV-01': -15,
                        'GV.RM-02': -5
                    },
                    operations: 5,
                    reputation: -5,
                    financial: 0
                }
            },
            {
                id: 'D',
                text: 'Terminar contrato con MercadoPago inmediatamente',
                impact: {
                    compliance: {
                        'GV.SC-07': -15,
                        'GV.SC-10': 5,
                        'GV.OC-05': -20
                    },
                    operations: -25,
                    reputation: -10,
                    financial: -30000000   // Migración
                }
            }
        ],
        correctAnswer: 'B',
        explanation: `GV.SC-07 requiere monitorear continuamente a proveedores y evaluar su 
cumplimiento de obligaciones contractuales.

La opción B es correcta: revisa el contrato para determinar si MercadoPago incumplió 
su obligación de alertar sobre patrones anómalos. Si el contrato especifica monitoreo 
y alertas, y no las proporcionaron, hay una discusión legítima de responsabilidad compartida.

Culpar sin evidencia (A) o asumir 100% responsabilidad sin investigar (C) son extremos 
que no siguen un proceso de gestión de proveedores maduro.`,
        learningObjective: 'Evaluar objetivamente el rol de todos los actores en un incidente, incluyendo obligaciones contractuales de proveedores.'
    },

    // ═══════════════════════════════════════════════════════════════
    // GV.RR-04: HR Practices - Developer Who Introduced Vulnerability
    // ═══════════════════════════════════════════════════════════════
    {
        id: 'ar-fintech-govern-04',
        category: 'GV.RR',
        subcategoryId: 'GV.RR-04',
        title: '👨‍💻 ¿Qué hacemos con el desarrollador que escribió el código vulnerable?',
        description: `El análisis de root cause identifica que la vulnerabilidad IDOR fue 
introducida por Martín, desarrollador senior con 3 años en la empresa, durante un 
sprint de alta presión hace 2 meses.

Hallazgos:
- El código no pasó por peer review (la empresa no tiene proceso obligatorio)
- No hay herramienta de SAST/DAST en el pipeline de CI/CD
- Martín nunca recibió capacitación en OWASP Top 10
- El gerente de Martín presionó: "Deploy antes del viernes o perdemos al cliente"

El CEO quiere despedir a Martín "para mostrar que tomamos esto en serio".`,
        options: [
            {
                id: 'A',
                text: 'Despedir a Martín para enviar mensaje claro',
                impact: {
                    compliance: {
                        'GV.RR-04': -25,
                        'GV.RR-01': -15,
                        'GV.OV-03': -10
                    },
                    operations: -10,
                    reputation: -15,
                    financial: -5000000    // Indemnización
                }
            },
            {
                id: 'B',
                text: 'Mantener a Martín + implementar code review + SAST + capacitación OWASP',
                impact: {
                    compliance: {
                        'GV.RR-04': 15,
                        'GV.PO-02': 15,
                        'GV.RR-01': 10
                    },
                    operations: 0,
                    reputation: 5,
                    financial: -8000000    // Herramientas + capacitación
                }
            },
            {
                id: 'C',
                text: 'Suspender a Martín 30 días mientras se investiga',
                impact: {
                    compliance: {
                        'GV.RR-04': -10,
                        'GV.RR-01': -5,
                        'GV.OV-01': 0
                    },
                    operations: -5,
                    reputation: -5,
                    financial: -1000000
                }
            },
            {
                id: 'D',
                text: 'Despedir al gerente que presionó por el deploy rápido',
                impact: {
                    compliance: {
                        'GV.RR-04': -5,
                        'GV.RR-01': 0,
                        'GV.OV-03': -5
                    },
                    operations: -10,
                    reputation: -10,
                    financial: -8000000
                }
            }
        ],
        correctAnswer: 'B',
        explanation: `GV.RR-04 integra ciberseguridad en prácticas de recursos humanos de forma constructiva.

El análisis muestra que la vulnerabilidad es un fallo SISTÉMICO, no individual:
- No hay peer review obligatorio
- No hay herramientas de análisis de código
- No hay capacitación en seguridad
- La cultura premia delivery rápido sobre calidad

Despedir a Martín (A) no soluciona ninguno de estos problemas. La opción B es correcta: 
usar el incidente para implementar controles que deberían existir: code review, SAST/DAST, 
y capacitación en seguridad para todo el equipo de desarrollo.`,
        learningObjective: 'Identificar fallos sistémicos en lugar de buscar culpables individuales cuando los controles básicos no existen.'
    },

    // ═══════════════════════════════════════════════════════════════
    // GV.OC-03: Legal/Regulatory - Multi-Regulator Notification
    // ═══════════════════════════════════════════════════════════════
    {
        id: 'ar-fintech-govern-05',
        category: 'GV.OC',
        subcategoryId: 'GV.OC-03',
        title: '🏛️ ¿A qué reguladores notificamos en Argentina?',
        description: `Como fintech regulada, la empresa tiene obligaciones con múltiples entidades:

- BCRA (Banco Central): Comunicación A 6017 - incidentes operacionales
- Agencia de Acceso a la Información Pública: Ley 25.326 - breaches de datos
- AFIP: Posible exposición de datos fiscales de clientes
- CNV (si hay inversores): Hechos relevantes para el mercado

El equipo legal no tiene experiencia en notificaciones multi-regulador.
El plazo del BCRA es 24 horas. La Agencia de Acceso no tiene plazo explícito.
Los costos de asesoría legal especializada pueden llegar a 5 millones ARS.

El CFO pregunta: "¿Podemos notificar solo al BCRA y ver si los otros se enteran?"`,
        options: [
            {
                id: 'A',
                text: 'Notificar solo al BCRA (es el regulador principal)',
                impact: {
                    compliance: {
                        'GV.OC-03': -15,
                        'GV.RM-02': -10,
                        'GV.RR-01': -10
                    },
                    operations: 0,
                    reputation: -10,
                    financial: -20000000   // Multas si descubren
                }
            },
            {
                id: 'B',
                text: 'Notificar a BCRA + Agencia de Acceso + evaluar AFIP con asesoría legal',
                impact: {
                    compliance: {
                        'GV.OC-03': 15,
                        'GV.RM-04': 10,
                        'GV.RR-03': 5
                    },
                    operations: -5,
                    reputation: 5,
                    financial: -5000000    // Asesoría legal
                }
            },
            {
                id: 'C',
                text: 'Esperar 72 horas para evaluar si algún regulador contacta',
                impact: {
                    compliance: {
                        'GV.OC-03': -25,
                        'GV.RR-01': -20,
                        'GV.RM-02': -15
                    },
                    operations: 5,
                    reputation: -20,
                    financial: -30000000
                }
            },
            {
                id: 'D',
                text: 'Notificar solo a clientes y no a reguladores',
                impact: {
                    compliance: {
                        'GV.OC-03': -20,
                        'GV.RR-01': -15,
                        'GV.OV-01': -10
                    },
                    operations: 0,
                    reputation: -15,
                    financial: -40000000
                }
            }
        ],
        correctAnswer: 'B',
        explanation: `GV.OC-03 requiere comprender y cumplir con TODOS los requisitos legales 
y regulatorios aplicables.

En Argentina, las fintechs tienen múltiples reguladores:
- BCRA: Obligación clara de notificar incidentes operacionales (24h)
- Agencia de Acceso: Ley 25.326 requiere notificar breaches de datos personales
- AFIP: Depende de si hubo exposición de datos fiscales (evaluar con asesoría)

La opción B es correcta: cumplir con reguladores conocidos (BCRA, Agencia) y 
evaluar con asesoría especializada si AFIP aplica. "Ver si se enteran" (A, C) 
es una estrategia que siempre falla a largo plazo.`,
        learningObjective: 'Mapear todas las obligaciones regulatorias aplicables a una fintech argentina y cumplirlas proactivamente.'
    }
];

/**
 * Get all GOVERN dilemmas for AR Fintech IDOR scenario
 */
export function getArFintechIdorGovernDilemmas(): GovernDilemma[] {
    return AR_FINTECH_IDOR_GOVERN_DILEMMAS;
}

/**
 * Get dilemmas by category
 */
export function getDilemmasByCategory(categoryId: string): GovernDilemma[] {
    return AR_FINTECH_IDOR_GOVERN_DILEMMAS.filter(d => d.category === categoryId);
}

/**
 * Get dilemma by ID
 */
export function getDilemmaById(id: string): GovernDilemma | undefined {
    return AR_FINTECH_IDOR_GOVERN_DILEMMAS.find(d => d.id === id);
}

export const arFintechIdorGovernDilemmas = AR_FINTECH_IDOR_GOVERN_DILEMMAS;
