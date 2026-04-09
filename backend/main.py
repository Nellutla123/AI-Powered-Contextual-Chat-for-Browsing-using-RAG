from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import rag_pipeline

app = FastAPI(title="Chrome RAG Plugin Backend")

# Allow the Chrome extension to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, you'd specify your extension ID
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IngestRequest(BaseModel):
    text: str
    url: str

class ChatRequest(BaseModel):
    query: str
    url: str

@app.get("/")
async def root():
    return {"message": "Chrome RAG Plugin Backend is running"}

@app.post("/ingest")
async def ingest(request: IngestRequest):
    try:
        num_chunks = rag_pipeline.ingest_text(request.text, request.url)
        return {"status": "success", "chunks_ingested": num_chunks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        answer = rag_pipeline.query_rag(request.query, request.url)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
