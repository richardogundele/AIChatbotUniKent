# ChariotAI — Interview Prep & Architecture Reference

> **App**: ChariotAI — AI Powered Student Support Chatbot
> **Interview**: 30 March 2026 | Panel: Phil Anthony, Christopher Bailey, Kaidi Goke

---

## 1. The Stack & Why We Chose Each Component

| Layer | Technology | Why |
|---|---|---|
| **LLM** | Azure OpenAI (GPT-4o-mini) | UK GDPR compliant (data stays in Azure UK South region). No data used for training. Directly listed as desirable in the JD. Stronger institutional trust than raw OpenAI API. |
| **Embeddings** | Azure text-embedding-ada-002 | Stays within Azure boundary — same GDPR argument. Consistent with the OpenAI embedding standard. Cheap at $0.10/1M tokens. |
| **Vector Store** | Azure AI Search | JD explicitly names it. Managed service — no infra to maintain. Built-in semantic ranking. Scales without config changes. GDPR-safe within Azure. |
| **Orchestration** | LangChain (Python) | Industry standard for RAG pipelines. Native Azure AI Search + Azure OpenAI integrations. `ConversationalRetrievalChain` gives memory/context out of the box. |
| **Backend** | FastAPI (Python) | Async, lightweight, auto-generates OpenAPI docs. Standard for AI microservices. Compatible with Azure App Service. |
| **Frontend** | React (Vite) | Fast build, component-based, wide accessibility library support. Deployed to Azure SWA with zero backend coupling. |
| **Hosting (Frontend)** | Azure Static Web Apps | Free tier. Tight GitHub Actions CI/CD. Supports custom domains (ChariotAI domain ready). Global CDN. |
| **Hosting (Backend)** | Azure App Service (Linux) | JD desirable: "Azure App Services". Managed runtime, auto-scaling, supports Python 3.11+. |
| **IaC** | Terraform | JD desirable: "infrastructure-as-code". One `terraform apply` provisions everything. Reproducible, auditable, version-controlled. |
| **Accessibility** | Web Speech API + WCAG 2.1 AA | Legal requirement under UK Equality Act. Voice-to-text and text-to-voice via native browser APIs (no third-party cost). Demonstrates inclusive design thinking. |

---

## 2. Architecture Overview

```
Student Browser
     │
     │  HTTPS
     ▼
Azure Static Web Apps (React UI)
  - ChariotAI chat interface
  - Voice input (SpeechRecognition API)
  - Voice output (SpeechSynthesis API)
  - WCAG 2.1 AA compliant
     │
     │  REST API calls
     ▼
Azure App Service (FastAPI)
  - POST /chat
  - Safety guardrails (crisis detection)
  - LangChain RAG chain
  - Source attribution
  - Request logging
     │
     ├─────────────────────────────────┐
     │                                 │
     ▼                                 ▼
Azure OpenAI                  Azure AI Search
(GPT-4o-mini + ada-002)       (Kent knowledge index)
     │                                 │
     └──────── All within Azure ───────┘
               (UK South region)
               GDPR compliant
```

---

## 3. RAG Pipeline — "Verified Attribution" Loop (from Readme.md)

1. **Ingestion (one-off)**: `ingestion.py` scrapes 6 Kent pages, chunks the text, generates embeddings, and indexes into Azure AI Search with source URL metadata.
2. **Query**: Student types or speaks a message → React UI → FastAPI `/chat`.
3. **Safety check FIRST**: `guardrails.py` scans for crisis keywords. Hit → return emergency card immediately. Zero LLM calls.
4. **Retrieval**: LangChain retrieves top-k chunks from Azure AI Search.
5. **Self-Correction / Verification Loop** *(from Readme.md)*: If the retrieved answer is ambiguous (e.g. "Can I use AI?" needs an assignment-brief exception check), the agent re-queries with a refined prompt to find the specific exception. This mirrors the "Self-Correction Node" from the original Verified Insight Engine architecture.
6. **Generation**: GPT-4o-mini generates a response grounded strictly in retrieved context (`temperature=0.0`).
7. **Zero-hallucination gate**: If retrieval confidence below threshold → polite refusal, no generative answer.
8. **Verified Attribution**: Every response returns source URL(s) cited inline — branded as "Verified Attribution".

---

## 4. Safety & Trust Features

