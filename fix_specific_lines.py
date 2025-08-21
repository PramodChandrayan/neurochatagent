#!/usr/bin/env python3
"""
Fix specific gcr.io lines in the workflow generation
"""

def fix_specific_lines():
    with open('intelligent-cicd-system/intelligent_toolbox_v4.py', 'r') as f:
        lines = f.readlines()
    
    # Fix the first occurrence (around line 2326)
    for i, line in enumerate(lines):
        if 'docker build -t gcr.io/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}} .' in line:
            lines[i] = '        docker build -t us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}} .\n'
        elif 'docker push gcr.io/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}' in line:
            lines[i] = '        docker push us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}\n'
        elif 'image: gcr.io/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}' in line:
            lines[i] = '        image: us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}\n'
    
    with open('intelligent-cicd-system/intelligent_toolbox_v4.py', 'w') as f:
        f.writelines(lines)
    
    print("✅ Fixed specific gcr.io lines")

if __name__ == '__main__':
    fix_specific_lines()
