# Integración de Herramientas

## Contenido

```
04-integracion-de-herramientas/
├── requirements.txt    # Dependencias del proyecto
├── rag_client.py       # Cliente RAG con Chroma
├── langchain_setup.py  # Setup de LangChain
└── README.md
```

## Instalación

```bash
pip install -r requirements.txt
```

## Tecnologías

| Herramienta | Uso | Costo |
|-------------|-----|-------|
| **LangChain** | Orquestación de agentes | $0 (open source) |
| **Chroma** | Vector store | $0 (local) |
| **sentence-transformers** | Embeddings | $0 (local) |

## Uso

### RAG Client

```python
from rag_client import create_rag_client

# Crear cliente
rag = create_rag_client()

# Recuperar conocimiento
result = rag.retrieve_with_context(
    decision={"accion": "bloquear_ip"},
    contexto={"tipo_incidente": "phishing"}
)

print(result["contexto_rag"])
print(result["fuentes"])
```

### LangChain Setup

```python
from langchain_setup import create_langchain_setup

# Inicializar
setup = create_langchain_setup()

# Usar chains
result = setup.invoke_chain("analista", {
    "decision": {"accion": "bloquear_ip", "target": "192.168.1.1"},
    "contexto": {"tipo_incidente": "phishing", "fase": "contencion"},
    "contexto_rag": "..."
})
```

## Estructura de Archivos del Proyecto

```
soc-tutor-rag-system/
├── 01-ingenieria-de-prompts/     # ✅ Completado
├── 02-ingestion-datos/            # ✅ Completado
├── 03-configuracion-de-modelos/   # ✅ Completado
├── 04-integracion-de-herramientas/  # 🔄 Actual
├── src/
│   ├── agentes/                   # 📋 Prompts y tipos
│   └── ...
├── data/
│   ├── docs/                     # 📥 Documentos RAG
│   └── indices/                  # 📊 Índices Chroma
└── tests/
```