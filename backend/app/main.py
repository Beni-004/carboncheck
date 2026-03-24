"""
CarbonCheck API - Main FastAPI Application
Provides credit verification, bulk audit, and leaderboard endpoints.
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="CarbonCheck API",
    description="Carbon credit verification and trust scoring API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration for frontend integration
# TODO: Set FRONTEND_URL environment variable in Railway to your Vercel URL
frontend_url = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:3001",  # Alternate local port
]

if frontend_url:
    allowed_origins.append(frontend_url)
    # Also allow preview deployments if using Vercel pattern
    if "vercel.app" in frontend_url:
        base_domain = frontend_url.split("//")[1].split(".")[0]
        allowed_origins.append(f"https://*.vercel.app")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if frontend_url else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Basic health check - will be enhanced with dependency checks"""
    return {"status": "healthy"}


# Router registration will be added here as routers are implemented
# Example:
# from app.routers import verify, leaderboard, health
# app.include_router(verify.router, prefix="/api", tags=["verify"])
# app.include_router(leaderboard.router, prefix="/api", tags=["leaderboard"])
# app.include_router(health.router, prefix="/api", tags=["health"])

# Error handling middleware will be registered here
# Example:
# from app.middleware.error_mapper import error_handler_middleware
# app.middleware("http")(error_handler_middleware)
