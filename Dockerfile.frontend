# Build stage
FROM node:20-alpine as build-stage

# Accept build argument for API URL (set via Railway environment variable)
ARG VITE_API_URL
ARG VITE_GOOGLE_CLIENT_ID
ARG VITE_MAPBOX_ACCESS_TOKEN

# Set working directory
WORKDIR /app

# Copy package files and quasar config
COPY package*.json ./
COPY quasar.config.js ./
COPY index.html ./

# Copy source code
COPY . .

# Install dependencies
RUN sed -i 's|../node_modules/.bin/|./node_modules/.bin/|g' package.json && npm ci

# Set environment variable for build
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_GOOGLE_CLIENT_ID=$VITE_GOOGLE_CLIENT_ID
ENV VITE_MAPBOX_ACCESS_TOKEN=$VITE_MAPBOX_ACCESS_TOKEN

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine as production-stage

# Copy built files from build stage
COPY --from=build-stage /app/dist/spa /usr/share/nginx/html

# Copy nginx configuration to conf.d directory
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy and setup entrypoint script for Railway's dynamic PORT
COPY nginx-entrypoint.sh /nginx-entrypoint.sh
RUN chmod +x /nginx-entrypoint.sh

# Expose port
EXPOSE 80

# Start nginx with dynamic port
CMD ["/nginx-entrypoint.sh"]