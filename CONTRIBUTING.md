# Contributing to SOC Tutor 🛠️🏛️

Welcome to the **SOC Tutor** project! To maintain the high professional standard and architectural consistency of this repository, we follow specific guidelines regarding naming, language, and coding style.

## 1. Naming Strategy (English-First)

All structural and technical elements MUST use **English**. This ensures compatibility with global tooling and provides a professional appearance on GitHub.

-   **Folders**: Use the `NN-name-description` format in lowercase (e.g., `02-data-ingestion`, `src/agents`).
-   **Filenames**: Use `snake_case` in English (e.g., `analyst_agent.py`, `rag_client.py`).
-   **Class Names**: Use `PascalCase` in English (e.g., `AnalystAgent`, `UEFSOrchestrator`).
-   **Variables & Functions**: Use `snake_case` in English (e.g., `generate_feedback`, `technical_score`).

## 2. Hybrid Language Policy

We implement a unique strategy called **"English-First Reasoning / Multilingual Delivery"**.

### 💻 For the AI / System
-   **Prompts**: Must be in **English**. This reduces token consumption (~25%) and improves technical adherence to international frameworks (NIST, MITRE).
-   **Internal Reasoning**: Agents should perform thoughts and technical analysis in **English** before the final translation.
-   **Internal Documentation**: Technical docstrings (PEP 257) must be in **English**.
-   **Data Types**: Pydantic models and field descriptions must be in **English**.

### 👨‍🏫 For Human Accessibility (LATAM Focus)
-   **Pedagogical Headers**: Every major logical block, class, or complex function should start with a Spanish header using the double hash `# ##` or triple hash `# ###` format.
    -   *Example*: `# ## AGENTE ANALISTA - Evaluación Técnica (ReAct)`
-   **Comments**: Contextual comments that explain the "how" and "why" from a pedagogical perspective should be in **Spanish**.

## 3. Engineering Standards

-   **Type Safety**: Use Pydantic for all data schemas (see `src/agents/types.py`).
-   **Resilience**: Use the `tenacity` library for LLM retries and provide clear fallback mechanisms.
-   **Observability**: All agent interactions must be logged via the internal `tracer` utility.
-   **Testing**: New logic should include matching tests in the `tests/` directory.

## 4. Documentation

-   **README.md**: Main project overview in **English**.
-   **README_ES.md**: Full accessibility version in **Spanish**.
-   **Technical Docs**: Stored in `docs/` in English. Spanish versions should be suffixed with `_ES.md`.

---
Following these guidelines ensures that SOC Tutor remains a world-class educational tool for the cybersecurity community. Thank you for your contributions!
