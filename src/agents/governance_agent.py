"""
Governance Agent - Specialist in legal compliance and ethics.
"""

# ## AGENTE DE GOBERNANZA
# Evalúa el impacto legal (GDPR) y los riesgos éticos de las decisiones del jugador.

from typing import Dict, Any
from .prompts import build_prompt_gobernanza
from .types import EvaluacionGobernanza, Decision, ContextoEscenario
from ..utils.observability import tracer

class GovernanceAgent:


    """
    Agent that evaluates regulatory compliance (GDPR, local laws) and ethics.
    """

    
    def __init__(self, llm_client, rag_client):
        self.llm = llm_client
        self.rag = rag_client
        
    async def evaluar(
        self, 
        decision: Decision, 
        contexto: ContextoEscenario,
        contexto_rag: str = ""
    ) -> EvaluacionGobernanza:
        """
        Performs the governance evaluation based on the decision and RAG context.
        """
        
        # 1. Use provided context or retrieve specifically for compliance
        if not contexto_rag:
            print(f"  [Governance] No context provided. Retrieving via RAG...")
            query = f"Compliance and legal risks for {decision.accion} in {contexto.tipo_incidente}"
            rag_res = self.rag.retrieve(query, k=3)
            contexto_rag = "\n".join([d['text'] for d in rag_res])
        
        # 2. Construir prompt
        prompt = build_prompt_gobernanza(decision, contexto, contexto_rag)
        
        # 3. Llamar al LLM
        response = await self.llm.generate_json(prompt)
        
        # 4. Parsear resultado
        try:
            res = EvaluacionGobernanza(**response)
        except Exception as e:
            tracer.add_step("error_parsing_gobernanza", {"error": str(e)})
            # Fallback seguro (Fail-Closed)
            res = EvaluacionGobernanza(
                compliant=False, 
                risks=["Error parsing legal evaluation - Fail Closed triggered"],
                recommendations=["Consulte al departamento legal de forma manual"],
                frameworks=[],
                strategic_score=0,
                ethical_score=0
            )
            
        return res
