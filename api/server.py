"""FastAPI application for MEP Takeoff Pro."""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes.takeoff import router as takeoff_router

app = FastAPI(title="MEP Takeoff Pro API")

# CORS — allow local dev and any configured origin
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://localhost:5180").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(takeoff_router)

# Serve built frontend in production
_FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "MEP Takeoff Pro API"}


if _FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=_FRONTEND_DIR / "assets"), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve the SPA — any non-API route returns index.html."""
        file_path = _FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_FRONTEND_DIR / "index.html")
