# SOC Tutor (Cybersecurity RAG Multiagent System)

📖 [Versión en Español](README_ES.md) | 📜 [Architectural Guidelines](CONTRIBUTING.md)

Professional AI-driven pedagogical feedback system for cybersecurity incident response training. Optimized with an **"English-First Reasoning / Multilingual Delivery"** architecture for maximum token efficiency and technical precision.

## 🚀 Advanced Architecture

This system has evolved from a basic Multi-Agent System (MAS) to a production-grade architecture that prioritizes cost and accuracy:

1.  **Global Reasoning (English-First)**: The logic core of the agents (Analyst, Explainer, Validator) uses English prompts. This reduces token consumption by ~25% and improves compliance with original technical manuals (NIST/MITRE).
2.  **Universal Semantic Cache**: We implemented a cache layer that normalizes player intentions to English before matching. This allows a single AI response to serve players in Spanish, Portuguese, and English, drastically increasing the hit rate and reducing LLM costs.
3.  **Hybrid RAG with Translation Layer**: The system automatically translates technical player queries into English to search the highest-fidelity original sources, combining semantic search with exact matching of technical IDs (IPs, MITRE Tactics).
4.  **Adaptive Multilingual Delivery**: The **Explainer Agent** translates the technical analysis into pedagogical language in the user's preferred language (ES, PT, EN), adjusting the tone according to their experience level.

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
├── src/           # Python Backend (Multi-Agent System)
│   ├── agents/    # Agent logic (EN Prompts, Multilingual Output)
│   ├── orchest/   # Orchestrator (Pipeline with Observability and Cache)
│   ├── rag/       # Hybrid RAG (English-Targeted Search)
│   └── utils/     # Semantic Cache, LLMClient, Glossary
├── frontend/      # Next.js 14 Application (SOC Workstation)
│   ├── src/app/   # Workstation pages and layout
│   └── components/# Tactical UI components
├── data/
│   ├── docs/          # Official sources (EN/ES)
│   └── sample_scenarios/ # Standalone scenarios
└── scripts/           # Ingestion and simulation tools
```

## 🚀 Installation and Standalone Usage

```bash
# 1. Prepare environment
pip install -r requirements.txt
cp .env.example .env

# 2. Knowledge Ingestion (NIST/MITRE EN sources)
python scripts/download_sources.py
python 02-data-ingestion/ingest_docs.py

# 3. Run Demonstration
python scripts/verify_mixed_context.py
```

## 🧠 Professional Design Decisions

To ensure the project is easy to evaluate and scalable, the following strategic choices were made:

1.  **HuggingFace Spaces (Backend)**: Chosen as the hosting provider for the Python engine due to its **16GB RAM free tier**, which is necessary for the RAG index and local embedding models.
2.  **Next.js 14 (Frontend)**: Utilized the App Router for optimal performance. The decoupled architecture allows the frontend to run on Vercel with zero latency.
3.  **Framer Motion & Tailwind**: Selected to provide a **"Visceral Impact"** for the academic jury, ensuring the UI feels like a state-of-the-art SOC workstation rather than a simple chat bot.
4.  **"Manager of Drafts" UI**: The interface is designed as an **Advisor Sidebar**, promoting socratic learning where the AI evaluates and guides instead of just providing answers.

---
**Final Specialization Project - SOC Tutor RAG System**
*English Reasoning, LATAM Heart.*