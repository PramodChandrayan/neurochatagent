#!/usr/bin/env python3
"""
🔍 Universal Project Analyzer
Automatically detects project requirements, dependencies, and CI/CD needs
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import ast

# Optional imports
try:
    import yaml
except ImportError:
    yaml = None

try:
    import toml
except ImportError:
    toml = None

class ProjectAnalyzer:
    """Universal project analyzer for CI/CD automation"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis = {}
        
    def analyze_project(self) -> Dict[str, Any]:
        """Complete project analysis"""
        self.analysis = {
            "project_info": self._analyze_project_info(),
            "dependencies": self._analyze_dependencies(),
            "configuration": self._analyze_configuration(),
            "testing": self._analyze_testing(),
            "deployment": self._analyze_deployment(),
            "security": self._analyze_security(),
            "database": self._analyze_database(),
            "ci_cd_requirements": self._analyze_ci_cd_requirements()
        }
        return self.analysis
    
    def _analyze_project_info(self) -> Dict[str, Any]:
        """Analyze basic project information"""
        info = {
            "name": "Unknown",
            "type": "Unknown",
            "language": "Unknown",
            "framework": "Unknown",
            "version": "Unknown"
        }
        
        # Check for package files
        if (self.project_root / "package.json").exists():
            with open(self.project_root / "package.json") as f:
                data = json.load(f)
                info.update({
                    "name": data.get("name", "Unknown"),
                    "type": "Node.js",
                    "language": "JavaScript/TypeScript",
                    "version": data.get("version", "Unknown")
                })
                
                # Detect framework
                deps = data.get("dependencies", {})
                if "react" in deps:
                    info["framework"] = "React"
                elif "vue" in deps:
                    info["framework"] = "Vue"
                elif "express" in deps:
                    info["framework"] = "Express"
                elif "next" in deps:
                    info["framework"] = "Next.js"
                    
        elif (self.project_root / "requirements.txt").exists():
            info.update({
                "type": "Python",
                "language": "Python"
            })
            
            # Detect framework from requirements
            with open(self.project_root / "requirements.txt") as f:
                content = f.read()
                if "django" in content:
                    info["framework"] = "Django"
                elif "flask" in content:
                    info["framework"] = "Flask"
                elif "fastapi" in content:
                    info["framework"] = "FastAPI"
                elif "streamlit" in content:
                    info["framework"] = "Streamlit"
                    
        elif (self.project_root / "pom.xml").exists():
            info.update({
                "type": "Java",
                "language": "Java"
            })
            
        elif (self.project_root / "go.mod").exists():
            info.update({
                "type": "Go",
                "language": "Go"
            })
            
        elif (self.project_root / "Cargo.toml").exists():
            info.update({
                "type": "Rust",
                "language": "Rust"
            })
            
        # Check for Docker
        if (self.project_root / "Dockerfile").exists():
            info["containerized"] = True
            
        # Check for README
        for readme in ["README.md", "README.txt", "README"]:
            if (self.project_root / readme).exists():
                info["has_documentation"] = True
                break
                
        return info
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        deps = {
            "python": [],
            "node": [],
            "system": [],
            "database": [],
            "cloud": []
        }
        
        # Python dependencies
        if (self.project_root / "requirements.txt").exists():
            with open(self.project_root / "requirements.txt") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        package = line.split("==")[0].split(">=")[0].split("<=")[0]
                        deps["python"].append(package)
                        
                        # Categorize dependencies
                        if package in ["psycopg2", "mysql-connector", "sqlite3"]:
                            deps["database"].append(package)
                        elif package in ["boto3", "google-cloud", "azure"]:
                            deps["cloud"].append(package)
                            
        # Node.js dependencies
        if (self.project_root / "package.json").exists():
            with open(self.project_root / "package.json") as f:
                data = json.load(f)
                deps["node"].extend(data.get("dependencies", {}).keys())
                deps["node"].extend(data.get("devDependencies", {}).keys())
                
        # System dependencies (from Dockerfile)
        if (self.project_root / "Dockerfile").exists():
            with open(self.project_root / "Dockerfile") as f:
                content = f.read()
                # Extract RUN commands
                run_commands = re.findall(r'RUN\s+(.+)', content, re.IGNORECASE)
                for cmd in run_commands:
                    if "apt-get" in cmd or "yum" in cmd or "apk" in cmd:
                        deps["system"].append(cmd.strip())
                        
        return deps
    
    def _analyze_configuration(self) -> Dict[str, Any]:
        """Analyze configuration files and environment variables"""
        config = {
            "env_files": [],
            "config_files": [],
            "secrets_required": [],
            "environment_variables": []
        }
        
        # Environment files
        for env_file in [".env", ".env.local", ".env.production", ".env.staging"]:
            if (self.project_root / env_file).exists():
                config["env_files"].append(env_file)
                
        # Configuration files
        config_patterns = [
            "config.py", "config.yml", "config.yaml", "config.json",
            "settings.py", "settings.yml", "settings.yaml",
            "app.py", "main.py", "server.py"
        ]
        
        for pattern in config_patterns:
            if (self.project_root / pattern).exists():
                config["config_files"].append(pattern)
                
        # Extract environment variables from Python files
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file) as f:
                    content = f.read()
                    # Find os.environ.get or os.getenv calls
                    env_vars = re.findall(r'os\.environ\.get\([\'"]([^\'"]+)[\'"]', content)
                    env_vars.extend(re.findall(r'os\.getenv\([\'"]([^\'"]+)[\'"]', content))
                    config["environment_variables"].extend(env_vars)
            except:
                continue
                
        # Common secrets
        common_secrets = [
            "API_KEY", "SECRET_KEY", "DATABASE_URL", "PASSWORD",
            "TOKEN", "ACCESS_KEY", "PRIVATE_KEY"
        ]
        
        for var in config["environment_variables"]:
            if any(secret in var.upper() for secret in common_secrets):
                config["secrets_required"].append(var)
                
        return config
    
    def _analyze_testing(self) -> Dict[str, Any]:
        """Analyze testing setup and requirements"""
        testing = {
            "framework": "Unknown",
            "test_directory": None,
            "coverage_tool": None,
            "test_commands": [],
            "has_tests": False
        }
        
        # Python testing
        if (self.project_root / "requirements.txt").exists():
            with open(self.project_root / "requirements.txt") as f:
                content = f.read()
                if "pytest" in content:
                    testing["framework"] = "pytest"
                elif "unittest" in content:
                    testing["framework"] = "unittest"
                    
                if "coverage" in content:
                    testing["coverage_tool"] = "coverage"
                    
        # Node.js testing
        if (self.project_root / "package.json").exists():
            with open(self.project_root / "package.json") as f:
                data = json.load(f)
                scripts = data.get("scripts", {})
                if "test" in scripts:
                    testing["test_commands"].append(f"npm test")
                if "jest" in scripts:
                    testing["framework"] = "Jest"
                    
        # Test directories
        test_dirs = ["tests", "test", "specs", "spec", "__tests__"]
        for test_dir in test_dirs:
            if (self.project_root / test_dir).exists():
                testing["test_directory"] = test_dir
                testing["has_tests"] = True
                break
                
        return testing
    
    def _analyze_deployment(self) -> Dict[str, Any]:
        """Analyze deployment configuration"""
        deployment = {
            "containerized": False,
            "platform": "Unknown",
            "deployment_files": [],
            "infrastructure": "Unknown"
        }
        
        # Docker
        if (self.project_root / "Dockerfile").exists():
            deployment["containerized"] = True
            deployment["deployment_files"].append("Dockerfile")
            
        # Kubernetes
        k8s_files = list(self.project_root.rglob("*.yaml")) + list(self.project_root.rglob("*.yml"))
        for file in k8s_files:
            if "k8s" in file.name.lower() or "kubernetes" in file.name.lower():
                deployment["platform"] = "Kubernetes"
                deployment["deployment_files"].append(str(file))
                
        # Cloud deployment
        if (self.project_root / "deploy-cloud-run.sh").exists():
            deployment["platform"] = "Google Cloud Run"
            deployment["deployment_files"].append("deploy-cloud-run.sh")
        elif (self.project_root / "deploy.sh").exists():
            deployment["platform"] = "Custom Script"
            deployment["deployment_files"].append("deploy.sh")
            
        # Infrastructure as Code
        terraform_files = list(self.project_root.rglob("*.tf"))
        if terraform_files:
            deployment["infrastructure"] = "Terraform"
            deployment["deployment_files"].extend([str(f) for f in terraform_files])
            
        return deployment
    
    def _analyze_security(self) -> Dict[str, Any]:
        """Analyze security requirements"""
        security = {
            "vulnerability_scanning": False,
            "secret_scanning": False,
            "dependency_checking": False,
            "security_tools": []
        }
        
        # Check for security tools in dependencies
        if (self.project_root / "requirements.txt").exists():
            with open(self.project_root / "requirements.txt") as f:
                content = f.read()
                if "safety" in content:
                    security["dependency_checking"] = True
                    security["security_tools"].append("safety")
                    
        # Check for security configuration
        security_files = [".bandit", "bandit.yaml", "safety.yaml"]
        for sec_file in security_files:
            if (self.project_root / sec_file).exists():
                security["vulnerability_scanning"] = True
                security["security_tools"].append(sec_file)
                
        return security
    
    def _analyze_database(self) -> Dict[str, Any]:
        """Analyze database requirements"""
        database = {
            "type": "Unknown",
            "migrations": False,
            "orm": "Unknown",
            "connection_strings": []
        }
        
        # Check for migration directories
        if (self.project_root / "migrations").exists():
            database["migrations"] = True
            
        # Check for database dependencies
        if (self.project_root / "requirements.txt").exists():
            with open(self.project_root / "requirements.txt") as f:
                content = f.read()
                if "sqlalchemy" in content:
                    database["orm"] = "SQLAlchemy"
                elif "django" in content:
                    database["orm"] = "Django ORM"
                elif "psycopg2" in content:
                    database["type"] = "PostgreSQL"
                elif "mysql-connector" in content:
                    database["type"] = "MySQL"
                    
        return database
    
    def _analyze_ci_cd_requirements(self) -> Dict[str, Any]:
        """Analyze CI/CD requirements based on project analysis"""
        requirements = {
            "required_secrets": [],
            "required_services": [],
            "required_permissions": [],
            "deployment_steps": [],
            "customizations_needed": []
        }
        
        # Based on project type
        if self.analysis.get("project_info", {}).get("type") == "Python":
            requirements["required_secrets"].extend([
                "PYTHON_VERSION",
                "PIP_CACHE_DIR"
            ])
            
        if self.analysis.get("project_info", {}).get("type") == "Node.js":
            requirements["required_secrets"].extend([
                "NODE_VERSION",
                "NPM_TOKEN"
            ])
            
        # Based on database usage
        if self.analysis.get("database", {}).get("migrations"):
            requirements["required_secrets"].extend([
                "STAGING_DATABASE_URL",
                "PRODUCTION_DATABASE_URL"
            ])
            requirements["required_services"].append("Database Migration Service")
            
        # Based on cloud deployment
        if self.analysis.get("deployment", {}).get("platform") == "Google Cloud Run":
            requirements["required_secrets"].extend([
                "GCP_PROJECT_ID",
                "GCP_SA_KEY"
            ])
            requirements["required_permissions"].extend([
                "Cloud Run Admin",
                "Service Account User",
                "Storage Admin"
            ])
            
        # Based on testing
        if self.analysis.get("testing", {}).get("has_tests"):
            requirements["deployment_steps"].append("Run Tests")
            requirements["deployment_steps"].append("Generate Coverage Report")
            
        # Based on security
        if self.analysis.get("security", {}).get("vulnerability_scanning"):
            requirements["deployment_steps"].append("Security Scan")
            requirements["deployment_steps"].append("Dependency Check")
            
        return requirements
    
    def generate_ci_cd_config(self) -> Dict[str, Any]:
        """Generate CI/CD configuration based on analysis"""
        config = {
            "workflow_name": f"CI/CD Pipeline - {self.analysis['project_info']['name']}",
            "triggers": {
                "push": ["main", "develop"],
                "pull_request": ["main", "develop"]
            },
            "jobs": self._generate_jobs(),
            "secrets": self._generate_secrets_list(),
            "environment_variables": self._generate_env_vars(),
            "customization_guide": self._generate_customization_guide()
        }
        return config
    
    def _generate_jobs(self) -> List[Dict[str, Any]]:
        """Generate CI/CD jobs based on analysis"""
        jobs = []
        
        # Always include basic jobs
        jobs.append({
            "name": "Security & Compliance",
            "description": "Automated security scanning and compliance checks",
            "required": True
        })
        
        jobs.append({
            "name": "Testing & Validation",
            "description": "Run tests and validate code quality",
            "required": self.analysis["testing"]["has_tests"]
        })
        
        jobs.append({
            "name": "Build & Container",
            "description": "Build and optimize container images",
            "required": self.analysis["deployment"]["containerized"]
        })
        
        # Conditional jobs
        if self.analysis["database"]["migrations"]:
            jobs.append({
                "name": "Database Migration",
                "description": "Handle schema changes and ORM migrations",
                "required": True
            })
            
        if self.analysis["deployment"]["platform"] != "Unknown":
            jobs.append({
                "name": "Deployment",
                "description": f"Deploy to {self.analysis['deployment']['platform']}",
                "required": True
            })
            
        return jobs
    
    def _generate_secrets_list(self) -> List[str]:
        """Generate list of required secrets"""
        secrets = []
        
        # Project-specific secrets
        secrets.extend(self.analysis["ci_cd_requirements"]["required_secrets"])
        
        # Common secrets
        common_secrets = [
            "GITHUB_TOKEN",
            "DOCKER_USERNAME",
            "DOCKER_PASSWORD"
        ]
        
        secrets.extend(common_secrets)
        return list(set(secrets))  # Remove duplicates
    
    def _generate_env_vars(self) -> List[str]:
        """Generate list of environment variables"""
        env_vars = []
        
        # Project-specific environment variables
        env_vars.extend(self.analysis["configuration"]["environment_variables"])
        
        # Common environment variables
        common_env_vars = [
            "NODE_ENV",
            "PYTHON_VERSION",
            "BUILD_ENVIRONMENT"
        ]
        
        env_vars.extend(common_env_vars)
        return list(set(env_vars))  # Remove duplicates
    
    def _generate_customization_guide(self) -> Dict[str, Any]:
        """Generate customization guide for developers"""
        guide = {
            "quick_start": [
                "1. Copy .github/workflows/ci-cd-pipeline.yml to your project",
                "2. Update PROJECT_ID, SERVICE_NAME, and REGION variables",
                "3. Add required secrets to GitHub repository",
                "4. Customize deployment configuration if needed"
            ],
            "required_changes": [],
            "optional_customizations": [],
            "examples": {}
        }
        
        # Project-specific customization requirements
        if self.analysis["project_info"]["type"] == "Python":
            guide["required_changes"].append("Update Python version in workflow")
            
        if self.analysis["deployment"]["platform"] == "Google Cloud Run":
            guide["required_changes"].append("Update GCP project ID and region")
            
        if self.analysis["database"]["migrations"]:
            guide["required_changes"].append("Configure database connection strings")
            
        return guide
    
    def save_analysis(self, output_file: str = "ci-cd-analysis.json"):
        """Save analysis to file"""
        with open(output_file, 'w') as f:
            json.dump(self.analysis, f, indent=2, default=str)
        print(f"✅ Analysis saved to {output_file}")
    
    def print_summary(self):
        """Print analysis summary"""
        print("\n" + "="*60)
        print("🔍 PROJECT ANALYSIS SUMMARY")
        print("="*60)
        
        # Project Info
        info = self.analysis["project_info"]
        print(f"\n📋 Project: {info['name']} ({info['type']})")
        print(f"   Language: {info['language']}")
        print(f"   Framework: {info['framework']}")
        print(f"   Containerized: {info.get('containerized', False)}")
        
        # Dependencies
        deps = self.analysis["dependencies"]
        print(f"\n📦 Dependencies:")
        print(f"   Python: {len(deps['python'])} packages")
        print(f"   Node.js: {len(deps['node'])} packages")
        print(f"   Database: {len(deps['database'])} packages")
        
        # Testing
        testing = self.analysis["testing"]
        print(f"\n🧪 Testing:")
        print(f"   Framework: {testing['framework']}")
        print(f"   Has Tests: {testing['has_tests']}")
        print(f"   Test Directory: {testing['test_directory']}")
        
        # Deployment
        deployment = self.analysis["deployment"]
        print(f"\n🚀 Deployment:")
        print(f"   Platform: {deployment['platform']}")
        print(f"   Containerized: {deployment['containerized']}")
        print(f"   Infrastructure: {deployment['infrastructure']}")
        
        # CI/CD Requirements
        requirements = self.analysis["ci_cd_requirements"]
        print(f"\n⚙️ CI/CD Requirements:")
        print(f"   Required Secrets: {len(requirements['required_secrets'])}")
        print(f"   Required Services: {len(requirements['required_services'])}")
        print(f"   Deployment Steps: {len(requirements['deployment_steps'])}")
        
        print("\n" + "="*60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Universal Project Analyzer for CI/CD')
    parser.add_argument('--project-root', '-p', default='.', help='Project root directory')
    parser.add_argument('--output', '-o', default='ci-cd-analysis.json', help='Output file')
    parser.add_argument('--summary', '-s', action='store_true', help='Print summary')
    
    args = parser.parse_args()
    
    # Analyze project
    analyzer = ProjectAnalyzer(args.project_root)
    analysis = analyzer.analyze_project()
    
    # Save analysis
    analyzer.save_analysis(args.output)
    
    # Print summary if requested
    if args.summary:
        analyzer.print_summary()
    
    print(f"\n🎉 Project analysis complete! Check {args.output} for details.")


if __name__ == "__main__":
    main()
