"""
FastAPI Application - SOC Tutor RAG System
API para servir el sistema de feedback.
"""

import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import os
from .queue_manager import QueueManager, QueueStatus

# Importar tipos
import sys
from pathlib import Path
# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.types import (
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

# --- OBSERVABILIDAD JERÁRQUICA (OpenTelemetry + Phoenix) ---
# Cumpliendo con el estándar de observabilidad de IA: Trazas > Logs > Métricas
try:
    from phoenix.otel import register
    from openinference.instrumentation.langchain import LangChainInstrumentor
    
    otel_endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:4318/v1/traces")
    
    tracer_provider = register(
        project_name="soc-tutor-agent",
        endpoint=otel_endpoint,
    )
    LangChainInstrumentor().instrument(
        tracer_provider=tracer_provider
    )
    print(f"✅ Observabilidad OTel activada. Enviando trazas a: {otel_endpoint}")
except ImportError:
    print("⚠️ Módulos de Phoenix no instalados. Saltando instrumentación (requiere arize-phoenix).")
except Exception as e:
    print(f"⚠️ Error al inicializar OpenTelemetry: {e}")
# -----------------------------------------------------------

# CORS - Security: Orígenes restringidos (Principio de Mínimos Permisos)
ALLOWED_ORIGINS = [
    "http://localhost:3000",           # Frontend dev local
    "http://localhost:3001",           # Frontend dev alternativo (recording)
    "http://soc-tutor-frontend:3000",  # Frontend Docker interno
]

