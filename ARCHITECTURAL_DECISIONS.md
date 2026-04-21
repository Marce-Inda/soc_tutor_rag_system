# SOC Tutor: AI Engineering & Architectural Decisions

Este documento detalla las decisiones técnicas y estratégicas tomadas durante el desarrollo del sistema **SOC Tutor**, fundamentadas en principios de Ingeniería de IA, optimización de costos, resiliencia y experiencia de usuario (UX) técnica.

---

## 1. Gestión de Resiliencia y Experiencia Inmersiva
### Decisión: Supresión de Errores Técnicos y Reintentos de Fondo
- **Problema**: Los fallos en la conexión con el motor de IA o micro-desconexiones en herramientas tácticas (MCP) provocaban errores rojos en la consola, rompiendo la inmersión del jugador y su confianza en el sistema.
- **Solución (Arquitectura)**:
    - **Escudo de Inmersión**: Implementación de mensajes de fallback temáticos (*"Acción finalizada: Sin anomalías adicionales"*) que se muestran de inmediato en caso de error de red.
    - **Invisible Background Retry**: Lanzamiento de un bucle de reintento en segundo plano (8s de delay) que intenta recuperar el enlace sin que el jugador perciba el fallo inicial.
    - **Correlación de Timestamps**: Uso de identificadores de tiempo (`lastActionRef`) para evitar colisiones de estado si el jugador realiza una nueva acción mientras la anterior aún reintenta.
- **Rationale**: En un entorno de simulación táctica, el "Uptime" percibido es más importante que el reporte de errores crudos. El sistema debe fallar con elegancia, comportándose como un terminal de seguridad del mundo real.

## 2. Optimización Táctica: De RAG a Multi-Protocol (MCP)
### Decisión: Integración del Model Context Protocol (MCP)
- **Problema**: El sistema RAG tradicional proveía conocimiento teórico pero no datos reales de la simulación ("Ground Truth").
- **Solución**: Migración hacia una arquitectura donde el **Agente Analista** utiliza servidores MCP (EDR Server, SIEM Server) para interactuar con herramientas tácticas directas.
- **Impacto**: El modelo deja de "alucinar" logs y empieza a "leer" logs reales, separando el conocimiento estático (NIST/ISO) de los datos dinámicos de la partida.

## 3. Eficiencia de Costos y Latencia
### Decisión: Segmentación de Contexto (Context Splitting)
- **Problema**: Los prompts crecían exponencialmente al enviar el mismo bloque RAG (3000-5000 tokens) a cada uno de los 4 agentes en paralelo.
- **Solución**:
    - **Technical Facet**: Al Agente Analista (ReAct) solo se le envía contexto de MITRE y Evidencias.
    - **Strategic Facet**: Al Agente de Gobernanza solo se le envía contexto de NIST, GDPR y leyes locales.
- **Ahorro**: Reducción del **~50%** en el consumo de tokens por cada clic del usuario.

### Decisión: Podado de Conocimiento (Top-K & Truncation)
- **Técnica**: Reducción de recuperación a los 2-3 mejores fragmentos (`k=2/3`) y truncado agresivo a 1200 caracteres por documento.
- **Rationale**: Maximizar el "Signal-to-Noise Ratio". Inyectar demasiada teoría confunde al Analista y aumenta los costos sin mejorar la evaluación táctica.

## 4. Gobernanza y Seguridad Logística
### Decisión: Caché Semántica con Conciencia de Jurisdicción
- **Problema**: Un caché semántico simple basado en el texto de la acción podría entregar una respuesta de cumplimiento legal (GDPR España) a un jugador en otro contexto (AAIP Argentina) si el fingerprint técnica es similar.
- **Solución**: Hardening del "Fingerprint" del caché incluyendo `scenario_id`, `tipo_incidente` y `rol` del jugador como metadatos críticos para la identificación unívoca.
- **Seguridad**: Implementación de un **Guard Agent** (L1/L2) que valida entradas y salidas para prevenir inyecciones de prompt y asegurar la integridad de la IA.

## 5. Orquestación Multi-Agente (Manager of Drafts)
### Decisión: Patrón de Validación Asimétrica
- **Estructura**: El sistema utiliza un **Analista** (técnico) y un **Gobernanza** (legal) como borradores, un **Explicador** (pedagógico) como narrador, y un **Validador** (juez) como control de calidad.
- **Juez Asimétrico**: Activación de una "Asimetría de Modelos" donde, si el motor principal es Google Gemini, el Juez es Groq/Llama (o viceversa) para evitar sesgos de arquitectura en la validación del feedback.

---

## Resumen de KPI Técnicos de IA

| Categoría | Técnica Utilizada | Objetivo Principal |
| :--- | :--- | :--- |
| **Latencia** | Timeouts Estrictos (45s) | Prevenir colgado de workers de API. |
| **Resiliencia** | Background Retries | Mantener inmersión en fallos de red. |
| **Costo** | Context Splitting / Cache | Reducción de gasto en API Gemini y Groq. |
| **Precisión** | MCP + RAG Facets | Eliminar alucinaciones tácticas. |
| **Seguridad** | Semantic Fingerprinting | Cumplimiento preciso de jurisdicción legal. |

---
**Firmado**: *Ingeniería de IA - Proyecto SOC Tutor*
