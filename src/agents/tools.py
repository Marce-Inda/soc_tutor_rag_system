"""
Definition of Tools for the automated agents of the SOC-Tutor system.
"""

# ## HERRAMIENTAS (TOOLS)
# Funciones técnicas que permiten al agente realizar búsquedas en bases de datos (RAG).
from langchain_core.tools import StructuredTool

class SOCtools:
    """
    Main container for tools designed to assist the SOC Analyst role.
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

    def consultar_telemetria_mcp(self, action_type: str, target: str = "") -> str:
        """
        Nueva Herramienta (Fase 1 MCP): Se conecta a un Servidor MCP local para consultar 
        Sistemas externos simulados (Logs en vivo o NDR Scan).
        action_type puede ser 'analyze_logs' o 'network_scan'.
        """
        import asyncio
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def _run():
            # Conexión local tipo stdio al servidor simulado
            server_params = StdioServerParameters(command=".venv/bin/python", args=["src/mcp_servers/telemetry_server.py"])
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    if action_type == "analyze_logs" or action_type == "read_logs":
                        # Usar 'Resources' de MCP para leer el archivo de log entero (si el analista o frontend lo requiere)
                        resource_uri = "siem://incident-001/smtp-logs"
                        res = await session.read_resource(resource_uri)
                        return f"[MCP SIEM LOGS] {res.contents[0].text}"
                        
                    elif action_type == "evaluate_selected_log":
                        # Leer solo el log específico que el jugador clickeó
                        res = await session.call_tool("get_specific_log", arguments={"log_id": target})
                        return f"[MCP SELECTED LOG] {res.content[0].text}"
                        
                    elif action_type == "network_scan" or "scan" in action_type.lower():
                        # Usar 'Tools' de MCP para ejecutar una acción activa
                        # Fallback a localhost si no hay target
                        target_ip = target if target else "localhost"
                        res = await session.call_tool("execute_ndr_scan", arguments={"target_ip": target_ip})
                        return f"[MCP NDR SCAN RESULTS] {res.content[0].text}"
                        
                    return "Acción MCP no reconocida. Intentar con analyze_logs o network_scan."
        try:
            return asyncio.run(asyncio.wait_for(_run(), timeout=15.0))
        except asyncio.TimeoutError:
            return "Error: Tiempo de espera agotado al conectar con el Servidor MCP de Telemetría. El sistema está bajo alta carga."
        except Exception as e:
            return f"Error conectando al Servidor MCP de Telemetría: {str(e)}"

    def ejecutar_accion_edr_mcp(self, action_type: str, target: str) -> str:
        """
        Nueva Herramienta (Fase 2 MCP): Constata un intento de mitigación 
        conectándose a un Servidor MCP de EDR/Firewall (Acciones que mutan el estado).
        action_type puede ser 'isolate_host' o 'block_ip'.
        """
        import asyncio
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def _run():
            server_params = StdioServerParameters(command=".venv/bin/python", args=["src/mcp_servers/edr_server.py"])
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    if action_type == "isolate_host" or "isolate" in action_type.lower():
                        res = await session.call_tool("isolate_host", arguments={"hostname": target})
                        return f"[MCP EDR ACTION] {res.content[0].text}"
                        
                    elif action_type == "block_ip" or "block" in action_type.lower():
                        res = await session.call_tool("block_ip", arguments={"ip_address": target})
                        return f"[MCP FIREWALL ACTION] {res.content[0].text}"
                        
                    return "Acción de EDR no reconocida. Intentar con isolate_host o block_ip."
        try:
            return asyncio.run(asyncio.wait_for(_run(), timeout=15.0))
        except asyncio.TimeoutError:
            return "Error: Tiempo de espera agotado al conectar con el Servidor EDR. La acción de contención podría estar en proceso pero el enlace falló."
        except Exception as e:
            return f"Error conectando al Servidor EDR por MCP: {str(e)}"


    def get_tools(self):
        """
        Método final clave: Empaqueta y devuelve todas estas funciones al formato requerido 
        por 'LangChain', que es el gran cerebro lógico que coordina a los agents de IA.
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
                func=self.consultar_telemetria_mcp,
                name="telemetry_mcp_client",
                description="Crucial tool! Use this to intercept live telemetry using external systems (MCP). Pass 'action_type'='analyze_logs' to read raw SMTP logs from the SIEM. Pass 'action_type'='evaluate_selected_log' and 'target'=<log_id> to evaluate a specific log selected by the user. Pass 'action_type'='network_scan' and 'target' to execute a live port scan on the NDR."
            ),
            StructuredTool.from_function(
                func=self.ejecutar_accion_edr_mcp,
                name="edr_mcp_client",
                description="Crucial tool! Use this to execute containment actions on the simulated EDR (Endpoint Detection and Response) and Firewall using MCP. Pass 'action_type'='isolate_host' and 'target'=<hostname> to disconnect a machine. Pass 'action_type'='block_ip' and 'target'=<ip> to block traffic. You MUST use this to verify if containment worked."
            )
        ]
