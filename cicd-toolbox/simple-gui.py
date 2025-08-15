import streamlit as st
import subprocess
import json
import os
import time
from pathlib import Path

# Page config
st.set_page_config(
    page_title="🚀 CI/CD Deployment Toolbox",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for better look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-box {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: #f8f9fa;
    }
    .step-success {
        border-color: #28a745;
        background: #d4edda;
    }
    .step-running {
        border-color: #ffc107;
        background: #fff3cd;
    }
    .step-error {
        border-color: #dc3545;
        background: #f8d7da;
    }
    .step-pending {
        border-color: #6c757d;
        background: #f8f9fa;
    }
    .action-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

class SimpleCICDToolbox:
    def __init__(self):
        self.project_id = None
        self.project_analysis = None
        self.gcp_setup_done = False
        self.secrets_pushed = False
        self.gcloud_account = None
        self.gh_username = None
        
    def check_gcloud_auth(self):
        """Check if gcloud is authenticated"""
        try:
            result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE', '--format=value(account)'], 
                                  capture_output=True, text=True, check=True)
            account = result.stdout.strip()
            if account:
                self.gcloud_account = account
                return True
            return False
        except:
            self.gcloud_account = None
            return False
    
    def check_gh_auth(self):
        """Check if GitHub CLI is authenticated"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                  capture_output=True, text=True, check=True)
            if "✓ Logged in to github.com" in result.stdout:
                # Extract username from output
                for line in result.stdout.split('\n'):
                    if 'Logged in to github.com as' in line:
                        self.gh_username = line.split('as')[-1].strip()
                        break
                return True
            return False
        except:
            self.gh_username = None
            return False
    
    def authenticate_gcloud(self, project_id):
        """Set GCP project ID"""
        try:
            subprocess.run(['gcloud', 'config', 'set', 'project', project_id], 
                          check=True, capture_output=True, text=True)
            self.project_id = project_id
            return True, "Project configured successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to set project: {e.stderr}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def authenticate_github(self, token):
        """Authenticate with GitHub using token"""
        try:
            # Set GitHub token
            subprocess.run(['gh', 'auth', 'login', '--with-token'], 
                          input=token, text=True, capture_output=True, check=True)
            
            # Verify authentication
            result = subprocess.run(['gh', 'auth', 'status'], 
                                  capture_output=True, text=True, check=True)
            
            if "✓ Logged in to github.com" in result.stdout:
                # Extract username
                for line in result.stdout.split('\n'):
                    if 'Logged in to github.com as' in line:
                        self.gh_username = line.split('as')[-1].strip()
                        break
                return True, "Authentication successful"
            else:
                return False, "Authentication failed"
                
        except subprocess.CalledProcessError as e:
            return False, f"Error: {e.stderr}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def get_current_project(self):
        """Get current GCP project"""
        try:
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return None
    
    def analyze_project(self):
        """Simple project analysis for runtime secrets only"""
        st.info("🔍 Analyzing project for runtime secrets...")
        
        # Simple detection based on common patterns
        runtime_secrets = set()
        
        # Check for OpenAI
        if Path("../requirements.txt").exists():
            with open("../requirements.txt", "r") as f:
                content = f.read()
                if "openai" in content.lower():
                    runtime_secrets.add("OPENAI_API_KEY")
        
        # Check for Pinecone
        if Path("../requirements.txt").exists():
            with open("../requirements.txt", "r") as f:
                content = f.read()
                if "pinecone" in content.lower():
                    runtime_secrets.add("PINECONE_API_KEY")
                    runtime_secrets.add("PINECONE_ENVIRONMENT")
        
        # Check main Python files
        python_files = list(Path("..").glob("*.py"))
        for py_file in python_files[:5]:  # Check first 5 Python files
            try:
                with open(py_file, "r") as f:
                    content = f.read()
                    if "os.getenv" in content or "os.environ" in content:
                        # Look for common secret patterns
                        if "api_key" in content.lower():
                            runtime_secrets.add("API_KEY")
                        if "secret" in content.lower():
                            runtime_secrets.add("SECRET_KEY")
            except:
                continue
        
        self.project_analysis = {
            "project_type": "Python",
            "framework": "Streamlit",
            "runtime_secrets": list(runtime_secrets),
            "deployment_target": "GCP Cloud Run"
        }
        
        return self.project_analysis
    
    def setup_gcp_infrastructure(self):
        """Setup GCP infrastructure for Cloud Run"""
        st.info("⚙️ Setting up GCP infrastructure...")
        
        try:
            # Enable required APIs
            apis = [
                "cloudrun.googleapis.com",
                "iam.googleapis.com",
                "artifactregistry.googleapis.com",
                "cloudbuild.googleapis.com"
            ]
            
            for api in apis:
                st.write(f"Enabling {api}...")
                try:
                    subprocess.run(['gcloud', 'services', 'enable', api], check=True, capture_output=True, text=True)
                    st.write(f"✅ {api} enabled")
                except subprocess.CalledProcessError as e:
                    if "ALREADY_ENABLED" in e.stderr:
                        st.write(f"✅ {api} already enabled")
                    else:
                        st.warning(f"⚠️ {api} enable failed: {e.stderr}")
            
            # Create service account (handle if already exists)
            st.write("Creating service account...")
            try:
                subprocess.run([
                    'gcloud', 'iam', 'service-accounts', 'create', 'cicd-service-account',
                    '--display-name=CI/CD Service Account',
                    '--description=Service account for CI/CD pipeline'
                ], check=True, capture_output=True, text=True)
                st.write("✅ Service account created")
            except subprocess.CalledProcessError as e:
                if "ALREADY_EXISTS" in e.stderr:
                    st.write("✅ Service account already exists")
                else:
                    st.error(f"❌ Service account creation failed: {e.stderr}")
                    return False
            
            # Assign roles
            roles = [
                "roles/run.admin",
                "roles/iam.serviceAccountUser",
                "roles/storage.admin",
                "roles/artifactregistry.admin"
            ]
            
            service_account_email = f"cicd-service-account@{self.project_id}.iam.gserviceaccount.com"
            
            for role in roles:
                st.write(f"Assigning {role}...")
                try:
                    subprocess.run([
                        'gcloud', 'projects', 'add-iam-policy-binding', self.project_id,
                        f'--member=serviceAccount:{service_account_email}',
                        f'--role={role}'
                    ], check=True, capture_output=True, text=True)
                    st.write(f"✅ {role} assigned")
                except subprocess.CalledProcessError as e:
                    if "ALREADY_EXISTS" in e.stderr:
                        st.write(f"✅ {role} already assigned")
                    else:
                        st.warning(f"⚠️ {role} assignment failed: {e.stderr}")
            
            # Setup Workload Identity Federation
            st.write("Setting up Workload Identity Federation...")
            
            # Create WIF pool (handle if already exists)
            try:
                subprocess.run([
                    'gcloud', 'iam', 'workload-identity-pools', 'create', 'github-actions-pool',
                    '--location=global',
                    '--display-name=GitHub Actions Pool'
                ], check=True, capture_output=True, text=True)
                st.write("✅ WIF pool created")
            except subprocess.CalledProcessError as e:
                if "ALREADY_EXISTS" in e.stderr:
                    st.write("✅ WIF pool already exists")
                else:
                    st.error(f"❌ WIF pool creation failed: {e.stderr}")
                    return False
            
            # Create WIF provider (handle if already exists)
            try:
                subprocess.run([
                    'gcloud', 'iam', 'workload-identity-pools', 'providers', 'create-oidc', 'github-actions-provider',
                    '--workload-identity-pool=github-actions-pool',
                    '--location=global',
                    '--issuer-uri=https://token.actions.githubusercontent.com',
                    '--attribute-mapping=google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.aud=assertion.aud'
                ], check=True, capture_output=True, text=True)
                st.write("✅ WIF provider created")
            except subprocess.CalledProcessError as e:
                if "ALREADY_EXISTS" in e.stderr:
                    st.write("✅ WIF provider already exists")
                else:
                    st.error(f"❌ WIF provider creation failed: {e.stderr}")
                    return False
            
            # Get WIF pool resource name
            try:
                result = subprocess.run([
                    'gcloud', 'iam', 'workload-identity-pools', 'describe', 'github-actions-pool',
                    '--location=global', '--format=value(name)'
                ], check=True, capture_output=True, text=True)
                pool_name = result.stdout.strip()
                
                # Bind IAM policy
                try:
                    subprocess.run([
                        'gcloud', 'iam', 'service-accounts', 'add-iam-policy-binding', service_account_email,
                        f'--role=roles/iam.workloadIdentityUser',
                        f'--member=principalSet://iam.googleapis.com/{pool_name}/attribute.repository/neurofinance-468916/embeddingforpinecon'
                    ], check=True, capture_output=True, text=True)
                    st.write("✅ IAM policy bound")
                except subprocess.CalledProcessError as e:
                    if "ALREADY_EXISTS" in e.stderr:
                        st.write("✅ IAM policy already bound")
                    else:
                        st.warning(f"⚠️ IAM policy binding failed: {e.stderr}")
                
            except subprocess.CalledProcessError as e:
                st.error(f"❌ Failed to get pool name: {e.stderr}")
                return False
            
            self.gcp_setup_done = True
            return True
            
        except Exception as e:
            st.error(f"❌ GCP setup failed: {str(e)}")
            return False
    
    def push_secrets_to_github(self):
        """Push secrets to GitHub repository"""
        st.info("🔑 Pushing secrets to GitHub...")
        
        try:
            # Get WIF pool resource name
            result = subprocess.run([
                'gcloud', 'iam', 'workload-identity-pools', 'describe', 'github-actions-pool',
                '--location=global', '--format=value(name)'
            ], check=True, capture_output=True, text=True)
            pool_name = result.stdout.strip()
            
            # Get service account email
            service_account_email = f"cicd-service-account@{self.project_id}.iam.gserviceaccount.com"
            
            # Prepare secrets
            secrets = {
                "GCP_PROJECT_ID": self.project_id,
                "GCP_SERVICE_ACCOUNT_EMAIL": service_account_email,
                "GCP_WORKLOAD_IDENTITY_PROVIDER": pool_name,
                "GCP_WORKLOAD_IDENTITY_POOL": pool_name
            }
            
            # Add runtime secrets from project analysis
            if self.project_analysis and "runtime_secrets" in self.project_analysis:
                for secret in self.project_analysis["runtime_secrets"]:
                    secrets[secret] = f"YOUR_{secret}_HERE"
            
            # Display secrets that need to be added
            st.success("✅ **Secrets ready to be added to GitHub!**")
            st.info("**Add these secrets to your GitHub repository:**")
            
            for key, value in secrets.items():
                st.code(f"{key}={value}", language="bash")
            
            # Instructions
            st.markdown("""
            **To add these secrets:**
            1. Go to your GitHub repository
            2. Click **Settings** → **Secrets and variables** → **Actions**
            3. Click **New repository secret**
            4. Add each secret above
            """)
            
            self.secrets_pushed = True
            return True
            
        except Exception as e:
            st.error(f"❌ Failed to prepare secrets: {str(e)}")
            return False
    
    def trigger_pipeline(self):
        """Trigger the CI/CD pipeline"""
        st.info("🚀 Triggering CI/CD pipeline...")
        
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                st.error("❌ Not in a git repository")
                st.info("Please ensure you're in the root of your project directory")
                return False
            
            # Check if we have uncommitted changes
            result = subprocess.run(['git', 'diff', '--quiet'])
            if result.returncode != 0:
                st.warning("⚠️ You have uncommitted changes")
                st.info("Consider committing your changes before triggering the pipeline")
                
                if st.button("📝 Commit and Push Changes", key="commit_push"):
                    # Add all changes
                    subprocess.run(['git', 'add', '.'])
                    
                    # Commit
                    commit_message = st.text_input("Enter commit message:", value="Update deployment configuration", key="commit_msg")
                    if st.button("✅ Commit", key="commit_btn"):
                        subprocess.run(['git', 'commit', '-m', commit_message])
                        
                        # Push to trigger pipeline
                        if st.button("🚀 Push to Trigger Pipeline", key="push_btn"):
                            subprocess.run(['git', 'push', 'origin', 'main'])
                            st.success("✅ Pipeline triggered! Check GitHub Actions for progress.")
                            return True
            else:
                # No changes, just push to trigger
                if st.button("🚀 Push to Trigger Pipeline", key="push_no_changes"):
                    subprocess.run(['git', 'push', 'origin', 'main'])
                    st.success("✅ Pipeline triggered! Check GitHub Actions for progress.")
                    return True
            
            return False
            
        except Exception as e:
            st.error(f"❌ Failed to trigger pipeline: {str(e)}")
            return False

def main():
    st.markdown('<div class="main-header"><h1>🚀 CI/CD Deployment Toolbox</h1><p>Automated deployment to GCP Cloud Run</p></div>', unsafe_allow_html=True)
    
    # Initialize toolbox
    if 'toolbox' not in st.session_state:
        st.session_state.toolbox = SimpleCICDToolbox()
    
    toolbox = st.session_state.toolbox
    
    # Check authentication status
    gcloud_auth = toolbox.check_gcloud_auth()
    gh_auth = toolbox.check_gh_auth()
    
    # Progress tracking
    steps = {
        "gcp_setup": toolbox.gcp_setup_done,
        "secrets_pushed": toolbox.secrets_pushed,
        "pipeline_triggered": False  # Will be set when triggered
    }
    
    # Progress bar
    progress = sum(steps.values()) / len(steps)
    st.progress(progress)
    st.caption(f"Progress: {sum(steps.values())}/{len(steps)} steps completed")
    
    # Authentication Status (Read-only)
    st.markdown('<div class="step-box"><h3>🔐 Authentication Status</h3></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌐 Google Cloud (gcloud)")
        if gcloud_auth:
            st.success("✅ **Authenticated**")
            st.info(f"**Account:** {toolbox.gcloud_account}")
            st.info(f"**Project:** {toolbox.get_current_project() or 'Not set'}")
        else:
            st.error("❌ **Not Authenticated**")
            st.warning("Please run the authentication script first:")
            st.code("./launch-cicd-toolbox.sh", language="bash")
    
    with col2:
        st.markdown("#### 🐙 GitHub CLI (gh)")
        if gh_auth:
            st.success("✅ **Authenticated**")
            st.info(f"**Username:** {toolbox.gh_username}")
        else:
            st.error("❌ **Not Authenticated**")
            st.warning("Please run the authentication script first:")
            st.code("./launch-cicd-toolbox.sh", language="bash")
    
    # Only show next steps if authentication is complete
    if not (gcloud_auth and gh_auth):
        st.warning("⚠️ **Authentication required**")
        st.info("Please run the authentication script from your terminal:")
        st.code("./launch-cicd-toolbox.sh", language="bash")
        st.info("This will handle GCP and GitHub authentication, then launch this GUI.")
        return
    
    # Step 1: GCP Infrastructure Setup
    st.markdown('<div class="step-box"><h3>🏗️ Step 1: GCP Infrastructure Setup</h3></div>', unsafe_allow_html=True)
    
    if not toolbox.project_id:
        toolbox.project_id = st.text_input("Enter your GCP Project ID:", placeholder="your-project-id")
        if toolbox.project_id:
            st.success(f"✅ **Project ID:** {toolbox.project_id}")
    
    if toolbox.project_id and not toolbox.gcp_setup_done:
        if st.button("🔍 Analyze Project", type="primary", key="analyze_btn"):
            with st.spinner("Analyzing project..."):
                toolbox.project_analysis = toolbox.analyze_project()
                st.success("✅ Project analysis complete!")
                st.json(toolbox.project_analysis)
        
        if toolbox.project_analysis and st.button("⚙️ Setup GCP Infrastructure", type="primary", key="setup_gcp"):
            with st.spinner("Setting up GCP infrastructure..."):
                success = toolbox.setup_gcp_infrastructure()
                if success:
                    st.success("✅ GCP infrastructure setup complete!")
                    st.rerun()
    
    elif toolbox.gcp_setup_done:
        st.success("✅ **GCP Infrastructure: Complete**")
    
    # Step 2: Push Secrets to GitHub
    if toolbox.gcp_setup_done:
        st.markdown('<div class="step-box"><h3>🔑 Step 2: GitHub Secrets</h3></div>', unsafe_allow_html=True)
        
        if not toolbox.secrets_pushed:
            if st.button("🔑 Prepare GitHub Secrets", type="primary", key="prepare_secrets"):
                toolbox.push_secrets_to_github()
        else:
            st.success("✅ **GitHub Secrets: Ready**")
            st.info("Secrets have been prepared. Add them to your GitHub repository.")
    
    # Step 3: Trigger Pipeline
    if toolbox.secrets_pushed:
        st.markdown('<div class="step-box"><h3>🚀 Step 3: Trigger Pipeline</h3></div>', unsafe_allow_html=True)
        
        if st.button("🚀 Trigger CI/CD Pipeline", type="primary", key="trigger_pipeline"):
            with st.spinner("Triggering pipeline..."):
                success = toolbox.trigger_pipeline()
                if success:
                    st.success("✅ **Pipeline triggered successfully!**")
                    st.info("Check your GitHub Actions tab for deployment progress.")
                else:
                    st.warning("⚠️ Pipeline trigger failed. Check the instructions above.")
    
    # Final success message
    if all(steps.values()):
        st.markdown('<div class="step-box step-success"><h3>🎉 Deployment Complete!</h3></div>', unsafe_allow_html=True)
        st.success("**Your application is being deployed to GCP Cloud Run!**")
        st.info("Check GitHub Actions for deployment status and logs.")

if __name__ == "__main__":
    main()
