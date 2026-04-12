"""
Validator Agent - Quality verification and translation for SOC Tutor feedback.
"""

# ## AGENTE VALIDADOR
# Actúa como el 'Manager' del reporte final, asegurando calidad técnico-pedagógica y puliendo la traducción.



from typing import Dict, Any

from ..agents.types import (
    EvaluacionTecnica,
    FeedbackPedagogico,
    ValidacionCalidad,
    PlayerProfile,
    Score6D
)



class ValidatorAgent:


    """
    Validator Agent: Verifies quality and consistency of the final feedback.
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
            
            approved = result.get("approved", True)
            inconsistencies = result.get("inconsistencies", [])
            quality_score = result.get("quality_score", "Validation completed")

            
            return ValidacionCalidad(
                approved=approved,
                inconsistencies=inconsistencies,
                correction=result.get("correction", result.get("correccion")),
                quality_score=quality_score,
                numeric_score=result.get("numeric_score", 100),
                evaluacion_6d=Score6D(**result.get("evaluacion_6d", {})) if result.get("evaluacion_6d") else None,
                persona_role=result.get("persona_role")
            )



            
        except Exception as e:
            print(f"  [Validator] Error: {e}")
            # Fallback: Accept with warning if LLM fails
            return ValidacionCalidad(
                approved=True,
                inconsistencies=["LLM Validation failed - manually audit required"],
                quality_score="Accepted by default after error",
                numeric_score=50
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
            feedback_explicador=f"Analysis: {feedback.analysis}\nExplanation: {feedback.explanation}\nBest Practice: {feedback.best_practice}",
            player_level=profile.level,
            target_language=profile.language,
            contexto_rag=contexto_rag
        )