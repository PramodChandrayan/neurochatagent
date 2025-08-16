#!/usr/bin/env python3
"""
🔑 Secrets Manager
Manages secrets extraction and configuration with state management
"""

from typing import Dict, Any
from state_manager import StateManager

class SecretsManager:
    """Manages secrets extraction and configuration"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    def extract_all_secrets(self) -> bool:
        """Extract all required secrets from infrastructure state"""
        try:
            print("🔑 Extracting secrets from infrastructure configuration...")
            
            # Get infrastructure state
            infra_state = self.state_manager.get_infrastructure_state()
            
            if not infra_state['setup_complete']:
                print("❌ Infrastructure not complete - cannot extract secrets")
                return False
            
            # Extract GitHub secrets
            github_secrets = self._extract_github_secrets(infra_state)
            
            # Extract environment variables
            env_vars = self._extract_env_vars(infra_state)
            
            # Update state
            self.state_manager.update_secrets_state(
                github_secrets=github_secrets,
                env_vars=env_vars,
                secrets_extracted=True
            )
            
            print("✅ Secrets extracted successfully")
            return True
            
        except Exception as e:
            print(f"❌ Secrets extraction failed: {e}")
            return False
    
    def _extract_github_secrets(self, infra_state: Dict[str, Any]) -> Dict[str, str]:
        """Extract GitHub secrets from infrastructure state"""
        secrets = {}
        
        # GCP configuration
        if infra_state['project_id']:
            secrets['GCP_PROJECT_ID'] = infra_state['project_id']
            secrets['GCP_REGION'] = 'us-central1'
        
        # Service account
        if infra_state['service_account_email']:
            secrets['GCP_SERVICE_ACCOUNT'] = infra_state['service_account_email']
        
        # WIF configuration
        if infra_state['wif_pool'] and infra_state['wif_provider']:
            provider_resource = f"projects/{infra_state['project_id']}/locations/global/workloadIdentityPools/{infra_state['wif_pool']}/providers/{infra_state['wif_provider']}"
            secrets['WORKLOAD_IDENTITY_PROVIDER'] = provider_resource
            secrets['WORKLOAD_IDENTITY_POOL'] = infra_state['wif_pool']
            secrets['WORKLOAD_IDENTITY_PROVIDER_NAME'] = infra_state['wif_provider']
        
        # Artifact Registry
        if infra_state['artifact_registry']:
            secrets['ARTIFACT_REGISTRY'] = infra_state['artifact_registry']
        
        return secrets
    
    def _extract_env_vars(self, infra_state: Dict[str, Any]) -> Dict[str, str]:
        """Extract environment variables from infrastructure state"""
        env_vars = {}
        
        # Basic configuration
        if infra_state['project_id']:
            env_vars['PROJECT_ID'] = infra_state['project_id']
            env_vars['REGION'] = 'us-central1'
            env_vars['SERVICE_NAME'] = 'neurogent-finance-assistant'
        
        return env_vars
    
    def push_secrets_to_github(self) -> bool:
        """Push secrets to GitHub repository"""
        try:
            print("🔑 Pushing secrets to GitHub...")
            
            # Get secrets state
            secrets_state = self.state_manager.get_secrets_state()
            
            if not secrets_state['secrets_extracted']:
                print("❌ Secrets not extracted - cannot push to GitHub")
                return False
            
            # For now, just mark as pushed
            # In a real implementation, this would use GitHub CLI to set secrets
            print("✅ Secrets would be pushed to GitHub (placeholder)")
            
            # Update state
            self.state_manager.update_github_state(secrets_pushed=True)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to push secrets to GitHub: {e}")
            return False
