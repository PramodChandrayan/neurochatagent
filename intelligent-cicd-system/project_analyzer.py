#!/usr/bin/env python3
"""
🔍 Project Analyzer
Analyzes project structure and determines CI/CD requirements
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

class ProjectAnalyzer:
    """Analyzes project to determine CI/CD requirements and dependencies"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.analysis_cache = {}
    
    def analyze_project(self) -> Dict[str, any]:
        """Perform comprehensive project analysis"""
        if self.analysis_cache:
            return self.analysis_cache
        
        analysis = {
            'project_type': self._detect_project_type(),
            'files': self._analyze_project_files(),
            'dependencies': self._analyze_dependencies(),
            'configuration': self._analyze_configuration(),
            'deployment_requirements': self._analyze_deployment_requirements(),
            'recommendations': []
        }
        
        # Generate recommendations based on analysis
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        # Cache the analysis
        self.analysis_cache = analysis
        
        return analysis
    
    def _detect_project_type(self) -> str:
        """Detect the type of project"""
        if (self.project_root / 'Dockerfile').exists():
            return 'docker'
        elif (self.project_root / 'package.json').exists():
            return 'nodejs'
        elif (self.project_root / 'requirements.txt').exists() or (self.project_root / 'pyproject.toml').exists():
            return 'python'
        elif (self.project_root / 'pom.xml').exists():
            return 'java'
        elif (self.project_root / 'go.mod').exists():
            return 'go'
        else:
            return 'unknown'
    
    def _analyze_project_files(self) -> Dict[str, List[str]]:
        """Analyze project file structure"""
        files = {
            'source_files': [],
            'config_files': [],
            'dependency_files': [],
            'deployment_files': [],
            'documentation': []
        }
        
        # Common file patterns
        source_patterns = {
            'python': ['*.py', '*.pyx', '*.pyi'],
            'nodejs': ['*.js', '*.ts', '*.jsx', '*.tsx'],
            'java': ['*.java', '*.kt'],
            'go': ['*.go']
        }
        
        config_patterns = ['*.yml', '*.yaml', '*.json', '*.toml', '*.ini', '*.cfg', '*.conf']
        dependency_patterns = ['requirements.txt', 'package.json', 'pom.xml', 'go.mod', 'Cargo.toml']
        deployment_patterns = ['Dockerfile', 'docker-compose.yml', '*.sh', '*.bat']
        doc_patterns = ['*.md', '*.txt', '*.rst', '*.adoc']
        
        # Analyze files
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and not self._is_ignored_file(file_path):
                relative_path = file_path.relative_to(self.project_root)
                
                # Source files
                project_type = self._detect_project_type()
                if project_type in source_patterns:
                    for pattern in source_patterns[project_type]:
                        if relative_path.match(pattern):
                            files['source_files'].append(str(relative_path))
                            break
                
                # Config files
                for pattern in config_patterns:
                    if relative_path.match(pattern):
                        files['config_files'].append(str(relative_path))
                        break
                
                # Dependency files
                for pattern in dependency_patterns:
                    if relative_path.match(pattern):
                        files['dependency_files'].append(str(relative_path))
                        break
                
                # Deployment files
                for pattern in deployment_patterns:
                    if relative_path.match(pattern):
                        files['deployment_files'].append(str(relative_path))
                        break
                
                # Documentation
                for pattern in doc_patterns:
                    if relative_path.match(pattern):
                        files['documentation'].append(str(relative_path))
                        break
        
        return files
    
    def _analyze_dependencies(self) -> Dict[str, List[str]]:
        """Analyze project dependencies"""
        dependencies = {
            'python_packages': [],
            'node_packages': [],
            'system_dependencies': [],
            'cloud_services': []
        }
        
        # Python dependencies
        requirements_file = self.project_root / 'requirements.txt'
        if requirements_file.exists():
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
                        dependencies['python_packages'].append(package)
        
        # Node.js dependencies
        package_json = self.project_root / 'package.json'
        if package_json.exists():
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    if 'dependencies' in data:
                        dependencies['node_packages'].extend(data['dependencies'].keys())
                    if 'devDependencies' in data:
                        dependencies['node_packages'].extend(data['devDependencies'].keys())
            except:
                pass
        
        # Detect cloud services from dependencies
        cloud_indicators = {
            'openai': 'OpenAI API',
            'pinecone': 'Pinecone Vector Database',
            'google-cloud': 'Google Cloud Platform',
            'boto3': 'AWS Services',
            'azure': 'Microsoft Azure',
            'redis': 'Redis Database',
            'psycopg2': 'PostgreSQL Database',
            'pymongo': 'MongoDB Database'
        }
        
        for package in dependencies['python_packages']:
            for indicator, service in cloud_indicators.items():
                if indicator in package.lower():
                    dependencies['cloud_services'].append(service)
        
        return dependencies
    
    def _analyze_configuration(self) -> Dict[str, any]:
        """Analyze project configuration"""
        config = {
            'environment_variables': [],
            'secrets_required': [],
            'ports': [],
            'volumes': []
        }
        
        # Check for .env files
        env_files = list(self.project_root.glob('.env*'))
        for env_file in env_files:
            if env_file.is_file():
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                var_name = line.split('=')[0]
                                config['environment_variables'].append(var_name)
                                
                                # Identify potential secrets
                                secret_indicators = ['key', 'secret', 'password', 'token', 'api']
                                if any(indicator in var_name.lower() for indicator in secret_indicators):
                                    config['secrets_required'].append(var_name)
                except:
                    pass
        
        # Check Dockerfile for ports and volumes
        dockerfile = self.project_root / 'Dockerfile'
        if dockerfile.exists():
            try:
                with open(dockerfile, 'r') as f:
                    content = f.read()
                    
                    # Extract ports
                    port_matches = re.findall(r'EXPOSE\s+(\d+)', content, re.IGNORECASE)
                    config['ports'].extend(port_matches)
                    
                    # Extract volumes
                    volume_matches = re.findall(r'VOLUME\s+\[?([^\]]+)\]?', content, re.IGNORECASE)
                    config['volumes'].extend(volume_matches)
            except:
                pass
        
        return config
    
    def _analyze_deployment_requirements(self) -> Dict[str, any]:
        """Analyze deployment requirements"""
        requirements = {
            'container_registry': 'gcr.io',  # Default to GCR
            'deployment_platform': 'cloud_run',
            'scaling_config': {},
            'environment_variables': [],
            'secrets': []
        }
        
        # Check if this is a containerized application
        if (self.project_root / 'Dockerfile').exists():
            requirements['container_registry'] = 'gcr.io'
            requirements['deployment_platform'] = 'cloud_run'
        
        # Check for specific deployment configurations
        deployment_configs = [
            'deployment.yml',
            'deploy.sh',
            'docker-compose.yml',
            'kubernetes.yml',
            'k8s.yml'
        ]
        
        for config_file in deployment_configs:
            if (self.project_root / config_file).exists():
                requirements['deployment_platform'] = 'kubernetes'
                break
        
        # Determine scaling configuration
        if requirements['deployment_platform'] == 'cloud_run':
            requirements['scaling_config'] = {
                'min_instances': 0,
                'max_instances': 100,
                'cpu': 1,
                'memory': '512Mi'
            }
        
        return requirements
    
    def _generate_recommendations(self, analysis: Dict[str, any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        project_type = analysis['project_type']
        
        if project_type == 'python':
            recommendations.append("🐍 Python project detected - will use Python-specific CI/CD pipeline")
            
            # Check for specific Python frameworks
            if 'streamlit' in analysis['dependencies']['python_packages']:
                recommendations.append("📊 Streamlit app detected - will configure for web application deployment")
            
            if 'fastapi' in analysis['dependencies']['python_packages']:
                recommendations.append("🚀 FastAPI detected - will configure for API service deployment")
        
        elif project_type == 'docker':
            recommendations.append("🐳 Docker project detected - will use container-based deployment")
        
        # Check for cloud service dependencies
        cloud_services = analysis['dependencies']['cloud_services']
        if cloud_services:
            recommendations.append(f"☁️ Cloud services detected: {', '.join(cloud_services)} - will configure necessary secrets")
        
        # Check for database dependencies
        db_indicators = ['psycopg2', 'pymongo', 'redis', 'sqlite']
        if any(indicator in analysis['dependencies']['python_packages'] for indicator in db_indicators):
            recommendations.append("🗄️ Database dependencies detected - will configure database connection secrets")
        
        # Check for environment variables
        if analysis['configuration']['environment_variables']:
            recommendations.append(f"🔧 {len(analysis['configuration']['environment_variables'])} environment variables detected - will configure in Cloud Run")
        
        # Check for secrets
        if analysis['configuration']['secrets_required']:
            recommendations.append(f"🔐 {len(analysis['configuration']['secrets_required'])} secrets detected - will configure in GitHub secrets")
        
        # General recommendations
        recommendations.append("🚀 Will deploy to Google Cloud Run in us-central1 region")
        recommendations.append("🔗 Will use Workload Identity Federation for secure authentication")
        recommendations.append("📝 Will generate optimized CI/CD pipeline based on project analysis")
        
        return recommendations
    
    def _is_ignored_file(self, file_path: Path) -> bool:
        """Check if file should be ignored during analysis"""
        ignored_patterns = [
            '.git', '__pycache__', '*.pyc', '*.pyo', '*.pyd',
            '.pytest_cache', '.coverage', 'htmlcov', '.tox',
            'node_modules', 'dist', 'build', '.venv', 'venv',
            '.env.local', '.env.production', '.DS_Store'
        ]
        
        for pattern in ignored_patterns:
            if pattern.startswith('*'):
                if file_path.name.endswith(pattern[1:]):
                    return True
            elif pattern.startswith('.'):
                if file_path.name.startswith(pattern):
                    return True
            else:
                if pattern in file_path.parts:
                    return True
        
        return False
    
    def get_project_summary(self) -> Dict[str, any]:
        """Get a summary of the project analysis"""
        analysis = self.analyze_project()
        
        return {
            'project_type': analysis['project_type'],
            'total_files': sum(len(files) for files in analysis['files'].values()),
            'dependencies_count': sum(len(deps) for deps in analysis['dependencies'].values()),
            'environment_variables_count': len(analysis['configuration']['environment_variables']),
            'secrets_count': len(analysis['configuration']['secrets_required']),
            'deployment_platform': analysis['deployment_requirements']['deployment_platform'],
            'recommendations_count': len(analysis['recommendations'])
        }
    
    def needs_database(self) -> bool:
        """Check if project needs database configuration"""
        analysis = self.analyze_project()
        
        db_indicators = ['psycopg2', 'pymongo', 'redis', 'sqlite', 'mysql', 'postgresql']
        
        for package in analysis['dependencies']['python_packages']:
            if any(indicator in package.lower() for indicator in db_indicators):
                return True
        
        return False
    
    def needs_api_keys(self) -> bool:
        """Check if project needs API key configuration"""
        analysis = self.analyze_project()
        
        api_indicators = ['openai', 'pinecone', 'google', 'aws', 'azure', 'stripe', 'twilio']
        
        for package in analysis['dependencies']['python_packages']:
            if any(indicator in package.lower() for indicator in api_indicators):
                return True
        
        return False
