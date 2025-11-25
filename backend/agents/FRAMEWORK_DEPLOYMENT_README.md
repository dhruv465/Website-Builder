# Framework-Specific Deployment Support

This document describes the framework-specific deployment support added to the Smart Website Builder platform.

## Overview

The deployment system now supports multiple frontend frameworks including:
- **Vanilla HTML/CSS/JS** - Static HTML sites
- **React** - Component-based UI with Vite
- **Vue** - Progressive framework with Vite
- **Next.js** - React framework with SSR/SSG
- **Svelte** - Reactive framework with Vite/SvelteKit

## Architecture

### Framework Configuration (`framework_configs.py`)

The `framework_configs.py` module provides centralized configuration for all supported frameworks:

```python
from agents.framework_configs import Framework, get_framework_config

# Get configuration for a framework
config = get_framework_config(Framework.REACT)
print(config.build_command)  # "npm run build"
print(config.output_directory)  # "dist"
```

Each framework configuration includes:
- **Build command** - Command to build the project (e.g., `npm run build`)
- **Output directory** - Directory containing build output (e.g., `dist`)
- **Install command** - Command to install dependencies (e.g., `npm install`)
- **Dev command** - Command to run development server
- **Environment variables** - Default environment variables
- **Vercel configuration** - Framework-specific Vercel settings
- **Required files** - Files that must be present for deployment

### Deployment Agent Updates

The `DeploymentAgent` has been updated to:

1. **Accept framework parameter** - Deployments now specify which framework to use
2. **Validate framework files** - Ensures required files are present (e.g., `package.json` for React)
3. **Configure Vercel projects** - Sets up framework-specific build settings
4. **Deploy framework files** - Handles multi-file deployments for framework projects
5. **Store framework metadata** - Tracks which framework was used for each deployment

### Database Schema

The `deployments` table has been extended with:
- `framework` (String) - Framework used for the deployment
- `build_config` (JSON) - Build configuration used

Migration: `2024_11_16_1800-004_add_framework_to_deployments.py`

### API Updates

The deployment API (`/api/deploy`) now accepts:

**Request:**
```json
{
  "html_code": "...",           // For vanilla sites
  "files": {                    // For framework sites
    "package.json": "...",
    "src/App.tsx": "...",
    "index.html": "..."
  },
  "framework": "react",         // Framework to use
  "environment_variables": {    // Optional env vars
    "VITE_API_URL": "https://api.example.com"
  },
  "site_name": "my-site",
  "session_id": "...",
  "project_id": "..."           // For updates
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://my-site.vercel.app",
  "framework": "react",
  "build_config": {
    "buildCommand": "npm run build",
    "outputDirectory": "dist"
  },
  "build_time": 15000,
  "deployment_id": "...",
  "project_id": "..."
}
```

## Framework-Specific Features

### React Deployment

- **Build tool**: Vite
- **Output**: `dist/` directory
- **Routing**: SPA routing configured for client-side navigation
- **Environment**: `NODE_ENV=production`
- **Security headers**: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection

### Vue Deployment

- **Build tool**: Vite
- **Output**: `dist/` directory
- **Routing**: SPA routing configured for Vue Router
- **Environment**: `NODE_ENV=production`
- **Security headers**: Same as React

### Next.js Deployment

- **Build tool**: Next.js native
- **Output**: `.next/` directory
- **Routing**: Native Next.js routing (no custom config needed)
- **Features**: SSR, SSG, API routes, metadata
- **Environment**: `NODE_ENV=production`
- **Security headers**: Same as React

### Svelte Deployment

- **Build tool**: Vite or SvelteKit
- **Output**: `dist/` or `build/` directory
- **Routing**: SPA routing configured for SvelteKit
- **Environment**: `NODE_ENV=production`
- **Security headers**: Same as React

## Usage Examples

### Deploying a React App

