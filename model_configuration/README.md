# Configuración de Modelos

## Contenido

```
03-model-configuration/
├── llm_config.py       # Definición de configuraciones
├── llm_client.py       # Cliente unificado (Gemini/Groq)
├── config.json        # Configuración JSON
└── README.md
```

## Proveedores Soportados

| Proveedor | Modelo | Velocidad | Costo | Notas |
|-----------|--------|------------|-------|-------|
| **Google Gemini** | 1.5 Flash | Rápido | $0 (free tier) | Preferido |
| **Groq** | Llama 3.1 8B | Muy rápido | $0 (free tier) | Fallback |

## Parámetros Recomendados

```python
{
  "temperature": 0.3,      # Bajo para reducir alucinaciones
  "max_tokens": 512,        # Suficiente para feedback conciso
  "top_p": 0.8,
  "top_k": 40
}
```

## Variables de Entorno

```bash
# Para Gemini
export GEMINI_API_KEY="tu-api-key-aqui"

# Para Groq (alternativa)
export GROQ_API_KEY="tu-api-key-aqui"
```

## Uso

```python
from llm_client import create_client

# Crear cliente (usa config por defecto)
client = create_client()

# Generar respuesta
response = client.generate(
    prompt="¿Qué técnicas MITRE usa un ransomware?",
    system_prompt="Eres un experto en ciberseguridad."
)

# Generar JSON
result = client.generate_json(
    prompt="Evalúa esta decisión técnica",
    system_prompt="Responde en formato JSON"
)
```

## Costo Estimado por Sesión

| Operación | Costo |
|-----------|-------|
| Retrieval RAG | $0 (local) |
| Agente Analista | $0.0002 |
| Agente Explicador | $0.0002 |
| Agente Validador | $0.0002 |
| **Total** | **~$0.0006** |

## Alternativas

Si no tienes API keys, puedes usar:
1. **Ollama local** - modelos open source
2. **HuggingFace** - endpoints gratuitos
3. **Fallback determinista** - respuestas predefinidas