#!/bin/bash

echo "🔧 Setting up FixDocker environment for Railway deployment..."

# Check if we're in the right directory
if [ ! -f "backend/.env.railway.example" ]; then
    echo "❌ Error: Must run from the marketplace-mobile root directory"
    exit 1
fi

# Set Railway project
railway login --browserless
echo "🔗 Linking to Railway project..."
railway link

# Backend environment variables
echo "📝 Setting backend environment variables..."

# Database variables
railway variables set DB_USER=marketplace
railway variables set DB_PASSWORD=marketplace123
railway variables set DB_NAME=marketplace_db
railway variables set DB_HOST=postgres-staging
railway variables set DB_PORT=5432
railway variables set DATABASE_URL='postgresql://marketplace:marketplace123@postgres-staging:5432/marketplace_db'

# JWT and security
railway variables set JWT_SECRET_KEY='your-super-secret-jwt-key-change-in-production'
railway variables set JWT_ALGORITHM=HS256
railway variables set ACCESS_TOKEN_EXPIRE_MINUTES=30
railway variables set VITE_API_BASE_URL='https://marketplace-backend-staging.railway.app'

# Braintree settings (sandbox)
railway variables set BT_ENVIRONMENT=sandbox
railway variables set BT_MERCHANT_ID=7px9sktdg9vhfcpp
railway variables set BT_PUBLIC_KEY=swjv5gk7hrxbh8my
railway variables set BT_PRIVATE_KEY=09faa2f7b93e436e826bb78f616e1bb9

# Google Maps
railway variables set REACT_APP_GOOGLE_MAPS_API_KEY=AIzaSyAe2pJ1jNde-sJYr4rTbiMR7yUnKiJnpe8

# Email variables - IMPORTANT: Set these values in Railway dashboard for security
echo "⚠️  Email credentials should be set via Railway dashboard for security"
echo "    Required variables:"
echo "    - SMTP_HOST (e.g. smtp.gmail.com)"
echo "    - SMTP_PORT (e.g. 587)"
echo "    - SMTP_USER (your email)"
echo "    - SMTP_PASSWORD (your app password)"
echo "    - FROM_EMAIL (sender email)"

# AWS S3 variables - IMPORTANT: Set these values in Railway dashboard for security
echo "⚠️  AWS credentials should be set via Railway dashboard for security"
echo "    Required variables:"
echo "    - AWS_ACCESS_KEY_ID"
echo "    - AWS_SECRET_ACCESS_KEY"
echo "    - AWS_REGION (e.g. us-west-1)"
echo "    - S3_BUCKET_NAME"

# Copy FixDocker backend config and deploy
cp railway-backend-fixdocker.json railway.json
echo "🔥 Deploying FixDocker backend..."
railway up --detach

# Switch to frontend for FixDocker
echo "📝 Setting frontend environment variables..."
railway variables set VITE_API_BASE_URL='https://marketplace-backend-staging.railway.app'
railway variables set VITE_GOOGLE_MAPS_API_KEY=AIzaSyAe2pJ1jNde-sJYr4rTbiMR7yUnKiJnpe8

# Deploy frontend
cp railway-frontend-fixdocker.json railway.json
echo "🔥 Deploying FixDocker frontend..."
railway up --detach

# Deploy database
cp railway-database-fixdocker.json railway.json
echo "🔥 Deploying database for FixDocker..."
railway up --detach

echo "✅ FixDocker deployment initiated!"
echo ""
echo "📌 IMPORTANT: Remember to set email and AWS credentials in Railway dashboard!"
echo ""
echo "🔗 Check deployment status at: https://railway.app/dashboard"
echo ""
echo "📱 Once deployed, your apps will be available at:"
echo "   - Backend: https://marketplace-backend-staging.railway.app"
echo "   - Frontend: https://marketplace-frontend-staging.railway.app"