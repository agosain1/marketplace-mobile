# Marketplace Mobile - Docker Setup

This document explains how to run the Marketplace Mobile application using Docker.

## Prerequisites

- Docker and Docker Compose installed on your system
- Git (to clone the repository)

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd marketplace-mobile
```

### 2. Setup Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual values
nano .env  # or use your preferred editor
```

**Important**: Never commit your `.env` file to git. It contains sensitive information.

### 3. Run with Docker Compose

#### Production Mode
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

#### Development Mode (with hot reload)
```bash
# Start only database and backend with hot reload
docker-compose -f docker-compose.dev.yml up -d

# Run frontend separately for development
npm install
npm run dev
```

## Services

The application consists of three main services:

### 1. PostgreSQL Database
- **Container**: `marketplace-db`
- **Port**: `5432`
- **Database**: `marketplace`
- **User**: `postgres`
- **Password**: `postgres`

### 2. FastAPI Backend
- **Container**: `marketplace-backend`
- **Port**: `8000`
- **Health Check**: `http://localhost:8000/docs`
- **API Documentation**: `http://localhost:8000/docs`

### 3. Vue.js Frontend (Production only)
- **Container**: `marketplace-frontend`
- **Port**: `3000`
- **URL**: `http://localhost:3000`

## Environment Variables

The application uses environment variables for configuration. These are loaded from the `.env` file.

### Required Variables (see .env.example):

**Frontend:**
- `VITE_API_URL`: API base URL (e.g., http://localhost:8000/)

**Database:**
- `DB_HOST`: Database hostname
- `DB_PORT`: Database port (usually 5432)
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password

**Authentication:**
- `JWT_SECRET_KEY`: Secret key for JWT tokens (generate a strong random key)
- `JWT_ALGORITHM`: Algorithm for JWT signing (HS256 recommended)

**Email (for verification):**
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port
- `SMTP_USER`: Email username
- `SMTP_PASSWORD`: Email app password (not regular password)
- `FROM_EMAIL`: From email address

### Security Notes:
- Never commit your `.env` file to version control
- Use strong, unique passwords and secret keys
- For production, consider using Docker secrets or a secret management service
- Generate JWT secret with: `openssl rand -hex 32`

## Development Workflow

### Backend Development
1. Start database: `docker-compose -f docker-compose.dev.yml up postgres -d`
2. Start backend: `docker-compose -f docker-compose.dev.yml up backend -d`
3. Backend will hot-reload on file changes

### Frontend Development
1. Install dependencies: `npm install`
2. Start dev server: `npm run dev`
3. Frontend will be available at `http://localhost:9000` (Quasar default)

### Database Access
```bash
# Connect to PostgreSQL
docker exec -it marketplace-db-dev psql -U postgres -d marketplace

# View database logs
docker logs marketplace-db-dev
```

## Useful Commands

### View Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### Rebuild Services
```bash
# Rebuild all
docker-compose build

# Rebuild specific service
docker-compose build backend
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (careful - this deletes data!)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## Troubleshooting

### Database Connection Issues
1. Ensure PostgreSQL container is healthy: `docker-compose ps`
2. Check database logs: `docker logs marketplace-db`
3. Verify environment variables in docker-compose.yml

### Backend Issues
1. Check backend logs: `docker logs marketplace-backend`
2. Verify database connection
3. Ensure all required environment variables are set

### Frontend Issues
1. Check if backend is accessible at `http://localhost:8000`
2. Verify `VITE_API_URL` environment variable
3. Check browser console for errors

### Permission Issues
```bash
# Fix file permissions (if needed)
sudo chown -R $USER:$USER .
```

## Security Best Practices

### Environment Variables
1. **Never commit `.env` files** - they're in `.gitignore` for a reason
2. **Use strong secrets** - generate JWT keys with `openssl rand -hex 32`
3. **Rotate credentials regularly** - especially in production
4. **Use app passwords** - for email, not your regular password

### Production Deployment
1. **Use Docker secrets** or cloud secret management (AWS Secrets Manager, etc.)
2. **Configure reverse proxy** with SSL (nginx/traefik)
3. **Set up proper firewall rules**
4. **Enable database SSL connections**
5. **Use non-root users** in containers
6. **Regular security updates** for base images

### Setup for New Developers
```bash
# 1. Clone repo
git clone <repo-url>
cd marketplace-mobile

# 2. Copy environment template
cp .env.example .env

# 3. Ask team lead for actual values to put in .env
# 4. Never commit your .env file!

# 5. Run the application
docker-compose up -d
```

