# Use official slim Python image to minimise image size
FROM python:3.13-slim

# Prevent .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required by psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (leverages Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Set Flask environment variables for production
ENV FLASK_APP=run.py \
    FLASK_ENV=production

# Create a non-root user and switch to it (security best practice)
RUN useradd --no-create-home fitact
USER fitact

# Expose Flask port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]