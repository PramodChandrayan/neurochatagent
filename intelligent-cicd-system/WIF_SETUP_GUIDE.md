# 🔗 Workload Identity Federation Setup Guide

## Overview

This guide provides the correct setup for Workload Identity Federation (WIF) based on official Google Cloud Platform documentation. WIF allows GitHub Actions to authenticate to Google Cloud without storing long-lived service account keys.

## 🎯 Prerequisites

- Google Cloud CLI (`gcloud`) installed and authenticated
- GitHub CLI (`gh`) installed and authenticated
- A Google Cloud project with billing enabled
- A GitHub repository for your CI/CD pipeline

## 📋 Step-by-Step Setup

### 1. Enable Required APIs

```bash
# Enable the required APIs
gcloud services enable iam.googleapis.com
gcloud services enable iamcredentials.googleapis.com
gcloud services enable sts.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Create Service Account

```bash
# Create a service account for GitHub Actions
gcloud iam service-accounts create gha-deployer \
    --display-name="GitHub Actions Deployer" \
    --description="Service account for GitHub Actions CI/CD"
```

### 3. Grant IAM Roles

```bash
# Grant required roles to the service account
PROJECT_ID="your-project-id"
SERVICE_ACCOUNT="gha-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

# Cloud Run administration
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/run.admin"

# Service account impersonation
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/iam.serviceAccountUser"

# Artifact Registry administration
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/artifactregistry.admin"

# Cloud Storage administration
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.admin"

# Secret Manager access
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"

# Cloud Build builder
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudbuild.builds.builder"

# Logging permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/logging.logWriter"

# Monitoring permissions
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/monitoring.metricWriter"
```

### 4. Create Workload Identity Pool

```bash
# Create a Workload Identity Pool
POOL_ID="github-actions-pool-$(date +%s)"
gcloud iam workload-identity-pools create ${POOL_ID} \
    --project=${PROJECT_ID} \
    --location="global" \
    --display-name="GitHub Actions Pool" \
    --description="Workload Identity Pool for GitHub Actions"
```

### 5. Create Workload Identity Provider

```bash
# Create an OIDC provider for GitHub Actions
GITHUB_REPO="your-username/your-repo"

gcloud iam workload-identity-pools providers create-oidc github-actions-provider \
    --project=${PROJECT_ID} \
    --location="global" \
    --workload-identity-pool="${POOL_ID}" \
    --display-name="GitHub OIDC Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-condition="assertion.repository=='${GITHUB_REPO}'"
```

### 6. Configure Workload Identity Binding

```bash
# Get the project number
PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")

# Create the principal set for the repository
PRINCIPAL_SET="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${GITHUB_REPO}"

# Bind the service account to the Workload Identity Pool
gcloud iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT} \
    --project=${PROJECT_ID} \
    --role="roles/iam.workloadIdentityUser" \
    --member="${PRINCIPAL_SET}"
```

## 🔧 Troubleshooting

### Common Issues

1. **"NOT_FOUND: Requested entity was not found"**
   - **Cause**: Pool creation and description timing issue
   - **Solution**: Add a delay after pool creation or construct the pool name manually

2. **"Invalid principalSet format"**
   - **Cause**: Incorrect principalSet format
   - **Solution**: Use the exact format: `principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL_ID/attribute.repository/REPO_NAME`

3. **"Location must be specified"**
   - **Cause**: Missing `--location` parameter
   - **Solution**: Always include `--location="global"` in WIF commands

4. **"Service account already exists"**
   - **Cause**: Service account was previously created
   - **Solution**: This is not an error, continue with the next step

### Verification Commands

```bash
# Verify service account exists
gcloud iam service-accounts list --filter="email:gha-deployer"

# Verify WIF pool exists
gcloud iam workload-identity-pools list --location="global" --filter="displayName:GitHub Actions Pool"

# Verify WIF provider exists
gcloud iam workload-identity-pools providers list --location="global" --workload-identity-pool="${POOL_ID}"

# Verify IAM binding
gcloud iam service-accounts get-iam-policy ${SERVICE_ACCOUNT}
```

## 📝 GitHub Secrets

After setup, add these secrets to your GitHub repository:

```bash
# Add secrets to GitHub repository
gh secret set GCP_PROJECT_ID --body "${PROJECT_ID}" --repo ${GITHUB_REPO}
gh secret set GCP_REGION --body "us-central1" --repo ${GITHUB_REPO}
gh secret set WIF_PROVIDER --body "projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/github-actions-provider" --repo ${GITHUB_REPO}
gh secret set DEPLOY_SA_EMAIL --body "${SERVICE_ACCOUNT}" --repo ${GITHUB_REPO}
```

## 🚀 GitHub Actions Workflow

Example workflow using WIF:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write

    steps:
    - uses: actions/checkout@v4

    - id: auth
      name: Authenticate to Google Cloud
      uses: google-github-actions/auth@v2
      with:
        workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
        service_account: ${{ secrets.DEPLOY_SA_EMAIL }}

    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v2

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy your-service \
          --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/your-image \
          --region ${{ secrets.GCP_REGION }} \
          --platform managed
```

## 📚 Official Documentation

- [Workload Identity Federation Overview](https://cloud.google.com/iam/docs/workload-identity-federation)
- [GitHub Actions with Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation#github-actions)
- [gcloud iam workload-identity-pools](https://cloud.google.com/sdk/gcloud/reference/iam/workload-identity-pools)

## 🔍 Debugging Tips

1. **Enable debug logging**: Add `--verbosity=debug` to gcloud commands
2. **Check IAM policies**: Use `gcloud projects get-iam-policy` to verify bindings
3. **Verify token exchange**: Test the WIF setup with a simple GitHub Action
4. **Check permissions**: Ensure your user has the necessary IAM roles for WIF setup

## ⚠️ Security Best Practices

1. **Repository Restriction**: Always use `attribute-condition` to restrict access to specific repositories
2. **Minimal Permissions**: Grant only the necessary IAM roles to the service account
3. **Regular Audits**: Periodically review IAM policies and service account permissions
4. **Secret Rotation**: Rotate service account keys if they exist (WIF eliminates this need)
