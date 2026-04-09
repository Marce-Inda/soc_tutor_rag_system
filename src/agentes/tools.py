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

    def buscar_en_nist(self, query: str) -> str:
        """
        Herramienta número 1: Buscar contenido en nuestra base de datos de mejores prácticas de NIST 800-61.
        A partir de un texto (query) enviado por el usuario o agente, busca las partes más relevantes 
        en la documentación del marco de referencia de NIST.
        """
        # Hacemos una búsqueda pidiendo un máximo de 3 resultados, y filtramos específicamente por fuente 'nist'
        results = self.rag.retrieve(query, k=3, filter_source="nist")
        
        # Si no encontramos ningún documento relacionado, devolvemos un aviso amigable.
        if not results:
            return "No se encontraron resultados específicos en la documentación de NIST."
            
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
        
        # Validación en caso de que la búsqueda no arroje resultados.
        if not results:
            return "No se encontraron resultados específicos en la matriz de MITRE ATT&CK."
            
        # Devolvemos el texto encontrado formateado y con la referencia de origen.
        return "\n\n".join([f"[{r['source']}] {r['text']}" for r in results])

    def buscar_evidencia_en_juego(self, query: str, scenario_id: str) -> str:
        """
        Herramienta número 3: Buscar información técnica real recopilada de un escenario de juego específico.
        En lugar de buscar teoría o manuales, esto busca en los "logs", o "diarios" de eventos del sistema,
        para encontrar posibles rastros que el atacante haya dejado en la simulación actual del jugador.
        """
        # Se solicita la búsqueda de evidencia, limitando a 5 fragmentos, y forzando a que la búsqueda 
        # se centre únicamente en el escenario que el usuario está jugando (scenario_id).
        results = self.rag.retrieve(query, k=5, filter_scenario_id=scenario_id)
        
        if not results:
            return f"No se encontró evidencia técnica relacionada en los logs de la simulación para el escenario {scenario_id}."
            
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
                name="buscar_en_nist",
                description="Busca mejores prácticas y lineamientos en la base de datos del estándar internacional NIST 800-61. Útil para consultar fases de respuestas a incidentes."
            ),
            StructuredTool.from_function(
                func=self.buscar_en_mitre,
                name="buscar_en_mitre",
                description="Busca técnicas, tácticas y marcadores o IOCs en la base de inteligencia de MITRE ATT&CK. Usar para entender los pasos de un ciberadversario."
            ),
            StructuredTool.from_function(
                func=self.buscar_evidencia_en_juego,
                name="buscar_evidencia_en_juego",
                description="Busca evidencia técnica verídica presente en los eventos del sistema simulado (archivos del juego) para armar pistas. DEBES proveer explícitamente el 'scenario_id' (identificador del escenario de juego)."
            )
        ]
