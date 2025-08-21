# 🚀 Intelligent CI/CD Toolbox

A comprehensive, intelligent CI/CD automation toolbox built with Streamlit that handles GCP setup, GitHub configuration, and pipeline management automatically.

## ✨ Features

- **🔐 Smart Authentication**: Automatically detects and configures GCP and GitHub CLI access
- **🏗️ Intelligent GCP Setup**: Creates service accounts, IAM roles, and Workload Identity Federation
- **🔑 GitHub Secrets Management**: Automatically configures all required secrets
- **📊 Live Pipeline Monitoring**: Real-time status tracking and logging
- **🛠️ Error Prevention**: Smart detection and handling of common issues
- **🎯 User Experience**: Designed for both fresh and returning users

## 🚀 Quick Start

1. **Navigate to the toolbox directory:**
   ```bash
   cd cicd-toolbox
   ```

2. **Launch the toolbox:**
   ```bash
   ./launch.sh
   ```

3. **Open your browser:**
   Navigate to `http://localhost:8501`

## 📋 Prerequisites

- Python 3.8+
- Google Cloud CLI (`gcloud`)
- GitHub CLI (`gh`)
- Streamlit

## 🔧 What It Does

### Step 1: Smart Authentication
- Detects CLI tools and authentication status
- Provides guidance for missing tools
- Auto-authenticates when possible

### Step 2: Project Analysis
- Scans existing GCP resources
- Identifies missing components
- Provides intelligent recommendations

### Step 3: GCP Infrastructure
- Creates service accounts with proper permissions
- Sets up Workload Identity Federation
- Enables required APIs

### Step 4: GitHub Configuration
- Configures all required secrets
- Sets up proper authentication
- Validates configuration

### Step 5: Pipeline Management
- Live status monitoring
- Pipeline triggering
- Detailed logging and error tracking

## 🎯 Use Cases

- **Fresh Setup**: Complete CI/CD pipeline setup from scratch
- **Returning Users**: Quick status check and issue resolution
- **Troubleshooting**: Detailed error analysis and fixes
- **Monitoring**: Live pipeline status and performance tracking

## 🏗️ Architecture

Built with:
- **Streamlit**: Modern, responsive web interface
- **GCP APIs**: Direct integration with Google Cloud services
- **GitHub APIs**: Seamless GitHub Actions management
- **Smart Logic**: Intelligent error handling and user guidance

## 📁 File Structure

```
cicd-toolbox/
├── intelligent-cicd-toolbox-v2.py  # Main application
├── launch.sh                        # Launch script
└── README.md                        # This file
```

## 🚨 Troubleshooting

If you encounter issues:

1. **Check CLI tools**: Ensure `gcloud` and `gh` are installed and authenticated
2. **Verify permissions**: Ensure your GCP account has necessary IAM roles
3. **Check network**: Ensure connectivity to GCP and GitHub APIs
4. **Review logs**: Use the detailed logging in the toolbox

## 🤝 Contributing

This toolbox is designed to be self-contained and focused. For modifications:

1. Edit `intelligent-cicd-toolbox-v2.py`
2. Test thoroughly
3. Update this README if needed

## 📄 License

Part of the NeuroGent Finance Assistant project.