# Agregar FRONTEND_URL dinámica desde entorno de producción
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    # Permitimos separar múltiples URLs por comas si es necesario
    for url in frontend_url.split(","):
        ALLOWED_ORIGINS.append(url.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
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
    score_tecnico: float
    persona_role: str = "Mentor (Analista L2)"
    evaluacion_gobernanza: Optional[Dict[str, Any]] = None
    aprobado: bool
    costo_estimado: float
    total_tokens: int
    latencia_ms: float
    rag_precision: float
    status: str = "success"
    requires_hitl: bool = False
    hitl_message: Optional[str] = None

class ConfirmationRequest(BaseModel):
    session_id: str
    justificacion: str
    player_profile: Optional[PlayerProfile] = None


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    rag_documents: int


# Variables globales
_llm_client = None
_rag_client = None
_orchestrator = None
queue_manager = QueueManager(max_concurrent=2)


def get_orchestrator():
    """Inicializa el orquestador lazy."""
    global _llm_client, _rag_client, _orchestrator
    
    if _orchestrator is None:
        # Verificar API keys
        if not os.getenv("GEMINI_API_KEY") and not os.getenv("GROQ_API_KEY"):
            raise RuntimeError("API keys no configuradas")
        
        # Importar aquí para evitar errores si no están instalados
        try:
            from src.utils.llm_client import LLMClient
            from src.rag.rag_client import RAGClient
            from src.orchest.uefs_orchestrator import UEFSOrchestrator
            
            _llm_client = LLMClient(provider="gemini")
            _rag_client = RAGClient()
            
            # ASYMMETRIC SUPREME JUDGE: Priorizamos modelos de alta capacidad para validación.
            # Orden de prioridad: NVIDIA NIM (405B) -> DeepSeek -> Groq
            if os.getenv("NVIDIA_API_KEY"):
                print(" [Main] 🛡️ NVIDIA NIM (Llama-3.3-70B) activado como Juez Supremo.")
                _validator_llm_client = LLMClient(provider="nvidia", model="meta/llama-3.3-70b-instruct")
            elif os.getenv("DEEPSEEK_API_KEY"):
                print(" [Main] 🛡️ DeepSeek Supremo activado para validación de calidad.")
                _validator_llm_client = LLMClient(provider="deepseek")
            elif os.getenv("GROQ_API_KEY"):
                print(" [Main] ⚖️ Groq activado como Juez Asimétrico.")
                _validator_llm_client = LLMClient(provider="groq")
            else:
                _validator_llm_client = None
            
            _orchestrator = UEFSOrchestrator(
                llm_client=_llm_client, 
                rag_client=_rag_client,
                validator_llm_client=_validator_llm_client
            )
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


@app.get("/queue/status/{user_id}", response_model=QueueStatus)
def get_queue_status(user_id: str):
    """Obtiene el estado del usuario en la cola."""
    return queue_manager.get_user_status(user_id)


@app.post("/queue/heartbeat/{user_id}")
def heartbeat(user_id: str):
    """Mantiene activa la sesión del usuario."""
    return queue_manager.heartbeat(user_id)


@app.post("/feedback", response_model=FeedbackResponse)
async def generar_feedback(request: FeedbackRequest, user_id: str = "guest"):
    """Genera feedback para una decisión del jugador de forma asíncrona."""
    
    # Security: Validar formato de user_id
    if not re.match(r'^[a-zA-Z0-9_-]{1,64}$', user_id):
        raise HTTPException(status_code=400, detail="Identificador de usuario inválido.")
    
    # Validar que el usuario esté activo en la cola
    status = queue_manager.get_user_status(user_id)
    if status.status != "ACTIVE":
        raise HTTPException(
            status_code=429, 
            detail=f"Debe esperar su turno en la lista de espera. Posición: {status.position}"
        )

    try:
        orchestrator = get_orchestrator()
        
        # Generar feedback asíncronamente
        feedback = await orchestrator.generar_feedback(
            decision=request.decision,
            contexto=request.contexto,
            player_profile=request.player_profile
        )
        
        # Expulsión forzada de jugadores zombies
        if "API Budget exceeded" in feedback.evaluacion or "Session turn limit" in feedback.evaluacion:
            queue_manager.expel_user(user_id)
            
        # Mapear respuesta
        gov_eval = (
            feedback.evaluacion_gobernanza.model_dump() 
            if feedback.evaluacion_gobernanza 
            else None
        )
        return FeedbackResponse(
            evaluacion=feedback.evaluacion,
            explicacion=feedback.explicacion,
            mejor_practica=feedback.mejor_practica,
            fuentes_citadas=feedback.fuentes_citadas,
            score_tecnico=feedback.evaluacion_tecnica.technical_score if feedback.evaluacion_tecnica else 0,
            persona_role=feedback.persona_role if hasattr(feedback, 'persona_role') and feedback.persona_role else "SISTEMA MENTOR",
            evaluacion_gobernanza=gov_eval,
            aprobado=feedback.validacion.approved if feedback.validacion else True,
            costo_estimado=feedback.costo_estimado,
            total_tokens=feedback.total_tokens,
            latencia_ms=feedback.latencia_ms,
            rag_precision=feedback.rag_precision,
            status=feedback.status,
            requires_hitl=feedback.requires_hitl,
            hitl_message=feedback.hitl_message
        )
        
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        import traceback
        print(f"Error en feedback endpoint: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.post("/confirm", response_model=FeedbackResponse)
async def confirmar_accion(request: ConfirmationRequest, user_id: str = "guest"):
    """Reanuda una evaluación pausada por HITL tras la justificación del jugador."""
    try:
        orchestrator = get_orchestrator()
        feedback = await orchestrator.confirmar_accion(
            session_id=request.session_id,
            justificacion=request.justificacion,
            player_profile=request.player_profile
        )
        
        gov_eval = feedback.evaluacion_gobernanza.model_dump() if feedback.evaluacion_gobernanza else None
        
        return FeedbackResponse(
            evaluacion=feedback.evaluacion,
            explicacion=feedback.explicacion,
            mejor_practica=feedback.mejor_practica,
            fuentes_citadas=feedback.fuentes_citadas,
            score_tecnico=feedback.evaluacion_tecnica.technical_score if feedback.evaluacion_tecnica else 0,
            persona_role=feedback.persona_role or "Gobernanza Confirmada",
            evaluacion_gobernanza=gov_eval,
            aprobado=True,
            costo_estimado=feedback.costo_estimado,
            total_tokens=feedback.total_tokens,
            latencia_ms=feedback.latencia_ms,
            rag_precision=feedback.rag_precision,
            status="success",
            requires_hitl=False
        )
    except Exception as e:
        print(f"Error en confirm endpoint: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/audit/{user_id}")
async def audit_session(user_id: str):
    """Devuelve el historial técnico completo de la sesión para auditoría forense."""
    try:
        orchestrator = get_orchestrator()
        audit_trail = orchestrator.obtener_auditoria(user_id)
        return {"session_id": user_id, "audit_trail": audit_trail}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Sesión no encontrada o error: {str(e)}")


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
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7860")))