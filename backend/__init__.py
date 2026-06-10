from fastapi import FastAPI
from pathlib import Path
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.routes import api  # import APIRouter from routes.py
from sqlmodel import SQLModel 
from backend.db import engine

def create_app() -> FastAPI:
    """
    Factory function to create FastAPI app with CORS and routes.
    """

    async def lifespan(app:FastAPI):
        SQLModel.metadata.create_all(engine)
        yield

    app = FastAPI(title="Optimization API", lifespan=lifespan)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # adjust for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api, prefix="/api")

    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_DIR = BASE_DIR / "frontend" / "build"

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="react")
        
    return app