# 🔐 Required Secrets for CI/CD Pipeline

## 🚨 **CRITICAL: These secrets MUST be added to GitHub for deployment to work!**

### **1. 🔑 GCP Authentication & Project**
| Secret Name | Description | Example Value | Required |
|-------------|-------------|---------------|----------|
| `GCP_PROJECT_ID` | Your Google Cloud Project ID | `neurofinance-468916` | ✅ **YES** |
| `GCP_SA_KEY` | Service Account JSON key for GCP | `{"type": "service_account", ...}` | ✅ **YES** |
| `REGION` | GCP deployment region | `asia-south1` | ✅ **YES** |
| `SERVICE_NAME` | Your service name | `neurogent-finance-assistant` | ✅ **YES** |

### **2. 🗄️ Database Connections**
| Secret Name | Description | Example Value | Required |
|-------------|-------------|---------------|----------|
| `STAGING_DATABASE_URL` | Staging database connection | `postgresql://user:pass@host/db` | ✅ **YES** |
| `PRODUCTION_DATABASE_URL` | Production database connection | `postgresql://user:pass@host/db` | ✅ **YES** |

### **3. 🤖 OpenAI Configuration**
| Secret Name | Description | Example Value | Required |
|-------------|-------------|---------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` | ✅ **YES** |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` | ✅ **YES** |

### **4. 📍 Pinecone Configuration**
| Secret Name | Description | Example Value | Required |
|-------------|-------------|---------------|----------|
| `PINECONE_API_KEY` | Pinecone API key | `...` | ✅ **YES** |
| `PINECONE_ENVIRONMENT` | Pinecone environment | `gcp-starter` | ✅ **YES** |
| `PINECONE_INDEX_NAME` | Pinecone index name | `finance-knowledge` | ✅ **YES** |
| `PINECONE_NAMESPACE` | Pinecone namespace | `default` | ✅ **YES** |

### **5. 🔧 Application Configuration**
| Secret Name | Description | Example Value | Required |
|-------------|-------------|---------------|----------|
| `DEBUG` | Debug mode | `false` | ⚠️ Optional |
| `MAX_CONTEXT_CHUNKS` | Max context chunks | `5` | ⚠️ Optional |
| `CONFIDENCE_THRESHOLD` | Confidence threshold | `0.7` | ⚠️ Optional |
| `CHAT_STORAGE_DIR` | Chat storage directory | `chats/` | ⚠️ Optional |
| `ALLOWED_HOSTS` | Allowed hosts | `*` | ⚠️ Optional |

## 🚀 **How to Add These Secrets:**

### **Step 1: Go to GitHub Repository**
1. Navigate to your repository on GitHub
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**

### **Step 2: Add Each Secret**
1. Click **New repository secret**
2. Enter the **Name** (exactly as shown above)
3. Enter the **Value**
4. Click **Add secret**

### **Step 3: Verify All Secrets**
Ensure you have added **ALL** secrets marked with ✅ **YES**

## 🔍 **Secret Validation:**

### **Required for Basic Deployment:**
- ✅ `GCP_PROJECT_ID`
- ✅ `GCP_SA_KEY`
- ✅ `REGION`
- ✅ `SERVICE_NAME`

### **Required for Full Functionality:**
- ✅ `OPENAI_API_KEY`
- ✅ `PINECONE_API_KEY`
- ✅ `PINECONE_ENVIRONMENT`
- ✅ `PINECONE_INDEX_NAME`
- ✅ `STAGING_DATABASE_URL`
- ✅ `PRODUCTION_DATABASE_URL`

## 🚨 **Common Issues & Solutions:**

### **Issue 1: "Permission denied" errors**
**Solution:** Ensure `GCP_SA_KEY` has these roles:
- `roles/run.admin`
- `roles/storage.admin`
- `roles/artifactregistry.admin`
- `roles/logging.logWriter`

### **Issue 2: "Database connection failed"**
**Solution:** Verify database URLs are correct and accessible

### **Issue 3: "OpenAI API key invalid"**
**Solution:** Check `OPENAI_API_KEY` format and validity

### **Issue 4: "Pinecone index not found"**
**Solution:** Verify `PINECONE_INDEX_NAME` exists in your Pinecone account

## 🔧 **Testing Secrets:**

### **Test GCP Authentication:**
```bash
# Test with gcloud CLI
gcloud auth activate-service-account --key-file=service-account.json
gcloud config set project YOUR_PROJECT_ID
gcloud run services list
```

### **Test Database Connection:**
```bash
# Test PostgreSQL connection
psql "YOUR_DATABASE_URL" -c "SELECT version();"
```

### **Test OpenAI API:**
```bash
# Test OpenAI API key
curl -H "Authorization: Bearer YOUR_OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### **Test Pinecone API:**
```bash
# Test Pinecone API key
curl -H "Api-Key: YOUR_PINECONE_API_KEY" \
     https://YOUR_INDEX_NAME-YOUR_ENVIRONMENT.svc.pinecone.io/describe_index_stats
```

## 📋 **Pre-Deployment Checklist:**

- [ ] All required secrets added to GitHub
- [ ] GCP service account has proper permissions
- [ ] Database connections are accessible
- [ ] OpenAI API key is valid
- [ ] Pinecone index exists and is accessible
- [ ] GCP project is properly configured
- [ ] Artifact Registry repository exists

## 🆘 **Need Help?**

If you encounter issues:
1. Check the GitHub Actions logs for specific error messages
2. Verify all secrets are correctly added
3. Test individual services (GCP, database, APIs) manually
4. Check the troubleshooting section in `CI-CD-TOOLBOX.md`

## 🎯 **Next Steps:**

1. ✅ Add all required secrets to GitHub
2. ✅ Verify GCP permissions and configuration
3. ✅ Test database connections
4. ✅ Push code to trigger CI/CD pipeline
5. ✅ Monitor deployment progress

---

**Remember:** The CI/CD pipeline will fail if any required secrets are missing or invalid. Double-check everything before deployment!
