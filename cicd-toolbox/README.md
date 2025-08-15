# 🧠 Intelligent CI/CD Toolbox

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/your-repo/intelligent-cicd-toolbox)

> **Project-agnostic CI/CD automation toolbox with intelligent analysis**

The Intelligent CI/CD Toolbox automatically detects your project requirements, sets up cloud infrastructure, manages secrets, and provides pipeline control - all with real-time feedback and minimal manual intervention.

## ✨ Features

### 🧠 **Intelligent Project Analysis**
- **Auto-detection** of project type (Python, Node.js, Java, Go, Rust, Ruby)
- **Framework recognition** (Streamlit, Flask, Django, React, Express, etc.)
- **Secret discovery** from dependencies, config files, and source code
- **Cloud provider detection** (GCP, AWS, Azure, Docker)
- **Smart recommendations** based on project analysis

### ☁️ **Multi-Cloud Infrastructure Setup**
- **GCP Cloud Run** (fully implemented)
- **AWS ECS/Fargate** (coming soon)
- **Azure Container Instances** (coming soon)
- **Automatic API enabling** and service account creation
- **Workload Identity Federation** setup for secure authentication

### 🔑 **Intelligent Secrets Management**
- **Runtime secrets detection** (OpenAI, Pinecone, database credentials)
- **CI/CD secrets generation** (project IDs, service accounts, WIF providers)
- **Automatic GitHub integration** using GitHub CLI
- **One-click secrets pushing** to GitHub Actions

### 🚀 **Pipeline Control & Deployment Strategy**
- **Environment management** (staging → development → production)
- **Step filtering** (skip tests, linting, security scans, etc.)
- **Fast-track deployment** options
- **Pipeline triggering** with commit-based automation

### 📊 **Real-Time Feedback & Monitoring**
- **Execution logging** with timestamps and status
- **Progress tracking** for all operations
- **Error handling** with context-aware troubleshooting
- **Summary reports** of completed steps
- **Next steps guidance** based on current progress

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/intelligent-cicd-toolbox.git
cd intelligent-cicd-toolbox

# Install the package
pip install -e .

# Or install with GUI support
pip install -e .[gui]
```

### Basic Usage

```python
from intelligent_cicd_toolbox import IntelligentProjectAnalyzer, IntelligentCICDToolbox

# Analyze your project
analyzer = IntelligentProjectAnalyzer(".")
project_requirements = analyzer.analyze_project()

# Setup CI/CD infrastructure
toolbox = IntelligentCICDToolbox()
toolbox.project_analysis = project_requirements

# Configure GCP project
toolbox.set_project("your-gcp-project-id")

# Setup infrastructure
toolbox.setup_infrastructure("your-gcp-project-id")

# Generate and push secrets
secrets = toolbox.generate_secrets_template("your-gcp-project-id")
toolbox.push_secrets_to_github()

# Trigger pipeline
toolbox.trigger_pipeline(environment="staging")
```

### GUI Usage

```bash
# Launch the enhanced GUI
streamlit run intelligent_cicd_toolbox/gui.py

# Or use the launcher script
./launch-enhanced-gui.sh
```

## 📋 Requirements

### System Requirements
- **Python 3.8+**
- **Git** (for repository operations)
- **Google Cloud CLI** (`gcloud`) for GCP operations
- **GitHub CLI** (`gh`) for secrets management

### Authentication Setup
```bash
# Google Cloud authentication
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# GitHub CLI authentication
gh auth login
```

## 🏗️ Architecture

```
intelligent-cicd-toolbox/
├── __init__.py              # Package initialization
├── analyzer.py              # Intelligent project analyzer
├── toolbox.py               # Core CI/CD toolbox
├── gui.py                   # Streamlit-based GUI
├── cli.py                   # Command-line interface
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
└── README.md               # This file
```

### Core Components

1. **`IntelligentProjectAnalyzer`**: Analyzes project structure and requirements
2. **`IntelligentCICDToolbox`**: Handles infrastructure setup and pipeline control
3. **`EnhancedCICDGUI`**: User-friendly Streamlit interface
4. **CLI Interface**: Command-line automation capabilities

## 🔧 Configuration

### Environment Variables

```bash
# GCP Configuration
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="asia-south1"

