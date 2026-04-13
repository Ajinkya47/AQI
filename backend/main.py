"""
FastAPI main application entry point.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from contextlib import asynccontextmanager

from backend.database import create_tables
from backend.api.routes import aqi, traffic, predictions, routes
from backend.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    create_tables()
    print("✅ Database tables created")
    print("🚀 Application started")
    yield
    # Shutdown
    print("👋 Application shutting down")


app = FastAPI(
    title="AI Pollution & Traffic Optimizer",
    description="An AI-powered smart city system for pollution prediction and route optimization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Include routers
app.include_router(aqi.router, prefix="/api/aqi", tags=["AQI"])
app.include_router(traffic.router, prefix="/api/traffic", tags=["Traffic"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(routes.router, prefix="/api/routes", tags=["Routes"])


@app.get("/")
async def root(request: Request):
    """Serve the main dashboard."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Pollution & Traffic Optimizer"}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}
