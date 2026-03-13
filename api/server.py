"""FastAPI application for MEP Takeoff Pro."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.takeoff import router as takeoff_router

app = FastAPI(title="MEP Takeoff Pro API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(takeoff_router)


@app.get("/")
async def health_check():
    return {"status": "ok", "service": "MEP Takeoff Pro API"}
