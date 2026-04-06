# ChariotAI - Deploy to Your University

## 🎓 For Universities: 10-Minute Deployment

ChariotAI is ready to deploy to your university with **one Terraform command**.

### What You Get

✅ AI chatbot answering student questions 24/7  
✅ Crisis detection with live Telegram support  
✅ Fully hosted on Azure (GDPR compliant)  
✅ Auto-scaling infrastructure  
✅ Costs £60-210/month for 10,000 students  

---

## Quick Deploy

### Prerequisites (5 minutes)

1. **Azure subscription** - [Get free trial](https://azure.microsoft.com/free/)
2. **Telegram bot** - Message `@BotFather`, send `/newbot`
3. **Azure CLI** - [Install here](https://docs.microsoft.com/cli/azure/install-azure-cli)
4. **Terraform** - [Install here](https://www.terraform.io/downloads)

### Deploy (5 commands)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/AIChatbotUniKent.git
cd AIChatbotUniKent/terraform

# 2. Login to Azure
az login

# 3. Configure your university
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your details

# 4. Deploy everything
terraform init
terraform apply

# 5. Get your chatbot URL
terraform output frontend_url
```

**Done!** Your chatbot is live at the URL shown.

---

## Configuration File

Edit `terraform/terraform.tfvars`:

```hcl
# Your Azure details
subscription_id = "your-subscription-id"
tenant_id       = "your-tenant-id"

# Your university name
app_name            = "oxford-chatbot"
resource_group_name = "rg-oxford-chatbot"

# Telegram (from @BotFather)
telegram_bot_token = "123456789:ABCdef..."
telegram_chat_id   = "123456789"

# GitHub repo (your fork)
github_repo = "oxford-university/chatbot"
```

---

## Add Your Content

```bash
# Create folder with your university info
mkdir university-data
# Add .txt files with FAQs, policies, etc.

# Ingest into AI
cd backend
python ingest.py --data-folder ../university-data
```

---

## What Gets Deployed

| Resource | Purpose | Cost |
|----------|---------|------|
| Static Web App | Frontend (React) | FREE |
| App Service | Backend API | £10-50/month |
| Azure OpenAI | GPT-4 + Embeddings | £50-100/month |
| AI Search | Vector database | FREE or £60/month |
| Telegram Bot | Crisis support | FREE |

**Total: £60-210/month**

---

## Crisis Support Flow

1. Student types "I am depressed" or "kill"
2. System alerts your Telegram
3. You chat with student in real-time
4. Type `/end_sessionid` to close
5. Student returns to AI chatbot

---

## Customization

### Change University Name

Edit `frontend/src/App.jsx`:
```javascript
<h1>🤖 YourUniversity AI Assistant</h1>
```

### Update Crisis Keywords

Edit `backend/main.py`:
```python
CRISIS_KEYWORDS = [
    "suicide", "kill", "depressed",
    # Add your terms
]
```

### Change Colors

Edit `frontend/src/index.css`:
```css
:root {
  --primary-color: #your-color;
}
```

---

## Support

- **Full Guide**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Terraform Docs**: [terraform/README.md](./terraform/README.md)
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/AIChatbotUniKent/issues)

---

## License

MIT - Free for universities to use and modify.
