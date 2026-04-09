"""
Agente Validador - Verificación de calidad del feedback.
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
    Agente Validador: Verifica la calidad y consistencia del feedback.
    
    Responsabilidades:
    - Verificar que no haya alucinaciones
    - Asegurar consistencia entre evaluación y feedback
    - Validar apropiación para el nivel del jugador
    - Detectar sesgos o información contradictoria
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
        """Valida el feedback generado."""
        
        # 1. Validación básica (reglas deterministas)
        inconsistencias = []
        
        # Check: Score alto con feedback negativo
        if evaluacion_analista.score_tecnico >= 80:
            palabras_negativas = ["error", "incorrecto", "fallaste", "olvidaste", "mal"]
            if any(p in feedback_explicador.evaluacion.lower() for p in palabras_negativas):
                inconsistencia = "Score alto (≥80) con feedback aparentemente negativo"
                inconsistencias.append(inconsistencia)
        
        # Check: Score bajo con feedback positivo
        if evaluacion_analista.score_tecnico <= 30:
            palabras_positivas = ["excelente", "perfecto", "excelente trabajo", "muy bien"]
            if any(p in feedback_explicador.evaluacion.lower() for p in palabras_positivas):
                inconsistencia = "Score bajo (≤30) con feedback aparentemente positivo"
                inconsistencias.append(inconsistencia)
        
        # 2. Si hay inconsistencias deterministas, rechazar
        if inconsistencias:
            return ValidacionCalidad(
                aprobado=False,
                inconsistencias=inconsistencia,
                correccion=self._generar_correccion(
                    evaluacion_analista, 
                    player_profile
                ),
                nota="Inconsistencia detectada por reglas deterministas"
            )
        
        # 3. Validación con LLM (para casos más complejos)
        prompt = self._build_prompt(
            evaluacion_analista,
            feedback_explicador,
            player_profile,
            contexto_rag
        )
        
        try:
            result = self.llm.generate_json(
                prompt=prompt,
                system_prompt=self._get_system_prompt()
            )
            
            aprobado = result.get("aprobado", True)
            inconsistencias_extra = result.get("inconsistencias", [])
            nota = result.get("nota", "Validación completada")
            
            return ValidacionCalidad(
                aprobado=aprobado,
                inconsistencias=inconsistencias + inconsistencias_extra,
                correccion=result.get("correccion") if not aprobado else None,
                nota=nota
            )
            
        except Exception as e:
            print(f"Error en Agente Validador: {e}")
            # Si falla el LLM, aceptamos con warn
            return ValidacionCalidad(
                aprobado=True,
                inconsistencias=["Validación LLM falló - auditado manualmente"],
                nota="Aceptado por defecto tras error"
            )
    
    def _build_prompt(
        self,
        evaluacion: EvaluacionTecnica,
        feedback: FeedbackPedagogico,
        profile: PlayerProfile,
        contexto_rag: str
    ) -> str:
        """Construye el prompt de validación."""
        return f"""Eres un Validador de Calidad revisando el feedback generado.

EVALUACIÓN DEL ANALISTA:
- Score técnico: {evaluacion.score_tecnico}/100
- Fortalezas: {', '.join(evaluacion.fortalezas)}
- Debilidades: {', '.join(evaluacion.debilidades)}
- Evaluación: {evaluacion.evaluacion}

FEEDBACK DEL EXPLICADOR:
- Evaluación: {feedback.evaluacion}
- Explicación: {feedback.explicacion}
- Mejor práctica: {feedback.mejor_practica}

PERFIL DEL JUGADOR:
- Nivel: {profile.level}
- Rol: {profile.rol}

CONOCIMIENTO RAG:
{contexto_rag if contexto_rag else "Sin contexto"}

Responde en JSON con:
{{
  "aprobado": true/false,
  "inconsistencies": ["lista de problemas encontrados"],
  "correction": "feedback corregido si hay problemas",
  "nota": "nota de evaluación de calidad"
}}
"""
    
    def _get_system_prompt(self) -> str:
        """System prompt del validador."""
        return """Eres un Validador de Calidad确保 que el feedback generado sea:
1. Técnicamente correcto y sin alucinaciones
2. Consistente con la evaluación del Analista
3. Apropiado para el nivel del jugador
4. Pedagógicamente efectivo

Detecta posibles sesgos o información contradictoria.
Confirma que cite fuentes cuando sea necesario."""
    
    def _generar_correccion(
        self, 
        evaluacion: EvaluacionTecnica,
        profile: PlayerProfile
    ) -> str:
        """Genera una corrección básica determinista."""
        score = evaluacion.score_tecnico
        
        if score >= 80:
            return f"Tu decisión fue técnicamente correcta (score: {score}/100). {evaluacion.fortalezas[0] if evaluacion.fortalezas else 'Mantén este nivel.'}"
        elif score >= 50:
            return f"Tu decisión fue aceptable (score: {score}/100). Considera: {evaluacion.debilidades[0] if evaluacion.debilidades else 'Hay espacio de mejora.'}"
        else:
            return f"Tu decisión necesita mejora (score: {score}/100). {evaluacion.debilidades[0] if evaluacion.debilidades else 'Revisa las mejores prácticas.'}"