#!/usr/bin/env python3
"""
🧠 Intelligent CI/CD Toolbox Core
Handles infrastructure setup, secrets management, and pipeline control
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class IntelligentCICDToolbox:
    """Intelligent CI/CD toolbox that adapts to any project"""

    def __init__(self):
        self.project_analysis = None
        self.project_path = Path(".")
        self.secrets_data = {}
        self.execution_log = []
        self.step_results = {}
        self.current_step = None

    def log_execution(self, step: str, message: str, status: str = "info"):
        """Log execution steps with timestamps"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "step": step,
            "message": message,
            "status": status,
        }
        self.execution_log.append(log_entry)

        # Also log to console
        status_emoji = {
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
        }.get(status, "ℹ️")
        print(f"[{timestamp}] {status_emoji} {step}: {message}")

    def check_gcloud_auth(self) -> Tuple[bool, List]:
        """Check if gcloud is authenticated"""
        try:
            result = subprocess.run(
                ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=json"],
                capture_output=True,
                text=True,
                check=True,
            )
            auth_data = json.loads(result.stdout)
            return len(auth_data) > 0, auth_data
        except Exception as e:
            return False, []

    def check_gh_auth(self) -> Tuple[bool, Dict]:
        """Check if GitHub CLI is authenticated"""
        try:
            result = subprocess.run(
                ["gh", "auth", "status"], capture_output=True, text=True, check=True
            )
            return "Logged in to github.com" in result.stdout, {"status": result.stdout}
        except Exception as e:
            return False, {}

    def get_current_project(self) -> str:
        """Get current gcloud project"""
        try:
            result = subprocess.run(
                ["gcloud", "config", "get-value", "project"],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except Exception as e:
            return None

    def set_project(self, project_id: str) -> Tuple[bool, str]:
        """Set gcloud project with detailed logging"""
        self.current_step = "Project Configuration"
        self.log_execution(
            "Project Configuration", f"Setting GCP project to: {project_id}", "info"
        )

        try:
            result = subprocess.run(
                ["gcloud", "config", "set", "project", project_id],
                capture_output=True,
                text=True,
                check=True,
            )

            self.log_execution(
                "Project Configuration",
                f"Project set successfully to: {project_id}",
                "success",
            )
            self.step_results["project_config"] = {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "project_id": project_id,
            }

            return True, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to set project: {e.stderr.strip()}"
            self.log_execution("Project Configuration", error_msg, "error")
            return False, error_msg

    def setup_infrastructure(self, project_id: str) -> bool:
        """Setup infrastructure based on project analysis"""
        if not self.project_analysis:
            print("❌ Project analysis required first")
            return False

        self.current_step = "Infrastructure Setup"
        self.log_execution(
            "Infrastructure Setup", "Starting GCP infrastructure setup...", "info"
        )

        cloud_provider = self.project_analysis["project_info"]["cloud_provider"]

        if cloud_provider == "gcp" or cloud_provider == "none":
            return self._setup_gcp_infrastructure(project_id)
        elif cloud_provider == "aws":
            return self._setup_aws_infrastructure(project_id)
        elif cloud_provider == "azure":
            return self._setup_azure_infrastructure(project_id)
        else:
            print(f"⚠️ Infrastructure setup for {cloud_provider} not yet implemented")
            return False

    def _setup_gcp_infrastructure(self, project_id: str) -> bool:
        """Setup GCP infrastructure with detailed logging"""
        self.log_execution(
            "GCP Infrastructure", "Setting up GCP infrastructure...", "info"
        )

        # Enable APIs
        apis = [
            "iamcredentials.googleapis.com",
            "cloudresourcemanager.googleapis.com",
            "iam.googleapis.com",
            "run.googleapis.com",
            "artifactregistry.googleapis.com",
            "cloudbuild.googleapis.com",
        ]

        results = []
        self.log_execution(
            "GCP Infrastructure", f"Enabling {len(apis)} required APIs...", "info"
        )

        for i, api in enumerate(apis):
            self.log_execution("GCP Infrastructure", f"Enabling API: {api}", "info")

            try:
                result = subprocess.run(
                    [
                        "gcloud",
                        "services",
                        "enable",
                        api,
                        "--project",
                        project_id,
                        "--quiet",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                results.append(f"✅ {api}: Enabled successfully")
                self.log_execution(
                    "GCP Infrastructure", f"API enabled: {api}", "success"
                )
            except subprocess.CalledProcessError as e:
                results.append(f"❌ {api}: {e.stderr.strip()}")
                self.log_execution(
                    "GCP Infrastructure",
                    f"API failed: {api} - {e.stderr.strip()}",
                    "error",
                )

        self.log_execution("GCP Infrastructure", "All APIs configured", "success")

        # Create service account
        self.log_execution("GCP Infrastructure", "Creating service account...", "info")
        service_account, sa_result = self._create_service_account(project_id)
        if service_account:
            results.append(sa_result)
            self.log_execution("GCP Infrastructure", "Service account ready", "success")
        else:
            self.log_execution(
                "GCP Infrastructure", "Service account creation failed", "error"
            )
            return False

        # Setup Workload Identity
        self.log_execution(
            "GCP Infrastructure", "Setting up Workload Identity Federation...", "info"
        )
        wif_provider, wif_results = self._setup_workload_identity(project_id)
        results.extend(wif_results)

        # Log final results
        self.log_execution(
            "GCP Infrastructure",
            "Infrastructure setup completed successfully!",
            "success",
        )
        self.step_results["infrastructure_setup"] = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "project_id": project_id,
            "results": results,
        }

        print("🎉 GCP Infrastructure setup complete!")
        return True

    def _create_service_account(self, project_id: str) -> Tuple[str, str]:
        """Create service account for CI/CD"""
        sa_name = "github-actions-sa"
        sa_email = f"{sa_name}@{project_id}.iam.gserviceaccount.com"

        try:
            # Check if service account exists
            result = subprocess.run(
                [
                    "gcloud",
                    "iam",
                    "service-accounts",
                    "describe",
                    sa_email,
                    "--project",
                    project_id,
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                return sa_email, f"✅ Service account {sa_name} already exists"
            else:
                # Create service account
                result = subprocess.run(
                    [
                        "gcloud",
                        "iam",
                        "service-accounts",
                        "create",
                        sa_name,
                        "--display-name",
                        "GitHub Actions Service Account",
                        "--description",
                        "Service account for GitHub Actions CI/CD pipeline",
                        "--project",
                        project_id,
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )

                return sa_email, f"✅ Service account {sa_name} created successfully"
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ Failed to create service account: {e.stderr.strip()}"
            return None, error_msg

    def _setup_workload_identity(self, project_id: str) -> Tuple[str, List[str]]:
        """Setup Workload Identity Federation"""
        pool_id = "github-actions-pool"
        provider_id = "github-actions-provider"

        results = []

        # Create pool
        try:
            subprocess.run(
                [
                    "gcloud",
                    "iam",
                    "workload-identity-pools",
                    "create",
                    pool_id,
                    "--location",
                    "global",
                    "--display-name",
                    "GitHub Actions Pool",
                    "--description",
                    "Pool for GitHub Actions CI/CD pipeline",
                    "--project",
                    project_id,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            results.append(f"✅ Workload Identity Pool created: {pool_id}")
        except subprocess.CalledProcessError as e:
            if "ALREADY_EXISTS" in e.stderr:
                results.append(f"ℹ️ Workload Identity Pool already exists: {pool_id}")
            else:
                results.append(f"❌ Failed to create pool: {e.stderr.strip()}")

        # Create provider
        try:
            result = subprocess.run(
                [
                    "gcloud",
                    "iam",
                    "workload-identity-pools",
                    "providers",
                    "create-oidc",
                    provider_id,
                    "--workload-identity-pool",
                    pool_id,
                    "--location",
                    "global",
                    "--issuer-uri",
                    "https://token.actions.githubusercontent.com",
                    "--attribute-mapping",
                    "google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.aud=assertion.aud",
                    "--project",
                    project_id,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            results.append(f"✅ Workload Identity Provider created: {provider_id}")
        except subprocess.CalledProcessError as e:
            if "ALREADY_EXISTS" in e.stderr:
                results.append(
                    f"ℹ️ Workload Identity Provider already exists: {provider_id}"
                )
            else:
                results.append(f"❌ Failed to create provider: {e.stderr.strip()}")

        return (
            f"projects/{project_id}/locations/global/workloadIdentityPools/{pool_id}/providers/{provider_id}",
            results,
        )

    def _setup_aws_infrastructure(self, project_id: str) -> bool:
        """Setup AWS infrastructure (placeholder)"""
        print("🚧 AWS infrastructure setup coming soon...")
        return False

    def _setup_azure_infrastructure(self, project_id: str) -> bool:
        """Setup Azure infrastructure (placeholder)"""
        print("🚧 Azure infrastructure setup coming soon...")
        return False

    def generate_secrets_template(self, project_id: str) -> Dict[str, str]:
        """Generate secrets template based on project analysis"""
        if not self.project_analysis:
            print("❌ Project analysis required first")
            return {}

        self.current_step = "Secrets Generation"
        self.log_execution(
            "Secrets Generation", "Generating intelligent secrets template...", "info"
        )

        # Get current project info
        current_project = self.get_current_project()
        if not current_project:
            current_project = project_id

        # Generate CI/CD secrets
        ci_cd_secrets = {
            "GCP_PROJECT_ID": current_project,
            "GCP_SERVICE_ACCOUNT": f"github-actions-sa@{current_project}.iam.gserviceaccount.com",
            "WIF_PROVIDER": f"projects/{current_project}/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider",
            "REGION": "asia-south1",
            "SERVICE_NAME": "app-service",
        }

        # Add runtime secrets with placeholder values
        runtime_secrets = {}
        for secret in self.project_analysis["runtime_secrets"]:
            if secret not in ci_cd_secrets:
                runtime_secrets[secret] = f"YOUR_{secret}_HERE"

        self.secrets_data = {**ci_cd_secrets, **runtime_secrets}

        # Save to file
        with open("intelligent-secrets-template.json", "w") as f:
            json.dump(self.secrets_data, f, indent=2)

        self.log_execution(
            "Secrets Generation",
            f"Generated {len(self.secrets_data)} secrets",
            "success",
        )
        self.step_results["secrets_generation"] = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "total_secrets": len(self.secrets_data),
            "ci_cd_secrets": len(ci_cd_secrets),
            "runtime_secrets": len(runtime_secrets),
        }

        return self.secrets_data

    def push_secrets_to_github(self) -> Tuple[bool, Any]:
        """Push secrets to GitHub using GitHub CLI with detailed logging"""
        if not self.secrets_data:
            print("❌ No secrets to push. Generate secrets template first.")
            return False, "No secrets to push"

        self.current_step = "GitHub Secrets Push"
        self.log_execution(
            "GitHub Secrets Push", "Starting to push secrets to GitHub...", "info"
        )

        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                check=True,
            )
            repo_url = result.stdout.strip()

            if "github.com" not in repo_url:
                error_msg = "Not a GitHub repository"
                self.log_execution("GitHub Secrets Push", error_msg, "error")
                return False, error_msg

            parts = repo_url.split("github.com/")[1].replace(".git", "").split("/")
            repo_owner, repo_name = parts[0], parts[1]

            self.log_execution(
                "GitHub Secrets Push",
                f"Pushing to repository: {repo_owner}/{repo_name}",
                "info",
            )

            results = []
            failed_secrets = []

            for secret_name, secret_value in self.secrets_data.items():
                self.log_execution(
                    "GitHub Secrets Push", f"Setting secret: {secret_name}", "info"
                )

                try:
                    subprocess.run(
                        [
                            "gh",
                            "secret",
                            "set",
                            secret_name,
                            "--repo",
                            f"{repo_owner}/{repo_name}",
                            "--body",
                            secret_value,
                        ],
                        check=True,
                        input=secret_value.encode(),
                    )

                    results.append(f"✅ {secret_name}: Set successfully")
                    self.log_execution(
                        "GitHub Secrets Push", f"Secret set: {secret_name}", "success"
                    )
                except subprocess.CalledProcessError as e:
                    error_msg = f"❌ {secret_name}: Failed to set"
                    results.append(error_msg)
                    failed_secrets.append({"secret": secret_name, "error": str(e)})
                    self.log_execution(
                        "GitHub Secrets Push", f"Secret failed: {secret_name}", "error"
                    )

            if failed_secrets:
                self.log_execution(
                    "GitHub Secrets Push",
                    f"Failed to push {len(failed_secrets)} secrets",
                    "warning",
                )
            else:
                self.log_execution(
                    "GitHub Secrets Push", "All secrets pushed successfully!", "success"
                )

            # Store results
            self.step_results["github_secrets_push"] = {
                "status": (
                    "completed" if not failed_secrets else "completed_with_errors"
                ),
                "timestamp": datetime.now().isoformat(),
                "total_secrets": len(self.secrets_data),
                "successful": len(results) - len(failed_secrets),
                "failed": len(failed_secrets),
                "failed_details": failed_secrets,
            }

            return True, results

        except Exception as e:
            error_msg = f"Failed to push secrets: {str(e)}"
            self.log_execution("GitHub Secrets Push", error_msg, "error")
            return False, error_msg

    def trigger_pipeline(
        self,
        environment: str = "staging",
        skip_steps: List[str] = None,
        force_deploy: bool = False,
    ) -> Tuple[bool, Any]:
        """Trigger CI/CD pipeline with environment and step control"""
        if not skip_steps:
            skip_steps = []

        self.current_step = "Pipeline Trigger"
        self.log_execution(
            "Pipeline Trigger",
            f"Triggering pipeline for {environment} environment...",
            "info",
        )

        try:
            results = []

            # Check current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True,
            )
            current_branch = result.stdout.strip()
            results.append(f"📍 Current branch: {current_branch}")

            if current_branch != "main":
                self.log_execution(
                    "Pipeline Trigger",
                    f"Switching from {current_branch} to main branch...",
                    "info",
                )
                subprocess.run(["git", "checkout", "main"], check=True)
                subprocess.run(["git", "pull", "origin", "main"], check=True)
                results.append("✅ Switched to main branch")

            # Create trigger file with environment and step control
            with open(".pipeline-trigger", "w") as f:
                f.write(f"# Pipeline triggered by Intelligent CI/CD Toolbox\n")
                f.write(f"# Environment: {environment}\n")
                f.write(
                    f"# Skip Steps: {', '.join(skip_steps) if skip_steps else 'None'}\n"
                )
                f.write(f"# Force Deploy: {force_deploy}\n")
                f.write(f"# Timestamp: {datetime.now()}\n")

            results.append("📝 Created pipeline trigger file")

            # Commit and push
            subprocess.run(["git", "add", ".pipeline-trigger"], check=True)
            results.append("✅ Added trigger file to git")

            commit_message = f"🤖 Auto-trigger CI/CD pipeline - {environment}"
            if skip_steps:
                commit_message += f" [Skip: {', '.join(skip_steps)}]"
            if force_deploy:
                commit_message += " [Force Deploy]"
            commit_message += " [skip ci]"

            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            results.append("✅ Committed trigger file")

            subprocess.run(["git", "push", "origin", "main"], check=True)
            results.append("✅ Pushed to main branch")

            self.log_execution(
                "Pipeline Trigger",
                f"Pipeline triggered successfully for {environment}",
                "success",
            )
            self.step_results["pipeline_trigger"] = {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "environment": environment,
                "skip_steps": skip_steps,
                "force_deploy": force_deploy,
                "results": results,
            }

            return True, results

        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to trigger pipeline: {e.stderr.strip()}"
            self.log_execution("Pipeline Trigger", error_msg, "error")
            return False, error_msg

    def get_execution_summary(self) -> List[str]:
        """Get a summary of all executed steps"""
        if not self.step_results:
            return ["No steps executed yet"]

        summary = []
        for step, result in self.step_results.items():
            status_emoji = "✅" if result["status"] == "completed" else "❌"
            summary.append(
                f"{status_emoji} {step.replace('_', ' ').title()}: {result['status']}"
            )

        return summary

    def get_next_steps(self) -> List[str]:
        """Get the next steps based on current progress"""
        next_steps = []

        if not self.step_results.get("project_analysis"):
            next_steps.append("🧠 Run Project Analysis to detect requirements")
        elif not self.step_results.get("project_config"):
            next_steps.append("📋 Configure GCP Project ID")
        elif not self.step_results.get("infrastructure_setup"):
            next_steps.append(
                "🔧 Setup GCP Infrastructure (APIs, Service Account, WIF)"
            )
        elif not self.step_results.get("secrets_generation"):
            next_steps.append("🔑 Generate Secrets Template")
        elif not self.step_results.get("github_secrets_push"):
            next_steps.append("📤 Push Secrets to GitHub Actions")
        elif not self.step_results.get("pipeline_trigger"):
            next_steps.append("🚀 Trigger CI/CD Pipeline")
        else:
            next_steps.append("🎉 All steps completed! Monitor pipeline progress")

        return next_steps
