# Memoria Técnica y Documento Ejecutivo: SOC Tutor RAG System

**Autor:** Marcela Rosana Inda
**Contexto:** Proyecto Final - Bootcamp AI Engineer con Python
**Fecha:** Mayo 2026

---

## 1. Resumen Ejecutivo

SOC Tutor es un **Motor Cognitivo Multi-Agente** diseñado para revolucionar el entrenamiento de analistas en Centros de Operaciones de Seguridad (SOC). A diferencia de los simuladores convencionales que proporcionan respuestas estáticas, o los wrappers de modelos de lenguaje (LLMs) que sufren de alucinaciones forenses, SOC Tutor actúa como un mentor dinámico, auditable y escalable, evaluando las decisiones tácticas de los analistas en tiempo real contra los estándares de la industria (MITRE ATT&CK, NIST, GDPR).

## 2. El Problema a Resolver

El entrenamiento en ciberseguridad enfrenta tres grandes desafíos al usar Inteligencia Artificial:
1. **Alucinación Técnica Forense:** Los modelos generativos inventan IPs, logs y eventos que no existieron en la simulación, confundiendo al alumno.
2. **Complacencia Pedagógica:** La IA tiende a adoptar un tono complaciente, aprobando acciones ineficientes para evitar "discutir" con el usuario.
3. **Vulnerabilidad y Costo:** Depender de prompts monolíticos gigantescos hacia una única API resulta en sistemas inestables, costosos y susceptibles a *Prompt Injections*.

## 3. Arquitectura y Solución de Ingeniería

Para superar estos problemas, SOC Tutor abandonó el diseño de "prompt único" en favor de una arquitectura basada en el patrón **Manager of Drafts** (Gestor de Borradores), estructurando el razonamiento en un comité de 5 agentes especializados:

*   **Guard Agent (Seguridad):** Primera línea de defensa. Filtra entradas maliciosas utilizando heurísticas y un LLM clasificador para evitar ataques de inyección de estado.
*   **Analista (Táctica):** Opera bajo el patrón *ReAct* (Razonamiento y Acción). Es el único con acceso a la investigación activa.
*   **Gobernanza (Cumplimiento):** Revisa la acción desde una óptica legal y ética, validando contra normativas de privacidad.
*   **Explicador (Pedagogía):** Adapta el nivel de lenguaje técnico al *seniority* del jugador, traduciendo de la lingua franca interna (Inglés) al idioma de la UI (Deep Translation Gateway).
*   **Validador (Calidad):** Implementa un patrón de **Juez Asimétrico**. Utiliza modelos de proveedores competidores (NVIDIA NIM vs Gemini) para evitar el sesgo de confirmación, exigiendo además integridad criptográfica (SHA-256) de las fuentes citadas.

## 4. Infraestructura Híbrida: Cognitive RAG y MCP

El núcleo de la verdad del sistema se divide metodológicamente en dos:
1. **Teoría (RAG):** Las metodologías de respuesta (NIST 800-61) y las tácticas adversariales (MITRE) se inyectan a través de ChromaDB.
2. **Realidad Forense (Protocolo MCP):** Para evitar la "alucinación forense", el agente Analista no lee logs del RAG, sino que se conecta mediante el estándar **Model Context Protocol (MCP)** a servidores locales simulados de telemetría (SIEM) y contención (EDR). El LLM observa la misma evidencia determinista que vería un analista real.

## 5. Resiliencia, Gobernanza y Despliegue

### 5.1. Cascada de Resiliencia (Triple-Layer Fallback)
El sistema está diseñado para nunca interrumpir el proceso pedagógico. Cuenta con una cascada automática de reintentos entre proveedores:
*   **Capa 1:** Google Gemini (Latencia y costo óptimos).
*   **Capa 2:** Groq Llama-3 (Respaldo ultrarrápido).
*   **Capa 3:** NVIDIA NIM Llama-3.3-70B / DeepSeek (Validación Suprema).

En caso de fallo total de la red externa, un sistema de *Fail-Safe JSON* emite un feedback determinista pre-calculado, garantizando disponibilidad.

### 5.2. Control Financiero y "Cloud-Lite"
El orquestador incluye políticas de *Session Isolation* que evitan el *Wallet-Exhaustion DoS*. Con un costo operativo que ronda los **~$0.003 USD por evaluación completa**, el sistema es económicamente viable para uso institucional masivo. La infraestructura se diseñó para desplegarse ágilmente (Next.js en Vercel, FastAPI en Hugging Face Spaces).

## 6. Conclusión Académica

SOC Tutor no es simplemente un asistente conversacional; es una aplicación de ingeniería de IA de grado de producción. Demuestra que mediante patrones de orquestación estrictos (MCP, Manager of Drafts, Validación Asimétrica y English-First Reasoning), es posible domesticar el no-determinismo de los LLMs, creando una herramienta educativa **confiable, segura, escalable y auditable**.
