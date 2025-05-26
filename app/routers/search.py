from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from app.services.bm25 import bm25_search
from app.config import ENABLE_TRANSFORMERS
from app.services.transformer import transformer_search

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 30
    use_transformer: bool = False

class SearchResult(BaseModel):
    id: str
    title: str
    score: float
    snippet: str
    download_url: str | None

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.post("/search", response_model=list[SearchResult], summary="Run a BM25 or transformer search")

def search_endpoint(req: SearchRequest = Body(..., description="Your search parameters")) -> list[SearchResult]:
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")

    if req.use_transformer:
        return transformer_search(req.query, top_k=req.top_k)
    else:
        # existing BM25 search returns full results
        return bm25_search(req.query, top_k=req.top_k)