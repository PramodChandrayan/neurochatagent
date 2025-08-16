#!/usr/bin/env python3
"""
🏗️ Infrastructure Manager
Manages GCP infrastructure setup with proper state management
"""

import subprocess
import time
import re
from typing import Dict, List, Optional, Tuple, Any
from state_manager import StateManager

class InfrastructureManager:
    """Manages GCP infrastructure setup with proper state flow"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
        self.project_id = None
        self.service_account_email = None
        self.workload_identity_pool = None
        self.workload_identity_provider = None
    
    def setup_infrastructure(self) -> bool:
        """Setup complete GCP infrastructure with proper state management"""
        try:
            print("🏗️ Starting GCP infrastructure setup...")
            
            # Step 1: Get Project ID
            if not self._setup_project_id():
                self.state_manager.set_error("Failed to setup project ID", "infrastructure")
                return False
            
            # Step 2: Setup Service Account
            if not self._setup_service_account():
                self.state_manager.set_error("Failed to setup service account", "infrastructure")
                return False
            
            # Step 3: Enable Required APIs
            if not self._enable_required_apis():
                self.state_manager.set_error("Failed to enable required APIs", "infrastructure")
                return False
            
            # Step 4: Setup Workload Identity Federation
            if not self._setup_workload_identity_federation():
                self.state_manager.set_error("Failed to setup Workload Identity Federation", "infrastructure")
                return False
            
            # Step 5: Configure IAM Permissions
            if not self._configure_iam_permissions():
                self.state_manager.set_error("Failed to configure IAM permissions", "infrastructure")
                return False
            
            # Step 6: Setup Artifact Registry
            if not self._setup_artifact_registry():
                self.state_manager.set_error("Failed to setup Artifact Registry", "infrastructure")
                return False
            
            # Mark infrastructure as complete
            self.state_manager.update_infrastructure_state(setup_complete=True)
            print("🎉 GCP infrastructure setup completed successfully!")
            return True
            
        except Exception as e:
            error_msg = f"Infrastructure setup failed: {str(e)}"
            self.state_manager.set_error(error_msg, "infrastructure")
            print(f"❌ {error_msg}")
            return False
    
    def _setup_project_id(self) -> bool:
        """Setup project ID and store in state"""
        try:
            print("📁 Setting up GCP project ID...")
            
            # Get project ID from CLI
            project_id = self._get_project_id_from_cli()
            if not project_id:
                print("❌ No GCP project ID found")
                return False
            
            # Store in both local state and session state
            self.project_id = project_id
            self.state_manager.update_infrastructure_state(project_id=project_id)
            
            print(f"✅ GCP Project ID: {project_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup project ID: {e}")
            return False
    
    def _setup_service_account(self) -> bool:
        """Setup service account and store in state"""
        try:
            print("👤 Setting up CI/CD service account...")
            
            if not self.project_id:
                print("❌ Project ID not available")
                return False
            
            service_account_email = f"cicd-service-account@{self.project_id}.iam.gserviceaccount.com"
            
            # Check if service account exists
            if self._check_service_account_exists(service_account_email):
                print(f"✅ Service account already exists: {service_account_email}")
            else:
                # Create service account
                print(f"🏗️ Creating service account: {service_account_email}")
                if not self._create_service_account(service_account_email):
                    return False
            
            # Store in both local state and session state
            self.service_account_email = service_account_email
            self.state_manager.update_infrastructure_state(service_account_email=service_account_email)
            
            print(f"✅ Service account configured: {service_account_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup service account: {e}")
            return False
    
    def _enable_required_apis(self) -> bool:
        """Enable required GCP APIs and store status in state"""
        try:
            print("🔌 Enabling required GCP APIs...")
            
            required_apis = [
                'cloudrun.googleapis.com',
                'iam.googleapis.com',
                'artifactregistry.googleapis.com',
                'cloudbuild.googleapis.com'
            ]
            
            enabled_apis = []
            
            for api in required_apis:
                try:
                    if self._check_api_enabled(api):
                        print(f"✅ {api}: Already enabled")
                        enabled_apis.append(api)
                    else:
                        print(f"🔌 Enabling {api}...")
                        if self._enable_api(api):
                            print(f"✅ {api}: Enabled successfully")
                            enabled_apis.append(api)
                        else:
                            print(f"⚠️ {api}: Failed to enable (may need admin access)")
                except Exception as e:
                    print(f"⚠️ {api}: Error - {e}")
            
            # Store enabled APIs in state
            self.state_manager.update_infrastructure_state(apis_enabled=enabled_apis)
            
            print(f"✅ APIs configured: {len(enabled_apis)}/{len(required_apis)} enabled")
            return True
            
        except Exception as e:
            print(f"❌ Failed to enable APIs: {e}")
            return False
    
    def _setup_workload_identity_federation(self) -> bool:
        """Setup Workload Identity Federation and store in state"""
        try:
            print("🔗 Setting up Workload Identity Federation...")
            
            # Validate prerequisites
            if not self.project_id:
                print("❌ Project ID not available")
                return False
            
            if not self.service_account_email:
                print("❌ Service account not available")
                return False
            
            # Generate unique names
            timestamp = int(time.time())
            pool_name = f"neurogent-pool-{timestamp}"
            provider_name = f"github-actions-{timestamp}"
            
            # Create the pool
            print(f"🏊 Creating WIF pool: {pool_name}")
            if not self._create_wif_pool(pool_name):
                return False
            
            # Create the provider
            print(f"🔌 Creating WIF provider: {provider_name}")
            if not self._create_wif_provider(pool_name, provider_name):
                return False
            
            # Store in both local state and session state
            self.workload_identity_pool = pool_name
            self.workload_identity_provider = provider_name
            
            self.state_manager.update_infrastructure_state(
                wif_pool=pool_name,
                wif_provider=provider_name
            )
            
            print(f"✅ WIF configured: {pool_name} + {provider_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup WIF: {e}")
            return False
    
    def _configure_iam_permissions(self) -> bool:
        """Configure IAM permissions using stored state"""
        try:
            print("🔐 Configuring IAM permissions...")
            
            # Validate prerequisites from state
            if not self.project_id:
                print("❌ Project ID not available")
                return False
            
            if not self.service_account_email:
                print("❌ Service account not available")
                return False
            
            if not self.workload_identity_pool:
                print("❌ WIF pool not available")
                return False
            
            if not self.workload_identity_provider:
                print("❌ WIF provider not available")
                return False
            
            # Add IAM roles to service account
            required_roles = [
                'roles/run.admin',
                'roles/iam.serviceAccountUser',
                'roles/artifactregistry.writer',
                'roles/storage.admin',
                'roles/cloudbuild.builds.builder'
            ]
            
            for role in required_roles:
                print(f"🔑 Adding role: {role}")
                if not self._add_iam_role(role):
                    print(f"⚠️ Failed to add role: {role}")
            
            # Configure workload identity binding
            print("🔗 Configuring workload identity binding...")
            if not self._configure_workload_identity_binding():
                return False
            
            # Mark IAM as configured
            self.state_manager.update_infrastructure_state(iam_configured=True)
            
            print("✅ IAM permissions configured successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to configure IAM: {e}")
            return False
    
    def _setup_artifact_registry(self) -> bool:
        """Setup Artifact Registry and store in state"""
        try:
            print("🐳 Setting up Artifact Registry...")
            
            if not self.project_id:
                print("❌ Project ID not available")
                return False
            
            repository_name = "neurogent-repo"
            location = "us-central1"
            
            # Check if repository exists
            if self._check_artifact_registry_exists(repository_name, location):
                print(f"✅ Artifact Registry already exists: {repository_name}")
            else:
                # Create repository
                print(f"🏗️ Creating Artifact Registry: {repository_name}")
                if not self._create_artifact_registry(repository_name, location):
                    return False
            
            # Store in state
            self.state_manager.update_infrastructure_state(artifact_registry=repository_name)
            
            print(f"✅ Artifact Registry configured: {repository_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup Artifact Registry: {e}")
            return False
    
    # Helper methods
    def _get_project_id_from_cli(self) -> Optional[str]:
        """Get project ID using CLI commands"""
        try:
            # Try multiple methods
            methods = [
                ['gcloud', 'config', 'get-value', 'project'],
                ['gcloud', 'config', 'list', '--format', 'value(core.project)'],
                ['gcloud', 'projects', 'list', '--format', 'value(projectId)', '--limit', '1']
            ]
            
            for method in methods:
                try:
                    result = subprocess.run(method, capture_output=True, text=True, check=True)
                    project_id = result.stdout.strip()
                    if project_id:
                        return project_id
                except:
                    continue
            
            return None
        except:
            return None
    
    def _check_service_account_exists(self, email: str) -> bool:
        """Check if service account exists"""
        try:
            subprocess.run(['gcloud', 'iam', 'service-accounts', 'describe', email], 
                         capture_output=True, text=True, check=True)
            return True
        except:
            return False
    
    def _create_service_account(self, email: str) -> bool:
        """Create service account"""
        try:
            name = email.split('@')[0]
            subprocess.run([
                'gcloud', 'iam', 'service-accounts', 'create', name,
                '--display-name', 'CI/CD Service Account',
                '--description', 'Service account for CI/CD pipeline automation'
            ], capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            if "already exists" in e.stderr or "conflict" in e.stderr:
                return True  # Already exists
            return False
    
    def _check_api_enabled(self, api: str) -> bool:
        """Check if specific API is enabled"""
        try:
            result = subprocess.run(['gcloud', 'services', 'list', '--enabled', '--filter', f'name={api}'], 
                                  capture_output=True, text=True, check=True)
            return api in result.stdout
        except:
            return False
    
    def _enable_api(self, api: str) -> bool:
        """Enable specific API"""
        try:
            subprocess.run(['gcloud', 'services', 'enable', api], 
                         capture_output=True, text=True, check=True)
            return True
        except:
            return False
    
    def _create_wif_pool(self, pool_name: str) -> bool:
        """Create WIF pool"""
        try:
            subprocess.run([
                'gcloud', 'iam', 'workload-identity-pools', 'create', pool_name,
                '--location', 'global',
                '--display-name', 'NeuroGent GitHub Actions Pool',
                '--description', 'Workload Identity Pool for NeuroGent CI/CD'
            ], capture_output=True, text=True, check=True)
            return True
        except:
            return False
    
    def _create_wif_provider(self, pool_name: str, provider_name: str) -> bool:
        """Create WIF provider"""
        try:
            subprocess.run([
                'gcloud', 'iam', 'workload-identity-pools', 'providers', 'create-oidc', provider_name,
                '--workload-identity-pool', pool_name,
                '--location', 'global',
                '--issuer-uri', 'https://token.actions.githubusercontent.com',
                '--attribute-mapping', 'google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository',
                '--attribute-condition', 'assertion.repository=="PramodChandrayan/neurochatagent"'
            ], capture_output=True, text=True, check=True)
            return True
        except:
            return False
    
    def _add_iam_role(self, role: str) -> bool:
        """Add IAM role to service account"""
        try:
            subprocess.run([
                'gcloud', 'projects', 'add-iam-policy-binding', self.project_id,
                '--member', f'serviceAccount:{self.service_account_email}',
                '--role', role
            ], capture_output=True, text=True, check=True)
            return True
        except:
            return False
    
    def _configure_workload_identity_binding(self) -> bool:
        """Configure workload identity binding"""
        try:
            subprocess.run([
                'gcloud', 'iam', 'service-accounts', 'add-iam-policy-binding', self.service_account_email,
                '--role', 'roles/iam.workloadIdentityUser',
                '--member', f'principalSet://iam.googleapis.com/projects/{self.project_id}/locations/global/workloadIdentityPools/{self.workload_identity_pool}/attribute.repository/PramodChandrayan/neurochatagent'
            ], capture_output=True, text=True, check=True)
            return True
        except:
            return False
    
    def _check_artifact_registry_exists(self, name: str, location: str) -> bool:
        """Check if Artifact Registry exists"""
        try:
            subprocess.run([
                'gcloud', 'artifacts', 'repositories', 'describe', name,
                '--location', location
            ], capture_output=True, text=True, check=True)
            return True
        except:
            return False
    
    def _create_artifact_registry(self, name: str, location: str) -> bool:
        """Create Artifact Registry"""
        try:
            subprocess.run([
                'gcloud', 'artifacts', 'repositories', 'create', name,
                '--repository-format', 'docker',
                '--location', location,
                '--description', 'Docker repository for NeuroGent Finance Assistant'
            ], capture_output=True, text=True, check=True)
            return True
        except:
            return False
    
    def get_infrastructure_summary(self) -> Dict[str, Any]:
        """Get summary of infrastructure setup"""
        return {
            'project_id': self.project_id,
            'service_account_email': self.service_account_email,
            'workload_identity_pool': self.workload_identity_pool,
            'workload_identity_provider': self.workload_identity_provider,
            'setup_complete': self.state_manager.get_infrastructure_state()['setup_complete']
        }
