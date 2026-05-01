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

    
    def generar_feedback(
        self,
        decision: Decision,
        contexto: ContextoEscenario,
        player_profile: PlayerProfile,
        session_id: str = "sesion-default"
    ) -> FeedbackFinal:
        """
        Flujo Maestro con loop de corrección (Manager of Drafts).
        """
        
        tracer.start_trace("evaluacion_integral_maestra", {
            "accion": decision.accion,
            "session_isolation": "enabled"
        })
        
        # Inicializar tracking de costos para esta sesión si no existe
        if session_id not in self.session_costs:
            self.session_costs[session_id] = 0.0
        
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
            turns = self.memory.get_session_turn_count(session_id)
            if turns >= self.MAX_TURNS_PER_SESSION:
                 return self._get_safe_block_response("Session turn limit reached. Please start a new simulation.")

            # Check Cost limits
            if self.session_costs[session_id] >= self.MAX_COST_PER_SESSION:
                 return self._get_safe_block_response("API Budget exceeded for this session. Please contact support.")

            is_safe, error_msg = self.guard.validate_input(decision)
            if not is_safe:
                tracer.end_trace({"error": error_msg}, status="blocked")
                if error_msg == "L2_API_ERROR":
                    return self._get_api_error_response()
                return self._get_safe_block_response("Action could not be processed due to security policies.")
        except Exception as e:
            tracer.add_step("guard_error", {"error": str(e)})
            return self._get_api_error_response()

        
        # Recuperar Memoria Episódica
        history = self.memory.get_history_summary(session_id)
        
        # 2.5 PMS 2.0: ENRUTAMIENTO METACOGNITIVO (Fast Path vs Deep Reasoning)
        # Si es una pregunta teórica pura o saludo, la derivamos por un Fast Path para ahorrar cómputo
        # Aquí implementamos un triage heurístico simplificado
        accion_lower = decision.accion.lower()
        is_theoretical = decision.target.lower() in ["none", "", "tutor", "teoria"] and (
            any(kw in accion_lower for kw in ["que es", "explicame", "como funciona", "diferencia entre", "hola"])
        )
        
        if is_theoretical:
            print(" [PMS 2.0] Triage: Theoretical question detected. Routing to Fast Path (System-1).")
            tracer.add_step("PMS_2.0_Routing", {"route": "Fast Path", "reason": "Theoretical input"})
            
            # Recuperar solo contexto RAG estratégico/teórico rápido
            rag_rapido = self.rag.retrieve_hybrid(query=decision.accion, k=2, translate=True)
            contexto_str = "\n".join([d['text'] for d in rag_rapido])
            
            # Generar respuesta rápida con modelo barato
            try:
                prompt = f"Como tutor de ciberseguridad, responde brevemente a esto: '{decision.accion}'. Usa este contexto si ayuda: {contexto_str}"
                respuesta_rapida = self.llm.generate(prompt)
            except Exception as e:
                tracer.add_step("fast_path_error", {"error": str(e)})
                return self._get_api_error_response()
            
            res = FeedbackFinal(
                evaluacion=respuesta_rapida,
                explicacion="Respuesta rápida generada vía Fast Path (PMS 2.0).",
                mejor_practica="Sigue preguntando dudas teóricas.",
                fuentes_citadas=[d['source'] for d in rag_rapido],
                evaluacion_tecnica=EvaluacionTecnica(analysis="Fast Path", explanation="", best_practice="", sources=[], technical_score=100),
                evaluacion_gobernanza=EvaluacionGobernanza(compliant=True, risks=[], recommendations=[], frameworks=[], strategic_score=100, ethical_score=100),
                validacion=ValidacionCalidad(approved=True, inconsistencies=[], quality_score="Fast Path", numeric_score=100),
                costo_estimado=self.llm.last_usage.get("cost", 0.0001),
                persona_role="Tutor"
            )
            
            # 6.5 OUTPUT SECURITY CHECK (L3) para Fast Path
            if not self.guard.validate_output(res.evaluacion):
                 return self._get_safe_block_response("Integrity check failed for the generated response.")
                 
            # Guardar en memoria para mantener el Timeline coherente
            self.memory.save_step(session_id, {
                "decision": decision.model_dump(),
                "timestamp": datetime.now().isoformat()
            })
            
            return res
        
        print(" [PMS 2.0] Triage: Tactical action detected. Routing to Deep Reasoning (System-2).")
        
        # 3. RAG - Differentiated Retrieval (Performance Hub)
        if contexto.scenario_id:
            self.tools.set_scenario(contexto.scenario_id)

        print(f" [Orchestrator] Retrieving differentiated RAG context...")
        
        # Technical RAG (For Analyst) - k=2 to reduce bloat
        rag_tecnico = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=2,
            knowledge_type="technical"
        )
        
        # Strategic RAG (For Governance/Explainer) - k=2
        rag_estrategico = self.rag.retrieve_with_context(
            decision=decision.model_dump(),
            contexto=contexto.model_dump(),
            k=2,
            knowledge_type="strategic"
        )
        
        # Assemble filtered contexts
        def format_context(docs):
            parts = []
            for i, d in enumerate(docs):
                content = d.get('text', '')
                if len(content) > 1200: # Slightly more aggressive truncation
                    content = content[:1200] + "... [TRUNCATED]"
                
                prefix = "[MATCH EXACTO]" if d.get('is_exact') else f"[RELEVANCIA {i+1}]"
                doc_id = d.get('id', 'no-id')[:16]
                parts.append(f"{prefix} (Source: {d['source']} | Hash: {doc_id}): {content}")
            return "\n\n".join(parts)

        contexto_tecnico_str = format_context(rag_tecnico.get('documentos_recuperados', []))
        contexto_estrategico_str = format_context(rag_estrategico.get('documentos_recuperados', []))
        
        # Combined for Explainer/Validator
        contexto_full_str = f"--- TECHNICAL CONTEXT ---\n{contexto_tecnico_str}\n\n--- STRATEGIC/LEGAL CONTEXT ---\n{contexto_estrategico_str}"
        
        # 4. ANALYST DUO (Technical + Governance)
        print(f" [Orchestrator] Running parallel evaluations...")
        # Analyst only gets technical context and episodic memory
        evaluacion_analista = self.analyst_agent.evaluar(decision, contexto, contexto_rag=contexto_tecnico_str, memoria_episodica=history)
        self.session_costs[session_id] += self.llm.last_usage.get("cost", 0.0)
        
        # Governance only gets strategic/legal context
        evaluacion_gobernanza = self.governance_agent.evaluar(decision, contexto, contexto_rag=contexto_estrategico_str)
        self.session_costs[session_id] += self.llm.last_usage.get("cost", 0.0)
        
        # 5. GENERACIÓN Y VALIDACIÓN (Manager of Drafts Loop)
        max_retries = 1
        current_retry = 0
        feedback_explicador = None
        validacion = None
        
        while current_retry <= max_retries:
            print(f" [Orchestrator] Generating pedagogical feedback (Draft {current_retry + 1})...")
            
            # El Explainer usa contexto completo para narrar el choque asimétrico
            feedback_explicador = self.explainer_agent.generar(
                evaluacion_analista=evaluacion_analista,
                evaluacion_gobernanza=evaluacion_gobernanza,
                player_profile=player_profile,
                contexto_rag=contexto_full_str
            )
            self.session_costs[session_id] += self.llm.last_usage.get("cost", 0.0)
            
            # El Validador traduce y pule (solo si está habilitado)
            if self.enable_validation:
                validacion = self.validator_agent.validar(
                    evaluacion_analista=evaluacion_analista,
                    feedback_explicador=feedback_explicador,
                    player_profile=player_profile,
                    contexto_rag=contexto_full_str
                )
                self.session_costs[session_id] += self.llm.last_usage.get("cost", 0.0)

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
            fuentes_citadas=rag_tecnico.get("sources", []) + rag_estrategico.get("sources", []) + feedback_explicador.cited_sources,
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


        
        # 7. MEMORY & CACHE
        self.memory.save_step(session_id, {
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