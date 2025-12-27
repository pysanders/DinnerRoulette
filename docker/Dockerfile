FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and set up directories
# Use UID 99 and GID 100 to match Unraid's nobody:users
RUN groupadd -g 100 users || true && \
    useradd -m -u 99 -g 100 appuser && \
    mkdir -p /app/backups && \
    chown -R 99:100 /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)"

# Run with gunicorn for production (using config file for better logging)
CMD ["gunicorn", "--config", "docker/gunicorn.conf.py", "run:app"]
