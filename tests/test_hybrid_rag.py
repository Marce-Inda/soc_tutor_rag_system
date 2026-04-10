import os
import sys
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent))

from src.rag.rag_client import RAGClient

def test_hybrid_retrieval():
    print("Iniciando prueba de RAG Híbrido...")
    
    # Inicializar cliente
    rag = RAGClient()
    
    # 1. Crear documento de prueba con ID técnico
    test_docs = [
        {
            "id": "test_mitre_1",
            "text": "La técnica T1059.001 se refiere a la ejecución de comandos a través de PowerShell para evadir defensas.",
            "source": "MITRE Test",
            "type": "technique"
        },
        {
            "id": "test_ip_1",
            "text": "Se ha detectado tráfico sospechoso hacia la dirección IP 192.168.1.100 involucrando exfiltración de datos.",
            "source": "Log Test",
            "type": "log"
        }
    ]
    
    print("\nAgregando documentos de prueba...")
    rag.add_documents(test_docs)
    
    # 2. Prueba de búsqueda semántica (puede traer resultados similares)
    print("\n--- PRUEBA SEMÁNTICA ---")
    query_sem = "ejecución de scripts maliciosos"
    results_sem = rag.retrieve(query_sem, k=2)
    for r in results_sem:
        print(f"Match Semántico: {r['text'][:50]}... (Dist: {r['distance']:.4f})")
        
    # 3. Prueba de búsqueda exacta (debe encontrar el ID de MITRE)
    print("\n--- PRUEBA EXACTA ---")
    query_exact = "Cúal es la técnica T1059.001?"
    results_exact = rag.retrieve_exact(query_exact)
    found_exact = False
    for r in results_exact:
        print(f"Match Exacto: {r['text'][:50]}...")
        if "T1059.001" in r['text']:
            found_exact = True
            
    if found_exact:
        print("✓ Búsqueda exacta funcionó correctamente para ID de MITRE.")
    else:
        print("✗ Búsqueda exacta falló para ID de MITRE.")

    # 4. Prueba de búsqueda híbrida
    print("\n--- PRUEBA HÍBRIDA ---")
    query_hybrid = "Dime sobre la IP 192.168.1.100"
    results_hybrid = rag.retrieve_hybrid(query_hybrid)
    
    matches_ip = [r for r in results_hybrid if r.get('is_exact')]
    if matches_ip:
        print(f"✓ Búsqueda híbrida priorizó match exacto para IP.")
        for r in results_hybrid:
            tag = "[EXACTO]" if r.get('is_exact') else "[SEMÁNTICO]"
            print(f"{tag}: {r['text'][:50]}...")
    else:
        print("✗ Búsqueda híbrida no marcó el match exacto.")

if __name__ == "__main__":
    test_hybrid_retrieval()
