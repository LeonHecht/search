# Copyright 2025 Leon Hecht
# Licensed under the Apache License, Version 2.0 (see LICENSE file)

from typing import List

from fastapi import APIRouter, HTTPException, Body, Request
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.services.bm25 import bm25_search
from app.services.transformer import transformer_search
from app.models.query_log import QueryLog
from app.services.utils import country_from_ip, city_from_ip
from app.db import engine

router = APIRouter()


class SearchRequest(BaseModel):
    """Parameters for a search request."""
    query: str
    top_k: int = 30
    use_transformer: bool = False


class SearchResult(BaseModel):
    """A single search hit."""
    id: str
    score: float
    title: str | None = Field(default=None)   # <- allow None
    snippet: str | None = None
    download_url: str | None = None


class SearchResponse(BaseModel):
    """
    Response for `/search`.

    Parameters
    ----------
    query_log_id : int
        The ID of the logged query in the database.
    results : List[SearchResult]
        The list of retrieved documents.
    """
    query_log_id: int = Field(..., description="ID of the QueryLog entry")
    results: List[SearchResult] = Field(..., description="Retrieved documents")


@router.get("/ping")
def ping():
    return {"message": "pong"}


@router.post("/search", response_model=SearchResponse, summary="Run a BM25 or transformer search")
def search_endpoint(request: Request, req: SearchRequest = Body(..., description="Your search parameters")) -> SearchResponse:
    """
    Execute a search and log the query.

    1. Validates non-empty query.
    2. Captures client IP, country, and city.
    3. Inserts a QueryLog row and retrieves its ID.
    4. Runs either BM25 or transformer search.
    5. Returns the log ID along with the hits.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")
    
    client_ip = request.client.host or "Unknown"
    country   = country_from_ip(client_ip) or "Unknown"
    city      = city_from_ip(client_ip) or "Unknown"
    
    # 1) Log the search
    with Session(engine) as sess:
        log = QueryLog(
            client_ip=client_ip,
            country=country,
            city=city,
            mode="semantica" if req.use_transformer else "exacta",
            query=req.query.strip(),
        )
        sess.add(log)
        sess.commit()
        sess.refresh(log)  # populates log.id

    # 2) Run the actual search  
    if req.use_transformer:
        hits = transformer_search(req.query, top_k=req.top_k)
    else:
        # existing BM25 search returns full results
        hits = bm25_search(req.query, top_k=req.top_k)
    
    # 3) Return both the log ID and the results
    return SearchResponse(query_log_id=log.id, results=hits)