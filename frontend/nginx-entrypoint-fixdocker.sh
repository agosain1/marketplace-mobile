#!/bin/sh
# Railway entrypoint for FixDocker branch frontend testing
# Railway provides PORT env variable, default to 80 if not set
PORT=${PORT:-80}
echo "Starting nginx on port $PORT (FixDocker Branch)"

# Replace listen 80 with the actual PORT from Railway
sed -i "s/listen 80;/listen $PORT;/g" /etc/nginx/conf.d/default.conf
sed -i "s/listen \[::\]:80;/listen [::]:$PORT;/g" /etc/nginx/conf.d/default.conf

# Log nginx configuration for debugging
echo "Nginx configuration:"
cat /etc/nginx/conf.d/default.conf

# Test nginx configuration
nginx -t

# Start nginx
echo "Starting nginx daemon..."
nginx -g 'daemon off;'