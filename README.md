# SOC Tutor (Cybersecurity RAG Multiagent System)

📖 [Versión en Español](README_ES.md) | 📜 [Architectural Guidelines](CONTRIBUTING.md)

Professional AI-driven pedagogical feedback system for cybersecurity incident response training. Optimized with an **"English-First Reasoning / Multilingual Delivery"** architecture for maximum token efficiency and technical precision.

[![Live Demo](https://img.shields.io/badge/Demo-Try%20it%20Live-cyan?style=for-the-badge&logo=vercel)](https://soc-tutor-workstation.vercel.app)

## 🚀 Advanced Architecture

This system has evolved from a basic Multi-Agent System (MAS) to a production-grade architecture that prioritizes cost and accuracy:

1.  **Global Reasoning (English-First)**: The logic core of the agents (Analyst, Explainer, Validator) uses English prompts. This reduces token consumption by ~25% and improves compliance with original technical manuals (NIST/MITRE).
2.  **Universal Semantic Cache**: We implemented a cache layer that normalizes player intentions to English before matching. This allows a single AI response to serve players in Spanish, Portuguese, and English, drastically increasing the hit rate and reducing LLM costs.
3.  **Hybrid RAG with Translation Layer**: The system automatically translates technical player queries into English to search the highest-fidelity original sources, combining semantic search with exact matching of technical IDs (IPs, MITRE Tactics).
4.  **Adaptive Multilingual Delivery**: The **Explainer Agent** translates the technical analysis into pedagogical language in the user's preferred language (ES, PT, EN), adjusting the tone according to their experience level.


## 🌟 Recent Updates (Latest Sessions)

- **MCP Integration (Model Context Protocol)**: Integrated EDR and SIEM log simulations using MCP servers, decoupling interactive tools from the core RAG system for a more realistic immersive experience.
- **AI Engineering Optimization (Latency & Cost)**: Implemented RAG Context Splitting (Technical vs Strategic), Top-K pruning, and Semantic Cache hardening, reducing prompt overhead by ~50%.
- **Resilience Protocol**: Added invisible background retry loops and "Immersion Shields" for connection failures to ensure a seamless technical workspace experience.
- **Enhanced UI/UX Immersion**: Added ambient audio to the SOC Workstation and refined the Analyst Mentor interface for high-fidelity gameplay.

## 🛠️ Core Technologies

-   **Models**: Google `gemini-2.0-flash` (via a unified LLMClient with support for Groq as high-speed backbone).
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
# Ensure your .env file has GEMINI_API_KEY or GROQ_API_KEY
cp .env.example .env 

# 3. Launch the full stack
docker compose up -d --build
```

- **Frontend (Workstation)**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🛠️ Manual Installation (Standalone)

## 🧠 Professional AI Engineering

For a deep dive into the technical reasoning, cost optimizations, and resilience patterns implemented in this project, please consult the:

📜 **[Architectural Decisions & AI Design Log](ARCHITECTURAL_DECISIONS.md)**

1.  **HuggingFace Spaces (Backend)**: Chosen as the hosting provider for the Python engine due to its **16GB RAM free tier**, which is necessary for the RAG index and local embedding models.
2.  **Next.js 14 (Frontend)**: Utilized the App Router for optimal performance. The decoupled architecture allows the frontend to run on Vercel with zero latency.
3.  **Framer Motion & Tailwind**: Selected to provide a **"Visceral Impact"** for the academic jury, ensuring the UI feels like a state-of-the-art SOC workstation rather than a simple chat bot.
4.  **"Manager of Drafts" Multi-Agent Flow**: Uses an asymmetric judge pattern where a secondary LLM (Gemini/Groq) validates the pedagogical quality of the feedback before it reaches the player.

---
**Final Specialization Project - SOC Tutor RAG System**
*English Reasoning, LATAM Heart.*