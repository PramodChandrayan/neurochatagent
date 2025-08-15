#!/usr/bin/env python3
"""
🚀 Enhanced CI/CD GUI Toolbox
Real-time feedback, automatic secrets pushing, pipeline control, and deployment strategy
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set

import streamlit as st

# Import from the package
from analyzer import IntelligentProjectAnalyzer
from toolbox import IntelligentCICDToolbox

# Page configuration
st.set_page_config(
    page_title="🚀 Intelligent CI/CD Toolbox", page_icon="🚀", layout="wide"
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .execution-log {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
        font-size: 0.9rem;
        max-height: 300px;
        overflow-y: auto;
    }
    .summary-box {
        background-color: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .next-steps {
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .pipeline-control {
        background-color: #f3e5f5;
        border: 1px solid #9c27b0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .deployment-config {
        background-color: #e1f5fe;
        border: 1px solid #03a9f4;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .config-section {
        background-color: #fafafa;
        border: 1px solid #e0e0e0;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    st.markdown(
        '<h1 class="main-header">🚀 Intelligent CI/CD Toolbox</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="text-align: center; font-size: 1.2rem; color: #666;">Real-time feedback, automatic secrets pushing, pipeline control, and deployment strategy</p>',
        unsafe_allow_html=True,
    )

    # Initialize toolbox
    if "intelligent_toolbox" not in st.session_state:
        st.session_state.intelligent_toolbox = IntelligentCICDToolbox()

    toolbox = st.session_state.intelligent_toolbox

    # Project Analysis Section
    st.header("🔍 Project Analysis")

    if st.button("🧠 Analyze Project", key="analyze_project"):
        with st.spinner("🔍 Analyzing project structure and requirements..."):
            analyzer = IntelligentProjectAnalyzer(str(Path(".")))
            analysis = analyzer.analyze_project()
            if analysis:
                st.success("✅ Project analysis completed!")
                # Store in both session state and toolbox instance
                st.session_state.project_analysis = analysis
                toolbox.project_analysis = analysis
                st.rerun()

    # Display project analysis results
    analysis = None
    if (
        hasattr(st.session_state, "project_analysis")
        and st.session_state.project_analysis
    ):
        analysis = st.session_state.project_analysis
    elif toolbox.project_analysis:
        analysis = toolbox.project_analysis
        st.session_state.project_analysis = analysis  # Sync to session state

    if analysis:
        # Project Information
        st.markdown("### 📋 Project Information")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Type", analysis["project_info"]["type"].upper())
        with col2:
            st.metric("Framework", analysis["project_info"]["framework"])
        with col3:
            st.metric(
                "Cloud Provider",
                analysis["project_info"]["cloud_provider"] or "Not detected",
            )
        with col4:
            st.metric("Database", analysis["project_info"]["database_type"] or "None")

        # Secrets Overview
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Runtime Secrets", len(analysis["runtime_secrets"]))
        with col2:
            st.metric("CI/CD Secrets", len(analysis["ci_cd_secrets"]))
        with col3:
            st.metric("Recommendations", len(analysis["recommendations"]))

        # Runtime Secrets
        st.markdown("### 🔑 Runtime Secrets Required")
        for secret in analysis["runtime_secrets"]:
            st.markdown(f"- {secret}")

        # CI/CD Secrets
        st.markdown("### 🚀 CI/CD Infrastructure Secrets")
        for secret in analysis["ci_cd_secrets"]:
            st.markdown(f"- {secret}")

        # Recommendations
        st.markdown("### 💡 Intelligent Recommendations")
        for rec in analysis["recommendations"]:
            st.info(rec)

    # Setup Section
    if hasattr(st.session_state, "project_analysis"):
        st.header("⚙️ Intelligent Setup")

        # GCP Setup
        st.subheader("🔧 GCP Infrastructure Setup")

        # Project Configuration
        current_project = toolbox.get_current_project()
        if current_project:
            st.success(f"✅ Project: {current_project}")
        else:
            st.warning("⏳ No project set")
            project_id = st.text_input("Enter Google Cloud Project ID:")
            if st.button("Set Project", key="set_project"):
                if project_id:
                    with st.spinner("Setting project..."):
                        success, output = toolbox.set_project(project_id)
                        if success:
                            st.success(f"✅ Project set to: {project_id}")
                            st.rerun()
                        else:
                            st.error(f"❌ Failed to set project: {output}")
                else:
                    st.error("Please enter a project ID")

        # Infrastructure Setup
        if current_project or "project_id" in locals():
            project_to_use = current_project or project_id

            if st.button("🔧 Setup GCP Infrastructure", key="setup_gcp"):
                success = toolbox.setup_infrastructure(project_to_use)
                if success:
                    st.success("✅ GCP Infrastructure ready!")
                    st.rerun()

            # Generate Secrets Template
            if st.button("📋 Generate Secrets Template", key="generate_secrets"):
                with st.spinner("Generating intelligent secrets template..."):
                    secrets = toolbox.generate_secrets_template(project_to_use)
                    if secrets:
                        st.success("✅ Secrets template generated!")
                        st.download_button(
                            label="📥 Download Secrets Template",
                            data=json.dumps(secrets, indent=2),
                            file_name="intelligent-secrets-template.json",
                            mime="application/json",
                        )

            # Push Secrets to GitHub
            if toolbox.secrets_data:
                st.subheader("📤 GitHub Secrets Management")

                if st.button("📤 Push All Secrets to GitHub", key="push_secrets"):
                    with st.spinner("Pushing secrets to GitHub..."):
                        success, results = toolbox.push_secrets_to_github()
                        if success:
                            st.success("✅ All secrets pushed to GitHub!")
                            st.balloons()

                            # Show results
                            if isinstance(results, list):
                                st.markdown("**Push Results:**")
                                for result in results:
                                    if "✅" in result:
                                        st.success(result)
                                    elif "❌" in result:
                                        st.error(result)
                                    else:
                                        st.info(result)
                        else:
                            st.error(f"❌ Failed to push secrets: {results}")

    # Deployment Configuration Section
    if hasattr(st.session_state, "project_analysis"):
        st.header("⚙️ Deployment Configuration")

        st.markdown('<div class="deployment-config">', unsafe_allow_html=True)
        st.markdown("### 🎯 Configure Your Deployment Settings")

        # Environment Configuration
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🌍 Environment Settings")
            deployment_environment = st.selectbox(
                "Deployment Environment:",
                ["staging", "development", "production"],
                help="Choose the target environment for deployment",
            )

            deployment_region = st.selectbox(
                "GCP Region:",
                ["asia-south1", "us-central1", "europe-west1", "asia-northeast1"],
                help="Select the GCP region for deployment",
            )

            service_name = st.text_input(
                "Service Name:",
                value="finance-chatbot",
                help="Name for your Cloud Run service",
            )

        with col2:
            st.markdown("#### 🔧 Resource Configuration")
            cpu_allocation = st.selectbox(
                "CPU Allocation:",
                ["1000m", "2000m", "4000m", "8000m"],
                help="CPU allocation for your service",
            )

            memory_allocation = st.selectbox(
                "Memory Allocation:",
                ["512Mi", "1Gi", "2Gi", "4Gi", "8Gi"],
                help="Memory allocation for your service",
            )

            max_instances = st.slider(
                "Max Instances:",
                min_value=1,
                max_value=100,
                value=10,
                help="Maximum number of instances",
            )

        # Advanced Configuration
        st.markdown("#### ⚙️ Advanced Configuration")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Container Settings**")
            container_port = st.number_input(
                "Container Port:",
                min_value=1,
                max_value=65535,
                value=8501,
                help="Port your application listens on",
            )

            health_check_path = st.text_input(
                "Health Check Path:", value="/health", help="Path for health checks"
            )

        with col2:
            st.markdown("**Security Settings**")
            allow_unauthenticated = st.checkbox(
                "Allow Unauthenticated Access",
                value=True,
                help="Allow public access to your service",
            )

            enable_vpc_connector = st.checkbox(
                "Enable VPC Connector",
                value=False,
                help="Connect to VPC for private resources",
            )

        with col3:
            st.markdown("**Monitoring Settings**")
            enable_monitoring = st.checkbox(
                "Enable Monitoring", value=True, help="Enable Cloud Monitoring"
            )

            enable_logging = st.checkbox(
                "Enable Logging", value=True, help="Enable Cloud Logging"
            )

        # Custom Environment Variables
        st.markdown("#### 🔑 Custom Environment Variables")

        if "custom_env_vars" not in st.session_state:
            st.session_state.custom_env_vars = {}

        col1, col2 = st.columns([3, 1])

        with col1:
            new_env_key = st.text_input("Environment Variable Key:")
            new_env_value = st.text_input("Environment Variable Value:")

        with col2:
            if st.button("➕ Add Variable", key="add_env_var"):
                if new_env_key and new_env_value:
                    st.session_state.custom_env_vars[new_env_key] = new_env_value
                    st.success(f"✅ Added {new_env_key}")
                    st.rerun()

        # Display current environment variables
        if st.session_state.custom_env_vars:
            st.markdown("**Current Environment Variables:**")
            for key, value in st.session_state.custom_env_vars.items():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.text(key)
                with col2:
                    st.text(value)
                with col3:
                    if st.button("🗑️", key=f"remove_{key}"):
                        del st.session_state.custom_env_vars[key]
                        st.rerun()

        # Save Configuration
        if st.button("💾 Save Deployment Configuration", key="save_config"):
            config = {
                "environment": deployment_environment,
                "region": deployment_region,
                "service_name": service_name,
                "resources": {
                    "cpu": cpu_allocation,
                    "memory": memory_allocation,
                    "max_instances": max_instances,
                },
                "container": {
                    "port": container_port,
                    "health_check_path": health_check_path,
                },
                "security": {
                    "allow_unauthenticated": allow_unauthenticated,
                    "enable_vpc_connector": enable_vpc_connector,
                },
                "monitoring": {
                    "enable_monitoring": enable_monitoring,
                    "enable_logging": enable_logging,
                },
                "custom_environment_variables": st.session_state.custom_env_vars,
                "timestamp": datetime.now().isoformat(),
            }

            # Save to file
            with open("deployment-config.json", "w") as f:
                json.dump(config, f, indent=2)

            st.success("✅ Deployment configuration saved!")
            st.download_button(
                label="📥 Download Configuration",
                data=json.dumps(config, indent=2),
                file_name="deployment-config.json",
                mime="application/json",
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # Pipeline Control Section
    if hasattr(st.session_state, "project_analysis"):
        st.header("🚀 Pipeline Control & Deployment Strategy")

        st.markdown('<div class="pipeline-control">', unsafe_allow_html=True)
        st.markdown("### 🎯 Pipeline Execution Control")

        # Load saved configuration if exists
        deployment_config = None
        if os.path.exists("deployment-config.json"):
            try:
                with open("deployment-config.json", "r") as f:
                    deployment_config = json.load(f)
                st.success("✅ Using saved deployment configuration")
            except:
                st.warning("⚠️ Could not load saved configuration")

        # Environment Selection
        col1, col2 = st.columns(2)

        with col1:
            if deployment_config:
                environment = st.selectbox(
                    "Select Deployment Environment:",
                    ["staging", "production", "development"],
                    index=["staging", "production", "development"].index(
                        deployment_config.get("environment", "staging")
                    ),
                    help="Choose the target environment for deployment",
                )
            else:
                environment = st.selectbox(
                    "Select Deployment Environment:",
                    ["staging", "production", "development"],
                    help="Choose the target environment for deployment",
                )

        with col2:
            force_deploy = st.checkbox(
                "Force Deploy",
                help="Force deployment even if previous deployment exists",
            )

        # Pipeline Step Control
        st.markdown("#### 🔧 Pipeline Step Control")
        st.markdown("Select which steps to skip (optional):")

        col1, col2, col3 = st.columns(3)

        with col1:
            skip_tests = st.checkbox("Skip Tests")
            skip_lint = st.checkbox("Skip Linting")
            skip_build = st.checkbox("Skip Build")

        with col2:
            skip_scan = st.checkbox("Skip Security Scan")
            skip_deploy = st.checkbox("Skip Deployment")
            skip_notify = st.checkbox("Skip Notifications")

        with col3:
            skip_docs = st.checkbox("Skip Documentation")
            skip_metrics = st.checkbox("Skip Metrics Collection")
            skip_backup = st.checkbox("Skip Backup")

        # Collect skip steps
        skip_steps = []
        if skip_tests:
            skip_steps.append("tests")
        if skip_lint:
            skip_steps.append("lint")
        if skip_build:
            skip_steps.append("build")
        if skip_scan:
            skip_steps.append("security-scan")
        if skip_deploy:
            skip_steps.append("deploy")
        if skip_notify:
            skip_steps.append("notify")
        if skip_docs:
            skip_steps.append("docs")
        if skip_metrics:
            skip_steps.append("metrics")
        if skip_backup:
            skip_steps.append("backup")

        # Pipeline Trigger
        if st.button("🚀 Trigger CI/CD Pipeline", key="trigger_pipeline"):
            with st.spinner("Triggering pipeline..."):
                success, results = toolbox.trigger_pipeline(
                    environment=environment,
                    skip_steps=skip_steps,
                    force_deploy=force_deploy,
                )

                if success:
                    st.success(f"✅ Pipeline triggered for {environment}!")

                    # Show results
                    if isinstance(results, list):
                        st.markdown("**Pipeline Trigger Results:**")
                        for result in results:
                            if "✅" in result:
                                st.success(result)
                            elif "🔄" in result:
                                st.info(result)
                            elif "📝" in result:
                                st.info(result)
                            else:
                                st.info(result)
                else:
                    st.error(f"❌ Failed to trigger pipeline: {results}")

        st.markdown("</div>", unsafe_allow_html=True)

    # Execution Log Section
    if toolbox.execution_log:
        st.header("📋 Execution Log")

        st.markdown('<div class="execution-log">', unsafe_allow_html=True)
        for log_entry in toolbox.execution_log[-20:]:  # Show last 20 entries
            timestamp = log_entry["timestamp"]
            step = log_entry["step"]
            message = log_entry["message"]
            status = log_entry["status"]

            status_emoji = {
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️",
            }.get(status, "ℹ️")
            st.markdown(f"**[{timestamp}]** {status_emoji} **{step}:** {message}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Summary & Next Steps Section
    if toolbox.step_results:
        st.header("📊 Execution Summary")

        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
        st.markdown("### ✅ Completed Steps")
        summary = toolbox.get_execution_summary()
        if isinstance(summary, list):
            for step_summary in summary:
                st.markdown(f"- {step_summary}")
        else:
            st.info(summary)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="next-steps">', unsafe_allow_html=True)
        st.markdown("### 🎯 Next Steps")
        next_steps = toolbox.get_next_steps()
        for step in next_steps:
            st.info(step)
        st.markdown("</div>", unsafe_allow_html=True)

    # Authentication Section
    st.header("🔐 Authentication Setup")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Google Cloud")
        gcloud_auth, gcloud_data = toolbox.check_gcloud_auth()
        if gcloud_auth:
            st.success(
                f"✅ Authenticated as: {gcloud_data[0].get('account', 'Unknown')}"
            )
        else:
            st.warning("⏳ Not authenticated")
            if st.button("🔑 Authenticate with Google Cloud", key="gcloud_auth"):
                with st.spinner("Opening authentication..."):
                    try:
                        subprocess.run(["gcloud", "auth", "login"], check=True)
                        st.success("✅ Authentication completed!")
                        st.rerun()
                    except:
                        st.error("❌ Authentication failed")

    with col2:
        st.subheader("GitHub CLI")
        gh_auth, gh_data = toolbox.check_gh_auth()
        if gh_auth:
            st.success("✅ GitHub CLI authenticated")
        else:
            st.warning("⏳ Not authenticated")
            if st.button("🔑 Authenticate with GitHub", key="gh_auth"):
                with st.spinner("Opening authentication..."):
                    try:
                        subprocess.run(["gh", "auth", "login"], check=True)
                        st.success("✅ Authentication completed!")
                        st.rerun()
                    except:
                        st.error("❌ Authentication failed")

    # Quick Actions
    st.header("🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Refresh Analysis", key="refresh"):
            st.rerun()

    with col2:
        if st.button("📊 View Analysis JSON", key="view_json"):
            if (
                hasattr(st.session_state, "project_analysis")
                and st.session_state.project_analysis
            ):
                st.json(st.session_state.project_analysis)
            elif toolbox.project_analysis:
                st.json(toolbox.project_analysis)
            else:
                st.warning("No analysis data available")

    with col3:
        if st.button("📁 Browse Project", key="browse"):
            st.info("Project browser coming soon...")


if __name__ == "__main__":
    main()
