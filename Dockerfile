# Use an official Python image
FROM python:3.10-slim

# Install system dependencies required by OSMnx
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgeos-dev \
    proj-bin \
    proj-data \
    proj-dev \
    libproj-dev \
    libspatialindex-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . /app

# Expose port 5000 for Flask
EXPOSE 5000

# Run your Flask app
ENTRYPOINT ["gunicorn", "frontch:app", "--bind", "0.0.0.0:5000"]
