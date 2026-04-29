# SOC Tutor (Cybersecurity RAG Multiagent System)

🇺🇸 [English Version](README.md) | 📜 [Guía de Arquitectura](CONTRIBUTING.md)

Sistema profesional de feedback pedagógico basado en IA para entrenamiento en respuesta a incidentes de ciberseguridad. Optimizado con una arquitectura **"English-First Reasoning / Multilingual Delivery"** para máxima eficiencia de tokens y precisión técnica.

[![Demo en Vivo](https://img.shields.io/badge/Demo-Probar%20en%20Vivo-cyan?style=for-the-badge&logo=vercel)](https://soc-tutor-workstation.vercel.app)

## 🚀 Arquitectura Avanzada

Este sistema ha evolucionado de un MAS básico a una arquitectura de grado de producción que prioriza el costo y la exactitud:

1.  **Razonamiento Global (English-First)**: El núcleo lógico de los agents (Analyst, Explainer, Validator) utiliza prompts en inglés. Esto reduce el consumo de tokens en un ~25% y mejora la adherencia a manuales técnicos originales (NIST/MITRE).

2.  **Caché Semántico Universal**: Implementamos una capa de caché que normaliza las intenciones del jugador al inglés antes de realizar el *matching*. Esto permite que una misma respuesta de IA sirva para jugadores en español, portugués e inglés, aumentando drásticamente el *hit rate* y reduciendo costos de LLM.
3.  **RAG Híbrido con Capa de Traducción**: El sistema traduce automáticamente las consultas técnicas del jugador al inglés para buscar en las fuentes originales de mayor fidelidad, combinando búsqueda semántica con búsqueda exacta de IDs técnicos (IPs, Tácticas MITRE).
4.  **Entrega Multilingüe Adaptativa**: El **Explainer Agent** traduce el análisis técnico a un lenguaje pedagógico en el idioma preferido del usuario (ES, PT, EN), ajustando el tono según su nivel de experiencia.



## 🌟 Últimas Actualizaciones (Sesiones Recientes)

- **Integración de MCP (Model Context Protocol)**: Se integraron herramientas de contención EDR y análisis de logs SIEM utilizando servidores MCP, desacoplando la interacción táctica del sistema RAG principal para un realismo superior.
- **RAG Cognitivo y Fast Path**: Implementación de Silos de Memoria Semántica/Procedural y un Enrutador Metacognitivo (PMS 2.0) para consultas conceptuales, reduciendo costos de API en un 93% y latencia en un 85%.
- **Auditorías Adversariales (Red Hat / Blue Hat)**: Arquitectura fortificada con *Session Isolation* (previniendo Memory Leaks y Wallet-Exhaustion DoS), validación *Fail-Closed* para seguridad y corrección exhaustiva de "Shadow Logic" en el entorno de producción (Docker).
- **Lista de Espera y Gestión de Colas**: Se implementó un *Queue Manager* en el backend (con Anti-Camping/Zombie expulsion) y una *Waitlist* en el frontend para evitar sobrecargas de API durante demos con concurrencia.

## 🛠️ Tecnologías Core

-   **Modelos**: Google `gemini-2.0-flash` (vía LLMClient unificado con soporte para Groq y Ollama).
-   **Vector DB**: ChromaDB (local y embebido).
-   **Embeddings**: `all-MiniLM-L6-v2` (ejecución 100% local).
-   **Orquestación**: Flujo secuencial determinista (Security Guard -> Memory -> RAG -> Analyst -> Explainer -> Validator).
-   **Frameworks**: LangChain, Pydantic, Tenacity (Resiliencia).

## 📊 Fuentes de Conocimiento (RAG)

El sistema se fundamenta en documentación técnica oficial y actualizada:
-   **MITRE ATT&CK v18.1**: Catálogo nativo de tácticas y técnicas de adversarios.
-   **NIST 800-61 Rev. 2**: Guía de manejo de incidentes de seguridad informática.
-   **CISA / OWASP**: Marcos de referencia para remediación y vulnerabilidades.

## 📂 Estructura del Proyecto

```
soc-tutor-rag-system/
├── src/                # Lógica core de Agentes
├── data_ingestion/     # Pipeline de ingesta para RAG
├── model_configuration/# Cliente de LLMs y Proveedores
├── tool_integration/   # Cliente RAG y configuración de LangChain
├── deployment/         # Backend FastAPI y configs de Docker
├── frontend/           # Aplicación Next.js (Workstation)
├── data/               # Fuentes oficiales y Vector DB
└── scripts/            # Herramientas de simulación y verificación
```

## 🐳 Instalación con Docker (Recomendado)

Todo el ecosistema (Frontend + Backend) puede desplegarse con un solo comando. Este es el método recomendado para evaluación profesional.

```bash
# 1. Entrar a la carpeta del proyecto
cd soc-tutor-rag-system

# 2. Configurar variables de entorno
# Asegúrate de que el archivo .env tenga GEMINI_API_KEY o GROQ_API_KEY
cp .env.example .env 

# 3. Levantar todo el stack
docker compose up -d --build
```

- **Frontend (Workstation)**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🛠️ Instalación Manual (Standalone)

## 🧠 Decisiones de Diseño "Cloud-Lite"

Para garantizar que el proyecto sea evaluable sin fricciones y escalable, se eliminaron dependencias de nubes propietarias pesadas, permitiendo que el sistema corra con una latencia mínima y costo cero bajo la capa gratuita de Gemini 2.0. El diseño "Standalone" permite validar el motor de feedback de forma autónoma con datos sintéticos de alta fidelidad.

---
**Proyecto Final de Especialización - SOC Tutor RAG System**
*Razonamiento en Inglés, Corazón en Latam.*