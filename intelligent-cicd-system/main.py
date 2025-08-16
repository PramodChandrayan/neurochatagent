#!/usr/bin/env python3
"""
🚀 Intelligent CI/CD System
Main application with clean architecture and proper state management
"""

import streamlit as st
from state_manager import StateManager
from infrastructure_manager import InfrastructureManager
from auth_manager import AuthManager
from secrets_manager import SecretsManager
from pipeline_generator import PipelineGenerator

class IntelligentCICDSystem:
    """Main CI/CD system with clean architecture"""
    
    def __init__(self):
        # Initialize state manager first
        self.state_manager = StateManager()
        
        # Initialize other managers with state manager
        self.auth_manager = AuthManager(self.state_manager)
        self.infrastructure_manager = InfrastructureManager(self.state_manager)
        self.secrets_manager = SecretsManager(self.state_manager)
        self.pipeline_generator = PipelineGenerator(self.state_manager)
        
        # Project configuration
        self.project_name = "neurogent-finance-assistant"
        self.target_service = "Cloud Run"
        self.deployment_region = "us-central1"
    
    def run(self):
        """Main application entry point"""
        st.set_page_config(
            page_title="🚀 Intelligent CI/CD System",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Setup custom CSS
        self._setup_custom_css()
        
        # Main header
        st.markdown("""
        <div class="main-header">
            <h1>🚀 Intelligent CI/CD System</h1>
            <p>Automated Cloud Run Deployment for NeuroGent Finance Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show overall progress
        self._show_overall_progress()
        
        # Show current phase
        self._show_current_phase()
        
        # Show error if any
        self._show_error_state()
        
        # Main content based on current phase
        current_phase = self.state_manager.get_overall_progress()['current_phase']
        
        if current_phase == 'authentication':
            self._show_authentication_phase()
        elif current_phase == 'infrastructure':
            self._show_infrastructure_phase()
        elif current_phase == 'secrets':
            self._show_secrets_phase()
        elif current_phase == 'github_setup':
            self._show_github_setup_phase()
        elif current_phase == 'pipeline':
            self._show_pipeline_phase()
        else:
            self._show_authentication_phase()  # Default to authentication
    
    def _setup_custom_css(self):
        """Setup custom CSS styling"""
        st.markdown("""
        <style>
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .phase-box {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid #007bff;
        }
        
        .phase-box.complete {
            border-left-color: #28a745;
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        }
        
        .phase-box.current {
            border-left-color: #ffc107;
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        }
        
        .phase-box.pending {
            border-left-color: #6c757d;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        .progress-bar {
            background: linear-gradient(90deg, #28a745 0%, #ffc107 50%, #dc3545 100%);
            height: 20px;
            border-radius: 10px;
            margin: 1rem 0;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-success { background-color: #28a745; }
        .status-warning { background-color: #ffc107; }
        .status-error { background-color: #dc3545; }
        .status-info { background-color: #17a2b8; }
        </style>
        """, unsafe_allow_html=True)
    
    def _show_overall_progress(self):
        """Show overall progress across all phases"""
        progress = self.state_manager.get_overall_progress()
        
        st.markdown("## 📊 Overall Progress")
        
        # Progress bar
        st.progress(progress['progress_percentage'] / 100)
        st.markdown(f"**{progress['completed_steps']}/{progress['total_steps']} phases complete ({progress['progress_percentage']:.1f}%)**")
        
        # Phase status
        phase_status = self.state_manager.get_phase_status()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Phase 1: Authentication**")
            st.markdown(phase_status['authentication'])
        
        with col2:
            st.markdown("**Phase 2: Infrastructure**")
            st.markdown(phase_status['infrastructure'])
        
        with col3:
            st.markdown("**Phase 3: Secrets**")
            st.markdown(phase_status['secrets'])
        
        col4, col5 = st.columns(2)
        
        with col4:
            st.markdown("**Phase 4: GitHub Setup**")
            st.markdown(phase_status['github_setup'])
        
        with col5:
            st.markdown("**Phase 5: Pipeline**")
            st.markdown(phase_status['pipeline'])
    
    def _show_current_phase(self):
        """Show current phase information"""
        current_phase = self.state_manager.get_overall_progress()['current_phase']
        
        st.markdown(f"## 🎯 Current Phase: {current_phase.replace('_', ' ').title()}")
        
        if current_phase == 'authentication':
            st.info("🔐 Please authenticate with GCP and GitHub to proceed")
        elif current_phase == 'infrastructure':
            st.info("🏗️ Setting up GCP infrastructure for CI/CD")
        elif current_phase == 'secrets':
            st.info("🔑 Extracting and configuring secrets")
        elif current_phase == 'github_setup':
            st.info("🐙 Setting up GitHub repository and secrets")
        elif current_phase == 'pipeline':
            st.info("🚀 Managing CI/CD pipeline execution")
    
    def _show_error_state(self):
        """Show error state if any"""
        error_state = self.state_manager.get_error()
        
        if error_state['has_error']:
            st.error(f"❌ **Error in {error_state['error_phase']} phase:** {error_state['error_message']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Retry Current Phase"):
                    self.state_manager.clear_error()
                    st.rerun()
            
            with col2:
                if st.button("🔄 Reset to Previous Phase"):
                    # Reset to previous phase
                    if error_state['error_phase'] == 'infrastructure':
                        self.state_manager.reset_to_phase('authentication')
                    elif error_state['error_phase'] == 'secrets':
                        self.state_manager.reset_to_phase('infrastructure')
                    elif error_state['error_phase'] == 'github_setup':
                        self.state_manager.reset_to_phase('secrets')
                    elif error_state['error_phase'] == 'pipeline':
                        self.state_manager.reset_to_phase('github_setup')
                    
                    self.state_manager.clear_error()
                    st.rerun()
    
    def _show_authentication_phase(self):
        """Show authentication phase"""
        st.markdown("### 🔐 Phase 1: Authentication")
        
        # Check current authentication status FIRST (before showing any UI)
        with st.spinner("🔍 Checking current authentication status..."):
            current_auth = self.auth_manager.get_current_auth_status()
            
            # Update state with current status
            if current_auth['gcp_authenticated']:
                self.state_manager.update_auth_state(
                    gcp_authenticated=True,
                    gcp_project=current_auth['gcp_project']
                )
            
            if current_auth['github_authenticated']:
                self.state_manager.update_auth_state(
                    github_authenticated=True,
                    github_user=current_auth['github_user']
                )
        
        # Now get the updated state
        auth_state = self.state_manager.get_auth_state()
        
        # Show current authentication summary FIRST
        st.markdown("**📊 Current Authentication Status:**")
        
        col1, col2 = st.columns(2)
        with col1:
            if auth_state['gcp_authenticated']:
                st.success(f"🌐 GCP: ✅ Authenticated")
                st.info(f"Project: {auth_state['gcp_project']}")
            else:
                st.error("🌐 GCP: ❌ Not Authenticated")
        
        with col2:
            if auth_state['github_authenticated']:
                st.success(f"🐙 GitHub: ✅ Authenticated")
                st.info(f"User: {auth_state['github_user']}")
            else:
                st.error("🐙 GitHub: ❌ Not Authenticated")
        
        # Only show authentication forms if NOT authenticated
        if not auth_state['gcp_authenticated'] or not auth_state['github_authenticated']:
            st.markdown("---")
            st.markdown("**🔐 Authentication Required:**")
            
            # GCP Authentication (only if needed)
            if not auth_state['gcp_authenticated']:
                with st.expander("🌐 Google Cloud Platform Authentication", expanded=True):
                    st.info("Please authenticate with GCP to continue")
                    if st.button("🔐 Authenticate GCP"):
                        with st.spinner("Authenticating with GCP..."):
                            if self.auth_manager.authenticate_gcp():
                                st.success("✅ GCP Authentication successful!")
                                st.rerun()
                            else:
                                st.error("❌ GCP Authentication failed")
            
            # GitHub Authentication (only if needed)
            if not auth_state['github_authenticated']:
                with st.expander("🐙 GitHub Authentication", expanded=True):
                    st.info("Please authenticate with GitHub to continue")
                    if st.button("🔐 Authenticate GitHub"):
                        with st.spinner("Authenticating with GitHub..."):
                            if self.auth_manager.authenticate_github():
                                st.success("✅ GitHub Authentication successful!")
                                st.rerun()
                            else:
                                st.error("❌ GitHub Authentication failed")
        else:
            # Both are authenticated - show success and next step
            st.success("🎉 Authentication complete! Ready to proceed to infrastructure setup.")
            st.info("✅ Both GCP and GitHub are properly authenticated")
        
        # Add refresh button for manual status check
        st.markdown("---")
        if st.button("🔄 Refresh Authentication Status"):
            with st.spinner("🔍 Refreshing authentication status..."):
                current_auth = self.auth_manager.get_current_auth_status()
                
                # Update state with current status
                if current_auth['gcp_authenticated']:
                    self.state_manager.update_auth_state(
                        gcp_authenticated=True,
                        gcp_project=current_auth['gcp_project']
                    )
                
                if current_auth['github_authenticated']:
                    self.state_manager.update_auth_state(
                        github_authenticated=True,
                        github_user=current_auth['github_user']
                    )
                
                st.success("✅ Authentication status refreshed!")
                st.rerun()
        
        # Proceed to next phase (only if both are authenticated)
        if auth_state['gcp_authenticated'] and auth_state['github_authenticated']:
            st.markdown("---")
            if st.button("🏗️ Continue to Infrastructure Setup"):
                self.state_manager.update_infrastructure_state(current_phase='infrastructure')
                st.rerun()
        else:
            st.warning("⚠️ Please complete authentication for both GCP and GitHub to continue")
            
            # Show what's missing
            missing_auth = []
            if not auth_state['gcp_authenticated']:
                missing_auth.append("GCP")
            if not auth_state['github_authenticated']:
                missing_auth.append("GitHub")
            
            st.info(f"Missing authentication: {', '.join(missing_auth)}")
    
    def _show_infrastructure_phase(self):
        """Show infrastructure setup phase"""
        st.markdown("### 🏗️ Phase 2: GCP Infrastructure Setup")
        
        infra_state = self.state_manager.get_infrastructure_state()
        
        # Show current infrastructure status
        with st.expander("📊 Current Infrastructure Status", expanded=True):
            # Debug info
            st.info("🔍 Infrastructure Manager Status:")
            st.info(f"Project ID: {self.infrastructure_manager.project_id}")
            st.info(f"Service Account: {self.infrastructure_manager.service_account_email}")
            st.info(f"WIF Pool: {self.infrastructure_manager.workload_identity_pool}")
            st.info(f"WIF Provider: {self.infrastructure_manager.workload_identity_provider}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**✅ Configured Components:**")
                if infra_state['project_id']:
                    st.success(f"• GCP Project: {infra_state['project_id']}")
                if infra_state['service_account_email']:
                    st.success(f"• Service Account: {infra_state['service_account_email']}")
                if infra_state['wif_pool']:
                    st.success(f"• WIF Pool: {infra_state['wif_pool']}")
                if infra_state['wif_provider']:
                    st.success(f"• WIF Provider: {infra_state['wif_provider']}")
                if infra_state['artifact_registry']:
                    st.success(f"• Artifact Registry: {infra_state['artifact_registry']}")
            
            with col2:
                st.markdown("**❌ Missing Components:**")
                if not infra_state['project_id']:
                    st.error("• GCP Project ID")
                if not infra_state['service_account_email']:
                    st.error("• Service Account")
                if not infra_state['wif_pool']:
                    st.error("• WIF Pool")
                if not infra_state['wif_provider']:
                    st.error("• WIF Provider")
                if not infra_state['artifact_registry']:
                    st.error("• Artifact Registry")
                if not infra_state['iam_configured']:
                    st.error("• IAM Permissions")
        
        # Infrastructure setup button
        if not infra_state['setup_complete']:
            # Test button first
            if st.button("🧪 Test Infrastructure Manager"):
                st.info("🧪 Testing infrastructure manager...")
                try:
                    # Test basic functionality
                    test_result = self.infrastructure_manager._get_project_id_from_cli()
                    st.success(f"✅ Test successful! Project ID: {test_result}")
                except Exception as e:
                    st.error(f"❌ Test failed: {str(e)}")
            
            if st.button("🏗️ Setup GCP Infrastructure"):
                st.info("🔍 Starting infrastructure setup...")
                st.info("📊 Current state before setup:")
                st.json(infra_state)
                
                with st.spinner("Setting up GCP infrastructure..."):
                    try:
                        result = self.infrastructure_manager.setup_infrastructure()
                        if result:
                            st.success("✅ Infrastructure setup complete!")
                            st.rerun()
                        else:
                            st.error("❌ Infrastructure setup failed")
                            st.info("Check the terminal for detailed error messages")
                    except Exception as e:
                        st.error(f"❌ Infrastructure setup error: {str(e)}")
                        st.info("Check the terminal for detailed error messages")
        else:
            st.success("🎉 Infrastructure setup complete! Ready to proceed to secrets extraction.")
            
            if st.button("🔑 Continue to Secrets Extraction"):
                self.state_manager.update_secrets_state(current_phase='secrets')
                st.rerun()
    
    def _show_secrets_phase(self):
        """Show secrets extraction phase"""
        st.markdown("### 🔑 Phase 3: Secrets Extraction")
        
        secrets_state = self.state_manager.get_secrets_state()
        
        if not secrets_state['secrets_extracted']:
            st.info("Extracting required secrets from infrastructure configuration...")
            
            if st.button("🔍 Extract Secrets"):
                with st.spinner("Extracting secrets..."):
                    if self.secrets_manager.extract_all_secrets():
                        st.success("✅ Secrets extracted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Secrets extraction failed")
        else:
            st.success("🎉 Secrets extracted successfully!")
            
            # Show extracted secrets
            with st.expander("🔑 Extracted Secrets", expanded=True):
                st.markdown("**GitHub Secrets:**")
                for key, value in secrets_state['github_secrets'].items():
                    st.code(f"{key}: {value}")
                
                st.markdown("**Environment Variables:**")
                for key, value in secrets_state['env_vars'].items():
                    st.code(f"{key}: {value}")
            
            if st.button("🐙 Continue to GitHub Setup"):
                self.state_manager.update_github_state(current_phase='github_setup')
                st.rerun()
    
    def _show_github_setup_phase(self):
        """Show GitHub setup phase"""
        st.markdown("### 🐙 Phase 4: GitHub Setup")
        
        github_state = self.state_manager.get_github_state()
        
        if not github_state['setup_complete']:
            st.info("Setting up GitHub repository and pushing secrets...")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔑 Push Secrets to GitHub"):
                    with st.spinner("Pushing secrets to GitHub..."):
                        if self.secrets_manager.push_secrets_to_github():
                            st.success("✅ Secrets pushed successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to push secrets")
            
            with col2:
                if st.button("📋 Generate CI/CD YAML"):
                    with st.spinner("Generating CI/CD YAML..."):
                        if self.pipeline_generator.generate_cicd_yaml():
                            st.success("✅ CI/CD YAML generated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to generate CI/CD YAML")
        else:
            st.success("🎉 GitHub setup complete! Ready to proceed to pipeline execution.")
            
            if st.button("🚀 Continue to Pipeline Execution"):
                self.state_manager.update_pipeline_state(current_phase='pipeline')
                st.rerun()
    
    def _show_pipeline_phase(self):
        """Show pipeline execution phase"""
        st.markdown("### 🚀 Phase 5: Pipeline Execution")
        
        pipeline_state = self.state_manager.get_pipeline_state()
        
        st.info("Your CI/CD pipeline is ready! Here's what you need to do:")
        
        st.markdown("""
        **📋 Manual Steps Required:**
        
        1. **Commit and Push**: The CI/CD YAML has been generated
        2. **Monitor Pipeline**: Watch GitHub Actions for execution
        3. **Verify Deployment**: Check if your service is deployed to Cloud Run
        
        **🔧 Pipeline Details:**
        - **Trigger**: Push to main branch
        - **Build**: Docker image build and push to Artifact Registry
        - **Deploy**: Automatic deployment to Cloud Run
        - **Environment**: Production-ready with proper secrets
        """)
        
        # Show pipeline status
        with st.expander("📊 Pipeline Status", expanded=True):
            if pipeline_state['committed']:
                st.success("✅ Code committed to GitHub")
            else:
                st.info("⏳ Waiting for code commit")
            
            if pipeline_state['running']:
                st.success("🔄 Pipeline is running")
            else:
                st.info("⏳ Pipeline not yet started")
            
            st.markdown(f"**Status:** {pipeline_state['status']}")
        
        # Pipeline management
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Check Pipeline Status"):
                with st.spinner("Checking pipeline status..."):
                    # Update pipeline status
                    st.rerun()
        
        with col2:
            if st.button("📊 View Pipeline Logs"):
                st.info("Pipeline logs will be displayed here")
        
        # Reset option
        if st.button("🔄 Reset to Start"):
            self.state_manager.initialize_session_state()
            st.rerun()

if __name__ == "__main__":
    app = IntelligentCICDSystem()
    app.run()
