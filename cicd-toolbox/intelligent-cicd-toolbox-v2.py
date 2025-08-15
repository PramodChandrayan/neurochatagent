import streamlit as st
import subprocess
import json
import os
import time
import threading
from pathlib import Path
from datetime import datetime
import re

# Page config
st.set_page_config(
    page_title="🚀 Intelligent CI/CD Toolbox v2.0",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS for better UX
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .step-box {
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        background: #ffffff;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
    }
    .step-success {
        border-color: #28a745;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }
    .step-running {
        border-color: #ffc107;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    }
    .step-error {
        border-color: #dc3545;
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    }
    .pipeline-status {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border-left: 4px solid #007bff;
    }
    .pipeline-metrics {
        background: white;
        border-radius: 8px;
        padding: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border: 1px solid #17a2b8;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 1px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class IntelligentCICDToolboxV2:
    def __init__(self):
        self.project_id = None
        self.gcp_setup_done = False
        self.secrets_configured = False
        self.pipeline_status = "idle"
        self.pipeline_details = {
            "last_run": None,
            "commit_sha": None,
            "branch": None,
            "status": "idle",
            "logs": [],
            "duration": None
        }
        self.analysis_results = {}
        self.setup_steps = []
        
    def smart_authentication_check(self):
        """Intelligently check authentication with detailed diagnostics"""
        auth_status = {"gcp": False, "github": False, "details": {}, "issues": [], "tools": {}}
        
        # Check GCP CLI
        try:
            gcp_result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE'], 
                                      capture_output=True, text=True, check=True)
            if gcp_result.stdout.strip():
                auth_status["gcp"] = True
                auth_status["details"]["gcp_account"] = gcp_result.stdout.strip().split('\n')[0]
                
                # Get project
                project_result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                             capture_output=True, text=True, check=True)
                auth_status["details"]["gcp_project"] = project_result.stdout.strip()
                self.project_id = auth_status["details"]["gcp_project"]
            else:
                auth_status["issues"].append("❌ No active GCP authentication found")
        except subprocess.CalledProcessError:
            auth_status["issues"].append("❌ GCP CLI not accessible - please install Google Cloud SDK")
        except FileNotFoundError:
            auth_status["issues"].append("❌ GCP CLI not found - please install Google Cloud SDK")
            
        # Check GitHub CLI
        try:
            gh_result = subprocess.run(['gh', 'auth', 'status'], 
                                     capture_output=True, text=True, check=True)
            if "✓ Logged in to github.com" in gh_result.stdout:
                auth_status["github"] = True
                for line in gh_result.stdout.split('\n'):
                    if 'Logged in to github.com as' in line:
                        auth_status["details"]["github_user"] = line.split('as')[-1].strip()
                        break
            else:
                auth_status["issues"].append("❌ GitHub CLI not authenticated")
        except subprocess.CalledProcessError:
            auth_status["issues"].append("❌ GitHub CLI authentication failed")
        except FileNotFoundError:
            auth_status["issues"].append("❌ GitHub CLI not found - please install GitHub CLI")
            
        # Check required tools
        tools_to_check = {
            'git': 'Git version control',
            'docker': 'Docker containerization',
            'python': 'Python runtime'
        }
        
        for tool, description in tools_to_check.items():
            try:
                result = subprocess.run([tool, '--version'], capture_output=True, text=True, check=True)
                auth_status["tools"][tool] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                auth_status["tools"][tool] = False
                auth_status["issues"].append(f"❌ {description} not found")
            
        return auth_status
    
    def auto_authenticate_gcp(self):
        """Auto-authenticate GCP with user guidance"""
        try:
            st.info("🔐 Starting GCP authentication...")
            st.info("📋 Please follow these steps:")
            st.markdown("""
            1. **A new browser window will open**
            2. **Sign in with your Google account**
            3. **Grant necessary permissions**
            4. **Return here when complete**
            """)
            
            process = subprocess.Popen(['gcloud', 'auth', 'login'], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            st.success("✅ GCP authentication started!")
            st.info("🔄 Please complete the authentication in your browser and return here")
            return True
        except Exception as e:
            st.error(f"❌ GCP auth error: {str(e)}")
            st.info("💡 Manual authentication required:")
            st.code("gcloud auth login", language="bash")
            return False
    
    def auto_authenticate_github(self):
        """Auto-authenticate GitHub with user guidance"""
        try:
            st.info("🔐 Starting GitHub authentication...")
            st.info("📋 Please follow these steps:")
            st.markdown("""
            1. **A new browser window will open**
            2. **Sign in with your GitHub account**
            3. **Grant necessary permissions**
            4. **Return here when complete**
            """)
            
            process = subprocess.Popen(['gh', 'auth', 'login'], 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            st.success("✅ GitHub authentication started!")
            st.info("🔄 Please complete the authentication in your browser and return here")
            return True
        except Exception as e:
            st.error(f"❌ GitHub auth error: {str(e)}")
            st.info("💡 Manual authentication required:")
            st.code("gh auth login", language="bash")
            return False
    
    def smart_project_analysis(self):
        """Intelligently analyze GCP project and detect existing resources"""
        if not self.project_id:
            return {"error": "No project ID set"}
        
        analysis = {
            "project_info": {},
            "existing_resources": {},
            "missing_resources": {},
            "recommendations": [],
            "permissions": {}
        }
        
        try:
            # Get project details
            project_result = subprocess.run(['gcloud', 'projects', 'describe', self.project_id], 
                                         capture_output=True, text=True, check=True)
            analysis["project_info"]["exists"] = True
            
            # Check enabled APIs
            apis_result = subprocess.run(['gcloud', 'services', 'list', '--enabled'], 
                                       capture_output=True, text=True, check=True)
            
            required_apis = ["cloudrun.googleapis.com", "iam.googleapis.com", "artifactregistry.googleapis.com"]
            enabled_apis = []
            
            for line in apis_result.stdout.split('\n'):
                if 'googleapis.com' in line:
                    api_name = line.split()[0]
                    enabled_apis.append(api_name)
            
            analysis["existing_resources"]["enabled_apis"] = enabled_apis
            
            # Check which required APIs are missing
            missing_apis = [api for api in required_apis if api not in enabled_apis]
            if missing_apis:
                analysis["missing_resources"]["apis"] = missing_apis
                analysis["recommendations"].append(f"Enable missing APIs: {', '.join(missing_apis)}")
            else:
                analysis["recommendations"].append("✅ All required APIs are already enabled")
            
            # Check service accounts
            sa_result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'list'], 
                                     capture_output=True, text=True, check=True)
            
            if 'cicd-service-account@' in sa_result.stdout:
                analysis["existing_resources"]["service_account"] = "cicd-service-account"
                analysis["recommendations"].append("✅ CI/CD service account already exists")
            else:
                analysis["missing_resources"]["service_account"] = "cicd-service-account"
                analysis["recommendations"].append("Create CI/CD service account")
            
            # Check Workload Identity Federation
            wif_result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'list'], 
                                      capture_output=True, text=True, check=True)
            
            if 'my-pool' in wif_result.stdout:
                analysis["existing_resources"]["wif_pool"] = "my-pool"
                analysis["recommendations"].append("✅ WIF pool already exists")
            else:
                analysis["missing_resources"]["wif_pool"] = "my-pool"
                analysis["recommendations"].append("Create Workload Identity Federation pool")
            
            # Check Artifact Registry
            ar_result = subprocess.run(['gcloud', 'artifacts', 'repositories', 'list'], 
                                     capture_output=True, text=True, check=True)
            
            if 'neurogent-repo' in ar_result.stdout:
                analysis["existing_resources"]["artifact_registry"] = "neurogent-repo"
                analysis["recommendations"].append("✅ Artifact Registry repository exists")
            else:
                analysis["missing_resources"]["artifact_registry"] = "neurogent-repo"
                analysis["recommendations"].append("Create Artifact Registry repository")
            
            # Check user permissions
            try:
                test_result = subprocess.run(['gcloud', 'iam', 'test-iam-permissions', self.project_id, 
                                           'iam.serviceAccounts.create'], 
                                          capture_output=True, text=True, check=True)
                analysis["permissions"]["can_create_service_accounts"] = True
            except subprocess.CalledProcessError:
                analysis["permissions"]["can_create_service_accounts"] = False
                analysis["recommendations"].append("⚠️ Limited permissions - may need admin assistance")
                
        except Exception as e:
            analysis["error"] = str(e)
            
        self.analysis_results = analysis
        return analysis
    
    def intelligent_gcp_setup(self):
        """Intelligent GCP setup that handles existing resources gracefully"""
        st.info("🏗️ Starting Intelligent GCP Setup")
        
        if not self.project_id:
            st.error("❌ No project ID set! Cannot proceed with GCP setup.")
            return False
        
        # First, analyze what exists
        analysis = self.smart_project_analysis()
        if "error" in analysis:
            st.error(f"❌ Project analysis failed: {analysis['error']}")
            return False
        
        st.info("🔍 Analysis complete! Here's what we found:")
        
        # Display analysis results
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Existing Resources")
            for resource_type, resource_name in analysis["existing_resources"].items():
                st.success(f"**{resource_type.replace('_', ' ').title()}**: {resource_name}")
        
        with col2:
            st.markdown("#### ❌ Missing Resources")
            for resource_type, resource_name in analysis["missing_resources"].items():
                st.warning(f"**{resource_type.replace('_', ' ').title()}**: {resource_name}")
        
        # Show recommendations
        st.markdown("#### 💡 Recommendations")
        for rec in analysis["recommendations"]:
            st.info(rec)
        
        # Now proceed with setup based on what's missing
        success = True
        
        # Handle APIs (skip if already enabled)
        if "apis" in analysis["missing_resources"]:
            st.info("🚀 Enabling required APIs...")
            for api in analysis["missing_resources"]["apis"]:
                try:
                    subprocess.run(['gcloud', 'services', 'enable', api], 
                                  check=True, capture_output=True, text=True)
                    st.success(f"✅ {api} enabled")
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Failed to enable {api}: {e}")
                    success = False
        else:
            st.success("✅ All required APIs are already enabled")
        
        # Handle service account (skip if exists)
        if "service_account" in analysis["missing_resources"]:
            st.info("👤 Creating CI/CD service account...")
            try:
                subprocess.run([
                    'gcloud', 'iam', 'service-accounts', 'create', 'cicd-service-account',
                    '--display-name=CI/CD Service Account'
                ], check=True, capture_output=True, text=True)
                st.success("✅ CI/CD service account created")
            except subprocess.CalledProcessError as e:
                if "ALREADY_EXISTS" in e.stderr:
                    st.success("✅ CI/CD service account already exists")
                else:
                    st.error(f"❌ Service account creation failed: {e}")
                    success = False
        else:
            st.success("✅ CI/CD service account already exists")
        
        # Handle IAM roles (always check and set)
        st.info("🔐 Setting up IAM roles...")
        try:
            service_account = f"cicd-service-account@{self.project_id}.iam.gserviceaccount.com"
            roles = ["roles/run.admin", "roles/iam.serviceAccountUser", "roles/storage.admin", "roles/artifactregistry.writer"]
            
            for role in roles:
                try:
                    subprocess.run([
                        'gcloud', 'projects', 'add-iam-policy-binding', self.project_id,
                        f'--member=serviceAccount:{service_account}',
                        f'--role={role}'
                    ], check=True, capture_output=True, text=True)
                    st.success(f"✅ {role} assigned")
                except subprocess.CalledProcessError as e:
                    if "ALREADY_EXISTS" in e.stderr:
                        st.success(f"✅ {role} already assigned")
                    else:
                        st.warning(f"⚠️ {role} assignment failed: {e}")
            
        except Exception as e:
            st.error(f"❌ IAM setup failed: {e}")
            success = False
        
        # Handle Workload Identity Federation (skip if exists)
        if "wif_pool" in analysis["missing_resources"]:
            st.info("🔗 Setting up Workload Identity Federation...")
            try:
                # Create pool
                subprocess.run([
                    'gcloud', 'iam', 'workload-identity-pools', 'create', 'my-pool',
                    '--location=global', '--display-name=GitHub Actions Pool'
                ], check=True, capture_output=True, text=True)
                st.success("✅ WIF pool created")
            except subprocess.CalledProcessError as e:
                if "ALREADY_EXISTS" in e.stderr:
                    st.success("✅ WIF pool already exists")
                else:
                    st.error(f"❌ WIF pool creation failed: {e}")
                    success = False
            
            try:
                # Create provider
                subprocess.run([
                    'gcloud', 'iam', 'workload-identity-pools', 'providers', 'create-oidc', 'github-actions-provider',
                    '--workload-identity-pool=my-pool', '--location=global',
                    '--issuer-uri=https://token.actions.githubusercontent.com',
                    '--attribute-mapping=google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository',
                    '--attribute-condition=assertion.repository==\'PramodChandrayan/neurochatagent\''
                ], check=True, capture_output=True, text=True)
                st.success("✅ WIF provider created")
            except subprocess.CalledProcessError as e:
                if "ALREADY_EXISTS" in e.stderr:
                    st.success("✅ WIF provider already exists")
                else:
                    st.error(f"❌ WIF provider creation failed: {e}")
                    success = False
        else:
            st.success("✅ Workload Identity Federation already exists")
        
        # Handle Artifact Registry (skip if exists)
        if "artifact_registry" in analysis["missing_resources"]:
            st.info("🐳 Creating Artifact Registry repository...")
            try:
                subprocess.run([
                    'gcloud', 'artifacts', 'repositories', 'create', 'neurogent-repo',
                    '--repository-format=docker', '--location=us-central1',
                    '--description=NeuroGent Finance Assistant Docker Repository'
                ], check=True, capture_output=True, text=True)
                st.success("✅ Artifact Registry repository created")
            except subprocess.CalledProcessError as e:
                if "ALREADY_EXISTS" in e.stderr:
                    st.success("✅ Artifact Registry repository already exists")
                else:
                    st.error(f"❌ Artifact Registry creation failed: {e}")
                    success = False
        else:
            st.success("✅ Artifact Registry repository already exists")
        
        if success:
            self.gcp_setup_done = True
            st.success("🎉 GCP Setup Complete!")
            return True
        else:
            st.error("❌ GCP Setup had some issues. Check the logs above.")
            return False
    
    def intelligent_github_setup(self):
        """Intelligent GitHub setup that handles all required secrets"""
        st.info("🔑 Configuring GitHub Secrets")
        
        if not self.project_id:
            st.error("❌ No project ID set! Cannot proceed with GitHub setup.")
            return False
        
        # Get service account
        service_account = f"cicd-service-account@{self.project_id}.iam.gserviceaccount.com"
        
        # Define all required secrets with proper names
        required_secrets = {
            "GCP_PROJECT_ID": self.project_id,
            "WIF_PROVIDER": f"projects/71586032565/locations/global/workloadIdentityPools/my-pool/providers/github-actions-provider",
            "GCP_SERVICE_ACCOUNT": service_account,
            "REGION": "us-central1",
            "SERVICE_NAME": "neurogent-finance-assistant"
        }
        
        st.info("🚀 Setting up GitHub secrets...")
        
        # Push each secret using GitHub CLI
        success_count = 0
        for key, value in required_secrets.items():
            with st.spinner(f"Setting {key}..."):
                try:
                    result = subprocess.run([
                        'gh', 'secret', 'set', key, '--body', value
                    ], capture_output=True, text=True, check=True)
                    st.success(f"✅ {key} set successfully")
                    success_count += 1
                except subprocess.CalledProcessError as e:
                    if "already exists" in e.stderr.lower():
                        st.success(f"✅ {key} already exists")
                        success_count += 1
                    else:
                        st.warning(f"⚠️ {key} setting failed: {e.stderr}")
        
        if success_count == len(required_secrets):
            st.success("🎉 All GitHub secrets configured!")
            self.secrets_configured = True
            return True
        else:
            st.warning(f"⚠️ {len(required_secrets) - success_count} secrets failed to set")
            return False
    
    def get_live_pipeline_status(self):
        """Get live pipeline status from GitHub Actions"""
        try:
            # Get latest workflow run
            result = subprocess.run([
                'gh', 'run', 'list', '--limit', '1', '--json', 'status,conclusion,startedAt,completedAt,headSha,headBranch'
            ], capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                import json
                runs = json.loads(result.stdout)
                if runs:
                    run = runs[0]
                    
                    # Update pipeline details
                    self.pipeline_details.update({
                        "status": run.get('status', 'unknown'),
                        "conclusion": run.get('conclusion', 'unknown'),
                        "last_run": run.get('startedAt', self.pipeline_details["last_run"]),
                        "commit_sha": run.get('headSha', '')[:8] if run.get('headSha') else None,
                        "branch": run.get('headBranch', 'main')
                    })
                    
                    # Calculate duration if completed
                    if run.get('startedAt') and run.get('completedAt'):
                        start_time = datetime.fromisoformat(run['startedAt'].replace('Z', '+00:00'))
                        end_time = datetime.fromisoformat(run['completedAt'].replace('Z', '+00:00'))
                        duration = end_time - start_time
                        self.pipeline_details["duration"] = str(duration).split('.')[0]
                    
                    # Add status to logs
                    status_msg = f"🔄 Workflow {run.get('status', 'unknown')}"
                    if run.get('conclusion'):
                        status_msg += f" - {run.get('conclusion', 'unknown')}"
                    
                    if status_msg not in self.pipeline_details["logs"]:
                        self.pipeline_details["logs"].append(status_msg)
                    
                    return run
                    
        except Exception as e:
            self.pipeline_details["logs"].append(f"⚠️ Status check failed: {str(e)}")
        
        return None
    
    def get_workflow_logs(self):
        """Get detailed workflow logs"""
        try:
            # Check if there are any workflow runs
            result = subprocess.run([
                'gh', 'run', 'list', '--limit', '1', '--json', 'number'
            ], capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                import json
                runs = json.loads(result.stdout)
                if runs:
                    run_number = runs[0]['number']
                    
                    # Get logs for this run
                    logs_result = subprocess.run([
                        'gh', 'run', 'view', str(run_number), '--log'
                    ], capture_output=True, text=True, check=True)
                    
                    return logs_result.stdout
                else:
                    return "No workflow runs found yet"
            else:
                return "No workflow runs found yet"
                
        except subprocess.CalledProcessError as e:
            if "no runs found" in e.stderr.lower() or "no workflows" in e.stderr.lower():
                return "No workflow runs found yet. This is normal for new repositories."
            else:
                return f"Could not fetch logs: {e.stderr}"
        except Exception as e:
            return f"Could not fetch logs: {str(e)}"
    
    def trigger_pipeline(self):
        """Trigger CI/CD pipeline with user configuration"""
        try:
            st.info("🚀 Triggering Pipeline...")
            
            # Check git status
            result = subprocess.run(['git', 'status'], capture_output=True, text=True)
            if result.returncode != 0:
                st.error("❌ Not in git repository")
                return False
            
            # Get current commit info
            commit_result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
            commit_sha = commit_result.stdout.strip()[:8]
            
            # Update pipeline details
            self.pipeline_details.update({
                "last_run": datetime.now().isoformat(),
                "commit_sha": commit_sha,
                "branch": "main",
                "status": "triggered",
                "logs": [f"🚀 Pipeline triggered at {datetime.now().strftime('%H:%M:%S')}"],
                "duration": None
            })
            
            # Push to trigger
            subprocess.run(['git', 'add', '.'])
            subprocess.run(['git', 'commit', '-m', '🤖 Auto-commit for CI/CD'])
            subprocess.run(['git', 'push', 'origin', 'main'])
            
            st.success("✅ Pipeline triggered!")
            self.pipeline_status = "running"
            self.pipeline_details["status"] = "running"
            self.pipeline_details["logs"].append(f"📤 Code pushed to GitHub at {datetime.now().strftime('%H:%M:%S')}")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Pipeline trigger failed: {str(e)}")
            self.pipeline_details["status"] = "failed"
            self.pipeline_details["logs"].append(f"❌ Pipeline trigger failed: {str(e)}")
            return False

def main():
    st.markdown('<div class="main-header"><h1>🚀 Intelligent CI/CD Toolbox v2.0</h1><p>Complete Automation with Smart Detection & Error Prevention</p></div>', unsafe_allow_html=True)
    
    # Initialize toolbox in session state
    if 'toolbox' not in st.session_state:
        st.session_state.toolbox = IntelligentCICDToolboxV2()
    
    toolbox = st.session_state.toolbox
    
    # Step 1: Smart Authentication Check
    st.markdown('<div class="step-box"><h3>🔐 Step 1: Smart Authentication & CLI Check</h3></div>', unsafe_allow_html=True)
    
    auth_status = toolbox.smart_authentication_check()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌐 Google Cloud")
        if auth_status["gcp"]:
            st.success("✅ **Authenticated**")
            st.info(f"**Project:** {auth_status['details'].get('gcp_project', 'Unknown')}")
        else:
            st.error("❌ **Not Authenticated**")
            if st.button("🔐 **Auto-Authenticate GCP**", key="auth_gcp"):
                toolbox.auto_authenticate_gcp()
                st.rerun()
    
    with col2:
        st.markdown("#### 🐙 GitHub")
        if auth_status["github"]:
            st.success("✅ **Authenticated**")
            st.info(f"**User:** {auth_status['details'].get('github_user', 'Unknown')}")
        else:
            st.error("❌ **Not Authenticated**")
            if st.button("🔐 **Auto-Authenticate GitHub**", key="auth_gh"):
                toolbox.auto_authenticate_github()
                st.rerun()
    
    # Show any authentication issues
    if auth_status["issues"]:
        st.markdown('<div class="warning-box"><h4>⚠️ Authentication Issues Found:</h4></div>', unsafe_allow_html=True)
        for issue in auth_status["issues"]:
            st.warning(issue)
    
    # Show tool status
    if auth_status["tools"]:
        st.markdown("#### 🛠️ Required Tools Status")
        tool_cols = st.columns(len(auth_status["tools"]))
        for i, (tool, status) in enumerate(auth_status["tools"].items()):
            with tool_cols[i]:
                if status:
                    st.success(f"✅ {tool}")
                else:
                    st.error(f"❌ {tool}")
    
    if not (auth_status["gcp"] and auth_status["github"]):
        st.warning("⚠️ Complete authentication first")
        return
    
    # Step 2: Smart Project Selection & Analysis
    st.markdown('<div class="step-box"><h3>🏗️ Step 2: Smart Project Analysis & Setup</h3></div>', unsafe_allow_html=True)
    
    # Project ID input with smart detection
    if not toolbox.project_id:
        # Try to detect current project
        try:
            current_project = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                          capture_output=True, text=True, check=True)
            detected_project = current_project.stdout.strip()
            if detected_project:
                toolbox.project_id = detected_project
                st.success(f"🔍 **Detected Project:** {detected_project}")
        except:
            pass
    
    if not toolbox.project_id:
        project_id = st.text_input("🔑 Enter your GCP Project ID:", 
                                  placeholder="your-project-id",
                                  key="project_id_input")
        
        if project_id:
            toolbox.project_id = project_id
            st.success(f"✅ Project ID set to: {project_id}")
    
    if toolbox.project_id:
        # Smart analysis button
        if st.button("🔍 **Analyze Project & Detect Resources**", type="primary", key="analyze"):
            with st.spinner("🔍 Analyzing project..."):
                analysis = toolbox.smart_project_analysis()
                st.session_state.analysis_complete = True
                st.rerun()
        
        # Show analysis results if available
        if hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete:
            if toolbox.analysis_results:
                st.markdown("#### 📊 Project Analysis Results")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**✅ Existing Resources:**")
                    for resource_type, resource_name in toolbox.analysis_results.get("existing_resources", {}).items():
                        st.success(f"• {resource_type.replace('_', ' ').title()}: {resource_name}")
                
                with col2:
                    st.markdown("**❌ Missing Resources:**")
                    for resource_type, resource_name in toolbox.analysis_results.get("missing_resources", {}).items():
                        st.warning(f"• {resource_type.replace('_', ' ').title()}: {resource_name}")
                
                # Show recommendations
                if toolbox.analysis_results.get("recommendations"):
                    st.markdown("#### 💡 Recommendations")
                    for rec in toolbox.analysis_results["recommendations"]:
                        st.info(rec)
                
                # Setup button
                if st.button("⚙️ **Start Intelligent GCP Setup**", type="primary", key="setup_gcp"):
                    with st.spinner("🚀 Starting GCP Setup..."):
                        success = toolbox.intelligent_gcp_setup()
                        if success:
                            st.success("✅ GCP Setup completed successfully!")
                            toolbox.gcp_setup_done = True
                            st.session_state.gcp_setup_done = True
                            st.rerun()
                        else:
                            st.error("❌ GCP Setup failed. Check the logs above.")
    
    # Step 3: GitHub Secrets Configuration
    if toolbox.gcp_setup_done:
        st.markdown('<div class="step-box step-success"><h3>✅ GCP Infrastructure Complete</h3></div>', unsafe_allow_html=True)
        
        if not toolbox.secrets_configured:
            st.markdown('<div class="step-box"><h3>🔑 Step 3: GitHub Secrets Configuration</h3></div>', unsafe_allow_html=True)
            
            if st.button("🔑 **Configure GitHub Secrets**", type="primary", key="setup_gh"):
                with st.spinner("🔑 Setting up GitHub secrets..."):
                    success = toolbox.intelligent_github_setup()
                    if success:
                        st.success("✅ GitHub secrets configured successfully!")
                        st.rerun()
                    else:
                        st.error("❌ GitHub secrets setup failed. Check the logs above.")
    
    elif toolbox.secrets_configured:
        st.markdown('<div class="step-box step-success"><h3>✅ GitHub Secrets Configured</h3></div>', unsafe_allow_html=True)
    
    # Step 4: Pipeline Control & Live Monitoring
    if toolbox.secrets_configured:
        st.markdown('<div class="step-box"><h3>🚀 Step 4: Pipeline Control & Live Monitoring</h3></div>', unsafe_allow_html=True)
        
        # Pipeline Control
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🔄 **Refresh Pipeline Status**", key="refresh_status"):
                toolbox.get_live_pipeline_status()
                st.rerun()
        
        with col2:
            if st.button("🚀 **Trigger Pipeline**", type="primary", key="trigger"):
                toolbox.trigger_pipeline()
                st.rerun()
        
        # Live Pipeline Status
        st.markdown("### 📊 Live Pipeline Status")
        
        # Auto-refresh status every 30 seconds
        if 'last_status_check' not in st.session_state:
            st.session_state.last_status_check = 0
        
        current_time = time.time()
        if current_time - st.session_state.last_status_check > 30:
            toolbox.get_live_pipeline_status()
            st.session_state.last_status_check = current_time
        
        # Status Dashboard
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_color = {
                "completed": "🟢",
                "in_progress": "🟡", 
                "failed": "🔴",
                "queued": "🟠",
                "idle": "⚪",
                "no_runs": "🔵"
            }.get(toolbox.pipeline_details["status"], "⚪")
            
            status_display = toolbox.pipeline_details["status"].replace("_", " ").title()
            if toolbox.pipeline_details["status"] == "no_runs":
                status_display = "No Runs Yet"
            
            st.metric("Status", f"{status_color} {status_display}")
        
        with col2:
            if toolbox.pipeline_details["last_run"]:
                last_run = datetime.fromisoformat(toolbox.pipeline_details["last_run"].replace('Z', '+00:00'))
                st.metric("Last Run", last_run.strftime("%H:%M:%S"))
            else:
                st.metric("Last Run", "Never")
        
        with col3:
            if toolbox.pipeline_details["commit_sha"]:
                st.metric("Commit", toolbox.pipeline_details["commit_sha"])
            else:
                st.metric("Commit", "N/A")
        
        with col4:
            if toolbox.pipeline_details["duration"]:
                st.metric("Duration", toolbox.pipeline_details["duration"])
            else:
                st.metric("Duration", "N/A")
        
        # Pipeline Logs
        st.markdown("### 📝 Pipeline Activity Log")
        if toolbox.pipeline_details["logs"]:
            for log in toolbox.pipeline_details["logs"][-10:]:  # Show last 10 logs
                st.text(log)
        else:
            st.info("No pipeline activity yet")
        
        # Helpful message for new repositories
        if toolbox.pipeline_details["status"] == "no_runs":
            st.markdown('<div class="info-box"><h4>💡 New Repository Detected!</h4></div>', unsafe_allow_html=True)
            st.markdown("""
            To start seeing pipeline activity, you need to:
            1. **Create a GitHub Actions workflow** (`.github/workflows/deploy.yml`)
            2. **Push some code** to trigger the workflow
            3. **Or use the 'Trigger Pipeline' button** above to create your first run
            """)
        
        # Detailed Logs Button
        if st.button("📋 **View Detailed Workflow Logs**", key="view_logs"):
            logs = toolbox.get_workflow_logs()
            st.text_area("Workflow Logs", logs, height=300)
    
    # Success State
    if all([auth_status["gcp"], auth_status["github"], toolbox.gcp_setup_done, toolbox.secrets_configured]):
        st.markdown('<div class="step-box step-success"><h3>🎉 Ready for Deployment!</h3></div>', unsafe_allow_html=True)
        st.success("**Your application is ready for deployment!**")
        
        st.markdown("### 🎯 What's Next?")
        st.markdown("""
        1. **Configure your application** (environment variables, database, etc.)
        2. **Customize the CI/CD pipeline** if needed
        3. **Push code** to trigger automatic deployments
        4. **Monitor deployments** through the live dashboard above
        """)

if __name__ == "__main__":
    main()
