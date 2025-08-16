#!/usr/bin/env python3
"""
🏗️ State Manager
Central state management for the entire CI/CD toolbox workflow
"""

from typing import Dict, Any, Optional
import streamlit as st

class StateManager:
    """Manages state across all phases of the CI/CD setup"""
    
    def __init__(self):
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        # Phase 1: Authentication State
        if 'auth_state' not in st.session_state:
            st.session_state.auth_state = {
                'gcp_authenticated': False,
                'github_authenticated': False,
                'gcp_project': None,
                'github_user': None
            }
        
        # Phase 2: Infrastructure State
        if 'infrastructure_state' not in st.session_state:
            st.session_state.infrastructure_state = {
                'project_id': None,
                'service_account_email': None,
                'apis_enabled': [],
                'wif_pool': None,
                'wif_provider': None,
                'artifact_registry': None,
                'iam_configured': False,
                'setup_complete': False
            }
        
        # Phase 3: Secrets State
        if 'secrets_state' not in st.session_state:
            st.session_state.secrets_state = {
                'github_secrets': {},
                'env_vars': {},
                'secrets_extracted': False
            }
        
        # Phase 4: GitHub Setup State
        if 'github_state' not in st.session_state:
            st.session_state.github_state = {
                'secrets_pushed': False,
                'yaml_generated': False,
                'setup_complete': False
            }
        
        # Phase 5: Pipeline State
        if 'pipeline_state' not in st.session_state:
            st.session_state.pipeline_state = {
                'committed': False,
                'running': False,
                'status': 'pending'
            }
        
        # Current Phase Tracking
        if 'current_phase' not in st.session_state:
            st.session_state.current_phase = 'authentication'
        
        # Error State
        if 'error_state' not in st.session_state:
            st.session_state.error_state = {
                'has_error': False,
                'error_message': '',
                'error_phase': None
            }
    
    def get_auth_state(self) -> Dict[str, Any]:
        """Get current authentication state"""
        return st.session_state.auth_state
    
    def get_infrastructure_state(self) -> Dict[str, Any]:
        """Get current infrastructure state"""
        return st.session_state.infrastructure_state
    
    def get_secrets_state(self) -> Dict[str, Any]:
        """Get current secrets state"""
        return st.session_state.secrets_state
    
    def get_github_state(self) -> Dict[str, Any]:
        """Get current GitHub setup state"""
        return st.session_state.github_state
    
    def get_pipeline_state(self) -> Dict[str, Any]:
        """Get current pipeline state"""
        return st.session_state.pipeline_state
    
    def update_auth_state(self, **kwargs):
        """Update authentication state"""
        for key, value in kwargs.items():
            if key in st.session_state.auth_state:
                st.session_state.auth_state[key] = value
    
    def update_infrastructure_state(self, **kwargs):
        """Update infrastructure state"""
        for key, value in kwargs.items():
            if key in st.session_state.infrastructure_state:
                st.session_state.infrastructure_state[key] = value
    
    def update_secrets_state(self, **kwargs):
        """Update secrets state"""
        for key, value in kwargs.items():
            if key in st.session_state.secrets_state:
                st.session_state.secrets_state[key] = value
    
    def update_github_state(self, **kwargs):
        """Update GitHub setup state"""
        for key, value in kwargs.items():
            if key in st.session_state.github_state:
                st.session_state.github_state[key] = value
    
    def update_pipeline_state(self, **kwargs):
        """Update pipeline state"""
        for key, value in kwargs.items():
            if key in st.session_state.pipeline_state:
                st.session_state.pipeline_state[key] = value
    
    def set_error(self, message: str, phase: str):
        """Set error state"""
        st.session_state.error_state = {
            'has_error': True,
            'error_message': message,
            'error_phase': phase
        }
    
    def clear_error(self):
        """Clear error state"""
        st.session_state.error_state = {
            'has_error': False,
            'error_message': '',
            'error_phase': None
        }
    
    def get_error(self) -> Dict[str, Any]:
        """Get current error state"""
        return st.session_state.error_state
    
    def can_proceed_to_phase(self, target_phase: str) -> bool:
        """Check if we can proceed to a specific phase"""
        if target_phase == 'authentication':
            return True
        
        elif target_phase == 'infrastructure':
            auth = self.get_auth_state()
            return auth['gcp_authenticated'] and auth['github_authenticated']
        
        elif target_phase == 'secrets':
            infra = self.get_infrastructure_state()
            return infra['setup_complete']
        
        elif target_phase == 'github_setup':
            secrets = self.get_secrets_state()
            return secrets['secrets_extracted']
        
        elif target_phase == 'pipeline':
            github = self.get_github_state()
            return github['setup_complete']
        
        return False
    
    def get_phase_status(self) -> Dict[str, str]:
        """Get status of all phases"""
        return {
            'authentication': '✅ Complete' if self.get_auth_state()['gcp_authenticated'] and self.get_auth_state()['github_authenticated'] else '⏳ Pending',
            'infrastructure': '✅ Complete' if self.get_infrastructure_state()['setup_complete'] else '⏳ Pending',
            'secrets': '✅ Complete' if self.get_secrets_state()['secrets_extracted'] else '⏳ Pending',
            'github_setup': '✅ Complete' if self.get_github_state()['setup_complete'] else '⏳ Pending',
            'pipeline': '✅ Complete' if self.get_pipeline_state()['status'] == 'success' else '⏳ Pending'
        }
    
    def reset_to_phase(self, phase: str):
        """Reset state to a specific phase"""
        if phase == 'authentication':
            # Keep only auth state, reset everything else
            auth_state = st.session_state.auth_state
            self.initialize_session_state()
            st.session_state.auth_state = auth_state
            st.session_state.current_phase = 'authentication'
        
        elif phase == 'infrastructure':
            # Keep auth and infra state, reset everything else
            auth_state = st.session_state.auth_state
            infra_state = st.session_state.infrastructure_state
            self.initialize_session_state()
            st.session_state.auth_state = auth_state
            st.session_state.infrastructure_state = infra_state
            st.session_state.current_phase = 'infrastructure'
        
        # Add more phase resets as needed
    
    def get_overall_progress(self) -> Dict[str, Any]:
        """Get overall progress across all phases"""
        total_steps = 5
        completed_steps = 0
        
        if self.get_auth_state()['gcp_authenticated'] and self.get_auth_state()['github_authenticated']:
            completed_steps += 1
        
        if self.get_infrastructure_state()['setup_complete']:
            completed_steps += 1
        
        if self.get_secrets_state()['secrets_extracted']:
            completed_steps += 1
        
        if self.get_github_state()['setup_complete']:
            completed_steps += 1
        
        if self.get_pipeline_state()['status'] == 'success':
            completed_steps += 1
        
        progress_percentage = (completed_steps / total_steps) * 100
        
        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'progress_percentage': progress_percentage,
            'current_phase': st.session_state.current_phase
        }
