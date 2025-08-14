#!/usr/bin/env python3
"""
🧠 Smart Defaults & Environment Detection
Intelligently suggests secret values based on environment analysis
"""

import os
import json
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class SmartDefaults:
    """Intelligently suggests default values for secrets"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_file = self.project_root / "ci-cd-analysis.json"
        self.suggestions = {}

    def detect_environment(self) -> Dict[str, Any]:
        """Detect environment and suggest defaults"""
        env_info = {
            "gcp": self._detect_gcp_environment(),
            "github": self._detect_github_environment(),
            "local": self._detect_local_environment(),
            "secrets": self._analyze_secret_patterns(),
        }

        return env_info

    def _detect_gcp_environment(self) -> Dict[str, Any]:
        """Detect GCP environment and configuration"""
        gcp_info = {
            "project_id": None,
            "region": None,
            "service_account": None,
            "artifacts_repo": None,
        }

        try:
            # Check if gcloud is available
            result = subprocess.run(
                ["gcloud", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                gcp_info["gcloud_available"] = True

                # Get current project
                result = subprocess.run(
                    ["gcloud", "config", "get-value", "project"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    gcp_info["project_id"] = result.stdout.strip()

                # Get current region
                result = subprocess.run(
                    ["gcloud", "config", "get-value", "compute/region"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    gcp_info["region"] = result.stdout.strip()

                # Check if authenticated
                result = subprocess.run(
                    ["gcloud", "auth", "list"], capture_output=True, text=True
                )
                if result.returncode == 0 and "ACTIVE" in result.stdout:
                    gcp_info["authenticated"] = True

                    # Try to get project info
                    if gcp_info["project_id"]:
                        result = subprocess.run(
                            ["gcloud", "projects", "describe", gcp_info["project_id"]],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0:
                            gcp_info["project_exists"] = True

                            # Check for Artifact Registry
                            result = subprocess.run(
                                ["gcloud", "artifacts", "repositories", "list"],
                                capture_output=True,
                                text=True,
                            )
                            if result.returncode == 0:
                                repos = result.stdout.strip().split("\n")[
                                    1:
                                ]  # Skip header
                                if repos:
                                    gcp_info["artifacts_repo"] = repos[0].split()[
                                        0
                                    ]  # First repo name

            else:
                gcp_info["gcloud_available"] = False

        except FileNotFoundError:
            gcp_info["gcloud_available"] = False

        return gcp_info

    def _detect_github_environment(self) -> Dict[str, Any]:
        """Detect GitHub environment and configuration"""
        github_info = {
            "repository": None,
            "owner": None,
            "branch": None,
            "remote_url": None,
        }

        try:
            # Get git remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                github_info["remote_url"] = remote_url

                # Parse GitHub URL
                if "github.com" in remote_url:
                    # Extract owner/repo from URL
                    match = re.search(
                        r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$", remote_url
                    )
                    if match:
                        github_info["owner"] = match.group(1)
                        github_info["repository"] = match.group(2)

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )
            if result.returncode == 0:
                github_info["branch"] = result.stdout.strip()

        except (subprocess.SubprocessError, FileNotFoundError):
            pass

        return github_info

    def _detect_local_environment(self) -> Dict[str, Any]:
        """Detect local environment and configuration"""
        local_info = {
            "python_version": None,
            "env_files": [],
            "config_files": [],
            "docker_available": False,
        }

        # Check Python version
        try:
            result = subprocess.run(
                ["python3", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                local_info["python_version"] = result.stdout.strip()
        except FileNotFoundError:
            pass

        # Check for environment files
        env_patterns = [".env*", "env.*", "*.env"]
        for pattern in env_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    local_info["env_files"].append(str(file_path))

        # Check for config files
        config_patterns = ["config.py", "config.yml", "config.yaml", "config.json"]
        for pattern in config_patterns:
            config_file = self.project_root / pattern
            if config_file.exists():
                local_info["config_files"].append(str(config_file))

        # Check if Docker is available
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True
            )
            if result.returncode == 0:
                local_info["docker_available"] = True
        except FileNotFoundError:
            pass

        return local_info

    def _analyze_secret_patterns(self) -> Dict[str, Any]:
        """Analyze code for secret patterns and suggest defaults"""
        secret_patterns = {
            "openai": {
                "patterns": ["OPENAI_API_KEY", "openai_api_key"],
                "suggestions": ["Get from https://platform.openai.com/api-keys"],
            },
            "pinecone": {
                "patterns": [
                    "PINECONE_API_KEY",
                    "PINECONE_ENVIRONMENT",
                    "PINECONE_INDEX_NAME",
                ],
                "suggestions": ["Get from https://app.pinecone.io/"],
            },
            "gcp": {
                "patterns": ["GCP_PROJECT_ID", "GCP_SA_KEY"],
                "suggestions": ["Get from GCP Console → IAM → Service Accounts"],
            },
            "database": {
                "patterns": ["DATABASE_URL", "DB_URL", "POSTGRES_URL"],
                "suggestions": ["Format: postgresql://user:pass@host:port/db"],
            },
        }

        found_patterns = {}

        # Search for patterns in Python files
        for py_file in self.project_root.rglob("*.py"):
            try:
                with open(py_file, "r") as f:
                    content = f.read()

                    for category, info in secret_patterns.items():
                        for pattern in info["patterns"]:
                            if pattern.lower() in content.lower():
                                if category not in found_patterns:
                                    found_patterns[category] = []
                                found_patterns[category].append(
                                    {
                                        "pattern": pattern,
                                        "file": str(py_file),
                                        "suggestions": info["suggestions"],
                                    }
                                )
            except:
                continue

        return found_patterns

    def generate_suggestions(self) -> Dict[str, Any]:
        """Generate intelligent suggestions for secrets"""
        env_info = self.detect_environment()

        suggestions = {
            "automatic": {},
            "manual": {},
            "smart_defaults": {},
            "next_steps": [],
        }

        # GCP suggestions
        if env_info["gcp"]["gcloud_available"]:
            if env_info["gcp"]["project_id"]:
                suggestions["automatic"]["GCP_PROJECT_ID"] = env_info["gcp"][
                    "project_id"
                ]
                suggestions["smart_defaults"][
                    "GCP_PROJECT_ID"
                ] = f"✅ Auto-detected: {env_info['gcp']['project_id']}"

            if env_info["gcp"]["region"]:
                suggestions["automatic"]["REGION"] = env_info["gcp"]["region"]
                suggestions["smart_defaults"][
                    "REGION"
                ] = f"✅ Auto-detected: {env_info['gcp']['region']}"

            if not env_info["gcp"]["authenticated"]:
                suggestions["next_steps"].append("🔐 Run: gcloud auth login")

            if not env_info["gcp"]["project_exists"]:
                suggestions["next_steps"].append(
                    "☁️ Create GCP project or set correct project"
                )

        # GitHub suggestions
        if env_info["github"]["repository"]:
            suggestions["automatic"]["SERVICE_NAME"] = env_info["github"]["repository"]
            suggestions["smart_defaults"][
                "SERVICE_NAME"
            ] = f"✅ Auto-detected: {env_info['github']['repository']}"

        # Local environment suggestions
        if env_info["local"]["env_files"]:
            suggestions["next_steps"].append(
                f"📁 Found environment files: {', '.join(env_info['local']['env_files'])}"
            )
            suggestions["next_steps"].append(
                "💡 Check these files for existing secret values"
            )

        # Secret pattern suggestions
        for category, patterns in env_info["secrets"].items():
            if patterns:
                suggestions["manual"][category] = patterns
                suggestions["next_steps"].append(
                    f"🔍 Found {category} patterns in code - configure these secrets"
                )

        return suggestions

    def create_setup_script(self) -> str:
        """Create a setup script with detected values"""
        suggestions = self.generate_suggestions()

        script_content = f"""#!/bin/bash
