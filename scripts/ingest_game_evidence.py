"""
Script de Ingesta Dinámica de Evidencias Técnicas.
Su propósito es recorrer de forma automática todas las carpetas del videojuego donde están 
guardados los archivos técnicos (logs, configuraciones), leerlos y convertirlos en piezas
de conocimiento almacenadas en la memoria (ChromaDB) que nuestro Tutor Inteligente puede consultar después.
"""
import os
import json
import glob
from pathlib import Path
from typing import List, Dict, Any

# Agregamos la ruta principal (root) del proyecto de forma dinámica.
# Esto asegura que el código pueda encontrar e importar las subcarpetas del código original 'src'.
import sys
sys.path.append(str(Path(__file__).parent.parent))

from src.rag.rag_client import RAGClient

# -----------------
# Variables o Rutas Configurables
# Para mantener la independencia de este proyecto (modo Bootcamp),
# los datos de prueba ahora apuntan internamente a nuestra carpeta "sample_scenarios"
# en lugar de depender del repositorio externo del videojuego original.
# -----------------
PROJECT_ROOT = Path(__file__).parent.parent
SCENARIOS_DIR = os.path.join(PROJECT_ROOT, "data", "sample_scenarios")

def read_text_file(filepath: str) -> str:
    """
    Función auxiliar para abrir y extraer tal cual el texto interno de un documento cualquiera.
    Activa ignorar errores (errors='ignore') para evitar que el script falle (crushee) por 
    culpa de caracteres extraños o malformados que a veces aparecen en los textos y registros.
    """
    try:
        # Abrimos el archivo temporalmente y devolvemos su contenido entero (f.read()).
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        print(f"Alerta: Error leyendo el documento {filepath}. Motivo del problema: {e}")
        return ""

def iter_evidence_files():
    """
    Motor explorador: Función que peina o busca recursivamente, carpeta por carpeta, 
    buscando todo lo que pertenezca al compartimento "evidence" (donde guardamos pruebas).
    Al final, empaqueta los resultados individualmente en pequeños bloques listos 
    para ser guardados en nuestra memoria permanente RAG (ChromaDB).
    """
    print(f"[{'⚙️'}] Comenzando el recorrido de carpetas para buscar toda la evidencia en:\n -> {SCENARIOS_DIR}")
    
    # Solo procesaremos estos tipos concretos de archivos (son archivos que tienen puro texto real). 
    # Si encontramos otros como imágenes, audio o ejecutables técnicos, los desecharemos.
    supported_exts = ['.json', '.log', '.txt', '.sql', '.csv']
    
    count = 0
    # os.walk es poderoso, recorre automáticamente todas las rutas y subcarpetas sin programarlo a mano.
    for root, dirs, files in os.walk(SCENARIOS_DIR):
        
        # Filtramos para asegurarnos que solamente entremos a mirar donde dice la palabra "evidence"
        if "evidence" in root:
            # Separamos cada partecita de la dirección física de la carpeta para inspeccionar de dónde viene
            parts = Path(root).parts
            try:
                # Tratamos de deducir automáticamente a qué "nivel" o escenario del juego 
                # corresponde este archivo. En nuestro esquema, la palabra "evidence" siempre 
                # pertenece por norma o jerarquía a un escenario concreto. 
                # Con la matemática básica (idx - 1) sacamos el nivel anterior, que vendría a ser el identificador del escenario.
                evidence_idx = list(parts).index("evidence")
                scenario_id = parts[evidence_idx - 1]
            except ValueError:
                # En caso que haya desorden y falle la adivinanza, usamos una etiqueta de contingencia.
                scenario_id = "escenario_desconocido"
            
            # Revisamos rápidamente TODOS los archivos detectados en esta pequeña carpeta que agarramos
            for file in files:
                filepath = os.path.join(root, file)
                
                # Obtenemos la última parte del archivo. Ej. ".log" o ".txt", y la volvemos minúscula porsia (.LOG > .log)
                ext = Path(filepath).suffix.lower()
                
                # Si pasa nuestro filtro de texto y permitidas, lo comenzamos a transformar a formato sistema.
                if ext in supported_exts:
                    content = read_text_file(filepath)
                    
                    # Verificamos que el documento por lo menos tenga alguna palabra escrita adentro, si es que no está en blanco.
                    if content.strip():
                        count += 1
                        # Con yield le entregamos este registro individual, empaquetado, directo al bucle principal que pidió datos
                        yield {
                            "text": f"Contenido íntegro de la evidencia técnica (Archivo: {file}):\n...\n{content}\n...",
                            "source": "game_evidence",
                            "scenario_id": scenario_id,
                            "filename": file,
                            "type": "log" # Lo clasificamos bajo la etiqueta unificada 'log' para facilitar que el agente filtre en el futuro.
                        }

def main():
    """
    Punto de arranque y cabecera principal del sistema. Funciona orquestando y uniendo todas
    las tareas paso por paso usando las funciones que vimos recién. Resumen del proceso:
    1. Prender base de datos de memoria
    2. Recolectar lo necesario 
    3. Cargar hacia la base de datos de forma masiva (en lotes)
    """
    print("--------------------------------------------------------------------------")
    print("  🚀 Iniciando el proceso central de Ingestión (Carga) de Evidencias Dinámicas")
    print("--------------------------------------------------------------------------")
    
    # 1. Configurar y Activar la Memoria a Largo Plazo: Instanciamos a un intermediario.
    rag = RAGClient()
    rag._init_client()       # Abre y le avisa internamente a la base de datos vectorial que estamos aquí
    rag._init_embeddings()   # Enciende y descarga el cerebrito que convierte nuestras palabras a "vectores" de conocimiento matemático.
    
    # 2. Iniciar la excavación / recolección de los archivos de conocimiento 
    documents = []
    # Pedimos al explorador `iter_evidence_files` que nos vaya tirando sus agrupados
    for doc in iter_evidence_files():
        documents.append(doc)
    
    print(f"\n[✔️] Proceso completado. Se capturaron internamente {len(documents)} archivos de evidencia correctamente estructurados.")
    
    # 3. Solo si hallamos al menos un documento, lo volcamos masivamente a la máquina final
    if documents:
        print("\n[⚡] Comienza ahora la inyección hacia la memoria profunda de la Inteligencia Artificial...")
        
        # Enviamos la información pero agrupada en bloques compactos de hasta "200 elementos a la vez" 
        # Esta táctica (batching) es esencial para que la computadora no se llene o sobrecargue.
        rag.add_documents(documents=documents, batch_size=200)
        
        print("\n[🎉] ¡Inyección de datos nueva finalizada exitosamente! Listos.")
        
    else:
        print("\n[ℹ️] El recorrido terminó, sin embargo hoy no detectamos archivos recientes de evidencia para transferir.")

# Directriz esencial en Python que dicta "Solo ejecuta todo el proceso de arriba si llamas directamente a este script"
if __name__ == "__main__":
    main()
