FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies from correct location
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir "fastapi>=0.110.0" "uvicorn>=0.24.0" "sqlalchemy>=2.0.30" "python-jose[cryptography]" "pydantic>=2.0.0" "python-multipart"

# Copy backend source
COPY backend/ .

# Expose the API port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]