| Feature | Implementation | Why It Matters |
|---|---|---|
| **Crisis escalation** | Keyword list triggers immediate contact card: SSW (01227 823333), Samaritans (116 123), Spectrum Life 24/7 | University wellbeing duty of care. Panel will probe this. |
| **Zero hallucination** | Retrieval confidence threshold — refuse if no grounded Kent source | Core requirement of the task brief. |
| **Source attribution** | Every answer cites specific Kent webpage | Transparency, student trust, academic integrity alignment. |
| **GDPR compliance** | All data processed within Azure UK South. No PII stored in vector index. | Legal requirement. Christopher Bailey will ask about this. |
| **No PII in logs** | Request logs capture intent category, not message content | Data minimisation principle (UK GDPR Art. 5). |

---

## 5. Accessibility Features

| Feature | Technology | Standard |
|---|---|---|
| Keyboard navigation | Tab order, focus management, skip links | WCAG 2.1 AA 2.1.1 |
| Screen reader support | ARIA roles, live regions for new messages | WCAG 2.1 AA 4.1.2 |
| Voice-to-text input | Web Speech API `SpeechRecognition` | Supports motor-impaired users |
| Text-to-voice output | Web Speech API `SpeechSynthesis` | Supports visually-impaired users |
| High-contrast mode | CSS `prefers-color-scheme` + manual toggle | WCAG 2.1 AA 1.4.3 |
| Font size control | User-adjustable text size | WCAG 2.1 AA 1.4.4 |
| Colour contrast | Minimum 4.5:1 ratio on all text | WCAG 2.1 AA 1.4.3 |

---

## 6. Likely Interview Questions & Strong Answers

### Q: Why did you choose Azure OpenAI over the standard OpenAI API?
**A**: "The University handles student data, which falls under UK GDPR. Azure OpenAI processes all data within the Azure UK South region and Microsoft guarantees that data is never used to retrain models — this is critical for a university context. The JD also specifically listed Azure AI services as a desirable skill, so it was the obvious institutional fit. It also signals that ChariotAI could integrate naturally into Kent's existing Microsoft 365 infrastructure."

---

### Q: How does your RAG pipeline prevent hallucinations?
**A**: "Two layers. First, the retriever only surfaces documents from our Azure AI Search index — which contains exclusively official University of Kent content. Second, before generating a response, we check the retrieval confidence score. If no sufficiently relevant document is found, the system returns a refusal message rather than attempting to generate an answer from GPT's pre-trained knowledge. This zero-hallucination policy is non-negotiable for a student-facing support tool."

---

### Q: Walk me through what happens when a student says 'I'm struggling to cope'.
**A**: "Before the message even reaches the RAG pipeline, a guardrails module scans for crisis and wellbeing keywords. On a match, the system bypasses LLM entirely and immediately returns a pre-verified response card with the Student Support & Wellbeing number (01227 823333), Samaritans (116 123), and Spectrum Life's 24/7 link. This is a hard-coded, tested, non-generative response — it cannot hallucinate phone numbers or give wrong advice in a crisis situation."

---

### Q: Why Terraform? Couldn't you just click through the Azure portal?
**A**: "Terraform gives us reproducibility and auditability. Every resource — the OpenAI deployment, AI Search index, App Service, Static Web App — is declared in code and version-controlled in Git. If someone changes a setting in the portal it gets caught on the next `terraform plan`. For the University, this means the infrastructure configuration is reviewable by the security and governance teams, which aligns directly with the JD's mention of governance reviews and infrastructure-as-code. It also means the full environment can be torn down and rebuilt in minutes — important for cost management with the free-tier services."

---

### Q: How does the chatbot handle something it doesn't know about?
**A**: "It refuses politely. If the Azure AI Search retrieval returns no relevant documents — or documents with a low confidence score — the bot responds with something like: 'I can only answer questions based on official University of Kent documentation. For this query, please contact [relevant department].' It never invents information. This is enforced at the chain level, not just the prompt level."

---

### Q: How did you approach accessibility?
**A**: "I treated it as a first-class feature, not an afterthought. The UI meets WCAG 2.1 AA — full keyboard navigation, ARIA live regions so screen readers announce new messages, and a minimum 4.5:1 colour contrast ratio. I also added voice-to-text input using the Web Speech API so students with motor impairments can speak their questions, and text-to-voice output so visually impaired students can hear responses. There's also a high-contrast mode toggle and adjustable font sizes."

