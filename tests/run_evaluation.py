"""
Evaluación End-to-End del Sistema Multiagente SOC-Tutor-RAG.
Ejecuta el pipeline completo (Orquestador → Analista → Explicador → Validador)
y mide métricas reales sobre el comportamiento del sistema.

Uso:
    PYTHONPATH=. .venv/bin/python tests/run_evaluation.py [--provider ollama] [--model llama3.2] [--cases N]
"""

import json
import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from src.agents.types import (
    Decision, ContextoEscenario, PlayerProfile,
    FeedbackFinal, EvaluacionTecnica, FeedbackPedagogico, ValidacionCalidad
)
from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.rag.rag_client import create_rag_client
from src.utils.llm_client import create_llm_client, LLMClient
from src.agents.guard_agent import GuardAgent


# ============================================================================
# MÉTRICA 1: Pipeline Completeness (¿El flujo multiagente completa sin error?)
# ============================================================================

async def eval_pipeline_completeness(orchestrator, test_cases, profiles) -> Dict[str, Any]:
    """
    Ejecuta el orquestador completo caso por caso asíncronamente.
    """
    print("\n" + "=" * 60)
    print("MÉTRICA 1: PIPELINE COMPLETENESS (End-to-End)")
    print("=" * 60)

    results = []
    success = 0

    for case in test_cases:
        case_id = case["id"]
        print(f"\n  [{case_id}] {case.get('titulo', '')}...")

        decision = Decision(
            accion=case["decision"]["accion"],
            target=case["decision"]["target"],
            detalle=case["decision"].get("detalle")
        )
        contexto = ContextoEscenario(
            tipo_incidente=case["contexto"]["tipo_incidente"],
            fase=case["contexto"]["fase"],
            scenario_id=case["contexto"].get("scenario_id")
        )

        for profile in profiles:
            label = f"Lvl{profile.level}-{profile.rol}"
            start = time.perf_counter()
            try:
                feedback = await orchestrator.generar_feedback(decision, contexto, profile)
                latency = time.perf_counter() - start

                results.append({
                    "case_id": case_id,
                    "profile": label,
                    "success": True,
                    "latency_sec": round(latency, 2),
                    "feedback": feedback,
                    "decision_quality": case.get("decision_quality", "unknown"),
                    "min_score": case.get("min_score", 50),
                    "expected_concepts": case.get("expected_concepts", [])
                })
                success += 1
                print(f"    ✅ [{label}] OK en {latency:.1f}s | Score: {feedback.evaluacion_tecnica.technical_score}")

            except Exception as e:
                import traceback
                print(f"Error en evaluación: {traceback.format_exc()}")
                latency = time.perf_counter() - start
                results.append({
                    "case_id": case_id,
                    "profile": label,
                    "success": False,
                    "latency_sec": round(latency, 2),
                    "error": str(e)
                })
                print(f"    ❌ [{label}] ERROR en {latency:.1f}s: {e}")

    total = len(results)
    avg_latency = sum(r["latency_sec"] for r in results) / total if total else 0

    metrics = {
        "success_rate": success / total if total else 0,
        "total_runs": total,
        "successful_runs": success,
        "avg_latency_sec": round(avg_latency, 2),
        "results": results
    }

    print(f"\n  📊 Pipeline Success Rate: {metrics['success_rate']:.0%} ({success}/{total})")
    print(f"  📊 Latencia Promedio:     {avg_latency:.1f}s")
    return metrics


# ============================================================================
# MÉTRICA 2: Structural Validity (¿Los agents producen outputs Pydantic válidos?)
# ============================================================================

