"""
Configuración de modelos LLM para el proyecto.
Soporta: Gemini (Google), Groq (alternativa), DeepSeek (respaldo)
"""

import os
from typing import Optional
from pydantic import BaseModel


class LLMConfig(BaseModel):
    """Configuración base para cualquier LLM."""
    model: str
    temperature: float = 0.3
    max_tokens: int = 512
    top_p: float = 0.8
    top_k: Optional[int] = None


class GeminiConfig(LLMConfig):
    """Configuración para Google Gemini."""
    model: str = "gemini-2.5-flash"
    temperature: float = 0.3  # Bajo para reducir alucinaciones
    max_tokens: int = 512
    top_p: float = 0.8
    
    @property
    def provider(self) -> str:
        return "google"


class GroqConfig(LLMConfig):
    """Configuración para Groq (Llama 3)."""
    model: str = "llama-3.3-70b-versatile"
    temperature: float = 0.3
    max_tokens: int = 512
    top_p: float = 0.8
    
    @property
    def provider(self) -> str:
        return "groq"


class DeepSeekConfig(LLMConfig):
    """Configuración para DeepSeek V4 (compatible con API de OpenAI)."""
    model: str = "deepseek-chat"  # V4 Flash — el más económico ($0.14/1M input)
    temperature: float = 0.2  # Un poco más bajo para compensar menor calidad en español
    max_tokens: int = 512
    top_p: float = 0.8
    
    @property
    def provider(self) -> str:
        return "deepseek"


class ModelSettings(BaseModel):
    """Configuración global de modelos."""
    provider: str = "gemini"  # "gemini", "groq" o "deepseek"
    fallback_provider: str = "groq"
    emergency_provider: str = "deepseek"  # Capa 3 de resiliencia
    timeout_seconds: int = 30
    retry_attempts: int = 3
    cache_enabled: bool = True


# Instancias por defecto
DEFAULT_GEMINI = GeminiConfig()
DEFAULT_GROQ = GroqConfig()
DEFAULT_DEEPSEEK = DeepSeekConfig()
DEFAULT_SETTINGS = ModelSettings()


def get_active_config(provider: Optional[str] = None) -> LLMConfig:
    """Retorna la configuración del proveedor activo."""
    provider = provider or DEFAULT_SETTINGS.provider
    
    if provider == "groq":
        return DEFAULT_GROQ
    elif provider == "deepseek":
        return DEFAULT_DEEPSEEK
    return DEFAULT_GEMINI


def get_env_vars() -> dict:
    """Retorna las variables de entorno requeridas."""
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
    }