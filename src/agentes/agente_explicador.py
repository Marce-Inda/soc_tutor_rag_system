"""
Explainer Agent - Pedagogical feedback for SOC Tutor.
"""

from typing import Dict, Any
import json

from ..agentes.types import (
    EvaluacionTecnica,
    FeedbackPedagogico,
    PlayerProfile
)


class AgenteExplicador:
    """
    Explainer Agent: Translates technical evaluation into pedagogical feedback.
    
    Responsibilities:
    - Convert technical jargon into accessible explanations.
    - Provide educational context.
    - Adapt to the player's level (Junior vs. Senior).
    - Support localization in ES, PT, EN.
    """
    
    def __init__(self, llm_client, rag_client):
        self.llm = llm_client
        self.rag = rag_client
    
    def generar(
        self,
        evaluacion_analista: EvaluacionTecnica,
        player_profile: PlayerProfile,
        contexto_rag: str = ""
    ) -> FeedbackPedagogico:
        """Generates the pedagogical feedback."""
        
        # 1. Build prompt with pedagogical rules and language
        prompt = self._build_prompt(
            evaluacion_analista,
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
            evaluacion=result.get("evaluacion", "Evaluation not available"),
            explicacion=result.get("explicacion", "No explanation provided"),
            mejor_practica=result.get("mejor_practica", "Consult manual"),
            fuentes_citadas=result.get("fuentes_citadas", [])
        )
    
    def _build_prompt(
        self,
        evaluacion: EvaluacionTecnica,
        profile: PlayerProfile,
        contexto_rag: str
    ) -> str:
        """Builds the prompt using the central prompt infrastructure."""
        from .prompts import build_prompt_explicador
        
        return build_prompt_explicador(
            evaluacion_analista=evaluacion.model_dump(),
            player_level=profile.level,
            target_language=profile.language,
            dilemma_index=profile.dilema_index_session,
            contexto_rag=contexto_rag
        )
    
    def _fallback_feedback(self, evaluacion: EvaluacionTecnica, language: str) -> FeedbackPedagogico:
        """Language-adapted fallback feedback."""
        if language == "pt":
            return FeedbackPedagogico(
                evaluacion=f"Sua decisão teve uma pontuação de {evaluacion.score_tecnico}/100",
                explicacion="O sistema de feedback teve problemas técnicos.",
                mejor_practica="Consulte as melhores práticas de resposta a incidentes NIST 800-61",
                fuentes_citadas=["Fallback"]
            )
        elif language == "en":
            return FeedbackPedagogico(
                evaluacion=f"Your decision had a score of {evaluacion.score_tecnico}/100",
                explicacion="The feedback system encountered technical issues.",
                mejor_practica="Consult NIST 800-61 incident response best practices",
                fuentes_citadas=["Fallback"]
            )
        else: # es
            return FeedbackPedagogico(
                evaluacion=f"Tu decisión tuvo un score de {evaluacion.score_tecnico}/100",
                explicacion="El sistema de feedback tuvo problemas técnicos.",
                mejor_practica="Consulta las mejores prácticas de respuesta a incidentes NIST 800-61",
                fuentes_citadas=["Fallback"]
            )