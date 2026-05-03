"""
Main Orchestrator - SOC Tutor UEFS.
Agent coordinator using the Manager of Drafts pattern and bilingual reasoning.
"""

# ## ORQUESTADOR MAESTRO (UEFS)
# Este es el cerebro central del sistema que coordina la comunicación entre los agents.


from typing import Optional, Dict, Any
import time
import asyncio
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
from ..utils.translator import Translator
MAX_COST_PER_SESSION = 0.05 # USD
MAX_TURNS_PER_SESSION = 15

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
        validator_llm_client = None
    ):
        self.llm = llm_client
        self.rag = rag_client
        
        if hasattr(self.rag, 'llm_client') and self.rag.llm_client is None:
            self.rag.llm_client = llm_client
            
        self.enable_validation = enable_validation
                
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
        self.translator = Translator(llm_client=llm_client)
        
        # Security Thresholds
        self.MAX_TURNS_PER_SESSION = 15
        self.MAX_COST_PER_SESSION = 0.05
        self.session_costs = {}

    def health_check(self) -> Dict[str, Any]:
        """Returns the health status of the orchestrator and its components."""
        return {
            "status": "healthy",
            "llm_provider": self.llm.get_provider(),
            "rag_documents": self.rag.count_documents(),
            "validation_enabled": self.enable_validation,
            "session_isolation": "enabled"
        }

    async def generar_feedback(
        self,
        decision: Decision,
        contexto: ContextoEscenario,
        player_profile: PlayerProfile
    ) -> FeedbackFinal:
        """
        Flujo Maestro Asíncrono con loop de corrección (Manager of Drafts).
        """
        
        session_id = player_profile.player_id
        
        tracer.start_trace("evaluacion_integral_maestra", {
            "accion": decision.accion,
            "session_isolation": "enabled",
            "session_id": session_id
        })
        
        if session_id not in self.session_costs:
            self.session_costs[session_id] = 0.0
            
        # CHECK BUDGET (Wallet-Exhaustion Protection)
        if self.session_costs[session_id] >= MAX_COST_PER_SESSION:
            print(f" [Orchest] 🛑 Budget exceeded for session {session_id}!")
            return self._get_safe_block_response("Budget limit reached for this session. Contact support.")
        
        # 0. English-First Gateway
        if player_profile.language != "en":
            print(f" [Orchest] English-First Gateway: Translating input from '{player_profile.language}' to 'en'...")
            decision.accion = await self.translator.translate_to_english(decision.accion)
            if decision.detalle:
                decision.detalle = await self.translator.translate_to_english(decision.detalle)

        # 1. CACHÉ SEMÁNTICO
        cached_res = await self.cache.lookup(
            decision=decision.model_dump(),
            context=contexto.model_dump(),
            player_profile=player_profile.model_dump()
        )
        if cached_res:
             print(f" [Orchest] ⚡ Semantic Cache HIT!")
             tracer.add_step("HIT_EN_CACHE_SEMANTICO", {"msg": "Result found in semantic cache"})
             res = FeedbackFinal(**cached_res)
             tracer.end_trace({"Proceso": "Caché"}, status="cache_hit")
             return res

        # 2. GUARD & MEMORY
        is_safe, error_msg = await self.guard.validate_input(decision)
        if not is_safe:
            tracer.end_trace({"error": error_msg}, status="blocked")
            return self._get_safe_block_response(f"Action could not be processed: {error_msg}")

        # 3. RAG - Context Bundle
        print(f" [Orchestrator] Retrieving RAG context bundle...")
        try:
            contexto_bundle = await self._retrieve_context_bundle(decision, contexto)
            contexto_full_str = contexto_bundle.get("full_text", str(contexto_bundle))
        except Exception as e:
            print(f" [Orchestrator] ⚠️ Error en RAG: {str(e)}. Continuando con contexto vacío.")
            contexto_bundle = {"sources": [], "documentos_recuperados": []}
            contexto_full_str = ""
        
        # 4. ANALYST DUO (Parallel)
        history = self.memory.get_history_summary(session_id)
        
        print(f" [Orchestrator] Running Analyst and Governance in parallel...")
        analista_task = asyncio.create_task(self.analyst_agent.evaluar(decision, contexto, contexto_rag=contexto_full_str, memoria_episodica=history))
        gobernanza_task = asyncio.create_task(self.governance_agent.evaluar(decision, contexto, contexto_rag=contexto_full_str))
        
        try:
            evaluacion_analista, evaluacion_gobernanza = await asyncio.gather(analista_task, gobernanza_task)
        except Exception as e:
            print(f" [Orchestrator] ⚠️ Error en agentes: {str(e)}. Usando respuestas de emergencia.")
            evaluacion_analista = self._get_api_error_response().evaluacion_tecnica
            evaluacion_gobernanza = self._get_api_error_response().evaluacion_gobernanza

        self.session_costs[session_id] += self.llm.last_usage.get("cost", 0.0)
        
        # 5. GENERACIÓN Y VALIDACIÓN (Manager of Drafts Loop)
        max_retries = 1
        current_retry = 0
        validacion = None
        
        while current_retry <= max_retries:
            print(f" [Orchestrator] Generating pedagogical feedback (Draft {current_retry + 1})...")
            prev_errs = validacion.inconsistencies if validacion else None
            
            feedback_explicador = await self.explainer_agent.generar(
                evaluacion_analista=evaluacion_analista,
                evaluacion_gobernanza=evaluacion_gobernanza,
                player_profile=player_profile,
                contexto_rag=contexto_full_str,
                prev_inconsistencies=prev_errs
            )
            self.session_costs[session_id] += self.llm.last_usage.get("cost", 0.0)
            
            if self.enable_validation:
                print(f" [Orchestrator] Validating draft consistency...")
                validacion = await self.validator_agent.validar(
                    evaluacion_analista=evaluacion_analista,
                    feedback_explicador=feedback_explicador,
                    player_profile=player_profile,
                    contexto_rag=contexto_full_str
                )
                self.session_costs[session_id] += self.llm.last_usage.get("cost", 0.0)

                if validacion.approved:
                    print(f" [Orchestrator] Draft approved.")
                    break
                
                current_retry += 1
                print(f" [Orchestrator] ⚠️ Draft rejected. Retrying...")
                tracer.add_step(f"retry_draft_{current_retry}", {"inconsistencies": validacion.inconsistencies})
            else:
                print(" [Orchestrator] Skipping validation as requested.")
                from src.agents.types import ValidacionCalidad
                validacion = ValidacionCalidad(approved=True, numeric_score=100)
                break

        # 6. ENSAMBLAJE FINAL
        final_text = validacion.correction if validacion.correction else feedback_explicador.analysis
        
        res = FeedbackFinal(
            evaluacion=final_text,
            explicacion=feedback_explicador.explanation,
            mejor_practica=feedback_explicador.best_practice,
            fuentes_citadas=contexto_bundle.get("sources", []),
            evaluacion_tecnica=evaluacion_analista,
            evaluacion_gobernanza=evaluacion_gobernanza,
            evaluacion_6d=validacion.evaluacion_6d,
            validacion=validacion,
            costo_estimado=self.session_costs[session_id],
            persona_role=validacion.persona_role or "Senior Analyst"
        )

        # 6.5 OUTPUT SECURITY CHECK (L3)
        if not self.guard.validate_output(res.evaluacion):
             return self._get_safe_block_response("Integrity check failed for the generated response.")

        # 8. English-First Delivery: Translate back to user language if necessary
        if player_profile.language != "en":
            print(f" [Orchest] English-First Delivery: Translating result back to '{player_profile.language}'...")
            res.evaluacion = await self.translator.translate_to_user_language(res.evaluacion, player_profile.language)
            res.explicacion = await self.translator.translate_to_user_language(res.explicacion, player_profile.language)
            res.mejor_practica = await self.translator.translate_to_user_language(res.mejor_practica, player_profile.language)
            
            # Deep Translation for technical report
            await self._translate_deep(res, player_profile.language)

    async def _translate_deep(self, res: FeedbackFinal, lang: str):
        """Translates nested fields in technical and governance reports."""
        # Translate EvaluacionTecnica
        if res.evaluacion_tecnica:
            t = res.evaluacion_tecnica
            t.analysis = await self.translator.translate_to_user_language(t.analysis, lang)
            t.explanation = await self.translator.translate_to_user_language(t.explanation, lang)
            t.best_practice = await self.translator.translate_to_user_language(t.best_practice, lang)
            t.strengths = await self.translator.translate_batch(t.strengths, lang)
            t.weaknesses = await self.translator.translate_batch(t.weaknesses, lang)
            
        # Translate EvaluacionGobernanza
        if res.evaluacion_gobernanza:
            g = res.evaluacion_gobernanza
            g.risks = await self.translator.translate_batch(g.risks, lang)
            g.recommendations = await self.translator.translate_batch(g.recommendations, lang)
            # Framework names are usually kept in original but we can translate descriptions if they had any

        # 9. PERSISTENCIA EN CACHÉ & MEMORIA
        self.memory.save_step(session_id, {
            "decision": decision.model_dump(),
            "timestamp": datetime.now().isoformat()
        })
        
        if self.cache and validacion.approved:
            await self.cache.store(
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

    def _get_api_error_response(self) -> FeedbackFinal:
        """Genera una respuesta inmersiva cuando hay un error de conexión con los servicios de IA."""
        from src.agents.types import EvaluacionTecnica, EvaluacionGobernanza, ValidacionCalidad
        return FeedbackFinal(
            evaluacion="[SISTEMA AUTOMATIZADO DE CONTINGENCIA] Conexión con el Comando Central temporalmente degradada.",
            explicacion="Se ha detectado una anomalía en las comunicaciones con los servidores de análisis profundo (Interrupción de API). Para proteger la integridad de las operaciones, los comandos complejos han sido pausados.",
            mejor_practica="Por favor, espera unos segundos e intenta ejecutar la acción táctica nuevamente.",
            fuentes_citadas=[],
            evaluacion_tecnica=EvaluacionTecnica(
                analysis="Conexión interrumpida con el análisis heurístico.",
                explanation="Fallo de conexión L2.",
                best_practice="Reintentar conexión.",
                sources=[],
                technical_score=0
            ),
            evaluacion_gobernanza=EvaluacionGobernanza(compliant=True, risks=["Conexión Degradada"], recommendations=[], frameworks=[], strategic_score=0, ethical_score=0),
            validacion=ValidacionCalidad(approved=False, inconsistencies=["Error de conexión"], quality_score="Degradado", numeric_score=0),
            costo_estimado=0.0,
            persona_role="System Security"
        )

    async def _retrieve_context_bundle(self, decision: Decision, contexto: ContextoEscenario) -> Dict[str, Any]:
        """
        Recupera el contexto de forma asíncrona.
        """
        # Note: RAGClient is still sync, but we wrap it
        res = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=2
        )
        return res