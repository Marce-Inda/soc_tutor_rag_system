"""
Cliente LLM unificado.
Abstrae la interacción con diferentes proveedores (Gemini, Groq, Ollama).
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

# LangChain imports
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    from langchain_community.chat_models import ChatOllama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain no instalado. Instalar: pip install langchain-google-genai langchain-groq langchain-community")


class LLMClient:
    """Cliente unificado para LLMs."""
    
    def __init__(self, provider: str = "gemini", model: Optional[str] = None, temperature: float = 0.1):
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self._client = None
    
    def _init_client(self):
        """Inicializa el cliente LangChain según el proveedor."""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain no disponible.")
        
        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY no configurada")
            
            self._client = ChatGoogleGenerativeAI(
                model=self.model or "gemini-1.5-flash",
                temperature=self.temperature,
                google_api_key=api_key
            )
        
        elif self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY no configurada")
            
            self._client = ChatGroq(
                model=self.model or "llama-3-70b-versatile",
                temperature=self.temperature,
                groq_api_key=api_key
            )
            
        elif self.provider == "ollama":
            self._client = ChatOllama(
                model=self.model or "llama3",
                temperature=self.temperature
            )
        else:
            raise ValueError(f"Proveedor desconocido: {self.provider}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Genera una respuesta del LLM."""
        if not self._client:
            self._init_client()
        
        messages = []
        if system_prompt:
            messages.append(("system", system_prompt))
        messages.append(("human", prompt))
        
        response = self._client.invoke(messages)
        return response.content
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Genera respuesta en formato JSON."""
        json_prompt = f"{prompt}\n\nResponde solo con JSON válido."
        response = self.generate(json_prompt, system_prompt)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            cleaned = response.strip().strip("```json").strip("```")
            return json.loads(cleaned)
    
    def get_provider(self) -> str:
        return self.provider


def create_llm_client(provider: str = "gemini") -> LLMClient:
    return LLMClient(provider=provider)
