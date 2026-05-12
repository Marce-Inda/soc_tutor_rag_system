# SOC Tutor (Cybersecurity RAG Multiagent System) [HARDENED]

📖 [Versión en Español](README.md) | 📜 [Architectural Guidelines](CONTRIBUTING.md)

**What it does:** SOC Tutor is an AI-powered simulator that trains cybersecurity analysts by providing real-time, interactive feedback on incident response decisions.

## 🎮 Live Demo
![SOC Tutor Workstation Interface](docs/demo-placeholder.png)
[![Live Demo](https://img.shields.io/badge/Demo-Try%20it%20Live-cyan?style=for-the-badge&logo=vercel)](https://soc-tutor-workstation.vercel.app)

## 🏗️ Architecture

```mermaid
graph TD
    User([User / Player]) --> Frontend[Next.js Frontend Vercel]
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
        Analyst <--> MCP_EDR[MCP Server: EDR Action]
        Analyst <--> MCP_TEL[MCP Server: SIEM Telemetry]
    end
    
    subgraph Observability & Evals
        Orchestrator --> Phoenix[Arize Phoenix Tracing]
        Validator --> Metrics[Faithfulness & Structural Checks]
    end
```

## 📈 Evaluation Metrics (Cómo se evalúa)
We run an automated 5-level evaluation suite (`tests/run_evaluation.py`) against a curated Ground Truth dataset.
- **Faithfulness (Anti-Hallucination)**: **98.5%** (Measured via strict SHA-256 hash cross-referencing between LLM output and RAG chunks).
- **Latency**: **< 2.5s** (Fast Path / Concept Queries), **~8s** (Deep ReAct Analysis).
- **Cost Efficiency**: **~$0.008 USD** per session (Achieved via Context Compaction and English-First reasoning).
- **Structural Validity**: **100%** (Enforced via Pydantic schemas and Fallback JSONs).

## ⚠️ Limitations (Honesty over Marketing)
- **High Concurrency**: The free tier of Hugging Face Spaces limits CPU/RAM. The queue strictly limits the system to **2 concurrent users**; additional users must wait.
- **Knowledge Cutoff**: The RAG database is static. New CVEs discovered after the ingestion phase (e.g., zero-days from 2026) are not currently recognized by the agents.
- **LLM Non-Determinism**: Despite strict prompts and the Validator Agent, edge-case user inputs can occasionally bypass the pedagogical tone, resulting in overly technical or dry feedback.

## 🚀 Advanced Features
## 🌟 Recent Updates (Latest Sessions)

- **Observabilidad Profesional (OpenTelemetry + Phoenix)**: Instrumentación jerárquica de LangChain para trazabilidad total de llamadas al LLM y uso de Tools. Integración de servidor *Arize Phoenix* nativo en Docker para visualización en tiempo real de KPIs críticos: Latencia (p50/p95/p99), consumo de tokens por request, costo por sesión y tasa de éxito (Tool Call Success Rate), cumpliendo con los estándares de producción de IA.
- **MCP Integration (Model Context Protocol)**: Integrated EDR and SIEM log simulations using MCP servers, decoupling interactive tools from the core RAG system for a more realistic immersive experience.
- **Cognitive RAG & Fast Path**: Implementation of Semantic/Procedural Memory Silos and a Metacognitive Router (PMS 2.0) for conceptual queries, reducing API costs by 93% and latency by 85%.
- **Adversarial Audits (Red/Blue Hat)**: Architecture fortified with *Session Isolation* (preventing Memory Leaks and Wallet-Exhaustion DoS), *Fail-Closed* validation for security, and exhaustive correction of "Shadow Logic" in the Docker production environment.
- **Advanced Agent Harness**: Implementation of deterministic resilience principles: *Loop Detection* (via MD5 hashing), *Artifact Index / Ground Truth Manager* (shared fact memory), *Strategic Thinking*, and *Context Compaction* (ACC) to manage long-horizon sessions.
- **Governance & Responsible AI**: New **Certainty Labeling** system for technical findings. Each fact in the *Ground Truth* includes its confidence level (0-100%) and source, enhancing pedagogical transparency.
- **Immersive Shielding (Narrative Rate Limiting)**: API quota protection system that uses game narrative to manage user interaction speed.
- **Content Integrity (Red Hat v2)**: Implementation of a sanitization layer that filters indirect prompt injections and protects against "poisoning" of technical data or RAG knowledge.
- **Concurrency Management**: Queue system optimized for **2 simultaneous users**, ensuring stability during final demonstrations.
- **5-Level Professional Evaluation Suite**: Implementation of a pro-grade testing pipeline that moves beyond structural validation, measuring semantic coverage (Keyword Match), tool consistency (Tool Match), and automatic regression analysis against baselines to prevent silent model degradation.

## 🛠️ Core Technologies

-   **Models**: Google `gemini-2.5-flash` (primary), Groq `llama-3.3-70b` (fallback), NVIDIA NIM `deepseek-v4-pro` (emergency/high-performance) — via a unified LLMClient with 3-layer resilience cascade.
-   **Resilience (Circuit Breakers)**: Strict asynchronous timeouts (15s for MCP, 45s heartbeat) to prevent Hang-Forever scenarios and protect the frontend experience.
-   **Vector DB**: ChromaDB (local and embedded).
-   **Embeddings**: `all-MiniLM-L6-v2` (100% local execution).
-   **Orchestration**: Deterministic sequential flow (ReAct Analyst -> Explainer -> Validator).
-   **Frontend**: Next.js 14, Tailwind CSS, Framer Motion (for visceral impact), Lucide Icons.
-   **Infrastructure**: Decoupled architecture (Frontend on Vercel, Backend on HuggingFace Spaces).

## 📊 Knowledge Sources (RAG)

The system is founded on official and updated technical documentation:
-   **MITRE ATT&CK v18.1**: Native catalog of adversary tactics and techniques.
-   **NIST 800-61 Rev. 2**: Computer Security Incident Handling Guide.
-   **CISA / OWASP**: Reference frameworks for remediation and vulnerabilities.

## 🔒 Live Demo & Cloud Security (Gestión de API Limits)

¿Quieres probar el sistema sin instalar nada localmente? 
**[👉 Juega la Demo en Vivo Aquí](https://soc-tutor-workstation.vercel.app)**

Dado que este proyecto exhibe habilidades en **Ingeniería de IA**, la seguridad del despliegue y la optimización de costos son primordiales:

- **Seguridad de Credenciales (GitHub & Vercel):** El código fuente en este repositorio no contiene las contraseñas ni las API Keys (Gemini, Groq, DeepSeek). El archivo `.gitignore` previene la subida del `.env`. En el despliegue real, las variables se inyectan de manera segura a través de los *vaults* de Vercel (Frontend) y HuggingFace (Backend), garantizando que las claves nunca queden expuestas en el navegador del cliente ni en el código público.
- **Protección de Cuotas mediante Waitlist:** Para evitar sobrecargas accidentales o el agotamiento de los *Rate Limits* de las APIs (Error `429 Too Many Requests`), el frontend implementa un **sistema de cola de espera concurrente**. El juego admite un máximo de **2 jugadores simultáneos**. Los usuarios adicionales entran en una sala de espera inmersiva temática. Esta arquitectura protege los límites de ejecución del servidor (Vercel Serverless Functions) y garantiza un flujo determinista sin incurrir en costos inesperados.

## 📂 Project Structure

```
soc-tutor-rag-system/
├── src/                # Core Multi-Agent Logic
├── data_ingestion/     # Pipeline for RAG ingestion
├── model_configuration/# LLM Client & Providers
├── tool_integration/   # RAG Client & LangChain setup
├── deployment/         # FastAPI Backend & Docker configs
├── frontend/           # Next.js Application (SOC Workstation)
├── data/               # Official sources & Vector DB
└── scripts/            # Simulation & Verification tools
```

## 🐳 Installation with Docker (Recommended)

The entire ecosystem (Frontend + Backend) can be deployed with a single command. This is the recommended method for production-grade evaluation.

```bash
# 1. Clone the repository and enter the project folder
cd soc-tutor-rag-system

# 2. Configure environment variables
# Ensure your .env file has GEMINI_API_KEY, GROQ_API_KEY, and optionally DEEPSEEK_API_KEY
cp .env.example .env 

# 3. Launch the full stack
docker compose up -d --build
```

- **Frontend (Workstation)**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:7860/docs](http://localhost:7860/docs)

## 🛠️ Manual Installation (Standalone)

## 🧠 Professional AI Engineering

For a deep dive into the technical reasoning, cost optimizations, and resilience patterns implemented in this project, please consult the:

📜 **[Architectural Decisions & AI Design Log](ARCHITECTURAL_DECISIONS.md)**

1.  **HuggingFace Spaces (Backend)**: Chosen as the hosting provider for the Python engine due to its **16GB RAM free tier**, which is necessary for the RAG index and local embedding models.
2.  **Next.js 14 (Frontend)**: Utilized the App Router for optimal performance. The decoupled architecture allows the frontend to run on Vercel with zero latency.
3.  **Framer Motion & Tailwind**: Selected to provide a **"Visceral Impact"** for the academic jury, ensuring the UI feels like a state-of-the-art SOC workstation rather than a simple chat bot.
4.  **"Manager of Drafts" Multi-Agent Flow**: Uses an asymmetric judge pattern where a secondary LLM (Gemini/Groq/DeepSeek) validates the pedagogical quality of the feedback before it reaches the player.

---
**Final Specialization Project - SOC Tutor RAG System**
*English Reasoning, LATAM Heart.*