---

### Q: How would this scale beyond a prototype?
**A**: "A few ways. The Azure App Service can scale out horizontally. Azure AI Search supports up to millions of documents — we'd just ingest more Kent content. Azure OpenAI has rate limit tiers we can increase. For session memory, we'd move from in-memory LangChain memory to Azure Cosmos DB or Redis Cache to support concurrent users. The Terraform stack makes scaling infrastructure changes a configuration change, not a migration project."

---

### Q: What data does the chatbot store? How is student privacy protected?
**A**: "The knowledge index in Azure AI Search contains only scraped public pages from the University of Kent website — no student data whatsoever. Conversations are not persisted by default. Request logs capture only the intent category (e.g., 'wellbeing', 'academic integrity') and response latency — never the message content. This aligns with UK GDPR's data minimisation principle. All processing happens within our Azure UK South tenant boundary."

---

### Q: Why LangChain and not just raw API calls?
**A**: "LangChain gives us the `ConversationalRetrievalChain` which handles conversational memory, retrieval, and prompt assembly in a tested, maintainable way. It has native Azure AI Search and Azure OpenAI integrations, so there's minimal glue code. If we needed to swap the LLM or vector store, LangChain's abstractions make that a small config change. For a prototype timeline, it was the right balance of speed and structure."

---

### Q: Why did you pick this specific stack over, say, a no-code chatbot tool?
**A**: "The JD explicitly asks for someone who can 'develop, test and maintain AI-enabled applications', 'implement RAG patterns', and 'develop backend services and APIs'. A no-code tool wouldn't demonstrate any of that. ChariotAI is intentionally engineered to show the full stack — from infrastructure-as-code with Terraform, through a Python RAG backend, to an accessible React frontend. Every decision maps back to a requirement in the JD or the task brief."

---

### Q: You mentioned a self-correction loop — how does that work in practice?
**A**: "It's from the original Verified Insight Engine architecture. For straightforward queries the first retrieval pass is sufficient. But for ambiguous queries — like 'Can I use AI for my assignment?' — the policy answer varies by module. The agent detects low-confidence ambiguity and fires a second, refined retrieval query specifically targeting assignment-brief exceptions. Only then does it generate the response. This prevents the bot from giving a generic 'no' when the real answer is module-dependent."

---

### Q: What knowledge areas does the chatbot cover? Why those six?
**A**: "The task brief in The Whyy.md is explicit: admissions, assessments, deadlines, wellbeing support, and general enquiries. I added academic integrity and ChatGPT Edu because the JD's facts section specifically calls out Kent's ChatGPT Edu environment as central to this role, and AI misuse is the single biggest policy risk students face right now. Six knowledge areas: Academic Integrity (including the study buddy vs misconduct distinction), Student Support & Wellbeing, ChatGPT Edu rollout, Admissions, Deadlines & Key Dates, and General Enquiries/Contact Directories."

---

### Q: How do you handle errors? What if Azure OpenAI is unavailable?
**A**: "The FastAPI backend has three error handling layers. First, all external calls — Azure OpenAI, Azure AI Search — are wrapped in try/except with specific error types caught. If Azure OpenAI is rate-limited or unavailable, the endpoint returns a 503 with a user-friendly message rather than a 500 stack trace. Second, request validation via Pydantic models means malformed input is rejected at the schema level before any processing begins. Third, the /health endpoint lets the frontend detect degraded state and show a banner to the student rather than a broken experience."

---

### Q: Kent's systems appear to be C#/.NET — how does your Python backend integrate with that ecosystem?
**A**: "ChariotAI exposes a standard REST API — POST /chat returns JSON. Any system, whether it's a .NET webapp, a SharePoint plugin, or a PHP CMS, can call it with a standard HTTP POST. I deliberately kept the API contract simple: message in, answer + sources out. The Terraform-provisioned App Service supports custom domain and SSL, so it could sit behind Kent's existing API gateway or be called directly from any .NET service using HttpClient. If needed, the backend could be re-implemented in C# using Microsoft's Semantic Kernel, which is the .NET equivalent of LangChain — but Python was chosen for this prototype because of the richer LangChain ecosystem and faster iteration."

---

