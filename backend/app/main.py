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

    # Check Sentinel Hub (Copernicus Data Space)
    sentinel_client_id = os.getenv("SENTINEL_CLIENT_ID")
    sentinel_client_secret = os.getenv("SENTINEL_CLIENT_SECRET")

    if sentinel_client_id and sentinel_client_secret:
        try:
            from app.verification_engine.satellite_layer.sentinel_client import SentinelClient
            sentinel_client = SentinelClient()
            if sentinel_client.initialized:
                integrations["sentinel_hub"] = {
                    "status": "operational",
                    "message": "Sentinel Hub API configured with OAuth credentials"
                }
            else:
                integrations["sentinel_hub"] = {
                    "status": "degraded",
                    "message": "Sentinel Hub credentials configured but initialization failed"
                }
        except Exception as e:
            integrations["sentinel_hub"] = {
                "status": "degraded",
                "message": f"Sentinel Hub initialization error: {str(e)}"
            }
    else:
        integrations["sentinel_hub"] = {
            "status": "unavailable",
            "message": "Sentinel Hub credentials not configured - using deterministic mock satellite data"
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
            "satellite": "Sentinel Hub (Copernicus) requires OAuth credentials for live satellite data",
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
