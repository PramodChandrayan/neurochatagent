#!/usr/bin/env python3
"""
Universal Configuration for Intelligent CI/CD Toolbox
Makes the toolbox work in any project without hardcoding
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

class UniversalConfig:
    """Universal configuration system for any project"""
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.config_file = os.path.join(self.project_root, '.cicd-toolbox.json')
        self.load_config()
    
    def load_config(self):
        """Load existing config or create default"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self.get_default_config()
            self.save_config()
    
    def save_config(self):
        """Save current configuration"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "project_info": {
                "name": "Unknown Project",
                "type": "unknown",
                "language": "unknown",
                "framework": "unknown"
            },
            "deployment": {
                "target": "cloud_run",
                "region": "us-central1",
                "service_name": "app"
            },
            "database": {
                "enabled": False,
                "type": "none",
                "migrations": False
            },
            "secrets": {
                "required": [],
                "optional": []
            },
            "analysis": {
                "last_run": None,
                "dependencies": [],
                "files": []
            }
        }
    
    def analyze_project(self) -> Dict[str, Any]:
        """Analyze project structure and update configuration"""
        print("🔍 Analyzing project structure...")
        
        analysis = {
            "project_type": "unknown",
            "language": "unknown",
            "framework": "unknown",
            "dependencies": [],
            "files": [],
            "database": {
                "enabled": False,
                "type": "none",
                "migrations": False
            },
            "secrets": {
                "required": [],
                "optional": []
            }
        }
        
        # Detect project type based on files
        files = self.scan_project_files()
        analysis["files"] = files
        
        # Detect language and framework
        if "requirements.txt" in files:
            analysis["language"] = "python"
            analysis["dependencies"] = self.parse_requirements()
            
            if "streamlit_app.py" in files:
                analysis["project_type"] = "streamlit"
                analysis["framework"] = "streamlit"
            elif "app.py" in files:
                analysis["project_type"] = "flask"
                analysis["framework"] = "flask"
            elif "main.py" in files:
                analysis["project_type"] = "python"
                analysis["framework"] = "python"
        
        elif "package.json" in files:
            analysis["language"] = "javascript"
            analysis["dependencies"] = self.parse_package_json()
            
            if "next.config.js" in files:
                analysis["project_type"] = "nextjs"
                analysis["framework"] = "next.js"
            elif "react" in analysis["dependencies"]:
                analysis["project_type"] = "react"
                analysis["framework"] = "react"
            elif "vue" in analysis["dependencies"]:
                analysis["project_type"] = "vue"
                analysis["framework"] = "vue"
        
        # Detect database usage
        analysis["database"] = self.detect_database_usage(files, analysis["dependencies"])
        
        # Detect required secrets
        analysis["secrets"] = self.detect_required_secrets(analysis)
        
        # Update configuration
        self.config["project_info"] = {
            "name": self.get_project_name(),
            "type": analysis["project_type"],
            "language": analysis["language"],
            "framework": analysis["framework"]
        }
        self.config["database"] = analysis["database"]
        self.config["secrets"] = analysis["secrets"]
        self.config["analysis"] = {
            "last_run": self.get_timestamp(),
            "dependencies": analysis["dependencies"],
            "files": analysis["files"]
        }
        
        self.save_config()
        return analysis
    
    def scan_project_files(self) -> List[str]:
        """Scan project directory for important files"""
        files = []
        for root, dirs, filenames in os.walk(self.project_root):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
            
            for filename in filenames:
                if filename in [
                    'requirements.txt', 'package.json', 'Dockerfile', 'docker-compose.yml',
                    'streamlit_app.py', 'app.py', 'main.py', 'index.js', 'server.js',
                    'alembic.ini', 'models.py', 'schema.sql', 'migrations',
                    '.env', '.env.example', 'config.py', 'settings.py'
                ]:
                    files.append(filename)
        return list(set(files))  # Remove duplicates
    
    def parse_requirements(self) -> List[str]:
        """Parse Python requirements.txt"""
        requirements_file = os.path.join(self.project_root, 'requirements.txt')
        if not os.path.exists(requirements_file):
            return []
        
        dependencies = []
        with open(requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (remove version specifiers)
                    package = line.split('>=')[0].split('==')[0].split('<=')[0].strip()
                    dependencies.append(package)
        return dependencies
    
    def parse_package_json(self) -> List[str]:
        """Parse Node.js package.json"""
        package_file = os.path.join(self.project_root, 'package.json')
        if not os.path.exists(package_file):
            return []
        
        try:
            with open(package_file, 'r') as f:
                data = json.load(f)
                dependencies = list(data.get('dependencies', {}).keys())
                dev_dependencies = list(data.get('devDependencies', {}).keys())
                return dependencies + dev_dependencies
        except:
            return []
    
    def detect_database_usage(self, files: List[str], dependencies: List[str]) -> Dict[str, Any]:
        """Detect database usage in the project"""
        database_config = {
            "enabled": False,
            "type": "none",
            "migrations": False
        }
        
        # Check for database files
        if "alembic.ini" in files or "models.py" in files:
            database_config["enabled"] = True
            database_config["migrations"] = True
        
        # Check for database dependencies
        db_indicators = {
            "postgresql": ["psycopg2", "psycopg2-binary", "postgresql", "pg"],
            "mysql": ["mysql-connector", "mysqlclient", "pymysql"],
            "mongodb": ["pymongo", "motor"],
            "redis": ["redis", "hiredis"],
            "sqlite": ["sqlite3"]
        }
        
        for db_type, indicators in db_indicators.items():
            if any(indicator in dependencies for indicator in indicators):
                database_config["enabled"] = True
                database_config["type"] = db_type
                break
        
        return database_config
    
    def detect_required_secrets(self, analysis: Dict[str, Any]) -> Dict[str, List[str]]:
        """Detect required secrets based on project analysis"""
        secrets = {
            "required": [],
            "optional": []
        }
        
        # Common secrets
        common_secrets = {
            "streamlit": ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_ENVIRONMENT"],
            "flask": ["SECRET_KEY", "DATABASE_URL", "JWT_SECRET"],
            "nextjs": ["NEXT_PUBLIC_API_URL", "DATABASE_URL", "JWT_SECRET"],
            "react": ["REACT_APP_API_URL", "REACT_APP_API_KEY"],
            "python": ["OPENAI_API_KEY", "DATABASE_URL", "SECRET_KEY"]
        }
        
        project_type = analysis["project_type"]
        if project_type in common_secrets:
            secrets["required"].extend(common_secrets[project_type])
        
        # Add database secrets if database is enabled
        if analysis["database"]["enabled"]:
            secrets["required"].append("DATABASE_URL")
            
        # Add migration secrets if migrations are enabled
        if analysis["database"]["migrations"]:
            secrets["required"].append("DATABASE_URL")
        
        # Remove duplicates
        secrets["required"] = list(set(secrets["required"]))
        secrets["optional"] = list(set(secrets["optional"]))
        
        return secrets
    
    def get_project_name(self) -> str:
        """Get project name from various sources"""
        # Try git remote
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                url = result.stdout.strip()
                if url.endswith('.git'):
                    return url.split('/')[-1].replace('.git', '')
                return url.split('/')[-1]
        except:
            pass
        
        # Use directory name
        return os.path.basename(self.project_root)
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_deployment_config(self) -> Dict[str, Any]:
        """Get deployment configuration"""
        return self.config.get("deployment", {})
    
    def update_deployment_config(self, **kwargs):
        """Update deployment configuration"""
        if "deployment" not in self.config:
            self.config["deployment"] = {}
        
        self.config["deployment"].update(kwargs)
        self.save_config()
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return self.config.get("database", {"enabled": False, "type": "none"})
    
    def get_secrets_config(self) -> Dict[str, List[str]]:
        """Get secrets configuration"""
        return self.config.get("secrets", {"required": [], "optional": []})
    
    def export_config(self) -> Dict[str, Any]:
        """Export full configuration"""
        return self.config.copy()

# Test the universal configuration
if __name__ == "__main__":
    print("🧪 Testing Universal Configuration...")
    
    config = UniversalConfig()
    analysis = config.analyze_project()
    
    print(f"📊 Project Analysis:")
    print(f"   Type: {analysis['project_type']}")
    print(f"   Language: {analysis['language']}")
    print(f"   Framework: {analysis['framework']}")
    print(f"   Database: {analysis['database']}")
    print(f"   Secrets: {analysis['secrets']}")
    
    print(f"✅ Universal configuration test completed!")
