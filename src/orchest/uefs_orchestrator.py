"""
Main Orchestrator - SOC Tutor UEFS.
Agent coordinator using the Manager of Drafts pattern and bilingual reasoning.
"""

# ## ORQUESTADOR MAESTRO (UEFS)
# Este es el cerebro central del sistema que coordina la comunicación entre los agents.


from typing import Optional, Dict, Any
import time
from datetime import datetime

from ..agents.types import (
    InputFeedbackRequest, FeedbackFinal, EvaluacionTecnica, 
    EvaluacionGobernanza, FeedbackPedagogico, ValidacionCalidad, 
    Decision, ContextoEscenario, PlayerProfile
)

from ..agents.analyst_agent import AnalystAgent
from ..agents.explainer_agent import ExplainerAgent
from ..agents.validator_agent import ValidatorAgent
from ..agents.governance_agent import GovernanceAgent

from ..agents.guard_agent import GuardAgent
from ..agents.tools import SOCtools
from ..utils.memory import SessionMemory
from ..utils.observability import tracer
from ..utils.semantic_cache import get_cache_client

class UEFSOrchestrator:
    """
    Master Coordinator. Implements the Manager of Drafts pattern to ensure 
    pedagogical quality and legal compliance.
    """

    
    def __init__(
        self,
        llm_client,
        rag_client,
        enable_validation: bool = True,
        session_id: str = "sesion-default",
        validator_llm_client = None
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
        
        self.analyst_agent = AnalystAgent(llm_client, rag_client, tools=self.tools)
        self.governance_agent = GovernanceAgent(llm_client, rag_client)
        self.explainer_agent = ExplainerAgent(llm_client, rag_client)
        
        # Juez asimétrico: si no existe un cliente LLM externo, creamos uno de familia opuesta
        if validator_llm_client:
            judge_client = validator_llm_client
        else:
            # AUTO-ASIMETRÍA: Si el principal es Gemini, el Juez será Groq y viceversa.
            main_provider = llm_client.get_provider()
            judge_provider = "groq" if main_provider == "gemini" else "gemini"
            print(f" [Orchest] Asymmetric Judge activation: Main={main_provider} -> Judge={judge_provider}")
            from ..utils.llm_client import LLMClient
            judge_client = LLMClient(provider=judge_provider)
            
        self.validator_agent = ValidatorAgent(judge_client, rag_client)

        
        self.cache = get_cache_client(llm_client=llm_client)
        
        # Security Thresholds
        self.MAX_TURNS_PER_SESSION = 15
        self.MAX_COST_PER_SESSION = 0.05
        self.current_session_cost = 0.0

    def health_check(self) -> Dict[str, Any]:
        """Returns the health status of the orchestrator and its components."""
        return {
            "status": "healthy",
            "llm_provider": self.llm.get_provider(),
            "rag_documents": self.rag.count_documents(),
            "validation_enabled": self.enable_validation,
            "session_id": self.session_id
        }

    
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
             tracer.add_step("HIT_EN_CACHE_SEMANTICO", {"msg": "Result found in semantic cache"})
             res = FeedbackFinal(**cached_res)
             tracer.end_trace({"Proceso": "Caché"}, status="cache_hit")
             return res

        # 2. GUARD & MEMORY (Security L1/L2)
        try:
            # Check turn limits
            turns = self.memory.get_session_turn_count(self.session_id)
            if turns >= self.MAX_TURNS_PER_SESSION:
                 return self._get_safe_block_response("Session turn limit reached. Please start a new simulation.")

            # Check Cost limits
            if self.current_session_cost >= self.MAX_COST_PER_SESSION:
                 return self._get_safe_block_response("API Budget exceeded for this session. Please contact support.")

            is_safe, error_msg = self.guard.validate_input(decision)
            if not is_safe:
                tracer.end_trace({"error": error_msg}, status="blocked")
                return self._get_safe_block_response("Action could not be processed due to security policies.")
        except Exception as e:
            tracer.add_step("guard_error", {"error": str(e)})
            return self._get_safe_block_response("A technical security error occurred.")

        
        history = self.memory.get_history_summary(self.session_id)
        
        # 3. RAG
        if contexto.scenario_id:
            self.tools.set_scenario(contexto.scenario_id)

        # Optimization: k=3 + content truncation to stay under Groq 12k TPM
        raw_rag = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=3
        )
        
        # 4. Truncate and rebuild context string
        docs = raw_rag.get('documentos_recuperados', [])
        context_parts = []
        for i, d in enumerate(docs):
            content = d.get('text', '')
            if len(content) > 1500:
                content = content[:1500] + "... [TRUNCATED]"
            
            prefix = "[MATCH EXACTO]" if d.get('is_exact') else f"[RELEVANCIA {i+1}]"
            doc_id = d.get('id', 'no-id')[:8]
            context_parts.append(f"{prefix} (Source: {d['source']} | Hash: {doc_id}): {content}")
            
        contexto_rag_str = "\n\n".join(context_parts)
        
        # 4. ANALYST DUO (Technical + Governance)
        print(f" [Orchestrator] Running parallel evaluations...")
        evaluacion_analista = self.analyst_agent.evaluar(decision, contexto)
        self.current_session_cost += self.llm.last_usage["cost"]
        evaluacion_gobernanza = self.governance_agent.evaluar(decision, contexto)
        self.current_session_cost += self.llm.last_usage["cost"]
        
        # 5. GENERACIÓN Y VALIDACIÓN (Manager of Drafts Loop)
        max_retries = 1
        current_retry = 0
        feedback_explicador = None
        validacion = None
        
        while current_retry <= max_retries:
            print(f" [Orchestrator] Generating pedagogical feedback (Draft {current_retry + 1})...")
            
            # El Explainer usa inglés internamente
            feedback_explicador = self.explainer_agent.generar(
                evaluacion_analista=evaluacion_analista,
                evaluacion_gobernanza=evaluacion_gobernanza,
                player_profile=player_profile,
                contexto_rag=contexto_rag_str
            )
            self.current_session_cost += self.llm.last_usage["cost"]
            
            # El Validador traduce y pule (solo si está habilitado)
            if self.enable_validation:
                validacion = self.validator_agent.validar(
                    evaluacion_analista=evaluacion_analista,
                    feedback_explicador=feedback_explicador,
                    player_profile=player_profile,
                    contexto_rag=contexto_rag_str
                )
                self.current_session_cost += self.llm.last_usage["cost"]

                if validacion.approved or validacion.numeric_score >= 70:
                    print(f" [Orchestrator] Draft approved with score {validacion.numeric_score}")
                    break
                
                print(f" [Orchestrator] Draft rejected (Score: {validacion.numeric_score}). Retrying...")
                current_retry += 1
                tracer.add_step(f"retry_draft_{current_retry}", {"inconsistencies": validacion.inconsistencies})
            else:
                # Si la validación está desactivada, el primer draft es el final
                print(" [Orchestrator] Skipping validation as requested.")
                # Creamos un objeto validacion vacío o básico para que no rompa el ensamblaje final
                from src.agents.types import ValidacionCalidad
                validacion = ValidacionCalidad(
                    approved=True, 
                    correction=feedback_explicador.analysis, # Usamos el texto del explainer como "corrección"
                    numeric_score=100
                )
                break

        # 6. ENSAMBLAJE FINAL
        # Usamos la corrección del validador si existe, sino el feedback original
        final_text = validacion.correction if validacion.correction else feedback_explicador.analysis
        
        res = FeedbackFinal(
            evaluacion=final_text,
            explicacion=feedback_explicador.explanation,
            mejor_practica=feedback_explicador.best_practice,
            fuentes_citadas=raw_rag["sources"] + feedback_explicador.cited_sources,
            evaluacion_tecnica=evaluacion_analista,
            evaluacion_gobernanza=evaluacion_gobernanza,
            evaluacion_6d=validacion.evaluacion_6d,
            validacion=validacion,
            costo_estimado=self.current_session_cost,
            persona_role=validacion.persona_role or "Senior Analyst"
        )

        # 6.5 OUTPUT SECURITY CHECK (L3)
        if not self.guard.validate_output(res.evaluacion):
             return self._get_safe_block_response("Integrity check failed for the generated response.")


        
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

    def _get_safe_block_response(self, message: str) -> FeedbackFinal:
        """Genera una respuesta neutra y segura en caso de bloqueo."""
        return FeedbackFinal(
            evaluacion=message,
            explicacion="The system detected an entry or output that does not comply with security policies.",
            mejor_practica="Ensure your actions are technically focused on incident response.",
            fuentes_citadas=[],
            evaluacion_tecnica=EvaluacionTecnica(
                analysis="Blocked by security filters",
                explanation="Input does not comply with system safety requirements.",
                best_practice="Ensure your actions are technically focused on incident response.",
                sources=[],
                technical_score=0
            ),
            evaluacion_gobernanza=EvaluacionGobernanza(compliant=False, risks=["Security Block"], recommendations=[], frameworks=[], strategic_score=0, ethical_score=0),
            validacion=ValidacionCalidad(approved=False, inconsistencies=["Security Violation"], quality_score="High Risk", numeric_score=0),
            costo_estimado=0.0001,
            persona_role="System Security"
        )