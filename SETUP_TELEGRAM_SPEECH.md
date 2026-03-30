# Setup Guide: Telegram Alerts & Azure Speech

## 1. Create Telegram Bot for Crisis Alerts

### Step 1: Create Bot with BotFather
1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Choose a name (e.g., "ChariotAI Support")
4. Choose a username (e.g., "chariotai_support_bot")
5. Copy the **bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID
1. Search for `@userinfobot` on Telegram
2. Start a chat with it
3. It will send you your **Chat ID** (a number like: `123456789`)
4. OR create a group, add your bot, and use `@RawDataBot` to get the group chat ID

### Step 3: Add to .env
```env
TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
TELEGRAM_CHAT_ID="123456789"
```

### Step 4: Test It
Send a message with "depressed" to your chatbot - you should receive a Telegram alert!

---

## 2. Setup Azure Speech Services

### Step 1: Create Speech Resource in Azure
1. Go to Azure Portal
2. Create new resource → Search "Speech"
3. Click "Speech Services"
4. Fill in:
   - Resource group: (use existing or create new)
   - Region: **UK South** (closest to Kent)
   - Name: `kent-speech-service`
   - Pricing tier: **Free F0** (5 hours audio/month free)
5. Click "Review + Create"

### Step 2: Get Keys
1. Go to your Speech resource
2. Click "Keys and Endpoint"
3. Copy **KEY 1**
4. Note the **Location/Region** (should be `uksouth`)

### Step 3: Add to .env
```env
AZURE_SPEECH_KEY="your-speech-key-here"
AZURE_SPEECH_REGION="uksouth"
```

### Step 4: Add to Azure App Service
In Azure Portal → App Service → Environment variables, add:
- `AZURE_SPEECH_KEY`
- `AZURE_SPEECH_REGION`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

---

## 3. Pricing Estimate (5 students testing)

### Azure Speech Services
- **Free Tier**: 5 hours audio/month
- **Paid**: $1/hour after free tier
- **Your usage**: ~10 minutes total = **FREE**

### Telegram Bot
- **Cost**: FREE (unlimited messages)

### Total Additional Cost: $0

---

## 4. Features Added

✅ **Empathetic Crisis Response** - Softer, more caring language
✅ **Telegram Alerts** - Support team notified instantly via Telegram
✅ **Text-to-Speech** - Click speaker icon to hear AI responses (Azure TTS)
✅ **Speech-to-Text** - Already working with browser API (free)

---

## 5. Testing

1. **Test Crisis Detection**: Send "I am depressed"
   - Should see empathetic response
   - Should receive Telegram alert

2. **Test TTS**: Click the speaker icon on any AI response
   - Should hear natural British English voice

3. **Test STT**: Click microphone and speak
   - Should transcribe your speech to text

---

## Need Help?

- Telegram Bot API: https://core.telegram.org/bots
- Azure Speech Docs: https://learn.microsoft.com/en-us/azure/ai-services/speech-service/
