# Use the official Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy requirement files
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Ensure .env is picked up inside the container
ENV PYTHONPATH=/app

# Run the CLI app (can change this to uvicorn if you switch to FastAPI later)
CMD ["python", "app.py"]
