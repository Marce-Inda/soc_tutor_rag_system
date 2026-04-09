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
    fortalezas: List[str] = Field(default_factory=list)
    debilidades: List[str] = Field(default_factory=list)
    evaluacion: str = Field(..., description="Evaluación resumida")
    fuentes: List[str] = Field(default_factory=list, description="Referencias (MITRE, NIST, etc.)")
    score_tecnico: int = Field(..., description="Score técnico calculado (0-100)")


# ============================================================================
# Modelos de Salida - Agente Explicador
# ============================================================================

class FeedbackPedagogico(BaseModel):
    """Output del Agente Explicador."""
    evaluacion: str = Field(..., description="Evaluación en lenguaje natural")
    explicacion: str = Field(..., description="Explicación del 'por qué'")
    mejor_practica: str = Field(..., description="Best Practice recomendada")
    fuentes_citadas: List[str] = Field(default_factory=list)


# ============================================================================
# Modelos de Salida - Agente Validador
# ============================================================================

class ValidacionCalidad(BaseModel):
    """Output del Agente Validador."""
    aprobado: bool
    inconsistencias: List[str] = Field(default_factory=list)
    correccion: Optional[str] = Field(None, description="Feedback corregido si hay problemas")
    nota: str = Field(..., description="Nota general de calidad")


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
    validacion: ValidacionCalidad
    costo_estimado: float = Field(..., description="Costo en USD de la generación")


# ============================================================================
# Modelos para RAG
# ============================================================================

class RetrievalResult(BaseModel):
    """Resultado de retrieval del RAG."""
    docs: List[str] = Field(..., description="Documentos recuperados")
    fuentes: List[str] = Field(..., description="Nombres de las fuentes")
    score: List[float] = Field(default_factory=list, description="Scores de similaridad")