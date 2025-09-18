# docker buildx build --platform linux/amd64 -t agosain/marketplace-api-pod:latest . -f ./Dockerfile.backend --no-cache
#  1. Stop the container completely:
#  docker-compose down

#  2. Remove any cached containers:
#  docker system prune -f

#  3. Restart with fresh build:
#  docker-compose up --build
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 with optimized apt settings
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

# Copy .env file if it exists (optional)
COPY .env* ./

# Copy startup scripts
COPY start.sh ./
COPY railway-start.sh ./
RUN chmod +x start.sh railway-start.sh

# Copy API application code
COPY api/ ./api/

# Expose port
EXPOSE 8000

# Command to run the application using Railway's PORT variable
CMD ["./railway-start.sh"]