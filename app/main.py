from fastapi import FastAPI
from app.routers import search
from app.routers import upload

app = FastAPI(title="Legal Search App")

app.include_router(search.router)
app.include_router(upload.router)