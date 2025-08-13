# 🚀 NeuroGent Finance Assistant

A sophisticated AI-powered financial knowledge base chatbot built with Streamlit, OpenAI, and Pinecone vector database.

## ✨ Features

- **📚 PDF Processing**: Convert financial documents to searchable embeddings
- **🧠 AI Chatbot**: Intelligent responses using OpenAI GPT-4 with RAG (Retrieval-Augmented Generation)
- **🔍 Vector Search**: Fast semantic search using Pinecone vector database
- **💬 Persistent Chat**: Save and restore chat sessions
- **🎨 Modern UI**: ChatGPT-like interface built with Streamlit
- **☁️ Cloud Ready**: Deployable to Google Cloud Run

## 🏗️ Architecture

```
User Query → Streamlit UI → OpenAI GPT-4 → Pinecone Vector Search → Context Retrieval → Response Generation
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI/LLM**: OpenAI GPT-4
- **Vector Database**: Pinecone
- **PDF Processing**: PyPDF2
- **Backend**: Python 3.11
- **Deployment**: Docker + Google Cloud Run
- **Region**: Asia-south1 (Mumbai)

## 📋 Prerequisites

- Python 3.11+
- OpenAI API Key
- Pinecone API Key
- Google Cloud Project (for deployment)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/PramodChandrayan/neurochatagent.git
cd neurochatagent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Environment Variables
Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=your_pinecone_index_name
```

### 4. Run Locally
```bash
streamlit run streamlit_app.py
```

## 📖 Usage

### 1. Upload PDF Documents
- Use the sidebar to upload financial PDF documents
- The system will automatically process and create embeddings

### 2. Chat with Your Knowledge Base
- Ask questions about your financial documents
- Get intelligent, context-aware responses
- View source documents and confidence scores

### 3. Manage Chat Sessions
- Start new conversations
- View chat history
- Delete old sessions

## 🐳 Docker Deployment

### Build and Run Locally
```bash
docker build -t neurogent-finance-assistant .
docker run -p 8080:8080 neurogent-finance-assistant
```

### Deploy to Google Cloud Run
```bash
chmod +x deploy-cloud-run.sh
./deploy-cloud-run.sh
```

## 🔧 Configuration

Key configuration options in `config.py`:
- OpenAI model selection
- Pinecone index settings
- Chat parameters
- File storage settings

## 📁 Project Structure

```
neurochatagent/
├── streamlit_app.py          # Main Streamlit application
├── finance_chatbot.py        # Core chatbot logic
├── pdf_to_embeddings.py      # PDF processing and embedding
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── deploy-cloud-run.sh      # GCP deployment script
├── README.md                # This file
└── chats/                   # Chat session storage
```

## 🔐 Security

- Environment variables for sensitive data
- No hardcoded API keys
- Secure Docker configuration
- Production-ready deployment

## 🚀 Deployment

### Google Cloud Run
1. Enable required APIs
2. Set up Artifact Registry
3. Configure IAM permissions
4. Run deployment script

### Environment Variables for Production
- `OPENAI_API_KEY`: Your OpenAI API key
- `PINECONE_API_KEY`: Your Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment
- `PINECONE_INDEX_NAME`: Pinecone index name

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: hello@neurogent.ai

## 🔄 Updates

- **v1.0.0**: Initial release with basic functionality
- **v1.1.0**: Added persistent chat sessions
- **v1.2.0**: Enhanced UI with ChatGPT-like design
- **v1.3.0**: Production deployment to Google Cloud Run

---

Built with ❤️ by [NeuroGent](https://neurogent.ai)