def eval_structural_validity(pipeline_results: list) -> Dict[str, Any]:
    """
    Verifica que cada agente produjo outputs con la estructura correcta
    según los modelos Pydantic definidos en types.py.
    """
    print("\n" + "=" * 60)
    print("MÉTRICA 2: STRUCTURAL VALIDITY (Pydantic Compliance)")
    print("=" * 60)

    checks = {
        "evaluacion_tecnica_valid": 0,
        "feedback_pedagogico_valid": 0,
        "validacion_calidad_valid": 0,
        "feedback_final_valid": 0,
    }
    total = 0

    for r in pipeline_results:
        if not r["success"]:
            continue
        total += 1
        fb: FeedbackFinal = r["feedback"]

        # EvaluacionTecnica
        et = fb.evaluacion_tecnica
        if (isinstance(et.technical_score, int) and
            isinstance(et.analysis, str) and len(et.analysis) > 0 and
            isinstance(et.explanation, str) and len(et.explanation) > 0):
            checks["evaluacion_tecnica_valid"] += 1

        # FeedbackPedagogico (dentro de FeedbackFinal)
        if (isinstance(fb.evaluacion, str) and len(fb.evaluacion) > 0 and
            isinstance(fb.explicacion, str) and len(fb.explicacion) > 0 and
            isinstance(fb.mejor_practica, str) and len(fb.mejor_practica) > 0):
            checks["feedback_pedagogico_valid"] += 1

        # ValidacionCalidad
        v = fb.validacion
        if (isinstance(v.approved, bool) and
            isinstance(v.inconsistencies, list) and
            isinstance(v.quality_score, str)):
            checks["validacion_calidad_valid"] += 1

        # FeedbackFinal completo
        if (isinstance(fb.fuentes_citadas, list) and
            isinstance(fb.costo_estimado, float)):
            checks["feedback_final_valid"] += 1

    metrics = {}
    for key, count in checks.items():
        rate = count / total if total else 0
        metrics[key] = rate
        status = "✅" if rate >= 0.8 else "⚠️" if rate >= 0.5 else "❌"
        print(f"  {status} {key}: {rate:.0%} ({count}/{total})")

    metrics["total_checked"] = total
    return metrics


# ============================================================================
# MÉTRICA 3: Score Discrimination (¿El sistema diferencia buenas de malas decisiones?)
# ============================================================================

def eval_score_discrimination(pipeline_results: list) -> Dict[str, Any]:
    """
    Compara los scores técnicos asignados a decisiones 'buenas' vs 'malas'.
    Un buen sistema multiagente DEBE dar scores más altos a decisiones correctas.
    """
    print("\n" + "=" * 60)
    print("MÉTRICA 3: SCORE DISCRIMINATION (Buenas vs Malas)")
    print("=" * 60)

    good_scores = []
    bad_scores = []

    for r in pipeline_results:
        if not r["success"]:
            continue
        score = r["feedback"].evaluacion_tecnica.technical_score
        quality = r["decision_quality"]

        if quality == "buena":
            good_scores.append(score)
        elif quality == "mala":
            bad_scores.append(score)

    avg_good = sum(good_scores) / len(good_scores) if good_scores else 0
    avg_bad = sum(bad_scores) / len(bad_scores) if bad_scores else 0
    discriminates = avg_good > avg_bad

    print(f"  Decisiones BUENAS: scores = {good_scores}")
    print(f"    → Promedio: {avg_good:.0f}")
    print(f"  Decisiones MALAS:  scores = {bad_scores}")
    print(f"    → Promedio: {avg_bad:.0f}")
    print(f"  {'✅' if discriminates else '❌'} ¿Discrimina? avg_buenas({avg_good:.0f}) > avg_malas({avg_bad:.0f}): {discriminates}")

    metrics = {
        "avg_good_score": round(avg_good, 1),
        "avg_bad_score": round(avg_bad, 1),
        "discriminates": discriminates,
        "score_gap": round(avg_good - avg_bad, 1),
        "good_scores": good_scores,
        "bad_scores": bad_scores
    }
    return metrics


# ============================================================================
# MÉTRICA 4: Faithfulness / Source Grounding (¿Cita fuentes RAG?)
# ============================================================================

def eval_faithfulness(pipeline_results: list) -> Dict[str, Any]:
    """
    Verifica que el feedback final cite fuentes del RAG.
    Un sistema multiagente con RAG DEBE fundamentar sus respuestas.
    """
    print("\n" + "=" * 60)
    print("MÉTRICA 4: FAITHFULNESS (Citación de Fuentes)")
    print("=" * 60)

    has_sources = 0
    total = 0
    source_counts = []

    for r in pipeline_results:
        if not r["success"]:
            continue
        total += 1
        fuentes = r["feedback"].fuentes_citadas
        n = len(fuentes)
        source_counts.append(n)
        if n > 0:
            has_sources += 1
            print(f"  ✅ [{r['case_id']}-{r['profile']}] {n} fuentes: {fuentes[:3]}...")
        else:
            print(f"  ❌ [{r['case_id']}-{r['profile']}] Sin fuentes citadas")

    rate = has_sources / total if total else 0
    avg_sources = sum(source_counts) / total if total else 0

    metrics = {
        "faithfulness_rate": round(rate, 3),
        "avg_sources_per_response": round(avg_sources, 1),
        "total_checked": total
    }
    print(f"\n  📊 Faithfulness Rate:      {rate:.0%}")
    print(f"  📊 Fuentes promedio/resp:  {avg_sources:.1f}")
    return metrics


