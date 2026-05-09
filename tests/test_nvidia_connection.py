import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar model_configuration
sys.path.append(str(Path(__file__).parent.parent))

from model_configuration.llm_client import LLMClient

def test_nvidia_connection():
    load_dotenv()
    
    print("--- Verificando conexión con NVIDIA API Catalog ---")
    
    # Crear cliente configurado para NVIDIA
    client = LLMClient()
    client.switch_provider("nvidia")
    
    try:
        # Usar un prompt muy corto para no gastar créditos
        response = client.generate("Di 'Conexión exitosa' si puedes leerme.", system_prompt="Eres un asistente de pruebas.")
        print(f"\nRespuesta del modelo: {response}")
        
        if "Conexión exitosa" in response:
            print("\n[V] La integración con NVIDIA funciona correctamente.")
        else:
            print("\n[?] El modelo respondió pero no con la frase esperada.")
            
    except Exception as e:
        print(f"\n[X] Error al conectar con NVIDIA: {str(e)}")

if __name__ == "__main__":
    test_nvidia_connection()
