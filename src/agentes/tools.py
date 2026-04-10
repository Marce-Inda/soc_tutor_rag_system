"""
Definición de las Herramientas (Tools) para los agentes automatizados del sistema SOC-Tutor.
Estas herramientas funcionan como funciones que le permiten al agente o "Tutor"
realizar acciones específicas, como consultar manuales (NIST, MITRE) o buscar pistas (evidencias)
en la simulación del juego, para poder guiar y ayudar al jugador durante su entrenamiento.
"""

from typing import List, Dict, Any, Optional
from langchain_core.tools import StructuredTool

class SOCtools:
    """
    Contenedor principal de las herramientas diseñadas para asistir al rol de Analista SOC.
    Aquí agrupamos todas las capacidades de búsqueda del tutor.
    """
    
    def __init__(self, rag_client):
        """
        Constructor de la clase. Recibe el cliente RAG (Retrieval-Augmented Generation), 
        que es el componente encargado de conectarse a la base de datos de conocimiento
        y realizar las búsquedas inteligentes en los documentos.
        """
        self.rag = rag_client
        self.current_scenario_id = "default"

    def set_scenario(self, scenario_id: str):
        """Asigna el id del escenario bajo el telón para que la IA no tenga que memorizarlo y se eviten alucinaciones."""
        if scenario_id:
            self.current_scenario_id = scenario_id

    def buscar_en_nist(self, query: str) -> str:
        """
        Herramienta número 1: Buscar contenido en nuestra base de datos de mejores prácticas de NIST 800-61.
        A partir de un texto (query) enviado por el usuario o agente, busca las partes más relevantes 
        en la documentación del marco de referencia de NIST.
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
        Herramienta número 2: Buscar información en nuestra base de datos de tácticas y técnicas de MITRE ATT&CK.
        MITRE es un diccionario de comportamientos conocidos de los ciberatacantes.
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
        Herramienta número 3: Buscar información técnica real recopilada de un escenario de juego específico.
        En lugar de buscar teoría o manuales, esto busca en los "logs", o "diarios" de eventos del sistema,
        para encontrar posibles rastros que el atacante haya dejado en la simulación actual del jugador.
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
        Método final clave: Empaqueta y devuelve todas estas funciones al formato requerido 
        por 'LangChain', que es el gran cerebro lógico que coordina a los agentes de IA.
        Aporta descripciones detalladas de qué hace cada herramienta, para que la Inteligencia Artificial 
        sepa exactamente en qué momento es útil llamar a una u otra, según la duda que tenga el usuario.
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
