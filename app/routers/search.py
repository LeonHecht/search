from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.bm25 import bm25_search
from app.config import ENABLE_TRANSFORMERS

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 10

class SearchResult(BaseModel):
    id: str
    title: str
    score: float
    snippet: str
    download_url: str | None

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.post("/search", response_model=list[SearchResult])
def search_endpoint(req: SearchRequest):
    # TODO: wire BM25 or transformer search
    if not req.query:
        raise HTTPException(status_code=400, detail="Query must not be empty")
    
    results = bm25_search(req.query, top_k=req.top_k)
    return results