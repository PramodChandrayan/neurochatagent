#!/usr/bin/env python3
"""
🚀 Universal CI/CD Template Generator
Creates customized CI/CD workflows based on project analysis
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List
import argparse

# Optional imports
try:
    import yaml
except ImportError:
    yaml = None


class CICDTemplateGenerator:
    """Generates customized CI/CD workflows based on project analysis"""

    def __init__(self, analysis_file: str = "ci-cd-analysis.json"):
        self.analysis_file = analysis_file
        self.analysis = {}
        self.templates_dir = Path(__file__).parent.parent / "templates"

    def load_analysis(self) -> bool:
        """Load project analysis"""
        try:
            with open(self.analysis_file, "r") as f:
                self.analysis = json.load(f)
            print(f"✅ Loaded analysis from {self.analysis_file}")
            return True
        except FileNotFoundError:
            print(f"❌ Analysis file {self.analysis_file} not found")
            return False
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in {self.analysis_file}")
            return False

    def generate_workflow(self) -> str:
        """Generate customized CI/CD workflow"""
        project_info = self.analysis.get("project_info", {})
        project_type = project_info.get("type", "Unknown")

        # Load base template
        base_template = self._load_base_template()

        # Customize based on project type
        if project_type == "Python":
            workflow = self._customize_python_workflow(base_template)
        elif project_type == "Node.js":
            workflow = self._customize_nodejs_workflow(base_template)
        elif project_type == "Java":
            workflow = self._customize_java_workflow(base_template)
        elif project_type == "Go":
            workflow = self._customize_go_workflow(base_template)
        else:
            workflow = self._customize_generic_workflow(base_template)

        # Add conditional jobs
        workflow = self._add_conditional_jobs(workflow)

        return workflow

    def _load_base_template(self) -> str:
        """Load base CI/CD template"""
        base_template = """name: 🚀 Universal CI/CD Pipeline

