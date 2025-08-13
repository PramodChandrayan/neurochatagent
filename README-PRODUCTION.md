# ABC Housing Finance Assistant - Production Deployment Guide

## 🚀 Overview

This is a production-ready AI-powered finance assistant built with Streamlit, OpenAI, and Pinecone. The application provides intelligent responses to housing finance queries using RAG (Retrieval-Augmented Generation).

## 🏗️ Architecture

- **Frontend**: Streamlit web application
- **AI Backend**: OpenAI GPT-4 for natural language processing
- **Vector Database**: Pinecone for document embeddings
- **Storage**: Local file system for chat history
- **Deployment**: Google Cloud Run (containerized)

## 📋 Prerequisites

- Google Cloud Platform account
- OpenAI API key
- Pinecone API key and index
- gcloud CLI installed and configured

## 🔧 Environment Variables

Create a `.env` file based on `env.production`:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east1-aws
PINECONE_INDEX_NAME=pdf-documents
PINECONE_NAMESPACE=housing-finance

# App Configuration
DEBUG=False
APP_VERSION=1.0.0

# Chat Configuration
MAX_CONTEXT_CHUNKS=5
CONFIDENCE_THRESHOLD=0.8

# File Storage
CHAT_STORAGE_DIR=chats

# Security
ALLOWED_HOSTS=*
```

## 🐳 Local Docker Testing

```bash
# Build image
docker build -t abc-housing-finance .

# Run locally
docker run -p 8080:8080 --env-file .env abc-housing-finance

# Test at http://localhost:8080
```

## ☁️ Google Cloud Run Deployment

### 1. Configure Project

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"

# Update deploy-cloud-run.sh with your project ID
sed -i "s/your-gcp-project-id/$PROJECT_ID/g" deploy-cloud-run.sh
```

### 2. Deploy

```bash
# Make script executable
chmod +x deploy-cloud-run.sh

# Run deployment
./deploy-cloud-run.sh
```

### 3. Set Environment Variables

In Google Cloud Console:
1. Go to Cloud Run > your-service
2. Edit & Deploy New Revision
3. Set environment variables from your `.env` file

## 📊 Monitoring & Logs

```bash
# View logs
gcloud logs tail --service=abc-housing-finance-assistant --region=us-central1

# Check service status
gcloud run services describe abc-housing-finance-assistant --region=us-central1
```

## 🔒 Security Considerations

- ✅ Non-root Docker user
- ✅ Environment variable configuration
- ✅ Health checks
- ✅ Resource limits
- ✅ HTTPS enforcement (Cloud Run)

## 📈 Scaling

- **Memory**: 2Gi (configurable)
- **CPU**: 2 vCPU (configurable)
- **Max Instances**: 10 (configurable)
- **Concurrency**: 80 requests per instance
- **Timeout**: 300 seconds

## 🚨 Troubleshooting

### Common Issues:

1. **Environment Variables Missing**
   - Check Cloud Run console
   - Verify `.env` file locally

2. **Pinecone Connection Failed**
   - Verify API key and environment
   - Check index exists

3. **OpenAI API Errors**
   - Verify API key
   - Check quota limits

4. **Build Failures**
   - Check Dockerfile syntax
   - Verify requirements.txt

## 📞 Support

For production issues:
1. Check Cloud Run logs
2. Verify environment configuration
3. Test locally with Docker
4. Check OpenAI and Pinecone status

## 🔄 Updates

To update the service:

```bash
# Rebuild and redeploy
./deploy-cloud-run.sh
```

## 📊 Performance Metrics

Monitor these metrics in Cloud Run:
- Request count
- Response time
- Error rate
- Memory usage
- CPU utilization
