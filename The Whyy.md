# ARCHITECTURAL JUSTIFICATIONS (INTERVIEW DEFENSE)

> [!IMPORTANT]
> The panel (Phil, Christopher, Kaidi) will ask exactly *why* you didn't use other tools. Use these justifications to show you understand institutional constraints.

---

### 1. Why LangChain instead of LangGraph?
**Decision:** Standard `ConversationalRetrievalChain` from LangChain.
**Justification:** *"For a first-contact prototype, LangChain's mature RAG chain is far more stable and faster to implement than a custom LangGraph state machine. While LangGraph is great for complex 'loops', this project is a linear RAG execution. LangChain provides a robust, proven memory system natively without the overhead of manually managing node transitions."*

```python
# The choice for reliability over complexity
chain = ConversationalRetrievalChain.from_llm(
    llm=llm, 
    retriever=retriever, 
    memory=memory
)
```

---

### 2. Why Azure AI Search instead of FAISS or ChromaDB?
**Decision:** `azurerm_search_service` (Cloud-Native Vector Store).
**Justification:** *"Local vector stores like FAISS or ChromaDB are excellent for local research, but they don't scale or offer the 'Enterprise Grade' security the University requires. Azure AI Search integrates natively with Azure's RBAC security, offers a built-in **Semantic Ranker** (which yields higher accuracy than pure vector similarity), and is directly mentioned in the Job Description as a desirable skill."*

---

### 3. Why Azure Embeddings instead of OpenAI (Direct) or HuggingFace?
**Decision:** `text-embedding-ada-002` via Azure Cognitive Services.
**Justification:** *"Data privacy is paramount. By using Azure OpenAI Embeddings, the student's message never leaves the University's Azure UK South region. Utilizing HuggingFace or raw OpenAI APIs would trigger a Data Protection Impact Assessment (DPIA) for cross-border data transfer. This choice ensures GDPR compliance out of the box."*

---

### 4. Why GitHub Actions instead of Azure DevOps?
**Decision:** `.github/workflows/` (Independent CI/CD pipelines).
**Justification:** *"While Azure DevOps is a solid enterprise tool, GitHub Actions offers direct, native integration with the source repository. For a modern, high-velocity monorepo, GitHub Actions allows us to create surgical triggers—only building the frontend when the `/frontend` folder changes—without the complex overhead of DevOps pipelines. It proves the system is 'DevOps-ready' from Day 1."*

```yaml
# Precise Monorepo Triggering
on:
  push:
    paths: ['backend/**'] # Surgical precision
```

---

### 5. Why GPT-4o-mini?
**Decision:** `gpt-4o-mini` (Azure Deployment).
**Justification:** *"It is significantly faster and more cost-effective for a high-volume student support tool than GPT-4o, while maintaining nearly identical reasoning performance for policy retrieval. It keeps the project's token-spend low while providing instant response times."*

---

# EXECUTIVE SUMMARY: WHY CHARIOTAI PERFECTLY MATCHES THIS JD

| JD Requirement | How ChariotAI Proves You Have It |
|---|---|
| *"Develop backend services, APIs..."* | You wrote a high-performance **Python FastAPI** backend connected via REST to a React frontend. |
| *"Implement RAG patterns..."* | You built a LangChain RAG pipeline connected to **Azure AI Search** for semantic vector queries. |
| *"Familiarity with Azure services"* | You architected a massive **Multi-Region Azure environment** utilizing App Services, Static Web Apps, and Cognitive Services. |
| *"Experience working with version control"*| You utilized a **GitHub Monorepo** powered by custom **GitHub Actions CI/CD** YAML files. |
| *"Infrastructure-as-code"* | You strictly authored the entire architecture in **HashiCorp Terraform**. |
| *"Ensure work aligns with security... AI safeguards"* | You programmed a strict **Crisis Handoff Guardrail** that bypasses the generative LLM when a student is in distress. |

---

# ORIGINAL INVITATION & JOB DESCRIPTION

Dear Richard

We're pleased to invite you for an interview for the AI Software Engineer position.

*Action Required*: Book your interview

Please use this link to view dates and book your time slot, OR withdraw your application: https://jobs.kent.ac.uk/A/hFSXA_P_aImpZflpBvj!6Q--/
Interview details

When: 30th March 2026 - book your specific time via the link above.
Where: At our Canterbury campus. Please report to Registry reception at Registry reception**.
Duration: Approximately 45 minutes.

[ ... Continues as original ... ]