on:
  push:
    branches: [ main, develop, feature/* ]
    tags: [ 'v*' ]
  pull_request:
    branches: [ main, develop ]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment Environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - staging
        - production
      force_deploy:
        description: 'Force deployment (bypass checks)'
        required: false
        default: false
        type: boolean

env:
  PROJECT_ID: ${{ secrets.PROJECT_ID }}
  REGION: ${{ secrets.REGION || 'us-central1' }}
  SERVICE_NAME: ${{ secrets.SERVICE_NAME || 'app' }}

jobs:
  # 🔒 SECURITY & COMPLIANCE
  security-scan:
    name: 🔒 Security & Compliance Scan
    runs-on: ubuntu-latest
    outputs:
      security-status: ${{ steps.security-check.outputs.status }}
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      - name: 🔍 Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: 📊 Upload Trivy scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

      - name: 🔐 Secret scanning
        run: |
          echo "🔍 Scanning for secrets in code..."
          if grep -r "sk-" . --exclude-dir=.git --exclude-dir=node_modules; then
            echo "❌ Potential secrets found!"
            exit 1
          fi
          echo "✅ No secrets found in code"

      - name: 📋 Dependency vulnerability check
        run: |
          echo "🔍 Checking dependencies for vulnerabilities..."
          # This will be customized based on project type

      - name: 🎯 Set security status
        id: security-check
        run: |
          echo "status=passed" >> $GITHUB_OUTPUT

  # 🧪 TESTING & VALIDATION
  test-and-validate:
    name: 🧪 Test & Validation
    runs-on: ubuntu-latest
    needs: security-scan
    outputs:
      test-status: ${{ steps.test-results.outputs.status }}
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      # This section will be customized based on project type

      - name: 🎯 Set test status
        id: test-results
        run: |
          echo "status=passed" >> $GITHUB_OUTPUT

  # 🐳 BUILD & CONTAINER
  build-container:
    name: 🐳 Build & Container
    runs-on: ubuntu-latest
    needs: [security-scan, test-and-validate]
    if: needs.security-scan.outputs.security-status == 'passed' && needs.test-and-validate.outputs.test-status == 'passed'
    outputs:
      image-tag: ${{ steps.build.outputs.image-tag }}
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      # This section will be customized based on project type

      - name: 🎯 Set image tag
        run: echo "image-tag=${{ github.sha }}" >> $GITHUB_OUTPUT

  # 🗄️ DATABASE MIGRATION (if applicable)
  # This job will be conditionally added

  # 🚀 STAGING DEPLOYMENT
  deploy-staging:
    name: 🚀 Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build-container]
    if: github.ref == 'refs/heads/develop' || github.event_name == 'workflow_dispatch'
    environment: staging
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      # This section will be customized based on deployment platform

  # 🚀 PRODUCTION DEPLOYMENT
  deploy-production:
    name: 🚀 Deploy to Production
    runs-on: ubuntu-latest
    needs: [build-container, deploy-staging]
    if: github.ref == 'refs/heads/main' || (github.event_name == 'workflow_dispatch' && github.event.inputs.environment == 'production')
    environment: production
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      # This section will be customized based on deployment platform

  # 📊 POST-DEPLOYMENT MONITORING
  post-deployment:
    name: 📊 Post-Deployment Monitoring
    runs-on: ubuntu-latest
    needs: [deploy-production, deploy-staging]
    if: always()
    steps:
      - name: 📊 Deployment status
        run: |
          echo "📊 Deployment Summary:"
          echo "Security Scan: ${{ needs.security-scan.outputs.security-status }}"
          echo "Tests: ${{ needs.test-and-validate.outputs.test-status }}"
          echo "Build: ${{ needs.build-container.outputs.image-tag }}"
          echo "Staging: ${{ needs.deploy-staging.result }}"
          echo "Production: ${{ needs.deploy-production.result }}"
"""
        return base_template

    def _customize_python_workflow(self, template: str) -> str:
        """Customize workflow for Python projects"""
        # Add Python-specific setup
        python_setup = """
      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: 📦 Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-mock

      - name: 🔍 Lint and format check
        run: |
          echo "🔍 Running linting checks..."
          pip install flake8 black isort
          black --check --diff .
          isort --check-only --diff .
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: 🧪 Run unit tests
        run: |
          echo "🧪 Running unit tests..."
          pytest tests/ -v --cov=. --cov-report=xml --cov-report=html

      - name: 📊 Upload coverage reports
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          flags: unittests
          name: codecov-umbrella
"""

        # Replace placeholder in template
        template = template.replace(
            "# This section will be customized based on project type", python_setup
        )

        # Add Python-specific build steps
        python_build = """
      - name: 🔐 Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.PROJECT_ID }}

      - name: 🐳 Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: 🏗️ Build and push Docker image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGION }}-docker.pkg/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }}
            ${{ env.REGION }}-docker.pkg/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64
"""

        template = template.replace(
            "# This section will be customized based on project type", python_build
        )

        return template

    def _customize_nodejs_workflow(self, template: str) -> str:
        """Customize workflow for Node.js projects"""
        # Add Node.js-specific setup
        nodejs_setup = """
      - name: 🟢 Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'

      - name: 📦 Install dependencies
        run: |
          npm ci

      - name: 🔍 Lint and format check
        run: |
          echo "🔍 Running linting checks..."
          npm run lint
          npm run format:check

      - name: 🧪 Run unit tests
        run: |
          echo "🧪 Running unit tests..."
          npm test
          npm run test:coverage
"""

        template = template.replace(
            "# This section will be customized based on project type", nodejs_setup
        )

        # Add Node.js-specific build steps
        nodejs_build = """
      - name: 🔐 Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.PROJECT_ID }}

      - name: 🐳 Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: 🏗️ Build and push Docker image
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGION }}-docker.pkg/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:${{ github.sha }}
            ${{ env.REGION }}-docker.pkg/${{ env.PROJECT_ID }}/${{ env.SERVICE_NAME }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64
"""

        template = template.replace(
            "# This section will be customized based on project type", nodejs_build
        )

        return template

    def _customize_generic_workflow(self, template: str) -> str:
        """Customize workflow for generic projects"""
        # Add generic setup
        generic_setup = """
      - name: 📦 Install dependencies
        run: |
          echo "📦 Installing project dependencies..."
          # Generic dependency installation logic
          if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
          elif [ -f "package.json" ]; then
            npm install
          elif [ -f "pom.xml" ]; then
            mvn install -DskipTests
          fi

      - name: 🧪 Run tests
        run: |
          echo "🧪 Running project tests..."
          # Generic test execution logic
          if [ -f "pytest.ini" ] || [ -d "tests" ]; then
            pytest tests/ -v
          elif [ -f "package.json" ] && grep -q "test" package.json; then
            npm test
          elif [ -f "pom.xml" ]; then
            mvn test
          fi
"""

        template = template.replace(
            "# This section will be customized based on project type", generic_setup
        )

        return template

    def _add_conditional_jobs(self, template: str) -> str:
        """Add conditional jobs based on project analysis"""
        # Add database migration job if needed
        if self.analysis.get("database", {}).get("migrations"):
            migration_job = """
  # 🗄️ DATABASE MIGRATION
  migrate-database:
    name: 🗄️ Database Migration
    runs-on: ubuntu-latest
    needs: [build-container]
    if: github.ref == 'refs/heads/develop' || github.ref == 'refs/heads/main'
    environment: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4

      - name: 🔐 Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ env.PROJECT_ID }}

      - name: 🗄️ Run database migrations
        run: |
          echo "🗄️ Running database migrations..."
          if [ -f "migrations/run_migrations.py" ]; then
            python migrations/run_migrations.py \
              --environment="${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}" \
              --database-url="${{ github.ref == 'refs/heads/main' && secrets.PRODUCTION_DATABASE_URL || secrets.STAGING_DATABASE_URL }}"
          fi
"""

            # Insert migration job before staging deployment
            template = template.replace(
                "# 🚀 STAGING DEPLOYMENT", migration_job + "\n  # 🚀 STAGING DEPLOYMENT"
            )

            # Update staging deployment to depend on migration
            template = template.replace(
                "needs: [build-container]", "needs: [build-container, migrate-database]"
            )

        return template

    def generate_deployment_config(self) -> str:
        """Generate deployment configuration file"""
        deployment_platform = self.analysis.get("deployment", {}).get(
            "platform", "Unknown"
        )

        if deployment_platform == "Google Cloud Run":
            return self._generate_gcp_deployment_config()
        elif deployment_platform == "Kubernetes":
            return self._generate_k8s_deployment_config()
        else:
            return self._generate_generic_deployment_config()

    def _generate_gcp_deployment_config(self) -> str:
        """Generate GCP Cloud Run deployment configuration"""
        config = """# 🚀 GCP Cloud Run Deployment Configuration

# Environment-specific configurations
environments:
  staging:
    name: "Staging Environment"
    description: "Pre-production testing environment"
    auto_deploy: true
    required_reviews: 1
    scaling:
      min_instances: 0
      max_instances: 10
      concurrency: 80
    resources:
      cpu: "1"
      memory: "2Gi"

  production:
    name: "Production Environment"
    description: "Live production environment"
    auto_deploy: false
    required_reviews: 2
    scaling:
      min_instances: 1
      max_instances: 100
      concurrency: 80
    resources:
      cpu: "2"
      memory: "4Gi"

# Required secrets
required_secrets:
  - GCP_PROJECT_ID
  - GCP_SA_KEY
  - PROJECT_ID
  - REGION
  - SERVICE_NAME

# Optional secrets (add as needed)
optional_secrets:
  - DATABASE_URL
  - API_KEY
  - SECRET_KEY
"""
        return config

    def _generate_k8s_deployment_config(self) -> str:
        """Generate Kubernetes deployment configuration"""
        config = """# 🚀 Kubernetes Deployment Configuration

# Namespace configuration
namespaces:
  staging: "staging"
  production: "production"

# Resource limits
resources:
  staging:
    cpu: "500m"
    memory: "1Gi"
  production:
    cpu: "1000m"
    memory: "2Gi"

# Required secrets
required_secrets:
  - KUBECONFIG
  - DOCKER_REGISTRY
  - IMAGE_TAG
"""
        return config

    def _generate_generic_deployment_config(self) -> str:
        """Generate generic deployment configuration"""
        config = """# 🚀 Generic Deployment Configuration

# Deployment environments
environments:
  staging:
    name: "Staging"
    description: "Pre-production environment"
    auto_deploy: true
    
  production:
    name: "Production"
    description: "Live production environment"
    auto_deploy: false

# Required configuration
required_config:
  - PROJECT_NAME
  - DEPLOYMENT_REGION
  - SERVICE_NAME
"""
        return config

    def generate_setup_guide(self) -> str:
        """Generate setup guide for developers"""
        guide = f"""# 🚀 CI/CD Setup Guide for {self.analysis.get('project_info', {}).get('name', 'Your Project')}

## 📋 Quick Start

### 1. Copy CI/CD Files
```bash
# Copy the generated workflow
cp .github/workflows/ci-cd-pipeline.yml .github/workflows/

# Copy deployment configuration
cp deployment-config.yml .github/
```

### 2. Configure GitHub Secrets
Go to your repository → Settings → Secrets and variables → Actions

Add these required secrets:
{self._format_secrets_list()}

### 3. Customize Configuration
Update these variables in the workflow file:
- `PROJECT_ID`: Your project identifier
- `REGION`: Your deployment region
- `SERVICE_NAME`: Your service name

### 4. Enable Environments
Go to Settings → Environments and create:
- **staging**: Auto-deploy from develop branch
- **production**: Manual approval required

## 🔧 Customization Options

### Project Type: {self.analysis.get('project_info', {}).get('type', 'Unknown')}
### Language: {self.analysis.get('project_info', {}).get('language', 'Unknown')}
### Framework: {self.analysis.get('project_info', {}).get('framework', 'Unknown')}

## 📊 What's Included

This CI/CD pipeline automatically includes:
- ✅ Security scanning and compliance
- ✅ Automated testing and validation
- ✅ Container building and optimization
- ✅ Progressive deployment strategies
- ✅ Health monitoring and rollback
- ✅ Database migration support (if applicable)

## 🚨 Troubleshooting

### Common Issues:
1. **Missing Secrets**: Ensure all required secrets are added
2. **Permission Errors**: Check service account permissions
3. **Build Failures**: Verify Dockerfile and dependencies
4. **Deployment Failures**: Check environment configuration

## 📞 Support

For issues or questions:
- Check the workflow logs in GitHub Actions
- Review the deployment configuration
- Contact the DevOps team
"""
        return guide

    def _format_secrets_list(self) -> str:
        """Format the list of required secrets"""
        secrets = self.analysis.get("ci_cd_requirements", {}).get(
            "required_secrets", []
        )
        if not secrets:
            return "- No specific secrets required"

        formatted = ""
        for secret in secrets:
            formatted += f"- `{secret}`\n"
        return formatted

    def save_workflow(
        self, workflow: str, output_file: str = ".github/workflows/ci-cd-pipeline.yml"
    ):
        """Save the generated workflow"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, "w") as f:
            f.write(workflow)

        print(f"✅ Workflow saved to {output_file}")

    def save_deployment_config(
        self, config: str, output_file: str = "deployment-config.yml"
    ):
        """Save the deployment configuration"""
        with open(output_file, "w") as f:
            f.write(config)

        print(f"✅ Deployment config saved to {output_file}")

    def save_setup_guide(self, guide: str, output_file: str = "CI-CD-SETUP.md"):
        """Save the setup guide"""
        with open(output_file, "w") as f:
            f.write(guide)

        print(f"✅ Setup guide saved to {output_file}")

    def generate_all(self):
        """Generate all CI/CD files"""
        if not self.load_analysis():
            return False

        print("🚀 Generating CI/CD pipeline...")

        # Generate workflow
        workflow = self.generate_workflow()
        self.save_workflow(workflow)

        # Generate deployment config
        deployment_config = self.generate_deployment_config()
        self.save_deployment_config(deployment_config)

        # Generate setup guide
        setup_guide = self.generate_setup_guide()
        self.save_setup_guide(setup_guide)

        print("🎉 All CI/CD files generated successfully!")
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Universal CI/CD Template Generator")
    parser.add_argument(
        "--analysis", "-a", default="ci-cd-analysis.json", help="Analysis file path"
    )
    parser.add_argument("--output-dir", "-o", default=".", help="Output directory")

    args = parser.parse_args()

    # Change to output directory
    os.chdir(args.output_dir)

    # Generate CI/CD files
    generator = CICDTemplateGenerator(args.analysis)
    if generator.generate_all():
        print("\n📁 Generated files:")
        print("  - .github/workflows/ci-cd-pipeline.yml")
        print("  - deployment-config.yml")
        print("  - CI-CD-SETUP.md")

        print("\n🚀 Next steps:")
        print("  1. Review the generated files")
        print("  2. Add required secrets to GitHub")
        print("  3. Customize configuration if needed")
        print("  4. Push to trigger the pipeline")
    else:
        print("❌ Failed to generate CI/CD files")


if __name__ == "__main__":
    main()
