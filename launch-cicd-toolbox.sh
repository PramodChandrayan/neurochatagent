#!/bin/bash

# 🚀 CI/CD Toolbox Launcher
# This script launches the authentication process and then the GUI

echo "🚀 Launching CI/CD Toolbox..."
echo "=============================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the cicd-toolbox directory
cd "$SCRIPT_DIR/cicd-toolbox"

# Check if the authentication script exists
if [ ! -f "authenticate-and-launch.sh" ]; then
    echo "❌ Error: Authentication script not found!"
    echo "Please ensure you're running this from the project root directory."
    exit 1
fi

# Choose which toolbox to launch
echo "🚀 Choose Your CI/CD Toolbox:"
echo "1. Intelligent Toolbox (Recommended) - Fully automated, smart handling"
echo "2. Simple Toolbox - Basic automation with CLI authentication"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Launching Intelligent CI/CD Toolbox..."
        echo "=========================================="
        ./launch-intelligent-toolbox.sh
        ;;
    2)
        echo ""
        echo "🔐 Starting Simple Toolbox with Authentication..."
        echo "================================================"
        ./authenticate-and-launch.sh
        ;;
    *)
        echo "❌ Invalid choice. Launching Intelligent Toolbox by default..."
        ./launch-intelligent-toolbox.sh
        ;;
esac

echo ""
echo "🏁 CI/CD Toolbox session ended."
