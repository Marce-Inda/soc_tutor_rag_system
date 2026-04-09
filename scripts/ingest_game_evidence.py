import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any

# Agregar el root del proyecto al sys.path para poder importar src
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.rag.rag_client import RAGClient

# Rutas
GAME_PROJECT_DIR = "/home/marce-i/Documentos/proyectos/videojuego/juego-ciberseguridad"
SCENARIOS_DIR = os.path.join(GAME_PROJECT_DIR, "src", "scenarios")

def read_text_file(filepath: str) -> str:
    """Lee el contenido de un archivo de texto, ignorando errores de encoding."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return ""

def iter_evidence_files():
    """Itera sobre todos los archivos de evidencia en los escenarios."""
    print(f"Buscando evidencias en {SCENARIOS_DIR}...")
    
    # Extensiones soportadas para ingesta raw de texto
    supported_exts = ['.json', '.log', '.txt', '.sql', '.csv']
    
    count = 0
    for root, dirs, files in os.walk(SCENARIOS_DIR):
        if "evidence" in root:
            # Extraer el ID del escenario de la ruta
            # Ruta típica: src/scenarios/level3-practitioner/ar-fintech-idor/evidence/
            parts = Path(root).parts
            try:
                # El id del escenario suele ser el padre de la carpeta evidence (o su abuelo si hay subcarpetas)
                evidence_idx = list(parts).index("evidence")
                scenario_id = parts[evidence_idx - 1]
            except ValueError:
                scenario_id = "unknown_scenario"
            
            for file in files:
                filepath = os.path.join(root, file)
                ext = Path(filepath).suffix.lower()
                
                if ext in supported_exts:
                    content = read_text_file(filepath)
                    if content.strip():
                        count += 1
                        yield {
                            "text": f"Contenido de archivo de evidencia {file}:\n\n{content}",
                            "source": "game_evidence",
                            "scenario_id": scenario_id,
                            "filename": file,
                            "type": "log"
                        }

def main():
    print("Iniciando Ingesta de Evidencias Dinámicas...")
    
    # Instanciar el cliente RAG
    # Reutilizamos persist_directory por defecto
    rag = RAGClient()
    rag._init_client()
    rag._init_embeddings()
    
    documents = []
    
    for doc in iter_evidence_files():
        documents.append(doc)
    
    print(f"Se encontraron {len(documents)} archivos de evidencia parseables.")
    
    if documents:
        print("Ingestando a ChromaDB...")
        # Usa batching que ya implementamos
        rag.add_documents(documents=documents, batch_size=200)
        print("Ingesta finalizada con éxito.")
    else:
        print("No se encontraron evidencias para ingestar.")

if __name__ == "__main__":
    main()
