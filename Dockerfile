# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy application code
COPY . .

# PORT is automatically provided by Cloud Run, typically 8080
# ENV PORT=8080
# EXPOSE $PORT

# Expose the port Flask runs on
EXPOSE 5000

# Run the web service on container startup
# Set desired Gunicorn worker count (adjust based on Cloud Run CPU/Memory and expected load)
# Cloud Run v2 usually provides at least 1 CPU, v1 might share, start with 1 or 2
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling
CMD ["gunicorn", "--bind", ":5000", "--workers", "1", "--threads", "2", "--timeout", "0", "pjecz_casiopea_flask.main:app"]
