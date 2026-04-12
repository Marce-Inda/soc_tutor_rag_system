# MASTER DOCUMENT - SOC-Tutor-RAG

## 1. Project Vision
Develop a RAG-based pedagogical feedback system that assists SOC analysts in training, using official technical documentation as the ground truth.

## 2. Component Architecture
- **Module 1: RAG Engine**: Ingestion and vector search over NIST, MITRE, and OWASP documentation.
- **Module 2: Specialized Agents**: 
    - `Analyst`: Technical evaluation (ReAct).
    - `Explainer`: Adaptive pedagogical feedback.
    - `Validator`: Quality control and hallucination prevention.
    - `Governance`: Legal compliance and ethical evaluation.
- **Module 3: Orchestration**: Coordination of the flow and memory persistence.
- **Module 4: Observability**: Tracing of metrics, costs, and reasoning chains.

## 3. Production Standards
- **Typing**: Strict use of Pydantic models.
- **Testing**: Target >70% coverage in agent logic.
- **Deployment**: Full Dockerization.
- **Security**: Dynamic guardrails (GuardAgent) and prompt defense.

## 4. Roadmap v1.1
- [ ] Integration with Web Dashboard.
- [ ] Support for dynamic multi-language (PT expansion).
- [ ] Automatic evaluation with RAGAS.
- [ ] Hybrid Deployment: Web interfaces (Streamlit/Gradio) for non-technical evaluators and simple Docker.
