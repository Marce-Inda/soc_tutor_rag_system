"""
FastAPI Application - SOC Tutor RAG System
API para servir el sistema de feedback.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os

# Importar tipos
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agentes.types import (
    Decision,
    ContextoEscenario,
    PlayerProfile,
    FeedbackFinal
)

# Inicializar app
app = FastAPI(
    title="SOC Tutor RAG API",
    description="Sistema multiagente de feedback pedagógico con RAG para ciberseguridad",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de request/response
class FeedbackRequest(BaseModel):
    decision: Decision
    contexto: ContextoEscenario
    player_profile: PlayerProfile


class FeedbackResponse(BaseModel):
    evaluacion: str
    explicacion: str
    mejor_practica: str
    fuentes_citadas: List[str]
    score_tecnico: int
    aprobado: bool
    costo_estimado: float


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    rag_documents: int


# Variables globales
_llm_client = None
_rag_client = None
_orchestrator = None


def get_orchestrator():
    """Inicializa el orquestador lazy."""
    global _llm_client, _rag_client, _orchestrator
    
    if _orchestrator is None:
        # Verificar API keys
        if not os.getenv("GEMINI_API_KEY") and not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("API keys no configuradas")
        
        # Importar aquí para evitar errores si no están instalados
        try:
            from 03_configuracion_de_modelos.llm_client import LLMClient
            from 04_integracion_de_herramientas.rag_client import RAGClient
            from src.orchest.uefs_orchestrator import UEFSOrchestrator
            
            _llm_client = LLMClient()
            _rag_client = RAGClient()
            _orchestrator = UEFSOrchestrator(_llm_client, _rag_client)
        except ImportError as e:
            raise RuntimeError(f"Dependencias no instaladas: {e}")
    
    return _orchestrator


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "SOC Tutor RAG API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint."""
    orch = get_orchestrator()
    health_info = orch.health_check()
    
    return HealthResponse(
        status="healthy",
        llm_provider=health_info["llm_provider"],
        rag_documents=health_info["rag_documents"]
    )


@app.post("/feedback", response_model=FeedbackResponse)
def generar_feedback(request: FeedbackRequest):
    """Genera feedback para una decisión del jugador."""
    
    try:
        orchestrator = get_orchestrator()
        
        # Generar feedback
        feedback = orchestrator.generar_feedback(
            decision=request.decision,
            contexto=request.contexto,
            player_profile=request.player_profile
        )
        
        # Mapear respuesta
        return FeedbackResponse(
            evaluacion=feedback.evaluacion,
            explicacion=feedback.explicacion,
            mejor_practica=feedback.mejor_practica,
            fuentes_citadas=feedback.fuentes_citadas,
            score_tecnico=feedback.evaluacion_tecnica.score_tecnico,
            aprobado=feedback.validacion.aprobado,
            costo_estimado=feedback.costo_estimado
        )
        
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/stats")
def stats():
    """Estadísticas del sistema."""
    orch = get_orchestrator()
    health = orch.health_check()
    
    return {
        "llm_provider": health["llm_provider"],
        "documents_indexed": health["rag_documents"],
        "validation_enabled": health["validation_enabled"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)