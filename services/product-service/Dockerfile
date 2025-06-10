FROM python:3.10-slim

# Create a non-root user
RUN useradd -m appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

WORKDIR /app

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sqlite3 && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
USER appuser

# Copy application code
COPY --chown=appuser:appuser app.py .

# Create data directory with write permissions
RUN mkdir -p /app/data && \
    chmod 755 /app/data

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV DATABASE_PATH=/app/data/products.db

# Expose the application port
EXPOSE 5556

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5556/ || exit 1

# Run the application
CMD ["python", "app.py"]