# ============================================================================
# MÉTRICA 2b: Semantic Coverage (Keyword Match)
# ============================================================================

def eval_semantic_coverage(pipeline_results: list) -> Dict[str, Any]:
    """
    Verifica que la respuesta contenga los conceptos técnicos esperados (expected_concepts).
    Nivel 2 de la checklist profesional.
    """
    print("\n" + "=" * 60)
    print("MÉTRICA 2b: SEMANTIC COVERAGE (Keyword Match)")
    print("=" * 60)

    total_matches = 0
    total_expected = 0
    case_coverage = []

    for r in pipeline_results:
        if not r["success"]:
            continue
        expected = r.get("expected_concepts", [])
        if not expected:
            continue
        
        # Combinar análisis y explicación para buscar keywords
        full_text = (r["feedback"].evaluacion_tecnica.analysis + " " + 
                     r["feedback"].evaluacion_tecnica.explanation).lower()
        
        found = [kw for kw in expected if kw.lower() in full_text]
        score = len(found) / len(expected) if expected else 0
        
        total_matches += len(found)
        total_expected += len(expected)
        case_coverage.append(score)
        
        status = "✅" if score >= 0.7 else "⚠️" if score >= 0.4 else "❌"
        print(f"  {status} [{r['case_id']}] Found {len(found)}/{len(expected)}: {found}")

    avg_coverage = sum(case_coverage) / len(case_coverage) if case_coverage else 0
    metrics = {
        "avg_semantic_coverage": round(avg_coverage, 3),
        "total_keywords_found": total_matches,
        "total_keywords_expected": total_expected
    }
    print(f"\n  📊 Semantic Coverage: {avg_coverage:.0%}")
    return metrics


# ============================================================================
# MÉTRICA 3b: Tool Consistency (Tool Match)
# ============================================================================

def eval_tool_consistency(pipeline_results: list) -> Dict[str, Any]:
    """
    Verifica que el agente haya invocado las herramientas esperadas (expected_tools).
    Nivel 3 de la checklist profesional.
    """
    print("\n" + "=" * 60)
    print("MÉTRICA 3b: TOOL CONSISTENCY (Tool Match)")
    print("=" * 60)

    total_matches = 0
    total_expected = 0
    case_match = []

    for r in pipeline_results:
        if not r["success"]:
            continue
        expected = r.get("expected_tools", [])
        if not expected:
            continue
        
        # Extraer herramientas usadas de technical_data
        tech_data = r["feedback"].evaluacion_tecnica.technical_data or []
        analysis = r["feedback"].evaluacion_tecnica.analysis.lower()
        
        found = []
        for tool in expected:
            if tool in ["telemetry_mcp_client", "edr_mcp_client"] and tech_data:
                found.append(tool)
            elif tool.lower() in analysis:
                found.append(tool)
        
        score = len(found) / len(expected) if expected else 0
        total_matches += len(found)
        total_expected += len(expected)
        case_match.append(score)
        
        status = "✅" if score >= 0.5 else "❌"
        print(f"  {status} [{r['case_id']}] Tools matched {len(found)}/{len(expected)}: {found}")

    avg_match = sum(case_match) / len(case_match) if case_match else 0
    metrics = {
        "avg_tool_match": round(avg_match, 3),
        "total_tools_matched": total_matches,
        "total_tools_expected": total_expected
    }
    print(f"\n  📊 Tool Consistency Match: {avg_match:.0%}")
    return metrics


# ============================================================================
# MÉTRICA 5: Pedagogical Adaptation (¿Cambia el tono según nivel?)
# ============================================================================

