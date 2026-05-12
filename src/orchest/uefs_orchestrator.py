"""
Main Orchestrator - SOC Tutor UEFS.
Agent coordinator using the Manager of Drafts pattern and bilingual reasoning.
"""

# ## ORQUESTADOR MAESTRO (UEFS)
# Este es el cerebro central del sistema que coordina la comunicación entre los agents.


from typing import Optional, Dict, Any, List
import re
import time
import asyncio
from datetime import datetime

from ..agents.types import (
    InputFeedbackRequest, FeedbackFinal, EvaluacionTecnica, 
    EvaluacionGobernanza, FeedbackPedagogico, ValidacionCalidad, 
    Decision, ContextoEscenario, PlayerProfile
)
from ..utils.security import sanitize_content, truncate_log_data, mask_pii

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

    _active_sessions = {} # session_id: last_activity_timestamp
    MAX_CONCURRENT_SESSIONS = 2


    
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
        
        # --- CONCURRENT USER LIMIT (Harden Goal 3) ---
        current_time = time.time()
        # Clean expired sessions (inactive for > 5 mins)
        self._active_sessions = {sid: ts for sid, ts in self._active_sessions.items() if (current_time - ts) < 300}
        
        if session_id not in self._active_sessions and len(self._active_sessions) >= self.MAX_CONCURRENT_SESSIONS:
            print(f" [Orchest] 🛑 System saturated. Concurrent users: {len(self._active_sessions)}")
            return FeedbackFinal(
                evaluacion="[CONSOLA SOC] El sistema de análisis está operando a máxima capacidad procesando otros incidentes críticos. Por favor, mantente a la espera (Waitlist) un momento mientras liberamos ciclos de procesamiento.",
                explicacion="Se ha alcanzado el límite de usuarios concurrentes en la infraestructura pedagógica.",
                mejor_practica="Intenta de nuevo en un par de minutos.",
                fuentes_citadas=[],
                evaluacion_tecnica=EvaluacionTecnica(analysis="Waitlist trigger active", explanation="Max concurrent users reached", best_practice="Retry later", technical_score=0),
                validacion=ValidacionCalidad(approved=False, numeric_score=0, quality_score="Saturated"),
                costo_estimado=0.0
            )
        
        self._active_sessions[session_id] = current_time
        # ---------------------------------------------

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
        if self.cache:
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

        # 2. IMMERSIVE RATE LIMIT CHECK (Red Hat Mitigation)
        last_step_time = self.memory.get_last_step_timestamp(session_id)
        current_time = time.time()
        if last_step_time and (current_time - last_step_time) < 10:
            print(f" [Orchest] ⚡ Rate Limit Triggered (Immersive). Speed: {current_time - last_step_time:.2f}s")
            return FeedbackFinal(
                evaluacion=f"Analista, aguarda un momento. La consola del SOC está procesando una ráfaga de telemetría de {contexto.tipo_incidente}. Dame unos segundos para que los agentes de Gobernanza y Análisis sincronicen sus hallazgos antes de nuestra próxima acción.",
                explicacion="Espera unos 10 segundos entre acciones para permitir que la IA procese los datos correctamente.",
                mejor_practica="La velocidad de análisis del SOC está limitada para garantizar profundidad y calidad en cada evaluación.",
                fuentes_citadas=[],
                evaluacion_tecnica=EvaluacionTecnica(
                    analysis="Rate limit active", explanation="Immersive cooldown triggered",
                    best_practice="Wait 10 seconds between actions", sources=[], technical_score=0
                ),
                evaluacion_gobernanza=EvaluacionGobernanza(
                    compliant=True, risks=[], recommendations=["Sincronizando telemetría..."],
                    frameworks=[], strategic_score=0, ethical_score=0
                ),
                validacion=ValidacionCalidad(
                    approved=False, inconsistencies=["Rate limit cooldown"],
                    quality_score="Cooldown Active", numeric_score=0
                ),
                costo_estimado=0.0
            )

        # 3. GUARD & MEMORY (Sanitization Layer)
        # Sanitizar inputs del jugador para evitar inyección de prompt
        decision.accion = sanitize_content(decision.accion)
        decision.target = sanitize_content(decision.target)
        if decision.detalle:
            decision.detalle = sanitize_content(decision.detalle)


        is_safe, error_msg = await self.guard.validate_input(decision)
        if not is_safe:
            tracer.end_trace({"error": error_msg}, status="blocked")
            return self._get_safe_block_response(f"Action could not be processed: {error_msg}")

        # 4. RAG - Context Bundle
        print(f" [Orchestrator] Retrieving RAG context bundle...")
        try:
            contexto_bundle = await self._retrieve_context_bundle(decision, contexto)
            contexto_full_str = contexto_bundle.get("full_text", str(contexto_bundle))
            # Sanitizar contexto del RAG por si las fuentes fueron envenenadas
            contexto_full_str = sanitize_content(contexto_full_str)
        except Exception as e:
            print(f" [Orchestrator] ⚠️ Error en RAG: {str(e)}. Continuando con contexto vacío.")
            contexto_bundle = {"sources": [], "documentos_recuperados": []}
            contexto_full_str = ""
        
        # 5. ANALYST DUO (Parallel)
        history = self.memory.get_history_summary(session_id)
        # Sanitizar historial por si se compactó contenido malicioso
        history = sanitize_content(history)
        
        print(f" [Orchestrator] Running Analyst and Governance in parallel...")
        analista_task = asyncio.create_task(self.analyst_agent.evaluar(decision, contexto, contexto_rag=contexto_full_str, memoria_episodica=history))
        gobernanza_task = asyncio.create_task(self.governance_agent.evaluar(decision, contexto, contexto_rag=contexto_full_str, memoria_episodica=history))
        
        try:
            evaluacion_analista, evaluacion_gobernanza = await asyncio.gather(analista_task, gobernanza_task)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f" [Orchestrator] ⚠️ Error en agentes: {repr(e)}. Usando respuestas de emergencia.")
            evaluacion_analista = self._get_api_error_response().evaluacion_tecnica
            evaluacion_gobernanza = self._get_api_error_response().evaluacion_gobernanza

        self.session_costs[session_id] += self.llm.last_usage.get("cost", 0.0)
        
        # 4.5 HITL CHECK (Governance Pause)
        if evaluacion_gobernanza.requires_confirmation:
            print(f" [Orchestrator] 🚨 ACTION PAUSED BY GOVERNANCE: {evaluacion_gobernanza.confirmation_reason}")
            
            # Save state for resumption
            self.memory.save_pending_evaluation(
                session_id, 
                evaluacion_analista.model_dump(), 
                evaluacion_gobernanza.model_dump()
            )
            
            return FeedbackFinal(
                evaluacion="PAUSED",
                explicacion=evaluacion_gobernanza.confirmation_reason,
                mejor_practica="Please provide a technical or strategic justification for this high-risk action.",
                fuentes_citadas=[],
                evaluacion_tecnica=evaluacion_analista,
                evaluacion_gobernanza=evaluacion_gobernanza,
                status="paused",
                requires_hitl=True,
                hitl_message=evaluacion_gobernanza.confirmation_reason,
                validacion=ValidacionCalidad(approved=True, quality_score="HITL_PAUSE", numeric_score=0),
                costo_estimado=self.session_costs[session_id],
                persona_role="Strategic Governance Monitor"
            )
        
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
                memoria_episodica=history,
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
                validacion = ValidacionCalidad(approved=True, numeric_score=100, quality_score="Validation skipped")
                break

        # 6. ENSAMBLAJE FINAL
        final_text = validacion.correction if validacion.correction else feedback_explicador.analysis
        
        # Fallbacks for explanation and best practice if they are too short or empty
        explicacion = feedback_explicador.explanation
        if not explicacion or len(explicacion) < 10:
            print(" [Orchestrator] ⚠️ Pedagogical explanation was too short. Using technical explanation as fallback.")
            explicacion = evaluacion_analista.explanation
            
        mejor_practica = feedback_explicador.best_practice
        if not mejor_practica or len(mejor_practica) < 10:
            print(" [Orchestrator] ⚠️ Pedagogical best practice was too short. Using technical best practice as fallback.")
            mejor_practica = evaluacion_analista.best_practice

        res = FeedbackFinal(
            evaluacion=final_text,
            explicacion=explicacion,
            mejor_practica=mejor_practica,
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
             
        # 7. OUTPUT SANITIZATION (PII Masking)
        res.evaluacion = mask_pii(res.evaluacion)

        # 8. English-First Delivery: Translate back to user language if necessary
        if player_profile.language != "en":
            print(f" [Orchest] English-First Delivery: Translating result back to '{player_profile.language}'...")
            res.evaluacion = await self.translator.translate_to_user_language(res.evaluacion, player_profile.language)
            res.explicacion = await self.translator.translate_to_user_language(res.explicacion, player_profile.language)
            res.mejor_practica = await self.translator.translate_to_user_language(res.mejor_practica, player_profile.language)
            
            # Deep Translation for technical report
            await self._translate_deep(res, player_profile.language)

        # 9. PERSISTENCIA EN CACHÉ & MEMORIA (Artifact Index / Ground Truth Manager)
        # Extraer Evidence IDs y Hechos Verificados
        evidence_ids = re.findall(r"EV_[A-Z]+_\d+", str(res.evaluacion_tecnica.model_dump()))
        new_artifacts = []
        
        # Convert Evidence IDs to structured artifacts
        for eid in set(evidence_ids):
            new_artifacts.append({"fact": f"Evidence {eid} verified", "certainty": 100, "source": "tool"})
            
        # Add explicit verified artifacts from the agent
        if res.evaluacion_tecnica and hasattr(res.evaluacion_tecnica, "verified_artifacts") and res.evaluacion_tecnica.verified_artifacts:
            new_artifacts.extend([art.model_dump() for art in res.evaluacion_tecnica.verified_artifacts])
            
        if new_artifacts:
            print(f" [Orchest] 💾 Consolidating {len(new_artifacts)} artifacts into Ground Truth.")
            self.memory.update_artifact_index(session_id, new_artifacts)
            tracer.add_step("artifact_persistence", {"count": len(new_artifacts)})

        self.memory.save_step(session_id, {
            "decision": decision.model_dump(),
            "timestamp": datetime.now().isoformat(),
            "summary": res.evaluacion[:200] + "...",
            "snapshot": {
                "tecnico": res.evaluacion_tecnica.model_dump(),
                "gobernanza": res.evaluacion_gobernanza.model_dump() if res.evaluacion_gobernanza else None,
                "validacion": res.validacion.model_dump()
            }
        })
        
        # 10. CONTEXT COMPACTION (ACC - Adaptive Context Compaction)
        turn_count = self.memory.get_session_turn_count(session_id)
        token_count = self.memory.get_history_token_count(session_id)
        
        if turn_count >= 5 or token_count >= 3000:
            print(f" [Orchest] 🔄 Adaptive Context Compaction Triggered (Turns: {turn_count}, Tokens: ~{token_count}).")
            await self._compact_context(session_id, history)
            tracer.add_step("context_compaction", {"turn_count": turn_count, "token_count": token_count})


        if self.cache and validacion.approved:
            await self.cache.store(
                decision=decision.model_dump(),
                context=contexto.model_dump(),
                player_profile=player_profile.model_dump(),
                feedback=res
            )
        
        tracer.end_trace({"status": "success"})
        return res

    async def _compact_context(self, session_id: str, current_history: str):
        """
        Compresses the older session history while keeping the most recent steps.
        """
        prompt = f"""You are a Cybersecurity Memory Compactor.
Summarize the technical evolution of this investigation into a high-density executive summary.
Focus on:
1. Technical findings (Evidence IDs, IPs, hashes).
2. Decisions taken and their results.
3. Pending investigation vectors.

HISTORY TO COMPACT:
{current_history}

FINAL SUMMARY (English, max 200 words):
"""
        try:
            # Generate high-density summary
            summary = await self.llm.generate(prompt)
            
            # Persist summary
            self.memory.update_history_summary(session_id, summary)
            
            # INCREMENTAL COMPACTION: Keep last 3 steps for immediate context
            data = self.memory.load_session(session_id)
            if len(data["steps"]) > 3:
                print(f" [Orchest] ✂️ Truncating history: Keeping last 3 steps.")
                data["steps"] = data["steps"][-3:] 
            else:
                data["steps"] = []
                
            path = self.memory._get_path(session_id)
            with open(path, 'w') as f:
                import json
                json.dump(data, f, default=str, indent=2)
                
            print(f" [Orchest] ✅ Context compacted incrementally for {session_id}.")
        except Exception as e:
            print(f" [Orchest] ⚠️ Failed to compact context: {e}")


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

    async def confirmar_accion(
        self, 
        session_id: str, 
        justificacion: str, 
        player_profile: Optional[PlayerProfile] = None
    ) -> FeedbackFinal:
        """
        Resumes a paused evaluation after human justification.
        """
        print(f" [Orchestrator] Resuming action for session {session_id} with justification...")
        
        # 1. Load pending data
        pending = self.memory.load_pending_evaluation(session_id)
        if not pending:
            raise ValueError(f"No pending action found for session {session_id}")
            
        eval_analista = EvaluacionTecnica(**pending["analista"])
        eval_gobernanza = EvaluacionGobernanza(**pending["gobernanza"])
        
        # 2. Update context with justification for the Explainer
        self.memory.save_step(session_id, {
            "role": "player",
            "action": "JUSTIFICATION",
            "content": justificacion
        })
        
        # 3. Retrieve context bundle for the explainer (needed for RAG sources)
        history = self.memory.load_history(session_id)
        contexto_full_str = "Resumed after justification: " + justificacion
        
        # 4. Generate Pedagogical Feedback (Resuming Draft logic)
        feedback_explicador = await self.explainer_agent.generar(
            evaluacion_analista=eval_analista,
            evaluacion_gobernanza=eval_gobernanza,
            player_profile=player_profile or PlayerProfile(),
            contexto_rag=contexto_full_str,
            memoria_episodica=history,
            prev_inconsistencies=None
        )
        
        # 5. Final validation and return
        validacion = await self.validator_agent.validar(
            evaluacion_analista=eval_analista,
            feedback_explicador=feedback_explicador,
            player_profile=player_profile or PlayerProfile(),
            contexto_rag=contexto_full_str
        )
        
        # Final formatting
        return self._build_final_feedback(
            feedback_explicador, 
            eval_analista, 
            eval_gobernanza, 
            validacion, 
            session_id
        )

    def _build_final_feedback(self, explainer, analyst, governance, validation, session_id) -> FeedbackFinal:
        """Helper to create the final response object."""
        return FeedbackFinal(
            evaluacion=explainer.analysis,
            explicacion=explainer.explanation,
            mejor_practica=explainer.best_practice,
            fuentes_citadas=explainer.sources,
            evaluacion_tecnica=analyst,
            evaluacion_gobernanza=governance,
            status="success",
            pedagogical_feedback=explainer,
            validacion=validation,
            evaluacion_6d=validation.evaluacion_6d,
            costo_estimado=self.session_costs.get(session_id, 0.0),
            persona_role=validation.persona_role or "Senior SOC Analyst"
        )

    def obtener_auditoria(self, session_id: str) -> List[Dict[str, Any]]:
        """Recupera el historial de snapshots para auditoría forense."""
        return self.memory.get_audit_trail(session_id)