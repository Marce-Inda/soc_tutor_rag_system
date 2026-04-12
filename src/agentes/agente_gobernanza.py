"""
Agente de Gobernanza. Especialista en cumplimiento legal y ética.
"""

from typing import Dict, Any
from .prompts import build_prompt_gobernanza
from .types import EvaluacionGobernanza
from ..utils.observability import tracer


class AgenteGobernanza:
    """
    Agente que evalúa el cumplimiento normativo (GDPR, Leyes Locales) y ética.
    """
    
    def __init__(self, llm_client, rag_client):
        self.llm = llm_client
        self.rag = rag_client
        
    def evaluar(self, decision: Dict[str, Any], contexto: Dict[str, Any]) -> EvaluacionGobernanza:
        """
        Realiza la evaluación de gobernanza basándose en la decisión y el contexto RAG.
        """
        tracer.start_trace("evaluacion_gobernanza")
        
        # 1. Recuperar contexto RAG específico para cumplimiento
        query = f"Compliance and legal risks for {decision.get('accion')} in {contexto.get('tipo_incidente')}"
        rag_res = self.rag.retrieve(query, k=3)
        contexto_rag = "\n".join(rag_res.get("documentos_recuperados", []))
        
        # 2. Construir prompt
        prompt = build_prompt_gobernanza(decision, contexto, contexto_rag)
        
        # 3. Llamar al LLM
        response = self.llm.complete(prompt, json_mode=True)
        
        # 4. Parsear resultado
        try:
            res = EvaluacionGobernanza(**response)
        except Exception as e:
            tracer.add_step("error_parsing_gobernanza", {"error": str(e)})
            # Fallback seguro
            res = EvaluacionGobernanza(
                compliant=True, 
                risks=["Error parsing legal evaluation"],
                recommendations=[],
                frameworks=[]
            )
            
        tracer.end_trace({"cumplimiento": res.compliant})
        return res
