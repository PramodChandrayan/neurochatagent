#!/usr/bin/env python3
"""
🚀 Simple CI/CD Toolbox
Clean, robust architecture that actually works
"""

import streamlit as st
import json
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Set page config FIRST (before any other Streamlit commands)
st.set_page_config(
    page_title="🚀 Simple CI/CD Toolbox",
    page_icon="🚀",
    layout="wide"
)

class SimpleToolbox:
    """Simple, robust CI/CD toolbox with file-based state management"""
    
    def __init__(self):
        self.state_file = "toolbox_state.json"
        self.load_state()
    
    def load_state(self):
        """Load state from file"""
        try:
            if os.path.exists(self.state_file):
                # Check if file is not empty
                if os.path.getsize(self.state_file) > 0:
                    with open(self.state_file, 'r') as f:
                        content = f.read().strip()
                        if content:  # Only parse if content exists
                            st.session_state.update(json.loads(content))
                        else:
                            self.initialize_state()
                else:
                    self.initialize_state()
            else:
                self.initialize_state()
        except (json.JSONDecodeError, Exception) as e:
            st.warning(f"State file corrupted, initializing fresh state: {e}")
            # Backup corrupted file and start fresh
            if os.path.exists(self.state_file):
                backup_file = f"{self.state_file}.backup"
                os.rename(self.state_file, backup_file)
            self.initialize_state()
    
    def save_state(self):
        """Save state to file"""
        try:
            # Create a clean state dict with only serializable data
            clean_state = {}
            for key, value in st.session_state.items():
                # Only save basic types that can be serialized
                if isinstance(value, (str, int, float, bool, list, dict, type(None))):
                    clean_state[key] = value
                else:
                    # Convert non-serializable objects to strings
                    clean_state[key] = str(value)
            
            with open(self.state_file, 'w') as f:
                json.dump(clean_state, f, indent=2)
        except Exception as e:
            st.error(f"Failed to save state: {e}")
    
    def initialize_state(self):
        """Initialize default state"""
        st.session_state.update({
            'phase': 'auth',
            'gcp_authenticated': False,
            'github_authenticated': False,
            'gcp_project': None,
            'github_user': None,
            'infrastructure_complete': False,
            'secrets_complete': False,
            'pipeline_complete': False,
            'cicd_files_created': False,
            'errors': []
        })
        self.save_state()
    
    def update_state(self, **kwargs):
        """Update state and save to file"""
        # Update session state
        st.session_state.update(kwargs)
        # Save to file
        self.save_state()
    
    def add_error(self, error: str):
        """Add error to state"""
        if 'errors' not in st.session_state:
            st.session_state['errors'] = []
        st.session_state['errors'].append(error)
        self.save_state()
    
    def clear_errors(self):
        """Clear all errors"""
        st.session_state['errors'] = []
        self.save_state()
    
    def run(self):
        """Main application"""
        st.title("🚀 Simple CI/CD Toolbox")
        st.markdown("**Clean, robust architecture that actually works**")
        
        # Show current phase
        self.show_phase_indicator()
        
        # Show errors if any
        self.show_errors()
        
        # Show current phase content
        if st.session_state['phase'] == 'auth':
            self.show_auth_phase()
        elif st.session_state['phase'] == 'infrastructure':
            self.show_infrastructure_phase()
        elif st.session_state['phase'] == 'secrets':
            self.show_secrets_phase()
        elif st.session_state['phase'] == 'deploy':
            self.show_deploy_phase()
    
    def show_phase_indicator(self):
        """Show current phase and progress"""
        phases = ['auth', 'infrastructure', 'secrets', 'deploy']
        current_idx = phases.index(st.session_state['phase'])
        
        st.markdown("## 📊 Progress")
        
        # Progress bar
        progress = (current_idx + 1) / len(phases)
        st.progress(progress)
        
        # Phase indicators
        cols = st.columns(len(phases))
        for i, phase in enumerate(phases):
            with cols[i]:
                if i < current_idx:
                    st.success(f"✅ {phase.title()}")
                elif i == current_idx:
                    st.info(f"🔄 {phase.title()}")
                else:
                    st.info(f"⏳ {phase.title()}")
    
    def show_errors(self):
        """Show any errors"""
        if st.session_state.get('errors'):
            st.error("❌ **Errors Found:**")
            for error in st.session_state['errors']:
                st.error(f"• {error}")
            
            # Show helpful information
            st.info("💡 **Troubleshooting Tips:**")
            st.markdown("""
            - **GCP CLI Issues**: Make sure `gcloud` is installed and you're authenticated
            - **GitHub CLI Issues**: Make sure `gh` is installed and you're authenticated
            - **Permission Issues**: Check if you have the right permissions for your GCP project
            - **Network Issues**: Ensure you have internet access and can reach GCP/GitHub
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Clear Errors"):
                    self.clear_errors()
                    st.rerun()
            
            with col2:
                if st.button("🔄 Retry Auth Check"):
                    self.clear_errors()
                    self.check_auth_status()
                    st.rerun()
    
    def show_auth_phase(self):
        """Show authentication phase"""
        st.markdown("## 🔐 Phase 1: Authentication")
        
        # Check current auth status
        if st.button("🔍 Check Current Auth Status"):
            with st.spinner("Checking authentication..."):
                self.clear_errors()  # Clear previous errors
                self.check_auth_status()
                st.success("✅ Authentication check complete!")
        
        # Show current status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🌐 Google Cloud Platform**")
            if st.session_state['gcp_authenticated']:
                st.success(f"✅ Authenticated")
                st.info(f"Project: {st.session_state['gcp_project']}")
            else:
                st.error("❌ Not Authenticated")
                st.markdown("**To authenticate:**")
                st.markdown("1. Install Google Cloud SDK")
                st.markdown("2. Run: `gcloud auth login`")
                st.markdown("3. Run: `gcloud config set project PROJECT_ID`")
                if st.button("🔐 Check GCP Status"):
                    self.authenticate_gcp()
        
        with col2:
            st.markdown("**🐙 GitHub**")
            if st.session_state['github_authenticated']:
                st.success(f"✅ Authenticated")
                st.info(f"User: {st.session_state['github_user']}")
            else:
                st.error("❌ Not Authenticated")
                st.markdown("**To authenticate:**")
                st.markdown("1. Install GitHub CLI")
                st.markdown("2. Run: `gh auth login`")
                if st.button("🔐 Check GitHub Status"):
                    self.authenticate_github()
        
        # Continue button
        if st.session_state['gcp_authenticated'] and st.session_state['github_authenticated']:
            st.success("🎉 Authentication complete!")
            if st.button("🏗️ Continue to Infrastructure"):
                self.update_state(phase='infrastructure')
                st.rerun()
        else:
            st.warning("⚠️ Please complete authentication for both GCP and GitHub to continue")
            
            # Show what's missing
            missing_auth = []
            if not st.session_state['gcp_authenticated']:
                missing_auth.append("GCP")
            if not st.session_state['github_authenticated']:
                missing_auth.append("GitHub")
            
            st.info(f"Missing authentication: {', '.join(missing_auth)}")
            
            # Show manual steps
            st.markdown("**📋 Manual Authentication Steps:**")
            if not st.session_state['gcp_authenticated']:
                st.markdown("**GCP:** `gcloud auth login && gcloud config set project YOUR_PROJECT_ID`")
            if not st.session_state['github_authenticated']:
                st.markdown("**GitHub:** `gh auth login`")
    
    def check_auth_status(self):
        """Check current authentication status"""
        try:
            # Check GCP
            result = subprocess.run(['gcloud', 'auth', 'list'], 
                                 capture_output=True, text=True, check=True)
            if 'ACTIVE' in result.stdout:
                self.update_state(gcp_authenticated=True)
                
                # Get project
                project_result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                             capture_output=True, text=True, check=True)
                project = project_result.stdout.strip()
                if project:
                    self.update_state(gcp_project=project)
            
            # Check GitHub
            result = subprocess.run(['gh', 'auth', 'status'], 
                                 capture_output=True, text=True, check=True)
            if 'Logged in to github.com' in result.stdout:
                self.update_state(github_authenticated=True)
                
                # Get username - try multiple patterns
                import re
                username = None
                
                # Pattern 1: "as username"
                username_match = re.search(r'as (\w+)', result.stdout)
                if username_match:
                    username = username_match.group(1)
                
                # Pattern 2: "username@github.com"
                if not username:
                    username_match = re.search(r'(\w+)@github\.com', result.stdout)
                    if username_match:
                        username = username_match.group(1)
                
                # Pattern 3: Look for any word that might be a username
                if not username:
                    # Find lines with "github.com" and extract potential username
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'github.com' in line and '@' in line:
                            parts = line.split('@')
                            if len(parts) > 1:
                                potential_username = parts[0].strip()
                                if potential_username and len(potential_username) > 1:
                                    username = potential_username
                                    break
                
                if username:
                    self.update_state(github_user=username)
                else:
                    # If we can't detect username, just mark as authenticated
                    self.update_state(github_user="Unknown")
        
        except subprocess.CalledProcessError as e:
            # Handle CLI command failures gracefully
            if 'gcloud' in str(e):
                self.add_error(f"GCP CLI not available or not authenticated: {e}")
            elif 'gh' in str(e):
                self.add_error(f"GitHub CLI not available or not authenticated: {e}")
            else:
                self.add_error(f"CLI command failed: {e}")
        except FileNotFoundError as e:
            # Handle missing CLI tools
            if 'gcloud' in str(e):
                self.add_error("GCP CLI (gcloud) not installed. Please install Google Cloud SDK.")
            elif 'gh' in str(e):
                self.add_error("GitHub CLI (gh) not installed. Please install GitHub CLI.")
            else:
                self.add_error(f"Required tool not found: {e}")
        except Exception as e:
            self.add_error(f"Auth check failed: {e}")
    
    def authenticate_gcp(self):
        """Authenticate with GCP"""
        try:
            st.info("🔐 Starting GCP authentication...")
            # For now, just check if already authenticated
            self.check_auth_status()
            st.success("✅ GCP authentication check complete")
            # Don't call st.rerun() here - let the UI update naturally
        except Exception as e:
            self.add_error(f"GCP authentication failed: {e}")
    
    def authenticate_github(self):
        """Authenticate with GitHub"""
        try:
            st.info("🔐 Starting GitHub authentication...")
            # For now, just check if already authenticated
            self.check_auth_status()
            st.success("✅ GitHub authentication check complete")
            # Don't call st.rerun() here - let the UI update naturally
        except Exception as e:
            self.add_error(f"GitHub authentication failed: {e}")
    
    def show_infrastructure_phase(self):
        """Show infrastructure phase"""
        st.markdown("## 🏗️ Phase 2: Infrastructure Setup")
        
        if not st.session_state['infrastructure_complete']:
            st.info("Setting up GCP infrastructure...")
            
            # Show current status
            self.show_infrastructure_status()
            
            # Debug button to test individual components
            if st.button("🧪 Test Infrastructure Components"):
                with st.spinner("Testing infrastructure components..."):
                    self.test_infrastructure_components()
            
            # Add WIF diagnostic button
            if st.button("🔍 Diagnose WIF Issues"):
                with st.spinner("Diagnosing Workload Identity issues..."):
                    self.diagnose_wif_issues()
            
            if st.button("🏗️ Setup Infrastructure"):
                with st.spinner("Setting up infrastructure..."):
                    if self.setup_infrastructure():
                        self.update_state(infrastructure_complete=True)
                        st.success("✅ Infrastructure setup complete!")
                        st.rerun()
                    else:
                        st.error("❌ Infrastructure setup failed")
                        st.info("Check the errors above and try the test button to debug")
        else:
            st.success("✅ Infrastructure setup complete!")
            
            # Show final status
            self.show_infrastructure_status()
            
            if st.button("🔑 Continue to Secrets"):
                self.update_state(phase='secrets')
                st.rerun()
    
    def test_infrastructure_components(self):
        """Test individual infrastructure components"""
        try:
            project = st.session_state['gcp_project']
            if not project:
                st.error("❌ No GCP project found")
                return
            
            st.info(f"🧪 Testing infrastructure for project: {project}")
            
            # Test GCP CLI
            try:
                result = subprocess.run(['gcloud', '--version'], 
                                     capture_output=True, text=True, check=True)
                st.success("✅ GCP CLI is working")
            except Exception as e:
                st.error(f"❌ GCP CLI test failed: {e}")
                return
            
            # Test project access
            try:
                result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                     capture_output=True, text=True, check=True)
                current_project = result.stdout.strip()
                if current_project == project:
                    st.success(f"✅ Project access confirmed: {current_project}")
                else:
                    st.warning(f"⚠️ Project mismatch: expected {project}, got {current_project}")
            except Exception as e:
                st.error(f"❌ Project access test failed: {e}")
                return
            
            # Test API enablement
            try:
                result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--limit', '1'], 
                                     capture_output=True, text=True, check=True)
                st.success("✅ API service access confirmed")
            except Exception as e:
                st.error(f"❌ API service access test failed: {e}")
                return
            
            st.success("🎉 All infrastructure tests passed!")
            
        except Exception as e:
            st.error(f"❌ Infrastructure test failed: {e}")
    
    def setup_infrastructure(self) -> bool:
        """Setup GCP infrastructure"""
        try:
            # Simple infrastructure setup
            project_id = st.session_state['gcp_project']
            if not project_id:
                self.add_error("No GCP project found")
                return False
            
            st.info(f"Setting up infrastructure for project: {project_id}")
            
            # First, check what APIs are already enabled
            try:
                st.info("🔍 Checking currently enabled APIs...")
                result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--format', 'value(name)'], 
                                     capture_output=True, text=True, check=True)
                enabled_apis = result.stdout.strip().split('\n') if result.stdout.strip() else []
                st.info(f"Currently enabled APIs: {len(enabled_apis)}")
            except Exception as e:
                st.warning(f"⚠️ Could not check enabled APIs: {e}")
                enabled_apis = []
            
            # Discover required APIs dynamically
            st.info("🔍 Discovering required APIs...")
            discovered_apis = self.discover_required_apis()
            if not discovered_apis:
                st.error("❌ Could not discover any required APIs")
                return False
            
            st.info(f"✅ Discovered {len(discovered_apis)} required APIs")
            
            # Enable APIs
            required_apis = discovered_apis
            enabled_count = 0
            
            for api in required_apis:
                if api in enabled_apis:
                    st.success(f"✅ {api} is already enabled")
                    enabled_count += 1
                    continue
                
                try:
                    st.info(f"🔌 Enabling {api}...")
                    result = subprocess.run(['gcloud', 'services', 'enable', api], 
                                         capture_output=True, text=True, check=True)
                    st.success(f"✅ Enabled {api}")
                    enabled_count += 1
                except subprocess.CalledProcessError as e:
                    error_msg = e.stderr if e.stderr else str(e)
                    st.warning(f"⚠️ Could not enable {api}: {error_msg}")
                    
                    if "PERMISSION_DENIED" in error_msg:
                        st.warning(f"Permission denied for {api} - you may need admin access or the API may already be enabled")
                        # Try to check if it's actually enabled despite the error
                        try:
                            check_result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--filter', f'name:{api}'], 
                                                       capture_output=True, text=True, check=True)
                            if api in check_result.stdout:
                                st.success(f"✅ {api} is actually enabled (despite error)")
                                enabled_count += 1
                        except:
                            pass
                    elif "already enabled" in error_msg.lower():
                        st.success(f"✅ {api} is already enabled")
                        enabled_count += 1
                    elif "not found" in error_msg.lower():
                        st.error(f"❌ API {api} not found - check the API name")
                    else:
                        st.warning(f"⚠️ Unknown error enabling {api}: {error_msg}")
                except Exception as e:
                    st.warning(f"⚠️ Error enabling {api}: {e}")
            
            st.info(f"✅ Enabled {enabled_count}/{len(required_apis)} APIs")
            
            # If some APIs failed, provide manual instructions
            if enabled_count < len(required_apis):
                st.warning("⚠️ Some APIs could not be enabled automatically")
                st.info("You may need to enable them manually with admin permissions:")
                for api in required_apis:
                    if api not in enabled_apis:
                        st.code(f"gcloud services enable {api}")
                
                # Check if user wants to continue anyway
                if st.button("🔄 Retry API Enablement"):
                    st.info("Retrying API enablement...")
                    return self.setup_infrastructure()
                
                if st.button("⏭️ Continue Anyway (Manual Setup Required)"):
                    st.warning("⚠️ Continuing with manual API setup required")
                    st.info("You'll need to enable the missing APIs manually before proceeding")
            
            # Set up IAM roles for the current user to manage WIF
            try:
                st.info("🔐 Setting up IAM roles for Workload Identity management...")
                current_user = subprocess.run(['gcloud', 'config', 'get-value', 'account'], 
                                           capture_output=True, text=True, check=True).stdout.strip()
                
                if current_user:
                    st.info(f"👤 Current user: {current_user}")
                    
                    # Grant necessary roles for WIF management
                    wif_roles = [
                        'roles/iam.workloadIdentityPoolAdmin',
                        'roles/iam.workloadIdentityPoolViewer',
                        'roles/iam.serviceAccountAdmin'
                    ]
                    
                    for role in wif_roles:
                        try:
                            st.info(f"🔑 Granting {role} to {current_user}...")
                            result = subprocess.run(['gcloud', 'projects', 'add-iam-policy-binding', project_id,
                                                   '--member', f'user:{current_user}',
                                                   '--role', role], 
                                               capture_output=True, text=True, check=True)
                            st.success(f"✅ Granted {role}")
                        except subprocess.CalledProcessError as e:
                            if "already has" in e.stderr.lower() or "already bound" in e.stderr.lower():
                                st.success(f"✅ {role} already granted")
                            else:
                                st.warning(f"⚠️ Could not grant {role}: {e.stderr}")
                                st.info("This might require project owner permissions")
                else:
                    st.warning("⚠️ Could not determine current user")
                    
            except Exception as e:
                st.warning(f"⚠️ IAM role setup failed: {e}")
                st.info("You may need to manually grant the required roles")
                st.info("Required roles: Workload Identity Pool Admin, Workload Identity Pool Viewer, Service Account Admin")
            
            # Verify Workload Identity API is properly enabled
            try:
                st.info("🔍 Verifying Workload Identity API status...")
                result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--filter', 'name:iam.googleapis.com'], 
                                     capture_output=True, text=True, check=True)
                
                if 'iam.googleapis.com' in result.stdout:
                    st.success("✅ IAM API is enabled (required for Workload Identity)")
                else:
                    st.error("❌ IAM API is not enabled - this is required for Workload Identity")
                    st.info("Please enable the IAM API first:")
                    st.code("gcloud services enable iam.googleapis.com")
                    return False
                    
            except Exception as e:
                st.error(f"❌ Could not verify IAM API status: {e}")
                return False
            
            # Create CI/CD service account
            try:
                st.info("👤 Creating CI/CD service account...")
                service_account = f"cicd-service-account@{project_id}.iam.gserviceaccount.com"
                
                # Check if service account exists
                try:
                    result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'describe', service_account], 
                                         capture_output=True, text=True, check=True)
                    st.success(f"✅ Service account already exists: {service_account}")
                    self.update_state(service_account_email=service_account)
                except subprocess.CalledProcessError as e:
                    if "not found" in e.stderr.lower():
                        st.info(f"👤 Creating new service account: {service_account}")
                        result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'create', 'cicd-service-account',
                                               '--display-name', 'CI/CD Service Account',
                                               '--description', 'Service account for CI/CD pipeline'], 
                                           capture_output=True, text=True, check=True)
                        st.success(f"✅ Created service account: {service_account}")
                        self.update_state(service_account_email=service_account)
                    else:
                        st.error(f"❌ Service account creation failed: {e}")
                        return False
                        
            except Exception as e:
                st.error(f"❌ Service account setup failed: {e}")
                return False
            
            # Set up Workload Identity Federation
            try:
                st.info("🔗 Setting up Workload Identity Federation...")
                wif_pool_name = f"neurogent-wif-pool"
                wif_provider_name = f"neurogent-wif-provider"
                
                # Create or get WIF pool
                st.info(f"🔍 Checking Workload Identity Pool: {wif_pool_name}")
                try:
                    result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'describe', wif_pool_name, '--location', 'global'], 
                                         capture_output=True, text=True, check=True)
                    st.success(f"✅ Workload Identity Pool '{wif_pool_name}' already exists.")
                    self.update_state(workload_identity_pool=wif_pool_name)
                except subprocess.CalledProcessError as e:
                    error_output = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
                    st.info(f"📋 Pool check result: {error_output}")
                    
                    if "not found" in error_output.lower():
                        st.info(f"🔗 Creating Workload Identity Pool: {wif_pool_name}")
                        try:
                            result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'create', wif_pool_name,
                                                   '--location', 'global',
                                                   '--display-name', 'NeuroGent Workload Identity Pool'], 
                                               capture_output=True, text=True, check=True)
                            st.success(f"✅ Created Workload Identity Pool: {wif_pool_name}")
                            self.update_state(workload_identity_pool=wif_pool_name)
                        except subprocess.CalledProcessError as create_error:
                            create_error_output = create_error.stderr if create_error.stderr else create_error.stdout if create_error.stdout else str(create_error)
                            st.error(f"❌ Failed to create WIF pool: {create_error_output}")
                            st.info("This might be a permissions issue. You may need to:")
                            st.info("1. Ensure you have 'Workload Identity Pool Admin' role")
                            st.info("2. Check if the pool name is already taken")
                            st.info("3. Try a different pool name")
                            return False
                    else:
                        st.error(f"❌ Unexpected error checking WIF pool: {error_output}")
                        st.info("This might be a permissions issue. Please check:")
                        st.info("1. You have 'Workload Identity Pool Viewer' role")
                        st.info("2. The project has Workload Identity enabled")
                        st.info("3. Try running manually: gcloud iam workload-identity-pools list")
                        return False
                
                # Create or get WIF provider
                st.info(f"🔍 Checking Workload Identity Provider: {wif_provider_name}")
                try:
                    result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'providers', 'describe', wif_provider_name, '--workload-identity-pool', wif_pool_name, '--location', 'global'], 
                                         capture_output=True, text=True, check=True)
                    st.success(f"✅ Workload Identity Provider '{wif_provider_name}' already exists.")
                    self.update_state(workload_identity_provider=wif_provider_name)
                except subprocess.CalledProcessError as e:
                    error_output = e.stderr if e.stderr else e.stdout if e.stdout else str(e)
                    st.info(f"📋 Provider check result: {error_output}")
                    
                    if "not found" in error_output.lower():
                        st.info(f"🔗 Creating Workload Identity Provider: {wif_provider_name}")
                        try:
                            # For GitHub Actions, we need to use create-oidc (OpenID Connect)
                            result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'providers', 'create-oidc', wif_provider_name,
                                                   '--workload-identity-pool', wif_pool_name,
                                                   '--location', 'global',
                                                   '--issuer-uri', 'https://token.actions.githubusercontent.com',
                                                   '--attribute-mapping', 'google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner',
                                                   '--attribute-condition', 'assertion.repository_owner=="PramodChandrayan"'], 
                                               capture_output=True, text=True, check=True)
                            st.success(f"✅ Created Workload Identity Provider: {wif_provider_name}")
                            self.update_state(workload_identity_provider=wif_provider_name)
                        except subprocess.CalledProcessError as create_error:
                            create_error_output = create_error.stderr if create_error.stderr else create_error.stdout if create_error.stdout else str(create_error)
                            st.error(f"❌ Failed to create WIF provider: {create_error_output}")
                            st.info("This might be a permissions issue. You may need to:")
                            st.info("1. Ensure you have 'Workload Identity Provider Admin' role")
                            st.info("2. Check if the provider name is already taken")
                            st.info("3. Verify the pool exists and is accessible")
                            return False
                    else:
                        st.error(f"❌ Unexpected error checking WIF provider: {error_output}")
                        st.info("This might be a permissions issue. Please check:")
                        st.info("1. You have 'Workload Identity Provider Viewer' role")
                        st.info("2. The pool exists and is accessible")
                        st.info("3. Try running manually: gcloud iam workload-identity-pools providers list --workload-identity-pool=" + wif_pool_name)
                        return False
                
                st.success("🎉 Workload Identity Federation setup complete!")
                
                # Configure IAM binding between service account and WIF provider
                try:
                    st.info("🔗 Configuring IAM binding for service account...")
                    wif_provider_full_name = f"projects/{project_id}/locations/global/workloadIdentityPools/{wif_pool_name}/providers/{wif_provider_name}"
                    
                    result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'add-iam-policy-binding', service_account,
                                           '--role', 'roles/iam.workloadIdentityUser',
                                           '--member', f'principalSet://iam.googleapis.com/projects/{project_id}/locations/global/workloadIdentityPools/{wif_pool_name}/attribute.repository/PramodChandrayan/neurochatagent'], 
                                       capture_output=True, text=True, check=True)
                    st.success("✅ IAM binding configured for service account")
                    
                except subprocess.CalledProcessError as e:
                    st.warning(f"⚠️ IAM binding configuration failed: {e}")
                    st.info("You may need to configure this manually or the binding already exists")
                except Exception as e:
                    st.warning(f"⚠️ IAM binding configuration error: {e}")
                
            except Exception as e:
                st.error(f"❌ Workload Identity Federation setup failed: {e}")
                st.info("Please check the error details above and ensure you have proper permissions")
                
                # Try alternative approach
                st.info("🔄 Trying alternative WIF setup approach...")
                if self.setup_wif_alternative(project_id, service_account):
                    st.success("✅ Alternative WIF setup successful!")
                else:
                    st.error("❌ Alternative WIF setup also failed")
                    st.info("You may need to:")
                    st.info("1. Contact your GCP project owner")
                    st.info("2. Ensure you have admin permissions")
                    st.info("3. Check if Workload Identity is enabled for your organization")
                    return False
            
            # Create Artifact Registry repository
            try:
                st.info("🐳 Creating Artifact Registry repository...")
                result = subprocess.run(['gcloud', 'artifacts', 'repositories', 'create', 'neurogent-repo',
                                       '--repository-format', 'docker',
                                       '--location', 'us-central1',
                                       '--description', 'Docker repository for NeuroGent Finance Assistant'], 
                                     capture_output=True, text=True, check=True)
                st.success("✅ Created Artifact Registry repository: neurogent-repo")
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else str(e)
                if "already exists" in error_msg.lower():
                    st.success("✅ Artifact Registry repository already exists: neurogent-repo")
                else:
                    st.warning(f"⚠️ Artifact Registry creation failed: {error_msg}")
                    # Don't fail completely for this
            except Exception as e:
                st.warning(f"⚠️ Artifact Registry creation error: {e}")
                # Don't fail completely for this
            
            st.success("🎉 Infrastructure setup completed successfully!")
            return True
            
        except Exception as e:
            error_msg = f"Infrastructure setup failed: {e}"
            self.add_error(error_msg)
            st.error(f"❌ {error_msg}")
            return False
    
    def discover_required_apis(self):
        """Discover the correct API names for required services"""
        api_mappings = {
            'cloudrun': ['run.googleapis.com', 'cloudrun.googleapis.com'],
            'iam': ['iam.googleapis.com'],
            'artifactregistry': ['artifactregistry.googleapis.com'],
            'cloudbuild': ['cloudbuild.googleapis.com'],
            'containerregistry': ['containerregistry.googleapis.com']
        }
        
        discovered_apis = []
        
        for service_type, possible_names in api_mappings.items():
            for api_name in possible_names:
                try:
                    result = subprocess.run(['gcloud', 'services', 'list', '--available', '--filter', f'name:{api_name}'], 
                                         capture_output=True, text=True, check=True)
                    if api_name in result.stdout:
                        discovered_apis.append(api_name)
                        st.info(f"✅ Discovered {service_type} API: {api_name}")
                        break
                except:
                    continue
        
        return discovered_apis
    
    def setup_wif_alternative(self, project_id: str, service_account: str) -> bool:
        """Alternative WIF setup method using different approach"""
        try:
            st.info("🔄 Using alternative WIF setup method...")
            
            # Use timestamp-based names to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            wif_pool_name = f"neurogent-pool-{timestamp}"
            wif_provider_name = f"neurogent-provider-{timestamp}"
            
            st.info(f"🔗 Creating WIF Pool: {wif_pool_name}")
            
            # Create pool with explicit location
            result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'create', wif_pool_name,
                                   '--location', 'global',
                                   '--display-name', f'NeuroGent WIF Pool {timestamp}',
                                   '--description', 'Alternative WIF pool for CI/CD'], 
                               capture_output=True, text=True, check=True)
            
            st.success(f"✅ Created WIF Pool: {wif_pool_name}")
            self.update_state(workload_identity_pool=wif_pool_name)
            
            # Create provider with GitHub-specific attributes
            st.info(f"🔗 Creating WIF Provider: {wif_provider_name}")
            
            result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'providers', 'create-oidc', wif_provider_name,
                                   '--workload-identity-pool', wif_pool_name,
                                   '--location', 'global',
                                   '--issuer-uri', 'https://token.actions.githubusercontent.com',
                                   '--attribute-mapping', 'google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner',
                                   '--attribute-condition', 'assertion.repository_owner=="PramodChandrayan"'], 
                               capture_output=True, text=True, check=True)
            
            st.success(f"✅ Created WIF Provider: {wif_provider_name}")
            self.update_state(workload_identity_provider=wif_provider_name)
            
            return True
            
        except Exception as e:
            st.error(f"❌ Alternative WIF setup failed: {e}")
            return False
    
    def show_secrets_phase(self):
        """Show secrets phase"""
        st.markdown("## 🔑 Phase 3: Secrets Configuration")
        
        if not st.session_state['secrets_complete']:
            st.info("Configuring secrets for CI/CD...")
            
            if st.button("🔑 Configure Secrets"):
                with st.spinner("Configuring secrets..."):
                    if self.configure_secrets():
                        self.update_state(secrets_complete=True)
                        st.success("✅ Secrets configuration complete!")
                        st.rerun()
                    else:
                        st.error("❌ Secrets configuration failed")
        else:
            st.success("✅ Secrets configuration complete!")
            if st.button("🚀 Continue to Deploy"):
                self.update_state(phase='deploy')
                st.rerun()
    
    def configure_secrets(self) -> bool:
        """Smart secrets configuration: Check existing, analyze missing, configure via GitHub CLI, create YAML, let user push manually"""
        try:
            st.markdown("## 🔐 Phase 3: Smart Secrets Configuration")
            st.info("🔍 Analyzing infrastructure and GitHub secrets for CI/CD pipeline...")
            
            # Get current infrastructure state
            project_id = st.session_state.get('gcp_project')
            service_account = st.session_state.get('service_account_email')
            wif_pool = st.session_state.get('workload_identity_pool')
            wif_provider = st.session_state.get('workload_identity_provider')
            
            if not all([project_id, service_account, wif_pool, wif_provider]):
                st.error("❌ Missing required infrastructure configuration")
                st.info("Please complete infrastructure setup first")
                return False
            
            st.success("✅ Infrastructure configuration found:")
            st.info(f"📋 Project ID: {project_id}")
            st.info(f"👤 Service Account: {service_account}")
            st.info(f"🔗 WIF Pool: {wif_pool}")
            st.info(f"🔗 WIF Provider: {wif_provider}")
            
            # Step 1: Extract exact secret values from infrastructure
            st.markdown("### 🔍 Step 1: Extract Secret Values from Infrastructure")
            
            try:
                # Get WIF provider full name
                result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'providers', 'describe', 
                                       wif_provider, '--workload-identity-pool', wif_pool, '--location', 'global', 
                                       '--format', 'value(name)'], capture_output=True, text=True, check=True)
                wif_provider_full_name = result.stdout.strip()
                st.success(f"✅ **WIF Provider Resource**: `{wif_provider_full_name}`")
            except Exception as e:
                st.error(f"❌ **WIF Provider**: Could not extract - {e}")
                wif_provider_full_name = f"projects/{project_id}/locations/global/workloadIdentityPools/{wif_pool}/providers/{wif_provider}"
                st.warning(f"⚠️ **WIF Provider Resource**: Using fallback - `{wif_provider_full_name}`")
            
            st.success(f"✅ **Service Account**: `{service_account}`")
            st.success(f"✅ **Project ID**: `{project_id}`")
            
            # Step 2: Check GitHub CLI and repository
            st.markdown("### 🔍 Step 2: Verify GitHub Access")
            
            try:
                # Check GitHub CLI
                result = subprocess.run(['gh', '--version'], capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    st.error("❌ GitHub CLI not installed")
                    st.info("Please install GitHub CLI: https://cli.github.com/")
                    return False
                
                # Check authentication
                result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, check=False)
                if result.returncode == 0 and 'Logged in to github.com' in result.stdout:
                    st.success("✅ GitHub CLI is authenticated")
                else:
                    st.error("❌ GitHub CLI not authenticated")
                    st.info("Please run: gh auth login")
                    return False
                
                # Get repository info
                result = subprocess.run(['gh', 'repo', 'view', '--json', 'name,owner'], capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    repo_info = json.loads(result.stdout)
                    repo_name = repo_info['name']
                    repo_owner = repo_info['owner']['login']
                    st.success(f"✅ Repository: {repo_owner}/{repo_name}")
                else:
                    st.error("❌ Could not get repository info")
                    st.info("Please ensure you're in the correct repository directory")
                    return False
                    
            except Exception as e:
                st.error(f"❌ GitHub access error: {e}")
                return False
            
            # Step 3: Analyze existing GitHub secrets
            st.markdown("### 🔍 Step 3: Analyze GitHub Secrets Status")
            
            # Initialize variables
            missing_secrets = []
            existing_secret_names = []
            required_secrets = {
                'GCP_WORKLOAD_IDENTITY_PROVIDER': wif_provider_full_name,
                'GCP_SERVICE_ACCOUNT_EMAIL': service_account,
                'GCP_PROJECT_ID': project_id
            }
            
            try:
                result = subprocess.run(['gh', 'secret', 'list', '--repo', f'{repo_owner}/{repo_name}'], 
                                      capture_output=True, text=True, check=True)
                existing_secrets = result.stdout
                
                # Analyze what's missing
                for secret_name, secret_value in required_secrets.items():
                    if secret_name in existing_secrets:
                        st.success(f"✅ **{secret_name}** - Already configured")
                        existing_secret_names.append(secret_name)
                    else:
                        st.error(f"❌ **{secret_name}** - Missing")
                        missing_secrets.append(secret_name)
                        st.code(secret_value, language='text')
                
                if not missing_secrets:
                    st.success("🎉 All required secrets are already configured!")
                    st.info("Ready to proceed to pipeline creation")
                else:
                    st.warning(f"⚠️ {len(missing_secrets)} secrets need to be configured")
                    
            except Exception as e:
                st.error(f"❌ Error checking secrets: {e}")
                st.info("Proceeding with secret configuration...")
                missing_secrets = ['GCP_WORKLOAD_IDENTITY_PROVIDER', 'GCP_SERVICE_ACCOUNT_EMAIL', 'GCP_PROJECT_ID']
                existing_secret_names = []
            
            # Step 4: Configure missing secrets via GitHub CLI
            if missing_secrets:
                st.markdown("### 🔐 Step 4: Configure Missing Secrets")
                
                if st.button("🚀 Push Secrets to GitHub (GitHub CLI Magic)"):
                    with st.spinner("🔐 Configuring secrets via GitHub CLI..."):
                        success_count = 0
                        
                        for secret_name in missing_secrets:
                            try:
                                secret_value = required_secrets[secret_name]
                                st.info(f"🔐 Setting {secret_name}...")
                                
                                result = subprocess.run(['gh', 'secret', 'set', secret_name, '--repo', 
                                                       f'{repo_owner}/{repo_name}', '--body', secret_value], 
                                                      capture_output=True, text=True, check=True)
                                
                                st.success(f"✅ {secret_name} configured successfully!")
                                success_count += 1
                                
                            except subprocess.CalledProcessError as e:
                                st.error(f"❌ Failed to configure {secret_name}: {e.stderr}")
                                return False
                            except Exception as e:
                                st.error(f"❌ Error configuring {secret_name}: {e}")
                                return False
                        
                        if success_count == len(missing_secrets):
                            st.success(f"🎉 All {success_count} secrets configured successfully!")
                            st.rerun()  # Refresh to show updated status
                        else:
                            st.error(f"❌ Only {success_count}/{len(missing_secrets)} secrets configured")
                            return False
            
            # Step 5: Create CI/CD YAML and workflow files
            st.markdown("### 📋 Step 5: Create CI/CD Pipeline Files")
            
            # Check if CI/CD files already exist
            yaml_exists = os.path.exists(".github/workflows/deploy.yml")
            dockerfile_exists = os.path.exists("Dockerfile")
            
            if yaml_exists and dockerfile_exists:
                st.success("✅ CI/CD pipeline files already exist!")
                st.info("📁 .github/workflows/deploy.yml")
                st.info("📁 Dockerfile")
                st.info("📁 requirements.txt")
                
                # Step 6: Manual code push (user control) - ONLY ONE BUTTON
                st.markdown("### 🚀 Step 6: Push Code to GitHub (Manual Control)")
                st.info("🔒 **User Control**: You decide when to push code and trigger the pipeline")
                
                if st.button("🚀 Push Code & Trigger Pipeline"):
                    with st.spinner("🚀 Pushing code to GitHub..."):
                        if self.push_code_to_github():
                            st.success("🎉 Code pushed successfully!")
                            st.info("🚀 CI/CD pipeline is now running!")
                            st.info(f"📊 Monitor progress: https://github.com/{repo_owner}/{repo_name}/actions")
                            
                            # Update state
                            self.update_state(secrets_complete=True, pipeline_complete=True)
                            return True
                        else:
                            st.error("❌ Failed to push code")
                            return False
            else:
                # Show generate button if files don't exist
                st.info("📋 CI/CD pipeline files need to be created")
                
                if st.button("📋 Generate CI/CD Pipeline Files"):
                    with st.spinner("📋 Creating CI/CD pipeline files..."):
                        if self.create_cicd_files():
                            st.success("✅ CI/CD pipeline files created successfully!")
                            st.info("📁 .github/workflows/deploy.yml")
                            st.info("📁 Dockerfile")
                            st.info("📁 requirements.txt")
                            
                            # Update state and show next step
                            self.update_state(cicd_files_created=True)
                            
                            # Step 6: Manual code push (user control) - ONLY ONE BUTTON
                            st.markdown("### 🚀 Step 6: Push Code to GitHub (Manual Control)")
                            st.info("🔒 **User Control**: You decide when to push code and trigger the pipeline")
                            
                            if st.button("🚀 Push Code & Trigger Pipeline"):
                                with st.spinner("🚀 Pushing code to GitHub..."):
                                    if self.push_code_to_github():
                                        st.success("🎉 Code pushed successfully!")
                                        st.info("🚀 CI/CD pipeline is now running!")
                                        st.info(f"📊 Monitor progress: https://github.com/{repo_owner}/{repo_name}/actions")
                                        
                                        # Update state
                                        self.update_state(secrets_complete=True, pipeline_complete=True)
                                        return True
                                    else:
                                        st.error("❌ Failed to push code")
                                        return False
                        else:
                            st.error("❌ Failed to create CI/CD files")
                            return False
            
            # If we reach here and all secrets are configured, return True
            if not missing_secrets:
                st.success("🎉 All secrets are configured and ready for pipeline creation!")
                return True
            
            return False
            
        except Exception as e:
            error_msg = f"Secrets configuration failed: {e}"
            self.add_error(error_msg)
            st.error(f"❌ {error_msg}")
            return False
    
    def show_deploy_phase(self):
        """Show deployment phase"""
        st.markdown("## 🚀 Phase 4: Deploy Pipeline")
        
        if not st.session_state['pipeline_complete']:
            st.info("Setting up deployment pipeline...")
            st.warning("⚠️ **Note**: This will only generate CI/CD files. You will manually push to GitHub when ready.")
            
            if st.button("📋 Generate CI/CD Pipeline Files"):
                with st.spinner("📋 Generating CI/CD pipeline files..."):
                    if self.setup_pipeline():
                        self.update_state(pipeline_complete=True)
                        st.success("✅ Pipeline files generated successfully!")
                        st.info("📁 CI/CD files are ready for review")
                        st.rerun()
                    else:
                        st.error("❌ Failed to generate pipeline files")
        else:
            st.success("🎉 All phases complete!")
            st.info("Your CI/CD pipeline files are ready!")
            
            # Check if CI/CD files actually exist
            yaml_exists = os.path.exists(".github/workflows/deploy.yml")
            dockerfile_exists = os.path.exists("Dockerfile")
            
            if not yaml_exists or not dockerfile_exists:
                st.warning("⚠️ CI/CD files are missing! Let's generate them now.")
                self.update_state(pipeline_complete=False)
                st.rerun()
            else:
                st.success("✅ CI/CD files found:")
                st.info(f"📁 .github/workflows/deploy.yml: {'✅' if yaml_exists else '❌'}")
                st.info(f"📁 Dockerfile: {'✅' if dockerfile_exists else '❌'}")
                
                # Show the actual pipeline content
                if yaml_exists:
                    with open(".github/workflows/deploy.yml", 'r') as f:
                        yaml_content = f.read()
                    st.code(yaml_content, language='yaml')
                
                # Show pipeline status
                self.show_pipeline_status("PramodChandrayan", "neurochatagent")
                
                # Show next steps
                st.markdown("### 🎯 Next Steps:")
                st.markdown("1. **Review the generated CI/CD files** above")
                st.markdown("2. **Make any code changes** you want to deploy")
                st.markdown("3. **Manually push to GitHub** when you're ready:")
                st.code("git add .\ngit commit -m 'Add CI/CD pipeline'\ngit push origin main")
                st.markdown("4. **Check GitHub Actions** to see your pipeline running!")
                
                st.warning("⚠️ **Important**: Pipeline will NOT trigger automatically. You must manually push code when ready.")
                
                # Add button to regenerate if needed
                if st.button("🔄 Regenerate CI/CD Pipeline"):
                    self.update_state(pipeline_complete=False)
                    st.rerun()
            
            if st.button("🔄 Start Over"):
                self.initialize_state()
                st.rerun()
    
    def setup_pipeline(self) -> bool:
        """Setup deployment pipeline - Generate files only, no automatic push"""
        try:
            st.info("🚀 Setting up deployment pipeline...")
            
            # Validate infrastructure setup
            if not self.validate_infrastructure_setup():
                return False
            
            # Get current state
            project_id = st.session_state.get('gcp_project')
            service_account = st.session_state.get('service_account_email')
            wif_pool = st.session_state.get('workload_identity_pool')
            wif_provider = st.session_state.get('workload_identity_provider')
            
            # Generate CI/CD YAML
            st.info("📝 Generating CI/CD pipeline configuration...")
            cicd_yaml = self.generate_cicd_yaml(project_id, service_account, wif_pool, wif_provider)
            
            if not cicd_yaml:
                st.error("❌ Failed to generate CI/CD configuration")
                return False
            
            # Write YAML to file
            yaml_file = ".github/workflows/deploy.yml"
            os.makedirs(".github/workflows", exist_ok=True)
            
            with open(yaml_file, 'w') as f:
                f.write(cicd_yaml)
            
            st.success(f"✅ Generated {yaml_file}")
            
            # Generate Dockerfile
            st.info("🐳 Generating Dockerfile...")
            dockerfile_content = self.generate_dockerfile()
            if dockerfile_content:
                with open("Dockerfile", 'w') as f:
                    f.write(dockerfile_content)
                st.success("✅ Generated Dockerfile")
            else:
                st.warning("⚠️ Could not generate Dockerfile")
            
            # Ensure requirements.txt exists
            if not os.path.exists("requirements.txt"):
                st.info("📦 Creating requirements.txt...")
                requirements_content = """streamlit>=1.28.0
google-cloud-iam>=2.0.0
google-cloud-run>=0.10.0
google-cloud-artifact-registry>=1.0.0
google-auth>=2.0.0
"""
                with open("requirements.txt", 'w') as f:
                    f.write(requirements_content)
                st.success("✅ Created requirements.txt")
            
            st.success("🎉 CI/CD pipeline files generated successfully!")
            st.info("📁 .github/workflows/deploy.yml")
            st.info("📁 Dockerfile")
            st.info("📁 requirements.txt")
            
            # Show next steps WITHOUT automatic push
            st.markdown("### 🎯 Next Steps:")
            st.markdown("1. **Review the generated CI/CD files** above")
            st.markdown("2. **Make any code changes** you want to deploy")
            st.markdown("3. **Manually push to GitHub** when you're ready:")
            st.code("git add .\ngit commit -m 'Add CI/CD pipeline'\ngit push origin main")
            st.markdown("4. **Check GitHub Actions** to see your pipeline running!")
            
            st.warning("⚠️ **Important**: Pipeline will NOT trigger automatically. You must manually push code when ready.")
            
            return True
                
        except Exception as e:
            error_msg = f"Pipeline setup failed: {e}"
            self.add_error(error_msg)
            st.error(f"❌ {error_msg}")
            return False
    
    def generate_cicd_yaml(self, project_id: str, service_account: str, wif_pool: str, wif_provider: str, yaml_type: str = "comprehensive") -> str:
        """Generate CI/CD YAML configuration - Simple or Comprehensive"""
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
        # Use regular string to avoid f-string issues with GitHub Actions variables
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
        """Generate comprehensive CI/CD YAML configuration with all stages"""
        # Use regular string to avoid f-string issues with GitHub Actions variables
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

    def push_to_github(self, yaml_file: str) -> bool:
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
    
    def push_to_github(self, yaml_file: str) -> bool:
        """Push changes to GitHub"""
        try:
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                 capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                st.info("No changes to commit")
                return True
            
            # Add the new file
            subprocess.run(['git', 'add', yaml_file], check=True)
            
            # Commit
            commit_msg = f"Add CI/CD pipeline configuration - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            
            # Check current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True, check=True)
            current_branch = branch_result.stdout.strip()
            
            # Push to current branch
            subprocess.run(['git', 'push', 'origin', current_branch], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            st.error(f"❌ Push to GitHub failed: {e}")
            return False

    def generate_dockerfile(self) -> str:
        """Generate Dockerfile for the application"""
        try:
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
            
        except Exception as e:
            st.error(f"❌ Failed to generate Dockerfile: {e}")
            return ""

    def validate_infrastructure_setup(self) -> bool:
        """Validate that all required infrastructure components are set up"""
        required_values = {
            'gcp_project': 'GCP Project ID',
            'service_account_email': 'Service Account Email',
            'workload_identity_pool': 'Workload Identity Pool',
            'workload_identity_provider': 'Workload Identity Provider'
        }
        
        missing_values = []
        for key, description in required_values.items():
            if not st.session_state.get(key):
                missing_values.append(f"{description} ({key})")
        
        if missing_values:
            st.error("❌ Missing required infrastructure configuration:")
            for missing in missing_values:
                st.error(f"   • {missing}")
            st.info("Please complete infrastructure setup first")
            return False
        
        return True

    def show_infrastructure_status(self):
        """Show current infrastructure status"""
        st.markdown("### 🔍 Current Infrastructure Status")
        
        status_items = [
            ('gcp_project', 'GCP Project ID'),
            ('service_account_email', 'Service Account Email'),
            ('workload_identity_pool', 'Workload Identity Pool'),
            ('workload_identity_provider', 'Workload Identity Provider')
        ]
        
        for key, description in status_items:
            value = st.session_state.get(key)
            if value:
                st.success(f"✅ {description}: `{value}`")
            else:
                st.error(f"❌ {description}: Missing")
        
        # Show what's needed
        missing = [desc for key, desc in status_items if not st.session_state.get(key)]
        if missing:
            st.warning(f"⚠️ Missing: {', '.join(missing)}")
            st.info("Please complete infrastructure setup to proceed")
        else:
            st.success("🎉 All infrastructure components are ready!")

    def diagnose_wif_issues(self):
        """Diagnostic tool to help troubleshoot Workload Identity Federation issues"""
        st.markdown("## 🔍 Workload Identity Federation Diagnostics")
        
        project_id = st.session_state.get('gcp_project')
        if not project_id:
            st.error("❌ No GCP project found. Please complete infrastructure setup first.")
            return

        st.info(f"🔍 Diagnosing Workload Identity Federation for project: {project_id}")

        # 1. Check if Workload Identity API is enabled
        try:
            st.info("1. Checking if IAM API is enabled...")
            result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--filter', 'name:iam.googleapis.com'], 
                                 capture_output=True, text=True, check=True)
            if 'iam.googleapis.com' in result.stdout:
                st.success("✅ IAM API is enabled (required for Workload Identity)")
            else:
                st.error("❌ IAM API is NOT enabled. Please enable it: `gcloud services enable iam.googleapis.com`")
                st.info("You might need admin permissions or it's already enabled.")
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Could not check IAM API status: {e}")
            st.info("Please ensure gcloud is authenticated and try again.")

        # 2. Check if the WIF pool exists
        wif_pool_name = st.session_state.get('workload_identity_pool')
        if not wif_pool_name:
            st.error("❌ No Workload Identity Pool found. Please complete infrastructure setup first.")
            return

        try:
            st.info(f"2. Checking if Workload Identity Pool '{wif_pool_name}' exists...")
            result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'describe', wif_pool_name, '--location', 'global'], 
                                 capture_output=True, text=True, check=True)
            st.success(f"✅ Workload Identity Pool '{wif_pool_name}' exists.")
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Workload Identity Pool '{wif_pool_name}' NOT found. Please create it:")
            st.code(f"gcloud iam workload-identity-pools create {wif_pool_name} --location=global --display-name='{wif_pool_name}'")
            st.info("You might need 'Workload Identity Pool Admin' role.")

        # 3. Check if the WIF provider exists
        wif_provider_name = st.session_state.get('workload_identity_provider')
        if not wif_provider_name:
            st.error("❌ No Workload Identity Provider found. Please complete infrastructure setup first.")
            return

        try:
            st.info(f"3. Checking if Workload Identity Provider '{wif_provider_name}' exists...")
            result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'providers', 'describe', wif_provider_name, '--workload-identity-pool', wif_pool_name, '--location', 'global'], 
                                 capture_output=True, text=True, check=True)
            st.success(f"✅ Workload Identity Provider '{wif_provider_name}' exists.")
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Workload Identity Provider '{wif_provider_name}' NOT found. Please create it:")
            st.code(f"gcloud iam workload-identity-pools providers create-oidc {wif_provider_name} --workload-identity-pool={wif_pool_name} --location=global --issuer-uri=https://token.actions.githubusercontent.com --attribute-mapping='google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner' --attribute-condition='assertion.repository_owner==\"PramodChandrayan\"'")
            st.info("You might need 'Workload Identity Pool Admin' role.")

        # 4. Check if the service account exists
        service_account_email = st.session_state.get('service_account_email')
        if not service_account_email:
            st.error("❌ No CI/CD service account found. Please complete infrastructure setup first.")
            return

        try:
            st.info(f"4. Checking if service account '{service_account_email}' exists...")
            result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'describe', service_account_email], 
                                 capture_output=True, text=True, check=True)
            st.success(f"✅ Service account '{service_account_email}' exists.")
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Service account '{service_account_email}' NOT found. Please create it:")
            st.code(f"gcloud iam service-accounts create {service_account_email} --display-name='CI/CD Service Account' --description='Service account for CI/CD pipeline'")
            st.info("You might need 'Service Account Admin' role.")

        # 5. Check if the project has the necessary IAM roles
        try:
            st.info("5. Checking if current user has necessary IAM roles...")
            current_user = subprocess.run(['gcloud', 'config', 'get-value', 'account'], 
                                         capture_output=True, text=True, check=True).stdout.strip()
            
            if not current_user:
                st.warning("⚠️ Could not determine current user. Please ensure gcloud is authenticated.")
                st.info("Run `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`")
                return

            st.info(f"👤 Current user: {current_user}")

            # Define roles to check
            roles_to_check = [
                'roles/iam.workloadIdentityPoolAdmin',
                'roles/iam.workloadIdentityPoolViewer',
                'roles/iam.serviceAccountAdmin'
            ]

            missing_roles = []
            for role in roles_to_check:
                try:
                    result = subprocess.run(['gcloud', 'projects', 'get-iam-policy', project_id,
                                           '--flatten', 'bindings[].role',
                                           '--format', 'value(bindings.role)',
                                           '--filter', f'bindings.members:{current_user}'], 
                                       capture_output=True, text=True, check=True)
                    if role not in result.stdout:
                        missing_roles.append(role)
                except subprocess.CalledProcessError as e:
                    st.warning(f"⚠️ Could not check role '{role}' for current user: {e}")
                    st.info("Please ensure you have the role or are a project owner.")

            if missing_roles:
                st.error("❌ Missing necessary IAM roles for Workload Identity Federation:")
                for role in missing_roles:
                    st.error(f"   • {role}")
                st.info("You might need to manually grant these roles to your user or the service account.")
            else:
                st.success("✅ Current user has all required IAM roles.")

        except subprocess.CalledProcessError as e:
            st.error(f"❌ Could not check IAM roles: {e}")
            st.info("Please ensure gcloud is authenticated and try again.")

        # 6. Check if the service account has the correct WIF provider attribute
        try:
            st.info("6. Checking if service account has the correct WIF provider attribute...")
            result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'describe', service_account_email,
                                   '--format', 'value(wifConfig.workloadIdentityPoolProvider)'], 
                                   capture_output=True, text=True, check=True)
            wif_provider_from_sa = result.stdout.strip()
            if wif_provider_from_sa == wif_provider_name:
                st.success(f"✅ Service account '{service_account_email}' has the correct WIF provider attribute.")
            else:
                st.error(f"❌ Service account '{service_account_email}' has WIF provider attribute: `{wif_provider_from_sa}`")
                st.info(f"Expected: `{wif_provider_name}`")
                st.info("Please ensure the service account is linked to the correct WIF provider.")
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Could not check WIF provider attribute for service account: {e}")
            st.info("Please ensure gcloud is authenticated and try again.")

        st.info("💡 **Troubleshooting Tips:**")
        st.markdown("""
        - **WIF Pool/Provider Not Found**: Ensure you have 'Workload Identity Pool Admin' and 'Workload Identity Pool Viewer' roles.
        - **IAM API Not Enabled**: Ensure you have 'Service Account Admin' role and run `gcloud services enable iam.googleapis.com`.
        - **Service Account Missing**: Ensure you have 'Service Account Admin' role and run `gcloud iam service-accounts create`.
        - **Roles Missing**: Ensure you have 'Workload Identity Pool Admin', 'Workload Identity Pool Viewer', and 'Service Account Admin' roles.
        - **Attribute Mismatch**: Ensure the WIF provider attribute in the service account matches the one in the WIF provider.
        """)

    def test_wif_configuration(self, project_id: str, service_account: str, wif_pool: str, wif_provider: str) -> bool:
        """Test if the WIF configuration is correctly set up in GitHub."""
        try:
            st.info("🧪 Testing Workload Identity Federation configuration...")
            
            # Get the full WIF provider resource name
            wif_provider_full_name = f"projects/{project_id}/locations/global/workloadIdentityPools/{wif_pool}/providers/{wif_provider}"
            
            # Check if the WIF provider attribute is correctly set in the service account
            try:
                st.info(f"🔍 Checking if service account '{service_account}' has the WIF provider attribute...")
                result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'describe', service_account,
                                       '--format', 'value(wifConfig.workloadIdentityPoolProvider)'], 
                                       capture_output=True, text=True, check=True)
                wif_provider_from_sa = result.stdout.strip()
                if wif_provider_from_sa == wif_provider_full_name:
                    st.success(f"✅ Service account '{service_account}' has the correct WIF provider attribute: `{wif_provider_from_sa}`")
                else:
                    st.error(f"❌ Service account '{service_account}' has WIF provider attribute: `{wif_provider_from_sa}`")
                    st.info(f"Expected: `{wif_provider_full_name}`")
                    st.info("Please ensure the service account is linked to the correct WIF provider.")
                    return False
            except subprocess.CalledProcessError as e:
                st.error(f"❌ Could not check WIF provider attribute for service account: {e}")
                st.info("Please ensure gcloud is authenticated and try again.")
                return False

            # Check if the service account has the necessary IAM roles
            try:
                st.info(f"🔍 Checking if current user has necessary IAM roles for Workload Identity Federation...")
                current_user = subprocess.run(['gcloud', 'config', 'get-value', 'account'], 
                                             capture_output=True, text=True, check=True).stdout.strip()
                
                if not current_user:
                    st.warning("⚠️ Could not determine current user. Please ensure gcloud is authenticated.")
                    st.info("Run `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`")
                    return False

                st.info(f"👤 Current user: {current_user}")

                # Define roles to check
                roles_to_check = [
                    'roles/iam.workloadIdentityPoolAdmin',
                    'roles/iam.workloadIdentityPoolViewer',
                    'roles/iam.serviceAccountAdmin'
                ]

                missing_roles = []
                for role in roles_to_check:
                    try:
                        result = subprocess.run(['gcloud', 'projects', 'get-iam-policy', project_id,
                                               '--flatten', 'bindings[].role',
                                               '--format', 'value(bindings.role)',
                                               '--filter', f'bindings.members:{current_user}'], 
                                           capture_output=True, text=True, check=True)
                        if role not in result.stdout:
                            missing_roles.append(role)
                    except subprocess.CalledProcessError as e:
                        st.warning(f"⚠️ Could not check role '{role}' for current user: {e}")
                        st.info("Please ensure you have the role or are a project owner.")

                if missing_roles:
                    st.error("❌ Missing necessary IAM roles for Workload Identity Federation:")
                    for role in missing_roles:
                        st.error(f"   • {role}")
                    st.info("You might need to manually grant these roles to your user or the service account.")
                    return False
                else:
                    st.success("✅ Current user has all required IAM roles.")
            except subprocess.CalledProcessError as e:
                st.error(f"❌ Could not check IAM roles: {e}")
                st.info("Please ensure gcloud is authenticated and try again.")
                return False

            st.success("🎉 Workload Identity Federation configuration test passed!")
            return True

        except Exception as e:
            st.error(f"❌ Workload Identity Federation configuration test failed: {e}")
            return False

    def check_existing_github_secrets(self, repo_owner: str, repo_name: str) -> Dict[str, bool]:
        """Check which GitHub secrets already exist"""
        try:
            st.info(f"🔍 Checking existing secrets for {repo_owner}/{repo_name}...")
            
            # Try to list secrets
            result = subprocess.run(['gh', 'secret', 'list', '--repo', f'{repo_owner}/{repo_name}'], 
                                  capture_output=True, text=True, check=False)
            
            existing_secrets = {}
            required_secrets = ['GCP_WORKLOAD_IDENTITY_PROVIDER', 'GCP_SERVICE_ACCOUNT_EMAIL', 'GCP_PROJECT_ID']
            
            if result.returncode == 0:
                # Successfully got secrets list
                for secret in required_secrets:
                    existing_secrets[secret] = secret in result.stdout
                st.success(f"✅ Found {len([s for s in existing_secrets.values() if s])} existing secrets")
            else:
                # Failed to get secrets list, assume none exist
                st.warning(f"⚠️ Could not check existing secrets (exit code: {result.returncode})")
                st.info("Assuming no secrets are configured yet")
                for secret in required_secrets:
                    existing_secrets[secret] = False
            
            return existing_secrets
            
        except Exception as e:
            st.warning(f"⚠️ Error checking secrets: {e}")
            st.info("Assuming no secrets are configured yet")
            return {
                'GCP_WORKLOAD_IDENTITY_PROVIDER': False,
                'GCP_SERVICE_ACCOUNT_EMAIL': False,
                'GCP_PROJECT_ID': False
            }

    def update_github_secret(self, secret_name: str, secret_value: str, repo_owner: str, repo_name: str) -> bool:
        """Update an existing GitHub secret"""
        try:
            st.info(f"🔄 Updating secret `{secret_name}`...")
            result = subprocess.run(['gh', 'secret', 'set', secret_name, '--repo', f'{repo_owner}/{repo_name}', '--body', secret_value], 
                                  capture_output=True, text=True, check=True)
            st.success(f"✅ Secret `{secret_name}` updated successfully.")
            return True
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Failed to update secret `{secret_name}`: {e.stderr}")
            return False
        except Exception as e:
            st.error(f"❌ Error updating secret `{secret_name}`: {e}")
            return False

    def configure_github_secrets_automatically(self, secrets_to_configure: Dict[str, str], repo_owner: str, repo_name: str) -> bool:
        """Configures secrets for a GitHub repository using gh cli."""
        try:
            st.info(f"🚀 Attempting to configure secrets for {repo_owner}/{repo_name}...")
            
            # Check if gh cli is authenticated
            try:
                result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, check=True)
                if 'Logged in to github.com' not in result.stdout:
                    st.error("❌ GitHub CLI is not authenticated. Please run `gh auth login`.")
                    return False
                st.success("✅ GitHub CLI is authenticated.")
            except subprocess.CalledProcessError:
                st.error("❌ GitHub CLI not authenticated. Please run `gh auth login`.")
                return False
            except FileNotFoundError:
                st.error("❌ GitHub CLI not installed. Please install GitHub CLI first.")
                return False
            
            # Check if in a git repository
            try:
                result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], capture_output=True, text=True, check=True)
                if result.stdout.strip() != "true":
                    st.error("❌ Not in a git repository. Please run `git init` and `git add .` first.")
                    return False
                st.success("✅ In a git repository.")
            except subprocess.CalledProcessError:
                st.error("❌ Not in a git repository. Please run `git init` and `git add .` first.")
                return False
            
            # Check if secrets already exist and configure/update them
            for secret_name, secret_value in secrets_to_configure.items():
                try:
                    result = subprocess.run(['gh', 'secret', 'list', '--repo', f'{repo_owner}/{repo_name}'], capture_output=True, text=True)
                    if secret_name in result.stdout:
                        st.info(f"🔄 Secret `{secret_name}` already exists. Updating with new value...")
                        if not self.update_github_secret(secret_name, secret_value, repo_owner, repo_name):
                            return False
                    else:
                        st.info(f"🔐 Configuring new secret `{secret_name}`...")
                        result = subprocess.run(['gh', 'secret', 'set', secret_name, '--repo', f'{repo_owner}/{repo_name}', '--body', secret_value], capture_output=True, text=True, check=True)
                        st.success(f"✅ Secret `{secret_name}` configured successfully.")
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Failed to configure secret `{secret_name}`: {e.stderr}")
                    return False
            
            st.success(f"🎉 All secrets for {repo_owner}/{repo_name} configured successfully!")
            return True
        except Exception as e:
            st.error(f"❌ Failed to configure GitHub secrets automatically: {e}")
            return False

    def check_pipeline_status(self, repo_owner: str, repo_name: str) -> Dict[str, any]:
        """Check the status of the latest GitHub Actions workflow run"""
        try:
            # Get the latest workflow run
            result = subprocess.run(['gh', 'run', 'list', '--repo', f'{repo_owner}/{repo_name}', '--limit', '1', '--json', 'status,conclusion,url,createdAt'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                return {'status': 'no_runs', 'message': 'No workflow runs found'}
            
            run_info = json.loads(result.stdout)
            if not run_info:
                return {'status': 'no_runs', 'message': 'No workflow runs found'}
            
            latest_run = run_info[0]
            return {
                'status': latest_run.get('status', 'unknown'),
                'conclusion': latest_run.get('conclusion'),
                'url': latest_run.get('url'),
                'created_at': latest_run.get('createdAt'),
                'message': f"Latest run: {latest_run.get('status', 'unknown')}"
            }
            
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'message': f'Failed to check pipeline: {e}'}
        except Exception as e:
            return {'status': 'error', 'message': f'Error: {e}'}

    def show_pipeline_status(self, repo_owner: str, repo_name: str):
        """Show current pipeline status with refresh capability"""
        st.markdown("### 📊 Pipeline Status")
        
        if st.button("🔄 Refresh Pipeline Status"):
            st.rerun()
        
        # Check current status
        pipeline_info = self.check_pipeline_status(repo_owner, repo_name)
        
        if pipeline_info['status'] == 'completed':
            if pipeline_info['conclusion'] == 'success':
                st.success("✅ Pipeline completed successfully!")
                st.info(f"🔗 [View Details]({pipeline_info['url']})")
            else:
                st.error(f"❌ Pipeline failed: {pipeline_info['conclusion']}")
                st.info(f"🔗 [View Details]({pipeline_info['url']})")
        elif pipeline_info['status'] == 'in_progress':
            st.info("🔄 Pipeline is currently running...")
            st.info(f"🔗 [View Progress]({pipeline_info['url']})")
        elif pipeline_info['status'] == 'queued':
            st.info("⏳ Pipeline is queued and waiting to start...")
            st.info(f"🔗 [View Details]({pipeline_info['url']})")
        elif pipeline_info['status'] == 'no_runs':
            st.warning("⚠️ No pipeline runs found yet")
            st.info("Push some code to trigger the pipeline!")
        else:
            st.warning(f"⚠️ Pipeline status: {pipeline_info['message']}")
        
        # Show GitHub Actions link
        st.markdown(f"🔗 **GitHub Actions**: [View All Workflows](https://github.com/{repo_owner}/{repo_name}/actions)")

    def push_code_and_trigger_pipeline(self) -> bool:
        """Push code to GitHub and trigger CI/CD pipeline"""
        try:
            st.info("🚀 Setting up CI/CD pipeline and pushing code...")
            
            # First, generate and setup the pipeline
            if not self.setup_pipeline():
                st.error("❌ Failed to setup CI/CD pipeline")
                return False
            
            st.success("✅ CI/CD pipeline generated successfully!")
            
            # Now push the updated codebase
            st.info("📤 Pushing updated codebase to GitHub...")
            
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                 capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                st.info("ℹ️ No changes to commit - adding CI/CD files...")
                # Force add CI/CD files even if no changes
                subprocess.run(['git', 'add', '.github/', 'Dockerfile'], check=True)
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
            st.info(f"📊 Monitor progress: https://github.com/PramodChandrayan/neurochatagent/actions")
            
            # Update state
            self.update_state(pipeline_complete=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            st.error(f"❌ Git operation failed: {e}")
            return False
        except Exception as e:
            st.error(f"❌ Failed to push code: {e}")
            return False

    def create_cicd_files(self) -> bool:
        """Create all necessary CI/CD pipeline files"""
        try:
            st.info("📋 Creating CI/CD pipeline files...")
            
            # Get current state
            project_id = st.session_state.get('gcp_project')
            service_account = st.session_state.get('service_account_email')
            wif_pool = st.session_state.get('workload_identity_pool')
            wif_provider = st.session_state.get('workload_identity_provider')
            
            # Let user choose YAML type
            st.markdown("### 🎯 Choose CI/CD Pipeline Type")
            yaml_type = st.selectbox(
                "Select pipeline complexity:",
                ["comprehensive", "simple"],
                format_func=lambda x: "🚀 Comprehensive (Full CI/CD with testing, security, staging)" if x == "comprehensive" else "⚡ Simple (Basic build and deploy)",
                help="Comprehensive includes code quality, testing, security scanning, staging deployment, and production deployment. Simple is just build and deploy."
            )
            
            if st.button("📋 Generate Selected CI/CD Pipeline"):
                # 1. Create .github/workflows directory
                os.makedirs(".github/workflows", exist_ok=True)
                
                # 2. Generate CI/CD YAML
                st.info(f"📝 Generating {yaml_type} CI/CD pipeline configuration...")
                cicd_yaml = self.generate_cicd_yaml(project_id, service_account, wif_pool, wif_provider, yaml_type)
                
                if not cicd_yaml:
                    st.error("❌ Failed to generate CI/CD configuration")
                    return False
                
                # Write YAML to file
                yaml_file = ".github/workflows/deploy.yml"
                with open(yaml_file, 'w') as f:
                    f.write(cicd_yaml)
                
                st.success(f"✅ Generated {yaml_file} ({yaml_type})")
                
                # Show what was generated
                if yaml_type == "comprehensive":
                    st.info("🚀 **Comprehensive Pipeline Includes:**")
                    st.info("• Code Quality (flake8, black, isort)")
                    st.info("• Security Scanning (bandit, safety, Trivy)")
                    st.info("• Testing with Coverage")
                    st.info("• Staging Deployment (PRs)")
                    st.info("• Production Deployment (main/master)")
                    st.info("• Post-deployment Reporting")
                else:
                    st.info("⚡ **Simple Pipeline Includes:**")
                    st.info("• Basic Build & Push")
                    st.info("• Direct Production Deployment")
                
                # 3. Generate Dockerfile
                st.info("🐳 Generating Dockerfile...")
                dockerfile_content = self.generate_dockerfile()
                if dockerfile_content:
                    with open("Dockerfile", 'w') as f:
                        f.write(dockerfile_content)
                    st.success("✅ Generated Dockerfile")
                else:
                    st.warning("⚠️ Could not generate Dockerfile")
                
                # 4. Ensure requirements.txt exists
                if not os.path.exists("requirements.txt"):
                    st.info("📦 Creating requirements.txt...")
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
            error_msg = f"Failed to create CI/CD files: {e}"
            self.add_error(error_msg)
            st.error(f"❌ {error_msg}")
            return False

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

    def extract_and_configure_secrets_automatically(self, repo_owner: str, repo_name: str) -> bool:
        """Smart method: Extract exact secret values from infrastructure and configure them in GitHub"""
        try:
            st.info("🧠 Smart Secret Extraction & Configuration...")
            
            # Get current infrastructure state
            project_id = st.session_state.get('gcp_project')
            service_account = st.session_state.get('service_account_email')
            wif_pool = st.session_state.get('workload_identity_pool')
            wif_provider = st.session_state.get('workload_identity_provider')
            
            if not all([project_id, service_account, wif_pool, wif_provider]):
                st.error("❌ Missing infrastructure configuration")
                return False
            
            # Extract exact values from GCP
            st.info("🔍 Extracting exact secret values from GCP...")
            
            # 1. Get full WIF provider resource name
            try:
                result = subprocess.run(['gcloud', 'iam', 'workload-identity-pools', 'providers', 'describe', 
                                       wif_provider, '--workload-identity-pool', wif_pool, '--location', 'global', 
                                       '--format', 'value(name)'], capture_output=True, text=True, check=True)
                wif_provider_full_name = result.stdout.strip()
                st.success(f"✅ WIF Provider: {wif_provider_full_name}")
            except Exception as e:
                st.error(f"❌ Failed to get WIF provider: {e}")
                return False
            
            # 2. Verify service account exists
            try:
                result = subprocess.run(['gcloud', 'iam', 'service-accounts', 'describe', service_account, 
                                       '--format', 'value(email)'], capture_output=True, text=True, check=True)
                service_account_email = result.stdout.strip()
                st.success(f"✅ Service Account: {service_account_email}")
            except Exception as e:
                st.error(f"❌ Failed to get service account: {e}")
                return False
            
            # 3. Verify project ID
            try:
                result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                       capture_output=True, text=True, check=True)
                gcp_project_id = result.stdout.strip()
                st.success(f"✅ GCP Project: {gcp_project_id}")
            except Exception as e:
                st.error(f"❌ Failed to get project ID: {e}")
                return False
            
            # Define the exact secrets to configure
            secrets_to_configure = {
                'GCP_WORKLOAD_IDENTITY_PROVIDER': wif_provider_full_name,
                'GCP_SERVICE_ACCOUNT_EMAIL': service_account_email,
                'GCP_PROJECT_ID': gcp_project_id
            }
            
            st.success("🎯 Extracted all required secret values!")
            
            # Check what already exists in GitHub
            st.info("🔍 Checking existing GitHub secrets...")
            try:
                result = subprocess.run(['gh', 'secret', 'list', '--repo', f'{repo_owner}/{repo_name}'], 
                                      capture_output=True, text=True, check=True)
                existing_secrets = result.stdout
                
                # Check each secret
                for secret_name, secret_value in secrets_to_configure.items():
                    if secret_name in existing_secrets:
                        st.info(f"✅ {secret_name} already exists")
                    else:
                        st.info(f"❌ {secret_name} needs to be configured")
                        
            except Exception as e:
                st.warning(f"⚠️ Could not check existing secrets: {e}")
                st.info("Proceeding with secret configuration...")
            
            # Now configure all secrets (create or update)
            st.info("🚀 Configuring GitHub secrets...")
            success_count = 0
            
            for secret_name, secret_value in secrets_to_configure.items():
                try:
                    st.info(f"🔐 Setting {secret_name}...")
                    result = subprocess.run(['gh', 'secret', 'set', secret_name, '--repo', 
                                           f'{repo_owner}/{repo_name}', '--body', secret_value], 
                                          capture_output=True, text=True, check=True)
                    st.success(f"✅ {secret_name} configured successfully!")
                    success_count += 1
                except subprocess.CalledProcessError as e:
                    st.error(f"❌ Failed to configure {secret_name}: {e.stderr}")
                    return False
                except Exception as e:
                    st.error(f"❌ Error configuring {secret_name}: {e}")
                    return False
            
            if success_count == len(secrets_to_configure):
                st.success(f"🎉 All {success_count} secrets configured successfully!")
                return True
            else:
                st.error(f"❌ Only {success_count}/{len(secrets_to_configure)} secrets configured")
                return False
                
        except Exception as e:
            st.error(f"❌ Smart secret configuration failed: {e}")
            return False

if __name__ == "__main__":
    toolbox = SimpleToolbox()
    toolbox.run()
