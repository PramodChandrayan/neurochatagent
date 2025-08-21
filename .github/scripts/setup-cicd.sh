#!/bin/bash
# 🚀 Universal CI/CD Setup Script
# Automatically sets up CI/CD for any project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ANALYSIS_FILE="$PROJECT_ROOT/ci-cd-analysis.json"
SETUP_LOG="$PROJECT_ROOT/cicd-setup.log"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$SETUP_LOG"
}

warn() {
    echo -e "${YELLOW}[$(date +'%M:%S')] WARNING:${NC} $1" | tee -a "$SETUP_LOG"
}

error() {
    echo -e "${RED}[$(date +'%M:%S')] ERROR:${NC} $1" | tee -a "$SETUP_LOG"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%M:%S')] INFO:${NC} $1" | tee -a "$SETUP_LOG"
}

# Header
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🚀 Universal CI/CD Setup                 ║"
echo "║                Automatically configure CI/CD                ║"
echo "║                    for any project!                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

log "Starting CI/CD setup for project: $PROJECT_ROOT"

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not a git repository. Please run this script from a git repository."
    fi
    
    # Check if GitHub CLI is available
    if ! command -v gh &> /dev/null; then
        warn "GitHub CLI (gh) not found. Some features may be limited."
    else
        log "GitHub CLI found: $(gh --version)"
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        error "Python 3 is required but not found."
    fi
    
    log "Prerequisites check completed"
}

# Analyze project
analyze_project() {
    log "Analyzing project structure..."
    
    if [ ! -f "$ANALYSIS_FILE" ]; then
        log "Running project analysis..."
        
        # Run the project analyzer
        cd "$PROJECT_ROOT"
        python3 "$SCRIPT_DIR/project-analyzer.py" --summary
        
        if [ ! -f "$ANALYSIS_FILE" ]; then
            error "Failed to generate project analysis"
        fi
    else
        log "Project analysis already exists"
    fi
}

# Generate CI/CD files
generate_cicd_files() {
    log "Generating CI/CD files..."
    
    cd "$PROJECT_ROOT"
    
    # Run the CI/CD generator
    python3 "$SCRIPT_DIR/generate-ci-cd.py"
    
    if [ ! -f ".github/workflows/ci-cd-pipeline.yml" ]; then
        error "Failed to generate CI/CD workflow"
    fi
    
    log "CI/CD files generated successfully"
}

# Setup GitHub repository
setup_github_repo() {
    log "Setting up GitHub repository..."
    
    # Get repository info
    REPO_URL=$(git remote get-url origin 2>/dev/null || echo "")
    
    if [ -z "$REPO_URL" ]; then
        warn "No remote origin found. Please add a GitHub remote:"
        echo "  git remote add origin https://github.com/username/repository.git"
        return 1
    fi
    
    # Extract repository name
    REPO_NAME=$(basename -s .git "$REPO_URL")
    REPO_OWNER=$(echo "$REPO_URL" | sed -n 's/.*github\.com[:/]\([^/]*\)\/.*/\1/p')
    
    log "Repository: $REPO_OWNER/$REPO_NAME"
    
    # Check if GitHub CLI is available for advanced setup
    if command -v gh &> /dev/null; then
        setup_github_cli "$REPO_OWNER" "$REPO_NAME"
    else
        setup_github_manual "$REPO_OWNER" "$REPO_NAME"
    fi
}

# Setup with GitHub CLI
setup_github_cli() {
    local owner="$1"
    local repo="$2"
    
    log "Using GitHub CLI for setup..."
    
    # Check authentication
    if ! gh auth status &> /dev/null; then
        warn "GitHub CLI not authenticated. Please run: gh auth login"
        return 1
    fi
    
    # Check if repository exists
    if ! gh repo view "$owner/$repo" &> /dev/null; then
        error "Repository $owner/$repo not found or not accessible"
    fi
    
    # Create environments
    log "Creating GitHub environments..."
    
    # Staging environment
    if ! gh api "repos/$owner/$repo/environments/staging" &> /dev/null; then
        log "Creating staging environment..."
        gh api "repos/$owner/$repo/environments" \
            -f name=staging \
            -f protection_rules='[{"required_reviewers":{"users":["'$owner'"]}}]'
    fi
    
    # Production environment
    if ! gh api "repos/$owner/$repo/environments/production" &> /dev/null; then
        log "Creating production environment..."
        gh api "repos/$owner/$repo/environments" \
            -f name=production \
            -f protection_rules='[{"required_reviewers":{"users":["'$owner'"]}}]'
    fi
    
    log "GitHub environments created successfully"
}

