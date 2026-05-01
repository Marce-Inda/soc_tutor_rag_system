import sys
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent))

from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.agents.types import Decision, ContextoEscenario, PlayerProfile, FeedbackFinal, EvaluacionTecnica, EvaluacionGobernanza, ValidacionCalidad, Score6D, FeedbackPedagogico

def test_english_first_gateway():
    print("=== Testeando English-First Gateway ===")
    
    # Mocks
    mock_llm = MagicMock()
    # Mock para la traducción inicial (Gateway)
    # Primera llamada: traducir "Bloquear IP" -> "Block IP"
    # Segunda llamada: traducir detalle -> "Detail"
    mock_llm.generate.side_effect = [
        "Block IP", 
        "Suspicious traffic",
        "Fast Path Response in English"
    ]
    
    mock_rag = MagicMock()
    mock_rag.retrieve_hybrid.return_value = [{"text": "NIST info", "source": "NIST"}]
    
    # Orquestador
    orchestrator = UEFSOrchestrator(llm_client=mock_llm, rag_client=mock_rag)
    
    # Datos en Español
    decision = Decision(accion="Bloquear IP", target="1.1.1.1", detalle="Tráfico sospechoso")
    contexto = ContextoEscenario(tipo_incidente="phishing", fase="containment", scenario_id="test")
    profile = PlayerProfile(player_id="user1", level=1, language="es")
    
    print("\nEjecutando generar_feedback con input en Español...")
    # Forzamos que sea teórico para ir por el Fast Path y no necesitar mockear todos los agentes
    decision.target = "tutor"
    decision.accion = "Que es NIST?"
    
    # Reset mock para este caso
    mock_llm.generate.side_effect = [
        "What is NIST?", 
        "NIST is a framework..." # Respuesta del Fast Path
    ]
    
    res = orchestrator.generar_feedback(decision, contexto, profile)
    
    # Verificaciones
    calls = mock_llm.generate.call_args_list
    print(f"\nLlamadas al LLM ({len(calls)}):")
    for i, call in enumerate(calls):
        print(f"  {i+1}: {call}")

    # La primera llamada debe ser la traducción del Gateway
    first_call_prompt = calls[0][0][0]
    if "Translate to English: Que es NIST?" in first_call_prompt:
        print("\n✓ Gateway detectado: Se solicitó traducción del input original.")
    else:
        print("\n✗ Error: No se detectó la llamada de traducción inicial.")

    print(f"\nResultado final: {res.evaluacion[:50]}...")
    print("=== Test completado ===")

if __name__ == "__main__":
    test_english_first_gateway()