def eval_pedagogical_adaptation(pipeline_results: list) -> Dict[str, Any]:
    """
    Compara las respuestas del Explicador para el MISMO caso pero con diferentes perfiles.
    El sistema debe adaptar el lenguaje y tono según el nivel del jugador.
    """
    print("\n" + "=" * 60)
    print("MÉTRICA 5: PEDAGOGICAL ADAPTATION (Adaptación por Nivel)")
    print("=" * 60)

    # Agrupar respuestas por case_id
    by_case = {}
    for r in pipeline_results:
        if not r["success"]:
            continue
        cid = r["case_id"]
        if cid not in by_case:
            by_case[cid] = []
        by_case[cid].append(r)

    adaptations = 0
    total_cases = 0

    for cid, runs in by_case.items():
        if len(runs) < 2:
            continue
        total_cases += 1

        # Comparar las explicaciones entre niveles
        texts = {r["profile"]: r["feedback"].explicacion for r in runs}

        # Si hay al menos 2 perfiles con texto diferente, consideramos que adaptó
        unique_texts = set(texts.values())
        adapted = len(unique_texts) > 1

        if adapted:
            adaptations += 1
            print(f"  ✅ [{cid}] Textos diferentes entre perfiles")
            for prof, text in texts.items():
                print(f"      {prof}: \"{text[:80]}...\"")
        else:
            print(f"  ❌ [{cid}] Mismo texto para todos los perfiles")

    rate = adaptations / total_cases if total_cases else 0
    metrics = {
        "adaptation_rate": round(rate, 3),
        "adapted_cases": adaptations,
        "total_comparable_cases": total_cases
    }
    print(f"\n  📊 Adaptation Rate: {rate:.0%} ({adaptations}/{total_cases})")
    return metrics


# ============================================================================
# MÉTRICA 6: Validator Effectiveness (¿El Validador realmente valida?)
# ============================================================================

def eval_validator_effectiveness(pipeline_results: list) -> Dict[str, Any]:
    """
    Analiza las decisiones del Validador:
    - ¿Aprueba/rechaza de forma coherente?
    - ¿Detecta inconsistencias cuando las hay?
    """
    print("\n" + "=" * 60)
    print("MÉTRICA 6: VALIDATOR EFFECTIVENESS")
    print("=" * 60)

    approved = 0
    rejected = 0
    with_inconsistencies = 0
    total = 0

    for r in pipeline_results:
        if not r["success"]:
            continue
        total += 1
        v = r["feedback"].validacion

        if v.approved:
            approved += 1
        else:
            rejected += 1

        if v.inconsistencies:
            with_inconsistencies += 1
            print(f"  ⚠️  [{r['case_id']}-{r['profile']}] Inconsistencias: {v.inconsistencies}")
        else:
            print(f"  ✅ [{r['case_id']}-{r['profile']}] Aprobado: {v.quality_score[:60]}...")

    approval_rate = approved / total if total else 0
    metrics = {
        "approval_rate": round(approval_rate, 3),
        "approved": approved,
        "rejected": rejected,
        "with_inconsistencies": with_inconsistencies,
        "total": total
    }
    print(f"\n  📊 Approval Rate:         {approval_rate:.0%}")
    print(f"  📊 Con Inconsistencias:   {with_inconsistencies}/{total}")
    return metrics


# ============================================================================
# REPORTE MARKDOWN
# ============================================================================

def generate_report(all_metrics: Dict[str, Any], output_path: str):
    """Genera el reporte Markdown consolidado."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    m = all_metrics

    def sem(val, good=0.8, warn=0.5):
        if val >= good: return "🟢"
        if val >= warn: return "🟡"
        return "🔴"

    report = f"""# 📊 Evaluación del Sistema Multiagente — SOC-Tutor-RAG

> **Generado:** {timestamp}
> **Provider LLM:** {m.get('provider', '?')} / {m.get('model', '?')}
> **Dataset:** `tests/eval_dataset.json` ({m.get('num_cases', '?')} casos × {m.get('num_profiles', '?')} perfiles = {m['pipeline']['total_runs']} ejecuciones)

---

## Resumen Ejecutivo

