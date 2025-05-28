from datetime import datetime
from sqlmodel import SQLModel, Field


class Feedback(SQLModel, table=True):
    """
    Record whether a user found a retrieved document helpful.

    Attributes
    ----------
    id : int | None
        Auto-increment primary key.
    query_log_id : int
        Foreign-key to the QueryLog entry for this search.
    document_id : str
        The ID of the retrieved document.
    positive : bool
        True for “Like”, False for “Dislike”.
    timestamp : datetime
        When the feedback was submitted.
    """
    id: int | None = Field(default=None, primary_key=True)
    query_log_id: int = Field(foreign_key="querylog.id", index=True)
    document_id: str = Field(index=True)
    positive: bool
    timestamp: datetime = Field(default_factory=datetime.now)