# 🚀 Auto-Generated CI/CD Setup Script
# Generated based on environment analysis

set -e

echo "🚀 Setting up CI/CD with detected values..."

# Auto-detected values
"""

        # Add automatic values
        for secret, value in suggestions["automatic"].items():
            script_content += f"""
# {secret} - Auto-detected
export {secret}="{value}"
echo "✅ {secret}: {value}"
"""

        # Add manual setup instructions
        script_content += """
# Manual setup required for these secrets:
"""

        for category, patterns in suggestions["manual"].items():
            script_content += f"""
# {category.upper()} SECRETS:
"""
            for pattern_info in patterns:
                script_content += f"""# - {pattern_info['pattern']} (found in {pattern_info['file']})
#   {pattern_info['suggestions'][0]}
"""

        # Add setup commands
        script_content += """
# Setup commands
echo "🔐 Setting up GitHub secrets..."

# Add automatic secrets
"""

        for secret in suggestions["automatic"]:
            script_content += f"""gh secret set {secret} --repo "$REPO_OWNER/$REPO_NAME" --body "${{{secret}}}"
"""

        script_content += """
echo "🎉 Setup completed!"
echo ""
echo "Next steps:"
"""

        for step in suggestions["next_steps"]:
            script_content += f"""echo "{step}"
