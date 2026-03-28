import os, requests, uuid
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)
from azure.search.documents import SearchClient


# Load environment variables from .env
load_dotenv()

# The 6 specific URLs required for the ChariotAI prototype
KENT_URLS = [
    "https://www.kent.ac.uk/courses/undergraduate",
    "https://www.kent.ac.uk/whats-on#events",
    "https://www.kent.ac.uk/student-life",
    "https://www.kent.ac.uk/courses/visit/open-days",
    "https://www.kent.ac.uk/accommodation/canterbury/prices",
    "https://www.kent.ac.uk/courses/postgraduate",
    "https://www.kent.ac.uk/international/international-applicant-faqs"
]

def scrape_text_from_url(url: str) -> str:
    """Scrapes paragraph text securely from a given University URL."""
    try:
        print(f"Scraping: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract text from standard paragraph tags to avoid scraping navigation bars/footers
        paragraphs = soup.find_all('p')
        text = " ".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        return text
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return ""

def setup_azure_search_index():
    """Idempotent function to create the Azure AI Search index if it doesn't exist."""
    endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    key = os.getenv("AZURE_SEARCH_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX")

    credential = AzureKeyCredential(key)
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

    # Define the structure of our database table (Index)
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SearchableField(name="source_url", type=SearchFieldDataType.String),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=1536, vector_search_profile_name="chariotai-profile")
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="chariotai-algo")],
        profiles=[VectorSearchProfile(name="chariotai-profile", algorithm_configuration_name="chariotai-algo")]
    )

    index = SearchIndex(name=index_name, fields=fields, vector_search=vector_search)
    
    print(f"Ensuring index '{index_name}' exists...")
    # This creates the index or updates it if it exists
    index_client.create_or_update_index(index)
    return SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

def main():
    print("--- Starting ChariotAI Knowledge Ingestion ---")
    
    # 1. Setup Embeddings Model
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_EMBEDDING_DEPLOYMENT"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )
    
    # 2. Setup Vector Store
    search_client = setup_azure_search_index()
    
    # 3. Setup Text Splitter (chunks of 1000 characters with 100 char overlap)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    
    documents_to_upload = []

    # 4. Process each URL
    for url in KENT_URLS:
        raw_text = scrape_text_from_url(url)
        if not raw_text:
            continue
            
        chunks = text_splitter.split_text(raw_text)
        print(f"  -> Split into {len(chunks)} chunks.")
        
        for chunk in chunks:
            # We must handle the embedding process inside a try block
            try:
                vector = embeddings.embed_query(chunk)
                doc = {
                    "id": str(uuid.uuid4()),
                    "content": chunk,
                    "source_url": url,
                    "content_vector": vector
                }
                documents_to_upload.append(doc)
            except Exception as e:
                print(f"Error embedding chunk: {e}")
                
    # 5. Upload to Azure AI Search in a batch
    if documents_to_upload:
        print(f"Uploading {len(documents_to_upload)} vectorized chunks to Azure AI Search...")
        search_client.upload_documents(documents=documents_to_upload)
        print("Upload complete! Knowledge Base is ready.")
    else:
        print("No documents were processed.")

if __name__ == "__main__":
    main()
