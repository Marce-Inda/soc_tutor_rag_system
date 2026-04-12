"""
Explainer Agent - Pedagogical feedback and narrative generation for SOC Tutor.
"""

# ## AGENTE EXPLICADOR
# Traduce la evaluación técnica en un feedback narrativo y pedagógico.



from typing import Dict, Any
from ..agents.types import (
    EvaluacionTecnica,
    EvaluacionGobernanza,
    FeedbackPedagogico,
    PlayerProfile
)


class ExplainerAgent:

    """
    Explainer Agent: Translates technical evaluation into pedagogical feedback.
    """


    
    def __init__(self, llm_client, rag_client):
        self.llm = llm_client
        self.rag = rag_client
    
    def generar(
        self,
        evaluacion_analista: EvaluacionTecnica,
        evaluacion_gobernanza: EvaluacionGobernanza,
        player_profile: PlayerProfile,
        contexto_rag: str = ""
    ) -> FeedbackPedagogico:
        """Generates the pedagogical feedback."""
        
        # 1. Build prompt with pedagogical rules and language
        prompt = self._build_prompt(
            evaluacion_analista,
            evaluacion_gobernanza,
            player_profile,
            contexto_rag
        )
        
        # 2. Call the LLM
        try:
            # We use generate_json to get a structured response in the target language
            result = self.llm.generate_json(
                prompt=prompt
            )
        except Exception as e:
            print(f"  [Explainer] Error: {e}")
            return self._fallback_feedback(evaluacion_analista, player_profile.language)
        
        # 3. Parse response
        return FeedbackPedagogico(
            analysis=result.get("analysis", "Evaluation not available"),
            explanation=result.get("explanation", "No explanation provided"),
            best_practice=result.get("best_practice", "Consult manual"),
            cited_sources=result.get("cited_sources", [])
        )

    
    def _build_prompt(
        self,
        evaluacion_analista: EvaluacionTecnica,
        evaluacion_gobernanza: EvaluacionGobernanza,
        profile: PlayerProfile,
        contexto_rag: str
    ) -> str:
        """Builds the prompt using the central prompt infrastructure."""
        from .prompts import build_prompt_explicador
        
        return build_prompt_explicador(
            evaluacion_analista=evaluacion_analista.model_dump(),
            evaluacion_gobernanza=evaluacion_gobernanza.model_dump(),
            player_level=profile.level,
            target_language=profile.language,
            dilemma_index=profile.dilema_index_session,
            contexto_rag=contexto_rag
        )
    
    def _fallback_feedback(self, evaluacion: EvaluacionTecnica, language: str) -> FeedbackPedagogico:
        """Language-adapted fallback feedback."""
        if language == "pt":
            return FeedbackPedagogico(
                analysis=f"Sua decisão teve una pontuação de {evaluacion.technical_score}/100",
                explanation="O sistema de feedback teve problemas técnicos.",
                best_practice="Consulte as melhores práticas de resposta a incidentes NIST 800-61",
                cited_sources=["Fallback"]
            )
        elif language == "en":
            return FeedbackPedagogico(
                analysis=f"Your decision had a score of {evaluacion.technical_score}/100",
                explanation="The feedback system encountered technical issues.",
                best_practice="Consult NIST 800-61 incident response best practices",
                cited_sources=["Fallback"]
            )
        else: # es
            return FeedbackPedagogico(
                analysis=f"Tu decisión tuvo un score de {evaluacion.technical_score}/100",
                explanation="El sistema de feedback tuvo problemas técnicos.",
                best_practice="Consulta las mejores prácticas de respuesta a incidentes NIST 800-61",
                cited_sources=["Fallback"]
            )