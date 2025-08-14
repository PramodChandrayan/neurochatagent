#!/bin/bash
# 🔐 Automated Secrets Setup Script
# Uses GitHub CLI to intelligently set up secrets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ANALYSIS_FILE="$PROJECT_ROOT/ci-cd-analysis.json"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%M:%S')] ERROR:${NC} $1"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%M:%S')] INFO:${NC} $1"
}

# Header
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                🔐 Automated Secrets Setup                   ║"
echo "║              Smart secret detection & setup                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check GitHub CLI
    if ! command -v gh &> /dev/null; then
        error "GitHub CLI (gh) is required. Install from: https://cli.github.com/"
    fi
    
    # Check authentication
    if ! gh auth status &> /dev/null; then
        error "GitHub CLI not authenticated. Run: gh auth login"
    fi
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not a git repository"
    fi
    
    log "Prerequisites check completed"
}

# Get repository info
get_repo_info() {
    REPO_URL=$(git remote get-url origin)
    REPO_NAME=$(basename -s .git "$REPO_URL")
    REPO_OWNER=$(echo "$REPO_URL" | sed -n 's/.*github\.com[:/]\([^/]*\)\/.*/\1/p')
    
    log "Repository: $REPO_OWNER/$REPO_NAME"
    
    # Verify repository access
    if ! gh repo view "$REPO_OWNER/$REPO_NAME" &> /dev/null; then
        error "Cannot access repository $REPO_OWNER/$REPO_NAME"
    fi
}

# Smart secret detection
detect_secrets() {
    log "Detecting required secrets..."
    
    if [ ! -f "$ANALYSIS_FILE" ]; then
        error "Project analysis not found. Run project analyzer first."
    fi
    
    # Read secrets from analysis
    REQUIRED_SECRETS=$(python3 -c "
import json
with open('$ANALYSIS_FILE') as f:
    data = json.load(f)
    secrets = data.get('ci_cd_requirements', {}).get('required_secrets', [])
    print('\\n'.join(secrets))
")
    
    if [ -z "$REQUIRED_SECRETS" ]; then
        warn "No required secrets detected in analysis"
        return
    fi
    
    echo -e "${YELLOW}Required secrets detected:${NC}"
    echo "$REQUIRED_SECRETS" | while read -r secret; do
        if [ -n "$secret" ]; then
            echo "  - $secret"
        fi
    done
    echo ""
}

# Smart secret value suggestions
suggest_secret_values() {
    log "Providing smart suggestions for secret values..."
    
    echo -e "${BLUE}Smart Secret Suggestions:${NC}"
    echo ""
    
    # GCP Project ID detection
    if command -v gcloud &> /dev/null; then
        CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "Not set")
        if [ "$CURRENT_PROJECT" != "Not set" ]; then
            echo "🔍 GCP_PROJECT_ID: $CURRENT_PROJECT (detected from gcloud)"
        fi
    fi
    
    # GCP Region detection
    if command -v gcloud &> /dev/null; then
        CURRENT_REGION=$(gcloud config get-value compute/region 2>/dev/null || echo "Not set")
        if [ "$CURRENT_REGION" != "Not set" ]; then
            echo "🔍 REGION: $CURRENT_REGION (detected from gcloud)"
        fi
    fi
    
    # Service name suggestion
    echo "🔍 SERVICE_NAME: $REPO_NAME (from repository name)"
    
    # Environment file detection
    if [ -f ".env" ]; then
        echo "🔍 Found .env file - check for existing values"
        echo "   Common patterns: OPENAI_API_KEY, PINECONE_API_KEY"
    fi
    
    # Dockerfile detection
    if [ -f "Dockerfile" ]; then
        echo "🔍 Found Dockerfile - check for environment variables"
    fi
    
    # Config file detection
    if [ -f "config.py" ]; then
        echo "🔍 Found config.py - check for configuration values"
    fi
    
    echo ""
}

# Interactive secret setup
interactive_secret_setup() {
    log "Starting interactive secret setup..."
    
    echo -e "${YELLOW}Interactive Setup Options:${NC}"
    echo "1. Set secrets one by one (recommended for first time)"
    echo "2. Bulk import from .env file"
    echo "3. Skip and set manually later"
    echo ""
    
    read -p "Choose option (1-3): " -r choice
    
    case $choice in
        1)
            setup_secrets_one_by_one
            ;;
        2)
            bulk_import_from_env
            ;;
        3)
            log "Skipping secret setup. Set manually in GitHub repository settings."
            return
            ;;
        *)
            error "Invalid choice. Please select 1, 2, or 3."
            ;;
    esac
}

