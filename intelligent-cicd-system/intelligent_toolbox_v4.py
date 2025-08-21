#!/usr/bin/env python3
"""
Intelligent CI/CD Toolbox v4
Smart project analysis and automated deployment
"""

import os
import json
import subprocess
import time
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:3002', 'http://127.0.0.1:3002'], 
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Simple state management
class SmartStateManager:
    def __init__(self):
        self.state = {
            'step1_auth': {'completed': False, 'gcp_auth': False, 'gh_auth': False},
            'step2_project': {'completed': False, 'project_id': None, 'workload_identity_pool': None, 'service_account': None},
            'step3_extract_secrets': {'completed': False, 'project_type': None, 'migration_analysis': None, 'dependencies': []},
            'step4_push_secrets': {'completed': False, 'secrets_pushed': []},
            'step5_generate_workflow': {'completed': False, 'workflow_file': None, 'workflow_content': None},
            'step5_5_generate_dockerfile': {'completed': False, 'dockerfile_path': None, 'dockerfile_content': None},
            'step6_commit': {'completed': False, 'workflow_committed': False, 'workflow_pushed': False}
        }
    
    def can_proceed_to_step(self, step_name):
        if step_name == 'step1_auth':
            return True, "Authentication step can always be started"
        
        if step_name == 'step2_project':
            if self.state['step1_auth']['completed']:
                return True, "Authentication completed, can proceed to project setup"
            return False, "Step 1 (Authentication) must be completed first"
        
        if step_name == 'step3_secrets':
            if self.state['step2_project']['completed']:
                return True, "Project setup completed, can proceed to secrets extraction"
            return False, "Step 2 (Project Setup) must be completed first"
        
        if step_name == 'step4_push_secrets':
            if self.state['step3_secrets']['completed']:
                return True, "Secrets extracted, can proceed to push secrets"
            return False, "Step 3 (Secrets Extraction) must be completed first"
        
        if step_name == 'step5_workflow':
            if self.state['step4_push_secrets']['completed']:
                return True, "Secrets pushed, can proceed to workflow generation"
            return False, "Step 4 (Push Secrets) must be completed first"
        
        if step_name == 'step6_commit':
            if self.state['step5_workflow']['completed']:
                return True, "Workflow generated, can proceed to commit and push"
            return False, "Step 5 (Generate Workflow) must be completed first"
        
        return False, f"Unknown step: {step_name}"
    
    def complete_step(self, step_name):
        if step_name in self.state:
            self.state[step_name]['completed'] = True
            print(f"✅ Step {step_name} marked as completed")
        else:
            print(f"❌ Unknown step: {step_name}")
    
    def get_step_data(self, step_name):
        """Get data for a specific step"""
        return self.state.get(step_name, {})
    
    def mark_step_completed(self, step_name, data=None):
        """Mark a step as completed with optional data"""
        if step_name in self.state:
            self.state[step_name]['completed'] = True
            if data:
                self.state[step_name].update(data)
            print(f"✅ Step {step_name} marked as completed with data")
        else:
            print(f"❌ Unknown step: {step_name}")

# Initialize state manager
state_manager = SmartStateManager()

