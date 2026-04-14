"""
Simulation Driver - SOC Tutor Phased Incident.
This script runs a specific phase decision through the orchestrator.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.types import Decision, ContextoEscenario, PlayerProfile
from src.orchest.uefs_orchestrator import UEFSOrchestrator
from src.utils.llm_client import create_llm_client
from src.rag.rag_client import create_rag_client

def run_simulation_step(accion, target, detalle, tipo_incidente, fase, scenario_id):
    load_dotenv()
    
    # Init system (Resilient setup - switching to Groq as primary for speed during simulation)
    llm = create_llm_client(provider="groq")
    rag = create_rag_client()
    orchestrator = UEFSOrchestrator(llm, rag, enable_validation=False, session_id="simulation-ghost-bank")

    decision = Decision(accion=accion, target=target, detalle=detalle)
    contexto = ContextoEscenario(tipo_incidente=tipo_incidente, fase=fase, scenario_id=scenario_id)
    perfil = PlayerProfile(player_id="user-auto", level=3, language="es")

    print(f"\n--- [SIMULACIÓN] Procesando Fase: {fase.upper()} ---")
    feedback = orchestrator.generar_feedback(decision, contexto, perfil)
    
    print("\n" + "="*50)
    print(f"EVALUACIÓN: {feedback.evaluacion}")
    print(f"EXPLICACIÓN: {feedback.explicacion}")
    print(f"MEJOR PRÁCTICA: {feedback.mejor_practica}")
    print(f"FUENTES: {feedback.fuentes_citadas}")
    print(f"COSTO: {feedback.costo_estimado:.6f} USD")
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) < 7:
        print("Usage: python sim_driver.py <accion> <target> <detalle> <tipo_incidente> <fase> <scenario_id>")
    else:
        run_simulation_step(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
