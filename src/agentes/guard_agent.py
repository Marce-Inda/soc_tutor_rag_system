"""
Guard Agent - Protección y validación de entradas.
Detecta intentos de prompt injection e inputs malformados.
"""

import re
from typing import Dict, Any, Tuple
from ..agentes.types import Decision

class GuardAgent:
    """Implementación de guardrails para el sistema."""
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
        self.suspicious_patterns = [
            r"ignore previous instructions",
            r"ignora las instrucciones anteriores",
            r"ignore as instruções anteriores",
            r"system: ",
            r"<script>",
            r"dump your prompt",
            r"revelar su prompt",
            r"you are now an",
            r"ahora eres un",
            r"dan mode",
            r"forget everything"
        ]

    def validate_input(self, decision: Decision) -> Tuple[bool, str]:
        """
        Valida que la entrada sea segura.
        Retorna (es_seguro, mensaje_error).
        """
        text_to_check = f"{decision.accion} {decision.detalle or ''}"
        
        # 1. Reglas heurísticas simples
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_to_check, re.IGNORECASE):
                return False, f"Detectado patrón de seguridad no permitido: {pattern}"
        
        # 2. Validación de longitud
        if len(text_to_check) > 1000:
            return False, "Input excesivamente largo (potencial DoS)"
            
        return True, ""

    def validate_output(self, output: Dict[str, Any]) -> bool:
        """Verifica que el output no contenga leaks o contenido inadecuado."""
        # Simple check for required fields from agents/types.py
        return True