# Manual GitHub setup
setup_github_manual() {
    local owner="$1"
    local repo="$2"
    
    log "Manual GitHub setup required..."
    
    echo -e "${YELLOW}Please complete these steps manually:${NC}"
    echo ""
    echo "1. Go to: https://github.com/$owner/$repo/settings/environments"
    echo "2. Create 'staging' environment:"
    echo "   - Name: staging"
    echo "   - Protection rules: Required reviewers (add yourself)"
    echo ""
    echo "3. Create 'production' environment:"
    echo "   - Name: production"
    echo "   - Protection rules: Required reviewers (add yourself + 1 more)"
    echo ""
    echo "4. Go to: https://github.com/$owner/$repo/settings/secrets/actions"
    echo "5. Add the required secrets (see CI-CD-SETUP.md for details)"
    echo ""
    
    read -p "Press Enter when you've completed these steps..."
}

# Setup required secrets
setup_secrets() {
    log "Setting up required secrets..."
    
    # Read analysis to get required secrets
    if [ -f "$ANALYSIS_FILE" ]; then
        REQUIRED_SECRETS=$(python3 -c "
import json
with open('$ANALYSIS_FILE') as f:
    data = json.load(f)
    secrets = data.get('ci_cd_requirements', {}).get('required_secrets', [])
    print('\\n'.join(secrets))
")
        
        if [ -n "$REQUIRED_SECRETS" ]; then
            echo -e "${YELLOW}Required secrets for this project:${NC}"
            echo "$REQUIRED_SECRETS" | while read -r secret; do
                if [ -n "$secret" ]; then
                    echo "  - $secret"
                fi
            done
            echo ""
            
            # Check if GitHub CLI is available for secret setup
            if command -v gh &> /dev/null; then
                setup_secrets_cli
            else
                setup_secrets_manual
            fi
        fi
    fi
}

# Setup secrets with GitHub CLI
setup_secrets_cli() {
    log "Using GitHub CLI for secret setup..."
    
    if ! gh auth status &> /dev/null; then
        warn "GitHub CLI not authenticated. Please run: gh auth login"
        return 1
    fi
    
    echo -e "${YELLOW}Setting up secrets with GitHub CLI...${NC}"
    echo "For each secret, you'll be prompted to enter the value."
    echo "Press Ctrl+C to skip and set manually later."
    echo ""
    
    # Get repository info
    REPO_URL=$(git remote get-url origin)
    REPO_NAME=$(basename -s .git "$REPO_URL")
    REPO_OWNER=$(echo "$REPO_URL" | sed -n 's/.*github\.com[:/]\([^/]*\)\/.*/\1/p')
    
    echo "$REQUIRED_SECRETS" | while read -r secret; do
        if [ -n "$secret" ]; then
            echo -n "Enter value for $secret: "
            read -s secret_value
            echo ""
            
            if [ -n "$secret_value" ]; then
                log "Setting secret: $secret"
                echo "$secret_value" | gh secret set "$secret" --repo "$REPO_OWNER/$REPO_NAME"
            fi
        fi
    done
    
    log "Secrets setup completed"
}

# Manual secrets setup
setup_secrets_manual() {
    echo -e "${YELLOW}Manual secrets setup required:${NC}"
    echo ""
    echo "1. Go to your GitHub repository"
    echo "2. Navigate to Settings → Secrets and variables → Actions"
    echo "3. Add the following secrets:"
    echo ""
    
    echo "$REQUIRED_SECRETS" | while read -r secret; do
        if [ -n "$secret" ]; then
            echo "   - $secret"
        fi
    done
    
    echo ""
    echo "4. For each secret, click 'New repository secret'"
    echo "5. Enter the name and value"
    echo ""
    
    read -p "Press Enter when you've completed setting up the secrets..."
}

# Validate setup
validate_setup() {
    log "Validating CI/CD setup..."
    
    # Check if workflow file exists
    if [ ! -f ".github/workflows/ci-cd-pipeline.yml" ]; then
        error "CI/CD workflow file not found"
    fi
    
    # Check if deployment config exists
    if [ ! -f "deployment-config.yml" ]; then
        warn "Deployment configuration file not found"
    fi
    
    # Check if setup guide exists
    if [ ! -f "CI-CD-SETUP.md" ]; then
        warn "Setup guide not found"
    fi
    
    # Validate workflow syntax
    log "Validating workflow syntax..."
    if command -v yamllint &> /dev/null; then
        yamllint .github/workflows/ci-cd-pipeline.yml || warn "Workflow has syntax warnings"
    else
        log "yamllint not available, skipping syntax validation"
    fi
    
    log "Setup validation completed"
}

# Create initial commit
create_initial_commit() {
    log "Creating initial CI/CD commit..."
    
    # Check if there are changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        log "No changes to commit"
        return 0
    fi
    
    # Add CI/CD files
    git add .github/ || true
    git add deployment-config.yml || true
    git add CI-CD-SETUP.md || true
    git add ci-cd-analysis.json || true
    
    # Commit
    if git diff --cached --quiet; then
        log "No CI/CD files to commit"
    else
        git commit -m "🚀 Add CI/CD pipeline and configuration
        
- Automated CI/CD workflow
- Database migration support
- Security scanning and testing
- Progressive deployment
- Health monitoring and rollback"
        log "Initial CI/CD commit created"
    fi
}

# Push to trigger pipeline
push_to_trigger() {
    log "Pushing changes to trigger CI/CD pipeline..."
    
    # Check if we should push
    echo -e "${YELLOW}Do you want to push the changes now to trigger the CI/CD pipeline? (y/N)${NC}"
    read -p "> " -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Check current branch
        CURRENT_BRANCH=$(git branch --show-current)
        
        if [ "$CURRENT_BRANCH" = "main" ]; then
            warn "You're on the main branch. Consider creating a feature branch first."
            echo -e "${YELLOW}Continue with push to main? (y/N)${NC}"
            read -p "> " -r main_response
            
            if [[ ! "$main_response" =~ ^[Yy]$ ]]; then
                log "Push cancelled. You can push manually later with: git push origin $CURRENT_BRANCH"
                return 0
            fi
        fi
        
        # Push
        git push origin "$CURRENT_BRANCH"
        log "Changes pushed successfully! CI/CD pipeline should start automatically."
        
        # Show pipeline URL if GitHub CLI is available
        if command -v gh &> /dev/null; then
            REPO_URL=$(git remote get-url origin)
            REPO_NAME=$(basename -s .git "$REPO_URL")
            REPO_OWNER=$(echo "$REPO_URL" | sed -n 's/.*github\.com[:/]\([^/]*\)\/.*/\1/p')
            
            echo ""
            echo -e "${GREEN}🎉 CI/CD Pipeline Started!${NC}"
            echo "View progress at: https://github.com/$REPO_OWNER/$REPO_NAME/actions"
            echo ""
        fi
    else
        log "Push cancelled. You can push manually later with: git push origin $(git branch --show-current)"
    fi
}

# Show next steps
show_next_steps() {
    echo ""
    echo -e "${GREEN}🎉 CI/CD Setup Completed Successfully!${NC}"
    echo ""
    echo "📁 Generated files:"
    echo "  - .github/workflows/ci-cd-pipeline.yml"
    echo "  - deployment-config.yml"
    echo "  - CI-CD-SETUP.md"
    echo "  - ci-cd-analysis.json"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Review the generated files"
    echo "  2. Customize configuration if needed"
    echo "  3. Push to trigger the pipeline"
    echo "  4. Monitor the pipeline execution"
    echo ""
    echo "📚 Documentation:"
    echo "  - CI-CD-SETUP.md - Setup guide for your project"
    echo "  - CI-CD-TOOLBOX.md - Complete toolbox documentation"
    echo ""
    echo "🔧 Customization:"
    echo "  - Update PROJECT_ID, REGION, SERVICE_NAME in workflow"
    echo "  - Modify deployment configuration as needed"
    echo "  - Add project-specific environment variables"
    echo ""
}

# Main execution
main() {
    # Clear log file
    > "$SETUP_LOG"
    
    # Execute setup steps
    check_prerequisites
    analyze_project
    generate_cicd_files
    setup_github_repo
    setup_secrets
    validate_setup
    create_initial_commit
    push_to_trigger
    show_next_steps
    
    log "CI/CD setup completed successfully"
}

# Handle script interruption
trap 'error "Setup interrupted by user"' INT

# Run main function
main "$@"
