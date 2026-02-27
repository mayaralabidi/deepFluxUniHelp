# deepFluxUniHelp - Docker image
# Phase 1 - Base setup

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for PDF, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory
RUN mkdir -p data/chroma data/sample

EXPOSE 8000 8501

# Default: run both API and Streamlit
# Override with docker-compose for separate services
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
