# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend ./backend
COPY "CAP templates" "./CAP templates"

# Create temp_audio directory
RUN mkdir -p temp_audio

# Expose port (Fly.io uses PORT env variable)
EXPOSE 8080

# Run the application
CMD cd backend && uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
