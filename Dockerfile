# Dockerfile for Surf AI Agent
# Optimized for free container services (2-8GB RAM, Xeon CPUs)
# Multi-stage build for minimal image size

# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash surf && \
    mkdir -p /home/surf/app && \
    chown surf:surf /home/surf/app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/surf/.local

# Make sure scripts in .local are usable
ENV PATH=/home/surf/.local/bin:$PATH

# Copy application code
COPY . .

# Set ownership
RUN chown -R surf:surf /app

# Switch to non-root user
USER surf

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Default port
ENV PORT=8080 \
    HOST=0.0.0.0

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8080/api/health', timeout=2).raise_for_status()" || exit 1

# Run the web server
CMD ["python", "-m", "surf.web.server"]
