# 📊 Reporte de Evaluación — SOC-Tutor-RAG

> **Generado:** 2026-04-09 16:09:25
> **Dataset:** `tests/eval_dataset.json` (7 casos)

---

## Resumen Ejecutivo

| Métrica | Valor | Estado |
|---------|-------|--------|
| Retrieval Success Rate | 100% | 🟢 |
| Scenario Relevance | 100% | 🟢 |
| Latencia RAG (promedio) | 960.7ms | 🟡 |
| Guardrails Accuracy | 100% | 🟢 |
| Guardrails TPR (ataques) | 100% | 🟢 |
| Validador Accuracy | 100% | 🟢 |
| Fallback Keys Coverage | ✅ PASS | 🟢 |
| Fallback Type Safety | ✅ PASS | 🟢 |
| Concept Precision (RAG) | 39% | 🔴 |

---

## 1. RAG Retrieval

Evalúa si el motor de búsqueda vectorial (ChromaDB) devuelve documentos relevantes para cada decisión del jugador.

| Caso | Docs | Latencia | Match Escenario |
|------|------|----------|-----------------|
| eval-001 | 5 | 6456.0ms | ✅ |
| eval-002 | 5 | 30.1ms | ✅ |
| eval-003 | 5 | 70.5ms | ✅ |
| eval-004 | 5 | 104.4ms | ✅ |
| eval-005 | 5 | 19.1ms | ✅ |
| eval-006 | 5 | 23.1ms | ✅ |
| eval-007 | 5 | 22.0ms | ✅ |

**Documentos en índice:** 56
**Escenarios únicos:** 7

---

## 2. Guardrails (Seguridad)

Evalúa la capacidad del `GuardAgent` de detectar ataques de prompt injection y permitir inputs legítimos.

| Métrica | Valor |
|---------|-------|
| True Positives (ataques bloqueados) | 6 |
| True Negatives (legítimos permitidos) | 4 |
| False Positives (legítimos bloqueados) | 0 |
| False Negatives (ataques no detectados) | 0 |

---

## 3. Agente Validador (QA Determinista)

Evalúa las reglas deterministas del `AgenteValidador` que detectan inconsistencias score↔tono sin necesidad de LLM.

- **Accuracy:** 100% (4/4)

---

## 4. Fallback Determinista (Resiliencia)

Verifica que el JSON de emergencia del `LLMClient` cubre todos los campos requeridos por los modelos Pydantic de los 3 agentes.

| Agente | Campos Cubiertos | Estado |
|--------|-----------------|--------|
| Analista (EvaluacionTecnica) | ✅ PASS | 🟢 |
| Explicador (FeedbackPedagogico) | ✅ PASS | 🟢 |
| Validador (ValidacionCalidad) | ✅ PASS | 🟢 |

---

## 5. Cobertura Conceptual

Mide qué porcentaje de los conceptos técnicos esperados aparecen en el contexto RAG recuperado.

| Caso | Precision | Encontrados | Esperados |
|------|-----------|-------------|-----------|
| eval-001 | 0% | [] | ['contención', 'firewall', 'IOC', 'bloqueo'] |
| eval-002 | 25% | ['ransomware'] | ['aislar', 'impacto', 'crítico', 'ransomware'] |
| eval-003 | 50% | ['evidencia', 'forense'] | ['cadena de custodia', 'preservación', 'evidencia', 'forense'] |
| eval-004 | 50% | ['lateral', 'APT'] | ['segmentación', 'lateral', 'contención', 'APT'] |
| eval-005 | 50% | ['notificación', 'datos'] | ['notificación', 'datos', 'regulación', 'breach'] |
| eval-006 | 75% | ['evidencia', 'error', 'logs'] | ['preservar', 'evidencia', 'error', 'logs'] |
| eval-007 | 25% | ['MFA'] | ['MFA', 'credenciales', 'autenticación', 'erradicación'] |

---

## Notas Técnicas

- Las métricas RAG se ejecutan sobre el índice ChromaDB local (`data/indices/`).
- Los guardrails se evalúan con inputs sintéticos adversariales y legítimos.
- El validador se evalúa solo con reglas deterministas (sin llamada LLM).
- El fallback se evalúa forzando un error de conexión en `LLMClient`.
- La cobertura conceptual mide presencia de keywords en el contexto RAG, no semántica profunda.
