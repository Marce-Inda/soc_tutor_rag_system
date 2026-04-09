#!/bin/bash
# Script de despliegue - GCP Cloud Functions / Cloud Run
# Uso: ./deploy.sh [cloudrun|functions]

set -e

PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="soc-tutor-rag"

echo "=========================================="
echo "Deployment - SOC Tutor RAG System"
echo "=========================================="

# Verificar GCP CLI
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI no está instalado"
    exit 1
fi

# Verificar autenticación
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "Error: No hay cuenta de GCP autenticada"
    echo "Ejecuta: gcloud auth login"
    exit 1
fi

# Función para deploy a Cloud Run
deploy_cloudrun() {
    echo "\n[1/3] Construyendo imagen..."
    gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest" .
    
    echo "\n[2/3] Desplegando a Cloud Run..."
    gcloud run deploy "$SERVICE_NAME" \
        --image "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY,LOG_LEVEL=INFO"
    
    echo "\n[3/3] Obteniendo URL..."
    gcloud run describe "$SERVICE_NAME" --platform managed --region "$REGION" --format="value(status.url)"
}

# Función para deploy a Cloud Functions (gen2)
deploy_functions() {
    echo "\n[1/2] Desplegando Cloud Functions..."
    
    gcloud functions deploy "$SERVICE_NAME" \
        --runtime python310 \
        --trigger-http \
        --entry-point main \
        --region "$REGION" \
        --set-env-vars "GEMINI_API_KEY=$GEMINI_API_KEY,LOG_LEVEL=INFO" \
        --allow-unauthenticated
    
    echo "\n[2/2] Obteniendo URL..."
    gcloud functions describe "$SERVICE_NAME" --region "$REGION" --format="value(url)"
}

# Main
MODE="${1:-cloudrun}"

case "$MODE" in
    cloudrun)
        deploy_cloudrun
        ;;
    functions)
        deploy_functions
        ;;
    *)
        echo "Uso: $0 [cloudrun|functions]"
        exit 1
        ;;
esac

echo "\n✓ Deployment completado"