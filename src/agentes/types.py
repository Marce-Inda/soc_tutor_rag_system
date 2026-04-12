"""
Modelos de datos (Pydantic) para el sistema UEFS con RAG.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ============================================================================
# Modelos de Entrada
# ============================================================================

class Decision(BaseModel):
    """Decisión tomada por el jugador."""
    accion: str = Field(..., description="Acción realizada (ej: 'bloquear_ip', 'aislar_host')")
    target: str = Field(..., description="IP, hostname o sistema afectado")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    detalle: Optional[str] = Field(None, description="Detalles adicionales de la decisión")


class ContextoEscenario(BaseModel):
    """Contexto del escenario del juego."""
    tipo_incidente: str = Field(..., description="Tipo: phishing, ransomware, APT, etc.")
    fase: str = Field(..., description="Fase: detección, contención, erradicación, recuperación")
    sistemas_afectados: List[str] = Field(default_factory=list)
    score: int = Field(0, description="Score previo de la decisión")
    scenario_id: Optional[str] = None
    dificultad: Optional[str] = None


class PlayerProfile(BaseModel):
    """Perfil del jugador."""
    player_id: str
    level: int = Field(..., description="Nivel del jugador: 1 (junior) a 6 (expert)")
    rol: str = Field(default="analyst", description="analyst o ciso")
    language: str = Field(default="es", description="Idioma de entrega: es, pt, en")
    dilema_index_session: int = Field(0, description="Índice de dilema en la sesión actual")


class InputFeedbackRequest(BaseModel):
    """Request completo para generar feedback."""
    decision: Decision
    contexto: ContextoEscenario
    player_profile: PlayerProfile


# ============================================================================
# Modelos de Salida - Agente Analista
# ============================================================================

class EvaluacionTecnica(BaseModel):
    """Output del Agente Analista."""
    strengths: List[str] = Field(default_factory=list, alias="fortalezas")
    weaknesses: List[str] = Field(default_factory=list, alias="debilidades")
    evaluation: str = Field(..., description="Technical summary", alias="evaluacion")
    sources: List[str] = Field(default_factory=list, description="References (MITRE, NIST, etc.)", alias="fuentes")
    technical_score: int = Field(..., description="Calculated technical score (0-100)", alias="score_tecnico")
    forensic_notes: Optional[str] = Field(None, description="ISO 27037 compliance notes")

    class Config:
        populate_by_name = True



# ============================================================================
# Modelos de Salida - Agente de Gobernanza
# ============================================================================

class EvaluacionGobernanza(BaseModel):
    """Output del Agente de Gobernanza."""
    compliant: bool = Field(..., description="If the decision follows laws/ethics")
    risks: List[str] = Field(default_factory=list, description="Legal or ethical risks identified")
    recommendations: List[str] = Field(default_factory=list, description="Governance best practices")
    frameworks: List[str] = Field(default_factory=list, description="GDPR, Ley 25.326, etc.")


class FeedbackPedagogico(BaseModel):
    """Output del Agente Explicador."""
    analysis: str = Field(..., description="Natural language evaluation", alias="evaluacion")
    explanation: str = Field(..., description="Explanation of 'why'", alias="explicacion")
    best_practice: str = Field(..., description="Recommended best practice", alias="mejor_practica")
    cited_sources: List[str] = Field(default_factory=list, alias="fuentes_citadas")

    class Config:
        populate_by_name = True



# ============================================================================
# Modelos de Salida - Agente Validador
# ============================================================================

class ValidacionCalidad(BaseModel):
    """Output del Agente Validador."""
    approved: bool = Field(..., alias="aprobado")
    inconsistencies: List[str] = Field(default_factory=list, alias="inconsistencias")
    correction: Optional[str] = Field(None, description="Corrected feedback if issues found", alias="correccion")
    quality_score: str = Field(..., description="General quality note", alias="nota")
    numeric_score: int = Field(default=100, description="Quality score from 0 to 100")

    class Config:
        populate_by_name = True




# ============================================================================
# Modelos de Salida - Feedback Final
# ============================================================================

class FeedbackFinal(BaseModel):
    """Feedback final entregado al jugador."""
    evaluacion: str
    explicacion: str
    mejor_practica: str
    fuentes_citadas: List[str]
    evaluacion_tecnica: EvaluacionTecnica
    evaluacion_gobernanza: Optional[EvaluacionGobernanza] = None
    validacion: ValidacionCalidad
    costo_estimado: float = Field(..., description="Estimated cost in USD")



# ============================================================================
# Modelos para RAG
# ============================================================================

class RetrievalResult(BaseModel):
    """Resultado de retrieval del RAG."""
    docs: List[str] = Field(..., description="Documentos recuperados")
    fuentes: List[str] = Field(..., description="Nombres de las fuentes")
    score: List[float] = Field(default_factory=list, description="Scores de similaridad")