"""
UEFS Orchestrator v2 - Integración completa.
Incluye Memoria, Guardrails, Herramientas ReAct y Observabilidad.
"""

from typing import Optional
import time
from datetime import datetime

from ..agentes.types import (
    InputFeedbackRequest,
    FeedbackFinal,
    EvaluacionTecnica,
    FeedbackPedagogico,
    ValidacionCalidad,
    Decision,
    ContextoEscenario,
    PlayerProfile
)

from ..agentes.agente_analista import AgenteAnalista
from ..agentes.agente_explicador import AgenteExplicador
from ..agentes.agente_validador import AgenteValidador
from ..agentes.guard_agent import GuardAgent
from ..agentes.tools import SOCtools
from ..utils.memory import SessionMemory
from ..utils.observability import tracer


class UEFSOrchestrator:
    """
    Orquestador avanzado del sistema UEFS con RAG.
    """
    
    def __init__(
        self,
        llm_client,
        rag_client,
        enable_validation: bool = True,
        session_id: str = "default-session"
    ):
        self.llm = llm_client
        self.rag = rag_client
        self.enable_validation = enable_validation
        self.session_id = session_id
        
        # Componentes
        self.tools = SOCtools(rag_client)
        self.memory = SessionMemory()
        self.guard = GuardAgent(llm_client)
        
        # Inicializar agentes
        self.agente_analista = AgenteAnalista(llm_client, rag_client, tools=self.tools)
        self.agente_explicador = AgenteExplicador(llm_client, rag_client)
        self.agente_validador = AgenteValidador(llm_client, rag_client)
    
    def generar_feedback(
        self,
        decision: Decision,
        contexto: ContextoEscenario,
        player_profile: PlayerProfile
    ) -> FeedbackFinal:
        """Genera feedback completo con seguridad y memoria."""
        
        # Start Trace (Observability)
        tracer.start_trace("generar_feedback", {
            "accion": decision.accion,
            "session_id": self.session_id,
            "level": player_profile.level
        })
        
        # 1. Guardrails (Security)
        is_safe, error_msg = self.guard.validate_input(decision)
        if not is_safe:
            tracer.end_trace({"error": error_msg}, status="blocked")
            raise ValueError(f"Seguridad: {error_msg}")
        
        # 2. Memory Context
        history = self.memory.get_history_summary(self.session_id)
        tracer.add_step("Contexto_Memoria", {"history": history})
        
        # 3. RAG Retrieval
        rag_result = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=5
        )
        tracer.add_step("Retrieval_RAG", {"docs_count": len(rag_result['documentos_recuperados'])})
        
        # 4. Agente Analista (ReAct)
        evaluacion_analista = self.agente_analista.evaluar(decision, contexto)
        tracer.add_step("Agente_Analista_Done", {"score": evaluacion_analista.score_tecnico})
        
        # 5. Agente Explicador
        feedback_explicador = self.agente_explicador.generar(
            evaluacion_analista=evaluacion_analista,
            player_profile=player_profile,
            contexto_rag=rag_result["contexto_rag"]
        )
        tracer.add_step("Agente_Explicador_Done", {})
        
        # 6. Agente Validador
        validacion = self.agente_validador.validar(
            evaluacion_analista=evaluacion_analista,
            feedback_explicador=feedback_explicador,
            player_profile=player_profile,
            contexto_rag=rag_result["contexto_rag"]
        )
        
        # Final Step: Persist memory
        self.memory.save_step(self.session_id, {
            "decision": decision.model_dump(),
            "timestamp": datetime.now().isoformat()
        })
        
        # Build Result
        res = FeedbackFinal(
            evaluacion=feedback_explicador.evaluacion,
            explicacion=feedback_explicador.explicacion,
            mejor_practica=feedback_explicador.mejor_practica,
            fuentes_citadas=rag_result["fuentes"] + feedback_explicador.fuentes_citadas,
            evaluacion_tecnica=evaluacion_analista,
            validacion=validacion,
            costo_estimado=0.0006 # Estimación fija para demo
        )
        
        tracer.end_trace({"feedback": "completed"})
        return res