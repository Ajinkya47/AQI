"""
FastAPI main application entry point.
Routes: /  → landing page
        /register → register
        /login    → login
        /dashboard → AirAware dashboard (auth via JS)
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from contextlib import asynccontextmanager

from backend.database import create_tables
from backend.api.routes import aqi, traffic, predictions, routes
from backend.api.routes.auth import router as auth_router
from backend.config import get_settings


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("✅ Database tables created")
    print("🚀 Application started")
    yield
    print("👋 Application shutting down")


app = FastAPI(
    title="AirAware – AI Pollution & Traffic Optimizer",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# ── API Routers ────────────────────────────────────────────────────────────────
app.include_router(aqi.router,         prefix="/api/aqi",         tags=["AQI"])
app.include_router(traffic.router,     prefix="/api/traffic",     tags=["Traffic"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(routes.router,      prefix="/api/routes",      tags=["Routes"])
app.include_router(auth_router,        prefix="/api/auth",        tags=["Auth"])



# ── Page Routes ────────────────────────────────────────────────────────────────
@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}