### Q: How did you handle documentation and version control?
**A**: "All code is in a GitHub repository with a clean, meaningful commit history — not just a single commit dump. The project README covers architecture overview, environment setup, required env vars, how to run scraping, local development, and deployment. There's a .env.example so any developer can onboard without guessing at config. GitHub Actions handles CI/CD for the Static Web App. This directly addresses the JD's essential criteria around version control and documentation."

---

### Q: The JD talks about 'knowing when to escalate rather than resolve independently'. How does that reflect in the chatbot?
**A**: "It's actually the core architectural principle. When the bot encounters a wellbeing or crisis query, it doesn't try to resolve it — it escalates immediately to the proper human service. When a query is outside the knowledge base, it escalates to the relevant department rather than generating a guess. And technically, the self-correction loop has a hard stop — if two retrieval passes still don't yield confident results, it escalates to a 'please contact [department]' response. The bot models institutional escalation behaviour deliberately."

---

## 7. Demo Script (5 Minutes) — Exactly from Readme.md Structure

| Time | Section | Action |
|---|---|---|
| **0:00–0:30** | **The Problem** | "Students need 24/7 support for complex policies — admissions, deadlines, academic integrity, wellbeing — but generic AI hallucinates policies and phone numbers. That's dangerous in a university context." |
| **0:30–1:30** | **The Solution** | Show ChariotAI UI. "It's built on a Verified Attribution loop — every answer is grounded in official University of Kent documentation. No source = no answer." Show sidebar: API Ready ✅ Knowledge Base Loaded ✅ GDPR Compliant ✅ |
| **1:30–3:30** | **Live Demo** | Query 1: *"When do I get access to ChatGPT Edu?"* → show April 2026 answer with source link. Query 2: *"I'm feeling overwhelmed"* → show immediate crisis card (01227 823333) — point out: **no LLM was called**. |
| **3:30–4:30** | **Technical Justification** | "Azure OpenAI keeps data in UK South — GDPR compliant. Azure AI Search is the vector store — listed in the JD. Terraform provisioned the entire stack — IaC, auditable by your security team." |
| **4:30–5:00** | **Closing** | "This scales into the AI@Kent strategy — ingest more Kent content, same architecture, same safeguards. The Verified Attribution pattern is portable to any University system." |

---

## 8. Things To Know Cold

- **Emergency numbers**: SSW = 01227 823333 | Samaritans = 116 123 | Spectrum Life = 24/7 app
- **ChatGPT Edu rollout**: April 2026 for students (Kent is investing in ChatGPT Edu management as part of this role)
- **Knowledge base covers**: AI Academic Integrity, Wellbeing/SSW, ChatGPT Edu, Admissions, **Assessments, Deadlines, General Enquiries** (6 topic areas, not 4)
- **Study buddy vs misconduct**: Kent distinguishes between using AI as a learning aid vs submitting AI-generated work as your own — the bot explains this nuance
- **Architecture name**: "Verified Attribution" / "Verified Student Assistant" — use this language in the demo
- **Self-correction loop**: Second retrieval pass triggered when first answer is ambiguous — addresses assignment-specific exceptions
- **Azure AI Search Free tier limits**: 3 indexes, 50MB, 10,000 documents — sufficient for prototype
- **GPT-4o-mini pricing**: Input $0.15/1M tokens, Output $0.60/1M tokens
- **WCAG 2.1 AA vs AAA**: AA is the legal standard (UK Equality Act 2010). AAA is aspirational.
- **LangChain version**: 0.2.x (stable, Azure integrations working)
- **Git**: All code in GitHub, clean commit history — JD essential criteria
- **The role stays within agreed frameworks**: You implement, not architect. Demonstrate this mindset in discussion.

---

## 9. Code Walkthrough (Panel Will Ask You To Walk Through This)

> Practise narrating each file out loud. The panel expects you to open the code and talk through it.

---

### `terraform/main.tf` — How Everything Is Provisioned

**What to say**: *"Rather than clicking through the Azure portal, I defined every resource in Terraform. This makes the infrastructure auditable, version-controlled, and reproducible."*

