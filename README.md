an# Marketplace Mobile App

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

## Deployment

### Railway Deployment Options

**Option 1: Monorepo with separate services (recommended)**
- Use: `railway.json` (root) + individual service configs in `frontend/railway.json` and `api/railway.json`
- Railway automatically detects services in subdirectories
- Each service has its own config
- Delete: `railway-backend.json` and `railway-frontend.json`

**Option 2: Manual deployment script approach (current setup)**
- Use: `railway-backend.json` and `railway-frontend.json`
- The `railway-deploy.sh` script copies these to `railway.json` when deploying
- Delete: root `railway.json`

### Current Deployment Workflow

The deployment script uses Option 2:

```bash
# Copy backend config and deploy
cp railway-backend.json railway.json
echo "🔥 Deploying backend..."
railway up --detach

# Copy frontend config and deploy
cp railway-frontend.json railway.json
echo "🔥 Deploying frontend..."
railway up --detach
```

### Current Setup
- `railway-backend.json` - Used by deployment script for API service
- `railway-frontend.json` - Used by deployment script for frontend service
- `railway-deploy.sh` manages copying the right config to `railway.json` during deployment

This matches the existing deployment workflow and handles the moved frontend src folder structure.
