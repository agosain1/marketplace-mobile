#!/bin/bash

# Railway service startup script that uses SERVICE_TYPE to determine deployment
SERVICE_TYPE=${SERVICE_TYPE:-backend}

if [ "$SERVICE_TYPE" = "frontend" ]; then
    echo "Starting frontend service with nginx..."
    exec nginx -g 'daemon off;'
elif [ "$SERVICE_TYPE" = "backend" ]; then
    echo "Starting backend service with FastAPI..."
    # Load environment variables
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Set default values
    API_HOST=${API_HOST:-"0.0.0.0"}
    API_PORT=${PORT:-8000}
    
    # Start the FastAPI application
    exec uvicorn api.main:app --host "$API_HOST" --port "$API_PORT"
else
    echo "Invalid SERVICE_TYPE: $SERVICE_TYPE. Must be 'frontend' or 'backend'"
    exit 1
fi