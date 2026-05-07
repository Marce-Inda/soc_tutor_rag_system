# 📊 Evaluación del Sistema Multiagente — SOC-Tutor-RAG

> **Generado:** 2026-05-06 23:34:59
> **Provider LLM:** gemini / None
> **Dataset:** `tests/eval_dataset.json` (2 casos × 2 perfiles = 4 ejecuciones)

---

## Resumen Ejecutivo

| # | Métrica | Valor | Estado |
|---|---------|-------|--------|
| 1 | Pipeline Completeness | 100% | 🟢 |
| 2 | Structural Validity | 100% | 🟢 |
| 2 | Semantic Coverage (Keywords) | 0% | 🔴 |
| 3 | Tool Consistency (Tool Match) | 0% | 🔴 |
| 3 | Score Discrimination | Gap: 0.0 pts | 🔴 |
| 4 | Faithfulness (cita fuentes) | 100% | 🟢 |
| 5 | Pedagogical Adaptation | 0% | 🔴 |
| 6 | Validator Approval Rate | 0% | 🔴 |
|   | **Latencia promedio** | **74.66s** | 🔴 |

---

## 1. Nivel de Contratos (Estructura)

Verifica que cada agente produce outputs conformes a sus modelos Pydantic (`EvaluacionTecnica`, `FeedbackPedagogico`, `ValidacionCalidad`).

- **Structural Validity (Overall):** 100%
- **Compliance Pydantic:** 100% (Analista), 100% (Explicador)

---

## 2. Nivel Golden Tests (Sustancia Semántica)

¿La respuesta del agente contiene los términos técnicos obligatorios?

- **Semantic Coverage:** 0%
- **Keywords encontradas:** 0/16

---

## 3. Nivel de Trazas (Lógica y Comportamiento)

¿El agente utilizó las herramientas correctas y discrimina la calidad?

- **Tool Consistency Match:** 0%
- **Score Discrimination Gap:** 0.0 puntos
- **¿Discrimina buenas/malas?** ❌ No

| Tipo | Score Promedio | Scores Individuales |
|------|---------------|---------------------|
| Decisiones Buenas | 0.0 | [0, 0] |
| Decisiones Malas | 0.0 | [0, 0] |

- **Gap:** 0.0 puntos
- **¿Discrimina?** ❌ No

---

## 4. Faithfulness (Citación de Fuentes RAG)

¿El feedback final cita fuentes de la base de conocimiento?

- **Tasa de citación:** 100%
- **Fuentes promedio por respuesta:** 1.0

---

## 5. Pedagogical Adaptation

¿El Explicador adapta el lenguaje al nivel del jugador (Junior vs Senior)?

- **Tasa de adaptación:** 0% (0/2 casos)

---

## 6. Validator Effectiveness

¿El Agente Validador aprueba/rechaza coherentemente?

| Estado | Cantidad |
|--------|----------|
| Aprobados | 0 |
| Rechazados | 4 |
| Con inconsistencias | 4 |

---

## Notas Técnicas

- Evaluación ejecutada con **gemini** modelo **None** (para validar flujo).
- Se usaron 2 perfiles de jugador (Junior y Senior) por caso para medir adaptación pedagógica.
- Los resultados de calidad del LLM dependen del modelo; estas métricas evalúan el **sistema multiagente**, no el modelo.
- Para resultados de producción, re-ejecutar con `--provider gemini --model gemini-2.5-flash`.
