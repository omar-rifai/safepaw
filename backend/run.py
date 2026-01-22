from fastapi import FastAPI
from . import create_app

app: FastAPI = create_app()

# Run with:
#uvicorn backend.run:app --reload --host 0.0.0.0 --port 5000
