import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

load_dotenv()

app = FastAPI(title="ChariotAI - UoK Student Assistant")

# CORS setup (Robust handling for production + Fallbacks)
raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

# Hard-coded Golden Key Fallbacks (Ensures demo always works)
golden_origins = [
    "https://chariotai.org",
    "https://www.chariotai.org",
    "http://localhost:5173",
    "https://delightful-coast-0e2e5d103.6.azurestaticapps.net"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set(origins + golden_origins)), # Merge and de-duplicate
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import List

class MessageHistory(BaseModel):
    role: str
    text: str

class ChatRequest(BaseModel):
    message: str
    history: List[MessageHistory] = []

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    handoff_required: bool = False

# 🛡️ SAFETY GUARDRAIL: Crisis keywords that completely bypass the AI
CRISIS_KEYWORDS = ["suicide", "depressed", "overwhelmed", "self-harm", "hurt myself", "crisis", "samaritans"]

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
def chat_endpoint(request: ChatRequest):
    import time
    start_time = time.time()
    
    user_message = request.message.lower()
    print(f"[{time.strftime('%H:%M:%S')}] Received message: {request.message[:50]}...")
    
    # 1. Execute Safety Guardrail with Handoff
    if any(keyword in user_message for keyword in CRISIS_KEYWORDS):
        return ChatResponse(
            answer="**If you are in immediate distress, please contact the University of Kent Student Support & Wellbeing (SSW) emergency line at 01227 823333, or call the Samaritans free 24/7 on 116 123.** Your wellbeing is the most important thing.",
            sources=["https://www.kent.ac.uk/student-support"],
            handoff_required=True
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