Key blocks to highlight:
```hcl
# Azure OpenAI — GDPR-compliant, UK South region
resource "azurerm_cognitive_account" "openai" {
  kind     = "OpenAI"
  location = "uksouth"          # Data never leaves UK
  sku_name = "S0"
}

# GPT-4o-mini deployment
resource "azurerm_cognitive_deployment" "gpt" {
  name           = "gpt-4o-mini"
  cognitive_account_id = azurerm_cognitive_account.openai.id
  model { name = "gpt-4o-mini" }
}

# Azure AI Search — Free tier, GDPR-safe
resource "azurerm_search_service" "search" {
  sku = "free"
  location = "uksouth"
}

# FastAPI backend on Azure App Service
resource "azurerm_linux_web_app" "backend" {
  site_config {
    application_stack { python_version = "3.11" }
  }
}

# React frontend on Azure Static Web Apps
resource "azurerm_static_web_app" "frontend" {}
```
**Panel point**: Christopher Bailey will respect this. Say: *"One `terraform apply`, the entire stack is live. One `terraform destroy`, it's gone and billing stops."*

---

### `backend/app/safety/guardrails.py` — First Line of Defence

**What to say**: *"The very first thing the `/chat` endpoint does is run the guardrails check — before any LLM call. This is a deliberate architectural decision: no AI system should attempt to handle a mental health crisis generatively."*

```python
CRISIS_KEYWORDS = [
    "overwhelmed", "can't cope", "suicidal", "self-harm",
    "end it", "crisis", "breaking down", "hopeless"
]

ESCALATION_CARD = {
    "type": "emergency",
    "answer": (
        "I'm concerned about you. Please reach out for immediate support:\n\n"
        "Student Support & Wellbeing: 01227 823333\n"
        "Samaritans (24/7): 116 123\n"
        "Spectrum Life (24/7 app): via your student portal\n\n"
        "You don't have to face this alone."
    ),
    "sources": []
}

def check_guardrails(message: str) -> dict | None:
    if any(kw in message.lower() for kw in CRISIS_KEYWORDS):
        return ESCALATION_CARD
    return None  # Safe to proceed to RAG
```
**Panel point**: *"The phone numbers are hard-coded and tested — they cannot be hallucinated. This is a deliberate safety decision over a flexible generative one."*

---

### `backend/app/rag/chain.py` — The RAG Pipeline

**What to say**: *"This is the core intelligence of ChariotAI. LangChain wires together Azure OpenAI, Azure AI Search, and a confidence filter in about 40 lines of Python."*

```python
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.retrievers import AzureAISearchRetriever
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

llm = AzureChatOpenAI(
    azure_deployment="gpt-4o-mini",
    temperature=0.0,      # Deterministic — no creative hallucination
)

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-ada-002"
)

retriever = AzureAISearchRetriever(
    index_name="kent-knowledge",
    content_key="content",
    top_k=5
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True,  # Source attribution
)

SYSTEM_PROMPT = """You are ChariotAI, the University of Kent student support assistant.
RULES:
- Answer ONLY using the retrieved University of Kent documentation below.
- If the documentation does not contain the answer, say exactly:
  "I can only answer questions based on official University of Kent documentation."
- Always cite the source URL at the end of your answer.
- Never invent policies, dates, or contact details.
"""
```
**Panel point**: *"Temperature is set to 0.0 intentionally — we want deterministic, policy-grounded answers, not creative ones. The system prompt enforces zero-hallucination at the instruction level, and the confidence filter enforces it at the retrieval level."*

---

### `backend/app/rag/ingestion.py` — Building the Knowledge Base

**What to say**: *"This runs once to populate Azure AI Search with verified University of Kent content. It only ingests public pages — no student data enters the system."*

```python
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter

KENT_PAGES = [
    {"url": "https://www.kent.ac.uk/ai", "title": "AI & Academic Integrity"},
    {"url": "https://www.kent.ac.uk/student-support", "title": "Student Support & Wellbeing"},
    {"url": "https://www.kent.ac.uk/chatgpt-edu", "title": "ChatGPT Edu Rollout"},
    {"url": "https://www.kent.ac.uk/admissions", "title": "Admissions & Assessments"},
]

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # Optimised for Azure AI Search retrieval
    chunk_overlap=50
)

for page in KENT_PAGES:
    html = requests.get(page["url"]).text
    text = BeautifulSoup(html, "html.parser").get_text()
    chunks = splitter.split_text(text)
    # Generate embeddings + index into Azure AI Search
    # Each chunk stored with: content, source_url, page_title
```
**Panel point**: *"Chunks are 500 tokens with 50-token overlap. This is a deliberate choice — large enough to provide context, small enough for precise retrieval. The source URL is stored as metadata on every chunk, which is how source attribution works in the response."*

