import requests
import time
import json

BASE_URL = "http://localhost:7860"
USER_ID = "test_user_1"

def run_smoke_test():
    print(f"--- Iniciando Prueba de Lógica Multi-Agente (User: {USER_ID}) ---")
    
    # 1. Entrar en la cola y esperar a estar ACTIVO
    while True:
        status_resp = requests.get(f"{BASE_URL}/queue/status/{USER_ID}")
        status_data = status_resp.json()
        status = status_data.get("status")
        pos = status_data.get("position")
        codename = status_data.get("codename")
        
        print(f"Estado en la cola: {status} | Posición: {pos} | Codename: {codename}")
        
        if status == "ACTIVE":
            print("¡Ya estamos en el SOC! Procediendo con la solicitud de feedback...")
            break
        
        time.sleep(2)

    # 2. Enviar solicitud de feedback
    payload = {
        "decision": {
            "accion": "isolate_host",
            "target": "192.168.1.50",
            "detalle": "Isolated compromised workstation after detecting C2 beaconing"
        },
        "contexto": {
            "tipo_incidente": "malware",
            "fase": "containment",
            "sistemas_afectados": ["WS-01"],
            "score": 0
        },
        "player_profile": {
            "player_id": USER_ID,
            "level": 3,
            "rol": "analyst",
            "language": "es"
        }
    }

    start_time = time.time()
    response = requests.post(f"{BASE_URL}/feedback?user_id={USER_ID}", json=payload)
    end_time = time.time()

    if response.status_code == 200:
        result = response.json()
        print("\n--- RESULTADO DEL FEEDBACK ---")
        print(f"Evaluación: {result.get('evaluacion')}")
        print(f"Puntaje Técnico: {result.get('score_tecnico')}")
        print(f"Fuentes Citadas: {result.get('fuentes_citadas')}")
        print(f"Latencia: {result.get('latencia_ms')}ms")
        print(f"Costo Estimado: ${result.get('costo_estimado')}")
        print(f"Rol del Mentor: {result.get('persona_role')}")
        print(f"Aprobado por Juez Supremo: {result.get('aprobado')}")
        print("------------------------------")
        print(f"\nPrueba completada con éxito en {end_time - start_time:.2f} segundos.")
    else:
        print(f"\n[X] Error en la solicitud: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    run_smoke_test()
