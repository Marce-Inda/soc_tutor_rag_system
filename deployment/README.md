# Deployment

## Contenido

```
06-deployment/
├── Dockerfile                 # Contenedor Docker
├── docker-compose.yml         # Orquestación local
├── .dockerignore             # Archivos a ignorar
├── requirements-prod.txt     # Dependencias production
├── app/
│   └── main.py              # API FastAPI
├── cloudbuild.yaml          # GCP Cloud Build
├── deploy.sh                # Script de despliegue
└── README.md
```

## Opciones de Deployment

### Opción 1: Cloud Functions (GCP) - Recomendado
- Costo: Free tier generoso
- Escala automática
-Ideal para API stateless

### Opción 2: Cloud Run
- Más control
- Costo: $0.40/1M invocaciones
- Flexible

### Opción 3: Docker local (testing)
- Para desarrollo y testing

## Uso Rápido

```bash
# 1. Construir imagen
docker build -t soc-tutor-rag:latest .

# 2. Ejecutar localmente
docker-compose up

# 3. Probar API
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"decision": {...}, "contexto": {...}, "player_profile": {...}}'
```

## API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/feedback` | Generar feedback |
| GET | `/health` | Health check |
| GET | `/stats` | Estadísticas del sistema |

## Variables de Entorno (Production)

```bash
GEMINI_API_KEY=...
GOOGLE_APPLICATION_CREDENTIALS=...
RAG_INDEX_PATH=/app/data/indices
LOG_LEVEL=INFO
```

## Notas

- El índice Chroma debe estar en `/app/data/indices`
- Los documentos RAG se cargan al inicio
- Timeout configurado para 30s por request