# 📊 Evaluación del Sistema Multiagente — SOC-Tutor-RAG

> **Generado:** 2026-04-19 18:29:37
> **Provider LLM:** gemini / gemini-2.0-flash
> **Dataset:** `tests/eval_dataset.json` (7 casos × 2 perfiles = 14 ejecuciones)

---

## Resumen Ejecutivo

| # | Métrica | Valor | Estado |
|---|---------|-------|--------|
| 1 | Pipeline Completeness | 86% | 🟢 |
| 2 | Structural Validity (Analista) | 100% | 🟢 |
| 2 | Structural Validity (Explicador) | 100% | 🟢 |
| 2 | Structural Validity (Validador) | 100% | 🟢 |
| 3 | Score Discrimination | Gap: 35.0 pts | 🟢 |
| 4 | Faithfulness (cita fuentes) | 83% | 🟢 |
| 5 | Pedagogical Adaptation | 0% | 🔴 |
| 6 | Validator Approval Rate | 0% | 🔴 |
|   | **Latencia promedio** | **279.04s** | 🔴 |

---

## 1. Pipeline Completeness

Ejecuta el flujo completo del orquestador: `Guard → Memory → RAG → Analista (ReAct) → Explicador → Validador → FeedbackFinal`.

- **Success Rate:** 86% (12/14)
- **Latencia promedio:** 279.04s por ejecución

---

## 2. Structural Validity

Verifica que cada agente produce outputs conformes a sus modelos Pydantic (`EvaluacionTecnica`, `FeedbackPedagogico`, `ValidacionCalidad`).

| Modelo Pydantic | Compliance |
|----------------|------------|
| EvaluacionTecnica (Analista) | 100% |
| FeedbackPedagogico (Explicador) | 100% |
| ValidacionCalidad (Validador) | 100% |
| FeedbackFinal (Orquestador) | 100% |

---

## 3. Score Discrimination

¿El Analista diferencia buenas de malas decisiones?

| Tipo | Score Promedio | Scores Individuales |
|------|---------------|---------------------|
| Decisiones Buenas | 75.0 | [80, 80, 60, 60, 80, 80, 80, 80] |
| Decisiones Malas | 40.0 | [80, 80, 0, 0] |

- **Gap:** 35.0 puntos
- **¿Discrimina?** ✅ Sí

---

## 4. Faithfulness (Citación de Fuentes RAG)

¿El feedback final cita fuentes de la base de conocimiento?

- **Tasa de citación:** 83%
- **Fuentes promedio por respuesta:** 1.0

---

## 5. Pedagogical Adaptation

¿El Explicador adapta el lenguaje al nivel del jugador (Junior vs Senior)?

- **Tasa de adaptación:** 0% (0/6 casos)

---

## 6. Validator Effectiveness

¿El Agente Validador aprueba/rechaza coherentemente?

| Estado | Cantidad |
|--------|----------|
| Aprobados | 0 |
| Rechazados | 12 |
| Con inconsistencias | 12 |

---

## Notas Técnicas

- Evaluación ejecutada con **gemini** modelo **gemini-2.0-flash** (para validar flujo).
- Se usaron 2 perfiles de jugador (Junior y Senior) por caso para medir adaptación pedagógica.
- Los resultados de calidad del LLM dependen del modelo; estas métricas evalúan el **sistema multiagente**, no el modelo.
- Para resultados de producción, re-ejecutar con `--provider gemini --model gemini-2.5-flash`.
