import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

# Initialize LLM via OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-72b-instruct")

if OPENROUTER_API_KEY:
    print(f"--- LLM Setup ---")
    print(f"Model: {OPENROUTER_MODEL}")
    print(f"API Key loaded (ending in: {OPENROUTER_API_KEY[-4:]})")
else:
    print("WARNING: OPENROUTER_API_KEY not found in environment variables!")

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model=OPENROUTER_MODEL,
    default_headers={
        "HTTP-Referer": "http://localhost:8000", # Required by some OpenRouter models
        "X-Title": "Chrome RAG Plugin",
    }
)

# Initialize Embeddings (HuggingFace runs locally and is free)
# all-MiniLM-L6-v2 is a small, fast model with 384 dimensions
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Local persistence directory for ChromaDB
PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "chroma_db")

def get_vectorstore():
    """Returns the Chroma vector store, initialized with a persist directory."""
    return Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings
    )

def ingest_text(text: str, url: str):
    """Chunks the text and uploads it to Chroma with URL metadata."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    
    # Initialize/Load vector store
    vectorstore = get_vectorstore()
    
    # Adding metadata allows us to filter by URL during retrieval
    vectorstore.add_texts(chunks, metadatas=[{"url": url} for _ in chunks])
    return len(chunks)

def query_rag(query: str, url: str):
    """Retrieves relevant chunks for a URL and generates an answer using the LLM."""
    vectorstore = get_vectorstore()
    
    # Retrieve top 3 relevant documents specifically for this URL
    docs = vectorstore.similarity_search(query, k=3, filter={"url": url})
    
    context = "\n\n".join([doc.page_content for doc in docs])
    
    if not context:
        return "I don't have enough context from this page to answer your question. Have you ingested the page content yet?"

    prompt = f"""You are a helpful assistant for a Chrome extension. 
Use the following pieces of retrieved context from the current web page to answer the user's question. 
If the answer is not in the context, say that you don't know based on the provided information.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
    
    try:
        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        print(f"Error calling LLM: {str(e)}")
        return f"Sorry, I encountered an error while talking to the AI: {str(e)}"
