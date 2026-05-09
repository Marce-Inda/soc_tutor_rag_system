"""
Configuración de modelos LLM para el proyecto.
Soporta: Gemini (Google), Groq (alternativa), NVIDIA NIM (respaldo de alto rendimiento)
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
    """Configuración para DeepSeek oficial (compatible con API de OpenAI)."""
    model: str = "deepseek-chat"
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float = 0.8
    
    @property
    def provider(self) -> str:
        return "deepseek"


class NVIDIAConfig(LLMConfig):
    """Configuración para NVIDIA API Catalog (NIM)."""
    model: str = "deepseek-ai/deepseek-v4-pro" # Sucesor de R1 para razonamiento complejo
    temperature: float = 0.1
    max_tokens: int = 4096
    top_p: float = 0.7
    
    @property
    def provider(self) -> str:
        return "nvidia"


class ModelSettings(BaseModel):
    """Configuración global de modelos."""
    provider: str = "gemini"  # "gemini", "groq", "nvidia" o "deepseek"
    fallback_provider: str = "groq"
    emergency_provider: str = "nvidia"  # Capa 3 de resiliencia (NVIDIA NIM)
    timeout_seconds: int = 60 # Aumentado para modelos de razonamiento (R1)
    retry_attempts: int = 2
    cache_enabled: bool = True


# Instancias por defecto
DEFAULT_GEMINI = GeminiConfig()
DEFAULT_GROQ = GroqConfig()
DEFAULT_DEEPSEEK = DeepSeekConfig()
DEFAULT_NVIDIA = NVIDIAConfig()
DEFAULT_SETTINGS = ModelSettings()


def get_active_config(provider: Optional[str] = None) -> LLMConfig:
    """Retorna la configuración del proveedor activo."""
    provider = provider or DEFAULT_SETTINGS.provider
    
    if provider == "groq":
        return DEFAULT_GROQ
    elif provider == "nvidia":
        return DEFAULT_NVIDIA
    elif provider == "deepseek":
        return DEFAULT_DEEPSEEK
    return DEFAULT_GEMINI


def get_env_vars() -> dict:
    """Retorna las variables de entorno requeridas."""
    return {
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
        "NVIDIA_API_KEY": os.getenv("NVIDIA_API_KEY", ""),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
    }