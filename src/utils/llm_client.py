"""
Cliente LLM (Large Language Model) unificado.
Este archivo actúa como un "traductor universal" o enchufe. 
Nos permite conectar nuestro juego con diferentes cerebros artificiales 
(como Google Gemini, Groq, DeepSeek, o Ollama local) usando el mismo código, 
sin importar qué IA estemos usando por detrás.
"""

import os
import json
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv
from .token_counter import TokenCounter

# Intentamos importar LangChain. LangChain es una librería externa súper útil que 
# funciona como un intermediario o adaptador estandarizado para comunicarse con cualquier IA.
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_groq import ChatGroq
    from langchain_ollama import ChatOllama
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain no instalado. Instalar: pip install langchain-google-genai langchain-groq langchain-ollama")

try:
    from tenacity import retry, wait_exponential_jitter, stop_after_attempt, RetryError
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    print("Tenacity no instalado. Por favor instala tenacity para el sistema de reintentos: pip install tenacity")


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
        self._backup_client = None
        self.last_usage = {"input_tokens": 0, "output_tokens": 0, "cost": 0.0, "provider_used": provider}
    
    def _init_client(self):
        """
        Esta función "enciende" verdaderamente la conexión con el modelo de IA.
        Dependiendo del proveedor, buscará las "llaves" secretas (API Keys) que 
        actúan como contraseñas especiales para permitirnos usar los servidores de Google o Groq.
        """
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain no disponible. Requisito indispensable.")
        
        # 1. CARGA DE ENTORNO (Prioridad Absoluta al archivo .env)
        load_dotenv(override=True)
        
        # Conexión con IA de Google (Gemini)
        if self.provider == "gemini":
            # 2. LIMPIEZA DE CONFLICTOS
            # Forzamos que LangChain no use variables de entorno del sistema que puedan estar corruptas
            os.environ.pop("GOOGLE_API_KEY", None)
            
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")
            
            if not api_key:
                raise ValueError("No se encontró GEMINI_API_KEY o GOOGLE_API_KEY en el .env")
            
            self._client = ChatGoogleGenerativeAI(
                model=self.model or "gemini-2.5-flash",
                temperature=self.temperature,
                google_api_key=api_key,
                timeout=15.0 
            )
        
        # Conexión con IA súper rápida (Groq)
        elif self.provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("La llave maestra (GROQ_API_KEY) no está configurada.")
            
            self._client = ChatGroq(
                model=self.model or "llama-3.3-70b-versatile",
                temperature=self.temperature,
                groq_api_key=api_key,
                timeout=15.0 # Timeout global de seguridad
            )
            
        # Conexión con DeepSeek V4 (compatible con API de OpenAI)
        # DeepSeek usa el mismo formato que OpenAI, por lo que reutilizamos langchain-openai
        # como adaptador. Solo necesitas configurar DEEPSEEK_API_KEY en tu .env
        elif self.provider == "deepseek":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                raise RuntimeError(
                    "Para usar DeepSeek necesitas instalar langchain-openai: "
                    "pip install langchain-openai"
                )
            api_key = os.getenv("DEEPSEEK_API_KEY")
            if not api_key:
                raise ValueError("La llave maestra (DEEPSEEK_API_KEY) no fue encontrada. No podemos conectarnos a DeepSeek.")
            
            self._client = ChatOpenAI(
                model=self.model or "deepseek-chat",  # DeepSeek V4 Flash (el más económico)
                temperature=self.temperature,
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
                timeout=20.0  # DeepSeek puede tener mayor latencia desde Latinoamérica
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
    
    def _create_fallback_client(self, provider: str, model: str):
        """
        Fábrica interna para crear clientes de respaldo (fallback).
        Centraliza la lógica de creación para evitar duplicación de código
        cuando la cascada de resiliencia necesita inicializar un provider alternativo.
        """
        if provider == "groq":
            return ChatGroq(
                model=model,
                temperature=self.temperature,
                groq_api_key=os.getenv("GROQ_API_KEY"),
                timeout=15.0
            )
        elif provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model,
                temperature=self.temperature,
                google_api_key=os.getenv("GEMINI_API_KEY"),
                timeout=15.0
            )
        elif provider == "deepseek":
            try:
                from langchain_openai import ChatOpenAI
            except ImportError:
                raise RuntimeError("langchain-openai requerido para fallback DeepSeek: pip install langchain-openai")
            return ChatOpenAI(
                model=model,
                temperature=self.temperature,
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com/v1",
                timeout=20.0
            )
        else:
            raise ValueError(f"No se puede crear fallback para provider desconocido: {provider}")

    @retry(wait=wait_exponential_jitter(initial=1, max=10), stop=stop_after_attempt(3))
    async def _generate_with_retry(self, messages: list) -> str:
        """Función interna envuelta en Tenacity para intentar reconexiones asíncronas."""
        response = await self._client.ainvoke(messages)
        return response.content

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Toma una pregunta (prompt) del usuario y una instrucción base (system_prompt) 
        para pedirle asíncronamente a la Inteligencia Artificial una respuesta.
        """
        if not self._client:
            self._init_client()
        
        messages = []
        if system_prompt:
            messages.append(("system", system_prompt)) # Contexto oculto
        messages.append(("human", prompt))             # Lo que escribió el usuario
        
        try:
            response_text = await self._generate_with_retry(messages)
            current_provider = self.provider
        except Exception as primary_error:
            # CASCADA DE RESILIENCIA (3 capas):
            # Capa 1: Provider primario (ya falló arriba)
            # Capa 2: Fallback bidireccional Gemini ↔ Groq
            # Capa 3: DeepSeek como red de seguridad final
            
            # Determinar fallback de Capa 2
            if self.provider == "gemini" and os.getenv("GROQ_API_KEY"):
                fallback_provider = "groq"
                fallback_model = "llama-3.3-70b-versatile"
            elif self.provider == "groq" and os.getenv("GEMINI_API_KEY"):
                fallback_provider = "gemini"
                fallback_model = "gemini-2.5-flash"
            elif self.provider != "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
                # Si no tenemos ni Gemini ni Groq alternativos, saltar directo a DeepSeek
                fallback_provider = "deepseek"
                fallback_model = "deepseek-chat"
            else:
                fallback_provider = None

            if fallback_provider:
                print(f"  [LLMClient] Primary provider ({self.provider}) failed: {primary_error}. Falling back to {fallback_provider}...")
                try:
                    if not self._backup_client or getattr(self, '_backup_provider', None) != fallback_provider:
                        self._backup_client = self._create_fallback_client(fallback_provider, fallback_model)
                        self._backup_provider = fallback_provider
                    response = await self._backup_client.ainvoke(messages)
                    response_text = response.content
                    current_provider = fallback_provider
                except Exception as secondary_error:
                    if fallback_provider != "deepseek" and os.getenv("DEEPSEEK_API_KEY"):
                        print(f"  [LLMClient] Secondary fallback ({fallback_provider}) also failed: {secondary_error}. Last resort: DeepSeek...")
                        try:
                            deepseek_client = self._create_fallback_client("deepseek", "deepseek-chat")
                            response = await deepseek_client.ainvoke(messages)
                            response_text = response.content
                            current_provider = "deepseek"
                        except Exception as tertiary_error:
                            print(f"  [LLMClient] All 3 providers failed. Last error: {tertiary_error}")
                            raise primary_error
                    else:
                        raise primary_error
            else:
                raise primary_error

        # Track Tokens
        input_text = " ".join([msg[1] for msg in messages])
        in_tokens = TokenCounter.count_tokens(input_text)
        out_tokens = TokenCounter.count_tokens(response_text)
        cost = TokenCounter.estimate_cost(in_tokens, out_tokens, current_provider)
        
        self.last_usage = {
            "input_tokens": in_tokens,
            "output_tokens": out_tokens,
            "cost": cost,
            "provider_used": current_provider
        }
        
        return response_text
    
    async def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Fuerza a la IA a responder en formato máquina (JSON) de forma asíncrona.
        """
        json_prompt = f"{prompt}\n\nResponde solo y exclúsivamente con formato JSON válido."
        
        try:
            response = await self.generate(json_prompt, system_prompt)
        except Exception as e:
            # GRACEFUL DEGRADATION (Fallback Determinista)
            # Si pasaron todos los reintentos (ej. no hay internet), devolvemos este JSON universal súper-resiliente.
            # Cubre todos los keys ("fortalezas", "evaluacion", "aprobado") de los 3 agents para no romper el Pydantic.
            print(f"  [LLMClient Fallback] Conexión perdida. Activando Degradación Elegante. Error: {e}")
            return {
                "evaluacion": "Aviso del Sistema: El enlace con el servidor de inteligencia se interrumpió. Acción registrada como neutral.",
                "analysis": "Emergency analysis: AI connection lost.",
                "explanation": "Technical evaluation unavailable due to network timeout.",
                "best_practice": "Consult standard NIST/MITRE documentation and retry the action later.",
                "recommendation": "Check internet connection and API availability.",
                "technical_score": 50,
                "score_tecnico": 50,
                "fortalezas": ["Intento de acción completado."],
                "debilidades": ["Análisis interrumpido por fallo técnico."],
                "fuentes": ["System Fallback"],
                "explicacion": "Se ha activado el protocolo de emergencia por fallo de red.",
                "mejor_practica": "Verificar conectividad de los servidores MCP y LLM.",
                "verified_artifacts": [],
                "aprobado": True,
                "compliant": False,
                "risks": ["Error técnico en evaluación legal"],
                "quality_score": "Respuesta de Emergencia",
                "inconsistencies": []
            }

        
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

