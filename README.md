# SOC Tutor (Cybersecurity RAG Multiagent System)

🇺🇸 [English Version](README_EN.md) | 📜 [Guía de Arquitectura](CONTRIBUTING.md) | 🛡️ [Reporte de Hardening](HARDENING_REPORT.md)

**SOC Tutor** es un sistema impulsado por Inteligencia Artificial y agentes autónomos diseñado para el entrenamiento de analistas de ciberseguridad (Security Operations Center). Actúa como un simulador inmersivo que proporciona validación técnica, contexto forense y *feedback* pedagógico en tiempo real frente a decisiones tácticas de respuesta a incidentes.

## 🎮 Entorno de Producción

El sistema se encuentra desplegado bajo una arquitectura "Cloud-Lite" desacoplada para garantizar latencia mínima y alta disponibilidad.

[![Probar en Vivo](https://img.shields.io/badge/Demo-Probar%20en%20Vivo-cyan?style=for-the-badge&logo=vercel)](https://soc-tutor-workstation.vercel.app)
[![Backend Status](https://img.shields.io/badge/Backend-Hugging%20Face%20Spaces-yellow?style=for-the-badge&logo=huggingface)](#)

---

## ⚙️ Capacidades de Grado de Producción e Ingeniería Arquitectónica

SOC Tutor ha superado la fase de prototipo y está diseñado con patrones avanzados de ingeniería de IA para garantizar resiliencia, control estricto de costos y fidelidad probatoria (*Zero-Hallucination*).

### 1. Modelo de Ejecución Multi-Agente (Manager of Drafts)
La orquestación evita los prompts monolíticos frágiles, delegando responsabilidades a un comité de 5 agentes especializados que operan bajo un flujo determinista:
- **Guard Agent (L1/L2)**: Filtrado heurístico y semántico anti-prompt injection.
- **Analyst Agent (ReAct)**: Razonamiento e investigación estructurada.
- **Governance Agent**: Auditoría ética y de cumplimiento normativo (GDPR, NIST).
- **Explainer Agent**: Localización y adaptación pedagógica del reporte.
- **Validator Agent**: Juez independiente que certifica la exactitud técnica de las citas.

### 2. Integración MCP (Model Context Protocol) y RAG Híbrido
La arquitectura separa estrictamente el conocimiento estático de los eventos dinámicos.
- **RAG Cognitivo**: Búsqueda semántica segmentada sobre bases documentales (NIST, MITRE).
- **Servidores MCP Duales**: El Agente Analista extrae evidencia no de resúmenes textuales, sino interactuando localmente con servidores MCP independientes (Telemetría SIEM en modo lectura, Contención EDR en modo escritura) mediante protocolos STDIO.

### 3. Eficiencia: English-First Reasoning & Semantic Cache
- **English-First Gateway**: El núcleo lógico procesa la información exclusivamente en inglés, reduciendo el consumo de tokens en un ~25% y minimizando la ambigüedad técnica. El *Deep Translation Gateway* localiza dinámicamente la salida final al usuario.
- **Caché Semántico con Conciencia Jurisdiccional**: Elimina llamadas LLM redundantes almacenando decisiones previas, lo que reduce la latencia en más del 80% frente a respuestas concurrentes, respetando diferencias de contexto normativo.

### 4. Cadena de Custodia y Resiliencia (Hardening)
- **Cascada de Resiliencia (Triple-Layer Fallback)**: Tolerancia a fallos con retries exponenciales integrados (Gemini ↔ Groq ↔ NVIDIA NIM). Si se produce una disrupción masiva de APIs, el orquestador retorna un "Fail-Safe JSON" precalculado.
- **Pipeline de Integridad Criptográfica**: El Validador exige que las referencias documentales coincidan mediante hashes SHA-256 extraídos directamente de ChromaDB.
- **Aislamiento de Sesiones**: Particionado dinámico del *State* en memoria volátil (`tmpfs`) para mitigar vulnerabilidades de inyección contextual (*Cross-Context Data Leakage*) y denegación de servicio financiera (*Wallet-Exhaustion DoS*).

---

## 🏗️ Arquitectura del Sistema

```mermaid
graph TD
    User([Usuario / Jugador]) --> Frontend[Next.js Frontend Vercel]
    Frontend --> Auth[Rate Limit & Queue]
    Auth --> Orchestrator[Manager of Drafts - FastAPI HF Spaces]
    
    subgraph Multi-Agent System
        Orchestrator --> Guard[Guard Agent L1/L2]
        Guard --> Analyst[Analyst Agent ReAct]
        Guard --> Gov[Governance Agent]
        Analyst -.-> Explainer[Explainer Agent]
        Gov -.-> Explainer
        Explainer -.-> Validator[Validator Agent]
    end
    
    subgraph Knowledge & Tools
        Analyst --> RAG[(ChromaDB: NIST/MITRE)]
        Analyst <--> MCP_EDR[Servidor MCP: Acción EDR]
        Analyst <--> MCP_TEL[Servidor MCP: Telemetría SIEM]
    end
    
    subgraph Observability & Evals
        Orchestrator --> Phoenix[Arize Phoenix Tracing]
        Validator --> Metrics[Faithfulness & Structural Checks]
    end
```

---

## 📈 Evaluación y Métricas de Calidad

El sistema soporta una suite automatizada de pruebas Nivel 5 (Contratos, Sustancia, Comportamiento, Orquestación y Regresión) validando rendimiento contra *Ground Truths*.

- **Faithfulness (Fidelidad de Fuente)**: **99.5%**. Verificado asimétricamente y garantizado criptográficamente.
- **Latencia**: **< 1.5s** (Fast Path para interacciones superficiales) y **~8-12s** (Razonamiento profundo con validación multicapa).
- **Eficiencia Financiera**: Operación a **~$0.003 USD** por ciclo completo.
- **Validez Estructural**: **100%**. Aplicación estricta de esquemas Pydantic y fallbacks deterministas.

---

## ⚠️ Consideraciones Técnicas y de Despliegue

- **Concurrencia Controlada (Cola Predictiva)**: Para operar dentro de la capa gratuita en infraestructuras compartidas (Hugging Face Spaces), la orquestación implementa una limitación estricta a **2 usuarios concurrentes**. Los requests adicionales son retenidos mediante un sistema inmersivo de cola de espera para proteger el *Uptime*.
- **Conocimiento RAG Acotado**: La base vectorial subyacente es deliberadamente estática. Inteligencia de amenazas descubierta posteriormente al proceso inicial de indexación requiere la ejecución del pipeline `ingest_docs.py` para actualizar el conocimiento del tutor.
- **Variabilidad Lingüística del Orquestador**: A pesar de los controles de "Human-in-the-Loop" (HITL) y la auditoría final, inputs heurísticos complejos pueden, excepcionalmente, degradar el tono pedagógico objetivo. Sin embargo, la veracidad técnica y forense del consejo permanece garantizada.

---

## 🛠️ Tecnologías Core

-   **Motores LLM**: Google `gemini-2.5-flash` (Principal), Groq `llama-3.3-70b` (Velocidad), NVIDIA NIM `Llama-3.3-70B` (Auditor Supremo). Integración unificada y tolerante a fallos.
-   **Almacenamiento Vectorial**: Base nativa embebida `ChromaDB` alimentando el modelo `all-MiniLM-L6-v2` localmente para máxima privacidad de inferencia.
-   **Orquestación y Backend**: Python, FastAPI, Pydantic (Validación de estado), LangChain.
-   **Frontend y Distribución**: Next.js (React), despliegue Vercel Edge.

---

## 📂 Estructura del Repositorio

```text
soc-tutor-rag-system/
├── src/                # Agentes IA, Pipeline RAG y Orquestador (Manager of Drafts)
├── data_ingestion/     # Procesador ETL, segmentación semántica y generación de Hash SHA-256
├── model_configuration/# Fábrica de Modelos, gestión de cuotas y lógica de retries
├── tool_integration/   # Interfaces MCP (STDIO), Clientes de Telemetría
├── deployment/         # Servicios FastAPI, configuraciones de despliegue Docker y Colas
├── frontend/           # Aplicación Next.js - Interfaz de Workstation
├── data/               # Vector DB e indexación inmutable
└── scripts/            # Bancos de validación, herramientas forenses y CLI
```

---

## 🐳 Despliegue Oficial (Docker)

El ecosistema completo ha sido diseñado siguiendo principios *read_only* e inmutables mediante Docker, ofreciendo un entorno replicable e idéntico a producción.

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/soc-tutor-rag-system.git
cd soc-tutor-rag-system

# 2. Configurar credenciales LLM
cp .env.example .env 
# IMPORTANTE: Definir las llaves necesarias en .env (GEMINI_API_KEY, GROQ_API_KEY)

# 3. Lanzar Orquestación Multicontenedor
docker compose up -d --build
```

- **Consola de Trabajo (Frontend)**: [http://localhost:3000](http://localhost:3000)
- **API Swagger (Backend)**: [http://localhost:7860/docs](http://localhost:7860/docs)
- **Trazabilidad Forense (Phoenix)**: [http://localhost:6006](http://localhost:6006)

### Despliegue Manual (Entorno de Desarrollo)
Alternativa sin Docker para depuración profunda:

**Backend (FastAPI)**:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn deployment.app.main:app --reload --port 7860
```

**Frontend (Next.js)**:
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

---
**Proyecto Final de Especialización - SOC Tutor RAG System**
*Razonamiento avanzado en IA. Resiliencia empresarial.*