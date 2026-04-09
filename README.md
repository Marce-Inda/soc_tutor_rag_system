# SOC-Tutor-RAG System

Sistema multiagente de feedback pedagógico con RAG para entrenamiento en respuesta a incidentes de ciberseguridad.

## Descripción

Este sistema proporciona feedback contextualizado a jugadores del simulador SOC "The Responder", fundamentado en documentación técnica real (MITRE ATT&CK, NIST 800-61, OWASP, CISA).

## Características

- **3 agentes especializados**: Analista (ReAct), Explicador (pedagógico), Validador (verificación)
- **RAG avanzado**: Retrieval con ChromaDB y Sentence-Transformers
- **Agente Tool-Augmented**: Analista con capacidad de razonamiento ReAct y herramientas (NIST, MITRE)
- **Observabilidad**: Rastreo de latencia, tokens y costos (Traces locales)
- **Persistencia**: Memoria de sesión para seguimiento de aprendizaje
- **Seguridad**: Guardrails contra inyección y validación de Pydantic
- **Evaluación**: Dataset sintético y script de métricas de calidad

## Estructura

```
soc-tutor-rag-system/
├── src/
│   ├── agentes/        # Implementación de los 3 agentes
│   ├── orchest/        # Orquestador del sistema
│   ├── rag/            # Módulo de retrieval y vector store
│   └── utils/          # Utilidades
├── config/             # Configuraciones (LLM, paths)
├── data/
│   ├── docs/           # Documentos fuente para RAG
│   └── indices/        # Índices vectoriales
└── tests/              # Tests unitarios y de integración
```

## Uso

```python
from orchest.uefs_orchestrator import UEFSOrchestrator

orchestrator = UEFSOrchestrator()
feedback = orchestrator.generar_feedback(
    decision={"accion": "bloquear_ip", "ip": "192.168.1.100"},
    contexto={"tipo_incidente": "phishing", "fase": "contencion"}
)
```

## Arquitectura General

El sistema se basa en un flujo de orquestación (Pipeline):
1. **Entrada**: Acción del jugador (ej. "Bloquear IP").
2. **Retrieval**: El RAGClient busca evidencia en logs estáticos del juego simulado y en lineamientos oficiales.
3. **Agente Analista (ReAct)**: Usa herramientas para cruzar la decisión del jugador con la evidencia encontrada.
4. **Agente Explicador**: Convierte el análisis en feedback pedagógico.
5. **Agente Validador**: Asegura que el feedback cite manuales reales y no alucine.

## Instrucciones de Instalación (Local)

1. Clonar el repositorio.
2. Copiar el archivo de entorno y agregar tus credenciales:
   ```bash
   cp .env.example .env
   ```
3. Crear un entorno virtual e instalar las dependencias:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Población de la Base Vectorial (Ingesta de Logs del Juego y Manuales):
   ```bash
   python scripts/ingest_game_evidence.py
   ```

## Uso y Reproducción

Para correr una demostración integrada del pipeline:
```bash
python demo_integrated.py
```

Para correr la suite de pruebas (Unitarias y de Integración):
```bash
python -m unittest discover tests/
```

## Despliegue con Docker

El proyecto está dockerizado para facilitar el despliegue.
1. Asegúrate de tener tus claves en el archivo `.env`.
2. Construye y levanta los servicios usando Docker Compose:
   ```bash
   docker-compose up --build -d
   ```
3. Para detener el sistema:
   ```bash
   docker-compose down
   ```