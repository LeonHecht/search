from fastapi import FastAPI
from app.routers import search
from app.routers import upload
from fastapi.staticfiles import StaticFiles
from app.config import CORPUS_PATH
import os

app = FastAPI(title="Legal Search App")

app.include_router(search.router)
app.include_router(upload.router)

# Serve anything in your corpus folder at `/files/<filename>`
app.mount(
    "/files",
    StaticFiles(directory=os.path.join(CORPUS_PATH, "files")),
    name="files",
)