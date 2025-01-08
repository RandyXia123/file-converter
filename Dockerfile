# Use a more specific base image for better consistency
FROM python:3.9-slim-bullseye

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # Add environment variables for Tesseract
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata \
    # Configure number of workers based on CPU cores
    WORKERS=4

# Install system dependencies and clean up in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    # Add performance-related packages
    libtesseract-dev \
    libleptonica-dev \
    # Clean up
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    # Create necessary directories
    && mkdir -p /app/uploads /app/converted

# Set working directory
WORKDIR /app

# Install Python dependencies first (for better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    # Install additional performance-related packages
    && pip install --no-cache-dir \
    python-multipart \
    gunicorn[gevent]

# Copy application code
COPY . .

# Set correct permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 5000

# Use a more optimized Gunicorn configuration
CMD gunicorn \
    --bind 0.0.0.0:5000 \
    --timeout 300 \
    --workers ${WORKERS} \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --keep-alive 5 \
    --log-level info \
    app:app