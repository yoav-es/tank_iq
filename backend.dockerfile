# 1) Base image: small, secure Python runtime
FROM python:3.11-slim AS runtime

# 2) Set working directory inside the container
WORKDIR /app

# 3) Install system dependencies (optional: for building wheels or SSL/locales)
# Uncomment if you need build tools or ca-certificates
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# 4) Copy only dependency manifest first to leverage Docker layer caching
COPY requirements.txt .

# 5) Install Python dependencies (no cache to keep image small)
RUN pip install --no-cache-dir -r requirements.txt

# 6) Copy application source
COPY app/ ./app/
COPY main.py .

# 7) (Optional) Set environment for performance and predictable behavior
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    LOG_LEVEL=info \
    DEBUG=true

# 8) Expose service port
EXPOSE 8000

# 9) Default command: run FastAPI via Uvicorn
CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]

# # Healthcheck for backend (requires a /health endpoint in FastAPI)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
#   CMD curl -f http://localhost:8000/health || exit 1