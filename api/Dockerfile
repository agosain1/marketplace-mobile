# docker buildx build --platform linux/amd64 -t agosain/marketplace-api-pod:latest . -f ./Dockerfile.backend --no-cache
#  1. Stop the container completely:
#  docker-compose down

#  2. Remove any cached containers:
#  docker system prune -f

#  3. Restart with fresh build:
#  docker-compose up --build
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies for psycopg2 with optimized apt settings
RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy project files into the image (works for both root and api build contexts)
COPY . .

# Install Python dependencies from whichever requirements file exists
RUN bash -lc ' \
    if [ -f requirements.txt ]; then \
        echo "Installing deps from ./requirements.txt"; \
        pip install --no-cache-dir -r requirements.txt; \
    elif [ -f api/requirements.txt ]; then \
        echo "Installing deps from ./api/requirements.txt"; \
        pip install --no-cache-dir -r api/requirements.txt; \
    else \
        echo "ERROR: requirements.txt not found in build context" >&2; \
        ls -la; \
        exit 1; \
    fi'

ENV PYTHONPATH=/app

# Ensure startup scripts are executable (support both possible locations)
RUN chmod +x railway-start.sh 2>/dev/null || true && \
    chmod +x api/railway-start.sh 2>/dev/null || true

# Expose port
EXPOSE 8000

# Command to run the application using Railway's PORT variable
CMD ["./railway-start.sh"]