"""
Inicialización del paquete SOC Tutor RAG System.
"""

from pathlib import Path

# Agregar parent al path para imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Versión
__version__ = "1.0.0"
__author__ = "Marcela Rosana Inda"

# Exports principales
from src.agentes.types import (
    Decision,
    ContextoEscenario,
    PlayerProfile,
    FeedbackFinal,
    InputFeedbackRequest
)

from src.orchest.uefs_orchestrator import UEFSOrchestrator

__all__ = [
    "Decision",
    "ContextoEscenario", 
    "PlayerProfile",
    "FeedbackFinal",
    "InputFeedbackRequest",
    "UEFSOrchestrator",
]