| # | Métrica | Valor | Estado |
|---|---------|-------|--------|
| 1 | Pipeline Completeness | {m['pipeline']['success_rate']:.0%} | {sem(m['pipeline']['success_rate'])} |
| 2 | Structural Validity | {m['structure'].get('evaluacion_tecnica_valid', 0):.0%} | {sem(m['structure'].get('evaluacion_tecnica_valid', 0))} |
| 2 | Semantic Coverage (Keywords) | {m['semantic'].get('avg_semantic_coverage', 0):.0%} | {sem(m['semantic'].get('avg_semantic_coverage', 0), good=0.7)} |
| 3 | Tool Consistency (Tool Match) | {m['tools'].get('avg_tool_match', 0):.0%} | {sem(m['tools'].get('avg_tool_match', 0), good=0.5)} |
| 3 | Score Discrimination | Gap: {m['discrimination']['score_gap']} pts | {sem(1 if m['discrimination']['discriminates'] else 0)} |
| 4 | Faithfulness (cita fuentes) | {m['faithfulness']['faithfulness_rate']:.0%} | {sem(m['faithfulness']['faithfulness_rate'])} |
| 5 | Pedagogical Adaptation | {m['adaptation']['adaptation_rate']:.0%} | {sem(m['adaptation']['adaptation_rate'], good=0.5, warn=0.2)} |
| 6 | Validator Approval Rate | {m['validator']['approval_rate']:.0%} | {sem(m['validator']['approval_rate'])} |
|   | **Latencia promedio** | **{m['pipeline']['avg_latency_sec']}s** | {sem(1 if m['pipeline']['avg_latency_sec'] < 30 else 0)} |

---

## 1. Nivel de Contratos (Estructura)

Verifica que cada agente produce outputs conformes a sus modelos Pydantic (`EvaluacionTecnica`, `FeedbackPedagogico`, `ValidacionCalidad`).

- **Structural Validity (Overall):** {m['structure'].get('feedback_final_valid', 0):.0%}
- **Compliance Pydantic:** {m['structure'].get('evaluacion_tecnica_valid', 0):.0%} (Analista), {m['structure'].get('feedback_pedagogico_valid', 0):.0%} (Explicador)

---

## 2. Nivel Golden Tests (Sustancia Semántica)

¿La respuesta del agente contiene los términos técnicos obligatorios?

- **Semantic Coverage:** {m['semantic'].get('avg_semantic_coverage', 0):.0%}
- **Keywords encontradas:** {m['semantic'].get('total_keywords_found')}/{m['semantic'].get('total_keywords_expected')}

---

## 3. Nivel de Trazas (Lógica y Comportamiento)

¿El agente utilizó las herramientas correctas y discrimina la calidad?

- **Tool Consistency Match:** {m['tools'].get('avg_tool_match', 0):.0%}
- **Score Discrimination Gap:** {m['discrimination']['score_gap']} puntos
- **¿Discrimina buenas/malas?** {'✅ Sí' if m['discrimination']['discriminates'] else '❌ No'}

| Tipo | Score Promedio | Scores Individuales |
|------|---------------|---------------------|
| Decisiones Buenas | {m['discrimination']['avg_good_score']} | {m['discrimination']['good_scores']} |
| Decisiones Malas | {m['discrimination']['avg_bad_score']} | {m['discrimination']['bad_scores']} |

- **Gap:** {m['discrimination']['score_gap']} puntos
- **¿Discrimina?** {'✅ Sí' if m['discrimination']['discriminates'] else '❌ No'}

---

## 4. Faithfulness (Citación de Fuentes RAG)

¿El feedback final cita fuentes de la base de conocimiento?

- **Tasa de citación:** {m['faithfulness']['faithfulness_rate']:.0%}
- **Fuentes promedio por respuesta:** {m['faithfulness']['avg_sources_per_response']}

---

## 5. Pedagogical Adaptation

¿El Explicador adapta el lenguaje al nivel del jugador (Junior vs Senior)?

- **Tasa de adaptación:** {m['adaptation']['adaptation_rate']:.0%} ({m['adaptation']['adapted_cases']}/{m['adaptation']['total_comparable_cases']} casos)

---

## 6. Validator Effectiveness

¿El Agente Validador aprueba/rechaza coherentemente?

| Estado | Cantidad |
|--------|----------|
| Aprobados | {m['validator']['approved']} |
| Rechazados | {m['validator']['rejected']} |
| Con inconsistencias | {m['validator']['with_inconsistencies']} |

