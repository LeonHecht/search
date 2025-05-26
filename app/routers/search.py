from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from app.services.bm25 import bm25_search
from app.config import ENABLE_TRANSFORMERS
from app.services.transformer import transformer_search
from app.models.query_log import Session, QueryLog, engine
from app.services.utils import country_from_ip, city_from_ip

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 30
    use_transformer: bool = False

class SearchResult(BaseModel):
    id: str
    score: float
    title: str | None = Field(default=None)   # <- allow None
    snippet: str | None = None
    download_url: str | None = None

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.post("/search", response_model=list[SearchResult], summary="Run a BM25 or transformer search")

def search_endpoint(req: SearchRequest = Body(..., description="Your search parameters")) -> list[SearchResult]:
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")
    
    client_ip = request.client.host
    country   = country_from_ip(client_ip) or "Unknown"
    city      = city_from_ip(client_ip) or "Unknown"
    
    with Session(engine) as sess:
        sess.add(
            QueryLog(
                client_ip=req.client.host,
                country=country,
                city=city,
                mode="semantica" if req.use_transformer else "exacta",
                query=req.query.strip(),
            )
        )
        sess.commit()

    if req.use_transformer:
        return transformer_search(req.query, top_k=req.top_k)
    else:
        # existing BM25 search returns full results
        return bm25_search(req.query, top_k=req.top_k)