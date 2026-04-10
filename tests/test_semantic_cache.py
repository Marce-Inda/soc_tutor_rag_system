import os
import sys
import time
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.semantic_cache import SemanticCache

def test_cache_functionality():
    print("Iniciando prueba de Caché Semántica...")
    
    # Limpiar datos previos para asegurar estado puro
    import chromadb
    client = chromadb.PersistentClient(path="./data/indices")
    try:
        client.delete_collection("tutor-feedback-cache")
        print("✓ Colección antigua eliminada para limpieza.")
    except:
        pass
        
    # Inicializar caché
    cache = SemanticCache(threshold=0.98, ttl_days=1)
    
    # Datos de prueba
    decision = {"accion": "Bloquear IP", "target": "192.168.1.5", "justificacion": "Tráfico sospechoso de fuerza bruta."}
    context = {"scenario_id": "phishing_v1"}
    player_profile = {"level": "junior"}
    
    feedback_mock = {
        "evaluacion": "Correcto",
        "explicacion": "Bloquear la IP es la medida inmediata recomendada.",
        "mejor_practica": "Usar firewalls perimetrales.",
        "fuentes_citadas": ["NIST 800-61"],
        "costo_estimado": 0.05
    }
    
    # 1. Primer intento: Cache Miss
    print("\nIntento 1: Buscando en caché (debería fallar)...")
    res1 = cache.lookup(decision, context, player_profile)
    if res1 is None:
        print("✓ Resultado esperado: Cache Miss.")
    else:
        print("✗ Error: Se encontró algo en un caché vacío.")

    # 2. Guardar en caché
    print("\nGuardando resultado en caché...")
    cache.store(decision, context, player_profile, feedback_mock)
    
    # 3. Segundo intento: Cache Hit (Exactamente igual)
    print("\nIntento 2: Buscando exactamente lo mismo (debería acertar)...")
    res2 = cache.lookup(decision, context, player_profile)
    if res2 and res2['evaluacion'] == feedback_mock['evaluacion']:
        print("✓ Resultado esperado: Cache Hit!")
    else:
        print("✗ Error: No se encontró el resultado guardado.")

    # 4. Tercer intento: Semánticamente similar
    # Cambiamos un poco la justificación pero el sentido es el mismo
    decision_similar = {
        "accion": "Bloquear IP", 
        "target": "192.168.1.5", 
        "justificacion": "Se detectó tráfico de fuerza bruta, procedo a bloquear la IP."
    }
    print("\nIntento 3: Buscando algo semánticamente muy similar...")
    res3 = cache.lookup(decision_similar, context, player_profile)
    if res3:
        print("✓ Resultado esperado: Cache Hit Semántico (98% similitud)!")
    else:
        print("? Nota: No hubo hit semántico. Esto puede pasar si el umbral del 98% es muy estricto.")

    # 5. Cuarto intento: Algo diferente
    decision_diff = {"accion": "Aislar Host", "target": "PC-Admin", "justificacion": "Posible malware."}
    print("\nIntento 4: Buscando algo totalmente diferente...")
    res4 = cache.lookup(decision_diff, context, player_profile)
    if res4 is None:
        print("✓ Resultado esperado: Cache Miss (Diferente acción).")
    else:
        print("✗ Error: Hit en algo que debería ser diferente.")

if __name__ == "__main__":
    test_cache_functionality()
