# AI-Powered Website Builder

<div align="center">

A modern, production-ready website builder that uses AI agents to generate, audit, and deploy websites through natural language input.

[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18.0-blue.svg)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)

</div>

## Overview

This project is a full-stack AI-powered website builder that enables users to create, edit, audit, and deploy websites using natural language descriptions. The system uses a multi-agent architecture powered by Google's Gemini AI to handle different aspects of website creation.

### Key Features

- 🤖 **AI-Powered Generation**: Create websites from natural language descriptions
- 🎨 **Live Preview & Editing**: Real-time WYSIWYG editor with instant preview
- 📊 **Comprehensive Audits**: SEO, accessibility, and performance analysis
- 🎭 **Theme System**: Browse and apply professional design themes
- 🚀 **One-Click Deployment**: Deploy directly to Vercel
- 📱 **Responsive Design**: Mobile-first interface that works on all devices
- ♿ **Accessibility First**: WCAG 2.1 AA compliant with keyboard navigation
- 🔄 **Real-Time Updates**: WebSocket integration for live agent activity
- 📝 **Version History**: Track and restore previous versions
- 🎬 **Smooth Animations**: Polished UI with Framer Motion

## Architecture

The project consists of three main components:

### Frontend (`/frontend`)
- **Tech Stack**: React 18, TypeScript, Vite, ShadCN UI, Framer Motion
- **Purpose**: User interface for website creation and management
- **Documentation**: [Frontend README](./frontend/README.md)

### Backend (`/backend`)
- **Tech Stack**: Python, FastAPI, SQLAlchemy, Celery, Redis
- **Purpose**: API server and AI agent orchestration
- **Documentation**: [Backend README](./backend/README.md)

### Infrastructure (`/infrastructure`)
- **Tech Stack**: Docker, Kubernetes, PostgreSQL, Redis
- **Purpose**: Deployment and orchestration
- **Documentation**: [Infrastructure README](./infrastructure/README.md)

## Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Docker** and Docker Compose (for full stack)
- **PostgreSQL** 14+ (or use Docker)
- **Redis** 7+ (or use Docker)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd website-builder

# Copy environment files
cp .env.example .env.local
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Set your Gemini API key in backend/.env
# GEMINI_API_KEY=your_api_key_here

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
alembic upgrade head

# Set environment variables
export GEMINI_API_KEY=your_api_key_here
export DATABASE_URL=postgresql://user:password@localhost:5432/website_builder
export REDIS_URL=redis://localhost:6379

# Start the server
uvicorn main:app --reload --port 8000

# In another terminal, start Celery worker
celery -A services.celery_app worker --loglevel=info
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env
# Edit .env with your backend URL

# Start development server
npm run dev

# Access at http://localhost:3000
```

## Project Structure

```
.
├── frontend/              # React frontend application
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── lib/          # Utilities and hooks
│   │   └── ...
│   └── package.json
├── backend/              # FastAPI backend application
│   ├── agents/          # AI agent implementations
│   ├── api/             # API endpoints
│   ├── models/          # Database models
│   ├── services/        # Business logic
│   └── requirements.txt
├── infrastructure/       # Deployment configurations
│   ├── k8s/             # Kubernetes manifests
│   └── docker-compose.yml
└── .kiro/               # Kiro specs and documentation
    └── specs/
```

## Documentation

### Getting Started
- [Frontend Setup Guide](./frontend/README.md)
- [Backend Setup Guide](./backend/README.md)
- [Contributing Guidelines](./CONTRIBUTING.md)

### Development Guides
- [Component Documentation](./frontend/src/components/README.md)
- [API Integration Guide](./docs/API_INTEGRATION.md)
- [Accessibility Guide](./docs/ACCESSIBILITY_GUIDE.md)
- [Performance Optimization](./docs/PERFORMANCE_GUIDE.md)

### Security
- [Security Guide](./docs/SECURITY.md) - Comprehensive security documentation
- [Security Implementation](./SECURITY_IMPLEMENTATION.md) - Implementation details
- [Security Quick Reference](./SECURITY_QUICK_REFERENCE.md) - Quick reference guide

### Deployment
- [Deployment Guide](./docs/DEPLOYMENT_GUIDE.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)

### Architecture
- [System Architecture](./docs/ARCHITECTURE.md)
- [Agent System](./backend/agents/README.md)
- [Database Schema](./backend/models/README.md)

## Testing

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e:ui
```

### Backend Tests

```bash
cd backend

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents.py
```

## Environment Variables

### Backend (.env)
```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/website_builder
REDIS_URL=redis://localhost:6379
VERCEL_TOKEN=your_vercel_token
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_DEBUG=true
VITE_ENV=development
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) for details on:

- Code style and standards
- Development workflow
- Testing requirements
- Pull request process
- Code review guidelines

## License

MIT License - see [LICENSE](./LICENSE) for details

## Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs or request features via GitHub Issues
- **Discussions**: Join our community discussions

## Acknowledgments

- Built with [React](https://reactjs.org/) and [FastAPI](https://fastapi.tiangolo.com/)
- UI components from [ShadCN UI](https://ui.shadcn.com/)
- Animations powered by [Framer Motion](https://www.framer.com/motion/)
- AI powered by [Google Gemini](https://deepmind.google/technologies/gemini/)

---

Made with ❤️ by the Website Builder Team
