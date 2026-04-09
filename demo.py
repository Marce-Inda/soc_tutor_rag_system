"""
Demo del sistema UEFS con RAG.
Ejemplo de uso del orquestador con una decisión de prueba.
"""

import os
import sys
from pathlib import Path

# Agregar parent al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Imports del proyecto
from src.agentes.types import (
    Decision,
    ContextoEscenario,
    PlayerProfile,
    InputFeedbackRequest
)

# Importar módulos (simulados - en producción serían reales)
# from 03_configuracion_de_modelos.llm_client import LLMClient
# from 04_integracion_de-herramientas.rag_client import RAGClient
# from src.orchest.uefs_orchestrator import UEFSOrchestrator


def run_demo():
    """Ejecuta un demo del sistema."""
    
    print("=" * 60)
    print("SOC TUTOR RAG SYSTEM - DEMO")
    print("=" * 60)
    
    # Verificar API keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not gemini_key and not groq_key:
        print("\n⚠️  ATENCIÓN: No hay API keys configuradas.")
        print("   Configure sus variables de entorno:")
        print("   - GEMINI_API_KEY")
        print("   - GROQ_API_KEY")
        print("\n   Alternativamente, puede usar el fallback determinista.")
        
        # Ejecutar demo sin LLM
        run_demo_fallback()
        return
    
    # Aquí iría la ejecución con LLM real
    print("\n✓ API keys detectadas - sistema listo para ejecutar")
    print("   (Implementar con LLMClient y RAGClient reales)")
    

def run_demo_fallback():
    """Demo usando fallback determinista."""
    
    print("\n" + "=" * 60)
    print("EJECUTANDO DEMO - FALLBACK DETERMINISTA")
    print("=" * 60)
    
    # Crear request de ejemplo
    request = InputFeedbackRequest(
        decision=Decision(
            accion="bloquear_ip",
            target="192.168.1.100",
            detalle="IP sospechoso en logs de firewall"
        ),
        contexto=ContextoEscenario(
            tipo_incidente="phishing",
            fase="contencion",
            sistemas_afectados=["WORKSTATION-001", "MAIL-SERVER"],
            score=0
        ),
        player_profile=PlayerProfile(
            player_id="demo-user",
            level=1,
            rol="analyst",
            dilema_index_session=2
        )
    )
    
    print(f"\n📋 DECISIÓN: {request.decision.accion}")
    print(f"🎯 INCIDENTE: {request.contexto.tipo_incidente}")
    print(f"👤 JUGADOR: Level {request.player_profile.level} ({request.player_profile.rol})")
    
    # Output esperado (simulado)
    expected_output = {
        "evaluacion": "Buen instinto. Identificaste correctamente el tráfico sospechoso.",
        "explicacion": "El bloqueo de IPs desconocidas es una práctica básica de contención.",
        "mejor_practica": "Documenta el IOCs y ejecuta análisis forense en el endpoint.",
        "score_tecnico": 75,
        "fuentes_citadas": ["NIST SP 800-61", "MITRE ATT&CK T1071"]
    }
    
    print("\n📤 OUTPUT ESPERADO:")
    print("-" * 40)
    for key, value in expected_output.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✓ Demo completado")
    print("   Para ejecutar con LLM real:")
    print("   1. pip install -r requirements.txt")
    print("   2. python 02-ingestion-datos/download_docs.py")
    print("   3. python 02-ingestion-datos/ingest_docs.py")
    print("   4. Configure API keys y ejecute este script")
    print("=" * 60)


def main():
    """Entry point."""
    run_demo()


if __name__ == "__main__":
    main()