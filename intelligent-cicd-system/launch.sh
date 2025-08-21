#!/bin/bash

# 🚀 Intelligent CI/CD System Launcher
# Launches the intelligent CI/CD system with proper setup

echo "🚀 Launching Intelligent CI/CD System..."
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the intelligent-cicd-system directory"
    echo "   cd intelligent-cicd-system && ./launch.sh"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    echo "   Please install Python 3.8+ and try again"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python $python_version is installed, but Python $required_version+ is required"
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if required CLI tools are available
echo "🔍 Checking required CLI tools..."

# Check gcloud
if ! command -v gcloud &> /dev/null; then
    echo "⚠️  Warning: Google Cloud CLI (gcloud) is not installed"
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
    echo "   The system will work but GCP features will be limited"
else
    echo "✅ Google Cloud CLI (gcloud) found"
fi

# Check gh
if ! command -v gh &> /dev/null; then
    echo "⚠️  Warning: GitHub CLI (gh) is not installed"
    echo "   Install from: https://cli.github.com/"
    echo "   The system will work but GitHub features will be limited"
else
    echo "✅ GitHub CLI (gh) found"
fi

# Check git
if ! command -v git &> /dev/null; then
    echo "⚠️  Warning: Git is not installed"
    echo "   Install from: https://git-scm.com/"
    echo "   The system will work but repository features will be limited"
else
    echo "✅ Git found"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "Installing Streamlit..."
    pip3 install -r requirements.txt
else
    echo "✅ Dependencies already installed"
fi

# Launch the system
echo ""
echo "🚀 Starting Intelligent CI/CD System..."
echo "🌐 Opening at: http://localhost:8501"
echo "🔄 Press Ctrl+C to stop"
echo ""

        # Launch Streamlit
        if [ -z "$VIRTUAL_ENV" ]; then
            source venv/bin/activate
        fi
        python3 -m streamlit run main.py --server.port 8501 --server.headless false
