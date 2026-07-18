import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import settings

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    settings.STATIC_URL_PREFIX,
    StaticFiles(directory=settings.UPLOAD_DIR),
    name="static",
)


@app.get("/", tags=["health"])
def root() -> dict:
    """Basic liveness endpoint used to verify the server is running."""
    return {"project": settings.PROJECT_NAME, "status": "ok"}


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Health check endpoint for uptime monitoring and local dev sanity checks."""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
