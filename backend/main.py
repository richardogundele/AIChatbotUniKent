import os
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

load_dotenv()

# Startup validation — fail fast with a clear message instead of a cryptic SDK error
REQUIRED_ENV_VARS = [
    "AZURE_OPENAI_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_VERSION",
    "AZURE_GPT_DEPLOYMENT",
    "AZURE_EMBEDDING_DEPLOYMENT",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_INDEX",
    "AZURE_SEARCH_KEY",
]
missing_vars = [v for v in REQUIRED_ENV_VARS if not os.getenv(v)]
if missing_vars:
    raise RuntimeError(f"Missing required environment variables: {', '.join(missing_vars)}")

app = FastAPI(title="ChariotAI - UoK Student Assistant")

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
    allow_origins=origins,  # Never allow "*" with credentials
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

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    handoff_required: bool = False

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

# Initialize Azure Cloud Clients
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY")
)

llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_GPT_DEPLOYMENT"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    temperature=0.1
)

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
)

@app.get("/health")
def health_check():
    """Simple endpoint to prove the server is running."""
    return {"status": "healthy", "service": "ChariotAI"}

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    user_message = request.message.lower()
    
    # 1. Execute Safety Guardrail with Handoff
    if any(keyword in user_message for keyword in CRISIS_KEYWORDS):
        return ChatResponse(
            answer="**If you are in immediate distress, please contact the University of Kent Student Support & Wellbeing (SSW) emergency line at 01227 823333, or call the Samaritans free 24/7 on 116 123.** Your wellbeing is the most important thing.",
            sources=["https://www.kent.ac.uk/student-support"],
            handoff_required=True
        )
    
    try:
        # 2. Embed the student's question into vectors
        question_vector = embeddings.embed_query(request.message)
        
        # 3. Retrieve matching institutional knowledge from Azure AI Search
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
        
        response = llm.invoke(prompt)
        
        return ChatResponse(
            answer=response.content,
            sources=list(sources_set),
            handoff_required=False
        )
        
    except Exception as e:
        print(f"Error in chat: {e}")
        raise HTTPException(status_code=503, detail="ChariotAI engine is currently unavailable.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
