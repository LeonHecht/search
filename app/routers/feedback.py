# Copyright 2025 Leon Hecht
# Licensed under the Apache License, Version 2.0 (see LICENSE file)

from fastapi import APIRouter, HTTPException, Body, Request
from sqlmodel import Session, select
from pydantic import BaseModel, Field
from app.models.feedback import Feedback
from app.models.query_log import QueryLog
from app.db import engine

router = APIRouter()


class FeedbackRequest(BaseModel):
    """
    Payload for submitting feedback.
    """
    query_log_id: int = Field(..., description="ID of the original search log")
    document_id: str = Field(..., description="Retrieved document ID")
    positive: bool = Field(..., description="True=Like, False=Dislike")


@router.post("/feedback", summary="Submit like/dislike feedback")
async def submit_feedback(
    request: Request,
    fb: FeedbackRequest = Body(...),
) -> dict:
    # Optional: you could re-derive client IP if you care
    with Session(engine) as session:
        # ensure the referenced QueryLog exists
        if not session.exec(select(QueryLog).where(QueryLog.id == fb.query_log_id)).first():
            raise HTTPException(status_code=404, detail="QueryLog not found")

        new_fb = Feedback(
            query_log_id=fb.query_log_id,
            document_id=fb.document_id,
            positive=fb.positive,
        )
        session.add(new_fb)
        session.commit()
        session.refresh(new_fb)

    return {"status": "ok", "feedback_id": new_fb.id}
