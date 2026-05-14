import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar desde src
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.llm_client import LLMClient

async def test_nvidia_connection():
    load_dotenv()
    
    print("--- 🚀 Verificando Conexión con NVIDIA API Catalog (Llama-405B) ---")
    
    # Crear cliente configurado para NVIDIA
    # El modelo por defecto en el código es meta/llama-3.3-70b-instruct
    client = LLMClient(provider="nvidia")
    
    try:
        # Usar un prompt corto para validación
        print(f" [Test] Llamando a NVIDIA NIM con el modelo: {client.model or 'meta/llama-3.3-70b-instruct'}...")
        response = await client.generate(
            "Di 'CONEXIÓN EXITOSA' y dime qué modelo eres.", 
            system_prompt="Eres un validador técnico de infraestructura."
        )
        
        print(f"\nRespuesta de NVIDIA:\n{'-'*30}\n{response}\n{'-'*30}")
        
        if "CONEXIÓN EXITOSA" in response.upper():
            print("\n✅ ¡PRUEBA SUPERADA! La API Key de NVIDIA funciona correctamente.")
            print(f"   Tokens usados en test: {client.last_usage['input_tokens'] + client.last_usage['output_tokens']}")
        else:
            print("\n⚠️ El modelo respondió pero no incluyó la frase de validación.")
            
    except Exception as e:
        import traceback
        print(f"\n❌ ERROR DE CONEXIÓN:")
        traceback.print_exc()
        print("\nSugerencia: Revisa que NVIDIA_API_KEY esté correctamente configurada en el archivo .env")

if __name__ == "__main__":
    asyncio.run(test_nvidia_connection())
