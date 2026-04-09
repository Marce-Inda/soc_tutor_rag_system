"""
Cliente LLM (Large Language Model) unificado.
Este archivo actúa como un "traductor universal" o enchufe. 
Nos permite conectar nuestro juego con diferentes cerebros artificiales 
(como Google Gemini, Groq, o Ollama local) usando el mismo código, 
sin importar qué IA estemos usando por detrás.
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path

# Intentamos importar LangChain. LangChain es una librería externa súper útil que 
# funciona como un intermediario o adaptador estandarizado para comunicarse con cualquier IA.
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    from langchain_community.chat_models import ChatOllama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain no instalado. Instalar: pip install langchain-google-genai langchain-groq langchain-community")


class LLMClient:
    """
    Cliente unificado para IA.
    Es la clase principal que "abraza" o encapsula a cualquiera de los modelos de IA elegidos.
    """
    
    def __init__(self, provider: str = "gemini", model: Optional[str] = None, temperature: float = 0.1):
        """
        Al nacer esta clase, configuramos qué cerebro (provider) queremos usar 
        y qué tan creativa debe ser la IA (temperature). Una temperatura baja (0.1) 
        hace que las respuestas sean más serias, lógicas y predecibles (ideal para un tutor rígido de ciberseguridad).
        """
        self.provider = provider
        self.model = model
        self.temperature = temperature
        self._client = None
    
    def _init_client(self):
        """
        Esta función "enciende" verdaderamente la conexión con el modelo de IA.
        Dependiendo del proveedor, buscará las "llaves" secretas (API Keys) que 
        actúan como contraseñas especiales para permitirnos usar los servidores de Google o Groq.
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain no disponible. Requisito indispensable.")
        
        # Conexión con IA de Google (Gemini)
        if self.provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("La llave maestra (GEMINI_API_KEY) no fue encontrada. No podemos conectarnos a Google.")
            
            self._client = ChatGoogleGenerativeAI(
                model=self.model or "gemini-2.5-flash",
                temperature=self.temperature,
                google_api_key=api_key
            )
        
        # Conexión con IA súper rápida (Groq)
        elif self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("La llave maestra (GROQ_API_KEY) no está configurada.")
            
            self._client = ChatGroq(
                model=self.model or "llama-3-70b-versatile",
                temperature=self.temperature,
                groq_api_key=api_key
            )
            
        # Conexión con IA local que corre en nuestra computadora (Ollama)
        elif self.provider == "ollama":
            self._client = ChatOllama(
                model=self.model or "llama3",
                temperature=self.temperature
            )
        # Por si ponen en las configuraciones un cerebro que no existe
        else:
            raise ValueError(f"No conozco al proveedor de IA: {self.provider}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Toma una pregunta (prompt) del usuario y una instrucción base (system_prompt) 
        para pedirle asíncronamente a la Inteligencia Artificial una respuesta en formato de texto normal.
        """
        if not self._client:
            self._init_client()
        
        messages = []
        if system_prompt:
            messages.append(("system", system_prompt)) # Contexto oculto que le da la personalidad al bot
        messages.append(("human", prompt))             # Lo que escribió el usuario/jugador
        
        # Hacemos la consulta por internet a la IA y obtenemos la respuesta (.invoke)
        response = self._client.invoke(messages)
        return response.content
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        A veces en vez de texto normal para lectura humana, nuestro código necesita 
        que la IA le devuelva "Datos de Sistema" estructurados. Esta función fuerza 
        a la IA a responder sí o sí en formato máquina (JSON) para que otros códigos lo entiendan fácil.
        """
        json_prompt = f"{prompt}\n\nResponde solo y exclúsivamente con formato JSON válido."
        response = self.generate(json_prompt, system_prompt)
        
        try:
            # Intenta convertir la respuesta devuelta al formato JSON de Python limpio.
            return json.loads(response)
        except json.JSONDecodeError:
            # Si la IA se portó mal y puso texto basura (como disculpas) antes o después del JSON útil, 
            # este pequeño código auxiliar recorta limpiamente la basura y se queda solo con el bloque de código entre llaves '{' '}'.
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(response[start:end])
            raise ValueError(f"Falla crítica, no se pudo entender la respuesta JSON de la IA: {response}")
    
    def get_provider(self) -> str:
        """Devuelve el nombre del cerebro IA que estamos usando actualmente."""
        return self.provider


def create_llm_client(provider: str = "gemini") -> LLMClient:
    """Función de atajo rápida para crear toda esta conexión de IA en una 1 sola y elegante línea en otros archivos."""
    return LLMClient(provider=provider)