"""

        return script_content

    def print_analysis(self):
        """Print the complete analysis"""
        suggestions = self.generate_suggestions()

        print("\n" + "=" * 60)
        print("🧠 SMART DEFAULTS & ENVIRONMENT ANALYSIS")
        print("=" * 60)

        # Environment detection
        env_info = self.detect_environment()

        print(f"\n🔍 Environment Detection:")
        print(
            f"   GCP: {'✅ Available' if env_info['gcp']['gcloud_available'] else '❌ Not available'}"
        )
        print(
            f"   GitHub: {'✅ Connected' if env_info['github']['repository'] else '❌ Not connected'}"
        )
        print(
            f"   Docker: {'✅ Available' if env_info['local']['docker_available'] else '❌ Not available'}"
        )

        # Auto-detected values
        if suggestions["automatic"]:
            print(f"\n✅ Auto-Detected Values:")
            for secret, value in suggestions["automatic"].items():
                print(f"   {secret}: {value}")

        # Smart defaults
        if suggestions["smart_defaults"]:
            print(f"\n🧠 Smart Defaults:")
            for secret, description in suggestions["smart_defaults"].items():
                print(f"   {secret}: {description}")

        # Manual setup required
        if suggestions["manual"]:
            print(f"\n🔧 Manual Setup Required:")
            for category, patterns in suggestions["manual"].items():
                print(f"   {category.upper()}:")
                for pattern_info in patterns:
                    print(f"     - {pattern_info['pattern']}")
                    print(f"       File: {pattern_info['file']}")
                    print(f"       Help: {pattern_info['suggestions'][0]}")

        # Next steps
        if suggestions["next_steps"]:
            print(f"\n🚀 Next Steps:")
            for step in suggestions["next_steps"]:
                print(f"   {step}")

        print("\n" + "=" * 60)

    def save_analysis(self, output_file: str = "smart-defaults-analysis.json"):
        """Save analysis to file"""
        analysis = {
            "environment": self.detect_environment(),
            "suggestions": self.generate_suggestions(),
            "setup_script": self.create_setup_script(),
        }

        with open(output_file, "w") as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"✅ Analysis saved to {output_file}")

    def save_setup_script(self, output_file: str = "setup-cicd.sh"):
        """Save setup script to file"""
        script_content = self.create_setup_script()

        with open(output_file, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(output_file, 0o755)

        print(f"✅ Setup script saved to {output_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Smart Defaults & Environment Detection"
    )
    parser.add_argument(
        "--project-root", "-p", default=".", help="Project root directory"
    )
    parser.add_argument(
        "--output", "-o", default="smart-defaults-analysis.json", help="Output file"
    )
    parser.add_argument(
        "--script", "-s", default="setup-cicd.sh", help="Setup script file"
    )
    parser.add_argument("--summary", "-S", action="store_true", help="Print summary")

    args = parser.parse_args()

    # Create smart defaults analyzer
    analyzer = SmartDefaults(args.project_root)

    # Print analysis if requested
    if args.summary:
        analyzer.print_analysis()

    # Save analysis
    analyzer.save_analysis(args.output)

    # Save setup script
    analyzer.save_setup_script(args.script)

    print(f"\n🎉 Smart defaults analysis complete!")
    print(f"📁 Analysis: {args.output}")
    print(f"🚀 Setup script: {args.script}")
    print(f"\n💡 Run './{args.script}' to set up CI/CD with detected values")


if __name__ == "__main__":
    main()
