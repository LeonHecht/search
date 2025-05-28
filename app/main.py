import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import search
from app.routers import upload
from app.routers import feedback
from app.config import CORPUS_PATH
from app.models.query_log import QueryLog
from app.models.feedback import Feedback
from app.db import engine

app = FastAPI(title="Legal Search App")

app.include_router(search.router)
app.include_router(upload.router)
app.include_router(feedback.router)

# Serve anything in your corpus folder at `/files/<filename>`
app.mount(
    "/files",
    StaticFiles(directory=os.path.join(CORPUS_PATH, "files")),
    name="files",
)