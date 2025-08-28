#!/bin/sh
# Railway provides PORT env variable, default to 80 if not set
PORT=${PORT:-80}
echo "Starting nginx on port $PORT"

# Replace listen 80 with the actual PORT from Railway
sed -i "s/listen 80;/listen $PORT;/g" /etc/nginx/conf.d/default.conf
sed -i "s/listen \[::\]:80;/listen [::]:$PORT;/g" /etc/nginx/conf.d/default.conf

# Start nginx
nginx -g 'daemon off;'