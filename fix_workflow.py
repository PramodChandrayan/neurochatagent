#!/usr/bin/env python3
"""
Script to fix the workflow generation in intelligent_toolbox_v4.py
to use Artifact Registry instead of gcr.io
"""

import re

def fix_workflow_file():
    """Fix the workflow generation to use Artifact Registry"""
    
    # Read the current file
    with open('intelligent-cicd-system/intelligent_toolbox_v4.py', 'r') as f:
        content = f.read()
    
    # Replace gcr.io with Artifact Registry
    # Pattern 1: docker build and push commands
    content = re.sub(
        r'docker build -t gcr\.io/\$\{\{\{ env\.GCP_PROJECT_ID \}\}\}/\$\{\{\{ env\.SERVICE_NAME \}\}\}:\$\{\{\{ github\.sha \}\}\} \.',
        'docker build -t us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}} .',
        content
    )
    
    content = re.sub(
        r'docker push gcr\.io/\$\{\{\{ env\.GCP_PROJECT_ID \}\}\}/\$\{\{\{ env\.SERVICE_NAME \}\}\}:\$\{\{\{ github\.sha \}\}\}',
        'docker push us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}',
        content
    )
    
    # Pattern 2: image reference in deploy step
    content = re.sub(
        r'image: gcr\.io/\$\{\{\{ env\.GCP_PROJECT_ID \}\}\}/\$\{\{\{ env\.SERVICE_NAME \}\}\}:\$\{\{\{ github\.sha \}\}\}',
        'image: us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}',
        content
    )
    
    # Add Artifact Registry configuration
    content = re.sub(
        r'- name: Configure Docker\n      run: gcloud auth configure-docker',
        '''- name: Configure Docker for Artifact Registry
      run: |
        # Configure Docker to use Artifact Registry
        gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
        echo "✅ Docker configured for Artifact Registry"
      
    - name: Create Artifact Registry repository
      run: |
        echo "🏗️ Creating Artifact Registry repository..."
        # Create Artifact Registry repository if it doesn't exist
        gcloud artifacts repositories create ${{ env.SERVICE_NAME }} \\
          --repository-format=docker \\
          --location=${{ env.REGION }} \\
          --description="Docker repository for ${{ env.SERVICE_NAME }}" \\
          --quiet || echo "Repository already exists"
        echo "✅ Artifact Registry repository ready"''',
        content
    )
    
    # Add better logging to build and push steps
    content = re.sub(
        r'- name: Build and push container\n      run: \|\n        docker build -t us-central1-docker\.pkg\.dev/\$\{\{\{ env\.GCP_PROJECT_ID \}\}\}/\$\{\{\{ env\.SERVICE_NAME \}\}\}/\$\{\{\{ env\.SERVICE_NAME \}\}\}:\$\{\{\{ github\.sha \}\}\} \.\n        docker push us-central1-docker\.pkg\.dev/\$\{\{\{ env\.GCP_PROJECT_ID \}\}\}/\$\{\{\{ env\.SERVICE_NAME \}\}\}/\$\{\{\{ env\.SERVICE_NAME \}\}\}:\$\{\{\{ github\.sha \}\}\}',
        '''- name: Build and push container
      run: |
        echo "🐳 Building and pushing Docker image..."
        # Use Artifact Registry instead of Container Registry
        docker build -t us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}} .
        echo "✅ Docker image built successfully"
        
        echo "📤 Pushing to Artifact Registry..."
        docker push us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}
        echo "✅ Docker image pushed successfully"''',
        content
    )
    
    # Write the fixed content back
    with open('intelligent-cicd-system/intelligent_toolbox_v4.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed workflow generation to use Artifact Registry")

if __name__ == '__main__':
    fix_workflow_file()
