# Deploy ChariotAI with Terraform

## Prerequisites

1. **Azure CLI** installed and logged in:
```bash
az login
az account set --subscription "YOUR_SUBSCRIPTION_NAME"
```

2. **Terraform** installed (v1.5+)

3. **Telegram Bot** created:
   - Message `@BotFather` on Telegram
   - Send `/newbot` and follow prompts
   - Copy the bot token
   - Message `@userinfobot` to get your chat ID

4. **GitHub Token** (for automated deployment):
```bash
export GITHUB_TOKEN="your_github_personal_access_token"
```

## Quick Deploy (5 Commands)

### 1. Create `terraform.tfvars`

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:
```hcl
subscription_id      = "your-azure-subscription-id"
tenant_id            = "your-azure-tenant-id"
app_name             = "your-university-chatbot"
resource_group_name  = "rg-your-university-chatbot"
telegram_bot_token   = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
telegram_chat_id     = "123456789"
github_repo          = "your-username/your-repo"
chariotai_domain     = "chatbot.your-university.edu"  # Optional
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Preview Changes

```bash
terraform plan
```

### 4. Deploy Everything

```bash
terraform apply
```

Type `yes` when prompted.

### 5. Get Your URLs

```bash
terraform output
```

You'll see:
- `frontend_url` - Your chatbot website
- `backend_url` - Your API endpoint
- `openai_endpoint` - Your Azure OpenAI endpoint

## What Gets Deployed

✅ **Azure Static Web App** (Frontend) - FREE  
✅ **Azure App Service** (Backend API) - ~£10/month  
✅ **Azure OpenAI** (GPT-4 + Embeddings) - Pay per use  
✅ **Azure AI Search** (Vector database) - FREE tier  
✅ **GitHub Actions** (Auto-deployment) - FREE  

**Total: ~£50-150/month** depending on usage

## Post-Deployment Steps

### 1. Ingest Your University Data

```bash
cd ../backend
python ingest.py --data-folder ../your-university-data
```

### 2. Test the Chatbot

Visit your `frontend_url` and:
- Ask: "Tell me about accommodation"
- Test crisis: "I am depressed" (should alert Telegram)
- Reply on Telegram (should show on website)
- Type `/end_sessionid` to close session

### 3. Customize

Edit these files:
- `frontend/src/App.jsx` - Change branding, colors, university name
- `backend/main.py` - Update crisis keywords, contact numbers

Then push to GitHub - auto-deploys!

## Update Deployment

```bash
terraform apply
```

## Destroy Everything

```bash
terraform destroy
```

## Troubleshooting

### "Error: Insufficient quota"
- Change `location` in `terraform.tfvars` to different region
- Or request quota increase in Azure Portal

### "Telegram not working"
- Check bot token and chat ID in `terraform.tfvars`
- Verify bot is started (send `/start` to your bot)

### "Backend not responding"
- Check App Service logs in Azure Portal
- Verify GitHub Actions deployment succeeded

## Cost Optimization

**For small universities (<5000 students):**
```hcl
app_service_sku = "B1"    # ~£10/month
search_sku      = "free"  # FREE
```

**For large universities (>10000 students):**
```hcl
app_service_sku = "S1"     # ~£50/month
search_sku      = "basic"  # ~£60/month
```

## Support

Issues? Open a GitHub issue or contact your IT department.
