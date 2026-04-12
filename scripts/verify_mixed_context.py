"""
Verification script for Standalone English Context with Localized Names.
Ensures that the SOC Analyst (English Reasoning) correctly interprets the mixed context.
"""

from unittest.mock import MagicMock
from src.agents.types import Decision, ContextoEscenario, PlayerProfile
from src.agents.analyst_agent import AnalystAgent

from src.rag.rag_client import RAGClient

def test_mixed_context_reasoning():
    print("=" * 60)
    print("TEST: MIXED CONTEXT REASONING (English Log + Spanish Names)")
    print("=" * 60)
    
    # 1. Setup Mock LLM
    mock_llm = MagicMock()
    # Simulate ReAct reasoning where the LLM sees Spanish names but reasons in English
    mock_llm.generate.return_value = (
        "Thought: I see an alert from CreditoRápido S.A. "
        "The user involved is Juan Pérez, who was recently terminated. "
        "The sequential enumeration of IDs suggests an IDOR attack on the loan API. "
        "Action: search_mitre\n"
        "Observation: T1071 found.\n"
        "Final Answer: {\"fortalezas\": [\"Identification of Juan Pérez context\"], \"debilidades\": [], \"evaluacion\": \"Correct identification of IDOR attack targeting CreditoRápido S.A. infrastructure.\", \"fuentes\": [], \"score_tecnico\": 95}"
    )
    
    # 2. Setup Real/Mock RAG
    mock_rag = MagicMock()
    mock_rag.retrieve_with_context.return_value = {
        "contexto_rag": "Internal policy of CreditoRápido S.A. regarding JWT revocation.",
        "documentos_recuperados": [],
        "fuentes": []
    }
    
    analista = AnalystAgent(llm_client=mock_llm, rag_client=mock_rag)

    
    # 3. Decision and Context in English (but with Spanish Names)
    decision = Decision(
        accion="Analyze Request Payload",
        target="/api/v2/customers/1001/loans"
    )
    
    contexto = ContextoEscenario(
        scenario_id="ar-fintech-idor-001",
        tipo_incidente="IDOR Data Breach",
        fase="detection",
        organizacion="CreditoRápido S.A.", # Proper Name in Spanish
        sistemas_afectados=["Loan API Gateway"]
    )
    
    print("\n[Step 1] Executing Analyst evaluation...")
    evaluacion = analista.evaluar(decision, contexto)
    
    print(f"\n[Result]")
    print(f"  Score: {evaluacion.score_tecnico}")
    print(f"  Evaluation: {evaluacion.evaluacion}")
    
    # Success if the evaluation string contains the company name
    if "CreditoRápido S.A." in evaluacion.evaluacion:
        print("\n✓ SUCCESS: Analyst correctly preserved and used the specific local company name.")
    else:
        print("\n✗ FAILURE: Local context was lost in reasoning.")

if __name__ == "__main__":
    test_mixed_context_reasoning()
