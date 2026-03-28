# Multi-stage build for optimized Next.js frontend image
# Target size: < 300 MB (production runtime only)

# ============================================
# Stage 1: Dependencies - Install dependencies
# ============================================
FROM node:20-alpine AS dependencies

WORKDIR /build

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# ============================================
# Stage 2: Builder - Build Next.js application
# ============================================
FROM node:20-alpine AS builder

WORKDIR /build

# Copy node_modules from dependencies stage
COPY --from=dependencies /build/node_modules ./node_modules

# Copy source code and configuration
COPY . .

# Build Next.js application
# This creates optimized production build in .next/
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ============================================
# Stage 3: Production - Minimal runtime image
# ============================================
FROM node:20-alpine

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy package files and install ONLY production dependencies
COPY package.json package-lock.json ./
RUN npm ci --only=production --ignore-scripts && \
    npm cache clean --force

# Copy built Next.js application from builder
COPY --from=builder /build/.next ./.next
COPY --from=builder /build/public ./public
COPY --from=builder /build/next.config.js ./

# Set correct permissions
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port (Railway will override with $PORT)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:' + (process.env.PORT || 3000), (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start Next.js production server
CMD ["npm", "start"]
