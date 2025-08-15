#!/bin/bash

# 🚀 Intelligent CI/CD Toolbox Launcher
# This script launches the highly intelligent, fully automated CI/CD toolbox

echo "🚀 Launching Intelligent CI/CD Toolbox..."
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "intelligent-cicd-toolbox.py" ]; then
    echo "❌ Error: Intelligent toolbox not found!"
    echo "Please ensure you're in the cicd-toolbox directory."
    exit 1
fi

# Check requirements
echo "🔍 Checking requirements..."

if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found"
    echo "Please install Google Cloud SDK first"
    exit 1
fi

if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI not found"
    echo "Please install GitHub CLI first"
    exit 1
fi

if ! command -v streamlit &> /dev/null; then
    echo "⚠️ Streamlit not found. Installing..."
    pip install streamlit
fi

echo "✅ All requirements satisfied!"
echo ""

# Launch the intelligent toolbox
echo "🚀 Starting Intelligent CI/CD Toolbox..."
echo "The toolbox will open in your browser at: http://localhost:8506"
echo ""
echo "Press Ctrl+C to stop the toolbox"
echo ""

streamlit run intelligent-cicd-toolbox.py --server.port 8506
