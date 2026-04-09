"""
UEFS System Demo - Versión Integrada.
Ejecuta el pipeline completo: RAG -> ReAct Agent -> Memory -> Observability.
"""

import os
import sys
from pathlib import Path

# Configurar paths
sys.path.insert(0, str(Path(__file__).parent))

from src.agentes.types import Decision, ContextoEscenario, PlayerProfile
from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.utils.llm_client import create_llm_client
from src.rag.rag_client import create_rag_client

def run_integrated_demo():
    print("=" * 60)
    print("SOC TUTOR RAG SYSTEM - DEMO INTEGRADA")
    print("=" * 60)
    
    # 1. Verificar API Keys
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GROQ_API_KEY"):
        print("⚠️  Error: Se requieren API keys (GEMINI_API_KEY o GROQ_API_KEY).")
        return

    # 2. Inicializar Componentes reales
    print("\n[Init] Inicializando clientes de RAG y LLM...")
    llm = create_llm_client(provider="gemini")
    rag = create_rag_client()
    
    # Verificar si el RAG tiene documentos
    doc_count = rag.count_documents()
    print(f"[RAG] Documentos en base vectorial: {doc_count}")
    
    # 3. Inicializar Orquestador
    orchestrator = UEFSOrchestrator(llm, rag, session_id="demo-session-001")
    
    # 4. Simular decisión del jugador
    decision = Decision(
        accion="islar_host",
        target="WORKSTATION-X",
        detalle="Detectado proceso malicioso ejecutando comandos de PowerShell codificados."
    )
    contexto = ContextoEscenario(
        tipo_incidente="ransomware",
        fase="deteccion",
        sistemas_afectados=["WORKSTATION-X"]
    )
    perfil = PlayerProfile(player_id="marce-user", level=2)
    
    print(f"\n[Player] Decisión: {decision.accion} sobre {decision.target}")
    print(f"[System] Procesando feedback con agentes especializados...")
    
    # 5. Ejecutar Pipeline
    try:
        feedback = orchestrator.generar_feedback(decision, contexto, perfil)
        
        print("\n" + "=" * 60)
        print("FEEDBACK GENERADO PARA EL JUGADOR")
        print("-" * 60)
        print(f"📊 EVALUACIÓN: {feedback.evaluacion}")
        print(f"\n💡 EXPLICACIÓN: {feedback.explicacion}")
        print(f"\n🏆 MEJOR PRÁCTICA: {feedback.mejor_practica}")
        print(f"\n📚 FUENTES: {', '.join(feedback.fuentes_citadas)}")
        print(f"\n⭐ SCORE TÉCNICO: {feedback.evaluacion_tecnica.score_tecnico}/100")
        print("-" * 60)
        
        print(f"\n[Obs] Trace guardado en logs/traces/")
        print(f"[Mem] Decisión guardada en sesión {orchestrator.session_id}")
        
    except Exception as e:
        print(f"\n❌ Error en ejecución: {e}")

if __name__ == "__main__":
    run_integrated_demo()
