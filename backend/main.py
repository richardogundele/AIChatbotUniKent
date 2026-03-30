import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import asyncio
import time

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

# Telegram imports
try:
    from telegram import Bot
    from telegram_bridge import init_telegram_bot, create_crisis_session, send_student_message, get_agent_messages, is_session_active
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ Telegram bot not available - install python-telegram-bot")

# Speech services
try:
    from speech_service import text_to_speech
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("⚠️ Azure Speech not available")

load_dotenv()

# Print startup info for debugging
print("=" * 50)
print("ChariotAI Backend Starting...")
print(f"Python Path: {os.getcwd()}")
print(f"CORS Origins Configured: {os.getenv('CORS_ALLOWED_ORIGINS', 'None')}")
print("=" * 50)

app = FastAPI(title="ChariotAI - UoK Student Assistant")

# Initialize Telegram bot on startup
@app.on_event("startup")
async def startup_event():
    if TELEGRAM_AVAILABLE:
        await init_telegram_bot()
        print("✅ Telegram live chat bridge ready")

# CORS setup (Robust handling for production + Fallbacks)
raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
env_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

# Hard-coded Golden Key Fallbacks (always included regardless of env var)
golden_origins = [
    "https://chariotai.org",
    "https://www.chariotai.org",
    "http://localhost:5173",
    "https://delightful-coast-0e2e5d103.6.azurestaticapps.net"
]

# Merge both lists, preserving order and removing duplicates
origins = list(dict.fromkeys(golden_origins + env_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins + golden_origins)), # Merge and de-duplicate
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageHistory(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=2000)
    history: List[MessageHistory] = []
    session_id: Optional[str] = None  # For ongoing crisis sessions

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    handoff_required: bool = False
    session_id: Optional[str] = None  # For crisis sessions

# 🛡️ SAFETY GUARDRAIL: Crisis keywords that completely bypass the AI
CRISIS_KEYWORDS = [
    "suicide", "suicidal",
    "self-harm", "self harm", "hurt myself", "harm myself", "hurting myself",
    "depressed", "depression",
    "anxiety attack", "panic attack",
    "mental health crisis",
    "crisis",
    "samaritans",
]

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Your support team's chat ID

# Initialize Azure Cloud Clients
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_GPT_DEPLOYMENT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0.0 # Strict Zero-Creativity mode to prevent hallucination
)

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "ChariotAI API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    """Simple endpoint to prove the server is running."""
    try:
        # Test if environment variables are loaded
        missing_vars = []
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_GPT_DEPLOYMENT",
            "AZURE_EMBEDDING_DEPLOYMENT",
            "AZURE_SEARCH_ENDPOINT",
            "AZURE_SEARCH_KEY",
            "AZURE_SEARCH_INDEX"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        # Check for either AZURE_OPENAI_KEY or AZURE_OPENAI_API_KEY
        if not (os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_API_KEY")):
            missing_vars.append("AZURE_OPENAI_KEY or AZURE_OPENAI_API_KEY")
        
        if missing_vars:
            return {
                "status": "unhealthy",
                "service": "ChariotAI",
                "error": "Missing environment variables",
                "missing": missing_vars
            }
        
        return {"status": "healthy", "service": "ChariotAI", "config": "OK"}
    except Exception as e:
        return {"status": "error", "service": "ChariotAI", "error": str(e)}

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    start_time = time.time()
    
    user_message = request.message.lower()
    print(f"[{time.strftime('%H:%M:%S')}] Received message: {request.message[:50]}...")
    
    # Check if this is an ongoing crisis session
    if request.session_id and TELEGRAM_AVAILABLE:
        if is_session_active(request.session_id):
            # Forward student's message to agent on Telegram
            await send_student_message(request.session_id, request.message)
            
            # Get any new messages from agent
            agent_messages = get_agent_messages(request.session_id)
            
            if agent_messages:
                # Return agent's latest message
                latest_message = agent_messages[-1]
                return ChatResponse(
                    answer=f"**Support Agent:** {latest_message['text']}",
                    sources=[],
                    handoff_required=True,
                    session_id=request.session_id
                )
            else:
                # Agent hasn't replied yet
                return ChatResponse(
                    answer="Your message has been sent to our support team. They will respond shortly...",
                    sources=[],
                    handoff_required=True,
                    session_id=request.session_id
                )
    
    # 1. Execute Safety Guardrail with Handoff
    if any(keyword in user_message for keyword in CRISIS_KEYWORDS):
        # Create live chat session with agent
        session_id = None
        if TELEGRAM_AVAILABLE:
            session_id = await create_crisis_session(request.message)
        
        return ChatResponse(
            answer="""I can hear that you're going through a really difficult time right now, and I want you to know that your feelings are valid. 💙