# Setup secrets one by one
setup_secrets_one_by_one() {
    log "Setting up secrets one by one..."
    
    echo "$REQUIRED_SECRETS" | while read -r secret; do
        if [ -n "$secret" ]; then
            echo ""
            echo -e "${BLUE}Setting up: $secret${NC}"
            
            # Provide context for the secret
            case $secret in
                GCP_PROJECT_ID)
                    echo "   This is your Google Cloud Project ID"
                    echo "   Example: neurofinance-468916"
                    ;;
                GCP_SA_KEY)
                    echo "   This is your GCP Service Account JSON key"
                    echo "   You can generate this in GCP Console → IAM → Service Accounts"
                    ;;
                OPENAI_API_KEY)
                    echo "   This is your OpenAI API key"
                    echo "   Get it from: https://platform.openai.com/api-keys"
                    ;;
                PINECONE_API_KEY)
                    echo "   This is your Pinecone API key"
                    echo "   Get it from: https://app.pinecone.io/"
                    ;;
                *)
                    echo "   Please provide the value for this secret"
                    ;;
            esac
            
            echo -n "Enter value for $secret (or press Enter to skip): "
            read -s secret_value
            echo ""
            
            if [ -n "$secret_value" ]; then
                log "Setting secret: $secret"
                echo "$secret_value" | gh secret set "$secret" --repo "$REPO_OWNER/$REPO_NAME"
                echo "✅ Secret $secret set successfully"
            else
                echo "⏭️ Skipping $secret"
            fi
        fi
    done
}

# Bulk import from .env file
bulk_import_from_env() {
    log "Bulk importing secrets from .env file..."
    
    if [ ! -f ".env" ]; then
        error ".env file not found"
    fi
    
    echo "Reading .env file..."
    
    # Read .env file and extract secrets
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        if [[ $key =~ ^[[:space:]]*# ]] || [[ -z $key ]]; then
            continue
        fi
        
        # Remove quotes and spaces
        key=$(echo "$key" | xargs)
        value=$(echo "$value" | xargs | sed 's/^["'\'']//;s/["'\'']$//')
        
        if [ -n "$key" ] && [ -n "$value" ]; then
            echo "Found: $key"
            
            # Check if this secret is required
            if echo "$REQUIRED_SECRETS" | grep -q "^$key$"; then
                echo -n "Set $key as GitHub secret? (y/N): "
                read -r confirm
                
                if [[ $confirm =~ ^[Yy]$ ]]; then
                    log "Setting secret: $key"
                    echo "$value" | gh secret set "$key" --repo "$REPO_OWNER/$REPO_NAME"
                    echo "✅ Secret $key set successfully"
                else
                    echo "⏭️ Skipping $key"
                fi
            else
                echo "ℹ️ $key not in required secrets list"
            fi
        fi
    done < .env
    
    log "Bulk import completed"
}

# Verify secrets setup
verify_secrets() {
    log "Verifying secrets setup..."
    
    echo -e "${BLUE}Current repository secrets:${NC}"
    gh secret list --repo "$REPO_OWNER/$REPO_NAME" || {
        warn "Could not list secrets. Check repository permissions."
        return
    }
    
    echo ""
    echo -e "${YELLOW}Verification:${NC}"
    
    # Check critical secrets
    critical_secrets=("GCP_PROJECT_ID" "GCP_SA_KEY" "OPENAI_API_KEY" "PINECONE_API_KEY")
    
    for secret in "${critical_secrets[@]}"; do
        if gh secret list --repo "$REPO_OWNER/$REPO_NAME" | grep -q "$secret"; then
            echo "✅ $secret - Set"
        else
            echo "❌ $secret - Missing"
        fi
    done
    
    echo ""
}

# Create secrets template
create_secrets_template() {
    log "Creating secrets template file..."
    
    TEMPLATE_FILE="$PROJECT_ROOT/secrets-template.md"
    
    cat > "$TEMPLATE_FILE" << EOF
# 🔐 Secrets Template for $REPO_NAME

## Required Secrets

Copy these to your GitHub repository → Settings → Secrets and variables → Actions

EOF
    
    echo "$REQUIRED_SECRETS" | while read -r secret; do
        if [ -n "$secret" ]; then
            cat >> "$TEMPLATE_FILE" << EOF
### $secret
- **Description**: [Add description]
- **Value**: [Add value]
- **Source**: [Where to get this value]

EOF
        fi
    done
    
    cat >> "$TEMPLATE_FILE" << EOF

## How to Add Secrets

1. Go to: https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret above
4. Verify all secrets are set

## Testing Secrets

After setting secrets, push to trigger CI/CD pipeline and verify deployment.
EOF
    
    log "Secrets template created: $TEMPLATE_FILE"
}

# Main execution
main() {
    check_prerequisites
    get_repo_info
    detect_secrets
    suggest_secret_values
    interactive_secret_setup
    verify_secrets
    create_secrets_template
    
    echo ""
    echo -e "${GREEN}🎉 Secrets setup completed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review the secrets-template.md file"
    echo "2. Add any missing secrets manually"
    echo "3. Push code to trigger CI/CD pipeline"
    echo "4. Monitor deployment progress"
    echo ""
    echo "For manual setup, go to:"
    echo "https://github.com/$REPO_OWNER/$REPO_NAME/settings/secrets/actions"
}

# Run main function
main "$@"
