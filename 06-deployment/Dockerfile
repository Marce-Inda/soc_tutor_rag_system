# Docker image for SOC Tutor RAG System
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (layer caching)
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY src/ ./src/
COPY 03_configuracion_de_modelos/ ./03_configuracion_de_modelos/
COPY 04_integracion_de_herramientas/ ./04_integracion_de_herramientas/
COPY data/ ./data/
COPY config/ ./config/

# Create indices directory if not exists
RUN mkdir -p /app/data/indices

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]