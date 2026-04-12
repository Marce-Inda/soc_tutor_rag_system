import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.rag.rag_client import RAGClient
from src.agents.tools import SOCtools

def main():
    print("Testing BuscadorEvidenciaJuego Tool...")
    rag = RAGClient()
    tools = SOCtools(rag)
    
    # Pruebo buscando en un escenario que sabemos que existe: ar-fintech-idor
    scenario_test = "ar-fintech-idor"
    query = "error server internal" # algo generico para ver logs

    # Obtener la herramienta de la lista configurada por Langchain
    tools_list = tools.get_tools()
    evidencia_tool = next(t for t in tools_list if t.name == "buscar_evidencia_en_juego")
    
    print(f"\nQuerying: '{query}' for Scenario: '{scenario_test}'")
    result = evidencia_tool.invoke({"query": query, "scenario_id": scenario_test})
    
    print("\n[RESULTADOS DE LA HERRAMIENTA]")
    print(result[:1000] + "..." if len(result) > 1000 else result)

if __name__ == "__main__":
    main()
