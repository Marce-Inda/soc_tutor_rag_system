"""
Validator Agent - Quality verification and translation for SOC Tutor feedback.
"""

# ## AGENTE VALIDADOR
# Actúa como el 'Manager' del reporte final, asegurando calidad técnico-pedagógica y puliendo la traducción.



import re
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

    @staticmethod
    def _ensure_string(val: Any) -> str:
        """Converts any value to a safe string for Pydantic fields."""
        if isinstance(val, (dict, list)):
            return str(val)
        return str(val) if val is not None else ""
    
    async def validar(
        self,
        evaluacion_analista: EvaluacionTecnica,
        feedback_explicador: FeedbackPedagogico,
        player_profile: PlayerProfile,
        contexto_rag: str = ""
    ) -> ValidacionCalidad:
        """Validates the generated feedback with integrity checks."""
        
        # 0. INTEGRITY CHECK: Cross-reference hashes (Strict Integrity Mode)
        valid_hashes = re.findall(r"Hash: ([a-f0-9]+)", contexto_rag)
        integrity_warnings = []
        mismatches = 0
        
        for h in evaluacion_analista.source_integrity_hashes:
            if h not in valid_hashes:
                msg = f"Integrity violation: Cited hash {h[:16]}... not found in retrieved context."
                print(f"  [Validator] ⚠️ {msg}")
                integrity_warnings.append(msg)
                mismatches += 1
        
        # Penalización estricta: si >50% de los hashes citados no están en el contexto RAG,
        # el feedback pierde credibilidad y se marca como inconsistente.
        total_hashes = len(evaluacion_analista.source_integrity_hashes)
        integrity_compromised = total_hashes > 0 and (mismatches / total_hashes) > 0.5

        # 1. Validation with LLM (Dynamic and language-aware)
        prompt = self._build_prompt(
            evaluacion_analista,
            feedback_explicador,
            player_profile,
            contexto_rag
        )
        
        try:
            result = await self.llm.generate_json(
                prompt=prompt
            )
            
            approved = result.get("approved", True)
            inconsistencies = result.get("inconsistencies", [])
            quality_score = result.get("quality_score", "Validation completed")
            numeric_score = result.get("numeric_score", 100)

            # Aplicar penalización de integridad si hay compromiso
            if integrity_compromised:
                inconsistencies = integrity_warnings + inconsistencies
                numeric_score = max(0, numeric_score - 20)
                quality_score = f"{quality_score} [INTEGRITY PENALTY: -{mismatches} hash mismatches]"
                print(f"  [Validator] 🔴 Integrity penalty applied: {mismatches}/{total_hashes} hashes unverified. Score -20.")



            return ValidacionCalidad(
                approved=approved,
                inconsistencies=inconsistencies,
                correction=self._ensure_string(result.get("correction", result.get("correccion"))),
                quality_score=self._ensure_string(quality_score),
                numeric_score=numeric_score,
                evaluacion_6d=Score6D(**result.get("evaluacion_6d", {})) if result.get("evaluacion_6d") else None,
                persona_role=self._ensure_string(result.get("persona_role"))
            )
        except Exception as e:
            print(f"  [Validator] Error: {e}")
            # Fallback: Fail-Closed policy
            return ValidacionCalidad(
                approved=False,
                inconsistencies=["LLM Validation failed - system paused for safety"],
                quality_score="Blocked due to technical validation failure",
                numeric_score=0
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