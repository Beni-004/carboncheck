# Multi-stage build for optimized registry-service image
# Target size: < 300 MB (production runtime only)

# ============================================
# Stage 1: Dependencies - Install all dependencies
# ============================================
FROM node:20-alpine AS dependencies

WORKDIR /build

# Copy package files
COPY package.json package-lock.json ./

# Install ALL dependencies (including dev dependencies for build)
RUN npm ci --legacy-peer-deps

# ============================================
# Stage 2: Builder - Build the application
# ============================================
FROM node:20-alpine AS builder

WORKDIR /build

# Copy node_modules from dependencies stage
COPY --from=dependencies /build/node_modules ./node_modules

# Copy source code and configuration
COPY package.json package-lock.json nest-cli.json tsconfig.json ./
COPY src/ ./src/

# Build the application
RUN npm run build

# ============================================
# Stage 3: Production - Minimal runtime image
# ============================================
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install ONLY production dependencies
RUN npm ci --only=production --ignore-scripts --legacy-peer-deps && \
    npm cache clean --force

# Copy built application from builder stage
COPY --from=builder /build/dist ./dist

# Expose port (Railway will override with $PORT)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 3000) + '/api/v1/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the production server
CMD ["npm", "run", "start:prod"]
