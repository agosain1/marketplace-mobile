# Multi-stage build for both frontend and backend
FROM node:18-alpine AS frontend-build

# Build frontend - copy everything first, then build
WORKDIR /app
COPY package*.json ./
COPY quasar.config.js ./
COPY . .
RUN npm install
RUN npm run build

# Python backend stage  
FROM python:3.11-slim AS backend-base

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY api/ ./api/
COPY .env* ./

# Final runtime stage
FROM python:3.11-slim AS runtime

# Install nginx for potential frontend service
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python environment
COPY --from=backend-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-base /usr/local/bin /usr/local/bin

# Copy backend code and dependencies
COPY --from=backend-base /app ./

# Copy frontend build
COPY --from=frontend-build /app/dist/spa /usr/share/nginx/html

# Copy nginx config if it exists, otherwise create default
RUN echo 'events { worker_connections 1024; } \
http { \
    include /etc/nginx/mime.types; \
    default_type application/octet-stream; \
    server { \
        listen 80; \
        location / { \
            root /usr/share/nginx/html; \
            try_files $uri $uri/ /index.html; \
        } \
    } \
}' > /etc/nginx/nginx.conf

# Copy startup script
COPY railway-start-service.sh /app/railway-start-service.sh
RUN chmod +x /app/railway-start-service.sh

# Expose ports
EXPOSE 8000 80

# Use our service startup script
CMD ["/app/railway-start-service.sh"]