# GitHub Configuration
export GITHUB_TOKEN="your-github-token"
export GITHUB_REPOSITORY="owner/repo"
```

### Project-Specific Configuration

The toolbox automatically detects and configures:
- **Dependencies** from `requirements.txt`, `package.json`, `pom.xml`, etc.
- **Configuration files** like `.env`, `.yaml`, `.json`, `.toml`
- **Source code patterns** for environment variable usage
- **Deployment configurations** (Docker, Kubernetes, Terraform)

## 📚 Examples

### Python Streamlit Application

```python
# The toolbox automatically detects:
# - Python project with Streamlit framework
# - Required secrets: OPENAI_API_KEY, PINECONE_API_KEY
# - Deployment: Docker containerization
# - Cloud: GCP Cloud Run ready

analyzer = IntelligentProjectAnalyzer(".")
requirements = analyzer.analyze_project()

print(f"Project Type: {requirements['project_info']['type']}")
print(f"Framework: {requirements['project_info']['framework']}")
print(f"Runtime Secrets: {requirements['runtime_secrets']}")
```

### Node.js React Application

```python
# The toolbox automatically detects:
# - Node.js project with React framework
# - Required secrets: REACT_APP_API_KEY, DATABASE_URL
# - Deployment: Docker + Kubernetes ready
# - Cloud: Multi-cloud deployment options

analyzer = IntelligentProjectAnalyzer(".")
requirements = analyzer.analyze_project()

print(f"Project Type: {requirements['project_info']['type']}")
print(f"Framework: {requirements['project_info']['framework']}")
print(f"Deployment: {requirements['deployment_configs']}")
```

## 🚀 Deployment Workflow

### 1. Project Analysis
```bash
# Analyze project requirements
intelligent-cicd analyze
```

### 2. Infrastructure Setup
```bash
# Setup GCP infrastructure
intelligent-cicd setup gcp --project-id your-project-id
```

### 3. Secrets Management
```bash
# Generate secrets template
intelligent-cicd secrets generate

# Push to GitHub
intelligent-cicd secrets push
```

### 4. Pipeline Control
```bash
# Trigger pipeline
intelligent-cicd trigger --environment staging --skip-tests
```

## 🔍 Troubleshooting

### Common Issues

#### GCP Authentication
```bash
# Check authentication status
gcloud auth list

# Re-authenticate if needed
gcloud auth login
```

#### GitHub CLI Issues
```bash
# Check authentication status
gh auth status

# Re-authenticate if needed
gh auth login
```

#### Workload Identity Federation
```bash
# Clean up existing WIF resources
gcloud iam workload-identity-pools providers delete github-actions-provider \
  --workload-identity-pool=github-actions-pool \
  --location=global

gcloud iam workload-identity-pools delete github-actions-pool \
  --location=global
```

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with verbose output
toolbox = IntelligentCICDToolbox()
toolbox.log_execution("Debug", "Detailed logging enabled", "info")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/your-repo/intelligent-cicd-toolbox.git
cd intelligent-cicd-toolbox

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black intelligent_cicd_toolbox/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud Platform** for Cloud Run and Workload Identity Federation
- **GitHub Actions** for CI/CD pipeline automation
- **Streamlit** for the beautiful GUI framework
- **Open Source Community** for inspiration and feedback

## 📞 Support

- **Documentation**: [Wiki](https://github.com/your-repo/intelligent-cicd-toolbox/wiki)
- **Issues**: [GitHub Issues](https://github.com/your-repo/intelligent-cicd-toolbox/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/intelligent-cicd-toolbox/discussions)

---

**Made with ❤️ by the Intelligent CI/CD Toolbox Team**

*Transform your CI/CD workflow from manual to magical! 🚀✨*
