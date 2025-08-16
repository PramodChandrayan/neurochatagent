#!/usr/bin/env python3
"""
📋 Pipeline Generator
Generates CI/CD pipeline configuration with state management
"""

from typing import Dict, Any
from state_manager import StateManager

class PipelineGenerator:
    """Generates CI/CD pipeline configuration"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    def generate_cicd_yaml(self) -> bool:
        """Generate CI/CD YAML configuration"""
        try:
            print("📋 Generating CI/CD YAML configuration...")
            
            # Get infrastructure and secrets state
            infra_state = self.state_manager.get_infrastructure_state()
            secrets_state = self.state_manager.get_secrets_state()
            
            if not infra_state['setup_complete']:
                print("❌ Infrastructure not complete - cannot generate pipeline")
                return False
            
            if not secrets_state['secrets_extracted']:
                print("❌ Secrets not extracted - cannot generate pipeline")
                return False
            
            # Generate the YAML content
            yaml_content = self._generate_yaml_content(infra_state, secrets_state)
            
            # Write to file
            with open('.github/workflows/deploy.yml', 'w') as f:
                f.write(yaml_content)
            
            print("✅ CI/CD YAML generated successfully")
            
            # Update state
            self.state_manager.update_github_state(yaml_generated=True, setup_complete=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to generate CI/CD YAML: {e}")
            return False
    
    def _generate_yaml_content(self, infra_state: Dict[str, Any], secrets_state: Dict[str, Any]) -> str:
        """Generate the actual YAML content"""
        
        yaml_content = f"""name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

env:
  PROJECT_ID: {infra_state['project_id']}
  REGION: us-central1
  SERVICE_NAME: neurogent-finance-assistant
  ARTIFACT_REGISTRY: {infra_state['artifact_registry']}

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    permissions:
      contents: read
      id-token: write
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Google Auth
      id: auth
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{{{ secrets.WORKLOAD_IDENTITY_PROVIDER }}}}
        service_account: ${{{{ secrets.GCP_SERVICE_ACCOUNT }}}}
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
    
    - name: Configure Docker
      run: gcloud auth configure-docker
    
    - name: Build and push image
      run: |
        docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY/$SERVICE_NAME:${{{{ github.sha }}}} .
        docker push $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY/$SERVICE_NAME:${{{{ github.sha }}}}
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy $SERVICE_NAME \\
          --image $REGION-docker.pkg.dev/$PROJECT_ID/$ARTIFACT_REGISTRY/$SERVICE_NAME:${{{{ github.sha }}}} \\
          --region $REGION \\
          --platform managed \\
          --allow-unauthenticated \\
          --port 8501
"""
        
        return yaml_content
