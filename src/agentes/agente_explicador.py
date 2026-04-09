"""
Agente Explicador - Feedback pedagógico.
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
    Agente Explicador: Traduce la evaluación técnica en feedback pedagógico.
    
    Responsabilidades:
    - Convertir jerga técnica en explicaciones accesibles
    - Proporcionar contexto educativo
    - Adaptar al nivel del jugador (junior vs CISO)
    - Generar ejemplos prácticos
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
        """Genera el feedback pedagógico."""
        
        # 1. Aplicar reglas pedagógicas según nivel
        reglas_pedagogicas = self._get_reglas_pedagogicas(
            player_profile.level,
            player_profile.dilema_index_session
        )
        
        # 2. Construir prompt con reglas pedagógicas
        prompt = self._build_prompt(
            evaluacion_analista,
            player_profile,
            reglas_pedagogicas,
            contexto_rag
        )
        
        # 3. Llamar al LLM
        try:
            result = self.llm.generate_json(
                prompt=prompt,
                system_prompt=self._get_system_prompt()
            )
        except Exception as e:
            print(f"Error en Agente Explicador: {e}")
            return self._fallback_feedback(evaluacion_analista)
        
        # 4. Parsear respuesta
        return FeedbackPedagogico(
            evaluacion=result.get("evaluacion", "Evaluación no disponible"),
            explicacion=result.get("explicacion", "Sin explicación"),
            mejor_practica=result.get("mejor_practica", "Consultar manual"),
            fuentes_citadas=result.get("fuentes_citadas", [])
        )
    
    def _get_reglas_pedagogicas(self, level: int, dilema_index: int) -> str:
        """Determina las reglas pedagógicas según el perfil."""
        if level == 1 and dilema_index <= 3:
            return """
REGLA ACTIVA (Early Wins - Principiante):
- El jugador es principiante. ESTÁ PROHIBIDO ser destructivo.
- SIEMPRE empieza con refuerzo positivo ("Buen instinto", "Notaste lo importante")
- Limita las mejoras a MÁXIMO 1 concepto. No lo abrumes.
- Usa lenguaje accesible, evita jerga técnica excesiva.
"""
        elif level >= 5:
            return """
REGLA ACTIVA (CISO/Senior):
- Sé directo y corporativo. No uses cumplidos vacíos.
- Enfoca la 'Mejor Práctica' en impacto de negocio, SLA, cumplimiento normativo.
- Incluye consideraciones de comunicación a directivos/board.
- Mention regulatory implications (LGPD, GDPR, etc.)
"""
        else:
            return """
REGLA ACTIVA (Intermedio):
- Equilibra feedback positivo y constructivo.
- Explica el "por qué" técnica y pedagógicamente.
- Proporciona contexto sin ser abrumador.
"""
    
    def _build_prompt(
        self,
        evaluacion: EvaluacionTecnica,
        profile: PlayerProfile,
        reglas: str,
        contexto_rag: str
    ) -> str:
        """Construye el prompt."""
        return f"""Eres un Instructor generando feedback pedagógico para un juego de ciberseguridad.

EVALUACIÓN DEL ANALISTA:
- Fortalezas: {', '.join(evaluacion.fortalezas) if evaluacion.fortalezas else 'Ninguna'}
- Debilidades: {', '.join(evaluacion.debilidades) if evaluacion.debilidades else 'Ninguna'}
- Evaluación: {evaluacion.evaluacion}
- Score técnico: {evaluacion.score_tecnico}/100
- Fuentes: {', '.join(evaluacion.fuentes) if evaluacion.fuentes else 'Ninguna'}

PERFIL DEL JUGADOR:
- Nivel: {profile.level} (1=Junior, 5+=CISO/Senior)
- Rol: {profile.rol}
- Índice de dilema en sesión: {profile.dilema_index_session}

{reglas}

CONOCIMIENTO RAG:
{contexto_rag if contexto_rag else "Sin contexto RAG disponible"}

Responde en JSON con:
{{
  "evaluacion": "feedback de evaluación en lenguaje natural",
  "explicacion": "explicación del 'por qué' de la decisión",
  "mejor_practica": "best practice recomendada",
  "fuentes_citadas": ["referencias a fuentes"]
}}
"""
    
    def _get_system_prompt(self) -> str:
        """System prompt del agente."""
        return """Eres un Instructor experto en ciberseguridad especializado en pedagogía.
Tu tarea es traducir evaluaciones técnicas en feedback accionable y efectivo.

CARACTERÍSTICAS:
- Feedback constructivo, nunca destructivo
- Adapta el lenguaje al nivel del jugador
- Usa formato markdown
- Incluye siempre una "mejor práctica" accionable"""
    
    def _fallback_feedback(self, evaluacion: EvaluacionTecnica) -> FeedbackPedagogico:
        """Feedback de fallback."""
        return FeedbackPedagogico(
            evaluacion=f"Tu decisión tuvo un score de {evaluacion.score_tecnico}/100",
            explicacion="El sistema de feedback tuvo problemas técnicos.",
            mejor_practica="Consulta las mejores prácticas de respuesta a incidentes NIST 800-61",
            fuentes_citadas=["Fallback"]
        )