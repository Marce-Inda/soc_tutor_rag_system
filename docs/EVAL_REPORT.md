# 📊 Evaluación del Sistema Multiagente — SOC-Tutor-RAG

> **Generado:** 2026-05-03 15:05:53
> **Provider LLM:** gemini / None
> **Dataset:** `tests/eval_dataset.json` (1 casos × 2 perfiles = 2 ejecuciones)

---

## Resumen Ejecutivo

| # | Métrica | Valor | Estado |
|---|---------|-------|--------|
| 1 | Pipeline Completeness | 0% | 🔴 |
| 2 | Structural Validity (Analista) | 0% | 🔴 |
| 2 | Structural Validity (Explicador) | 0% | 🔴 |
| 2 | Structural Validity (Validador) | 0% | 🔴 |
| 3 | Score Discrimination | Gap: 0 pts | 🔴 |
| 4 | Faithfulness (cita fuentes) | 0% | 🔴 |
| 5 | Pedagogical Adaptation | 0% | 🔴 |
| 6 | Validator Approval Rate | 0% | 🔴 |
|   | **Latencia promedio** | **118.47s** | 🔴 |

---

## 1. Pipeline Completeness

Ejecuta el flujo completo del orquestador: `Guard → Memory → RAG → Analista (ReAct) → Explicador → Validador → FeedbackFinal`.

- **Success Rate:** 0% (0/2)
- **Latencia promedio:** 118.47s por ejecución

---

## 2. Structural Validity

Verifica que cada agente produce outputs conformes a sus modelos Pydantic (`EvaluacionTecnica`, `FeedbackPedagogico`, `ValidacionCalidad`).

| Modelo Pydantic | Compliance |
|----------------|------------|
| EvaluacionTecnica (Analista) | 0% |
| FeedbackPedagogico (Explicador) | 0% |
| ValidacionCalidad (Validador) | 0% |
| FeedbackFinal (Orquestador) | 0% |

---

## 3. Score Discrimination

¿El Analista diferencia buenas de malas decisiones?

| Tipo | Score Promedio | Scores Individuales |
|------|---------------|---------------------|
| Decisiones Buenas | 0 | [] |
| Decisiones Malas | 0 | [] |

- **Gap:** 0 puntos
- **¿Discrimina?** ❌ No

---

## 4. Faithfulness (Citación de Fuentes RAG)

¿El feedback final cita fuentes de la base de conocimiento?

- **Tasa de citación:** 0%
- **Fuentes promedio por respuesta:** 0

---

## 5. Pedagogical Adaptation

¿El Explicador adapta el lenguaje al nivel del jugador (Junior vs Senior)?

- **Tasa de adaptación:** 0% (0/0 casos)

---

## 6. Validator Effectiveness

¿El Agente Validador aprueba/rechaza coherentemente?

| Estado | Cantidad |
|--------|----------|
| Aprobados | 0 |
| Rechazados | 0 |
| Con inconsistencias | 0 |

---

## Notas Técnicas

- Evaluación ejecutada con **gemini** modelo **None** (para validar flujo).
- Se usaron 2 perfiles de jugador (Junior y Senior) por caso para medir adaptación pedagógica.
- Los resultados de calidad del LLM dependen del modelo; estas métricas evalúan el **sistema multiagente**, no el modelo.
- Para resultados de producción, re-ejecutar con `--provider gemini --model gemini-2.5-flash`.
