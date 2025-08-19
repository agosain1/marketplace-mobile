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

### 2. Run with Docker Compose

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

The application uses these environment variables (configured in docker-compose.yml):

### Database
- `DB_HOST`: Database hostname
- `DB_PORT`: Database port
- `DB_NAME`: Database name
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password

### Authentication
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `JWT_ALGORITHM`: Algorithm for JWT signing

### Email (for verification)
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port
- `SMTP_USER`: Email username
- `SMTP_PASSWORD`: Email password
- `FROM_EMAIL`: From email address

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

## Production Deployment

For production deployment:

1. Update environment variables in `docker-compose.yml`
2. Use proper secrets management
3. Configure reverse proxy (nginx/traefik)
4. Set up SSL certificates
5. Configure backup strategy for database

