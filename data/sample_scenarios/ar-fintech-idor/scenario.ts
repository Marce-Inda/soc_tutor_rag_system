import { ScenarioV2I18n } from '../../../types/ScenarioV2';
import translations from './translations/scenario_es.json';

export const arFintechIDOR: ScenarioV2I18n = {
    id: 'ar-fintech-idor',
    version: '1.5.0',
    titleKey: 'scenarios.ar-fintech-idor.title',
    subtitleKey: 'scenarios.ar-fintech-idor.subtitle',
    descriptionKey: 'scenarios.ar-fintech-idor.description',
    difficulty: 'intermediate',
    estimatedTimeMinutes: 40,
    targetLevel: 3,
    supportedRoles: ['Analista de Seguridad', 'CISO'],
    briefing: {
        condicionesIniciales: {
            tipoCEO: {
                perfil: 'Impaciente',
                descripcion: 'CEO presionado por inversores y el BCRA para mantener estándares de seguridad, exigiendo arreglos definitivos antes del próximo reporte.',
                impactoInicial: { confianzaCEO: -5, presionTemporal: 'Alta' }
            },
            madurezCiberseguridad: {
                nivel: 'Gestionado',
                descripcion: 'FinTech con procesos de desarrollo modernos pero con vulnerabilidades remanentes en endpoints legados (IDOR).',
                impactoInicial: { gobernanza: 5, herramientasDisponibles: ['API Gateway Logs', 'Burp Suite Report'] }
            },
            recursosHumanos: {
                equipoDisponible: { analistas: 1, ingenieros: 2, consultoresExternos: false },
                descripcion: 'Un analista de seguridad y dos desarrolladores enfocados en cerrar la brecha de autorización.',
                impactoInicial: { velocidadRespuesta: 'Rápida', capacidadInvestigacion: 'Media' }
            },
            scoreInicial: {
                gobernanza: 105,
                metodologia: 100,
                confianzaCEO: 95,
                justificacion: 'Tecnología robusta pero con deudas técnicas que exponen datos personales.'
            }
        },
        condicionesEscenario: {
            tiempoDisponible: '40 min',
            hintsDisponibles: 3,
            dificultadTecnica: 'Media',
            complejidadLegal: 'Compleja'
        }
    },

    threatProfile: {
        attackType: 'API Vulnerability (IDOR)',
        attackVector: 'Insecure Direct Object Reference',
        threatActorProfileKey: 'scenarios.ar-fintech-idor.threat_profile.actor',
        realWorldReferenceKey: 'scenarios.ar-fintech-idor.threat_profile.reference',
        mitreAttackTechniques: ['T1552', 'T1213']
    },

    primaryNISTFunction: 'RESPOND',
    secondaryNISTFunctions: ['PROTECT', 'GOVERN'],

    complianceFrameworks: [
        {
            id: 'ley-25326',
            nameKey: 'scenarios.ar-fintech-idor.compliance.pd.name',
            descriptionKey: 'scenarios.ar-fintech-idor.compliance.pd.description',
            type: 'legal_obligatorio',
            jurisdiction: 'Argentina'
        },
        {
            id: 'bcra-a7724',
            nameKey: 'scenarios.ar-fintech-idor.compliance.bcra.name',
            descriptionKey: 'scenarios.ar-fintech-idor.compliance.bcra.description',
            type: 'legal_obligatorio',
            jurisdiction: 'Argentina',
            notificationDeadlineHours: 24
        }
    ],

    phases: [
        {
            id: 'phase_discovery',
            nameKey: 'scenarios.ar-fintech-idor.phases.discovery.name',
            descriptionKey: 'scenarios.ar-fintech-idor.phases.discovery.description',
            nistFunction: 'DETECT',
            timeLimitMinutes: 10,
            evidence: [
                {
                    id: 'burp-api-traversal-log',
                    type: 'system-log',
                    contentKey: 'scenarios.ar-fintech-idor.evidence.logs.desc',
                    rawContent: `[2026-03-20T11:45:01Z] HTTP/1.1 200 OK\nGET /api/v1/accounts/10045/profile\nX-User-ID: 99999 (Attacker)\nResponse: { "name": "Juan Perez", "secret_question": "...", "id": 10045 }`,
                    discoveredBy: 'api-gateway-anomalies',
                    isKeyEvidence: true,
                    recommendedTool: 'LOG_ANALYZER'
                }
            ],
            availableTools: [],
            objectivesKeys: [],
            hintsKeys: [],
            dilemmas: [
                {
                    id: 'd1_containment',
                    titleKey: 'scenarios.ar-fintech-idor.dilemmas.d1.title',
                    contextKey: 'scenarios.ar-fintech-idor.dilemmas.d1.context',
                    questionKey: 'scenarios.ar-fintech-idor.dilemmas.d1.question',
                    category: 'RS.MI-01',
                    timeLimitMinutes: 10,
                    hints: {
                        strategicKey: 'scenarios.ar-fintech-idor.dilemmas.d1.hints.strategic',
                        tacticalKey: 'scenarios.ar-fintech-idor.dilemmas.d1.hints.tactical'
                    },
                    options: [
                        {
                            id: 'op1',
                            textKey: 'scenarios.ar-fintech-idor.dilemmas.d1.options.op1.text',
                            rationaleKey: 'scenarios.ar-fintech-idor.dilemmas.d1.options.op1.rationale',
                            technicalImpact: 50,
                            reputationImpact: -10,
                            budgetImpact: -5000,
                            complianceScore: 30,
                            isOptimal: true
                        },
                        {
                            id: 'op2',
                            textKey: 'scenarios.ar-fintech-idor.dilemmas.d1.options.op2.text',
                            rationaleKey: 'scenarios.ar-fintech-idor.dilemmas.d1.options.op2.rationale',
                            technicalImpact: -20,
                            reputationImpact: 10,
                            budgetImpact: 0,
                            complianceScore: -20
                        }
                    ]
                }
            ]
        },
        {
            id: 'phase_remediation',
            nameKey: 'scenarios.ar-fintech-idor.phases.remediation.name',
            descriptionKey: 'scenarios.ar-fintech-idor.phases.remediation.description',
            nistFunction: 'PROTECT',
            timeLimitMinutes: 15,
            evidence: [],
            availableTools: [],
            objectivesKeys: [],
            hintsKeys: [],
            dilemmas: [
                {
                    id: 'd2_remediation_depth',
                    titleKey: 'scenarios.ar-fintech-idor.dilemmas.d2.title',
                    contextKey: 'scenarios.ar-fintech-idor.dilemmas.d2.context',
                    questionKey: 'scenarios.ar-fintech-idor.dilemmas.d2.question',
                    category: 'PR.DS-01', // Data Security / Access Control
                    timeLimitMinutes: 10,
                    hints: {
                        strategicKey: 'scenarios.ar-fintech-idor.dilemmas.d2.hints.strategic',
                        tacticalKey: 'scenarios.ar-fintech-idor.dilemmas.d2.hints.tactical'
                    },
                    options: [
                        {
                            id: 'op1',
                            textKey: 'scenarios.ar-fintech-idor.dilemmas.d2.options.op1.text',
                            rationaleKey: 'scenarios.ar-fintech-idor.dilemmas.d2.options.op1.rationale',
                            technicalImpact: 50,
                            reputationImpact: 0,
                            budgetImpact: -10000,
                            complianceScore: 40,
                            isOptimal: true
                        },
                        {
                            id: 'op2',
                            textKey: 'scenarios.ar-fintech-idor.dilemmas.d2.options.op2.text',
                            rationaleKey: 'scenarios.ar-fintech-idor.dilemmas.d2.options.op2.rationale',
                            technicalImpact: 10,
                            reputationImpact: 0,
                            budgetImpact: -2000,
                            complianceScore: 10
                        }
                    ]
                }
            ]
        },
        {
            id: 'phase_governance',
            nameKey: 'scenarios.ar-fintech-idor.phases.governance.name',
            descriptionKey: 'scenarios.ar-fintech-idor.phases.governance.description',
            nistFunction: 'GOVERN',
            timeLimitMinutes: 15,
            evidence: [],
            availableTools: [],
            objectivesKeys: [],
            hintsKeys: [],
            dilemmas: [
                {
                    id: 'd3_disclosure',
                    titleKey: 'scenarios.ar-fintech-idor.dilemmas.d3.title',
                    contextKey: 'scenarios.ar-fintech-idor.dilemmas.d3.context',
                    questionKey: 'scenarios.ar-fintech-idor.dilemmas.d3.question',
                    category: 'GV.OC-01',
                    timeLimitMinutes: 10,
                    hints: {
                        strategicKey: 'scenarios.ar-fintech-idor.dilemmas.d3.hints.strategic',
                        tacticalKey: 'scenarios.ar-fintech-idor.dilemmas.d3.hints.tactical'
                    },
                    options: [
                        {
                            id: 'op1',
                            textKey: 'scenarios.ar-fintech-idor.dilemmas.d3.options.op1.text',
                            rationaleKey: 'scenarios.ar-fintech-idor.dilemmas.d3.options.op1.rationale',
                            technicalImpact: 0,
                            reputationImpact: 20,
                            budgetImpact: 0,
                            complianceScore: 50,
                            isOptimal: true
                        },
                        {
                            id: 'op2',
                            textKey: 'scenarios.ar-fintech-idor.dilemmas.d3.options.op2.text',
                            rationaleKey: 'scenarios.ar-fintech-idor.dilemmas.d3.options.op2.rationale',
                            technicalImpact: 0,
                            reputationImpact: -60,
                            budgetImpact: 0,
                            complianceScore: -80
                        }
                    ]
                }
            ]
        }
    ],

    scoringCriteria: {
        technical: 0.4,
        governance: 0.2,
        communication: 0.2,
        compliance: 0.2
    },

    learningOutcomesKeys: [
        'scenarios.ar-fintech-idor.learning.outcome1',
        'scenarios.ar-fintech-idor.learning.outcome2',
        'scenarios.ar-fintech-idor.learning.outcome3'
    ],

    achievements: [],

    metadata: {
        id: '12-ar-fintech-idor',
        createdDate: '2026-02-11',
        lastUpdated: '2026-03-20',
        tags: ['fintech', 'api', 'idor', 'argentina', 'bcra', 'privacy', 'practitioner'],
        author: 'GoPyme Security Team',
        status: 'Production-Ready',
        disclaimer: '🚨 AVISO LEGAL Y DE SIMULACIÓN 🚨: Ficción y Propósito Educativo. Este escenario es una simulación didáctica. Todos los personajes, empresas y ataques descritos son ficticios; cualquier semejanza con la realidad es coincidencia. Menciones a marcos de trabajo, leyes o agencias reguladoras buscan preparar para el mundo real. Las acciones e hilos no constituyen asesoramiento técnico ni legal vinculante.'
    }
,

    translations: {
        es: translations
    }
};

export default arFintechIDOR;
