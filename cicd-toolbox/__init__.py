"""
🧠 Intelligent CI/CD Toolbox
Project-agnostic, automatically detects requirements and provides intelligent setup

A comprehensive toolbox that:
- Intelligently analyzes any project to detect requirements
- Automatically sets up cloud infrastructure (GCP, AWS, Azure)
- Manages secrets and pushes them to GitHub Actions
- Provides pipeline control and deployment strategy management
- Offers real-time feedback and progress tracking
"""

__version__ = "1.0.0"
__author__ = "Intelligent CI/CD Toolbox Team"
__description__ = "Project-agnostic CI/CD automation toolbox with intelligent analysis"

from .analyzer import IntelligentProjectAnalyzer
from .gui import EnhancedCICDGUI
from .toolbox import IntelligentCICDToolbox

__all__ = ["IntelligentProjectAnalyzer", "IntelligentCICDToolbox", "EnhancedCICDGUI"]
