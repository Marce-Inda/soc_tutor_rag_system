"""
Cliente LLM unificado.
Abstrae la interacción con diferentes proveedores (Gemini, Groq).
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

# LangChain imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain no instalado: pip install langchain-google-genai langchain-groq")

from .llm_config import (
    get_active_config, 
    ModelSettings, 
    DEFAULT_SETTINGS,
    get_env_vars
)


class LLMClient:
    """Cliente unificado para LLMs."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.settings = self._load_settings(config_path)
        self._client = None
        self._provider = self.settings.provider
    
    def _load_settings(self, config_path: Optional[str] = None) -> ModelSettings:
        """Carga configuración desde archivo o entorno."""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                data = json.load(f)
                return ModelSettings(**data)
        return DEFAULT_SETTINGS
    
    def _init_client(self):
        """Inicializa el cliente LangChain según el proveedor."""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain no disponible. Instalar: pip install langchain-google-genai langchain-groq")
        
        config = get_active_config(self._provider)
        
        if self._provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY no configurada")
            
            self._client = ChatGoogleGenerativeAI(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                google_api_key=api_key
            )
        
        elif self._provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY no configurada")
            
            self._client = ChatGroq(
                model=config.model,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                groq_api_key=api_key
            )
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Genera una respuesta del LLM."""
        if not self._client:
            self._init_client()
        
        # Construir messages
        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        messages.append(("human", prompt))
        
        response = self._client.invoke(messages)
        return response.content
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Genera respuesta en formato JSON."""
        # Agregar instrucción de JSON al prompt
        json_prompt = f"{prompt}\n\nResponde solo con JSON válido."
        
        response = self.generate(json_prompt, system_prompt)
        
        # Parsear JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Limpiar markdown fences si hay
            cleaned = response.strip().strip("```json").strip("```")
            return json.loads(cleaned)
    
    def switch_provider(self, provider: str):
        """Cambia el proveedor de LLM."""
        self._provider = provider
        self._client = None  # Reset para reinicializar
    
    def get_provider(self) -> str:
        """Retorna el proveedor activo."""
        return self._provider


def create_client(provider: Optional[str] = None) -> LLMClient:
    """Factory function para crear cliente."""
    return LLMClient()


# Ejemplo de uso
if __name__ == "__main__":
    # Verificar configuración
    envs = get_env_vars()
    print("Variables de entorno requeridas:")
    for k, v in envs.items():
        status = "✓ configurada" if v else "✗ NO configurada"
        print(f"  {k}: {status}")