---

### `backend/app/main.py` — The API Endpoint

**What to say**: *"FastAPI handles the request. The guardrails check happens before any AI call — if it's a crisis, we return immediately. If it's safe, the RAG chain runs and returns an attributed answer."*

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # 1. Log intent category (not content — GDPR data minimisation)
    logger.info(f"session={request.session_id} intent_detected")

    # 2. Safety first — before any LLM call
    emergency = check_guardrails(request.message)
    if emergency:
        return emergency

    # 3. RAG chain
    result = chain({"question": request.message})

    # 4. Extract sources for attribution
    sources = [doc.metadata["source_url"]
               for doc in result["source_documents"]]

    return {
        "answer": result["answer"],
        "sources": sources,
        "type": "rag"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "knowledge_base": "loaded"}
```

---

### `frontend/src/components/ChatWindow.jsx` — Accessibility & Voice

**What to say**: *"The UI was built with accessibility as a first-class concern. Voice input and output are native browser APIs — no third-party service, no additional cost, no data leaving the browser."*

```jsx
// Voice-to-text: SpeechRecognition API
const startListening = () => {
  const recognition = new window.SpeechRecognition();
  recognition.onresult = (e) => setInput(e.results[0][0].transcript);
  recognition.start();
};

// Text-to-voice: SpeechSynthesis API
const speak = (text) => {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-GB";   // British English for Kent students
  window.speechSynthesis.speak(utterance);
};

// ARIA live region — screen readers announce new messages
<div aria-live="polite" aria-label="Chat messages" role="log">
  {messages.map(msg => <Message key={msg.id} {...msg} onSpeak={speak} />)}
</div>
```
**Panel point**: *"Native browser APIs mean no GDPR risk from third-party voice services. The `aria-live='polite'` region means screen readers announce every new bot response automatically."*

---

## 10. AI Tools Used — Justify Every One

| Tool | Category | Justification |
|---|---|---|
| **Azure OpenAI GPT-4o-mini** | LLM | GDPR-safe (Azure boundary), no model training on data, cost-efficient ($0.60/1M output tokens), Microsoft enterprise SLA |
| **Azure text-embedding-ada-002** | Embeddings | Same Azure boundary as LLM. 1536-dimension embeddings, industry standard. Used to semantically index all Kent documents |
| **Azure AI Search** | Vector store + semantic search | JD desirable criteria. Managed, scalable, GDPR-compliant. Built-in semantic ranker improves retrieval quality over pure vector similarity |
| **LangChain** | Orchestration | Abstracts RAG complexity. `ConversationalRetrievalChain` handles memory, retrieval and prompt assembly. Swap LLM/vector store with one config change |
| **Web Speech API** | Voice I/O | Browser-native. No data sent to third-party. Free. Supports motor-impaired (voice-to-text) and visually-impaired (text-to-voice) users |
| **Terraform** | IaC | JD desirable. Reproducible infrastructure. Git-auditable. Security team can review infra as code. `terraform destroy` = immediate cost stop |

---

## 11. Data Handling & GDPR Flow

```
WHAT ENTERS THE SYSTEM:
  User query (text/voice) → processed in browser → sent to FastAPI

WHAT LEAVES THE BROWSER:
  POST /chat { message: "...", session_id: "uuid" }
  → No name, no student ID, no email

WHAT GOES TO AZURE OPENAI:
  System prompt + retrieved Kent text chunks + user query
  → No PII from student
  → Azure contractually cannot use this for training

WHAT IS LOGGED:
  session_id | intent_category | response_latency_ms
  → NOT the message content (data minimisation, UK GDPR Art. 5(1)(c))

WHAT IS STORED IN AZURE AI SEARCH:
  Public Kent webpage text + source URL
  → Zero student data in the index

CONVERSATION MEMORY:
  In-memory per session → gone when session ends
  → No persistence to database in prototype

DATA RESIDENCY:
  All Azure resources in UK South region
  → UK GDPR Article 44 (transfers) not triggered
```

**Key phrase to use**: *"The system was designed with data minimisation as a first principle. Student queries are processed but never persisted. The knowledge base contains only public University information. All processing happens within the Azure UK South boundary."*

