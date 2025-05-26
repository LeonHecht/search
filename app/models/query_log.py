from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime

class QueryLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    country: str | None = Field(default=None, index=True)  # e.g. "US", "PY"
    city: str | None = Field(default=None, index=True)  # e.g. "Asuncion"
    timestamp: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))
    client_ip: str
    mode: str            # "exacta" or "semantica"
    query: str

# configure your SQLite (or any) engine
sqlite_url = "sqlite:///./queries.db"
engine = create_engine(sqlite_url, echo=False)
SQLModel.metadata.create_all(engine)