# Multi-stage build for optimized backend image
# Target size: < 500 MB (production runtime only)

# Cache buster - change this value to force Railway rebuild
ARG CACHE_BUST=v3

# ============================================
# Stage 1: Builder - Install dependencies
# ============================================
FROM python:3.12-slim AS builder

ARG CACHE_BUST
RUN echo "Cache bust: ${CACHE_BUST}"

WORKDIR /build

# Install system dependencies for geospatial libraries (GDAL, GEOS, PROJ)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables for compilation
ENV GDAL_CONFIG=/usr/bin/gdal-config \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

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

# Install runtime geospatial libraries
# Only gdal-bin - apt will automatically pull correct dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gdal-bin && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH"

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
