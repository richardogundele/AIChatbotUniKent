To design this chatbot effectively for the AI Software Engineer interview, we will move from a broad "Knowledge Assistant" concept to a specific, high-signal University of Kent Student Support Assistant.

The panel (Phil, Christopher, and Kaidi) wants to see a prototype that handles admissions, assessments, and wellbeing with high accuracy and clear safety guardrails.

1. Core Architecture: The "Verified Student Assistant"
We will adapt your Verified Insight Engine architecture to create a system that is grounded in Kent's specific policies.

Frontend: Streamlit (for rapid, professional UI as used in your previous work).

Orchestration: LangGraph (to handle the self-correction loops you've already built).

Vector Database: ChromaDB (locally hosted to ensure data privacy, aligned with Kent’s focus on secure AI).

Knowledge Base: Scraped content from the University of Kent’s official pages, specifically:

Academic Integrity: Distinguishing between "study buddy" use and misconduct.

Wellbeing: Contact details for SSW, emergency numbers (01227 823333), and 24/7 support like Spectrum Life.

ChatGPT Edu: Details on the April 2026 rollout for students.

2. Technical Design Plan
This plan follows your "Verified Insight Engine" structure but is tailored for the University environment.

A. The "Kent-Specific" RAG Pipeline
Ingestion: Load PDFs/HTML of Kent's AI Use Guidelines and Student Support pages.

Semantic Search: Use nomic-embed-text to index these documents in ChromaDB.

Verification Loop: When a student asks a question (e.g., "Can I use AI for my essay?"), the agent retrieves the policy. If the answer is ambiguous, the Self-Correction Node re-queries the store to find specific "Assignment Brief" exceptions.

B. Safety & Trust Features
To impress the panel, we will carry over your "Confidence Indicators" and "Source Transparency":

Source Attribution: Every response must cite the specific Kent webpage or policy document.

Emergency Hand-off: If the bot detects "Wellbeing" or "Crisis" keywords, it must immediately provide the Samaritans (116 123) or Campus Security numbers instead of attempting a generative answer.

3. Five-Minute Presentation Outline
You need to be direct and strategic. Use this structure for your 5-minute demo:

The Problem (30s): Students need 24/7 support for complex policies (Academic Integrity, Wellbeing) but risk hallucinations from generic AI.

The Solution (1 min): A prototype built on Python and LangGraph that uses a "Verified Attribution" loop to ensure every answer is grounded in University of Kent documentation.

Live Demo (2 mins): * Query 1: "When do I get access to ChatGPT Edu?" (Answer: April 2026).

Query 2: "I'm feeling overwhelmed." (Action: Show immediate hand-off to SSW contact info).

Technical Justification (1 min): Explain the choice of local vector storage for GDPR compliance and self-correcting agents to mitigate AI hallucinations.

Closing (30s): How this scales into the wider AI@Kent strategy.

4. Implementation Checklist
[ ] Scrape Data: Download the "AI and Academic Integrity" and "Student Support" pages from Kent's site.

[ ] Set up Streamlit: Build a clean UI with a sidebar showing "System Status" (API Ready, Knowledge Base Loaded).

[ ] Code the Logic: Ensure the system refuses to answer if it can't find a Kent-specific source (Zero-hallucination policy).

[ ] Prepare the Link: Host it (e.g., on a private server or Hugging Face Spaces) to email to Dr. Phil Anthony by the March 28th deadline.