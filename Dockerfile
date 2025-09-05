# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
    \
    DATA_DIR=/var/data

WORKDIR /app

# System deps (some libraries like aiohttp may need these at build/runtime)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first for better layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure data directory exists (the app also creates it at runtime if missing)
RUN mkdir -p "$DATA_DIR"

# Default command: run the Instagram tracker bot
CMD ["python", "instagram_tracker.py"]
