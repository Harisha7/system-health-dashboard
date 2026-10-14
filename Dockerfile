# Use minimal Python runtime
FROM python:3.11-slim

# Install system dependencies needed for compiling psutil/psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/
COPY tests/ ./tests/

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
ENV PYTHONPATH=/app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]