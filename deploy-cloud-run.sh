#!/bin/bash

# Google Cloud Run Deployment Script for ABC Housing Finance Assistant
# Make sure you have gcloud CLI installed and configured

set -e

# Configuration
PROJECT_ID="neurofinance-468916"
REGION="asia-south1"
SERVICE_NAME="neurogent-finance-assistant"
IMAGE_NAME="asia-south1-docker.pkg.dev/$PROJECT_ID/neurogent-repo/$SERVICE_NAME"

echo "🚀 Starting deployment to Google Cloud Run..."

# Check if gcloud is configured
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Error: gcloud CLI not configured. Please run 'gcloud auth login' first."
    exit 1
fi

# Set project
echo "📋 Setting GCP project to: $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and push Docker image
echo "🐳 Building and pushing Docker image..."
gcloud builds submit --tag $IMAGE_NAME

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --timeout 300 \
    --concurrency 80 \
    --set-env-vars="DEBUG=False" \
    --set-env-vars="STREAMLIT_SERVER_PORT=8080" \
    --set-env-vars="STREAMLIT_SERVER_ADDRESS=0.0.0.0"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: $SERVICE_URL"
echo ""
echo "📝 Next steps:"
echo "1. Set environment variables in Cloud Run console:"
echo "   - OPENAI_API_KEY"
echo "   - PINECONE_API_KEY"
echo "   - PINECONE_ENVIRONMENT"
echo "2. Test the service at: $SERVICE_URL"
echo "3. Monitor logs: gcloud logs tail --service=$SERVICE_NAME --region=$REGION"
