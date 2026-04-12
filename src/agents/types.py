"""
Pydantic data models for the UEFS system with RAG.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime


# ## MODELOS DE ENTRADA
# Estos modelos definen la estructura de los datos que recibe el sistema desde el juego.

class Decision(BaseModel):
    """Represents a technical decision made by the player in the simulator."""
    accion: str = Field(..., description="Action performed (e.g., 'block_ip', 'isolate_host')")
    target: str = Field(..., description="IP, hostname, or system affected by the decision")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    detalle: Optional[str] = Field(None, description="Additional contextual details")


class ContextoEscenario(BaseModel):
    """Context of the game scenario."""
    tipo_incidente: str = Field(..., description="Type: phishing, ransomware, APT, etc.")
    fase: str = Field(..., description="Phase: detection, containment, eradication, recovery")
    sistemas_afectados: List[str] = Field(default_factory=list)
    score: int = Field(0, description="Previous score of the decision")
    scenario_id: Optional[str] = None
    dificultad: Optional[str] = None


class PlayerProfile(BaseModel):
    """Profile of the player."""
    player_id: str
    level: int = Field(..., description="Player level: 1 (junior) to 6 (expert)")
    rol: str = Field(default="analyst", description="analyst or ciso")
    language: str = Field(default="es", description="Delivery language: es, pt, en")
    dilema_index_session: int = Field(0, description="Dilemma index in current session")


class InputFeedbackRequest(BaseModel):
    """Complete request to generate feedback."""
    decision: Decision
    contexto: ContextoEscenario
    player_profile: PlayerProfile


# ## MODELOS DE SALIDA - AGENTE ANALISTA
# Evaluación técnica detallada basada en marcos de referencia (NIST, MITRE).

class Score6D(BaseModel):
    """Integral evaluation model under the 6D standard (Technical, Strategic, Ethical, Communicative, Resilience, Learning)."""
    technical: int = Field(0, description="Correctness of technical incident response")
    strategic: int = Field(0, description="Business impact and recovery")
    ethical: int = Field(0, description="Legal compliance and ethical principles")
    communicative: int = Field(0, description="Efficiency of information sharing")
    resilience: int = Field(0, description="Ability to preserve evidence and recover systems")
    learning: int = Field(0, description="Knowledge application and pedagogical growth")

    class Config:
        populate_by_name = True

class EvaluacionTecnica(BaseModel):
    """Detailed result of the technical evaluation performed by the Analyst Agent."""
    analysis: str = Field(..., description="Technical reasoning of the finding")
    explanation: str = Field(..., description="Detailed technical explanation")
    best_practice: str = Field(..., description="Technical recommendation based on standards")
    sources: List[str] = Field(default_factory=list, description="References (MITRE, NIST, ISO, etc.)")
    technical_score: int = Field(..., description="Calculated technical score (0-100)")
    resilience_score: int = Field(default=0, description="Resilience and preservation score (ISO 27037)")
    forensic_notes: Optional[str] = Field(None, description="Forensic compliance notes")


    class Config:
        populate_by_name = True


# ## MODELOS DE SALIDA - AGENTE DE GOBERNANZA
# Evaluación de riesgos legales y cumplimiento normativo.

class EvaluacionGobernanza(BaseModel):
    """Output of the Governance Agent."""
    compliant: bool = Field(..., description="If the decision follows laws/ethics")
    risks: List[str] = Field(default_factory=list, description="Legal or ethical risks identified")
    recommendations: List[str] = Field(default_factory=list, description="Governance best practices")
    frameworks: List[str] = Field(default_factory=list, description="GDPR, Ley 25.326, etc.")
    strategic_score: int = Field(0, description="Business impact (0-100)")
    ethical_score: int = Field(0, description="Legal/Ethical risk (0-100)")


class FeedbackPedagogico(BaseModel):
    """Output of the Explainer Agent."""
    analysis: str = Field(..., description="Natural language evaluation")
    explanation: str = Field(..., description="Explanation of 'why'")
    best_practice: str = Field(..., description="Recommended best practice")
    cited_sources: List[str] = Field(default_factory=list)

    class Config:
        populate_by_name = True


# ## MODELOS DE SALIDA - AGENTE VALIDADOR
# Verificación de calidad y traducción final.

class ValidacionCalidad(BaseModel):
    """Output of the Validator Agent."""
    approved: bool
    inconsistencies: List[str] = Field(default_factory=list)
    correction: Optional[str] = Field(None, description="Corrected feedback if issues found")
    quality_score: str = Field(..., description="General quality note")
    numeric_score: int = Field(default=100, description="Quality score from 0 to 100")
    evaluacion_6d: Optional[Score6D] = None
    persona_role: Optional[str] = None

    class Config:
        populate_by_name = True


# ## MODELOS DE SALIDA - FEEDBACK FINAL
# Estructura del objeto final que se entrega al motor del juego.

class FeedbackFinal(BaseModel):
    """Final feedback delivered to the player."""
    evaluacion: str
    explicacion: str
    mejor_practica: str
    fuentes_citadas: List[str]
    evaluacion_tecnica: EvaluacionTecnica
    evaluacion_gobernanza: Optional[EvaluacionGobernanza] = None
    evaluacion_6d: Optional[Score6D] = None
    validacion: ValidacionCalidad
    costo_estimado: float = Field(..., description="Estimated cost in USD")
    persona_role: str = Field(default="Senior Analyst", description="Character role narrating the feedback")


# ## MODELOS PARA RAG
# Estructuras internas para la gestión del conocimiento recuperado.

class RetrievalResult(BaseModel):
    """Result of RAG retrieval."""
    docs: List[str] = Field(..., description="Retrieved documents")
    fuentes: List[str] = Field(..., description="Source names")
    score: List[float] = Field(default_factory=list, description="Similarity scores")