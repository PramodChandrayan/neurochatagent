#!/usr/bin/env python3
"""
🧠 Intelligent Project Analyzer
Automatically detects project type, framework, and required secrets
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml


class IntelligentProjectAnalyzer:
    """Intelligent analyzer that detects project requirements automatically"""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.detected_secrets = set()
        self.detected_frameworks = set()
        self.detected_databases = set()
        self.detected_cloud_providers = set()

    def analyze_project(self) -> Dict[str, Any]:
        """Main analysis method that returns comprehensive project requirements"""
        print("🔍 Starting intelligent project analysis...")

        # Detect project type and framework
        project_info = self._detect_project_type()
        print(
            f"✅ Detected: {project_info['type']} project with {project_info['framework']} framework"
        )

        # Analyze dependencies
        print("🔍 Analyzing dependencies...")
        dependencies = self._analyze_dependencies()

        # Analyze configuration files
        print("🔍 Analyzing configuration files...")
        config_secrets = self._analyze_config_files()

        # Analyze source code
        print("🔍 Analyzing source code...")
        code_secrets = self._analyze_source_code()

        # Analyze deployment configurations
        print("🔍 Analyzing deployment configurations...")
        deployment_configs = self._analyze_deployment_configs()

        # Generate comprehensive requirements
        print("🔍 Generating requirements...")
        requirements = self._generate_requirements(
            project_info, dependencies, config_secrets, code_secrets, deployment_configs
        )

        return requirements

    def _detect_project_type(self) -> Dict[str, str]:
        """Detect project type and framework"""
        project_type = "unknown"
        framework = "unknown"

        # Check for Python project
        if (self.project_path / "requirements.txt").exists() or (
            self.project_path / "pyproject.toml"
        ).exists():
            project_type = "python"
            framework = self._detect_python_framework()

        # Check for Node.js project
        elif (self.project_path / "package.json").exists():
            project_type = "nodejs"
            framework = self._detect_nodejs_framework()

        # Check for Java project
        elif (self.project_path / "pom.xml").exists() or (
            self.project_path / "build.gradle"
        ).exists():
            project_type = "java"
            framework = self._detect_java_framework()

        # Check for Go project
        elif (self.project_path / "go.mod").exists():
            project_type = "go"
            framework = "standard"

        # Check for Rust project
        elif (self.project_path / "Cargo.toml").exists():
            project_type = "rust"
            framework = "cargo"

        # Check for Ruby project
        elif (self.project_path / "Gemfile").exists():
            project_type = "ruby"
            framework = "bundler"

        return {
            "type": project_type,
            "framework": framework,
            "database_type": self._detect_database_type(),
            "cloud_provider": self._detect_cloud_provider(),
        }

    def _detect_python_framework(self) -> str:
        """Detect Python framework"""
        frameworks = []

        # Check requirements.txt
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text().lower()
            if "streamlit" in content:
                frameworks.append("streamlit")
            if "flask" in content:
                frameworks.append("flask")
            if "django" in content:
                frameworks.append("django")
            if "fastapi" in content:
                frameworks.append("fastapi")
            if "tornado" in content:
                frameworks.append("tornado")

        # Check pyproject.toml
        pyproject_file = self.project_path / "pyproject.toml"
        if pyproject_file.exists():
            content = pyproject_file.read_text().lower()
            if "streamlit" in content:
                frameworks.append("streamlit")
            if "flask" in content:
                frameworks.append("flask")
            if "django" in content:
                frameworks.append("django")
            if "fastapi" in content:
                frameworks.append("fastapi")

        # Check for common framework files
        if (self.project_path / "app.py").exists() or (
            self.project_path / "main.py"
        ).exists():
            if not frameworks:
                frameworks.append("standard")

        return frameworks[0] if frameworks else "standard"

    def _detect_nodejs_framework(self) -> str:
        """Detect Node.js framework"""
        package_file = self.project_path / "package.json"
        if package_file.exists():
            try:
                content = json.loads(package_file.read_text())
                dependencies = content.get("dependencies", {})

                if "react" in dependencies:
                    return "react"
                elif "vue" in dependencies:
                    return "vue"
                elif "express" in dependencies:
                    return "express"
                elif "next" in dependencies:
                    return "nextjs"
                elif "nuxt" in dependencies:
                    return "nuxtjs"
                else:
                    return "nodejs"
            except:
                return "nodejs"
        return "nodejs"

    def _detect_java_framework(self) -> str:
        """Detect Java framework"""
        if (self.project_path / "pom.xml").exists():
            return "maven"
        elif (self.project_path / "build.gradle").exists():
            return "gradle"
        return "java"

    def _detect_database_type(self) -> str:
        """Detect database type from dependencies and configs"""
        databases = []

        # Check Python requirements
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text().lower()
            if "psycopg2" in content or "postgresql" in content:
                databases.append("postgresql")
            if "mysql-connector" in content or "pymysql" in content:
                databases.append("mysql")
            if "redis" in content:
                databases.append("redis")
            if "pymongo" in content:
                databases.append("mongodb")
            if "sqlite" in content:
                databases.append("sqlite")

        # Check Node.js dependencies
        package_file = self.project_path / "package.json"
        if package_file.exists():
            try:
                content = json.loads(package_file.read_text())
                dependencies = content.get("dependencies", {})

                if "pg" in dependencies or "postgres" in dependencies:
                    databases.append("postgresql")
                if "mysql" in dependencies or "mysql2" in dependencies:
                    databases.append("mysql")
                if "redis" in dependencies:
                    databases.append("redis")
                if "mongodb" in dependencies:
                    databases.append("mongodb")
                if "sqlite3" in dependencies:
                    databases.append("sqlite")
            except:
                pass

        return databases[0] if databases else "none"

    def _detect_cloud_provider(self) -> str:
        """Detect cloud provider from configuration files"""
        cloud_providers = []

        # Check for GCP
        if (self.project_path / ".gcloudignore").exists() or (
            self.project_path / "app.yaml"
        ).exists():
            cloud_providers.append("gcp")

        # Check for AWS
        if (self.project_path / ".ebignore").exists() or (
            self.project_path / "elasticbeanstalk"
        ).exists():
            cloud_providers.append("aws")

        # Check for Azure
        if (self.project_path / ".azure").exists() or (
            self.project_path / "azure.yaml"
        ).exists():
            cloud_providers.append("azure")

        # Check for Docker/Kubernetes
        if (self.project_path / "Dockerfile").exists() or (
            self.project_path / "docker-compose.yml"
        ).exists():
            cloud_providers.append("docker")

        return cloud_providers[0] if cloud_providers else "none"

    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies for secret requirements"""
        dependencies = {
            "python": [],
            "nodejs": [],
            "java": [],
            "go": [],
            "rust": [],
            "ruby": [],
        }

        # Python dependencies
        req_file = self.project_path / "requirements.txt"
        if req_file.exists():
            content = req_file.read_text()
            dependencies["python"] = [
                line.strip()
                for line in content.split("\n")
                if line.strip() and not line.startswith("#")
            ]

            # Check for secret-requiring libraries
            if "openai" in content:
                self.detected_secrets.add("OPENAI_API_KEY")
            if "pinecone" in content:
                self.detected_secrets.add("PINECONE_API_KEY")
                self.detected_secrets.add("PINECONE_ENVIRONMENT")
            if "anthropic" in content:
                self.detected_secrets.add("ANTHROPIC_API_KEY")
            if "cohere" in content:
                self.detected_secrets.add("COHERE_API_KEY")
            if "psycopg2" in content:
                self.detected_secrets.add("DATABASE_URL")
                self.detected_secrets.add("DB_PASSWORD")
            if "redis" in content:
                self.detected_secrets.add("REDIS_URL")
                self.detected_secrets.add("REDIS_PASSWORD")

        # Node.js dependencies
        package_file = self.project_path / "package.json"
        if package_file.exists():
            try:
                content = json.loads(package_file.read_text())
                dependencies["nodejs"] = list(content.get("dependencies", {}).keys())

                # Check for secret-requiring packages
                if "openai" in dependencies["nodejs"]:
                    self.detected_secrets.add("OPENAI_API_KEY")
                if "pinecone" in dependencies["nodejs"]:
                    self.detected_secrets.add("PINECONE_API_KEY")
                    self.detected_secrets.add("PINECONE_ENVIRONMENT")
                if "pg" in dependencies["nodejs"]:
                    self.detected_secrets.add("DATABASE_URL")
                    self.detected_secrets.add("DB_PASSWORD")
            except:
                pass

        return dependencies

    def _analyze_config_files(self) -> Set[str]:
        """Analyze configuration files for secret patterns"""
        config_secrets = set()

        # Common config file patterns
        config_patterns = [
            "*.env*",
            ".config.*",
            "*.yaml",
            "*.yml",
            "*.json",
            "*.toml",
            "*.ini",
        ]

        for pattern in config_patterns:
            for file_path in self.project_path.glob(pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text()

                        # Look for secret patterns
                        secret_patterns = [
                            r"([A-Z_]+_API_KEY)",
                            r"([A-Z_]+_SECRET)",
                            r"([A-Z_]+_PASSWORD)",
                            r"([A-Z_]+_TOKEN)",
                            r"([A-Z_]+_URL)",
                            r"([A-Z_]+_HOST)",
                            r"([A-Z_]+_PORT)",
                            r"([A-Z_]+_DATABASE)",
                            r"([A-Z_]+_DB)",
                        ]

                        for pattern in secret_patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                if not self._is_system_env_var(match):
                                    config_secrets.add(match)
                                    self.detected_secrets.add(match)
                    except:
                        continue

        return config_secrets

    def _analyze_source_code(self) -> Set[str]:
        """Analyze source code for environment variable usage"""
        code_secrets = set()

        # Common source file extensions
        source_extensions = [
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".java",
            ".go",
            ".rs",
            ".rb",
        ]

        for ext in source_extensions:
            for file_path in self.project_path.rglob(f"*{ext}"):
                if file_path.is_file() and not any(
                    part.startswith(".") for part in file_path.parts
                ):
                    try:
                        content = file_path.read_text()

                        # Python patterns
                        if ext == ".py":
                            env_patterns = [
                                r'os\.getenv\(["\']([^"\']+)["\']\)',
                                r'os\.environ\[["\']([^"\']+)["\']\]',
                                r'os\.environ\.get\(["\']([^"\']+)["\']\)',
                            ]
                        # Node.js patterns
                        elif ext in [".js", ".ts", ".jsx", ".tsx"]:
                            env_patterns = [
                                r"process\.env\.([A-Z_]+)",
                                r'process\.env\[["\']([^"\']+)["\']\]',
                            ]
                        # Java patterns
                        elif ext == ".java":
                            env_patterns = [r'System\.getenv\(["\']([^"\']+)["\']\)']
                        # Go patterns
                        elif ext == ".go":
                            env_patterns = [r'os\.Getenv\(["\']([^"\']+)["\']\)']
                        # Rust patterns
                        elif ext == ".rs":
                            env_patterns = [
                                r'env!\(["\']([^"\']+)["\']\)',
                                r'std::env::var\(["\']([^"\']+)["\']\)',
                            ]
                        # Ruby patterns
                        elif ext == ".rb":
                            env_patterns = [r'ENV\[["\']([^"\']+)["\']\]']
                        else:
                            continue

                        for pattern in env_patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                if not self._is_system_env_var(match):
                                    code_secrets.add(match)
                                    self.detected_secrets.add(match)
                    except:
                        continue

        return code_secrets

    def _analyze_deployment_configs(self) -> Dict[str, Any]:
        """Analyze deployment configuration files"""
        deployment_configs = {
            "docker": False,
            "kubernetes": False,
            "terraform": False,
            "cloudformation": False,
            "helm": False,
            "docker_compose": False,
        }

        # Check for Docker
        if (self.project_path / "Dockerfile").exists():
            deployment_configs["docker"] = True

        # Check for Docker Compose
        if (self.project_path / "docker-compose.yml").exists() or (
            self.project_path / "docker-compose.yaml"
        ).exists():
            deployment_configs["docker_compose"] = True

        # Check for Kubernetes
        for k8s_file in self.project_path.rglob("*.yaml"):
            if (
                "kubernetes" in k8s_file.read_text().lower()
                or "apiVersion" in k8s_file.read_text()
            ):
                deployment_configs["kubernetes"] = True
                break

        # Check for Terraform
        if (self.project_path / "*.tf").exists() or (
            self.project_path / "*.tfvars"
        ).exists():
            deployment_configs["terraform"] = True

        # Check for CloudFormation
        if (self.project_path / "*.template").exists() or (
            self.project_path / "*.yaml"
        ).exists():
            content = (self.project_path / "*.yaml").read_text()
            if "AWSTemplateFormatVersion" in content:
                deployment_configs["cloudformation"] = True

        # Check for Helm
        if (self.project_path / "Chart.yaml").exists():
            deployment_configs["helm"] = True

        return deployment_configs

    def _is_system_env_var(self, var_name: str) -> bool:
        """Check if environment variable is a system variable"""
        system_vars = {
            "PATH",
            "HOME",
            "USER",
            "SHELL",
            "TERM",
            "LANG",
            "LC_ALL",
            "PWD",
            "HOSTNAME",
            "HOST",
            "PORT",
            "NODE_ENV",
            "PYTHONPATH",
            "JAVA_HOME",
            "GOPATH",
            "RUST_BACKTRACE",
            "RUBY_VERSION",
        }
        return var_name in system_vars

    def _generate_requirements(
        self,
        project_info: Dict,
        dependencies: Dict,
        config_secrets: Set,
        code_secrets: Set,
        deployment_configs: Dict,
    ) -> Dict[str, Any]:
        """Generate comprehensive requirements summary"""

        # Combine all detected secrets
        all_secrets = self.detected_secrets.union(config_secrets).union(code_secrets)

        # Separate CI/CD secrets from runtime secrets
        ci_cd_secrets = {
            "GCP_PROJECT_ID",
            "GCP_SERVICE_ACCOUNT",
            "WIF_PROVIDER",
            "REGION",
            "SERVICE_NAME",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "AWS_REGION",
            "AZURE_CLIENT_ID",
            "AZURE_CLIENT_SECRET",
            "AZURE_TENANT_ID",
        }

        runtime_secrets = all_secrets - ci_cd_secrets

        # Generate intelligent recommendations
        recommendations = []

        if project_info["type"] == "python":
            if "streamlit" in project_info["framework"]:
                recommendations.append(
                    "Consider using Streamlit Cloud for easy deployment"
                )
            if (
                "flask" in project_info["framework"]
                or "django" in project_info["framework"]
            ):
                recommendations.append(
                    "Web framework detected - consider containerization for deployment"
                )

        if deployment_configs["docker"]:
            recommendations.append(
                "Docker detected - ready for containerized deployment"
            )

        if deployment_configs["kubernetes"]:
            recommendations.append(
                "Kubernetes manifests detected - ready for K8s deployment"
            )

        if "OPENAI_API_KEY" in runtime_secrets:
            recommendations.append(
                "OpenAI integration detected - ensure API key is securely managed"
            )

        if "PINECONE_API_KEY" in runtime_secrets:
            recommendations.append(
                "Pinecone vector database detected - ensure API credentials are secure"
            )

        return {
            "project_info": project_info,
            "dependencies": dependencies,
            "runtime_secrets": list(runtime_secrets),
            "ci_cd_secrets": list(ci_cd_secrets),
            "deployment_configs": deployment_configs,
            "recommendations": recommendations,
            "analysis_timestamp": str(Path().cwd()),
        }
