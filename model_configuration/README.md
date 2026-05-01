# Configuración de Modelos

## Contenido

```
model_configuration/
├── llm_config.py       # Definición de configuraciones
├── llm_client.py       # Cliente unificado (Gemini/Groq/DeepSeek)
├── config.json        # Configuración JSON
└── README.md
```

## Proveedores Soportados

| Proveedor | Modelo | Velocidad | Costo (por 1M tokens) | Rol |
|-----------|--------|------------|-------|------|
| **Google Gemini** | `gemini-2.5-flash` | Rápido | $0.15 input / $0.60 output | **Primario** |
| **Groq** | `llama-3.3-70b-versatile` | Muy rápido | $0.50 input / $0.80 output | **Fallback** |
| **DeepSeek** | `deepseek-chat` (V4 Flash) | Rápido | $0.14 input / $0.28 output | **Emergencia** |
| **Ollama** | `llama3` (local) | Variable | $0.00 | **Desarrollo** |

## Cascada de Resiliencia (3 Capas)

```
Capa 1: Provider Primario (Gemini 2.5 Flash)
    ↓ falla
Capa 2: Fallback Bidireccional (Groq ↔ Gemini)
    ↓ falla
Capa 3: Red de Seguridad (DeepSeek V4 Flash)
    ↓ falla
Capa 4: Graceful Degradation (JSON determinista)
```

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
# Para Gemini (Primario)
export GEMINI_API_KEY="tu-api-key-aqui"

# Para Groq (Fallback)
export GROQ_API_KEY="tu-api-key-aqui"

# Para DeepSeek V4 (Emergencia — Opcional)
# Obtener en: https://platform.deepseek.com/api_keys
export DEEPSEEK_API_KEY="tu-api-key-aqui"
```

## Uso

```python
from src.utils.llm_client import create_llm_client

# Crear cliente con provider primario (Gemini)
client = create_llm_client(provider="gemini")

# Crear cliente con DeepSeek como primario
client = create_llm_client(provider="deepseek")

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

| Operación | Costo (Gemini) | Costo (DeepSeek) |
|-----------|-------|-------|
| Retrieval RAG | $0 (local) | $0 (local) |
| Agente Analista | $0.0002 | $0.00018 |
| Agente Explicador | $0.0002 | $0.00018 |
| Agente Validador | $0.0002 | $0.00018 |
| **Total** | **~$0.0006** | **~$0.00054** |

## Alternativas

Si no tienes API keys, puedes usar:
1. **Ollama local** - modelos open source
2. **OpenRouter** - agregador con modelos gratuitos
3. **Fallback determinista** - respuestas predefinidas (se activa automáticamente)