#!/bin/bash

# 🚀 Simple CI/CD Toolbox Launcher
# Launches the simplified, focused CI/CD toolbox

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Launching Simple CI/CD Toolbox...${NC}"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
    echo -e "${YELLOW}💡 Please install Python 3 and try again${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "ci-cd-gui-env" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv ci-cd-gui-env
fi

# Activate virtual environment and install requirements
echo -e "${YELLOW}📦 Installing required packages...${NC}"
source ci-cd-gui-env/bin/activate

# Install streamlit if not already installed
if ! pip show streamlit &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Streamlit...${NC}"
    pip install streamlit
fi

echo -e "${GREEN}✅ Environment ready!${NC}"
echo -e "${BLUE}🚀 Starting Simple CI/CD Toolbox...${NC}"
echo -e "${YELLOW}💡 Open your browser to: http://localhost:8506${NC}"

# Launch the simplified GUI
streamlit run simple-gui.py --server.port 8506 --server.address localhost --server.headless true
