# 🧠 NeuroGent Finance Assistant

An intelligent finance chatbot powered by OpenAI and Pinecone, with automated CI/CD deployment to Google Cloud Platform.

## ✨ Features

- **🤖 AI-Powered Finance Assistant**: Built with OpenAI GPT models
- **🔍 Document Intelligence**: PDF processing and semantic search with Pinecone
- **🌐 Web Interface**: Modern Streamlit-based user interface
- **🚀 Automated Deployment**: Full CI/CD pipeline with GitHub Actions
- **☁️ Cloud-Native**: Deployed on Google Cloud Run

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the chatbot:**
   ```bash
   streamlit run streamlit_app.py
   ```

### CI/CD Toolbox

For automated deployment setup:

```bash
cd cicd-toolbox
./launch.sh
```

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key
- Pinecone API key and index
- Google Cloud Platform account (for deployment)

## 🏗️ Architecture

- **Frontend**: Streamlit web interface
- **AI Engine**: OpenAI GPT models
- **Vector Database**: Pinecone for semantic search
- **Deployment**: Google Cloud Run via CI/CD pipeline
- **CI/CD**: GitHub Actions with Workload Identity Federation

## 📁 Project Structure

```
├── finance_chatbot.py          # Core chatbot logic
├── streamlit_app.py            # Web interface
├── pdf_to_embeddings.py        # PDF processing
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
├── cicd-toolbox/              # CI/CD automation toolbox
│   ├── intelligent-cicd-toolbox-v2.py
│   ├── launch.sh
│   └── README.md
├── .github/workflows/          # CI/CD pipeline definitions
└── tests/                      # Test suite
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=your_index_name
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### GCP Deployment

The CI/CD pipeline automatically:
- Builds and pushes Docker images
- Deploys to Cloud Run
- Manages environment variables
- Handles scaling and monitoring

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

## 📊 Monitoring

- **Application**: Cloud Run metrics and logs
- **Pipeline**: GitHub Actions workflow status
- **Toolbox**: Live monitoring dashboard

## 🚨 Troubleshooting

### Common Issues

1. **API Key Errors**: Verify environment variables are set correctly
2. **Pinecone Connection**: Check API key and environment settings
3. **Deployment Failures**: Use the CI/CD toolbox for diagnostics

### Getting Help

- Check the CI/CD toolbox for deployment issues
- Review GitHub Actions workflow logs
- Verify GCP service account permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is part of the NeuroGent Finance Assistant platform.

## 🔗 Links

- [CI/CD Toolbox Documentation](cicd-toolbox/README.md)
- [Deployment Guide](DEPLOYMENT-READINESS-CHECKLIST.md)
- [Required Secrets](REQUIRED-SECRETS.md)
