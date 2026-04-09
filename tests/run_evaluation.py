"""
Script de evaluación para el sistema UEFS.
Calcula métricas de calidad sobre el dataset sintético.
"""

import json
import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agentes.types import Decision, ContextoEscenario, PlayerProfile
from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.utils.llm_client import create_llm_client
from src.rag.rag_client import create_rag_client

def run_eval():
    print("=" * 60)
    print("INICIANDO EVALUACIÓN DE CALIDAD (Métricas RAG)")
    print("=" * 60)
    
    # Cargar dataset
    dataset_path = Path(__file__).parent / "eval_dataset.json"
    with open(dataset_path, 'r') as f:
        test_cases = json.load(f)
    
    # Inicializar orquestador (mocked or real)
    llm = create_llm_client()
    rag = create_rag_client()
    orchestrator = UEFSOrchestrator(llm, rag)
    
    results = []
    total_score = 0
    
    for case in test_cases:
        print(f"\nProbando caso {case['id']}...")
        
        # Generar feedback
        try:
            feedback = orchestrator.generar_feedback(
                decision=Decision(**case['decision']),
                contexto=ContextoEscenario(**case['contexto']),
                player_profile=PlayerProfile(player_id="eval-bot", level=3)
            )
            
            # Calcular métricas simples
            # 1. Faithfulness (¿cita fuentes?)
            has_sources = len(feedback.fuentes_citadas) > 0
            
            # 2. Precision (¿contiene conceptos esperados?)
            found_concepts = []
            for concept in case['expected_concepts']:
                if concept.lower() in feedback.explicacion.lower() or concept.lower() in feedback.evaluacion.lower():
                    found_concepts.append(concept)
            
            precision = len(found_concepts) / len(case['expected_concepts'])
            
            # 3. Alignment (Score técnico vs esperado)
            score_diff = abs(feedback.evaluacion_tecnica.score_tecnico - case['min_score'])
            
            results.append({
                "id": case['id'],
                "precision": precision,
                "faithfulness": 1.0 if has_sources else 0.0,
                "found_concepts": found_concepts
            })
            
            total_score += precision
            print(f"  → Precision: {precision:.2f}")
            print(f"  → Faithfulness: {'Cita fuentes' if has_sources else 'NO cita fuentes'}")
            
        except Exception as e:
            import traceback
            print(f"  ❌ Error en caso {case['id']}: {e}")
            traceback.print_exc()

    # Resumen final
    avg_precision = total_score / len(test_cases)
    print("\n" + "=" * 60)
    print("RESUMEN DE EVALUACIÓN")
    print(f"  Precision Promedio: {avg_precision:.2f}")
    print(f"  Casos exitosos: {len(results)}/{len(test_cases)}")
    print("=" * 60)

if __name__ == "__main__":
    run_eval()
