import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

def list_nvidia_models():
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        print("Error: NVIDIA_API_KEY no encontrada.")
        return

    print("--- Consultando modelos disponibles en NVIDIA API Catalog ---")
    
    url = "https://integrate.api.nvidia.com/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            models = response.json().get("data", [])
            print(f"\nSe encontraron {len(models)} modelos:")
            # Filtrar por deepseek o llama para no saturar
            for m in models:
                mid = m.get("id")
                if "deepseek" in mid.lower() or "llama-3" in mid.lower():
                    print(f"  - {mid}")
        else:
            print(f"\nError al consultar modelos: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"\nError de conexión: {str(e)}")

if __name__ == "__main__":
    list_nvidia_models()
