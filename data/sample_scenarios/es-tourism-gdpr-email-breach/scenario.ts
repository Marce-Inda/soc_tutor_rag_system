import { ScenarioV2I18n } from '../../../types/ScenarioV2';
import translations from './translations/scenario_es.json';

export const esTourismGDPRScenario: ScenarioV2I18n = {
    id: 'es-tourism-gdpr-email-breach',
    version: '3.0.0',
    titleKey: 'scenarios.es-tourism-gdpr-email-breach.title',
    subtitleKey: 'scenarios.es-tourism-gdpr-email-breach.subtitle',
    descriptionKey: 'scenarios.es-tourism-gdpr-email-breach.description',
    difficulty: 'intermediate',
    estimatedTimeMinutes: 40,
    targetLevel: 2,
    supportedRoles: ['Analista de Seguridad', 'CISO'],
    briefing: {
        condicionesIniciales: {
            tipoCEO: {
                perfil: 'Cauteloso',
                descripcion: 'Dirección del ente de turismo preocupada por el impacto reputacional en la marca "España" y las posibles multas de la AEPD.',
                impactoInicial: { confianzaCEO: 0, presionTemporal: 'Media' }
            },
            madurezCiberseguridad: {
                nivel: 'Gestionado',
                descripcion: 'Organismo público con delegados de protección de datos (DPO) y políticas de privacidad establecidas, pero fallos en la ejecución técnica.',
                impactoInicial: { gobernanza: 10, herramientasDisponibles: ['Email Filter Audit', 'DLP Basic Alerts'] }
            },
            recursosHumanos: {
                equipoDisponible: { analistas: 2, ingenieros: 0, consultoresExternos: true },
                descripcion: 'Dos analistas internos y asesoramiento legal externo especializado en GDPR.',
                impactoInicial: { velocidadRespuesta: 'Normal', capacidadInvestigacion: 'Alta' }
            },
            scoreInicial: {
                gobernanza: 110,
                metodologia: 100,
                confianzaCEO: 100,
                justificacion: 'Base sólida de gobernanza pero bajo escrutinio legal inmediato.'
            }
        },
        condicionesEscenario: {
            tiempoDisponible: '40 min',
            hintsDisponibles: 3,
            dificultadTecnica: 'Baja',
            complejidadLegal: 'Compleja'
        }
    },

    threatProfile: {
        attackType: 'Data Breach',
        attackVector: 'Human Error (CC vs BCC misconfiguration)',
        threatActorProfileKey: 'scenarios.es-tourism-gdpr-email-breach.threat_profile.actor',
        realWorldReferenceKey: 'scenarios.es-tourism-gdpr-email-breach.threat_profile.reference',
        mitreAttackTechniques: ['T1566']
    },

    primaryNISTFunction: 'RESPOND',
    secondaryNISTFunctions: ['GOVERN', 'PROTECT'],

    complianceFrameworks: [
        {
            id: 'gdpr',
            nameKey: 'scenarios.es-tourism-gdpr-email-breach.compliance.gdpr.name',
            descriptionKey: 'scenarios.es-tourism-gdpr-email-breach.compliance.gdpr.description',
            type: 'legal_obligatorio',
            jurisdiction: 'Europa',
            notificationDeadlineHours: 72
        },
        {
            id: 'lopdgdd',
            nameKey: 'scenarios.es-tourism-gdpr-email-breach.compliance.lopsdgdd.name',
            descriptionKey: 'scenarios.es-tourism-gdpr-email-breach.compliance.lopsdgdd.description',
            type: 'legal_obligatorio',
            jurisdiction: 'España'
        }
    ],

    phases: [
        {
            id: 'containment',
            nameKey: 'scenarios.es-tourism-gdpr-email-breach.phases.containment.name',
            descriptionKey: 'scenarios.es-tourism-gdpr-email-breach.phases.containment.description',
            nistFunction: 'RESPOND',
            timeLimitMinutes: 10,
            evidence: [
                {
                    id: 'smtp-bulk-log',
                    type: 'file',
                    contentKey: 'scenarios.es-tourism-gdpr-email-breach.evidence.header.desc',
                    rawContent: `[2026-03-20T10:00:05Z] SMTP_RELAY: SUCCESS: Message sent to 2,500 recipients.\n[Header Analysis]\nCC: "customer-list@tourism-spain.fake" <2,500 addresses exposed in CC field>\nSubject: EXCLUSIVO: Promo Semana Santa 2026`,
                    discoveredBy: 'Customer Complaint',
                    isKeyEvidence: true,
                    recommendedTool: 'LOG_ANALYZER'
                }
            ],
            availableTools: [],
            objectivesKeys: [],
            hintsKeys: [],
            dilemmas: [
                {
                    id: 'decision_001_containment',
                    titleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.title',
                    contextKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.context',
                    questionKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.question',
                    category: 'RS.MI-01',
                    timeLimitMinutes: 5,
                    hints: {
                        strategicKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.hints.strategic',
                        tacticalKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.hints.tactical'
                    },
                    options: [
                        {
                            id: 'op1',
                            textKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.options.op1.text',
                            rationaleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.options.op1.rationale',
                            technicalImpact: 40,
                            reputationImpact: 10,
                            budgetImpact: 0,
                            complianceScore: 20,
                            isOptimal: true
                        },
                        {
                            id: 'op2',
                            textKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.options.op2.text',
                            rationaleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d1.options.op2.rationale',
                            technicalImpact: -50,
                            reputationImpact: -20,
                            budgetImpact: 0,
                            complianceScore: -30
                        }
                    ]
                }
            ]
        },
        {
            id: 'response',
            nameKey: 'scenarios.es-tourism-gdpr-email-breach.phases.response.name',
            descriptionKey: 'scenarios.es-tourism-gdpr-email-breach.phases.response.description',
            nistFunction: 'GOVERN',
            timeLimitMinutes: 15,
            evidence: [],
            availableTools: [],
            objectivesKeys: [],
            hintsKeys: [],
            dilemmas: [
                {
                    id: 'decision_002_notification',
                    titleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.title',
                    contextKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.context',
                    questionKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.question',
                    category: 'GV.OC-01',
                    timeLimitMinutes: 10,
                    hints: {
                        strategicKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.hints.strategic',
                        tacticalKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.hints.tactical'
                    },
                    options: [
                        {
                            id: 'op1',
                            textKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.options.op1.text',
                            rationaleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.options.op1.rationale',
                            technicalImpact: 0,
                            reputationImpact: 20,
                            budgetImpact: -5000,
                            complianceScore: 50,
                            isOptimal: true
                        },
                        {
                            id: 'op2',
                            textKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.options.op2.text',
                            rationaleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d2.options.op2.rationale',
                            technicalImpact: 0,
                            reputationImpact: -80,
                            budgetImpact: -500000,
                            complianceScore: -100
                        }
                    ]
                }
            ]
        },
        {
            id: 'recovery',
            nameKey: 'scenarios.es-tourism-gdpr-email-breach.phases.recovery.name',
            descriptionKey: 'scenarios.es-tourism-gdpr-email-breach.phases.recovery.description',
            nistFunction: 'RECOVER',
            timeLimitMinutes: 15,
            evidence: [],
            availableTools: [],
            objectivesKeys: [],
            hintsKeys: [],
            dilemmas: [
                {
                    id: 'decision_003_disclosure',
                    titleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.title',
                    contextKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.context',
                    questionKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.question',
                    category: 'RC.RP-01',
                    timeLimitMinutes: 10,
                    hints: {
                        strategicKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.hints.strategic',
                        tacticalKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.hints.tactical'
                    },
                    options: [
                        {
                            id: 'op1',
                            textKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.options.op1.text',
                            rationaleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.options.op1.rationale',
                            technicalImpact: 0,
                            reputationImpact: 30,
                            budgetImpact: -2000,
                            complianceScore: 20,
                            isOptimal: true
                        },
                        {
                            id: 'op2',
                            textKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.options.op2.text',
                            rationaleKey: 'scenarios.es-tourism-gdpr-email-breach.dilemmas.d3.options.op2.rationale',
                            technicalImpact: 0,
                            reputationImpact: -40,
                            budgetImpact: 0,
                            complianceScore: -30
                        }
                    ]
                }
            ]
        }
    ],

    scoringCriteria: {
        technical: 0.2,
        governance: 0.4,
        communication: 0.2,
        compliance: 0.2
    },

    learningOutcomesKeys: [
        'scenarios.es-tourism-gdpr-email-breach.learning.outcome1',
        'scenarios.es-tourism-gdpr-email-breach.learning.outcome2',
        'scenarios.es-tourism-gdpr-email-breach.learning.outcome3'
    ],

    achievements: [],

    metadata: {
        id: '08-es-tourism-gdpr-email-breach',
        createdDate: '2026-01-28',
        lastUpdated: '2026-03-20',
        tags: ['gdpr', 'email', 'spain', 'aepd', 'privacy', 'tourism', 'student'],
        author: 'GoPyme Security Team',
        status: 'Production-Ready',
        disclaimer: '🚨 AVISO LEGAL Y DE SIMULACIÓN 🚨: Ficción y Propósito Educativo. Este escenario es una simulación didáctica. Todos los personajes, empresas y ataques descritos son ficticios; cualquier semejanza con la realidad es coincidencia. Menciones a marcos de trabajo, leyes o agencias reguladoras buscan preparar para el mundo real. Las acciones e hilos no constituyen asesoramiento técnico ni legal vinculante.'
    },

    translations: {
        es: translations
    }
};

export default esTourismGDPRScenario;
