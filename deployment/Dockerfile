# Docker image for SOC Tutor RAG System
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY deployment/requirements-prod.txt ./requirements-prod.txt
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY src/ ./src/
COPY model_configuration/ ./model_configuration/
COPY tool_integration/ ./tool_integration/
COPY data/ ./data/
COPY data_ingestion/ ./data_ingestion/
COPY config/ ./config/
COPY deployment/app/ ./app/

# Create indices directory if not exists
RUN mkdir -p /app/data/indices

# Security: Crear usuario no-root (Principio de Mínimos Permisos)
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HOME=/tmp

# Security: Ejecutar como usuario no privilegiado
USER appuser

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]