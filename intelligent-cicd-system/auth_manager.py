#!/usr/bin/env python3
"""
🔐 Authentication Manager
Manages GCP and GitHub authentication with state management
"""

import subprocess
import re
from typing import Dict, Any, Optional
from state_manager import StateManager

class AuthManager:
    """Manages authentication for GCP and GitHub"""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    def authenticate_gcp(self) -> bool:
        """Authenticate with GCP and store state"""
        try:
            print("🔐 Authenticating with GCP...")
            
            # Check if already authenticated
            if self._check_gcp_auth():
                print("✅ GCP already authenticated")
                return True
            
            # Try to get current project
            project_id = self._get_gcp_project()
            if not project_id:
                print("❌ No GCP project found")
                return False
            
            # Update state
            self.state_manager.update_auth_state(
                gcp_authenticated=True,
                gcp_project=project_id
            )
            
            print(f"✅ GCP authenticated successfully - Project: {project_id}")
            return True
            
        except Exception as e:
            print(f"❌ GCP authentication failed: {e}")
            return False
    
    def authenticate_github(self) -> bool:
        """Authenticate with GitHub and store state"""
        try:
            print("🔐 Authenticating with GitHub...")
            
            # Check if already authenticated
            if self._check_github_auth():
                print("✅ GitHub already authenticated")
                return True
            
            # Try to get current user
            username = self._get_github_user()
            if not username:
                print("❌ No GitHub user found")
                return False
            
            # Update state
            self.state_manager.update_auth_state(
                github_authenticated=True,
                github_user=username
            )
            
            print(f"✅ GitHub authenticated successfully - User: {username}")
            return True
            
        except Exception as e:
            print(f"❌ GitHub authentication failed: {e}")
            return False
    
    def get_current_auth_status(self) -> Dict[str, Any]:
        """Get current authentication status without updating state"""
        return {
            'gcp_authenticated': self._check_gcp_auth(),
            'github_authenticated': self._check_github_auth(),
            'gcp_project': self._get_gcp_project() if self._check_gcp_auth() else None,
            'github_user': self._get_github_user() if self._check_github_auth() else None
        }
    
    def check_gcp_auth(self) -> bool:
        """Check if GCP is authenticated (public method)"""
        return self._check_gcp_auth()
    
    def check_github_auth(self) -> bool:
        """Check if GitHub is authenticated (public method)"""
        return self._check_github_auth()
    
    def _check_gcp_auth(self) -> bool:
        """Check if GCP is authenticated"""
        try:
            result = subprocess.run(['gcloud', 'auth', 'list'], 
                                 capture_output=True, text=True, check=True)
            return 'ACTIVE' in result.stdout
        except:
            return False
    
    def _check_github_auth(self) -> bool:
        """Check if GitHub is authenticated"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                 capture_output=True, text=True, check=True)
            return 'Logged in to github.com' in result.stdout
        except:
            return False
    
    def _get_gcp_project(self) -> Optional[str]:
        """Get current GCP project ID"""
        try:
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                 capture_output=True, text=True, check=True)
            project_id = result.stdout.strip()
            return project_id if project_id else None
        except:
            return None
    
    def _get_github_user(self) -> Optional[str]:
        """Get current GitHub username"""
        try:
            result = subprocess.run(['gh', 'auth', 'status'], 
                                 capture_output=True, text=True, check=True)
            
            if 'Logged in to github.com' in result.stdout:
                username_match = re.search(r'as (\w+)', result.stdout)
                return username_match.group(1) if username_match else 'Unknown'
            
            return None
        except:
            return None
    
    def is_gcp_authenticated(self) -> bool:
        """Check if GCP is authenticated (from state)"""
        auth_state = self.state_manager.get_auth_state()
        return auth_state['gcp_authenticated']
    
    def is_github_authenticated(self) -> bool:
        """Check if GitHub is authenticated (from state)"""
        auth_state = self.state_manager.get_auth_state()
        return auth_state['github_authenticated']
    
    def get_gcp_project(self) -> Optional[str]:
        """Get GCP project from state"""
        auth_state = self.state_manager.get_auth_state()
        return auth_state['gcp_project']
    
    def get_github_user(self) -> Optional[str]:
        """Get GitHub user from state"""
        auth_state = self.state_manager.get_auth_state()
        return auth_state['github_user']
