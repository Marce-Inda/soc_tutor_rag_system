"""
Herramientas para los agentes del sistema UEFS.
Permiten realizar búsquedas técnicas en el conocimiento RAG.
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import StructuredTool

class SOCtools:
    """Contenedor de herramientas para el Analista SOC."""
    
    def __init__(self, rag_client):
        self.rag = rag_client

    def buscar_en_nist(self, query: str) -> str:
        """Busca mejores prácticas en NIST 800-61."""
        results = self.rag.retrieve(query, k=3, filter_source="nist")
        if not results:
            return "No se encontraron resultados específicos en NIST."
        return "\n\n".join([f"[{r['source']}] {r['text']}" for r in results])

    def buscar_en_mitre(self, query: str) -> str:
        """Busca tácticas y técnicas en MITRE ATT&CK."""
        results = self.rag.retrieve(query, k=3, filter_source="mitre")
        if not results:
            return "No se encontraron resultados específicos en MITRE."
        return "\n\n".join([f"[{r['source']}] {r['text']}" for r in results])

    def buscar_evidencia_en_juego(self, query: str, scenario_id: str) -> str:
        """Busca evidencia técnica real en los logs de la simulación del juego."""
        results = self.rag.retrieve(query, k=5, filter_scenario_id=scenario_id)
        if not results:
            return f"No se encontró evidencia técnica en los logs de la simulación para el escenario {scenario_id}."
        return "\n\n".join([f"[Evidencia - {r['filename']}] {r['text']}" for r in results if 'filename' in r] or 
                           [f"[Evidencia] {r['text']}" for r in results])

    def get_tools(self):
        """Retorna la lista de herramientas compatibles con LangChain."""
        return [
            StructuredTool.from_function(
                func=self.buscar_en_nist,
                name="buscar_en_nist",
                description="Busca mejores prácticas y lineamientos en la base de datos del NIST 800-61. Útil para fases de respuesta a incidentes."
            ),
            StructuredTool.from_function(
                func=self.buscar_en_mitre,
                name="buscar_en_mitre",
                description="Busca técnicas, tácticas y IOCs en MITRE ATT&CK. Útil para identificar el comportamiento del adversario."
            ),
            StructuredTool.from_function(
                func=self.buscar_evidencia_en_juego,
                name="buscar_evidencia_en_juego",
                description="Busca evidencia técnica real (logs, archivos json) dentro de la simulación del juego. DEBES pasar el 'scenario_id' actual del juego."
            )
        ]
