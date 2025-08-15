#!/bin/bash

# 🚀 CI/CD Toolbox Authentication & Launch Script
# This script handles authentication first, then launches the GUI

set -e

echo "🚀 CI/CD Toolbox Authentication & Launch"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "gcloud CLI not found. Please install Google Cloud SDK first."
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI not found. Please install GitHub CLI first."
        echo "Visit: https://cli.github.com/"
        exit 1
    fi
    
    if ! command -v streamlit &> /dev/null; then
        print_warning "Streamlit not found. Installing now..."
        pip install streamlit
    fi
    
    print_success "All requirements satisfied!"
    echo ""
}

# Check GCP authentication
check_gcp_auth() {
    print_status "Checking GCP authentication..."
    
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        local account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)
        print_success "GCP authenticated as: $account"
        
        # Check if project is set
        local project=$(gcloud config get-value project 2>/dev/null || echo "")
        if [ -n "$project" ]; then
            print_success "GCP project set to: $project"
            return 0
        else
            print_warning "GCP project not set"
            return 1
        fi
    else
        print_warning "GCP not authenticated"
        return 1
    fi
}

# Authenticate with GCP
authenticate_gcp() {
    print_status "Starting GCP authentication..."
    echo ""
    echo "Your browser will open for Google authentication."
    echo "Please complete the sign-in process."
    echo ""
    
    # Run gcloud auth login
    if gcloud auth login; then
        print_success "GCP authentication completed!"
        
        # Set project if not already set
        local project=$(gcloud config get-value project 2>/dev/null || echo "")
        if [ -z "$project" ]; then
            echo ""
            echo "Please enter your GCP Project ID:"
            read -p "Project ID: " project_id
            
            if [ -n "$project_id" ]; then
                gcloud config set project "$project_id"
                print_success "Project set to: $project_id"
            fi
        fi
        
        return 0
    else
        print_error "GCP authentication failed"
        return 1
    fi
}

# Check GitHub authentication
check_gh_auth() {
    print_status "Checking GitHub authentication..."
    
    if gh auth status &>/dev/null; then
        # Use a more compatible method to extract username
        local username=$(gh auth status 2>/dev/null | grep "Logged in to github.com as" | sed 's/.*Logged in to github.com as //' | sed 's/.*//' || echo "unknown")
        if [ -z "$username" ] || [ "$username" = "unknown" ]; then
            username=$(gh auth status 2>/dev/null | grep "github.com" | head -1 | sed 's/.*github.com as //' | sed 's/.*//' || echo "unknown")
        fi
        print_success "GitHub authenticated as: $username"
        return 0
    else
        print_warning "GitHub not authenticated"
        return 1
    fi
}

# Authenticate with GitHub
authenticate_github() {
    print_status "Starting GitHub authentication..."
    echo ""
    echo "Choose authentication method:"
    echo "1. Personal Access Token (recommended)"
    echo "2. Interactive login"
    echo ""
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            echo ""
            echo "Please enter your GitHub Personal Access Token:"
            echo "Get it from: GitHub Settings → Tokens → Generate new token"
            echo "Required scopes: repo, workflow, admin:org"
            echo ""
            read -s -p "Token: " token
            echo ""
            
            if [ -n "$token" ]; then
                if echo "$token" | gh auth login --with-token; then
                    print_success "GitHub authentication completed!"
                    return 0
                else
                    print_error "GitHub authentication failed"
                    return 1
                fi
            else
                print_error "No token provided"
                return 1
            fi
            ;;
        2)
            echo ""
            echo "Starting interactive GitHub login..."
            if gh auth login; then
                print_success "GitHub authentication completed!"
                return 0
            else
                print_error "GitHub authentication failed"
                return 1
            fi
            ;;
        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
}

# Main authentication flow
main() {
    echo "🔐 Starting authentication process..."
    echo ""
    
    # Check requirements
    check_requirements
    
    # GCP Authentication
    if ! check_gcp_auth; then
        echo ""
        print_status "GCP authentication required"
        if authenticate_gcp; then
            print_success "GCP authentication successful!"
        else
            print_error "Failed to complete GCP authentication"
            exit 1
        fi
    fi
    
    echo ""
    
    # GitHub Authentication
    if ! check_gh_auth; then
        echo ""
        print_status "GitHub authentication required"
        if authenticate_github; then
            print_success "GitHub authentication successful!"
        else
            print_error "Failed to complete GitHub authentication"
            exit 1
        fi
    fi
    
    echo ""
    print_success "🎉 All authentication completed successfully!"
    echo ""
    
    # Final verification
    print_status "Verifying authentication..."
    if check_gcp_auth && check_gh_auth; then
        print_success "✅ Ready to launch GUI toolbox!"
        echo ""
        
        # Launch the GUI
        print_status "Launching CI/CD Toolbox..."
        echo "The toolbox will open in your browser at: http://localhost:8506"
        echo ""
        echo "Press Ctrl+C to stop the toolbox"
        echo ""
        
        # Change to the cicd-toolbox directory and launch
        cd "$(dirname "$0")"
        streamlit run simple-gui.py --server.port 8506
        
    else
        print_error "Authentication verification failed"
        exit 1
    fi
}

# Run main function
main "$@"
