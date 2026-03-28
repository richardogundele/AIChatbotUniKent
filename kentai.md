# ChariotAI — Interview Cheat Sheet & Architecture Defense

**Interview Date:** 30 March 2026
**Panel:** Phil Anthony (Head of AI), Christopher Bailey (Enterprise Architect), Kaidi Goke (Digital Enablement)

This document is your technical defense. You built an enterprise-tier architecture that explicitly answers every requirement in the Job Description.

---

## 1. Why Did You Build It This Way? (The Defense)

### A. The Multi-Region Azure Architecture
**What you did:** The Frontend and Backend compute run in **West Europe** (Amsterdam), while the Cognitive resources (Azure OpenAI & AI Search) run in **UK South** (London).
**Why you did it (SAY THIS):** *"When provisioning the infrastructure via Terraform, I encountered a strict zero-quota constraint for Linux App Services in the UK South datacenter due to Microsoft's regional capacity limits. Rather than failing the deployment, I architected a Multi-Region deployment. The compute layer sits in West Europe, communicating with the data layer in UK South. The geographic proximity yields a latency penalty of less than ~15ms—which is mathematically imperceptible to a chatbot user—while perfectly bypassing the regional quota blockade."*

### B. The Monorepo CI/CD (GitHub Actions)
**What you did:** You abandoned the Azure UI wizard and wrote two custom GitHub Actions YAML files.
**Why you did it:** *"Standard Azure UI deployments struggle with Monorepos. By writing precise GitHub Actions, I created a true CI/CD pipeline. If I edit a React component, only the Frontend workflow triggers. If I edit Python, only the Backend Azure App Service deploys. This is the enterprise standard for full-stack applications."*

### C. FastAPI over Django/Flask
**What you did:** You used FastAPI for the Python backend.
**Why you did it:** *"FastAPI is natively asynchronous, meaning it doesn't block the server while waiting 3 seconds for OpenAI to stream a response back. It also self-documents the API contract, making frontend integration flawless."*

---

## 2. Guarding Student Safety (The "Handoff" Logic)

**Phil Anthony (Head of AI) will ask about safety.**
*The Chatbot handles admissions, but what if a student types "I want to hurt myself"?*

**Your Answer:** *"An AI should never generatively respond to a life-threatening crisis. Before the message is even sent to LangChain, my `main.py` intercepts the request against a pre-defined list of crisis vectors. If tripped, the API immediately throws an `handoff_required: True` flag. The React frontend catches that flag and physically overrides the UI to display the Samaritans and SSW emergency phone numbers. It's a deterministic, hard-coded safety net."*

---

## 3. Code Walkthrough Prep

If they ask to see the code, guide them to these specific files:

### `terraform/main.tf`
Show them this file when they ask about **Cloud Infrastructure**.
Explain that every single resource (App Services, Static Web Apps, Custom Domains) is defined as code. This proves you know how to work at scale. You didn't just click buttons; you engineered it.

### `backend/main.py`
Show them this file when they ask about **RAG & LangChain**.
Point to lines where `embeddings.embed_query` connects to `AzureAI Search`. Explain that you force `temperature=0.0` on the `AzureChatOpenAI` model to entirely choke out hallucinations and force it to stick to the rulebook.

### `frontend/src/App.jsx`
Show them this when they ask about **UX and Integration**.
Point out that the React API call sends the `history: messages.slice(-6)` array. Explain that *this* is how the bot has conversational memory—the frontend passively reminds the backend of the last 6 things they talked about on every REST call.

---

## 4. Key Metrics to Drop in Conversation
* **GDPR Compliance:** Azure OpenAI ensures student data is never used to retrain Microsoft's models.
* **B1 Linux App Service:** Emphasize that you used `always_on = true` in Terraform so the FastAPI container doesn't go to sleep, ensuring instant replies for students.
* **Component Styling:** Emphasize the UI uses University of Kent brand colours (Navy & Gold) with CSS micro-animations to feel like a premium, modern Ivy League app, not a basic prototype.
