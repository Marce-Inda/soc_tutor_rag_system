"""
Script de Análisis de Regresión para SOC-Tutor-RAG.
Compara los resultados de la última evaluación contra una línea base (Baseline).
Detecta 'fallos silenciosos' (Nivel 5 de la checklist profesional).
"""

import json
import os
from pathlib import Path
import argparse

def compare_metrics(current, baseline):
    print("\n" + "=" * 60)
    print("🔬 ANÁLISIS DE REGRESIÓN (Nivel 5)")
    print("=" * 60)
    
    threshold_warning = 0.05
    threshold_critical = 0.15
    
    metrics_to_compare = [
        ("pipeline.success_rate", "Pipeline Success"),
        ("structure.feedback_final_valid", "Structural Validity"),
        ("semantic.avg_semantic_coverage", "Semantic Coverage"),
        ("tools.avg_tool_match", "Tool Consistency"),
        ("discrimination.score_gap", "Score Gap"),
        ("faithfulness.faithfulness_rate", "Faithfulness"),
        ("adaptation.adaptation_rate", "Pedagogical Adaptation")
    ]
    
    def get_val(d, path):
        parts = path.split(".")
        for p in parts:
            d = d.get(p, {})
        return d if isinstance(d, (int, float)) else 0.0

    print(f"{'Métrica':<30} | {'Baseline':<10} | {'Actual':<10} | {'Delta':<10} | {'Estado'}")
    print("-" * 80)
    
    regressions = []
    
    for path, label in metrics_to_compare:
        val_curr = get_val(current, path)
        val_base = get_val(baseline, path)
        delta = val_curr - val_base
        
        status = "🟢 OK"
        if delta <= -threshold_critical:
            status = "🔴 CRITICAL"
            regressions.append(f"CRITICAL: {label} dropped by {abs(delta):.2f}")
        elif delta <= -threshold_warning:
            status = "🟡 WARNING"
            regressions.append(f"WARNING: {label} dropped by {abs(delta):.2f}")
            
        print(f"{label:<30} | {val_base:<10.2f} | {val_curr:<10.2f} | {delta:<+10.2f} | {status}")

    print("\n" + "=" * 60)
    if regressions:
        print("⚠️  REGRESIONES DETECTADAS:")
        for r in regressions:
            print(f"  - {r}")
    else:
        print("✅ No se detectaron regresiones significativas.")
    print("=" * 60)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", default="eval_results.json")
    parser.add_argument("--baseline", default="eval_baseline.json")
    args = parser.parse_args()
    
    base_path = Path(__file__).parent
    current_file = base_path / args.current
    baseline_file = base_path / args.baseline
    
    if not current_file.exists():
        print(f"❌ Error: No se encuentra el archivo de resultados actuales: {current_file}")
        return
        
    if not baseline_file.exists():
        print(f"⚠️  No hay línea base ({args.baseline}). Creándola a partir de los resultados actuales...")
        with open(current_file, 'r') as f:
            data = json.load(f)
        with open(baseline_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Línea base creada en {baseline_file}")
        return

    with open(current_file, 'r') as f:
        curr_data = json.load(f)
    with open(baseline_file, 'r') as f:
        base_data = json.load(f)
        
    compare_metrics(curr_data, base_data)

if __name__ == "__main__":
    main()
