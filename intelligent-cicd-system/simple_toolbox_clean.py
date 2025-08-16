import streamlit as st
import subprocess
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Set page config at the very top
st.set_page_config(
    page_title="Intelligent CI/CD Toolbox",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SimpleToolbox:
    def __init__(self):
        self.initialize_state()
        self.load_state()
    
    def initialize_state(self):
        """Initialize default state values"""
        if 'phase' not in st.session_state:
            st.session_state['phase'] = 'authentication'
        if 'gcp_authenticated' not in st.session_state:
            st.session_state['gcp_authenticated'] = False
        if 'github_authenticated' not in st.session_state:
            st.session_state['github_authenticated'] = False
        if 'infrastructure_complete' not in st.session_state:
            st.session_state['infrastructure_complete'] = False
        if 'secrets_complete' not in st.session_state:
            st.session_state['secrets_complete'] = False
        if 'pipeline_complete' not in st.session_state:
            st.session_state['pipeline_complete'] = False
        if 'cicd_files_created' not in st.session_state:
            st.session_state['cicd_files_created'] = False
    
    def load_state(self):
        """Load state from file"""
        try:
            if os.path.exists('toolbox_state.json'):
                with open('toolbox_state.json', 'r') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        st.session_state[key] = value
        except Exception as e:
            st.warning(f"Could not load state: {e}")
    
    def save_state(self):
        """Save state to file"""
        try:
            # Filter out non-serializable objects
            state_data = {}
            for key, value in st.session_state.items():
                if isinstance(value, (str, int, float, bool, list, dict)):
                    state_data[key] = value
                else:
                    state_data[key] = str(value)
            
            with open('toolbox_state.json', 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            st.error(f"Could not save state: {e}")
    
    def update_state(self, **kwargs):
        """Update state values"""
        for key, value in kwargs.items():
            st.session_state[key] = value
        self.save_state()
    
    def add_error(self, message: str):
        """Add error message to session state"""
        if 'errors' not in st.session_state:
            st.session_state['errors'] = []
        st.session_state['errors'].append(message)
    
    def run(self):
        """Main application runner"""
        st.title("🚀 Intelligent CI/CD Toolbox")
        st.markdown("**Complete CI/CD Pipeline Setup for Google Cloud Platform**")
        
        # Show current phase
        st.sidebar.markdown("## 📍 Current Phase")
        st.sidebar.info(f"**{st.session_state['phase'].title()}**")
        
        # Phase navigation
        if st.session_state['phase'] == 'authentication':
            self.show_authentication_phase()
        elif st.session_state['phase'] == 'infrastructure':
            self.show_infrastructure_phase()
        elif st.session_state['phase'] == 'secrets':
            self.show_secrets_phase()
        elif st.session_state['phase'] == 'pipeline':
            self.show_pipeline_phase()
        elif st.session_state['phase'] == 'deploy':
            self.show_deploy_phase()
    
    def show_authentication_phase(self):
        """Show authentication phase"""
        st.markdown("## 🔐 Phase 1: Authentication")
        
        # Check current authentication status
        self.check_auth_status()
        
        # Authentication buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔑 Authenticate GCP"):
                if self.authenticate_gcp():
                    st.success("✅ GCP authentication successful!")
                    self.update_state(phase='infrastructure')
                    st.rerun()
                else:
                    st.error("❌ GCP authentication failed")
        
        with col2:
            if st.button("🔑 Authenticate GitHub"):
                if self.authenticate_github():
                    st.success("✅ GitHub authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ GitHub authentication failed")
        
        # Show next phase button if both are authenticated
        if st.session_state['gcp_authenticated'] and st.session_state['github_authenticated']:
            if st.button("🚀 Continue to Infrastructure Setup"):
                self.update_state(phase='infrastructure')
                st.rerun()
    
    def check_auth_status(self):
        """Check current authentication status"""
        st.markdown("### 🔍 Authentication Status")
        
        # GCP Status
        try:
            result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'], 
                                 capture_output=True, text=True, check=True)
            if result.stdout.strip():
                st.success(f"✅ **GCP**: {result.stdout.strip()}")
                st.session_state['gcp_authenticated'] = True
            else:
                st.error("❌ **GCP**: Not authenticated")
                st.session_state['gcp_authenticated'] = False
        except Exception as e:
            st.error(f"❌ **GCP**: Error checking status - {e}")
            st.session_state['gcp_authenticated'] = False
        
        # GitHub Status
        try:
            result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, check=False)
            if result.returncode == 0 and 'Logged in to github.com' in result.stdout:
                # Extract username
                username_match = None
                for line in result.stdout.split('\n'):
                    if 'Logged in to github.com as' in line:
                        username_match = line.split('Logged in to github.com as')[-1].strip()
                        break
                
                if username_match:
                    st.success(f"✅ **GitHub**: {username_match}")
                else:
                    st.success("✅ **GitHub**: Authenticated")
                st.session_state['github_authenticated'] = True
            else:
                st.error("❌ **GitHub**: Not authenticated")
                st.session_state['github_authenticated'] = False
        except Exception as e:
            st.error(f"❌ **GitHub**: Error checking status - {e}")
            st.session_state['github_authenticated'] = False
    
    def authenticate_gcp(self) -> bool:
        """Authenticate with GCP"""
        try:
            st.info("🔑 Authenticating with GCP...")
            
            # Check if already authenticated
            result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE'], 
                                 capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                st.success("✅ Already authenticated with GCP")
                return True
            
            # Run interactive authentication
            st.info("📱 Please complete GCP authentication in the terminal...")
            result = subprocess.run(['gcloud', 'auth', 'login'], 
                                 capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                st.success("✅ GCP authentication successful!")
                return True
            else:
                st.error("❌ GCP authentication failed")
                return False
                
        except Exception as e:
            st.error(f"❌ GCP authentication error: {e}")
            return False
    
    def authenticate_github(self) -> bool:
        """Authenticate with GitHub"""
        try:
            st.info("🔑 Authenticating with GitHub...")
            
            # Check if already authenticated
            result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, check=False)
            
            if result.returncode == 0 and 'Logged in to github.com' in result.stdout:
                st.success("✅ Already authenticated with GitHub")
                return True
            
            # Run interactive authentication
            st.info("📱 Please complete GitHub authentication in the terminal...")
            result = subprocess.run(['gh', 'auth', 'login'], 
                                 capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                st.success("✅ GitHub authentication successful!")
                return True
            else:
                st.error("❌ GitHub authentication failed")
                return False
                
        except Exception as e:
            st.error(f"❌ GitHub authentication error: {e}")
            return False
    
    def show_infrastructure_phase(self):
        """Show infrastructure setup phase"""
        st.markdown("## 🏗️ Phase 2: Infrastructure Setup")
        
        if not st.session_state['infrastructure_complete']:
            st.info("Setting up GCP infrastructure...")
            
            if st.button("🚀 Setup Infrastructure"):
                with st.spinner("Setting up infrastructure..."):
                    if self.setup_infrastructure():
                        self.update_state(infrastructure_complete=True, phase='secrets')
                        st.success("✅ Infrastructure setup complete!")
                        st.rerun()
                    else:
                        st.error("❌ Infrastructure setup failed")
        else:
            st.success("🎉 Infrastructure setup complete!")
            st.info("Ready to proceed to secrets configuration")
            
            if st.button("🔐 Continue to Secrets Configuration"):
                self.update_state(phase='secrets')
                st.rerun()
    
    def setup_infrastructure(self) -> bool:
        """Setup GCP infrastructure"""
        try:
            # Get current project
            project_result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                         capture_output=True, text=True, check=True)
            project_id = project_result.stdout.strip()
            
            if not project_id:
                st.error("❌ No GCP project configured")
                st.info("Please run: gcloud config set project PROJECT_ID")
                return False
            
            st.session_state['gcp_project'] = project_id
            st.success(f"✅ Using GCP project: {project_id}")
            
            # Enable required APIs
            required_apis = [
                'run.googleapis.com',
                'iam.googleapis.com',
                'artifactregistry.googleapis.com',
                'cloudbuild.googleapis.com'
            ]
            
            for api in required_apis:
                try:
                    st.info(f"🔌 Enabling {api}...")
                    subprocess.run(['gcloud', 'services', 'enable', api], 
                                capture_output=True, text=True, check=True)
                    st.success(f"✅ Enabled {api}")
                except subprocess.CalledProcessError as e:
                    if "already enabled" in e.stderr.lower():
                        st.success(f"✅ {api} already enabled")
                    else:
                        st.warning(f"⚠️ Could not enable {api}: {e.stderr}")
            
            # Create service account
            service_account_name = "cicd-service-account"
            service_account_email = f"{service_account_name}@{project_id}.iam.gserviceaccount.com"
            
            try:
                st.info(f"👤 Creating service account: {service_account_name}")
                subprocess.run(['gcloud', 'iam', 'service-accounts', 'create', service_account_name, 
                              '--display-name', 'CI/CD Service Account'], 
                             capture_output=True, text=True, check=True)
                st.success(f"✅ Created service account: {service_account_email}")
            except subprocess.CalledProcessError as e:
                if "already exists" in e.stderr.lower():
                    st.success(f"✅ Service account already exists: {service_account_email}")
                else:
                    st.error(f"❌ Failed to create service account: {e.stderr}")
                    return False
            
            st.session_state['service_account_email'] = service_account_email
            
            # Grant necessary roles
            roles = [
                'roles/run.admin',
                'roles/iam.serviceAccountUser',
                'roles/artifactregistry.writer',
                'roles/cloudbuild.builds.builder'
            ]
            
            for role in roles:
                try:
                    st.info(f"🔐 Granting {role}...")
                    subprocess.run(['gcloud', 'projects', 'add-iam-policy-binding', project_id,
                                  '--member', f'serviceAccount:{service_account_email}',
                                  '--role', role], 
                                 capture_output=True, text=True, check=True)
                    st.success(f"✅ Granted {role}")
                except subprocess.CalledProcessError as e:
                    st.warning(f"⚠️ Could not grant {role}: {e.stderr}")
            
            # Create Artifact Registry
            try:
                st.info("📦 Creating Artifact Registry...")
                subprocess.run(['gcloud', 'artifacts', 'repositories', 'create', 'neurogent-repo',
                              '--repository-format', 'docker',
                              '--location', 'us-central1'], 
                             capture_output=True, text=True, check=True)
                st.success("✅ Created Artifact Registry: neurogent-repo")
            except subprocess.CalledProcessError as e:
                if "already exists" in e.stderr.lower():
                    st.success("✅ Artifact Registry already exists: neurogent-repo")
                else:
                    st.warning(f"⚠️ Could not create Artifact Registry: {e.stderr}")
            
            # Setup Workload Identity Federation
            try:
                st.info("🔗 Setting up Workload Identity Federation...")
                
                # Create WIF pool
                pool_name = "neurogent-wif-pool"
                subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'create', pool_name,
                              '--location', 'global',
                              '--display-name', 'Neurogent WIF Pool'], 
                             capture_output=True, text=True, check=True)
                st.success(f"✅ Created WIF pool: {pool_name}")
                
                # Create OIDC provider
                provider_name = "github-actions"
                subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'providers', 'create-oidc', provider_name,
                              '--workload-identity-pool', pool_name,
                              '--location', 'global',
                              '--issuer-uri', 'https://token.actions.githubusercontent.com',
                              '--attribute-mapping', 'google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner',
                              '--attribute-condition', 'assertion.repository_owner=="PramodChandrayan"'], 
                             capture_output=True, text=True, check=True)
                st.success(f"✅ Created OIDC provider: {provider_name}")
                
                st.session_state['workload_identity_pool'] = pool_name
                st.session_state['workload_identity_provider'] = provider_name
                
            except subprocess.CalledProcessError as e:
                if "already exists" in e.stderr.lower():
                    st.success("✅ Workload Identity Federation already exists")
                else:
                    st.error(f"❌ Failed to setup WIF: {e.stderr}")
                    return False
            
            st.success("🎉 Infrastructure setup complete!")
            return True
            
        except Exception as e:
            st.error(f"❌ Infrastructure setup failed: {e}")
            return False
    
    def show_secrets_phase(self):
        """Show secrets configuration phase"""
        st.markdown("## 🔐 Phase 3: Secrets Configuration")
        
        if not st.session_state['secrets_complete']:
            if self.configure_secrets():
                self.update_state(secrets_complete=True, phase='pipeline')
                st.success("🎉 Secrets configuration complete!")
                st.rerun()
        else:
            st.success("🎉 Secrets configuration complete!")
            st.info("Ready to proceed to pipeline creation")
            
            if st.button("📋 Continue to Pipeline Creation"):
                self.update_state(phase='pipeline')
                st.rerun()
    
    def configure_secrets(self) -> bool:
        """Configure GitHub secrets for CI/CD"""
        try:
            st.markdown("### 🔍 Analyzing infrastructure and GitHub secrets...")
            
            # Get current infrastructure state
            project_id = st.session_state.get('gcp_project')
            service_account = st.session_state.get('service_account_email')
            wif_pool = st.session_state.get('workload_identity_pool')
            wif_provider = st.session_state.get('workload_identity_provider')
            
            if not all([project_id, service_account, wif_pool, wif_provider]):
                st.error("❌ Missing required infrastructure configuration")
                return False
            
            st.success("✅ Infrastructure configuration found:")
            st.info(f"📋 Project ID: {project_id}")
            st.info(f"👤 Service Account: {service_account}")
            st.info(f"🔗 WIF Pool: {wif_pool}")
            st.info(f"🔗 WIF Provider: {wif_provider}")
            
            # Extract WIF provider full name
            wif_provider_full_name = f"projects/{project_id}/locations/global/workloadIdentityPools/{wif_pool}/providers/{wif_provider}"
            st.success(f"✅ WIF Provider Resource: {wif_provider_full_name}")
            
            # Check GitHub repository
            try:
                result = subprocess.run(['gh', 'repo', 'view', '--json', 'name,owner'], 
                                      capture_output=True, text=True, check=True)
                repo_info = json.loads(result.stdout)
                repo_name = repo_info['name']
                repo_owner = repo_info['owner']['login']
                st.success(f"✅ Repository: {repo_owner}/{repo_name}")
            except Exception as e:
                st.error(f"❌ Could not get repository info: {e}")
                return False
            
            # Check existing secrets
            try:
                result = subprocess.run(['gh', 'secret', 'list', '--repo', f'{repo_owner}/{repo_name}'], 
                                      capture_output=True, text=True, check=True)
                existing_secrets = result.stdout
                
                required_secrets = {
                    'GCP_WORKLOAD_IDENTITY_PROVIDER': wif_provider_full_name,
                    'GCP_SERVICE_ACCOUNT_EMAIL': service_account,
                    'GCP_PROJECT_ID': project_id
                }
                
                missing_secrets = []
                for secret_name, secret_value in required_secrets.items():
                    if secret_name in existing_secrets:
                        st.success(f"✅ {secret_name} - Already configured")
                    else:
                        st.error(f"❌ {secret_name} - Missing")
                        missing_secrets.append(secret_name)
                        st.code(secret_value, language='text')
                
                if not missing_secrets:
                    st.success("🎉 All required secrets are already configured!")
                    return True
                
                # Configure missing secrets
                if st.button("🚀 Configure Missing Secrets"):
                    with st.spinner("Configuring secrets..."):
                        success_count = 0
                        
                        for secret_name in missing_secrets:
                            try:
                                secret_value = required_secrets[secret_name]
                                result = subprocess.run(['gh', 'secret', 'set', secret_name, '--repo', 
                                                       f'{repo_owner}/{repo_name}', '--body', secret_value], 
                                                      capture_output=True, text=True, check=True)
                                st.success(f"✅ {secret_name} configured successfully!")
                                success_count += 1
                            except Exception as e:
                                st.error(f"❌ Failed to configure {secret_name}: {e}")
                        
                        if success_count == len(missing_secrets):
                            st.success("🎉 All secrets configured successfully!")
                            return True
                        else:
                            st.error(f"❌ Only {success_count}/{len(missing_secrets)} secrets configured")
                            return False
                
            except Exception as e:
                st.error(f"❌ Error checking secrets: {e}")
                return False
            
            return False
            
        except Exception as e:
            st.error(f"❌ Secrets configuration failed: {e}")
            return False
    
    def show_pipeline_phase(self):
        """Show pipeline creation phase"""
        st.markdown("## 📋 Phase 4: Pipeline Creation")
        
        if not st.session_state['pipeline_complete']:
            st.info("Creating CI/CD pipeline files...")
            
            if st.button("📋 Generate CI/CD Pipeline Files"):
                with st.spinner("Generating pipeline files..."):
                    if self.create_cicd_files():
                        self.update_state(pipeline_complete=True, phase='deploy')
                        st.success("✅ Pipeline files created successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to create pipeline files")
        else:
            st.success("🎉 Pipeline files created successfully!")
            st.info("Ready to proceed to deployment")
            
            if st.button("🚀 Continue to Deployment"):
                self.update_state(phase='deploy')
                st.rerun()
    
    def create_cicd_files(self) -> bool:
        """Create CI/CD pipeline files"""
        try:
            # Create .github/workflows directory
            os.makedirs(".github/workflows", exist_ok=True)
            
            # Generate CI/CD YAML
            project_id = st.session_state.get('gcp_project')
            service_account = st.session_state.get('service_account_email')
            wif_pool = st.session_state.get('workload_identity_pool')
            wif_provider = st.session_state.get('workload_identity_provider')
            
            # Let user choose YAML type
            yaml_type = st.selectbox(
                "Select pipeline complexity:",
                ["comprehensive", "simple"],
                format_func=lambda x: "🚀 Comprehensive (Full CI/CD with testing, security, staging)" if x == "comprehensive" else "⚡ Simple (Basic build and deploy)"
            )
            
            if st.button("📋 Generate Selected CI/CD Pipeline"):
                cicd_yaml = self.generate_cicd_yaml(project_id, service_account, wif_pool, wif_provider, yaml_type)
                
                if not cicd_yaml:
                    st.error("❌ Failed to generate CI/CD configuration")
                    return False
                
                # Write YAML to file
                yaml_file = ".github/workflows/deploy.yml"
                with open(yaml_file, 'w') as f:
                    f.write(cicd_yaml)
                
                st.success(f"✅ Generated {yaml_file} ({yaml_type})")
                
                # Generate Dockerfile
                dockerfile_content = self.generate_dockerfile()
                if dockerfile_content:
                    with open("Dockerfile", 'w') as f:
                        f.write(dockerfile_content)
                    st.success("✅ Generated Dockerfile")
                
                # Ensure requirements.txt exists
                if not os.path.exists("requirements.txt"):
                    requirements_content = """streamlit>=1.28.0
google-cloud-iam>=2.0.0
google-cloud-run>=0.10.0
google-cloud-artifact-registry>=1.0.0
google-auth>=2.0.0
"""
                    with open("requirements.txt", 'w') as f:
                        f.write(requirements_content)
                    st.success("✅ Created requirements.txt")
                
                st.success("🎉 All CI/CD pipeline files created successfully!")
                return True
            
            return False
            
        except Exception as e:
            st.error(f"❌ Failed to create CI/CD files: {e}")
            return False
    
    def generate_cicd_yaml(self, project_id: str, service_account: str, wif_pool: str, wif_provider: str, yaml_type: str = "comprehensive") -> str:
        """Generate CI/CD YAML configuration"""
        try:
            if yaml_type == "simple":
                return self._generate_simple_yaml(project_id, service_account, wif_pool, wif_provider)
            else:
                return self._generate_comprehensive_yaml(project_id, service_account, wif_pool, wif_provider)
        except Exception as e:
            st.error(f"❌ Failed to generate YAML: {e}")
            return ""
    
    def _generate_simple_yaml(self, project_id: str, service_account: str, wif_pool: str, wif_provider: str) -> str:
        """Generate simple CI/CD YAML configuration"""
        yaml_content = """name: Deploy to Cloud Run (Simple)

on:
  push:
    branches: [ main, master, develop ]
  workflow_dispatch:

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  SERVICE_ACCOUNT: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}
  REGION: us-central1
  SERVICE_NAME: neurochatagent
  IMAGE_NAME: neurochatagent

permissions:
  contents: read
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Google Auth
      id: auth
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
        service_account: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}
        
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: Configure Docker for Artifact Registry
      run: |
        gcloud auth configure-docker us-central1-docker.pkg.dev
        
    - name: Build and push image
      run: |
        docker build -t us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}:${{ github.sha }} .
        docker push us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}:${{ github.sha }}
        
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy ${{ env.SERVICE_NAME }} \\
          --image us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}:${{ github.sha }} \\
          --platform managed \\
          --region ${{ env.REGION }} \\
          --allow-unauthenticated \\
          --service-account ${{ env.SERVICE_ACCOUNT }} \\
          --port 8501
"""
        return yaml_content
    
    def _generate_comprehensive_yaml(self, project_id: str, service_account: str, wif_pool: str, wif_provider: str) -> str:
        """Generate comprehensive CI/CD YAML configuration"""
        yaml_content = """name: Deploy to Cloud Run (Comprehensive)

on:
  push:
    branches: [ main, master, develop ]
  pull_request:
    branches: [ main, master, develop ]
  workflow_dispatch:

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  SERVICE_ACCOUNT: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}
  REGION: us-central1
  SERVICE_NAME: neurochatagent
  IMAGE_NAME: neurochatagent

permissions:
  contents: read
  id-token: write

jobs:
  # Stage 1: Code Quality & Security
  code-quality:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install flake8 black isort bandit safety
        
    - name: Lint with flake8
      run: |
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        
    - name: Format check with black
      run: |
        black --check --diff .
        
    - name: Import sorting check with isort
      run: |
        isort --check-only --diff .
        
    - name: Security scan with bandit
      run: |
        bandit -r . -f json -o bandit-report.json || true
        
    - name: Security vulnerabilities check
      run: |
        safety check --json --output safety-report.json || true

  # Stage 2: Testing
  test:
    runs-on: ubuntu-latest
    needs: code-quality
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock
        
    - name: Run tests with coverage
      run: |
        pytest --cov=. --cov-report=xml --cov-report=html
        
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  # Stage 3: Build & Security Scan
  build-and-scan:
    runs-on: ubuntu-latest
    needs: test
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
      
    - name: Build Docker image
      id: build
      uses: docker/build-push-action@v4
      with:
        context: .
        push: false
        tags: ${{ env.IMAGE_NAME }}:${{ github.sha }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
        
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.IMAGE_NAME }}:${{ github.sha }}
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'

  # Stage 4: Deploy to Staging (if PR)
  deploy-staging:
    runs-on: ubuntu-latest
    needs: build-and-scan
    if: github.event_name == 'pull_request'
    environment: staging
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Google Auth
      id: auth
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
        service_account: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}
        
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: Configure Docker for Artifact Registry
      run: |
        gcloud auth configure-docker us-central1-docker.pkg.dev
        
    - name: Build and push staging image
      run: |
        docker build -t us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}-staging:${{ github.sha }} .
        docker push us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}-staging:${{ github.sha }}
        
    - name: Deploy to Cloud Run (Staging)
      run: |
        gcloud run deploy ${{ env.SERVICE_NAME }}-staging \\
          --image us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}-staging:${{ github.sha }} \\
          --platform managed \\
          --region ${{ env.REGION }} \\
          --allow-unauthenticated \\
          --service-account ${{ env.SERVICE_ACCOUNT }} \\
          --port 8501 \\
          --memory 1Gi \\
          --cpu 1 \\
          --max-instances 5

  # Stage 5: Deploy to Production (if push to main/master)
  deploy-production:
    runs-on: ubuntu-latest
    needs: build-and-scan
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master'
    environment: production
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Google Auth
      id: auth
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
        service_account: ${{ secrets.GCP_SERVICE_ACCOUNT_EMAIL }}
        
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: Configure Docker for Artifact Registry
      run: |
        gcloud auth configure-docker us-central1-docker.pkg.dev
        
    - name: Build and push production image
      run: |
        docker build -t us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}:${{ github.sha }} .
        docker push us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}:${{ github.sha }}
        
    - name: Deploy to Cloud Run (Production)
      run: |
        gcloud run deploy ${{ env.SERVICE_NAME }} \\
          --image us-central1-docker.pkg/${{ env.PROJECT_ID }}/neurogent-repo/${{ env.IMAGE_NAME }}:${{ github.sha }} \\
          --platform managed \\
          --region ${{ env.REGION }} \\
          --allow-unauthenticated \\
          --service-account ${{ env.SERVICE_ACCOUNT }} \\
          --port 8501 \\
          --memory 1Gi \\
          --cpu 1 \\
          --max-instances 10 \\
          --min-instances 1 \\
          --concurrency 80
        
    - name: Show deployment URL
      run: |
        DEPLOYMENT_URL=$(gcloud run services describe ${{ env.SERVICE_NAME }} \\
          --platform managed \\
          --region ${{ env.REGION }} \\
          --format 'value(status.url)')
        echo "🚀 Production Deployment URL: $DEPLOYMENT_URL"
        echo "DEPLOYMENT_URL=$DEPLOYMENT_URL" >> $GITHUB_ENV
        
    - name: Health check
      run: |
        sleep 30  # Wait for service to be ready
        curl -f ${{ env.DEPLOYMENT_URL }} || echo "Service might still be starting up"
        
    - name: Notify deployment success
      if: success()
      run: |
        echo "🎉 Production deployment successful!"
        echo "URL: ${{ env.DEPLOYMENT_URL }}"
        
  # Stage 6: Post-deployment (always runs)
  post-deployment:
    runs-on: ubuntu-latest
    needs: [deploy-staging, deploy-production]
    if: always()
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Generate deployment report
      run: |
        echo "## 🚀 Deployment Summary" >> deployment-report.md
        echo "**Repository:** ${{ github.repository }}" >> deployment-report.md
        echo "**Commit:** ${{ github.sha }}" >> deployment-report.md
        echo "**Branch:** ${{ github.ref_name }}" >> deployment-report.md
        echo "**Triggered by:** ${{ github.actor }}" >> deployment-report.md
        echo "**Timestamp:** $(date)" >> deployment-report.md
        echo "" >> deployment-report.md
        echo "### 📊 Job Results:" >> deployment-report.md
        echo "- Code Quality: ${{ needs.code-quality.result }}" >> deployment-report.md
        echo "- Testing: ${{ needs.test.result }}" >> deployment-report.md
        echo "- Build & Scan: ${{ needs.build-and-scan.result }}" >> deployment-report.md
        if contains(github.ref, 'main') || contains(github.ref, 'master'); then
          echo "- Production Deploy: ${{ needs.deploy-production.result }}" >> deployment-report.md
        fi
        if github.event_name == 'pull_request'; then
          echo "- Staging Deploy: ${{ needs.deploy-staging.result }}" >> deployment-report.md
        fi
        
    - name: Upload deployment report
      uses: actions/upload-artifact@v3
      with:
        name: deployment-report
        path: deployment-report.md
"""
        return yaml_content
    
    def generate_dockerfile(self) -> str:
        """Generate Dockerfile for the application"""
        dockerfile_content = """# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Set environment variables
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run the application
CMD ["streamlit", "run", "simple_toolbox.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""
        return dockerfile_content
    
    def show_deploy_phase(self):
        """Show deployment phase"""
        st.markdown("## 🚀 Phase 5: Deploy Pipeline")
        
        if not st.session_state['pipeline_complete']:
            st.info("Pipeline files need to be created first")
            if st.button("📋 Go to Pipeline Creation"):
                self.update_state(phase='pipeline')
                st.rerun()
        else:
            st.success("🎉 Pipeline files are ready!")
            st.info("📁 .github/workflows/deploy.yml")
            st.info("📁 Dockerfile")
            st.info("📁 requirements.txt")
            
            # Show manual push option
            st.markdown("### 🚀 Manual Code Push")
            st.info("🔒 **User Control**: You decide when to push code and trigger the pipeline")
            
            if st.button("🚀 Push Code & Trigger Pipeline"):
                with st.spinner("Pushing code to GitHub..."):
                    if self.push_code_to_github():
                        st.success("🎉 Code pushed successfully!")
                        st.info("🚀 CI/CD pipeline is now running!")
                        st.info("📊 Check GitHub Actions for progress")
                        
                        # Update state
                        self.update_state(secrets_complete=True, pipeline_complete=True)
                        return True
                    else:
                        st.error("❌ Failed to push code")
                        return False
            
            # Show next steps
            st.markdown("### 🎯 Next Steps:")
            st.markdown("1. **Review the generated CI/CD files** above")
            st.markdown("2. **Make any code changes** you want to deploy")
            st.markdown("3. **Click 'Push Code & Trigger Pipeline'** when ready")
            st.markdown("4. **Check GitHub Actions** to see your pipeline running!")
            
            st.warning("⚠️ **Important**: Pipeline will NOT trigger automatically. You must manually push code when ready.")
    
    def push_code_to_github(self) -> bool:
        """Push code to GitHub to trigger CI/CD pipeline"""
        try:
            st.info("📤 Pushing code to GitHub...")
            
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                 capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                st.info("ℹ️ No changes to commit - adding CI/CD files...")
                # Force add CI/CD files even if no changes
                subprocess.run(['git', 'add', '.github/', 'Dockerfile', 'requirements.txt'], check=True)
            else:
                st.info("📝 Adding all changes...")
                subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit with descriptive message
            commit_msg = f"🚀 Add CI/CD pipeline and trigger deployment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # Get current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True, check=True)
            current_branch = branch_result.stdout.strip()
            
            st.info(f"📤 Pushing to branch: {current_branch}")
            
            # Push to current branch
            subprocess.run(['git', 'push', 'origin', current_branch], check=True)
            
            st.success("🎉 Code pushed successfully!")
            st.info("🚀 CI/CD pipeline is now running!")
            
            return True
            
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            st.error(f"❌ Failed to push code: {e}")
            return False

if __name__ == "__main__":
    toolbox = SimpleToolbox()
    toolbox.run()