**You don't have to face this alone.** I'm connecting you with a live support agent right now.

🆘 **While you wait, immediate support is available:**
• University of Kent Student Support & Wellbeing: **01227 823333**
• Samaritans (24/7, free): **116 123**
• Crisis Text Line: Text **SHOUT** to **85258**

📞 **A support agent has been notified** and will respond to you here shortly. Please stay on this chat.""",
            sources=["https://www.kent.ac.uk/student-support"],
            handoff_required=True,
            session_id=session_id
        )
    
    try:
        # 2. Embed the student's question into vectors
        embed_start = time.time()
        question_vector = embeddings.embed_query(request.message)
        print(f"  ⏱️ Embedding took: {time.time() - embed_start:.2f}s")
        
        # 3. Retrieve matching institutional knowledge from Azure AI Search
        search_start = time.time()
        vector_query = VectorizedQuery(
            vector=question_vector, 
            k_nearest_neighbors=3, 
            fields="content_vector"
        )
        
        results = search_client.search(
            search_text=request.message,
            vector_queries=[vector_query],
            select=["content", "source_url"],
            top=3
        )
        
        retrieved_docs = []
        sources_set = set()
        
        for result in results:
            retrieved_docs.append(f"Source ({result['source_url']}):\n{result['content']}")
            sources_set.add(result['source_url'])
        
        print(f"  ⏱️ Search took: {time.time() - search_start:.2f}s")
            
        context = "\n\n".join(retrieved_docs)
        
        # Compile previous conversation history
        history_str = ""
        for msg in request.history[-6:]: # Keep last 6 messages
            name = "Student" if msg.role == "human" else "ChariotAI"
            history_str += f"[{name}]: {msg.text}\n"
        
        # 4. Prompt the GPT model using the "Verified Attribution" system
        prompt = f"""
        You are ChariotAI, the official University of Kent Student Support Assistant.
        First, try to answer the student's question using the provided context from the Kent website below.
        If the exact answer is not in the context, you can use your general knowledge to provide a helpful, related answer. 
        When using general knowledge, kindly mention that they may want to check with the university directly for the most official details.
        
        CRITICAL FORMATTING INSTRUCTIONS:
        - Format your response beautifully and professionally using Markdown.
        - Use bolding (**) for key terms or emphasis.
        - Use bullet points (-) for any lists or step-by-step instructions.
        - Keep paragraphs short and properly spaced.
        
        Always answer in a friendly, supportive tone.
        
        Previous Conversation History:
        {history_str}
        
        Context from Knowledge Base:
        {context}
        
        Student's Latest Question: {request.message}
        """
        
        llm_start = time.time()
        response = llm.invoke(prompt)
        print(f"  ⏱️ LLM took: {time.time() - llm_start:.2f}s")
        print(f"✅ Total request time: {time.time() - start_time:.2f}s")
        
        return ChatResponse(
            answer=response.content,
            sources=list(sources_set),
            handoff_required=False
        )
        
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        print(f"  Total time before error: {time.time() - start_time:.2f}s")
        raise HTTPException(status_code=503, detail="ChariotAI engine is currently unavailable.")

@app.get("/poll_agent/{session_id}")
async def poll_agent_messages(session_id: str):
    """Poll for new messages from agent (for real-time updates)"""
    if not TELEGRAM_AVAILABLE:
        return {"messages": []}
    
    messages = get_agent_messages(session_id)
    return {"messages": messages, "active": is_session_active(session_id)}

@app.post("/tts")
async def text_to_speech_endpoint(text: str):
    """Convert text to speech audio"""
    if not SPEECH_AVAILABLE:
        raise HTTPException(status_code=501, detail="Speech services not available")
    
    try:
        audio_data = text_to_speech(text)
        return Response(content=audio_data, media_type="audio/wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
