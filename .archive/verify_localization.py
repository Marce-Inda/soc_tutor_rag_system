"""
Verification script for SOC Tutor Localization.
Tests the orchestration flow with different languages (ES, PT, EN).
"""

from typing import Dict, Any
import json
from unittest.mock import MagicMock

from src.agents.types import Decision, ContextoEscenario, PlayerProfile
from src.orchest.uefs_orchestrator import UEFSOrchestrator

class MockLLM:
    def generate(self, prompt, system_prompt=None):
        print(f"\n[DEBUG] LLM.generate called with prompt starting with: {prompt[:100]}...")
        # Simular razonamiento en inglés
        if "Action:" in prompt or "Senior SOC Analyst" in prompt:
            return "Thought: I need to analyze the incident. Final Answer: {\"fortalezas\": [\"English strength\"], \"debilidades\": [], \"evaluacion\": \"Tech assessment\", \"fuentes\": [], \"score_tecnico\": 90}"
        
        # Simular traduccion
        if "Translate" in prompt:
            return "English Translation for RAG"
            
        return "Generic Response"

    def generate_json(self, prompt, system_prompt=None):
        print(f"\n[DEBUG] LLM.generate_json called with prompt containing language: {prompt.split('language: ')[-1][:20] if 'language: ' in prompt else 'unknown'}")
        
        # Si es el explicador, devolver en el idioma solicitado (simulado)
        if "You MUST generate the entire feedback in:" in prompt:
            if "Spanish" in prompt or " es" in prompt:
                return {
                    "evaluacion": "Feedback en ESPAÑOL",
                    "explicacion": "Explicación en ESPAÑOL",
                    "mejor_practica": "Práctica en ESPAÑOL",
                    "fuentes_citadas": []
                }
            if "Portuguese" in prompt or " pt" in prompt:
                return {
                    "evaluacion": "Feedback em PORTUGUÊS",
                    "explicacion": "Explicação em PORTUGUÊS",
                    "mejor_practica": "Prática em PORTUGUÊS",
                    "fuentes_citadas": []
                }
            if "English" in prompt or " en" in prompt:
                return {
                    "evaluacion": "Feedback in ENGLISH",
                    "explicacion": "Explanation in ENGLISH",
                    "mejor_practica": "Practice in ENGLISH",
                    "fuentes_citadas": []
                }
        
        # Validador
        if "aprobado" in prompt:
            return {"aprobado": True, "inconsistencias": [], "nota": "Validado"}

        return {}

def test_language(lang: str):
    print(f"\n" + "="*50)
    print(f"TESTING LANGUAGE: {lang.upper()}")
    print("="*50)
    
    mock_llm = MockLLM()
    mock_rag = MagicMock()
    # Mock RAG response
    mock_rag.retrieve_with_context.return_value = {
        "contexto_rag": "Knowledge fragment in English",
        "documentos_recuperados": ["doc1"],
        "fuentes": ["NIST"]
    }
    mock_rag.llm_client = None # For UEFSOrchestrator to inject mock_llm
    
    orchestrator = UEFSOrchestrator(
        llm_client=mock_llm,
        rag_client=mock_rag,
        session_id=f"test-{lang}"
    )
    
    # Perfil con idioma específico
    profile = PlayerProfile(
        player_id="tester",
        level=3,
        rol="analyst",
        language=lang
    )
    
    decision = Decision(accion="test_action", target="victim-host")
    contexto = ContextoEscenario(tipo_incidente="ransomware", fase="detection")
    
    print(f"Running orchestrator for {lang}...")
    res = orchestrator.generar_feedback(decision, contexto, profile)
    
    print(f"\nRESULT for {lang}:")
    print(f"  Evaluación: {res.evaluacion}")
    print(f"  Idioma detectado en respuesta: {'ESPAÑOL' if 'ESPAÑOL' in res.evaluacion else 'PORTUGUÊS' if 'PORTUGUÊS' in res.evaluacion else 'ENGLISH' if 'ENGLISH' in res.evaluacion else 'UNKNOWN'}")

if __name__ == "__main__":
    test_language("es")
    test_language("pt")
    test_language("en")
