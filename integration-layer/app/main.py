"""
Integration Layer Main Application
FastAPI application that bridges CarbonCheck with UNDP Registry
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .routers.registry_router import router as registry_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CarbonCheck Integration Layer",
    description="""
    Integration layer connecting CarbonCheck AI verification system
    with UNDP National Carbon Registry.

    ## Features
    - Registry project management
    - Verification pipeline execution
    - Trust score computation
    - Leaderboard generation

    ## Architecture
    - **Ground Layer**: UNDP Registry data ingestion
    - **Satellite Layer**: NDVI analysis via Sentinel Hub (Copernicus)
    - **AI Layer**: CO2 prediction and anomaly detection
    - **Scoring Layer**: Trust score calculation
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(registry_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "CarbonCheck Integration Layer",
        "version": "1.0.0",
        "description": "Bridge between CarbonCheck and UNDP Registry",
        "endpoints": {
            "registry_projects": "/api/registry/projects",
            "verify_project": "/api/registry/projects/{id}/verify",
            "leaderboard": "/api/registry/leaderboard",
            "statistics": "/api/registry/statistics",
            "documentation": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "integration-layer"}


# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Integration Layer starting up...")
    logger.info("Registry service URL: configured in environment")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Integration Layer shutting down...")
