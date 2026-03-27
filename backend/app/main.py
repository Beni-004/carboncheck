"""
CarbonCheck API - Main FastAPI Application
Provides credit verification, bulk audit, and leaderboard endpoints.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.routers import verify, leaderboard

# Import middleware
from app.middleware.error_mapper import error_mapping_middleware
from app.clients.base_client import close_http_client

# Import for integration checks
from app.db import get_db_client
from app.verification_engine.satellite_layer.gee_client import GEE_AVAILABLE
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="CarbonCheck API",
    description="Carbon credit verification and trust scoring API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for frontend integration
frontend_url = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:3001",  # Alternate local port
]

if frontend_url:
    allowed_origins.append(frontend_url)
    # Also allow preview deployments if using Vercel pattern
    if "vercel.app" in frontend_url:
        allowed_origins.append("https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if frontend_url else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error mapping middleware (ensures no HTTP 500 responses)
app.middleware("http")(error_mapping_middleware)

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "service": "CarbonCheck API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with integration status"""
    status = "healthy"
    integrations = {}

    # Check database connectivity
    try:
        db_client = get_db_client()
        # Simple query to test connection
        result = db_client.client.table("carbon_credits").select("count").limit(1).execute()
        integrations["database"] = {
            "status": "operational",
            "message": "Supabase connection successful"
        }
    except Exception as e:
        integrations["database"] = {
            "status": "degraded",
            "message": f"Database connection failed: {str(e)}"
        }
        status = "degraded"

    # Check Google Earth Engine
    gee_status = "operational" if GEE_AVAILABLE else "unavailable"
    gee_message = "GEE Python library available" if GEE_AVAILABLE else "GEE library not installed - using mock satellite data"

    # Check if GEE is actually initialized (not just library available)
    if GEE_AVAILABLE:
        try:
            from app.verification_engine.satellite_layer.gee_client import GEEClient
            gee_client = GEEClient()
            if not gee_client.initialized:
                gee_status = "degraded"
                gee_message = "GEE library available but not authenticated - using mock satellite data"
        except Exception as e:
            gee_status = "degraded"
            gee_message = f"GEE initialization error: {str(e)}"

    integrations["google_earth_engine"] = {
        "status": gee_status,
        "message": gee_message
    }

    # Registry status
    integrations["verra_registry"] = {
        "status": "operational",
        "message": "Verra registry scraping available"
    }

    integrations["gold_standard"] = {
        "status": "mock",
        "message": "Gold Standard API not implemented - using mock data"
    }

    integrations["acr_registry"] = {
        "status": "mock",
        "message": "ACR API not implemented - using mock data"
    }

    # Check if any critical systems are down
    critical_services = ["database", "verra_registry"]
    for service in critical_services:
        if integrations[service]["status"] in ["degraded", "unavailable"]:
            status = "degraded"

    return {
        "status": status,
        "timestamp": "2026-03-27T00:00:00Z",
        "integrations": integrations,
        "notes": {
            "gee": "Google Earth Engine requires service account credentials for live satellite data",
            "registries": "Gold Standard and ACR integrations are placeholder implementations",
            "cache": "System uses intelligent fallback caching when external APIs are unavailable"
        }
    }


# Register routers
app.include_router(verify.router, prefix="/api", tags=["verify"])
app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"])


# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Close pooled HTTP client on app shutdown."""
    await close_http_client()
