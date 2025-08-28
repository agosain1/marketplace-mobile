#!/bin/bash

# Railway-optimized startup script for Marketplace Backend
set -e

echo "=== Marketplace Backend Railway Startup ==="
echo "PORT: ${PORT:-8000}"
echo "ENVIRONMENT: ${ENVIRONMENT:-production}"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Use Railway's PORT environment variable or default to 8000
API_PORT=${PORT:-8000}
echo "Starting FastAPI on port: $API_PORT"

# Start the application with Railway's dynamic port
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running in development mode with auto-reload"
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port "$API_PORT" \
        --reload
else
    echo "Running in production mode"
    exec uvicorn api.main:app \
        --host 0.0.0.0 \
        --port "$API_PORT" \
        --log-level info \
        --access-log
fi