```python
from agents.deployment_agent import deployment_agent, DeploymentInput
from agents.base_agent import AgentContext

# Prepare files
files = {
    "package.json": json.dumps({
        "name": "my-react-app",
        "dependencies": {
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        },
        "scripts": {
            "build": "vite build",
            "dev": "vite"
        }
    }),
    "index.html": "<!DOCTYPE html>...",
    "src/main.tsx": "import React from 'react'...",
    "src/App.tsx": "export default function App() {...}",
    "vite.config.ts": "import { defineConfig } from 'vite'..."
}

# Create deployment input
input_data = DeploymentInput(
    files=files,
    framework="react",
    site_name="my-react-app",
    environment_variables={
        "VITE_API_URL": "https://api.example.com"
    }
)

# Execute deployment
context = AgentContext(session_id="...", workflow_id="...")
result = await deployment_agent.execute(input_data, context)

print(f"Deployed to: {result.deployment_metadata.url}")
print(f"Framework: {result.deployment_metadata.framework}")
```

### Deploying a Next.js App

```python
files = {
    "package.json": json.dumps({
        "name": "my-nextjs-app",
        "dependencies": {
            "next": "^14.0.0",
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        },
        "scripts": {
            "build": "next build",
            "dev": "next dev"
        }
    }),
    "app/layout.tsx": "export default function RootLayout({children}) {...}",
    "app/page.tsx": "export default function Home() {...}",
    "next.config.js": "module.exports = {...}"
}

input_data = DeploymentInput(
    files=files,
    framework="nextjs",
    site_name="my-nextjs-app"
)

result = await deployment_agent.execute(input_data, context)
```

## Vercel Configuration

Each framework deployment includes a `vercel.json` file with:

1. **Routing rules** - For SPA frameworks (React, Vue, Svelte)
2. **Security headers** - X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
3. **Build settings** - Build command, output directory, install command

Example `vercel.json` for React:
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "routes": [
    {
      "src": "/[^.]+",
      "dest": "/",
      "status": 200
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        }
      ]
    }
  ]
}
```

## Deployment Metrics

Framework-specific metrics are tracked for each deployment:
- Framework used
- Build time
- Build configuration
- Success/failure rates by framework
- Environment variables used

These metrics are stored in the database and can be queried via the API:

```bash
GET /api/deploy/history/{site_id}
```

Response includes framework information for each deployment.

## Migration Guide

### Existing Deployments

Existing vanilla HTML deployments will continue to work. The `framework` field defaults to `"vanilla"` for backward compatibility.

### Updating to Framework-Based Deployment

To update an existing vanilla site to use a framework:

1. Generate framework-specific files (package.json, components, etc.)
2. Call the deployment API with `framework` parameter
3. Provide `files` instead of `html_code`
4. Include `project_id` to update the existing project

## Testing

To test framework deployments:

```bash
# Run unit tests
pytest backend/tests/test_deployment_agent.py -v

# Test specific framework
pytest backend/tests/test_deployment_agent.py::test_react_deployment -v
```

## Future Enhancements

Potential future improvements:
- Support for additional frameworks (Angular, Nuxt, Astro)
- Custom build commands per deployment
- Framework version detection and validation
- Automatic dependency updates
- Build optimization suggestions
- Framework-specific performance monitoring

## Troubleshooting

### Common Issues

**Issue**: Deployment fails with "Missing required files"
**Solution**: Ensure all required files for the framework are included (e.g., `package.json` for React)

**Issue**: Build fails on Vercel
**Solution**: Check that build command and output directory are correct for your framework

**Issue**: SPA routing not working
**Solution**: Verify that `vercel.json` includes routing rules for client-side navigation

**Issue**: Environment variables not available
**Solution**: Pass `environment_variables` in the deployment request

## References

- [Vercel Build Configuration](https://vercel.com/docs/build-step)
- [Vercel Framework Detection](https://vercel.com/docs/frameworks)
- [React Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [Next.js on Vercel](https://nextjs.org/docs/deployment)
- [Vue Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [Svelte Deployment Guide](https://kit.svelte.dev/docs/adapter-vercel)
