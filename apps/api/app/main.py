"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app import routes

app = FastAPI(
    title="Production Lineage Concierge API",
    description="Phase 1: Deterministic lineage and auditability",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router, prefix="/api", tags=["api"])


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "environment": settings.app_env
    }


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Production Lineage Concierge API", "version": "0.1.0"}
