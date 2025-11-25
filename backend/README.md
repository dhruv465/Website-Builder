# Smart Website Builder - Backend

Python FastAPI backend for the Smart Multi-Agent Website Builder & Optimizer.

## Project Structure

```
backend/
├── agents/              # AI agent implementations
│   ├── __init__.py
│   ├── base_agent.py   # Base agent class
│   ├── input_agent.py
│   ├── code_generation_agent.py
│   ├── audit_agent.py
│   ├── deployment_agent.py
│   └── memory_agent.py
├── api/                 # FastAPI routes
│   ├── __init__.py
│   ├── workflows.py
│   ├── requirements.py
│   ├── code.py
│   ├── audit.py
│   ├── deploy.py
│   └── sessions.py
├── models/              # Database models
│   ├── __init__.py
│   ├── session.py
│   ├── site.py
│   ├── audit.py
│   └── deployment.py
├── services/            # Business logic services
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── gemini_service.py
│   ├── celery_app.py
│   └── redis_service.py
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── config.py
│   ├── logging.py
│   └── validators.py
├── alembic/             # Database migrations
├── tests/               # Test files
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Docker and Docker Compose (optional)

### Local Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn main:app --reload
```

### Docker Development

1. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

2. Start all services:
```bash
docker-compose up -d
```

3. View logs:
```bash
docker-compose logs -f api
```

4. Run migrations:
```bash
docker-compose exec api alembic upgrade head
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Monitoring

- Celery Flower: http://localhost:5555
- API Health: http://localhost:8000/health

## Environment Variables

See `.env.example` for all available configuration options.

## Architecture

This backend implements a multi-agent architecture where specialized agents handle different aspects of website creation:

- **Input Agent**: Parses natural language requirements
- **Code Generation Agent**: Generates HTML/CSS/JS code
- **Audit Agent**: Evaluates SEO, accessibility, and performance
- **Deployment Agent**: Deploys to Vercel
- **Memory Agent**: Manages session persistence

All agents are coordinated by the **Agent Orchestrator** which manages workflow execution, error handling, and state management.
