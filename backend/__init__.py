from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.routes import api  # import APIRouter from routes.py

def create_app() -> FastAPI:
    """
    Factory function to create FastAPI app with CORS and routes.
    """
    app = FastAPI(title="Optimization API")

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

    try:
        app.mount("/", StaticFiles(directory="frontend/build", html=True), name="react")
    except FileNotFoundError:
        print("frontend/build not found, skipping static files mount")

    return app