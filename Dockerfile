# Multi-stage build for both frontend and backend
FROM node:18-alpine AS frontend-build

# Build frontend
WORKDIR /frontend
COPY package*.json ./
RUN npm install
COPY . .
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

# Nginx stage for serving frontend
FROM nginx:alpine AS frontend-runtime

# Copy built frontend from frontend-build stage
COPY --from=frontend-build /frontend/dist/spa /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Final runtime stage
FROM python:3.11-slim AS runtime

# Install nginx for potential frontend service
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy backend dependencies and code
COPY --from=backend-base /app ./
COPY --from=backend-base /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-base /usr/local/bin /usr/local/bin

# Copy frontend build
COPY --from=frontend-build /frontend/dist/spa /usr/share/nginx/html

# Copy nginx config and startup script
COPY nginx.conf /etc/nginx/nginx.conf
COPY railway-start-service.sh /app/railway-start-service.sh
RUN chmod +x /app/railway-start-service.sh

# Expose ports
EXPOSE 8000 80

# Use our service startup script
CMD ["/app/railway-start-service.sh"]