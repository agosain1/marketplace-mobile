#!/bin/bash

# Railway-optimized startup script for FixDocker branch testing
set -e

echo "=== Marketplace Backend Railway Startup (FixDocker Branch) ==="
echo "PORT: ${PORT:-8000}"
echo "ENVIRONMENT: ${ENVIRONMENT:-production}"
echo "BRANCH: FixDocker"

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Use Railway's PORT environment variable or default to 8000
API_PORT=${PORT:-8000}
echo "Starting FastAPI on port: $API_PORT"

# Determine the app module path based on file layout (FixDocker branch specific logic)
APP_MODULE="api.main:app"
if [ -f "./main.py" ]; then
  APP_MODULE="main:app"
  echo "Using root-level main.py module"
elif [ -f "./api/main.py" ]; then
  echo "Using api/main.py module"
else
  echo "ERROR: No main.py found in expected locations" >&2
  ls -la
  exit 1
fi

echo "App module: $APP_MODULE"

# Start the application with Railway's dynamic port
if [ "$ENVIRONMENT" = "development" ]; then
    echo "Running in development mode with auto-reload"
    exec uvicorn "$APP_MODULE" \
        --host 0.0.0.0 \
        --port "$API_PORT" \
        --reload \
        --log-level debug
else
    echo "Running in production mode (FixDocker branch)"
    exec uvicorn "$APP_MODULE" \
        --host 0.0.0.0 \
        --port "$API_PORT" \
        --log-level info \
        --access-log \
        --workers 1
fi