# Cosmic Watch - Frontend Docker Image
# Copyright © 2026 Rohit. Made with love by Rohit.
# All rights reserved.
# Repository: https://github.com/rohitb6/Cosmic_Watch

# Frontend Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run the app
RUN npm install -g serve

# Copy built app from builder
COPY --from=builder /app/dist ./dist

# Create non-root user
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1

# Run application
CMD ["serve", "-s", "dist", "-l", "3000"]
