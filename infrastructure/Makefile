.PHONY: help build up down restart logs clean test migrate seed

# Default target
help:
	@echo "Smart Website Builder - Docker Commands"
	@echo "========================================"
	@echo "make build          - Build all Docker images"
	@echo "make up             - Start all services"
	@echo "make down           - Stop all services"
	@echo "make restart        - Restart all services"
	@echo "make logs           - View logs from all services"
	@echo "make logs-api       - View API logs"
	@echo "make logs-frontend  - View frontend logs"
	@echo "make logs-celery    - View Celery worker logs"
	@echo "make clean          - Remove all containers, volumes, and images"
	@echo "make test           - Run tests"
	@echo "make migrate        - Run database migrations"
	@echo "make shell-api      - Open shell in API container"
	@echo "make shell-db       - Open PostgreSQL shell"
	@echo "make shell-redis    - Open Redis CLI"
	@echo "make ps             - Show running containers"
	@echo "make health         - Check health of all services"

# Build all images
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d
	@echo "Services started. Access:"
	@echo "  Frontend: http://localhost:80"
	@echo "  API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo "  Flower: http://localhost:5555"

# Start services with logs
up-logs:
	docker-compose up

# Stop all services
down:
	docker-compose down

# Restart all services
restart:
	docker-compose restart

# View logs
logs:
	docker-compose logs -f

logs-api:
	docker-compose logs -f api

logs-frontend:
	docker-compose logs -f frontend

logs-celery:
	docker-compose logs -f celery_worker

logs-flower:
	docker-compose logs -f flower

# Clean up everything
clean:
	docker-compose down -v --rmi all --remove-orphans
	@echo "All containers, volumes, and images removed"

# Clean volumes only
clean-volumes:
	docker-compose down -v
	@echo "All volumes removed"

# Run tests
test:
	docker-compose exec api pytest tests/ -v

test-coverage:
	docker-compose exec api pytest tests/ --cov=. --cov-report=html

# Database operations
migrate:
	docker-compose exec api alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	docker-compose exec api alembic revision --autogenerate -m "$$msg"

migrate-downgrade:
	docker-compose exec api alembic downgrade -1

# Shell access
shell-api:
	docker-compose exec api /bin/bash

shell-db:
	docker-compose exec postgres psql -U postgres -d smart_website_builder

shell-redis:
	docker-compose exec redis redis-cli

# Container status
ps:
	docker-compose ps

# Health checks
health:
	@echo "Checking service health..."
	@curl -f http://localhost:8000/health || echo "API: DOWN"
	@curl -f http://localhost:80/health || echo "Frontend: DOWN"
	@docker-compose exec postgres pg_isready -U postgres || echo "PostgreSQL: DOWN"
	@docker-compose exec redis redis-cli ping || echo "Redis: DOWN"

# Development helpers
dev-setup:
	cp .env.example .env.local
	@echo "Created .env.local - please update with your API keys"

dev-reset:
	make down
	make clean-volumes
	make up
	sleep 10
	make migrate
	@echo "Development environment reset complete"

# Production build
prod-build:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Monitoring
stats:
	docker stats

# Backup database
backup-db:
	docker-compose exec postgres pg_dump -U postgres smart_website_builder > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backup created"

# Restore database
restore-db:
	@read -p "Enter backup file path: " file; \
	docker-compose exec -T postgres psql -U postgres smart_website_builder < $$file