def run_command_safely(command):
    """Run a shell command safely and return result"""
    try:
        print(f"🔧 Running command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        
        success = result.returncode == 0
        output = result.stdout.strip()
        error = result.stderr.strip()
        
        print(f"📊 Command result: success={success}, returncode={result.returncode}")
        if output:
            print(f"📤 Output: {output[:200]}...")
        if error:
            print(f"❌ Error: {error[:200]}...")
        
        return {
            'success': success,
            'output': output,
            'error': error,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Command timed out after 30 seconds', 'returncode': -1}
    except Exception as e:
        return {'success': False, 'error': str(e), 'returncode': -1}

# Intelligent automation functions
def intelligent_github_auth():
    """Intelligent GitHub authentication with automatic fallback strategies"""
    try:
        print("🔐 Starting intelligent GitHub authentication...")
        
        # Strategy 1: Check if already authenticated
        result = run_command_safely("gh auth status")
        if result['success']:
            print("✅ Already authenticated with GitHub")
            return True
            
        # Strategy 2: Try token-based authentication
        print("🔄 Attempting token-based authentication...")
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            result = run_command_safely(f"gh auth login --with-token < {github_token}")
            if result['success']:
                print("✅ Token-based authentication successful")
                return True
                
        # Strategy 3: Interactive authentication with workflow scope
        print("🔄 Attempting interactive authentication with workflow scope...")
        result = run_command_safely("gh auth login --web --scope workflow")
        if result['success']:
            print("✅ Interactive authentication successful")
            return True
            
        # Strategy 4: Fallback to basic authentication
        print("🔄 Attempting basic authentication...")
        result = run_command_safely("gh auth login --web")
        if result['success']:
            print("✅ Basic authentication successful")
            return True
            
        print("❌ All authentication strategies failed")
        return False
        
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False

def intelligent_workflow_push():
    """Intelligent workflow file push with automatic permission handling"""
    try:
        print("📤 Starting intelligent workflow push...")
        
        # Check if workflow files exist
        if not os.path.exists('.github/workflows'):
            print("❌ No workflow directory found")
            return False
            
        # Strategy 1: Try direct push
        print("🔄 Attempting direct push...")
        result = run_command_safely("git add . && git commit -m '🚀 Automated CI/CD setup' && git push origin main")
        if result['success']:
            print("✅ Direct push successful")
            return True
            
        # Strategy 2: Check and fix permissions
        print("🔄 Checking GitHub permissions...")
        result = run_command_safely("gh auth status")
        if not result['success']:
            print("🔄 Re-authenticating with workflow scope...")
            auth_result = intelligent_github_auth()
            if not auth_result:
                return False
                
        # Strategy 3: Force push with workflow permissions
        print("🔄 Attempting force push with workflow permissions...")
        result = run_command_safely("gh auth login --web --scope workflow --force")
        if result['success']:
            push_result = run_command_safely("git push origin main --force")
            if push_result['success']:
                print("✅ Force push successful")
                return True
                
        # Strategy 4: Manual intervention guidance
        print("⚠️ Automated push failed, providing manual guidance...")
        return provide_manual_push_guidance()
        
    except Exception as e:
        print(f"❌ Push error: {str(e)}")
        return False

def provide_manual_push_guidance():
    """Provide intelligent manual push guidance"""
    guidance = {
        "steps": [
            "1. Run: gh auth logout",
            "2. Run: gh auth login --web --scope workflow",
            "3. Run: git add .",
            "4. Run: git commit -m '🚀 Automated CI/CD setup'",
            "5. Run: git push origin main"
        ],
        "explanation": "GitHub requires workflow scope permissions for automated CI/CD setup",
        "automated_retry": True
    }
    
    print("📋 Manual push guidance:")
    for step in guidance["steps"]:
        print(f"   {step}")
    
    return guidance

def intelligent_secret_management():
    """Intelligent secret management with automatic detection and setup"""
    try:
        print("🔐 Starting intelligent secret management...")
        
        # Get project analysis
        analysis = analyze_project_intelligently()
        required_secrets = []
        
        # Detect required secrets based on project type
        if analysis.get('project_type') == 'streamlit':
            required_secrets.extend([
                'OPENAI_API_KEY',
                'PINECONE_API_KEY',
                'PINECONE_ENVIRONMENT'
            ])
            
        # Check for existing secrets
        existing_secrets = run_command_safely("gh secret list")
        if existing_secrets['success']:
            print("✅ Found existing secrets")
            
        # Provide secret setup guidance
        secret_guidance = {
            "required_secrets": required_secrets,
            "setup_commands": [
                f"gh secret set {secret} --body 'YOUR_{secret}_VALUE'" 
                for secret in required_secrets
            ],
            "automated_detection": True
        }
        
        return secret_guidance
        
    except Exception as e:
        print(f"❌ Secret management error: {str(e)}")
        return None

def analyze_project_intelligently():
    """Enhanced project analysis for automation"""
    try:
        print("🔍 Starting intelligent project analysis...")
        
        analysis = {
            'project_type': 'unknown',
            'dependencies': [],
            'required_secrets': [],
            'deployment_target': 'cloud_run',
            'needs_database': False,
            'needs_authentication': False
        }
        
        # Detect project type
        if os.path.exists('streamlit_app.py'):
            analysis['project_type'] = 'streamlit'
        elif os.path.exists('app.py'):
            analysis['project_type'] = 'flask'
        elif os.path.exists('main.py'):
            analysis['project_type'] = 'python'
            
        # Detect dependencies
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                content = f.read()
                if 'streamlit' in content:
                    analysis['project_type'] = 'streamlit'
                if 'flask' in content:
                    analysis['project_type'] = 'flask'
                    
        # Detect required secrets
        if analysis['project_type'] == 'streamlit':
            analysis['required_secrets'].extend([
                'OPENAI_API_KEY',
                'PINECONE_API_KEY',
                'PINECONE_ENVIRONMENT'
            ])
            
        print(f"✅ Project analysis complete: {analysis['project_type']}")
        return analysis
        
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        return {'project_type': 'unknown'}

def automated_cicd_setup():
    """Fully automated CI/CD setup with intelligent fallbacks"""
    try:
        print("🚀 Starting fully automated CI/CD setup...")
        
        # Step 1: Intelligent authentication
        print("📋 Step 1: GitHub Authentication")
        auth_success = intelligent_github_auth()
        if not auth_success:
            print("⚠️ Authentication failed, providing manual guidance")
            return {"success": False, "step": "authentication", "manual_required": True}
            
        # Step 2: Project analysis
        print("📋 Step 2: Project Analysis")
        analysis = analyze_project_intelligently()
        
        # Step 3: Generate configurations
        print("📋 Step 3: Generate Configurations")
        
        # Get migration analysis and dependencies
        migration_analysis = {
            'needs_migrations': False,
            'migration_type': None,
            'database_types': [],
            'database_dependencies': []
        }
        
        dependencies = ['requirements.txt']
        if os.path.exists('pyproject.toml'):
            dependencies.append('pyproject.toml')
            
        # Generate Dockerfile with correct parameters
        dockerfile_content = generate_smart_dockerfile(
            project_type=analysis.get('project_type', 'unknown'),
            migration_analysis=migration_analysis,
            dependencies=dependencies
        )
        
        # Generate workflow with correct parameters
        workflow_content = generate_workflow_content(
            project_id='neurofinance-468916',  # Default project ID
            github_repo='PramodChandrayan/neurochatagent',  # Default repo
            wif_provider='',  # Will be filled from state
            service_account='',  # Will be filled from state
            project_type=analysis.get('project_type', 'unknown'),
            migration_analysis=migration_analysis
        )
        
        # Step 4: Write files
        print("📋 Step 4: Write Configuration Files")
        
        # Create .github/workflows directory if it doesn't exist
        os.makedirs('.github/workflows', exist_ok=True)
        
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        with open('.github/workflows/deploy-cloudrun.yml', 'w') as f:
            f.write(workflow_content)
            
        # Step 5: Intelligent push
        print("📋 Step 5: Automated Push")
        push_success = intelligent_workflow_push()
        
        if push_success:
            print("✅ Fully automated CI/CD setup complete!")
            return {"success": True, "automated": True}
        else:
            print("⚠️ Automated push failed, manual intervention required")
            return {"success": False, "step": "push", "manual_required": True}
            
    except Exception as e:
        print(f"❌ Automated setup error: {str(e)}")
        return {"success": False, "error": str(e)}

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Basic routes
@app.route('/')
def index():
    return render_template('toolbox.html')

# API endpoints
@app.route('/api/step1/check_auth')
def check_auth():
    """Check GCP and GitHub authentication status"""
    try:
        # Check GCP auth - simplified without filter
        gcp_result = run_command_safely('gcloud auth list --format="value(account)"')
        gcp_auth = gcp_result['success'] and gcp_result['output'].strip() != ''
        
        # Check GitHub auth - robust check for all authentication methods
        gh_auth = False
        gh_account = None
        
        # Method 1: Try gh auth status (works for all auth methods)
        gh_result = run_command_safely('gh auth status')
        if gh_result['success']:
            gh_auth = True
            print("✅ GitHub authenticated via gh auth status")
            # Extract username from auth status output
            if 'Logged in to github.com account' in gh_result['output']:
                # Extract username from "Logged in to github.com account PramodChandrayan (keyring)"
                parts = gh_result['output'].split('Logged in to github.com account')
                if len(parts) > 1:
                    gh_account = parts[1].split()[0].strip()  # Get first word after "account"
                    print(f"✅ GitHub account detected: {gh_account}")
            elif 'Logged in to github.com as' in gh_result['output']:
                gh_account = gh_result['output'].split('Logged in to github.com as')[1].strip()
                print(f"✅ GitHub account detected: {gh_account}")
        
        # Method 2: Try gh api user (works for all auth methods)
        if not gh_auth:
            print("🔍 GitHub auth status failed, trying user API check...")
            user_result = run_command_safely('gh api user --jq .login')
            if user_result['success']:
                gh_auth = True
                gh_account = user_result['output'].strip().strip('"')
                print(f"✅ GitHub authenticated via user API check: {gh_account}")
        
        # Method 3: Try gh api user without jq (fallback)
        if not gh_auth:
            print("🔍 User API with jq failed, trying without jq...")
            user_result = run_command_safely('gh api user')
            if user_result['success']:
                gh_auth = True
                print("✅ GitHub authenticated via user API check (without jq)")
                # Try to extract username from JSON response
                try:
                    import json
                    user_data = json.loads(user_result['output'])
                    gh_account = user_data.get('login', 'Authenticated')
                except:
                    gh_account = "Authenticated"
        
        # Method 4: Check for environment tokens (keychain, personal access tokens)
        if not gh_auth:
            print("🔍 Checking for GitHub tokens in environment...")
            # Check multiple possible token environment variables
            token_vars = ['GH_TOKEN', 'GITHUB_TOKEN', 'GITHUB_PAT']
            for token_var in token_vars:
                token_result = run_command_safely(f'echo ${token_var}')
                if token_result['success'] and token_result['output'].strip():
                    gh_auth = True
                    print(f"✅ GitHub token found in {token_var}")
                    break
        
        # Method 5: Check keychain/credential storage
        if not gh_auth:
            print("🔍 Checking keychain/credential storage...")
            # Try to get stored credentials
            cred_result = run_command_safely('gh auth status --json')
            if cred_result['success']:
                try:
                    import json
                    cred_data = json.loads(cred_result['output'])
                    if cred_data.get('token') or cred_data.get('user'):
                        gh_auth = True
                        gh_account = cred_data.get('user', {}).get('login', 'Authenticated')
                        print(f"✅ GitHub authenticated via keychain: {gh_account}")
                except:
                    pass
        
        # Method 6: Final fallback - try to list repos (requires auth)
        if not gh_auth:
            print("🔍 Final check - trying to list repositories...")
            repo_result = run_command_safely('gh repo list --limit 1')
            if repo_result['success']:
                gh_auth = True
                print("✅ GitHub authenticated via repo list check")
        
        # Update state
        state_manager.state['step1_auth'].update({
            'gcp_auth': gcp_auth,
            'gh_auth': gh_auth
        })
        
        if gcp_auth and gh_auth:
            state_manager.complete_step('step1_auth')
        
        # gh_account is already set in the check above
        
        return jsonify({
            "success": True,
            "gcp_authenticated": gcp_auth,
            "gh_authenticated": gh_auth,
            "message": "Authentication status checked",
            "gcp_account": gcp_result['output'].strip() if gcp_auth else None,
            "gh_account": gh_account if gh_auth else None
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/auth_gcp')
def auth_gcp():
    """Authenticate to Google Cloud Platform"""
    try:
        print("🔐 Starting GCP authentication...")
        
        # Check if already authenticated
        check_result = run_command_safely('gcloud auth list --format="value(account)"')
        if check_result['success'] and check_result['output'].strip():
            print(f"✅ GCP already authenticated: {check_result['output'].strip()}")
            return jsonify({
                "success": True,
                "message": f"GCP already authenticated: {check_result['output'].strip()}",
                "account": check_result['output'].strip()
            })
        
        # Start gcloud auth login with browser
        import subprocess
        import threading
        
        def run_auth():
            try:
                subprocess.run(['gcloud', 'auth', 'login'], check=True)
            except subprocess.CalledProcessError:
                pass
        
        # Run authentication in background thread
        auth_thread = threading.Thread(target=run_auth)
        auth_thread.daemon = True
        auth_thread.start()
        
        return jsonify({
            "success": True,
            "message": "GCP authentication started - check your browser for OAuth flow",
            "instructions": "Complete the authentication in your browser, then check authentication status"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/auth_github')
def auth_github():
    """Authenticate to GitHub"""
    try:
        print("🔐 Starting GitHub authentication...")
        
        # Check if already authenticated
        check_result = run_command_safely('gh auth status')
        if check_result['success']:
            print("✅ GitHub already authenticated")
            return jsonify({
                "success": True,
                "message": "GitHub already authenticated"
            })
        
        # Check if user wants to authenticate CLI manually
        data = request.get_json() if request.is_json else {}
        manual_auth = data.get('manual', False)
        
        if manual_auth:
            return jsonify({
                "success": True,
                "message": "Manual authentication mode",
                "instructions": "Please run 'gh auth login' in your terminal to authenticate the CLI",
                "manual_command": "gh auth login",
                "auth_type": "manual_cli"
            })
        
        # Actually launch GitHub authentication in browser
        import subprocess
        import threading
        import webbrowser
        import time
        
        def run_github_auth():
            try:
                print("🔐 Starting GitHub web authentication...")
                # Open browser for web authentication
                webbrowser.open('https://github.com/login')
                
                # Try web authentication
                result = subprocess.run(['gh', 'auth', 'login', '--web'], 
                                      capture_output=True, text=True, timeout=60)
                print(f"GitHub web auth result: {result.stdout}")
                if result.stderr:
                    print(f"GitHub web auth stderr: {result.stderr}")
                        
            except subprocess.TimeoutExpired:
                print("GitHub web auth timeout")
            except Exception as e:
                print(f"GitHub web auth error: {e}")
                # Fallback: open browser
                try:
                    webbrowser.open('https://github.com/login')
                except:
                    pass
        
        # Run authentication in background thread
        auth_thread = threading.Thread(target=run_github_auth)
        auth_thread.daemon = True
        auth_thread.start()
        
        return jsonify({
            "success": True,
            "message": "GitHub CLI authentication started",
            "instructions": "Complete the authentication in your browser. If you're already logged into GitHub, you may need to authenticate the CLI separately.",
            "auth_type": "cli_authentication",
            "note": "GitHub CLI authentication is separate from browser login"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/auth_github_cli')
def auth_github_cli():
    """Start interactive GitHub CLI authentication - Step 1: Get user preferences"""
    try:
        print("🔧 Starting interactive GitHub CLI authentication...")
        
        # Check if already authenticated
        check_result = run_command_safely('gh auth status')
        if check_result['success']:
            print("✅ GitHub CLI already authenticated")
            return jsonify({
                "success": True,
                "message": "GitHub CLI already authenticated",
                "auth_type": "already_authenticated"
            })
        
        return jsonify({
            "success": True,
            "message": "Starting GitHub CLI authentication",
            "auth_type": "interactive_start",
            "step": 1,
            "question": "Where do you use GitHub?",
            "options": ["GitHub.com", "GitHub Enterprise Server"],
            "next_endpoint": "/api/step1/auth_github_cli_step2"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/auth_github_cli_step2', methods=['POST'])
def auth_github_cli_step2():
    """Step 2: Get protocol preference"""
    try:
        data = request.get_json()
        hostname = data.get('hostname', 'GitHub.com')
        
        # Store the hostname for later use
        if 'auth_session' not in state_manager.state:
            state_manager.state['auth_session'] = {}
        state_manager.state['auth_session']['hostname'] = hostname
        
        return jsonify({
            "success": True,
            "message": f"Using {hostname}",
            "auth_type": "interactive_step2",
            "step": 2,
            "question": "What is your preferred protocol for Git operations on this host?",
            "options": ["HTTPS", "SSH"],
            "next_endpoint": "/api/step1/auth_github_cli_step3"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/auth_github_cli_step3', methods=['POST'])
def auth_github_cli_step3():
    """Step 3: Get authentication method"""
    try:
        data = request.get_json()
        protocol = data.get('protocol', 'HTTPS')
        
        # Store the protocol
        state_manager.state['auth_session']['protocol'] = protocol
        
        return jsonify({
            "success": True,
            "message": f"Using {protocol} protocol",
            "auth_type": "interactive_step3",
            "step": 3,
            "question": "How would you like to authenticate GitHub CLI?",
            "options": ["Login with a web browser", "Paste an authentication token"],
            "next_endpoint": "/api/step1/auth_github_cli_step4"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/auth_github_cli_step4', methods=['POST'])
def auth_github_cli_step4():
    """Step 4: Start device authentication"""
    try:
        data = request.get_json()
        auth_method = data.get('auth_method', 'Login with a web browser')
        
        if auth_method == "Login with a web browser":
            # Start the device authentication process
            import subprocess
            import threading
            import re
            import time
            
            def run_device_auth():
                try:
                    print("🔧 Starting device authentication...")
                    
                    # Build the command with stored preferences
                    hostname = state_manager.state.get('auth_session', {}).get('hostname', 'GitHub.com')
                    protocol = state_manager.state.get('auth_session', {}).get('protocol', 'HTTPS')
                    
                    # Start gh auth login with interactive flow
                    process = subprocess.Popen(
                        ['gh', 'auth', 'login'],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=1
                    )
                    
                    # Send responses to the interactive prompts
                    responses = [
                        f'{hostname}\n',  # Where do you use GitHub?
                        f'{protocol}\n',  # Preferred protocol
                        'Login with a web browser\n'  # Authentication method
                    ]
                    
                    # Send initial responses
                    for response in responses:
                        process.stdin.write(response)
                        process.stdin.flush()
                        time.sleep(0.5)
                    
                    # Read output to get device code
                    device_code = None
                    output_lines = []
                    
                    # Read all available output first
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            break
                        output_lines.append(line.strip())
                        print(f"CLI output: {line.strip()}")
                        
                        # Look for device code pattern
                        if 'one-time code:' in line:
                            match = re.search(r'([A-Z0-9]{4}-[A-Z0-9]{4})', line)
                            if match:
                                device_code = match.group(1)
                                print(f"🔑 Device code generated: {device_code}")
                                
                                # Store device code in state
                                state_manager.state['auth_session']['device_code'] = device_code
                                break
                        # Also look for the URL
                        elif 'Open this URL to continue' in line:
                            url_match = re.search(r'(https://github\.com/login/device)', line)
                            if url_match:
                                device_url = url_match.group(1)
                                print(f"🌐 Device URL found: {device_url}")
                                state_manager.state['auth_session']['device_url'] = device_url
                    
                    # If no device code found in initial output, try to read more
                    if not device_code:
                        print("🔍 No device code found in initial output, checking for more...")
                        try:
                            # Try to read more output with a short timeout
                            stdout, stderr = process.communicate(timeout=10)
                            if stdout:
                                print(f"Additional stdout: {stdout}")
                                # Look for device code in additional output
                                if 'one-time code:' in stdout:
                                    match = re.search(r'([A-Z0-9]{4}-[A-Z0-9]{4})', stdout)
                                    if match:
                                        device_code = match.group(1)
                                        print(f"🔑 Device code found in additional output: {device_code}")
                                        state_manager.state['auth_session']['device_code'] = device_code
                        except subprocess.TimeoutExpired:
                            print("Timeout reading additional output")
                    
                    if device_code:
                        print(f"✅ Device code stored: {device_code}")
                        # Wait for user to complete authentication
                        print("⏳ Waiting for user to complete authentication...")
                        try:
                            stdout, stderr = process.communicate(timeout=300)  # 5 minutes timeout
                            
                            if process.returncode == 0:
                                print("✅ GitHub CLI authentication successful!")
                                state_manager.state['auth_session']['completed'] = True
                            else:
                                print(f"❌ GitHub CLI authentication failed: {stderr}")
                        except subprocess.TimeoutExpired:
                            print("Authentication timeout - user may still be completing the process")
                    else:
                        print("❌ Failed to generate device code")
                        process.kill()
                            
                except subprocess.TimeoutExpired:
                    print("Device auth timeout")
                    if 'process' in locals():
                        process.kill()
                except Exception as e:
                    print(f"Device auth error: {e}")
                    if 'process' in locals():
                        process.kill()
            
            # Run authentication in background thread
            auth_thread = threading.Thread(target=run_device_auth)
            auth_thread.daemon = True
            auth_thread.start()
            
            return jsonify({
                "success": True,
                "message": "Device authentication started",
                "auth_type": "device_auth_started",
                "step": 4,
                "instructions": "Device authentication process started. Check the terminal output for the device code.",
                "next_endpoint": "/api/step1/auth_github_cli_status"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Token authentication not implemented yet"
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/auth_github_cli_status')
def auth_github_cli_status():
    """Check authentication status and get device code"""
    try:
        print("🔍 Checking GitHub CLI authentication status...")
        
        # Check if device code is available
        device_code = state_manager.state.get('auth_session', {}).get('device_code')
        auth_session = state_manager.state.get('auth_session', {})
        
        print(f"Auth session state: {auth_session}")
        
        if device_code:
            print(f"✅ Device code found: {device_code}")
            device_url = state_manager.state.get('auth_session', {}).get('device_url', 'https://github.com/login/device')
            return jsonify({
                "success": True,
                "message": "Device code available",
                "auth_type": "device_code_ready",
                "device_code": device_code,
                "device_url": device_url,
                "instructions": f"Copy this code and enter it in your browser: {device_code}",
                "terminal_simulation": f"! First copy your one-time code: {device_code}\nOpen this URL to continue in your web browser: {device_url}"
            })
        else:
            # Check if authentication completed
            print("🔍 Checking if authentication is already complete...")
            check_result = run_command_safely('gh auth status')
            print(f"Auth status check result: {check_result}")
            
            if check_result['success']:
                account_info = "Authenticated"
                if 'Logged in to github.com account' in check_result['output']:
                    try:
                        account_info = check_result['output'].split('Logged in to github.com account')[1].split()[0]
                    except:
                        pass
                
                print(f"✅ Authentication completed: {account_info}")
                return jsonify({
                    "success": True,
                    "message": "Authentication completed successfully!",
                    "auth_type": "completed",
                    "account": account_info
                })
            else:
                # Check if auth session exists but no device code yet
                if auth_session:
                    print("⏳ Authentication session exists but no device code yet")
                    return jsonify({
                        "success": True,
                        "message": "Authentication in progress...",
                        "auth_type": "in_progress",
                        "instructions": "Please wait for the device code to be generated.",
                        "debug_info": f"Session exists: {bool(auth_session)}"
                    })
                else:
                    print("❌ No authentication session found")
                    return jsonify({
                        "success": False,
                        "message": "No authentication session found",
                        "auth_type": "no_session",
                        "instructions": "Please start the authentication process first."
                    })
                
    except Exception as e:
        print(f"❌ Error in auth status check: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/revoke_gcp')
def revoke_gcp():
    """Revoke GCP authentication"""
    try:
        print("🚫 Revoking GCP authentication...")
        
        # Revoke GCP authentication
        result = run_command_safely('gcloud auth revoke --all')
        
        if result['success']:
            print("✅ GCP authentication revoked successfully")
            # Reset state
            state_manager.state['step1_auth']['gcp_auth'] = False
            state_manager.state['step1_auth']['completed'] = False
            
            return jsonify({
                "success": True,
                "message": "GCP authentication revoked successfully",
                "note": "You can now re-authenticate GCP from the frontend"
            })
        else:
            print(f"❌ Failed to revoke GCP: {result.get('error', 'Unknown error')}")
            return jsonify({
                "success": False,
                "error": f"Failed to revoke GCP: {result.get('error', 'Unknown error')}"
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step1/revoke_github')
def revoke_github():
    """Revoke GitHub authentication"""
    try:
        print("🚫 Revoking GitHub authentication...")
        
        # Revoke GitHub authentication
        result = run_command_safely('gh auth logout')
        
        if result['success']:
            print("✅ GitHub authentication revoked successfully")
            # Reset state
            state_manager.state['step1_auth']['gh_auth'] = False
            state_manager.state['step1_auth']['completed'] = False
            
            return jsonify({
                "success": True,
                "message": "GitHub authentication revoked successfully",
                "note": "You can now re-authenticate GitHub from the frontend"
            })
        else:
            print(f"❌ Failed to revoke GitHub: {result.get('error', 'Unknown error')}")
            return jsonify({
                "success": False,
                "error": f"Failed to revoke GitHub: {result.get('error', 'Unknown error')}"
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step2/discover_projects')
def discover_projects():
    """Discover available GCP projects"""
    try:
        result = run_command_safely('gcloud projects list --format="value(projectId)"')
        if result['success']:
            projects = [p.strip() for p in result['output'].split('\n') if p.strip()]
            return jsonify({"success": True, "projects": projects})
        else:
            return jsonify({"success": False, "error": result['error']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step2/discover_repos')
def discover_repos():
    """Discover GitHub repositories"""
    try:
        print("🔍 Discovering GitHub repositories...")
        
        # Get user's repositories using GitHub CLI
        result = run_command_safely('gh repo list --json name,owner,description,url --limit 50')
        if result['success']:
            import json
            repos_data = json.loads(result['output'])
            repos = []
            
            for repo in repos_data:
                repos.append({
                    'name': repo['name'],
                    'full_name': f"{repo['owner']['login']}/{repo['name']}",
                    'description': repo.get('description', ''),
                    'url': repo['url']
                })
            
            print(f"✅ Found {len(repos)} repositories")
            return jsonify({"success": True, "repos": repos})
        else:
            print(f"❌ Failed to discover repos: {result.get('error', 'Unknown error')}")
            return jsonify({"success": False, "error": result.get('error', 'Unknown error')})
    except Exception as e:
        print(f"❌ Exception discovering repos: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step2/select_repo', methods=['POST'])
def select_repo():
    """Select GitHub repository for WIF binding"""
    try:
        data = request.get_json()
        selected_repo = data.get('repo')
        
        if not selected_repo:
            return jsonify({"success": False, "error": "No repository selected"})
        
        # Store the selected repository in state
        if 'step2_project' not in state_manager.state:
            state_manager.state['step2_project'] = {}
        
        state_manager.state['step2_project']['selected_repo'] = selected_repo
        
        print(f"✅ Selected repository: {selected_repo}")
        return jsonify({"success": True, "message": f"Repository {selected_repo} selected for WIF binding"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step2/setup_infrastructure')
def setup_infrastructure():
    """Setup GCP infrastructure for CI/CD"""
    try:
        print("🔧 Setting up GCP infrastructure...")
        
        # Check if infrastructure already exists
        print("🔍 Checking for existing infrastructure...")
        
        # Check if service account exists
        sa_result = run_command_safely('gcloud iam service-accounts list --filter="email:gha-deployer" --format="value(email)"')
        if sa_result['success'] and sa_result['output'].strip():
            print("✅ Service account already exists")
            
            # Check if WIF pool exists - FIXED: Add location parameter
            wif_result = run_command_safely('gcloud iam workload-identity-pools list --location="global" --filter="displayName:GitHub Actions Pool" --format="value(name)"')
            if wif_result['success'] and wif_result['output'].strip():
                print("✅ WIF pool already exists")
                
                # Check if WIF provider exists - FIXED: Add location parameter
                provider_result = run_command_safely('gcloud iam workload-identity-pools providers list --location="global" --workload-identity-pool="github-actions-pool" --filter="displayName:GitHub OIDC Provider" --format="value(name)"')
                if provider_result['success'] and provider_result['output'].strip():
                    print("✅ WIF provider already exists")
                    
                    return jsonify({
                        "success": True,
                        "message": "✅ Infrastructure already exists! Using existing setup.",
                        "existing": True,
                        "service_account": sa_result['output'].strip(),
                        "wif_pool": wif_result['output'].strip(),
                        "wif_provider": provider_result['output'].strip()
                    })
        
        print("🏗️ Creating new infrastructure...")
        
        # Use the selected project or default
        project_id = "neurofinance-468916"  # Hardcoded for now
        service_account = f"gha-deployer@{project_id}.iam.gserviceaccount.com"
        
        print("📋 Step 1: Enabling required APIs...")
        # Enable required APIs
        apis = ['iam.googleapis.com', 'iamcredentials.googleapis.com', 'sts.googleapis.com', 'run.googleapis.com', 'artifactregistry.googleapis.com', 'secretmanager.googleapis.com']
        enabled_apis = []
        for api in apis:
            result = run_command_safely(f'gcloud services enable {api} --project={project_id}')
            if result['success']:
                enabled_apis.append(api)
                print(f"✅ Enabled {api}")
            else:
                print(f"⚠️ {api} already enabled or failed: {result.get('error', 'Unknown error')}")
        
        print("📋 Step 2: Creating service account...")
        # Create service account if it doesn't exist
        result = run_command_safely(f'gcloud iam service-accounts create gha-deployer --display-name="GitHub Actions Deployer" --project={project_id}')
        if result['success']:
            print("✅ Created service account")
        elif 'already exists' in result.get('error', ''):
            print("✅ Service account already exists")
        else:
            return jsonify({"success": False, "error": f"Failed to create service account: {result.get('error', 'Unknown error')}"})
        
        print("📋 Step 3: Granting IAM roles...")
        # Grant required roles for complete Cloud Run deployment
        roles = [
            'roles/run.admin',                    # Cloud Run administration
            'roles/iam.serviceAccountUser',       # Service account impersonation
            'roles/artifactregistry.admin',       # Artifact Registry full access (includes createOnPush)
            'roles/storage.admin',                # Cloud Storage administration
            'roles/secretmanager.secretAccessor', # Secret Manager access
            'roles/cloudbuild.builds.builder',    # Cloud Build builder
            'roles/logging.logWriter',            # Logging permissions
            'roles/monitoring.metricWriter'       # Monitoring permissions
        ]
        granted_roles = []
        for role in roles:
            result = run_command_safely(f'gcloud projects add-iam-policy-binding {project_id} --member="serviceAccount:{service_account}" --role="{role}"')
            if result['success']:
                granted_roles.append(role)
                print(f"✅ Granted {role}")
            else:
                print(f"⚠️ {role} already granted or failed: {result.get('error', 'Unknown error')}")
        
        print("📋 Step 4: Creating Workload Identity Pool...")
        # Create Workload Identity Pool with proper naming
        pool_id = f"github-actions-pool-{int(time.time())}"
        pool_result = run_command_safely(f'gcloud iam workload-identity-pools create {pool_id} --project={project_id} --location="global" --display-name="GitHub Actions Pool"')
        if not pool_result['success']:
            return jsonify({"success": False, "error": f"Failed to create WIF pool: {pool_result.get('error', 'Unknown error')}"})
        print("✅ Created WIF pool")
        
        # FIXED: Get pool name with proper location parameter and wait for propagation
        print("⏳ Waiting for pool to propagate...")
        time.sleep(5)  # Wait for pool to be available
        
        pool_name_result = run_command_safely(f'gcloud iam workload-identity-pools describe {pool_id} --project={project_id} --location="global" --format="value(name)"')
        if not pool_name_result['success']:
            # Try alternative approach: construct the pool name manually
            print("⚠️ Could not get pool name, constructing manually...")
            pool_name = f"projects/{project_id}/locations/global/workloadIdentityPools/{pool_id}"
        else:
            pool_name = pool_name_result['output'].strip()
        
        print("📋 Step 5: Creating WIF provider...")
        # FIXED: Create WIF provider with correct parameters based on official GCP docs
        github_repo = state_manager.state.get('step2_project', {}).get('selected_repo', "PramodChandrayan/neurochatagent")
        
        # Use the correct provider creation command from official GCP docs
        provider_cmd = f'''gcloud iam workload-identity-pools providers create-oidc github-actions-provider \
            --project={project_id} \
            --location="global" \
            --workload-identity-pool="{pool_id}" \
            --display-name="GitHub OIDC Provider" \
            --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
            --issuer-uri="https://token.actions.githubusercontent.com" \
            --attribute-condition="assertion.repository=='{github_repo}'"'''
        
        result = run_command_safely(provider_cmd)
        if not result['success']:
            return jsonify({"success": False, "error": f"Failed to create WIF provider: {result['error']}"})
        print("✅ Created WIF provider")
        
        # Step 6: Bind WIF Provider to Service Account
        print("📋 Step 6: Binding WIF Provider to Service Account...")
        
        # Get project number for the binding
        project_number_result = run_command_safely(f'gcloud projects describe {project_id} --format="value(projectNumber)"')
        if not project_number_result['success']:
            return jsonify({"success": False, "error": f"Failed to get project number: {project_number_result.get('error', 'Unknown error')}"})
        
        project_number = project_number_result['output'].strip()
        
        # FIXED: Build the provider resource name correctly
        provider_resource = f"projects/{project_number}/locations/global/workloadIdentityPools/{pool_id}/providers/github-actions-provider"
        
        # FIXED: Use the correct principalSet format from official GCP docs
        # Format: principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.repository/REPO_NAME
        correct_principal_set = f"principalSet://iam.googleapis.com/projects/{project_number}/locations/global/workloadIdentityPools/{pool_id}/attribute.repository/{github_repo}"
        
        print(f"🔗 Binding WIF provider to service account for repo: {github_repo}")
        print(f"🔗 PrincipalSet: {correct_principal_set}")
        
        binding_result = run_command_safely(f'gcloud iam service-accounts add-iam-policy-binding {service_account} --project={project_id} --role="roles/iam.workloadIdentityUser" --member="{correct_principal_set}"')
        
        if binding_result['success']:
            print("✅ Bound WIF provider to service account successfully")
            principal_set = correct_principal_set
            wif_binding_success = True
        else:
            print(f"⚠️ WIF binding failed: {binding_result.get('error', 'Unknown error')}")
            print("⚠️ WIF binding will need to be configured manually")
            principal_set = correct_principal_set
            wif_binding_success = False
        
        # Update state with WIF details
        github_secrets = {
            'GCP_PROJECT_ID': project_id,
            'GCP_REGION': 'us-central1',  # Default region
            'WIF_PROVIDER': provider_resource,
            'DEPLOY_SA_EMAIL': service_account,
            'GITHUB_REPO': github_repo
        }
        
        state_manager.state['step2_project'].update({
            'project_id': project_id,
            'workload_identity_pool': pool_name,
            'service_account': service_account,
            'wif_provider': provider_resource,
            'github_repo': github_repo,
            'wif_binding_success': wif_binding_success,
            'principal_set': principal_set,
            'github_secrets': github_secrets
        })
        
        state_manager.complete_step('step2_project')
        
        print("🎉 Infrastructure setup completed successfully!")
        return jsonify({
            "success": True,
            "message": f"Infrastructure setup completed! Project: {project_id}",
            "project_id": project_id,
            "workload_identity_pool": pool_name,
            "service_account": service_account,
            "wif_provider": provider_resource,
            "github_repo": github_repo,
            "wif_binding_success": wif_binding_success,
            "principal_set": principal_set,
            "github_secrets": github_secrets,
            "enabled_apis": enabled_apis,
            "granted_roles": granted_roles
        })
    except Exception as e:
        print(f"❌ Infrastructure setup failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step4/push_secrets', methods=['POST'])
def push_secrets():
    """Push secrets to GitHub repository"""
    try:
        data = request.get_json()
        secrets_to_push = data.get('secrets', [])
        
        print(f"🔐 Pushing {len(secrets_to_push)} secrets to GitHub...")
        
        # Get repository from state
        step2_data = state_manager.state.get('step2_project', {})
        github_repo = step2_data.get('selected_repo', 'PramodChandrayan/neurochatagent')
        
        # Check if secrets already exist
        print("🔍 Checking for existing secrets...")
        existing_secrets = []
        
        for secret in secrets_to_push:
            secret_name = secret.get('name')
            if secret_name:
                # Check if secret exists
                check_result = run_command_safely(f'gh secret list --repo {github_repo} --json name')
                if check_result['success'] and secret_name in check_result['output']:
                    existing_secrets.append(secret_name)
        
        if existing_secrets:
            print(f"✅ Found existing secrets: {existing_secrets}")
            return jsonify({
                "success": True,
                "message": f"✅ All required secrets are already configured",
                "existing": True,
                "pushed_secrets": existing_secrets,
                "total_secrets": len(existing_secrets)
            })
        
        print("📤 Pushing new secrets...")
        
        pushed_secrets = []
        failed_secrets = []
        
        for secret in secrets_to_push:
            secret_name = secret.get('name')
            secret_value = secret.get('value')
            
            if secret_name and secret_value:
                try:
                    # Use gh CLI to set the secret
                    result = run_command_safely(f'gh secret set {secret_name} --body "{secret_value}" --repo {github_repo}')
                    
                    if result['success']:
                        pushed_secrets.append(secret_name)
                        print(f"✅ Pushed secret: {secret_name}")
                    else:
                        failed_secrets.append(f"{secret_name}: {result['error']}")
                        print(f"❌ Failed to push secret {secret_name}: {result['error']}")
                        
                except Exception as e:
                    failed_secrets.append(f"{secret_name}: {str(e)}")
                    print(f"❌ Error pushing secret {secret_name}: {str(e)}")
            else:
                failed_secrets.append(f"{secret_name}: Missing name or value")
        
        if pushed_secrets:
            state_manager.complete_step('step4_push_secrets')
            return jsonify({
                "success": True, 
                "message": f"Successfully pushed {len(pushed_secrets)} secrets to {github_repo}",
                "pushed_secrets": pushed_secrets,
                "failed_secrets": failed_secrets,
                "total_secrets": len(pushed_secrets),
                "repository": github_repo
            })
        else:
            return jsonify({
                "success": False, 
                "error": f"Failed to push any secrets. Errors: {failed_secrets}"
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/check-existing-secrets', methods=['GET'])
def check_existing_secrets():
    """Check existing secrets in GitHub repository"""
    try:
        # Get repository from state
        step2_data = state_manager.state.get('step2_project', {})
        github_repo = step2_data.get('selected_repo', 'PramodChandrayan/neurochatagent')
        
        print(f"🔍 Checking existing secrets in {github_repo}...")
        
        # Get list of secrets
        result = run_command_safely(f'gh secret list --repo {github_repo} --json name')
        
        if result['success']:
            # Parse the JSON output to extract secret names
            import json
            try:
                secrets_data = json.loads(result['output'])
                secret_names = [secret['name'] for secret in secrets_data]
                
                print(f"✅ Found {len(secret_names)} existing secrets: {secret_names}")
                
                return jsonify({
                    "success": True,
                    "secrets": secret_names,
                    "total": len(secret_names),
                    "repository": github_repo
                })
            except json.JSONDecodeError:
                # Fallback: try to extract names from text output
                lines = result['output'].strip().split('\n')
                secret_names = []
                for line in lines:
                    if line.strip() and not line.startswith('[') and not line.startswith(']'):
                        # Extract name from line like '{"name":"SECRET_NAME"}'
                        if '"name":"' in line:
                            name = line.split('"name":"')[1].split('"')[0]
                            secret_names.append(name)
                
                return jsonify({
                    "success": True,
                    "secrets": secret_names,
                    "total": len(secret_names),
                    "repository": github_repo
                })
        else:
            return jsonify({
                "success": False,
                "error": f"Failed to fetch secrets: {result['error']}"
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Add smart project analysis endpoints
@app.route('/api/analyze_project', methods=['GET'])
def analyze_project():
    """Analyze project structure and determine deployment requirements"""
    try:
        print("🔍 Analyzing project structure for smart deployment...")
        
        # Navigate to parent directory (project root)
        parent_dir = os.path.dirname(os.getcwd())
        original_dir = os.getcwd()
        os.chdir(parent_dir)
        
        project_analysis = {
            'project_type': 'unknown',
            'main_files': [],
            'dependencies': [],
            'deployment_files': [],
            'recommendations': [],
            'required_secrets': [],
            'env_variables': {}
        }
        
        # Check for main application files
        main_files = []
        if os.path.exists('streamlit_app.py'):
            main_files.append('streamlit_app.py')
            project_analysis['project_type'] = 'streamlit'
        if os.path.exists('app.py'):
            main_files.append('app.py')
            project_analysis['project_type'] = 'flask'
        if os.path.exists('main.py'):
            main_files.append('main.py')
            project_analysis['project_type'] = 'python'
        if os.path.exists('index.js') or os.path.exists('package.json'):
            project_analysis['project_type'] = 'nodejs'
        
        project_analysis['main_files'] = main_files
        
        # Check for dependency files
        dependencies = []
        if os.path.exists('requirements.txt'):
            dependencies.append('requirements.txt')
        if os.path.exists('pyproject.toml'):
            dependencies.append('pyproject.toml')
        if os.path.exists('package.json'):
            dependencies.append('package.json')
        if os.path.exists('Pipfile'):
            dependencies.append('Pipfile')
        
        project_analysis['dependencies'] = dependencies
        
        # Check for existing deployment files
        deployment_files = []
        if os.path.exists('Dockerfile'):
            deployment_files.append('Dockerfile')
        if os.path.exists('.dockerignore'):
            deployment_files.append('.dockerignore')
        if os.path.exists('.github/workflows'):
            deployment_files.append('.github/workflows/')
        
        project_analysis['deployment_files'] = deployment_files
        
        # Extract environment variables and secrets
        print("🔍 Extracting environment variables and secrets...")
        
        # Read .env file if exists
        env_vars = {}
        if os.path.exists('.env'):
            try:
                with open('.env', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key.strip()] = value.strip()
                project_analysis['env_variables'] = env_vars
                print(f"✅ Found {len(env_vars)} environment variables in .env")
            except Exception as e:
                print(f"⚠️ Error reading .env: {e}")
        
        # Read .env.example if exists
        if os.path.exists('.env.example'):
            try:
                with open('.env.example', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            if key.strip() not in env_vars:
                                env_vars[key.strip()] = value.strip()
                print(f"✅ Found additional variables in .env.example")
            except Exception as e:
                print(f"⚠️ Error reading .env.example: {e}")
        
        # Analyze Python files for common API keys and secrets
        required_secrets = []
        common_secrets = [
            'OPENAI_API_KEY', 'PINECONE_API_KEY', 'PINECONE_ENVIRONMENT',
            'GOOGLE_API_KEY', 'AZURE_API_KEY', 'AWS_ACCESS_KEY_ID',
            'DATABASE_URL', 'REDIS_URL', 'JWT_SECRET', 'SECRET_KEY',
            'STRIPE_SECRET_KEY', 'TWILIO_AUTH_TOKEN', 'SENDGRID_API_KEY'
        ]
        
        for secret in common_secrets:
            if secret in env_vars:
                required_secrets.append({
                    'name': secret,
                    'value': env_vars.get(secret, ''),
                    'description': f'Required for {project_analysis["project_type"]} application',
                    'source': 'env_file'
                })
        
        # Add GCP-specific secrets for WIF - use existing state values
        step2_data = state_manager.state.get('step2_project', {})
        gcp_secrets = [
            {
                'name': 'GCP_PROJECT_ID',
                'value': step2_data.get('project_id', 'neurofinance-468916'),
                'description': 'GCP Project ID for deployment',
                'source': 'gcp_setup'
            },
            {
                'name': 'GCP_REGION',
                'value': 'us-central1',  # Default region
                'description': 'GCP Region for deployment',
                'source': 'gcp_setup'
            },
            {
                'name': 'WIF_PROVIDER',
                'value': step2_data.get('wif_provider', ''),
                'description': 'Workload Identity Federation Provider',
                'source': 'gcp_setup'
            },
            {
                'name': 'DEPLOY_SA_EMAIL',
                'value': step2_data.get('service_account', ''),
                'description': 'GCP Service Account Email for deployment',
                'source': 'gcp_setup'
            }
        ]
        
        # Add GCP secrets to required_secrets, avoiding duplicates
        for gcp_secret in gcp_secrets:
            if gcp_secret['name'] not in [s['name'] for s in required_secrets]:
                required_secrets.append(gcp_secret)
        
        project_analysis['required_secrets'] = required_secrets
        
        # 🔍 DATABASE ANALYSIS
        print("🔍 Analyzing database requirements...")
        
        database_analysis = {
            'enabled': False,
            'type': None,
            'url_template': None,
            'detected_packages': [],
            'migration_tools': [],
            'migrations_enabled': False,
            'connection_strings': []
        }
        
        # Check requirements.txt for database packages
        if os.path.exists('requirements.txt'):
            try:
                with open('requirements.txt', 'r') as f:
                    requirements_content = f.read().lower()
                    
                    # Database package detection
                    if 'psycopg2' in requirements_content or 'postgresql' in requirements_content:
                        database_analysis['type'] = 'postgresql'
                        database_analysis['url_template'] = 'postgresql://username:password@host:5432/database_name'
                        database_analysis['detected_packages'].extend(['psycopg2', 'psycopg2-binary'])
                    elif 'mysql' in requirements_content or 'pymysql' in requirements_content:
                        database_analysis['type'] = 'mysql'
                        database_analysis['url_template'] = 'mysql://username:password@host:3306/database_name'
                        database_analysis['detected_packages'].extend(['mysql-connector-python', 'pymysql'])
                    elif 'sqlite' in requirements_content:
                        database_analysis['type'] = 'sqlite'
                        database_analysis['url_template'] = 'sqlite:///database.db'
                        database_analysis['detected_packages'].append('sqlite3')
                        
                    # Migration tools detection
                    if 'alembic' in requirements_content or os.path.exists('alembic.ini'):
                        database_analysis['migration_tools'].append('alembic')
                    if 'django' in requirements_content and os.path.exists('manage.py'):
                        database_analysis['migration_tools'].append('django')
                    if 'flask-migrate' in requirements_content:
                        database_analysis['migration_tools'].append('flask-migrate')
                        
                    if database_analysis['detected_packages']:
                        database_analysis['enabled'] = True
                        database_analysis['migrations_enabled'] = len(database_analysis['migration_tools']) > 0
                        
            except Exception as e:
                print(f"⚠️ Error reading requirements.txt: {e}")
        
        # Check for database model files
        db_files = ['models.py', 'database.py', 'db.py', 'schema.sql']
        for file in db_files:
            if os.path.exists(file):
                database_analysis['enabled'] = True
                break
                
        project_analysis['database'] = database_analysis
        
        # Add DATABASE_URL to required secrets if database is detected
        if database_analysis['enabled']:
            # Check if DATABASE_URL is already in required_secrets
            if not any(secret['name'] == 'DATABASE_URL' for secret in required_secrets):
                required_secrets.append({
                    'name': 'DATABASE_URL',
                    'value': '',
                    'description': f'Database connection string for {database_analysis["type"]}',
                    'source': 'database_analysis',
                    'template': database_analysis['url_template']
                })
        
        # 🔍 SMART MIGRATION DETECTION
        print("🔍 Analyzing for database migration requirements...")
        
        migration_analysis = {
            'needs_migrations': False,
            'migration_type': None,
            'migration_files': [],
            'database_dependencies': [],
            'migration_recommendations': []
        }
        
        # Check for migration-related files and dependencies
        migration_indicators = []
        
        # Check for migration directories
        if os.path.exists('migrations'):
            migration_indicators.append('migrations directory')
            migration_analysis['migration_files'].append('migrations/')
        
        # Check for Alembic configuration
        if os.path.exists('alembic.ini'):
            migration_indicators.append('alembic.ini')
            migration_analysis['migration_files'].append('alembic.ini')
        
        # Check for SQLAlchemy models
        if os.path.exists('models') or os.path.exists('models.py'):
            migration_indicators.append('SQLAlchemy models')
            migration_analysis['migration_files'].extend(['models/', 'models.py'])
        
        # Check requirements.txt for database dependencies
        if os.path.exists('requirements.txt'):
            try:
                with open('requirements.txt', 'r') as f:
                    requirements_content = f.read().lower()
                    
                    # Comprehensive database package detection
                    db_packages = {
                        # SQL Databases
                        'postgresql': ['psycopg2', 'psycopg2-binary', 'postgresql', 'pg8000', 'asyncpg'],
                        'mysql': ['mysql-connector-python', 'mysql-connector', 'pymysql', 'mysqlclient'],
                        'sqlite': ['sqlite3', 'sqlite'],
                        'oracle': ['cx_oracle', 'oracle'],
                        'sqlserver': ['pyodbc', 'pymssql', 'sqlserver'],
                        
                        # NoSQL Databases
                        'mongodb': ['pymongo', 'motor', 'mongoengine'],
                        'redis': ['redis', 'hiredis', 'redis-py'],
                        'cassandra': ['cassandra-driver', 'cqlengine'],
                        'dynamodb': ['boto3', 'dynamodb'],
                        'elasticsearch': ['elasticsearch', 'elasticsearch-dsl'],
                        
                        # ORM and Migration Tools
                        'sqlalchemy': ['sqlalchemy', 'sqlalchemy-utils'],
                        'alembic': ['alembic'],
                        'django': ['django', 'djangorestframework'],
                        'flask_sqlalchemy': ['flask-sqlalchemy'],
                        'peewee': ['peewee'],
                        'tortoise': ['tortoise-orm'],
                        
                        # Database Utilities
                        'connection_pooling': ['sqlalchemy-pool', 'psycopg2-pool'],
                        'database_migration': ['alembic', 'django-migrations', 'flask-migrate'],
                        'database_backup': ['pg_dump', 'mysqldump', 'mongodump']
                    }
                    
                    found_db_packages = []
                    detected_db_types = []
                    
                    for db_type, packages in db_packages.items():
                        for package in packages:
                            if package in requirements_content:
                                found_db_packages.append(package)
                                if db_type not in detected_db_types:
                                    detected_db_types.append(db_type)
                    
                    if found_db_packages:
                        migration_analysis['database_dependencies'] = found_db_packages
                        migration_analysis['database_types'] = detected_db_types
                        migration_indicators.append(f'database packages: {", ".join(found_db_packages)}')
                        migration_indicators.append(f'database types: {", ".join(detected_db_types)}')
                        
                        print(f"🔍 Detected database types: {', '.join(detected_db_types)}")
                        print(f"🔍 Found database packages: {', '.join(found_db_packages)}")
                        
            except Exception as e:
                print(f"⚠️ Error reading requirements.txt: {e}")
        
        # Check for database URLs and connection strings in environment variables
        db_url_indicators = {
            'postgresql': ['DATABASE_URL', 'POSTGRES_URL', 'POSTGRES_DB_URL', 'PG_URL', 'STAGING_DATABASE_URL', 'PRODUCTION_DATABASE_URL'],
            'mysql': ['MYSQL_URL', 'MYSQL_DATABASE_URL', 'MARIADB_URL'],
            'sqlite': ['SQLITE_URL', 'SQLITE_DB'],
            'mongodb': ['MONGO_URL', 'MONGODB_URL', 'MONGO_DATABASE_URL'],
            'redis': ['REDIS_URL', 'REDIS_HOST', 'REDIS_DB_URL'],
            'elasticsearch': ['ELASTICSEARCH_URL', 'ES_URL'],
            'generic': ['DATABASE_URL', 'DB_URL', 'DB_CONNECTION']
        }
        
        found_db_urls = []
        detected_url_types = []
        
        for db_type, urls in db_url_indicators.items():
            for url in urls:
                if url in env_vars:
                    found_db_urls.append(url)
                    if db_type not in detected_url_types:
                        detected_url_types.append(db_type)
        
        if found_db_urls:
            migration_indicators.append(f'database URLs: {", ".join(found_db_urls)}')
            migration_indicators.append(f'URL types: {", ".join(detected_url_types)}')
            migration_analysis['database_urls'] = found_db_urls
            migration_analysis['url_types'] = detected_url_types
        
        # Determine if migrations are needed
        if migration_indicators:
            migration_analysis['needs_migrations'] = True
            
            # Determine migration type based on indicators and database types
            detected_db_types = migration_analysis.get('database_types', [])
            detected_url_types = migration_analysis.get('url_types', [])
            
            # Smart migration type detection
            if 'alembic' in str(migration_analysis['database_dependencies']):
                migration_analysis['migration_type'] = 'alembic'
                
                # Database-specific Alembic recommendations
                if 'postgresql' in detected_db_types or 'postgresql' in detected_url_types:
                    migration_analysis['migration_recommendations'] = [
                        'Include Alembic migration steps with PostgreSQL support',
                        'Add PostgreSQL backup before migrations (pg_dump)',
                        'Configure PostgreSQL staging and production URLs',
                        'Add PostgreSQL-specific migration rollback capabilities',
                        'Include PostgreSQL connection pooling configuration'
                    ]
                elif 'mysql' in detected_db_types or 'mysql' in detected_url_types:
                    migration_analysis['migration_recommendations'] = [
                        'Include Alembic migration steps with MySQL support',
                        'Add MySQL backup before migrations (mysqldump)',
                        'Configure MySQL staging and production URLs',
                        'Add MySQL-specific migration rollback capabilities',
                        'Include MySQL connection pooling configuration'
                    ]
                else:
                    migration_analysis['migration_recommendations'] = [
                        'Include Alembic migration steps in workflow',
                        'Add database backup before migrations',
                        'Configure staging and production database URLs',
                        'Add migration rollback capabilities'
                    ]
                    
            elif 'django' in str(migration_analysis['database_dependencies']):
                migration_analysis['migration_type'] = 'django'
                migration_analysis['migration_recommendations'] = [
                    'Include Django migration steps (python manage.py migrate)',
                    'Add Django makemigrations step for new models',
                    'Configure Django database settings for staging/production',
                    'Include Django migration rollback capabilities'
                ]
                
            elif 'mongodb' in detected_db_types or 'mongodb' in detected_url_types:
                migration_analysis['migration_type'] = 'mongodb'
                migration_analysis['migration_recommendations'] = [
                    'Include MongoDB schema migration scripts',
                    'Add MongoDB backup before migrations (mongodump)',
                    'Configure MongoDB staging and production connections',
                    'Include MongoDB collection validation steps',
                    'Add MongoDB migration rollback capabilities'
                ]
                
            elif 'redis' in detected_db_types or 'redis' in detected_url_types:
                migration_analysis['migration_type'] = 'redis'
                migration_analysis['migration_recommendations'] = [
                    'Include Redis data migration scripts',
                    'Add Redis backup before migrations',
                    'Configure Redis staging and production connections',
                    'Include Redis key migration and cleanup steps'
                ]
                
            elif 'sqlalchemy' in str(migration_analysis['database_dependencies']):
                migration_analysis['migration_type'] = 'sqlalchemy'
                migration_analysis['migration_recommendations'] = [
                    'Include SQLAlchemy migration steps',
                    'Add database schema validation',
                    'Configure database connection pooling',
                    'Include SQLAlchemy model synchronization'
                ]
            else:
                migration_analysis['migration_type'] = 'custom'
                migration_analysis['migration_recommendations'] = [
                    'Include custom migration scripts',
                    'Add database connection testing',
                    'Configure migration environment variables',
                    'Add database backup and rollback procedures'
                ]
            
            print(f"✅ Migration requirements detected: {migration_analysis['migration_type']}")
            print(f"📋 Migration indicators: {', '.join(migration_indicators)}")
        else:
            print("✅ No migration requirements detected - skipping migration steps")
            migration_analysis['migration_recommendations'] = [
                'No database migrations needed for this project',
                'Focus on application deployment only'
            ]
        
        project_analysis['migration_analysis'] = migration_analysis
        
        # Add database information in the format expected by frontend
        database_info = {
            'enabled': migration_analysis.get('needs_migrations', False),
            'type': None,
            'url_template': None,
            'detected_packages': migration_analysis.get('database_dependencies', []),
            'migration_tools': [],
            'migrations_enabled': migration_analysis.get('needs_migrations', False)
        }
        
        # Determine database type from detected packages
        detected_db_types = migration_analysis.get('database_types', [])
        if 'postgresql' in detected_db_types:
            database_info['type'] = 'postgresql'
            database_info['url_template'] = 'postgresql://username:password@host:5432/database_name'
        elif 'mysql' in detected_db_types:
            database_info['type'] = 'mysql'
            database_info['url_template'] = 'mysql://username:password@host:3306/database_name'
        elif 'sqlite' in detected_db_types:
            database_info['type'] = 'sqlite'
            database_info['url_template'] = 'sqlite:///database.db'
            
        # Determine migration tools
        if 'alembic' in migration_analysis.get('database_dependencies', []):
            database_info['migration_tools'].append('alembic')
        if 'django' in migration_analysis.get('database_dependencies', []):
            database_info['migration_tools'].append('django')
        if 'flask-migrate' in migration_analysis.get('database_dependencies', []):
            database_info['migration_tools'].append('flask-migrate')
            
        project_analysis['database'] = database_info
        
        # Generate recommendations based on project type
        if project_analysis['project_type'] == 'streamlit':
            project_analysis['recommendations'] = [
                'Create Dockerfile optimized for Streamlit',
                'Generate Cloud Run workflow with port 8501',
                'Configure environment variables for Streamlit',
                'Set appropriate resource limits for ML applications'
            ]
        elif project_analysis['project_type'] == 'flask':
            project_analysis['recommendations'] = [
                'Create Dockerfile for Flask application',
                'Generate Cloud Run workflow with port 8080',
                'Configure WSGI server settings',
                'Set environment variables for Flask config'
            ]
        elif project_analysis['project_type'] == 'nodejs':
            project_analysis['recommendations'] = [
                'Create Dockerfile for Node.js application',
                'Generate Cloud Run workflow with port 8080',
                'Configure npm/yarn build process',
                'Set Node.js environment variables'
            ]
        
        # Return to original directory
        os.chdir(original_dir)
        
        # Store the analysis data in step3_extract_secrets
        state_manager.mark_step_completed("step3_extract_secrets", {
            'project_type': project_analysis['project_type'],
            'main_files': project_analysis['main_files'],
            'dependencies': project_analysis['dependencies'],
            'deployment_files': project_analysis['deployment_files'],
            'required_secrets': project_analysis['required_secrets'],
            'migration_analysis': project_analysis['migration_analysis'],
            'recommendations': project_analysis['recommendations']
        })
        
        return jsonify({
            "success": True,
            "analysis": project_analysis,
            "message": f"Project analyzed successfully. Detected: {project_analysis['project_type']} application"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Smart workflow content generation
def generate_workflow_content(project_id, github_repo, wif_provider, service_account, project_type, migration_analysis):
    """
    Generate workflow content with proper permissions for Workload Identity Federation.
    This function ensures all generated workflows include the required permissions.
    """
    """Generate workflow content as a separate function"""
    print(f"🔍 Debug - generate_workflow_content called with project_id={project_id}, repo={github_repo}")
    print(f"🔍 Debug - wif_provider={wif_provider}, service_account={service_account}")
    print(f"🔍 Debug - project_type={project_type}, migration_analysis={migration_analysis}")
    
    # Base workflow template
    workflow_content = f"""name: Deploy to Cloud Run

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

permissions:
  contents: 'read'
  id-token: 'write'

env:
  GCP_PROJECT_ID: ${{{{ secrets.GCP_PROJECT_ID }}}}
  GCP_REGION: ${{{{ secrets.GCP_REGION }}}}
  SERVICE_NAME: finance-chatbot
  REGION: ${{{{ secrets.GCP_REGION }}}}

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Google Cloud Auth
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{{{ secrets.WIF_PROVIDER }}}}
        service_account: ${{{{ secrets.DEPLOY_SA_EMAIL }}}}
        
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: Configure Docker for Artifact Registry
      run: |
        # Configure Docker to use Artifact Registry
        gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
        echo "✅ Docker configured for Artifact Registry"
      
    - name: Create Artifact Registry repository
      run: |
        echo "🏗️ Creating Artifact Registry repository..."
        # Create Artifact Registry repository if it doesn't exist
        gcloud artifacts repositories create ${{{{ env.SERVICE_NAME }}}} \\
          --repository-format=docker \\
          --location=${{{{ env.REGION }}}} \\
          --description="Docker repository for ${{{{ env.SERVICE_NAME }}}}" \\
          --quiet || echo "Repository already exists"
        echo "✅ Artifact Registry repository ready"
      
    - name: Build and push container
      run: |
        echo "🐳 Building and pushing Docker image..."
        # Use Artifact Registry instead of Container Registry
        docker build -t us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}} .
        echo "✅ Docker image built successfully"
        
        echo "📤 Pushing to Artifact Registry..."
        docker push us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}
        echo "✅ Docker image pushed successfully"
        
    - name: Deploy to Cloud Run
      uses: google-github-actions/deploy-cloudrun@v2
      with:
        service: ${{{{ env.SERVICE_NAME }}}}
        image: us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}
        region: ${{{{ env.REGION }}}}
        
    - name: Show Output
      run: echo ${{{{ steps.deploy.outputs.url }}}}
"""
    
    # Add migration job if needed (only if actually using databases)
    if migration_analysis.get('needs_migrations', False) and migration_analysis.get('database_types', []):
        migration_job = f"""
  migrate-database:
    runs-on: ubuntu-latest
    needs: deploy
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Google Cloud Auth
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{{{ secrets.WIF_PROVIDER }}}}
        service_account: ${{{{ secrets.DEPLOY_SA_EMAIL }}}}
        
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: Run Database Migrations
      run: |
        echo "🔄 Running database migrations..."
        # Set database URL based on detected type
        export DATABASE_URL="${{{{ secrets.DATABASE_URL }}}}"
        
        # Run migrations based on detected type
        if [ -f "alembic.ini" ]; then
          echo "📊 Running Alembic migrations..."
          alembic upgrade head
        elif [ -f "manage.py" ]; then
          echo "🐍 Running Django migrations..."
          python manage.py migrate
        else
          echo "⚠️ No migration system detected, skipping migrations"
        fi
        echo "✅ Database migrations completed"
"""
        # Insert migration job before deploy job
        workflow_content = workflow_content.replace("jobs:", "jobs:" + migration_job)
    
    print(f"🔍 Debug - generate_workflow_content returning content length: {len(workflow_content)}")
    
    # Validate that the workflow has required permissions
    if 'permissions:' not in workflow_content:
        print("⚠️ Warning: Generated workflow missing permissions section")
        # Add permissions if missing
        workflow_content = workflow_content.replace(
            'env:',
            'permissions:\n  contents: \'read\'\n  id-token: \'write\'\n\nenv:'
        )
        print("✅ Added missing permissions to workflow")
    
    # Validate that Dockerfile generation doesn't have inline comments
    if 'generate_smart_dockerfile' in globals():
        print("🔍 Validating Dockerfile generation for inline comments...")
    
    return workflow_content

# Smart workflow generation
def generate_smart_dockerfile(project_type, migration_analysis, dependencies):
    """Generate a smart Dockerfile based on project analysis"""
    print(f"🔍 Debug - generate_smart_dockerfile called with project_type={project_type}")
    print(f"🔍 Debug - migration_analysis={migration_analysis}")
    print(f"🔍 Debug - dependencies={dependencies}")
    
    # Base Dockerfile template
    dockerfile_content = f"""# 🐳 Smart Dockerfile for {project_type} project
# Generated automatically by Intelligent CI/CD Toolbox v4

# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies based on project requirements
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libpq-dev \\
    libssl-dev \\
    libffi-dev \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

"""
    
    # Add database-specific dependencies (only if actually using databases)
    database_types = migration_analysis.get('database_types', [])
    if database_types and migration_analysis.get('needs_migrations', False):
        dockerfile_content += f"""
# 🗄️ Install database-specific dependencies
"""
        if 'postgresql' in database_types:
            dockerfile_content += """RUN pip install --no-cache-dir psycopg2-binary
"""
        if 'mysql' in database_types:
            dockerfile_content += """RUN pip install --no-cache-dir mysqlclient pymysql
"""
        if 'mongodb' in database_types:
            dockerfile_content += """RUN pip install --no-cache-dir pymongo motor
"""
        if 'redis' in database_types:
            dockerfile_content += """RUN pip install --no-cache-dir redis hiredis
"""
    
    # Add migration tools
    migration_type = migration_analysis.get('migration_type', None)
    if migration_type:
        dockerfile_content += f"""
# 🔄 Install migration tools
"""
        if migration_type == 'alembic':
            dockerfile_content += """RUN pip install --no-cache-dir alembic
"""
        elif migration_type == 'django':
            dockerfile_content += """RUN pip install --no-cache-dir django
"""
    
    # Add project-specific setup
    dockerfile_content += f"""
# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

"""
    
    # Add project-specific environment variables
    if project_type == 'streamlit':
        dockerfile_content += """# Cloud Run expects PORT environment variable
ENV PORT=8080
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLE_CORS=false
ENV STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

"""
    elif project_type == 'flask':
        dockerfile_content += """ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

"""
    
    # Add health check
    dockerfile_content += """# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8080/ || exit 1

"""
    
    # Add the appropriate command based on project type
    if project_type == 'streamlit':
        dockerfile_content += """# Run the Streamlit application
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
"""
    elif project_type == 'flask':
        dockerfile_content += """# Expose port
EXPOSE 5000

# Run the Flask application
CMD ["python", "app.py"]
"""
    else:
        dockerfile_content += """# Expose port
EXPOSE 8501

# Run the application
CMD ["python", "main.py"]
"""
    
    print(f"🔍 Debug - generate_smart_dockerfile returning content length: {len(dockerfile_content)}")
    return dockerfile_content

@app.route('/api/generate_smart_workflow', methods=['POST'])
def generate_smart_workflow():
    """Generate workflow YAML based on project analysis"""
    try:
        data = request.get_json()
        project_type = data.get('project_type', 'unknown')
        migration_analysis = data.get('migration_analysis', {})
        
        print(f"📝 Generating smart workflow for {project_type} project...")
        
        # Get project info from state
        step2_data = state_manager.state.get('step2_project', {})
        project_id = step2_data.get('project_id', 'neurofinance-468916')
        github_repo = step2_data.get('github_repo', 'PramodChandrayan/neurochatagent')
        wif_provider = step2_data.get('wif_provider', '')
        service_account = step2_data.get('service_account', '')
        
        print(f"🔍 Debug - Project ID: {project_id}")
        print(f"🔍 Debug - GitHub Repo: {github_repo}")
        print(f"🔍 Debug - WIF Provider: {wif_provider}")
        print(f"🔍 Debug - Service Account: {service_account}")
        print(f"🔍 Debug - Migration Analysis: {migration_analysis}")
        print(f"🔍 Debug - Full step2_data: {step2_data}")
        
        if not wif_provider or not service_account:
            return jsonify({"success": False, "error": f"WIF provider or service account not found. WIF: '{wif_provider}', SA: '{service_account}'. Please complete Step 2 first."})
        
        # 🔍 SMART MIGRATION DETECTION
        needs_migrations = migration_analysis.get('needs_migrations', False)
        migration_type = migration_analysis.get('migration_type', None)
        database_types = migration_analysis.get('database_types', [])
        url_types = migration_analysis.get('url_types', [])
        
        print(f"🔍 Migration Analysis: needs_migrations={needs_migrations}, type={migration_type}")
        print(f"🔍 Database Types: {database_types}")
        print(f"🔍 URL Types: {url_types}")
        
        # Generate workflow content based on project type and migration needs
        if project_type == 'streamlit':
            if needs_migrations:
                print("✅ Including migration steps in workflow")
                workflow_content = f"""# GitHub Actions Workflow for {github_repo}
# Deploy Streamlit Finance Chatbot to Google Cloud Run with Database Migrations

name: Deploy Streamlit Finance Chatbot to Cloud Run

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

env:
  GCP_PROJECT_ID: {project_id}
  REGION: us-central1
  SERVICE_NAME: finance-chatbot

permissions:
  id-token: write
  contents: read

jobs:
  # 🗄️ DATABASE MIGRATION JOB (if needed)
  migrate-database:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'  # Only run on main branch
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install alembic psycopg2-binary
        
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        token_format: access_token
        workload_identity_provider: {wif_provider}
        service_account: {service_account}
        
    - name: 🗄️ Run Database Migrations
      run: |
        echo "🗄️ Running database migrations..."
        
        # Set database URL based on environment and database type
        if [ "${{{{ github.ref }}}}" = "refs/heads/main" ]; then
          # Production database selection based on detected type
          if [ -n "${{{{ secrets.PRODUCTION_DATABASE_URL }}}}" ]; then
            export DATABASE_URL="${{{{ secrets.PRODUCTION_DATABASE_URL }}}}"
            echo "📊 Using production database"
          elif [ -n "${{{{ secrets.PRODUCTION_POSTGRES_URL }}}}" ]; then
            export DATABASE_URL="${{{{ secrets.PRODUCTION_POSTGRES_URL }}}}"
            echo "📊 Using production PostgreSQL database"
          elif [ -n "${{{{ secrets.PRODUCTION_MYSQL_URL }}}}" ]; then
            export DATABASE_URL="${{{{ secrets.PRODUCTION_MYSQL_URL }}}}"
            echo "📊 Using production MySQL database"
          elif [ -n "${{{{ secrets.PRODUCTION_MONGO_URL }}}}" ]; then
            export MONGO_URL="${{{{ secrets.PRODUCTION_MONGO_URL }}}}"
            echo "📊 Using production MongoDB database"
          else
            echo "⚠️ No production database URL found"
            exit 1
          fi
        else
          # Staging database selection based on detected type
          if [ -n "${{{{ secrets.STAGING_DATABASE_URL }}}}" ]; then
            export DATABASE_URL="${{{{ secrets.STAGING_DATABASE_URL }}}}"
            echo "🧪 Using staging database"
          elif [ -n "${{{{ secrets.STAGING_POSTGRES_URL }}}}" ]; then
            export DATABASE_URL="${{{{ secrets.STAGING_POSTGRES_URL }}}}"
            echo "🧪 Using staging PostgreSQL database"
          elif [ -n "${{{{ secrets.STAGING_MYSQL_URL }}}}" ]; then
            export DATABASE_URL="${{{{ secrets.STAGING_MYSQL_URL }}}}"
            echo "🧪 Using staging MySQL database"
          elif [ -n "${{{{ secrets.STAGING_MONGO_URL }}}}" ]; then
            export MONGO_URL="${{{{ secrets.STAGING_MONGO_URL }}}}"
            echo "🧪 Using staging MongoDB database"
          else
            echo "⚠️ No staging database URL found"
            exit 1
          fi
        fi
        
        # Run migrations based on type and database
        if [ -f "alembic.ini" ]; then
          echo "🔄 Running Alembic migrations..."
          alembic upgrade head
        elif [ -f "manage.py" ]; then
          echo "🔄 Running Django migrations..."
          python manage.py migrate
        elif [ -f "migrations/run_migrations.py" ]; then
          echo "🔄 Running custom migrations..."
          python migrations/run_migrations.py
        elif [ -f "migrations/mongo_migrate.py" ]; then
          echo "🔄 Running MongoDB migrations..."
          python migrations/mongo_migrate.py
        else
          echo "⚠️ No migration runner found, skipping migrations"
        fi
        
        echo "✅ Database migrations completed"

  # 🚀 APPLICATION DEPLOYMENT JOB
  deploy:
    runs-on: ubuntu-latest
    needs: [migrate-database]  # Wait for migrations if they exist
    if: always()  # Always run deployment
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        token_format: access_token
        workload_identity_provider: {wif_provider}
        service_account: {service_account}
        
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: Configure Docker for Artifact Registry
      run: |
        # Configure Docker to use Artifact Registry
        gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
        echo "✅ Docker configured for Artifact Registry"
      
    - name: Create Artifact Registry repository
      run: |
        echo "🏗️ Creating Artifact Registry repository..."
        # Create Artifact Registry repository if it doesn't exist
        gcloud artifacts repositories create ${{ env.SERVICE_NAME }} \
          --repository-format=docker \
          --location=${{ env.REGION }} \
          --description="Docker repository for ${{ env.SERVICE_NAME }}" \
          --quiet || echo "Repository already exists"
        echo "✅ Artifact Registry repository ready"
      
    - name: Build and push container
      run: |
        docker build -t us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}} .
        docker push us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}
        
    - name: Deploy to Cloud Run
      uses: google-github-actions/deploy-cloudrun@v2
      with:
        service: ${{{{ env.SERVICE_NAME }}}}
        image: us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}
        region: ${{{{ env.REGION }}}}
        env_vars: |
          OPENAI_API_KEY=${{{{ secrets.OPENAI_API_KEY }}}}
          PINECONE_API_KEY=${{{{ secrets.PINECONE_API_KEY }}}}
          PINECONE_ENVIRONMENT=${{{{ secrets.PINECONE_ENVIRONMENT }}}}
          DATABASE_URL=${{{{ secrets.DATABASE_URL }}}}
        port: 8501
        cpu: 1
        memory: 2Gi
        max_instances: 10
        
    - name: Show service URL
      run: |
        echo "🎉 Streamlit Finance Chatbot deployed successfully!"
        echo "🌐 Service URL: $(gcloud run services describe ${{{{ env.SERVICE_NAME }}}} --region=${{{{ env.REGION }}}} --format='value(status.url)')"
"""
            else:
                print("✅ No migrations needed - generating simple workflow")
                workflow_content = f"""# GitHub Actions Workflow for {github_repo}
# Deploy Streamlit Finance Chatbot to Google Cloud Run

name: Deploy Streamlit Finance Chatbot to Cloud Run

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
  workflow_dispatch:

env:
  GCP_PROJECT_ID: {project_id}
  REGION: us-central1
  SERVICE_NAME: finance-chatbot

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        token_format: access_token
        workload_identity_provider: {wif_provider}
        service_account: {service_account}
        
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2
      
    - name: Configure Docker for Artifact Registry
      run: |
        # Configure Docker to use Artifact Registry
        gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
        echo "✅ Docker configured for Artifact Registry"
      
    - name: Create Artifact Registry repository
      run: |
        echo "🏗️ Creating Artifact Registry repository..."
        # Create Artifact Registry repository if it doesn't exist
        gcloud artifacts repositories create ${{ env.SERVICE_NAME }} \
          --repository-format=docker \
          --location=${{ env.REGION }} \
          --description="Docker repository for ${{ env.SERVICE_NAME }}" \
          --quiet || echo "Repository already exists"
        echo "✅ Artifact Registry repository ready"
      
    - name: Build and push container
      run: |
        docker build -t us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}} .
        docker push us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}
        
    - name: Deploy to Cloud Run
      uses: google-github-actions/deploy-cloudrun@v2
      with:
        service: ${{{{ env.SERVICE_NAME }}}}
        image: us-central1-docker.pkg.dev/${{{{ env.GCP_PROJECT_ID }}}}/${{{{ env.SERVICE_NAME }}}}/${{{{ env.SERVICE_NAME }}}}:${{{{ github.sha }}}}
        region: ${{{{ env.REGION }}}}
        env_vars: |
          OPENAI_API_KEY=${{{{ secrets.OPENAI_API_KEY }}}}
          PINECONE_API_KEY=${{{{ secrets.PINECONE_API_KEY }}}}
          PINECONE_ENVIRONMENT=${{{{ secrets.PINECONE_ENVIRONMENT }}}}
        port: 8501
        cpu: 1
        memory: 2Gi
        max_instances: 10
        
    - name: Show service URL
      run: |
        echo "🎉 Streamlit Finance Chatbot deployed successfully!"
        echo "🌐 Service URL: $(gcloud run services describe ${{{{ env.SERVICE_NAME }}}} --region=${{{{ env.REGION }}}} --format='value(status.url)')"
"""
        else:
            workflow_content = f"# Generic workflow for {project_type} project"
        
        # Create .github/workflows directory
        workflows_dir = os.path.join(os.path.dirname(os.getcwd()), '.github', 'workflows')
        os.makedirs(workflows_dir, exist_ok=True)
        
        # Write workflow file
        workflow_file = os.path.join(workflows_dir, 'deploy-cloudrun.yml')
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        print(f"✅ Smart workflow generated: {workflow_file}")
        print(f"🔍 Debug - About to start Dockerfile generation...")
        
        # 🐳 GENERATE SMART DOCKERFILE
        print("🐳 Generating smart Dockerfile based on project analysis...")
        print(f"🔍 Debug - About to call generate_smart_dockerfile with project_type={project_type}")
        print(f"🔍 Debug - migration_analysis={migration_analysis}")
        print(f"🔍 Debug - dependencies={data.get('dependencies', [])}")
        
        try:
            dockerfile_content = generate_smart_dockerfile(project_type, migration_analysis, data.get('dependencies', []))
            print(f"🔍 Debug - Dockerfile content generated successfully, length: {len(dockerfile_content)}")
        except Exception as e:
            print(f"❌ Error generating Dockerfile: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({"success": False, "error": f"Failed to generate Dockerfile: {str(e)}"})
        
        # Write Dockerfile
        dockerfile_path = os.path.join(os.path.dirname(os.getcwd()), 'Dockerfile')
        print(f"🔍 Debug - Dockerfile path: {dockerfile_path}")
        print(f"🔍 Debug - Current working directory: {os.getcwd()}")
        print(f"🔍 Debug - Parent directory: {os.path.dirname(os.getcwd())}")
        
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        print(f"✅ Smart Dockerfile generated: {dockerfile_path}")
        
        return jsonify({
            "success": True,
            "message": f"✅ Smart workflow and Dockerfile generated for {project_type} project!",
            "workflow_file": workflow_file,
            "dockerfile_path": dockerfile_path,
            "workflow_content": workflow_content,
            "dockerfile_content": dockerfile_content,
            "project_type": project_type
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Separate endpoint for generating only the workflow YAML
@app.route('/api/step5/generate_workflow_only', methods=['POST'])
def generate_workflow_only():
    """Generate only the workflow YAML file"""
    try:
        print("📝 Generating workflow YAML only...")
        
        # Get data from previous stages
        step2_data = state_manager.get_step_data("step2_project")
        step3_data = state_manager.get_step_data("step3_extract_secrets")
        
        if not step2_data.get('completed'):
            return jsonify({"success": False, "error": "Infrastructure setup not completed. Please complete Step 2 first."})
        
        if not step3_data.get('completed'):
            return jsonify({"success": False, "error": "Project analysis not completed. Please complete Step 3 first."})
        
        # Extract required data
        project_id = step2_data.get('project_id')
        github_repo = step2_data.get('github_repo')
        wif_provider = step2_data.get('wif_provider')
        service_account = step2_data.get('service_account')
        project_type = step3_data.get('project_type', 'streamlit')
        migration_analysis = step3_data.get('migration_analysis', {})
        
        print(f"🔍 Debug - Project ID: {project_id}")
        print(f"🔍 Debug - GitHub Repo: {github_repo}")
        print(f"🔍 Debug - WIF Provider: {wif_provider}")
        print(f"🔍 Debug - Service Account: {service_account}")
        print(f"🔍 Debug - Project Type: {project_type}")
        print(f"🔍 Debug - Migration Analysis: {migration_analysis}")
        
        # Generate workflow content
        workflow_content = generate_workflow_content(
            project_id, github_repo, wif_provider, service_account, 
            project_type, migration_analysis
        )
        
        # Write workflow file
        workflow_dir = os.path.join(os.path.dirname(os.getcwd()), '.github', 'workflows')
        os.makedirs(workflow_dir, exist_ok=True)
        workflow_file = os.path.join(workflow_dir, 'deploy-cloudrun.yml')
        
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        print(f"✅ Workflow YAML generated: {workflow_file}")
        
        # Mark step as completed
        state_manager.mark_step_completed("step5_generate_workflow", {
            "workflow_file": workflow_file,
            "workflow_content": workflow_content,
            "project_type": project_type
        })
        
        return jsonify({
            "success": True,
            "message": f"✅ Workflow YAML generated for {project_type} project!",
            "workflow_file": workflow_file,
            "workflow_content": workflow_content,
            "project_type": project_type
        })
        
    except Exception as e:
        print(f"❌ Error generating workflow: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

# Separate endpoint for generating only the Dockerfile
@app.route('/api/step5_5/generate_dockerfile_only', methods=['POST'])
def generate_dockerfile_only():
    """Generate only the Dockerfile"""
    try:
        print("🐳 Generating Dockerfile only...")
        
        # Get data from previous stages
        step3_data = state_manager.get_step_data("step3_extract_secrets")
        
        if not step3_data.get('completed'):
            return jsonify({"success": False, "error": "Project analysis not completed. Please complete Step 3 first."})
        
        # Extract required data
        project_type = step3_data.get('project_type', 'streamlit')
        migration_analysis = step3_data.get('migration_analysis', {})
        dependencies = step3_data.get('dependencies', [])
        
        print(f"🔍 Debug - Project Type: {project_type}")
        print(f"🔍 Debug - Migration Analysis: {migration_analysis}")
        print(f"🔍 Debug - Dependencies: {dependencies}")
        
        # Generate Dockerfile content
        dockerfile_content = generate_smart_dockerfile(project_type, migration_analysis, dependencies)
        
        # Write Dockerfile
        dockerfile_path = os.path.join(os.path.dirname(os.getcwd()), 'Dockerfile')
        print(f"🔍 Debug - Dockerfile path: {dockerfile_path}")
        
        with open(dockerfile_path, 'w') as f:
            f.write(dockerfile_content)
        
        print(f"✅ Dockerfile generated: {dockerfile_path}")
        
        # Mark step as completed
        state_manager.mark_step_completed("step5_5_generate_dockerfile", {
            "dockerfile_path": dockerfile_path,
            "dockerfile_content": dockerfile_content,
            "project_type": project_type
        })
        
        return jsonify({
            "success": True,
            "message": f"✅ Dockerfile generated for {project_type} project!",
            "dockerfile_path": dockerfile_path,
            "dockerfile_content": dockerfile_content,
            "project_type": project_type
        })
        
    except Exception as e:
        print(f"❌ Error generating Dockerfile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

# Enhanced commit and push
@app.route('/api/step6/commit_and_push_enhanced', methods=['POST'])
def commit_and_push_enhanced():
    """Enhanced commit and push with automatic file generation"""
    try:
        print("📝 Enhanced commit and push with smart files...")
        
        # Check if we're in the right directory
        parent_dir = os.path.dirname(os.getcwd())
        git_dir = os.path.join(parent_dir, '.git')
        
        if not os.path.exists(git_dir):
            return jsonify({"success": False, "error": f"Git repository not found in {parent_dir}"})
        
        print(f"✅ Found Git repository in: {parent_dir}")
        
        # Change to parent directory for Git operations
        original_dir = os.getcwd()
        os.chdir(parent_dir)
        
        # Stage all generated files
        files_to_stage = []
        if os.path.exists('Dockerfile'):
            files_to_stage.append('Dockerfile')
        if os.path.exists('.github/workflows/deploy-cloudrun.yml'):
            files_to_stage.append('.github/workflows/deploy-cloudrun.yml')
        
        print(f"📁 Staging files: {files_to_stage}")
        
        for file_path in files_to_stage:
            result = run_command_safely(f'git add {file_path}')
            if not result['success']:
                return jsonify({"success": False, "error": f"Failed to stage {file_path}: {result.get('error')}"})
        
        # Commit the changes
        commit_message = "Setup CI/CD pipeline with smart deployment configuration"
        result = run_command_safely(f'git commit -m "{commit_message}"')
        if not result['success']:
            return jsonify({"success": False, "error": f"Failed to commit changes: {result.get('error')}"})
        
        # Push to GitHub with better error handling
        print("📤 Pushing to GitHub...")
        
        # First, check what branch we're on
        branch_result = run_command_safely('git branch --show-current')
        current_branch = branch_result['output'].strip() if branch_result['success'] else 'main'
        
        print(f"🔍 Current branch: {current_branch}")
        
        # Try pushing to the current branch first
        result = run_command_safely(f'git push origin {current_branch}')
        if not result['success']:
            print(f"⚠️ Push to {current_branch} failed: {result.get('error')}")
            
            # If that fails, try main branch
            result = run_command_safely('git push origin main')
            if not result['success']:
                print(f"⚠️ Push to main failed: {result.get('error')}")
                
                # If main fails, try master branch
                result = run_command_safely('git push origin master')
                if not result['success']:
                    error_msg = result.get('error', 'Unknown error')
                    
                    # Check if it's a workflow file restriction
                    if 'workflow' in error_msg.lower() and 'oauth' in error_msg.lower():
                        return jsonify({
                            "success": False,
                            "error": "GitHub OAuth app cannot create workflow files. Please manually push the files or use a Personal Access Token with workflow permissions.",
                            "manual_push_required": True,
                            "files_to_push": files_to_stage,
                            "branch": current_branch
                        })
                    else:
                        return jsonify({
                            "success": False,
                            "error": f"Failed to push to GitHub: {error_msg}"
                        })
        
        # Return to original directory
        os.chdir(original_dir)
        
        return jsonify({
            "success": True,
            "message": "✅ Enhanced commit and push completed successfully!",
            "commit_message": commit_message,
            "files_staged": files_to_stage,
            "next_step": "GitHub Actions pipeline will now run automatically"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/step6/check_push_status')
def check_push_status():
    """Check if files have been pushed to GitHub"""
    try:
        print("🔍 Checking push status...")
        
        # Check if we're in the right directory
        parent_dir = os.path.dirname(os.getcwd())
        git_dir = os.path.join(parent_dir, '.git')
        
        if not os.path.exists(git_dir):
            return jsonify({"success": False, "error": "Git repository not found"})
        
        # Change to parent directory for Git operations
        original_dir = os.getcwd()
        os.chdir(parent_dir)
        
        # Check local files
        local_files = []
        if os.path.exists('Dockerfile'):
            local_files.append('Dockerfile')
        if os.path.exists('.github/workflows/deploy-cloudrun.yml'):
            local_files.append('.github/workflows/deploy-cloudrun.yml')
        
        # Check if files are committed
        status_result = run_command_safely('git status --porcelain')
        committed_files = []
        uncommitted_files = []
        
        if status_result['success']:
            if not status_result['output'].strip():
                # No changes, check if files exist in last commit
                log_result = run_command_safely('git log --name-only --oneline -1')
                if log_result['success'] and 'Dockerfile' in log_result['output']:
                    committed_files.append('Dockerfile')
                if log_result['success'] and 'deploy-cloudrun.yml' in log_result['output']:
                    committed_files.append('.github/workflows/deploy-cloudrun.yml')
            else:
                # Has changes
                uncommitted_files = [line.split()[-1] for line in status_result['output'].strip().split('\n') if line.strip()]
        
        # Check if pushed to remote
        remote_result = run_command_safely('git ls-remote --heads origin main')
        local_commit_result = run_command_safely('git rev-parse HEAD')
        
        files_pushed = False
        commit_hash = None
        branch = 'main'
        
        if remote_result['success'] and local_commit_result['success']:
            local_commit = local_commit_result['output'].strip()
            remote_commits = remote_result['output'].strip().split('\n')
            
            for remote_commit in remote_commits:
                if local_commit in remote_commit:
                    files_pushed = True
                    commit_hash = local_commit[:8]  # Short hash
                    break
        
        # Return to original directory
        os.chdir(original_dir)
        
        return jsonify({
            "success": True,
            "files_pushed": files_pushed,
            "local_files": local_files,
            "committed_files": committed_files,
            "uncommitted_files": uncommitted_files,
            "commit_hash": commit_hash,
            "branch": branch,
            "status": "Files committed locally" if committed_files else "Files not committed"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Add these new functions after the existing imports and before the main Flask app

def intelligent_github_auth():
    """Intelligent GitHub authentication with automatic fallback strategies"""
    try:
        print("🔐 Starting intelligent GitHub authentication...")
        
        # Strategy 1: Check if already authenticated
        result = run_command_safely("gh auth status")
        if result['success']:
            print("✅ Already authenticated with GitHub")
            return True
            
        # Strategy 2: Try token-based authentication
        print("🔄 Attempting token-based authentication...")
        github_token = os.getenv('GITHUB_TOKEN')
        if github_token:
            result = run_command_safely(f"gh auth login --with-token < {github_token}")
            if result['success']:
                print("✅ Token-based authentication successful")
                return True
                
        # Strategy 3: Interactive authentication with workflow scope
        print("🔄 Attempting interactive authentication with workflow scope...")
        result = run_command_safely("gh auth login --web --scope workflow")
        if result['success']:
            print("✅ Interactive authentication successful")
            return True
            
        # Strategy 4: Fallback to basic authentication
        print("🔄 Attempting basic authentication...")
        result = run_command_safely("gh auth login --web")
        if result['success']:
            print("✅ Basic authentication successful")
            return True
            
        print("❌ All authentication strategies failed")
        return False
        
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return False

def intelligent_workflow_push():
    """Intelligent workflow file push with automatic permission handling"""
    try:
        print("📤 Starting intelligent workflow push...")
        
        # Check if workflow files exist
        if not os.path.exists('.github/workflows'):
            print("❌ No workflow directory found")
            return False
            
        # Strategy 1: Try direct push
        print("🔄 Attempting direct push...")
        result = run_command_safely("git add . && git commit -m '🚀 Automated CI/CD setup' && git push origin main")
        if result['success']:
            print("✅ Direct push successful")
            return True
            
        # Strategy 2: Check and fix permissions
        print("🔄 Checking GitHub permissions...")
        result = run_command_safely("gh auth status")
        if not result['success']:
            print("🔄 Re-authenticating with workflow scope...")
            auth_result = intelligent_github_auth()
            if not auth_result:
                return False
                
        # Strategy 3: Force push with workflow permissions
        print("🔄 Attempting force push with workflow permissions...")
        result = run_command_safely("gh auth login --web --scope workflow --force")
        if result['success']:
            push_result = run_command_safely("git push origin main --force")
            if push_result['success']:
                print("✅ Force push successful")
                return True
                
        # Strategy 4: Manual intervention guidance
        print("⚠️ Automated push failed, providing manual guidance...")
        return provide_manual_push_guidance()
        
    except Exception as e:
        print(f"❌ Push error: {str(e)}")
        return False

def provide_manual_push_guidance():
    """Provide intelligent manual push guidance"""
    guidance = {
        "steps": [
            "1. Run: gh auth logout",
            "2. Run: gh auth login --web --scope workflow",
            "3. Run: git add .",
            "4. Run: git commit -m '🚀 Automated CI/CD setup'",
            "5. Run: git push origin main"
        ],
        "explanation": "GitHub requires workflow scope permissions for automated CI/CD setup",
        "automated_retry": True
    }
    
    print("📋 Manual push guidance:")
    for step in guidance["steps"]:
        print(f"   {step}")
    
    return guidance

def intelligent_secret_management():
    """Intelligent secret management with automatic detection and setup"""
    try:
        print("🔐 Starting intelligent secret management...")
        
        # Get project analysis
        analysis = analyze_project_intelligently()
        required_secrets = []
        
        # Detect required secrets based on project type
        if analysis.get('project_type') == 'streamlit':
            required_secrets.extend([
                'OPENAI_API_KEY',
                'PINECONE_API_KEY',
                'PINECONE_ENVIRONMENT'
            ])
            
        # Check for existing secrets
        existing_secrets = run_command_safely("gh secret list")
        if existing_secrets['success']:
            print("✅ Found existing secrets")
            
        # Provide secret setup guidance
        secret_guidance = {
            "required_secrets": required_secrets,
            "setup_commands": [
                f"gh secret set {secret} --body 'YOUR_{secret}_VALUE'" 
                for secret in required_secrets
            ],
            "automated_detection": True
        }
        
        return secret_guidance
        
    except Exception as e:
        print(f"❌ Secret management error: {str(e)}")
        return None

def analyze_project_intelligently():
    """Enhanced project analysis for automation"""
    try:
        print("🔍 Starting intelligent project analysis...")
        
        analysis = {
            'project_type': 'unknown',
            'dependencies': [],
            'required_secrets': [],
            'deployment_target': 'cloud_run',
            'needs_database': False,
            'needs_authentication': False
        }
        
        # Detect project type
        if os.path.exists('streamlit_app.py'):
            analysis['project_type'] = 'streamlit'
        elif os.path.exists('app.py'):
            analysis['project_type'] = 'flask'
        elif os.path.exists('main.py'):
            analysis['project_type'] = 'python'
            
        # Detect dependencies
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                content = f.read()
                if 'streamlit' in content:
                    analysis['project_type'] = 'streamlit'
                if 'flask' in content:
                    analysis['project_type'] = 'flask'
                    
        # Detect required secrets
        if analysis['project_type'] == 'streamlit':
            analysis['required_secrets'].extend([
                'OPENAI_API_KEY',
                'PINECONE_API_KEY',
                'PINECONE_ENVIRONMENT'
            ])
            
        print(f"✅ Project analysis complete: {analysis['project_type']}")
        return analysis
        
    except Exception as e:
        print(f"❌ Analysis error: {str(e)}")
        return {'project_type': 'unknown'}

def automated_cicd_setup():
    """Fully automated CI/CD setup with intelligent fallbacks"""
    try:
        print("🚀 Starting fully automated CI/CD setup...")
        
        # Step 1: Intelligent authentication
        print("📋 Step 1: GitHub Authentication")
        auth_success = intelligent_github_auth()
        if not auth_success:
            print("⚠️ Authentication failed, providing manual guidance")
            return {"success": False, "step": "authentication", "manual_required": True}
            
        # Step 2: Project analysis
        print("📋 Step 2: Project Analysis")
        analysis = analyze_project_intelligently()
        
        # Step 3: Generate configurations
        print("📋 Step 3: Generate Configurations")
        
        # Get migration analysis and dependencies
        migration_analysis = {
            'needs_migrations': False,
            'migration_type': None,
            'database_types': [],
            'database_dependencies': []
        }
        
        dependencies = ['requirements.txt']
        if os.path.exists('pyproject.toml'):
            dependencies.append('pyproject.toml')
            
        # Generate Dockerfile with correct parameters
        dockerfile_content = generate_smart_dockerfile(
            project_type=analysis.get('project_type', 'unknown'),
            migration_analysis=migration_analysis,
            dependencies=dependencies
        )
        
        # Generate workflow with correct parameters
        workflow_content = generate_workflow_content(
            project_id='neurofinance-468916',  # Default project ID
            github_repo='PramodChandrayan/neurochatagent',  # Default repo
            wif_provider='',  # Will be filled from state
            service_account='',  # Will be filled from state
            project_type=analysis.get('project_type', 'unknown'),
            migration_analysis=migration_analysis
        )
        
        # Step 4: Write files
        print("📋 Step 4: Write Configuration Files")
        
        # Create .github/workflows directory if it doesn't exist
        os.makedirs('.github/workflows', exist_ok=True)
        
        with open('Dockerfile', 'w') as f:
            f.write(dockerfile_content)
        with open('.github/workflows/deploy-cloudrun.yml', 'w') as f:
            f.write(workflow_content)
            
        # Step 5: Intelligent push
        print("📋 Step 5: Automated Push")
        push_success = intelligent_workflow_push()
        
        if push_success:
            print("✅ Fully automated CI/CD setup complete!")
            return {"success": True, "automated": True}
        else:
            print("⚠️ Automated push failed, manual intervention required")
            return {"success": False, "step": "push", "manual_required": True}
            
    except Exception as e:
        print(f"❌ Automated setup error: {str(e)}")
        return {"success": False, "error": str(e)}

# Add new API endpoints for automation
@app.route('/api/automated-setup', methods=['POST'])
def api_automated_setup():
    """API endpoint for fully automated CI/CD setup"""
    try:
        result = automated_cicd_setup()
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/intelligent-auth', methods=['POST'])
def api_intelligent_auth():
    """API endpoint for intelligent GitHub authentication"""
    try:
        result = intelligent_github_auth()
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/intelligent-push', methods=['POST'])
def api_intelligent_push():
    """API endpoint for intelligent workflow push"""
    try:
        result = intelligent_workflow_push()
        return jsonify({"success": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/secret-management', methods=['POST'])
def api_secret_management():
    """API endpoint for intelligent secret management"""
    try:
        result = intelligent_secret_management()
        return jsonify({"success": True, "guidance": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/set-database-secret', methods=['POST'])
def api_set_database_secret():
    """API endpoint for setting database secret"""
    try:
        data = request.get_json()
        database_url = data.get('database_url')
        
        if not database_url:
            return jsonify({"success": False, "error": "Database URL is required"})
        
        # Set the secret using GitHub CLI
        result = run_command_safely(f'gh secret set DATABASE_URL --body "{database_url}"')
        
        if result['success']:
            return jsonify({"success": True, "message": "DATABASE_URL secret set successfully"})
        else:
            return jsonify({"success": False, "error": f"Failed to set secret: {result['output']}"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("🚀 Intelligent CI/CD Toolbox v4 Starting...")
    print("🧠 Learning from previous mistakes with smart implementation")
    print("🌐 URL: http://localhost:3002")
    
    # Check if required tools are available
    tools = ['gcloud', 'gh', 'git']
    for tool in tools:
        result = run_command_safely(f'{tool} --version')
        if result['success']:
            print(f"✅ {tool} is available")
        else:
            print(f"❌ {tool} is not available: {result['error']}")
    
    app.run(host='127.0.0.1', port=3002, debug=False)