---

## Notas Técnicas

- Evaluación ejecutada con **{m.get('provider', '?')}** modelo **{m.get('model', '?')}** (para validar flujo).
- Se usaron {m.get('num_profiles', '?')} perfiles de jugador (Junior y Senior) por caso para medir adaptación pedagógica.
- Los resultados de calidad del LLM dependen del modelo; estas métricas evalúan el **sistema multiagente**, no el modelo.
- Para resultados de producción, re-ejecutar con `--provider gemini --model gemini-2.5-flash`.
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n  📄 Reporte guardado en: {output_path}")


# ============================================================================
# MAIN
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(description="Evaluación del Sistema Multiagente SOC-Tutor-RAG")
    parser.add_argument("--provider", default="ollama", help="Provider LLM: gemini, groq, ollama")
    parser.add_argument("--model", default=None, help="Modelo a usar (opcional)")
    parser.add_argument("--cases", type=int, help="Número de casos a ejecutar (opcional)")
    parser.add_argument("--dataset", type=str, default="eval_dataset.json", help="Nombre del archivo dataset en folder tests/")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🔬 EVALUACIÓN MULTIAGENTE — SOC-TUTOR-RAG SYSTEM")
    print(f"   Provider: {args.provider} | Modelo: {args.model}")
    print("=" * 60)

    # Cargar dataset
    dataset_path = Path(__file__).parent / args.dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        test_cases = json.load(f)

    if args.cases:
        test_cases = test_cases[:args.cases]

    print(f"📂 Dataset: {len(test_cases)} casos")

    # Inicializar componentes
    llm = create_llm_client(provider=args.provider)
    llm.model = args.model
    rag = create_rag_client()

    print(f"📚 Documentos en ChromaDB: {rag.count_documents()}")

    # Perfiles de jugador para evaluar adaptación pedagógica
    profiles = [
        PlayerProfile(player_id="eval-junior", level=1, rol="analyst"),
        PlayerProfile(player_id="eval-senior", level=5, rol="ciso"),
    ]

    # Inicializar orquestador y desactivar caché para evaluación
    orchestrator = UEFSOrchestrator(llm, rag)
    orchestrator.cache = None 

    # MÉTRICA 1: Pipeline Completeness (genera los resultados para las demás)
    pipeline_metrics = await eval_pipeline_completeness(
        orchestrator,
        test_cases,
        profiles
    )
    successful_results = [r for r in pipeline_metrics["results"] if r["success"]]

    # MÉTRICAS 2-6: Sobre los resultados exitosos
    structure_metrics = eval_structural_validity(successful_results)
    semantic_metrics = eval_semantic_coverage(successful_results)
    tool_metrics = eval_tool_consistency(successful_results)
    discrimination_metrics = eval_score_discrimination(successful_results)
    faithfulness_metrics = eval_faithfulness(successful_results)
    adaptation_metrics = eval_pedagogical_adaptation(successful_results)
    validator_metrics = eval_validator_effectiveness(successful_results)

    # Compilar todo
    all_metrics = {
        "provider": args.provider,
        "model": args.model,
        "num_cases": len(test_cases),
        "num_profiles": len(profiles),
        "pipeline": pipeline_metrics,
        "structure": structure_metrics,
        "semantic": semantic_metrics,
        "tools": tool_metrics,
        "discrimination": discrimination_metrics,
        "faithfulness": faithfulness_metrics,
        "adaptation": adaptation_metrics,
        "validator": validator_metrics,
    }

    # Generar reporte
    report_path = Path(__file__).parent.parent / "docs" / "EVAL_REPORT.md"
    generate_report(all_metrics, str(report_path))

    # Guardar JSON (sin los objetos Pydantic)
    json_safe = json.loads(json.dumps(all_metrics, default=str))
    # Limpiar objetos feedback del JSON (no serializables directamente)
    for r in json_safe.get("pipeline", {}).get("results", []):
        r.pop("feedback", None)

    json_path = Path(__file__).parent / "eval_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_safe, f, indent=2, ensure_ascii=False)
    print(f"  📄 Resultados JSON: {json_path}")

    print("\n" + "=" * 60)
    print("✅ EVALUACIÓN MULTIAGENTE COMPLETADA")
    print("=" * 60)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
