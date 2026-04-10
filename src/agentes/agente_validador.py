"""
Validator Agent - Quality verification for SOC Tutor feedback.
"""

from typing import Dict, Any

from ..agentes.types import (
    EvaluacionTecnica,
    FeedbackPedagogico,
    ValidacionCalidad,
    PlayerProfile
)


class AgenteValidador:
    """
    Validator Agent: Verifies the quality and consistency of the feedback.
    
    Responsibilities:
    - Verify absence of hallucinations.
    - Ensure consistency between technical evaluation and pedagogical feedback.
    - Validate appropriateness for the player's level.
    - Support multi-language validation (ES, PT, EN).
    """
    
    def __init__(self, llm_client, rag_client):
        self.llm = llm_client
        self.rag = rag_client
    
    def validar(
        self,
        evaluacion_analista: EvaluacionTecnica,
        feedback_explicador: FeedbackPedagogico,
        player_profile: PlayerProfile,
        contexto_rag: str = ""
    ) -> ValidacionCalidad:
        """Validates the generated feedback."""
        
        # 1. Validation with LLM (Dynamic and language-aware)
        prompt = self._build_prompt(
            evaluacion_analista,
            feedback_explicador,
            player_profile,
            contexto_rag
        )
        
        try:
            result = self.llm.generate_json(
                prompt=prompt
            )
            
            aprobado = result.get("aprobado", True)
            inconsistencias = result.get("inconsistencias", [])
            nota = result.get("nota", "Validation completed")
            
            return ValidacionCalidad(
                aprobado=aprobado,
                inconsistencias=inconsistencias,
                correccion=result.get("correcciones") if not aprobado else None,
                nota=nota
            )
            
        except Exception as e:
            print(f"  [Validator] Error: {e}")
            # Fallback: Accept with warning if LLM fails
            return ValidacionCalidad(
                aprobado=True,
                inconsistencias=["LLM Validation failed - manually audit required"],
                nota="Accepted by default after error"
            )
    
    def _build_prompt(
        self,
        evaluacion: EvaluacionTecnica,
        feedback: FeedbackPedagogico,
        profile: PlayerProfile,
        contexto_rag: str
    ) -> str:
        """Builds the validation prompt using central infrastructure."""
        from .prompts import build_prompt_validador
        
        return build_prompt_validador(
            evaluacion_analista=evaluacion.model_dump(),
            feedback_explicador=f"Evaluation: {feedback.evaluacion}\nExplanation: {feedback.explicacion}\nBest Practice: {feedback.mejor_practica}",
            player_level=profile.level,
            target_language=profile.language,
            contexto_rag=contexto_rag
        )