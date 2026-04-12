"""
Orquestador Principal - SOC Tutor UEFS.
Coordinador de agentes con patrón Manager of Drafts y razonamiento bilingüe.
"""

from typing import Optional, Dict, Any
import time
from datetime import datetime

from ..agentes.types import (
    InputFeedbackRequest, FeedbackFinal, EvaluacionTecnica, 
    EvaluacionGobernanza, FeedbackPedagogico, ValidacionCalidad, 
    Decision, ContextoEscenario, PlayerProfile
)

from ..agentes.agente_analista import AgenteAnalista
from ..agentes.agente_explicador import AgenteExplicador
from ..agentes.agente_validador import AgenteValidador
from ..agentes.agente_gobernanza import AgenteGobernanza  # Nuevo Agente
from ..agentes.guard_agent import GuardAgent
from ..agentes.tools import SOCtools
from ..utils.memory import SessionMemory
from ..utils.observability import tracer
from ..utils.semantic_cache import get_cache_client

class UEFSOrchestrator:
    """
    Coordinador Maestro. Implementa el patrón Manager of Drafts para asegurar 
    calidad pedagógica y cumplimiento legal.
    """
    
    def __init__(
        self,
        llm_client,
        rag_client,
        enable_validation: bool = True,
        session_id: str = "sesion-default"
    ):
        self.llm = llm_client
        self.rag = rag_client
        
        if hasattr(self.rag, 'llm_client') and self.rag.llm_client is None:
            self.rag.llm_client = llm_client
            
        self.enable_validation = enable_validation
        self.session_id = session_id
        
        self.tools = SOCtools(rag_client)
        self.memory = SessionMemory()
        self.guard = GuardAgent(llm_client)
        
        self.agente_analista = AgenteAnalista(llm_client, rag_client, tools=self.tools)
        self.agente_gobernanza = AgenteGobernanza(llm_client, rag_client)
        self.agente_explicador = AgenteExplicador(llm_client, rag_client)
        self.agente_validador = AgenteValidador(llm_client, rag_client)
        
        self.cache = get_cache_client(llm_client=llm_client)
    
    def generar_feedback(
        self,
        decision: Decision,
        contexto: ContextoEscenario,
        player_profile: PlayerProfile
    ) -> FeedbackFinal:
        """
        Flujo Maestro con loop de corrección (Manager of Drafts).
        """
        
        tracer.start_trace("evaluacion_integral_maestra", {
            "accion": decision.accion,
            "session_id": self.session_id
        })
        
        # 1. CACHÉ SEMÁNTICO
        cached_res = self.cache.lookup(
            decision=decision.model_dump(),
            context=contexto.model_dump(),
            player_profile=player_profile.model_dump()
        )
        if cached_res:
             tracer.add_step("HIT_EN_CACHE_SEMANTICO")
             res = FeedbackFinal(**cached_res)
             tracer.end_trace({"Proceso": "Caché"}, status="cache_hit")
             return res

        # 2. GUARD & MEMORY
        is_safe, error_msg = self.guard.validate_input(decision)
        if not is_safe:
            tracer.end_trace({"error": error_msg}, status="blocked")
            raise ValueError(f"Security Alert: {error_msg}")
        
        history = self.memory.get_history_summary(self.session_id)
        
        # 3. RAG
        if contexto.scenario_id:
            self.tools.set_scenario(contexto.scenario_id)

        rag_result = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=5
        )
        
        # 4. DUO DE ANALISTAS (Técnico + Gobernanza)
        print(f" [Orchestrator] Running parallel evaluations...")
        evaluacion_analista = self.agente_analista.evaluar(decision, contexto)
        evaluacion_gobernanza = self.agente_gobernanza.evaluar(decision, contexto)
        
        # 5. GENERACIÓN Y VALIDACIÓN (Manager of Drafts Loop)
        max_retries = 1
        current_retry = 0
        feedback_explicador = None
        validacion = None
        
        while current_retry <= max_retries:
            print(f" [Orchestrator] Generating pedagogical feedback (Draft {current_retry + 1})...")
            
            # El Explainer usa inglés internamente
            feedback_explicador = self.agente_explicador.generar(
                evaluacion_analista=evaluacion_analista,
                evaluacion_gobernanza=evaluacion_gobernanza,
                player_profile=player_profile,
                contexto_rag=rag_result["contexto_rag"]
            )
            
            # El Validador traduce y pule
            validacion = self.agente_validador.validar(
                evaluacion_analista=evaluacion_analista,
                feedback_explicador=feedback_explicador,
                player_profile=player_profile,
                contexto_rag=rag_result["contexto_rag"]
            )
            
            if validacion.approved or validacion.numeric_score >= 70:
                print(f" [Orchestrator] Draft approved with score {validacion.numeric_score}")
                break
            
            print(f" [Orchestrator] Draft rejected (Score: {validacion.numeric_score}). Retrying...")
            current_retry += 1
            tracer.add_step(f"retry_draft_{current_retry}", {"inconsistencies": validacion.inconsistencies})

        # 6. ENSAMBLAJE FINAL
        # Usamos la corrección del validador si existe, sino el feedback original
        final_text = validacion.correction if validacion.correction else feedback_explicador.analysis
        
        res = FeedbackFinal(
            evaluacion=final_text,
            explicacion=feedback_explicador.explanation,
            mejor_practica=feedback_explicador.best_practice,
            fuentes_citadas=rag_result["sources"] + feedback_explicador.cited_sources,
            evaluacion_tecnica=evaluacion_analista,
            evaluacion_gobernanza=evaluacion_gobernanza,
            validacion=validacion,
            costo_estimado=0.0008
        )
        
        # 7. MEMORY & CACHE
        self.memory.save_step(self.session_id, {
            "decision": decision.model_dump(),
            "timestamp": datetime.now().isoformat()
        })
        
        self.cache.store(
            decision=decision.model_dump(),
            context=contexto.model_dump(),
            player_profile=player_profile.model_dump(),
            feedback=res
        )
        
        tracer.end_trace({"status": "success"})
        return res