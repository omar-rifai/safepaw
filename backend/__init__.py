from fastapi import FastAPI
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.private_routes import internal_api  # import APIRouter from routes.py
from .api.public_routes import public_api
from sqlmodel import SQLModel 
from backend.db import engine

def create_app() -> FastAPI:
    """
    Factory function to create FastAPI app with CORS and routes.
    """

    async def lifespan(app:FastAPI):
        SQLModel.metadata.create_all(engine)
        yield

    app = FastAPI(title="SAFEPAW API", lifespan=lifespan)

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],   # adjust for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(public_api, prefix="/api")
    app.include_router(internal_api, prefix="/api/private")

    BASE_DIR = Path(__file__).resolve().parent.parent
    STATIC_DIR = BASE_DIR / "frontend" / "build"

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="react")
        
    return app