"""
Setup e inicialización de LangChain.
Conecta el LLM client con el RAG y los agents.
"""

from typing import Optional, Dict, Any

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from langchain_core.runnables import RunnableSequence
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain no disponible")

# Importar nuestros módulos
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.prompts import (
    build_prompt_analista,
    build_prompt_explicador,
    build_prompt_validador,
    PROMPT_RETRIEVAL
)
from 03_configuracion_de_modelos.llm_client import LLMClient


class LangChainSetup:
    """Setup de LangChain para el sistema multiagente."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self._prompt_templates = {}
        self._parsers = {}
    
    def _init_prompts(self):
        """Inicializa los prompt templates de LangChain."""
        
        # Prompt template para Analyst
        self._prompt_templates['analyst'] = PromptTemplate(

            input_variables=["decision", "contexto", "contexto_rag"],
            template="Eres un Analista SOC Senior evaluando una decisión técnica.\n\n"
                    "DECISIÓN: {decision}\n"
                    "CONTEXTO: {contexto}\n"
                    "CONOCIMIENTO RAG:\n{contexto_rag}\n\n"
                    "Responde en JSON con: fortalezas, debilidades, evaluacion, fuentes, score_tecnico"
        )
        
        # Prompt template para Explainer
        self._prompt_templates['explainer'] = PromptTemplate(

            input_variables=["evaluacion_analista", "player_level", "dilemma_index", "contexto_rag"],
            template="Eres un Instructor generando feedback pedagógico.\n\n"
                    "EVALUACIÓN DEL ANALISTA: {evaluacion_analista}\n"
                    "NIVEL DEL JUGADOR: {player_level}\n"
                    "ÍNDICE DE DILEMA: {dilemma_index}\n"
                    "CONOCIMIENTO RAG:\n{contexto_rag}\n\n"
                    "Responde en JSON con: evaluacion, explicacion, mejor_practica, fuentes_citadas"
        )
        
        # Prompt template para Validator
        self._prompt_templates['validator'] = PromptTemplate(

            input_variables=["evaluacion_analista", "feedback_explicador", "player_level", "contexto_rag"],
            template="Eres un Validador de Calidad revisando feedback.\n\n"
                    "EVALUACIÓN DEL ANALISTA: {evaluacion_analista}\n"
                    "FEEDBACK DEL EXPLICADOR: {feedback_explicador}\n"
                    "NIVEL DEL JUGADOR: {player_level}\n"
                    "CONOCIMIENTO RAG:\n{contexto_rag}\n\n"
                    "Responde en JSON con: aprobado, inconsistencias, correccion, nota"
        )
    
    def _init_parsers(self):
        """Inicializa los output parsers JSON."""
        self._parsers['json'] = JsonOutputParser()
    
    def build_chain(self, agent_name: str) -> RunnableSequence:
        """Construye una chain para un agente específico."""
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("LangChain no disponible")
        
        if not self._prompt_templates:
            self._init_prompts()
        if not self._parsers:
            self._init_parsers()
        
        prompt = self._prompt_templates.get(agent_name)
        if not prompt:
            raise ValueError(f"Agente desconocido: {agent_name}")
        
        # Crear chain: prompt -> llm -> parser
        chain = prompt | self.llm._client | self._parsers['json']
        return chain
    
    def invoke_chain(self, agent_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Invoca una chain con inputs."""
        chain = self.build_chain(agent_name)
        return chain.invoke(inputs)


def create_langchain_setup(llm_client: Optional[LLMClient] = None) -> LangChainSetup:
    """Factory function."""
    if not llm_client:
        llm_client = LLMClient()
    return LangChainSetup(llm_client)


# Ejemplo
if __name__ == "__main__":
    print("LangChain Setup verificado")
    print(f"Disponible: {LANGCHAIN_AVAILABLE}")