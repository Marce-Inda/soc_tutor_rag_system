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

def mask_pii(text: str) -> str:
    """
    Enmascara Información de Identificación Personal (PII) en el texto de salida.
    (Cumplimiento de Data Leakage / Output Guardrails).
    """
    if not isinstance(text, str):
        return text
        
    masked = text
    # Tarjetas de crédito (16 dígitos)
    masked = re.sub(r'\b(?:\d[ -]*?){13,16}\b', '[REDACTED_CREDIT_CARD]', masked)
    
    # RFC (México) genérico (Letras y números, 12-13 caracteres)
    # Patrón básico: 3-4 letras, 6 números, 3 alfanuméricos
    masked = re.sub(r'\b[A-Z&Ñ]{3,4}\d{6}[A-V1-9][A-Z1-9][0-9A-Z]\b', '[REDACTED_RFC]', masked)
    
    # Teléfonos genéricos (10 dígitos o más)
    masked = re.sub(r'\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b', '[REDACTED_PHONE]', masked)
    
    # Emails - Protegemos la privacidad por defecto (GDPR)
    # Solo permitimos ver el dominio si es de prueba para mantener contexto pedagógico.
    masked = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', '[REDACTED_EMAIL]', masked)
    
    return masked

def truncate_log_data(data: Any, max_events: int = 50) -> Any:
    """
    Trunca listas de eventos o logs para evitar 'Context Bombing'.
    """
    if isinstance(data, list):
        if len(data) > max_events:
            return data[:max_events] + [{"info": f"... {len(data) - max_events} more events truncated for stability"}]
    return data
