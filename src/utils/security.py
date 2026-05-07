import re
from typing import Any

def sanitize_content(text: Any) -> str:
    """
    Sanitiza el contenido para evitar inyecciones indirectas de prompts.
    Elimina palabras clave de control y secuencias sospechosas.
    """
    if not isinstance(text, str):
        text = str(text)
        
    # Palabras clave peligrosas que podrían intentar redefinir el sistema
    danger_keywords = [
        r"SYSTEM_OVERRIDE",
        r"IGNORE ALL PREVIOUS INSTRUCTIONS",
        r"IGNORE PREVIOUS INSTRUCTIONS",
        r"DISREGARD ALL INSTRUCTIONS",
        r"ACT AS A",
        r"YOU ARE NOW A",
        r"JAILBREAK",
        r"DEVELOPER MODE",
        r"ADMIN_MSG",
        r"ADMIN_NOTICE"
    ]
    
    sanitized = text
    for pattern in danger_keywords:
        # Reemplazamos por una versión censurada para no romper el flujo pero anular el comando
        sanitized = re.sub(pattern, "[CENSORED_CONTROL_TOKEN]", sanitized, flags=re.IGNORECASE)
        
    # Eliminar secuencias de escape o caracteres que intenten engañar al tokenizer
    sanitized = sanitized.replace("\r", " ").replace("\t", " ")
    
    return sanitized

def truncate_log_data(data: Any, max_events: int = 50) -> Any:
    """
    Trunca listas de eventos o logs para evitar 'Context Bombing'.
    """
    if isinstance(data, list):
        if len(data) > max_events:
            return data[:max_events] + [{"info": f"... {len(data) - max_events} more events truncated for stability"}]
    return data
