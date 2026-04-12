# SOC Tutor (Cybersecurity RAG Multiagent System)

🇺🇸 [English Version](README.md) | 📜 [Guía de Arquitectura](CONTRIBUTING.md)

Sistema profesional de feedback pedagógico basado en IA para entrenamiento en respuesta a incidentes de ciberseguridad. Optimizado con una arquitectura **"English-First Reasoning / Multilingual Delivery"** para máxima eficiencia de tokens y precisión técnica.

## 🚀 Arquitectura Avanzada

Este sistema ha evolucionado de un MAS básico a una arquitectura de grado de producción que prioriza el costo y la exactitud:

1.  **Razonamiento Global (English-First)**: El núcleo lógico de los agents (Analyst, Explainer, Validator) utiliza prompts en inglés. Esto reduce el consumo de tokens en un ~25% y mejora la adherencia a manuales técnicos originales (NIST/MITRE).

2.  **Caché Semántico Universal**: Implementamos una capa de caché que normaliza las intenciones del jugador al inglés antes de realizar el *matching*. Esto permite que una misma respuesta de IA sirva para jugadores en español, portugués e inglés, aumentando drásticamente el *hit rate* y reduciendo costos de LLM.
3.  **RAG Híbrido con Capa de Traducción**: El sistema traduce automáticamente las consultas técnicas del jugador al inglés para buscar en las fuentes originales de mayor fidelidad, combinando búsqueda semántica con búsqueda exacta de IDs técnicos (IPs, Tácticas MITRE).
4.  **Entrega Multilingüe Adaptativa**: El **Explainer Agent** traduce el análisis técnico a un lenguaje pedagógico en el idioma preferido del usuario (ES, PT, EN), ajustando el tono según su nivel de experiencia.


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
├── src/
│   ├── agents/        # Lógica de agents (Prompts EN, Output Multilenguaje)
│   ├── orchest/        # Orquestador (Pipeline con Observabilidad y Caché)
│   ├── rag/            # RAG Híbrido (English-Targeted Search)
│   └── utils/          # Caché Semántico, LLMClient, Glosario
├── data/
│   ├── docs/           # Fuentes oficiales (EN/ES)
│   └── sample_scenarios/ # Escenarios standalone (Ej: ar-fintech-idor)
└── scripts/            # Herramientas de ingesta y validación
```

## 🚀 Instalación y Uso Standalone

```bash
# 1. Preparar entorno
pip install -r requirements.txt
cp .env.example .env

# 2. Ingesta de conocimiento (Fuentes NIST/MITRE EN)
python scripts/download_sources.py
python 02-data-ingestion/ingest_docs.py

# 3. Ejecutar Demostración
python scripts/verify_mixed_context.py
```

## 🧠 Decisiones de Diseño "Cloud-Lite"

Para garantizar que el proyecto sea evaluable sin fricciones y escalable, se eliminaron dependencias de nubes propietarias pesadas, permitiendo que el sistema corra con una latencia mínima y costo cero bajo la capa gratuita de Gemini 2.0. El diseño "Standalone" permite validar el motor de feedback de forma autónoma con datos sintéticos de alta fidelidad.

---
**Proyecto Final de Especialización - SOC Tutor RAG System**
*Razonamiento en Inglés, Corazón en Latam.*