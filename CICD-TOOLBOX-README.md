# 🚀 CI/CD Deployment Toolbox

**Automated deployment to GCP Cloud Run with CLI-first authentication**

## 🎯 **What This Toolbox Does**

This toolbox automates the complete CI/CD setup and deployment process for GCP Cloud Run:

1. **🔐 Authentication** - CLI-based setup for GCP and GitHub
2. **🏗️ GCP Infrastructure** - Automated setup of all required resources
3. **🔑 GitHub Secrets** - Automatic preparation of deployment secrets
4. **🚀 Pipeline Trigger** - One-click deployment to production

## 🚀 **Quick Start**

### **Step 1: Launch the Toolbox**
```bash
# From your project root directory
./launch-cicd-toolbox.sh
```

### **Step 2: Complete Authentication**
The script will automatically:
- Check if you're already authenticated
- Guide you through GCP authentication (opens browser)
- Guide you through GitHub authentication
- Launch the GUI toolbox

### **Step 3: Use the GUI**
Once authentication is complete, the GUI will open and you can:
- Set up GCP infrastructure
- Configure GitHub secrets
- Trigger the deployment pipeline

## 🔐 **Authentication Flow**

### **GCP Authentication**
- **CLI Command**: `gcloud auth login`
- **Browser**: Opens automatically for OAuth
- **Project**: Set automatically or prompted to enter

### **GitHub Authentication**
- **Option 1**: Personal Access Token (recommended)
- **Option 2**: Interactive login
- **Required Scopes**: `repo`, `workflow`, `admin:org`

## 🏗️ **What Gets Set Up Automatically**

### **GCP Resources**
- ✅ Required APIs enabled
- ✅ Service account created
- ✅ IAM roles assigned
- ✅ Workload Identity Federation configured

### **GitHub Integration**
- ✅ Secrets prepared and displayed
- ✅ CI/CD pipeline configuration
- ✅ Deployment automation

## 📁 **Project Structure**

```
embeddingforpinecon/
├── launch-cicd-toolbox.sh          # Main launcher
├── cicd-toolbox/
│   ├── authenticate-and-launch.sh  # Authentication script
│   ├── simple-gui.py              # GUI toolbox
│   └── requirements.txt            # Python dependencies
└── README.md
```

## 🛠️ **Requirements**

- **Google Cloud SDK** (`gcloud`)
- **GitHub CLI** (`gh`)
- **Python 3.7+** with `streamlit`
- **Git repository** with GitHub Actions workflow

## 🔧 **Installation**

### **1. Install Google Cloud SDK**
```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### **2. Install GitHub CLI**
```bash
# macOS
brew install gh

# Or download from: https://cli.github.com/
```

### **3. Install Python Dependencies**
```bash
cd cicd-toolbox
pip install -r requirements.txt
```

## 🚀 **Usage**

### **First Time Setup**
```bash
# 1. Launch the toolbox
./launch-cicd-toolbox.sh

# 2. Complete authentication when prompted
# 3. Use the GUI for the rest
```

### **Subsequent Uses**
```bash
# If already authenticated, just launch
./launch-cicd-toolbox.sh
```

## 🎯 **Workflow Steps**

### **CLI Phase (Authentication)**
1. **GCP Setup**: `gcloud auth login` + project configuration
2. **GitHub Setup**: Token or interactive authentication
3. **Verification**: Check both authentications are working

### **GUI Phase (Deployment)**
1. **GCP Infrastructure**: Create service accounts, enable APIs, setup WIF
2. **GitHub Secrets**: Prepare and display required secrets
3. **Pipeline Trigger**: Deploy to production

## 🔑 **GitHub Secrets Required**

After setup, add these to your GitHub repository secrets:

- `GCP_PROJECT_ID` - Your Google Cloud Project ID
- `GCP_SERVICE_ACCOUNT_EMAIL` - Service account email
- `GCP_WORKLOAD_IDENTITY_PROVIDER` - WIF provider resource
- `GCP_WORKLOAD_IDENTITY_POOL` - WIF pool resource
- `OPENAI_API_KEY` - Your OpenAI API key (if detected)
- `PINECONE_API_KEY` - Your Pinecone API key (if detected)
- `PINECONE_ENVIRONMENT` - Your Pinecone environment (if detected)

## 🚨 **Troubleshooting**

### **Authentication Issues**
```bash
# Check GCP status
gcloud auth list

# Check GitHub status
gh auth status

# Re-authenticate if needed
gcloud auth login
gh auth login
```

### **Permission Issues**
- Ensure your GCP account has necessary permissions
- Check GitHub token has required scopes
- Verify project ID is correct

### **GUI Not Loading**
```bash
# Check if Streamlit is running
ps aux | grep streamlit

# Kill existing processes
pkill -f streamlit

# Restart
./launch-cicd-toolbox.sh
```

## 🎉 **Success Indicators**

- ✅ **GCP**: Service account created, APIs enabled, WIF configured
- ✅ **GitHub**: Secrets prepared and displayed
- ✅ **Pipeline**: Deployment triggered successfully
- ✅ **Deployment**: Application running on GCP Cloud Run

## 📞 **Support**

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all requirements are installed
3. Ensure you have proper permissions
4. Check the terminal output for error messages

---

**Happy Deploying! 🚀**
