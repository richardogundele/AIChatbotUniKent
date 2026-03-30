# 📋 Interview Panel Requirements
> **Format**: Presentation & Chatbot Demo
> **Duration**: 5 minutes maximum
> **Title**: Chatbot Demo
> **Details**: Demonstrate the chatbot, explain how it was designed and built, talk through the code and overall architecture, and justify key technical decisions (AI tools, data handling, safeguards).

# 🤖 ChariotAI - Interview Preparation Guide

This guide is your primary resource for a 5-minute project pitch and technical deep-dive during your interview. It focuses on demonstrating the seniority required for an **AI Solution Architect** or **Full Stack Developer** role.

---

## 🚀 The 60-Second "Elevator Pitch"
*(Ideal for: "Tell me about your most proud project.")*

"I built **ChariotAI**, an enterprise-ready, RAG-powered chatbot for the University of Kent. It provides 24/7 student support by grounding its answers in official university documents using **Azure OpenAI** and **Azure AI Search**. What sets it apart is its **Crisis Handoff System**—I implemented a safety guardrail that detects mental health keywords and immediately connects the student to a **live human agent via a Telegram bridge**, ensuring zero hallucination in critical scenarios. The entire ecosystem is deployed using **Terraform (IaC)** and **GitHub Actions**, making it a fully automated, cloud-native solution."

---

## 🏗️ Technical Architecture Breakdown
Use these details to explain *how* it works when they ask about your stack.

| **Layer** | **Technology** | **Why You Chose It** |
| :--- | :--- | :--- |
| **Frontend** | React + Vite | Fast startup, smooth UX with glassmorphism, and built-in **Speech-to-Text**. |
| **Backend** | FastAPI (Python) | High-performance, asynchronous endpoints required for multi-step AI inference tasks. |
| **AI Engine** | LangChain | For managing conversation memory and the RAG (Retrieval-Augmented Generation) loop. |
| **Search Engine** | Azure AI Search | Hybrid search (vector + keyword) ensures extremely high accuracy for institutional docs. |
| **LLM** | GPT-4o-mini | The best balance of **latency and cost** for high-volume student queries. |
| **DevOps** | Terraform + GH Actions | Ensures the infrastructure is reproducible and deployments are "push-to-prod" simple. |

---

## 🛡️ Key Innovation: The "Crisis Handoff"
*(Explain this to show your focus on Safety & Ethics)*

- **Detection**: A list of high-risk keywords (e.g., "crisis," "suicidal," "self-harm") is tracked in the backend.
- **Bypass**: When triggered, the AI is **completely bypassed** to prevent unpredictable generated responses.
- **Telegram Bridge**: I integrated a `telegram_bridge.py` service. It notifies a support team bot on Telegram, allowing a real human to reply directly through the bot, which then appears in the student's browser via a **polling mechanism**.

---

## 💡 Top 10 Technical Mock Q&A

**1. Why use RAG (Retrieval-Augmented Generation) instead of fine-tuning?**
> "Fine-tuning is expensive and the model starts losing information as soon as university rules change. RAG allows us to "ground" the model in the latest PDF/HTML documents from the Kent website, ensuring 100% accuracy and easy updates without retraining."

**2. How did you handle hallucinations in the chatbot?**
> "I set the `temperature` to `0.0` for maximum consistency. I also implemented a **Strict Attribution System** where the prompt directs the LLM to only use provided context. If the answer isn't there, it must explicitly say so."

**3. Tell me about the Infrastructure-as-Code (IaC) part.**
> "I used **Terraform** to provision the Azure resource group, AI Search services, and App Services. This means I can tear down and rebuild the entire production environment across regions in minutes with one command."

**4. How did you optimize for latency?**
> "I added logging to track each stage: Embedding took ~0.2s, Search ~0.5s, and LLM ~1.5s. I also chose **GPT-4o-mini** on Azure, which has significantly lower latency than the standard GPT-4 models."

**5. How does the speech-to-text work?**
> "It uses the native browser `webkitSpeechRecognition` API for instant feedback, and I built a custom `/tts` endpoint on the backend using **Azure Speech Services** to read responses back smoothly."

**6. What was your biggest technical challenge?**
> "Handling **CORS** in a split frontend/backend architecture on Azure. I solved it with a robust FastAPI middleware that handles dynamic environment origins and a 'Golden Key' fallback system for the production URLs."

**7. How do you handle conversation memory?**
> "In the backend, I extract the last 6 messages from the request payload to provide session context, ensuring the LLM remembers previous questions within a single chat window."

**8. Why Azure over AWS for this specific project?**
> "Azure's native integration of **Azure OpenAI** and **Azure AI Search** is industry-leading for RAG. The ability to link a search index directly to a vector store with 'Integrated Vectorization' saved weeks of dev time."

**9. How do you ensure the chatbot is accessible?**
> "I implemented high-contrast UI themes and **Voice Input/Output** as core features, making sure students with visual or motor impairments can still access support."

**10. How would you scale this to 100,000 students?**
> "I'd implement **Redis caching** for common questions and upgrade the Azure Search tier to support more 'Replicas' for parallel querying. The FastAPI backend is already async, so it's ready for high concurrency."

---

## 📅 The 5-Minute Presentation Script

1.  **Minute 1: Problem Statement** (Students struggle to find info in 1,000s of pages of rules; support teams are overwhelmed).
2.  **Minute 2: Solution Architecture** (React front, FastAPI back, Azure AI Search for 'Kent Brain').
3.  **Minute 3: Live Feature Showcase** (Voice search, Sources/Citations, and the Crisis Guardrail).
4.  **Minute 4: DevOps & Scalability** (Terraform, CI/CD, and the Cloud-Native approach).
5.  **Minute 5: Potential Growth** (Proactive outreach, integration with student IDs, and multi-language support).

---

> [!TIP]
> **Pro Tip**: If asked about the crisis handoff, mention that you chose **Telegram** because it has a great API and is free, which is perfect for a university budget!

> [!IMPORTANT]
> **Check your URLs**: Ensure your live demo links are ready and you've tested them 10 minutes before the interview to clear any Azure 'cold starts'.
