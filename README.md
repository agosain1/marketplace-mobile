# Marketplace Mobile App

A Quasar-based marketplace application with FastAPI backend

## Install the dependencies

```bash
yarn
# or
npm install
```

### Start the app in development mode (hot-code reloading, error reporting, etc.)

```bash
quasar dev
```

### Lint the files

```bash
yarn lint
# or
npm run lint
```

### Format the files

```bash
yarn format
# or
npm run format
```

### Build the app for production

```bash
quasar build
```

### Customize the configuration

See [Configuring quasar.config.js](https://v2.quasar.dev/quasar-cli-vite/quasar-config-js).

## Project Structure

```
marketplace-mobile/
├── api/                        # FastAPI backend
│   ├── Dockerfile              # Backend Docker config
│   ├── requirements.txt        # Python dependencies
│   ├── main.py                 # FastAPI main app
│   ├── routers/                # API routes
│   └── railway-start.sh        # Railway startup script
├── frontend/                   # Quasar frontend
│   ├── Dockerfile              # Frontend Docker config
│   ├── package.json            # Node.js dependencies
│   ├── src/                    # Frontend source code
│   ├── default.conf            # Nginx configuration
│   └── nginx-entrypoint.sh     # Nginx startup script
├── Dockerfile.backend          # Railway backend Docker config
├── Dockerfile.frontend         # Railway frontend Docker config
├── railway-backend.json        # Railway backend service config
└── railway-frontend.json       # Railway frontend service config
```

## Railway Deployment

### Setup

1. **Create Railway Project**: Go to [Railway](https://railway.app) and create a new project
2. **Connect Repository**: Link your GitHub repository
3. **Create Services**: You'll need two services - one for backend, one for frontend

### Backend Service Configuration

1. **Service Settings**:
   - Branch: Select your deployment branch (e.g., `FixDocker` or `main`)
   - Root Directory: Leave empty (uses repository root)
   - Dockerfile Path: `Dockerfile.backend` (Railway will find this automatically)

2. **Environment Variables** (set in Railway dashboard):
   ```
   SERVICE_TYPE=backend
   DB_HOST=your-database-host
   DB_USER=your-database-user
   DB_PASSWORD=your-database-password
   DB_NAME=your-database-name
   JWT_SECRET_KEY=your-jwt-secret
   AWS_ACCESS_KEY_ID=your-aws-key
   AWS_SECRET_ACCESS_KEY=your-aws-secret
   AWS_REGION=us-west-1
   S3_BUCKET_NAME=your-bucket-name
   SMTP_HOST=smtp.gmail.com
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

### Frontend Service Configuration

1. **Service Settings**:
   - Branch: Same as backend
   - Root Directory: Leave empty
   - Dockerfile Path: `Dockerfile.frontend` (Railway will find this automatically)

2. **Environment Variables** (set in Railway dashboard):
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   VITE_GOOGLE_CLIENT_ID=your-google-client-id
   VITE_MAPBOX_ACCESS_TOKEN=your-mapbox-token
   ```

### Deployment Process

Railway automatically deploys when you push to the selected branch. The deployment uses:

- **Backend**: `Dockerfile.backend` (builds from `api/` directory)
- **Frontend**: `Dockerfile.frontend` (builds from `frontend/` directory)
- **Configuration**: `railway-backend.json` and `railway-frontend.json`

### Important Notes

- **SERVICE_TYPE**: Set `SERVICE_TYPE=backend` for backend service only. Frontend defaults to frontend behavior.
- **Sensitive Data**: Always set credentials via Railway dashboard, never in code
- **Branch Deployment**: Railway deploys automatically from your selected branch
- **Custom Domains**: Configure custom domains in Railway dashboard if needed

## Docker Configuration

### Local Development

For local development, use the Dockerfiles in their respective directories:

```bash
# Backend
cd api
docker build -t marketplace-backend .

# Frontend
cd frontend
docker build -t marketplace-frontend .
```

### Railway Deployment

Railway uses the root-level Dockerfiles:

- **`Dockerfile.backend`**: Copies from `api/` directory to `/app` in container
- **`Dockerfile.frontend`**: Copies from `frontend/` directory and builds the Quasar app

These root-level Dockerfiles are specifically configured for Railway's build context and automatically handle the monorepo structure.

### Key Differences

| Environment | Backend Dockerfile | Frontend Dockerfile | Build Context |
|-------------|-------------------|---------------------|---------------|
| Local Dev   | `api/Dockerfile` | `frontend/Dockerfile` | Directory-specific |
| Railway     | `Dockerfile.backend` | `Dockerfile.frontend` | Repository root |

### Troubleshooting

- **Module not found errors**: Ensure `PYTHONPATH=/app` is set in backend containers
- **File not found errors**: Check that COPY commands use correct source paths
- **Build context issues**: Railway builds from repository root, so all paths are relative to root
