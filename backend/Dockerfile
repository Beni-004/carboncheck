# Optimized multi-stage build for Railway
# Target size: < 1 GB (removed unused ML packages)

# Cache buster - change this value to force Railway rebuild
ARG CACHE_BUST=v4-lean

# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.12-slim AS builder

ARG CACHE_BUST
RUN echo "Cache bust: ${CACHE_BUST}"

WORKDIR /build

# Install only essential build dependencies
# NOTE: GDAL removed - rasterio/geopandas not used, code has fallback
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies in the virtual environment
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime - Minimal production image
# ============================================
FROM python:3.12-slim AS runtime

ARG CACHE_BUST
RUN echo "Cache bust: ${CACHE_BUST}"

WORKDIR /app

# No additional system packages needed!
# GDAL/GEOS/PROJ removed since rasterio/geopandas not used

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy ONLY application code
COPY app/ ./app/
COPY *.py ./

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:${PORT:-8000}/health')" || exit 1

# Start the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
