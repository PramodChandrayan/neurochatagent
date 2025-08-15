#!/bin/bash

# 🚀 Intelligent CI/CD Toolbox Launcher
# Simple and clean launcher for the CI/CD toolbox

echo "🚀 Launching Intelligent CI/CD Toolbox..."

# Check if we're in the right directory
if [ ! -f "intelligent-cicd-toolbox-v2.py" ]; then
    echo "❌ Error: Please run this script from the cicd-toolbox directory"
    echo "   cd cicd-toolbox && ./launch.sh"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Streamlit is available
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "📦 Installing Streamlit..."
    pip3 install streamlit
fi

# Launch the toolbox
echo "✅ Starting Intelligent CI/CD Toolbox..."
echo "🌐 Opening at: http://localhost:8501"
echo "🔄 Press Ctrl+C to stop"

python3 -m streamlit run intelligent-cicd-toolbox-v2.py --server.port 8501
