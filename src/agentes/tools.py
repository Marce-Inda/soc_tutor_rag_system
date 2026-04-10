"""
Definition of Tools for the automated agents of the SOC Tutor system.
These tools function as capabilities that allow the agent or "Tutor"
to perform specific actions, such as consulting manuals (NIST, MITRE) or searching for evidence
in the game simulation, in order to guide and help the player during training.
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import StructuredTool

class SOCtools:
    """
    Main container for tools designed to assist the SOC Analyst role.
    Here we group all the tutor's search capabilities.
    """
    
    def __init__(self, rag_client):
        """
        Constructor. Receives the RAG (Retrieval-Augmented Generation) client,
        which is the component responsible for connecting to the knowledge base
        and performing intelligent searches in documents.
        """
        self.rag = rag_client
        self.current_scenario_id = "default"

    def set_scenario(self, scenario_id: str):
        """Asigna el id del escenario bajo el telón para que la IA no tenga que memorizarlo y se eviten alucinaciones."""
        if scenario_id:
            self.current_scenario_id = scenario_id

    def buscar_en_nist(self, query: str) -> str:
        """
        Tool: Search content in our NIST 800-61 best practices database.
        Searches for the most relevant parts in the NIST framework documentation
        based on a search string.
        """
        # Hacemos una búsqueda pidiendo un máximo de 3 resultados, y filtramos específicamente por fuente 'nist'
        results = self.rag.retrieve(query, k=3, filter_source="nist")
        
        # If no documents are found, return a friendly notice.
        if not results:
            return "No specific results were found in the NIST documentation."
            
        # Si encontramos respuestas, las unimos separadas por dos saltos de línea para que sea fácil de leer,
        # indicando el nombre de la fuente de donde provino la información.
        return "\n\n".join([f"[{r['source']}] {r['text']}" for r in results])

    def buscar_en_mitre(self, query: str) -> str:
        """
        Tool: Search information in our MITRE ATT&CK tactics and techniques database.
        MITRE is a dictionary of known cyberattacker behaviors.
        """
        # Búsqueda usando la fuente específica 'mitre' para asegurar que los resultados solo vengan de este catálogo.
        results = self.rag.retrieve(query, k=3, filter_source="mitre")
        
        # Validation in case the search yields no results.
        if not results:
            return "No specific results were found in the MITRE ATT&CK matrix."
            
        # Devolvemos el texto encontrado formateado y con la referencia de origen.
        return "\n\n".join([f"[{r['source']}] {r['text']}" for r in results])

    def buscar_evidencia_en_juego(self, query: str) -> str:
        """
        Tool: Search for real technical evidence collected from a specific game scenario.
        Instead of searching theory or manuals, this searches in system logs or event journals
        to find possible traces left by the attacker in the current player's simulation.
        """
        # Se solicita la búsqueda de evidencia, limitando a 5 fragmentos, y forzando a que la búsqueda 
        # se centre únicamente en el escenario que el usuario está jugando usando el ID guardado por la clase.
        results = self.rag.retrieve(query, k=5, filter_scenario_id=self.current_scenario_id)
        
        if not results:
            return f"No related technical evidence was found in the simulation logs for the current scenario ({self.current_scenario_id})."
            
        # Retornamos el texto con la referencia estructurada. Ponemos el nombre de archivo ('filename') si existe,
        # para que el agente sepa exactamente dónde apareció ese log. Si no existe nombre, mostramos la etiqueta general.
        return "\n\n".join([f"[Evidencia detectada - Archivo: {r['filename']}] {r['text']}" for r in results if 'filename' in r] or 
                           [f"[Evidencia detectada] {r['text']}" for r in results])

    def get_tools(self):
        """
        Packages and returns all these functions in the format required by LangChain.
        Provides detailed descriptions for the AI to know exactly when each tool is useful.
        """
        return [
            StructuredTool.from_function(
                func=self.buscar_en_nist,
                name="search_nist",
                description="Useful for searching best practices and official guidelines in the NIST 800-61 database. Ideal for incident response phases. Requires a search string."
            ),
            StructuredTool.from_function(
                func=self.buscar_en_mitre,
                name="search_mitre",
                description="Useful for consulting attacker techniques, tactics, and IOCCs in the MITRE ATT&CK database. Requires a search string."
            ),
            StructuredTool.from_function(
                func=self.buscar_evidencia_en_juego,
                name="search_game_evidence",
                description="Useful for investigating technical clues or evidence present in simulated system events (current game logs). Requires a search string indicating the pattern you are looking for."
            )
        ]
