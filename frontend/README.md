# Unimarket (unimarket-frontend)

Frontend for Unimarket

## Install the dependencies

```bash
yarn
# or
npm install
```

## Sync types for API and data models [TODO: AWAITING BACKEND RESPONSE TYPING]

### API

Makes use of FastAPI's generation of OpenAPI schemas. First, you must start up the backend.

```bash
npx openapi-typescript http://localhost:8000/openapi.json -o src/types/api.d.ts  # replace URL with wherever the backend is served
```

### Data models

All data models needed for frontend are included in OpenAPI schema. No need to introspect the entire database or anything else.

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
