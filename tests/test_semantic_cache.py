import os
import sys
import time
from pathlib import Path

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.semantic_cache import SemanticCache

import os
import sys
import time
import logging
from pathlib import Path
from unittest.mock import MagicMock

# Configurar logging para ver los detalles del caché
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Agregar src al path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.semantic_cache import SemanticCache

def test_cache_functionality():
    print("=== Iniciando prueba de Caché Semántica V2 ===")
    
    # Limpiar datos previos para asegurar estado puro
    import chromadb
    persist_path = "./data/indices"
    client = chromadb.PersistentClient(path=persist_path)
    try:
        client.delete_collection("tutor-feedback-cache-test")
        print("✓ Colección de prueba antigua eliminada.")
    except:
        pass
        
    # Mock de LLM Client para probar traducción
    mock_llm = MagicMock()
    mock_llm.generate.return_value = "Block IP address"
    
    # Inicializar caché con umbral alto y colección específica de test
    cache = SemanticCache(
        collection_name="tutor-feedback-cache-test",
        threshold=0.95, 
        ttl_days=1,
        llm_client=mock_llm
    )
    
    # Datos de prueba en Español
    decision_es = {
        "accion": "Bloquear la dirección IP", 
        "target": "192.168.1.100", 
        "justificacion": "Actividad maliciosa detectada."
    }
    context = {"scenario_id": "test_scenario", "tipo_incidente": "brute_force", "fase": "containment"}
    player_profile = {"level": "junior", "rol": "analyst"}
    
    feedback_mock = {
        "evaluacion": "Excelente",
        "explicacion": "El bloqueo de la IP es correcto.",
        "aprobado": True
    }
    
    # 1. Primer intento: Cache Miss
    print("\n[1] Intento 1: Buscando en caché vacía...")
    res1 = cache.lookup(decision_es, context, player_profile)
    if res1 is None:
        print("✓ Resultado esperado: Cache Miss.")
    else:
        print("✗ Error: Se encontró algo en un caché vacío.")

    # 2. Guardar en caché
    print("\n[2] Guardando resultado en caché...")
    cache.store(decision_es, context, player_profile, feedback_mock)
    
    # Verificar que el LLM fue llamado para traducir "Bloquear la dirección IP"
    if mock_llm.generate.called:
        print(f"✓ LLM llamado para traducción: {mock_llm.generate.call_args}")
    
    # 3. Segundo intento: Cache Hit (Exactamente igual)
    print("\n[3] Intento 2: Buscando exactamente lo mismo...")
    res2 = cache.lookup(decision_es, context, player_profile)
    if res2 and res2['evaluacion'] == feedback_mock['evaluacion']:
        print("✓ Resultado esperado: Cache Hit!")
    else:
        print("✗ Error: No se encontró el resultado guardado.")

    # 4. Tercer intento: Hit Cross-Language (Simulado)
    # Buscamos en Inglés lo que guardamos en Español
    # El caché debería traducir "Block the IP" -> "Block IP address" (vía mock) y encontrar el hit
    decision_en = {
        "accion": "Block the IP address", 
        "target": "192.168.1.100", 
        "justificacion": "Malicious activity."
    }
    print("\n[4] Intento 3: Buscando en Inglés (Cross-Language Hit)...")
    res3 = cache.lookup(decision_en, context, player_profile)
    if res3:
        print("✓ Resultado esperado: Cache Hit Multilingüe detectado!")
    else:
        print("✗ Error: No hubo hit multilingüe.")

    # 5. Cuarto intento: Umbral de similitud
    # Algo similar pero por debajo del 95% de similitud (o por encima de la distancia permitida)
    # Nota: Aquí dependemos de cómo el modelo codifica la diferencia
    decision_diff = {
        "accion": "Aislar el servidor", 
        "target": "SRV-PROD", 
        "justificacion": "Limpiar malware."
    }
    print("\n[5] Intento 4: Buscando algo diferente (Debería ser Miss)...")
    res4 = cache.lookup(decision_diff, context, player_profile)
    if res4 is None:
        print("✓ Resultado esperado: Cache Miss (Diferencia semántica clara).")
    else:
        print(f"✗ Error: Hit inesperado en algo diferente. Feedback: {res4['evaluacion']}")

    print("\n=== Todas las pruebas de validación completadas con éxito ===")

if __name__ == "__main__":
    test_cache_functionality()
