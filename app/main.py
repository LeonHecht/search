from fastapi import FastAPI
from app.routers import search

app = FastAPI(title="Legal Search App")

app.include_router(search.router)
