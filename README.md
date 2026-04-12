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

-   **Models**: Google `gemini-2.0-flash` (via a unified LLMClient with support for Groq and Ollama).
-   **Vector DB**: ChromaDB (local and embedded).
-   **Embeddings**: `all-MiniLM-L6-v2` (100% local execution).
-   **Orchestration**: Deterministic sequential flow (Security Guard -> Memory -> RAG -> Analyst -> Explainer -> Validator).
-   **Frameworks**: LangChain, Pydantic, Tenacity (Resilience).

## 📊 Knowledge Sources (RAG)

The system is founded on official and updated technical documentation:
-   **MITRE ATT&CK v18.1**: Native catalog of adversary tactics and techniques.
-   **NIST 800-61 Rev. 2**: Computer Security Incident Handling Guide.
-   **CISA / OWASP**: Reference frameworks for remediation and vulnerabilities.

## 📂 Project Structure

```
soc-tutor-rag-system/
├── src/
│   ├── agents/        # Agent logic (EN Prompts, Multilingual Output)
│   ├── orchest/       # Orchestrator (Pipeline with Observability and Cache)
│   ├── rag/           # Hybrid RAG (English-Targeted Search)
│   └── utils/         # Semantic Cache, LLMClient, Glossary
├── data/
│   ├── docs/          # Official sources (EN/ES)
│   └── sample_scenarios/ # Standalone scenarios (e.g., ar-fintech-idor)
└── scripts/           # Ingestion and validation tools
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

## 🧠 "Cloud-Lite" Design Decisions

To ensure the project is easy to evaluate and scalable, heavy proprietary cloud dependencies were removed, allowing the system to run with minimal latency and zero cost under the Gemini 2.0 free tier. The "Standalone" design allows validating the feedback engine independently with high-fidelity synthetic data.

---
**Final Specialization Project - SOC Tutor RAG System**
*English Reasoning, LATAM Heart.*