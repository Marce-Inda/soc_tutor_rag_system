# 📊 Evaluation Report — SOC-Tutor-RAG

> **Generated:** 2026-04-09 16:09:25
> **Dataset:** `tests/eval_dataset.json` (7 cases)

---

## Executive Summary

| Metric | Value | Status |
|---------|-------|--------|
| Retrieval Success Rate | 100% | 🟢 |
| Scenario Relevance | 100% | 🟢 |
| RAG Latency (average) | 960.7ms | 🟡 |
| Guardrails Accuracy | 100% | 🟢 |
| Guardrails TPR (attacks) | 100% | 🟢 |
| Validator Accuracy | 100% | 🟢 |

| Fallback Keys Coverage | ✅ PASS | 🟢 |
| Fallback Type Safety | ✅ PASS | 🟢 |
| Concept Precision (RAG) | 39% | 🔴 |

---

## 1. RAG Retrieval

Evaluates whether the vector search engine (ChromaDB) returns relevant documents for each player decision.

| Case | Docs | Latency | Scenario Match |
|------|------|----------|-----------------|
| eval-001 | 5 | 6456.0ms | ✅ |
| eval-002 | 5 | 30.1ms | ✅ |
| eval-003 | 5 | 70.5ms | ✅ |
| eval-004 | 5 | 104.4ms | ✅ |
| eval-005 | 5 | 19.1ms | ✅ |
| eval-006 | 5 | 23.1ms | ✅ |
| eval-007 | 5 | 22.0ms | ✅ |

**Documents in index:** 56
**Unique scenarios:** 7

---

## 2. Guardrails (Security)

Evaluates the `GuardAgent`'s ability to detect prompt injection attacks and allow legitimate inputs.

| Metric | Value |
|---------|-------|
| True Positives (blocked attacks) | 6 |
| True Negatives (legitimate allowed) | 4 |
| False Positives (legitimate blocked) | 0 |
| False Negatives (undetected attacks) | 0 |

---

## 3. Validator Agent (Deterministic QA)

Evaluates the deterministic rules of the `ValidatorAgent` that detect score↔tone inconsistencies without needing an LLM call.

- **Accuracy:** 100% (4/4)

---

## 4. Deterministic Fallback (Resilience)

Verifies that the `LLMClient` emergency JSON covers all fields required by the Pydantic models of the 3 agents.

| Agent | Fields Covered | Status |
|--------|-----------------|--------|
| Analyst (EvaluacionTecnica) | ✅ PASS | 🟢 |
| Explainer (FeedbackPedagogico) | ✅ PASS | 🟢 |
| Validator (ValidacionCalidad) | ✅ PASS | 🟢 |

---

## 5. Conceptual Coverage

Measures the percentage of expected technical concepts that appear in the retrieved RAG context.

| Case | Precision | Found | Expected |
|------|-----------|-------------|-----------|
| eval-001 | 0% | [] | ['containment', 'firewall', 'IOC', 'blocking'] |
| eval-002 | 25% | ['ransomware'] | ['isolate', 'impact', 'critical', 'ransomware'] |
| eval-003 | 50% | ['evidence', 'forensic'] | ['chain of custody', 'preservation', 'evidence', 'forensic'] |
| eval-004 | 50% | ['lateral', 'APT'] | ['segmentation', 'lateral', 'containment', 'APT'] |
| eval-005 | 50% | ['notification', 'data'] | ['notification', 'data', 'regulation', 'breach'] |
| eval-006 | 75% | ['evidence', 'error', 'logs'] | ['preserve', 'evidence', 'error', 'logs'] |
| eval-007 | 25% | ['MFA'] | ['MFA', 'credentials', 'authentication', 'eradication'] |

---

## Technical Notes

- RAG metrics are executed on the local ChromaDB index (`data/indices/`).
- Guardrails are evaluated with adversarial and legitimate synthetic inputs.
- The validator is evaluated only with deterministic rules (no LLM call).
- Fallback is evaluated by forcing a connection error in `LLMClient`.
- Conceptual coverage measures the presence of keywords in the RAG context, not deep semantics.
