.PHONY: help setup install dev test clean docker-up docker-down migrate format lint

help:
	@echo "Smart Website Builder - Backend Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Initial setup (venv + dependencies)"
	@echo "  make install        - Install dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start development server"
	@echo "  make worker         - Start Celery worker"
	@echo "  make flower         - Start Celery Flower"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start all Docker services"
	@echo "  make docker-down    - Stop all Docker services"
	@echo "  make docker-logs    - View Docker logs"
	@echo "  make docker-build   - Rebuild Docker containers"
	@echo ""
	@echo "Database:"
	@echo "  make migrate        - Run database migrations"
	@echo "  make migration      - Create new migration"
	@echo "  make db-reset       - Reset database (WARNING: deletes all data)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-cov       - Run tests with coverage"
	@echo "  make test-watch     - Run tests in watch mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format         - Format code with black"
	@echo "  make lint           - Lint code with flake8"
	@echo "  make type-check     - Type check with mypy"
	@echo "  make quality        - Run all quality checks"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Remove cache and build files"

setup:
	@echo "Setting up development environment..."
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env file"; fi
	@echo "Setup complete! Edit .env with your configuration."

install:
	. venv/bin/activate && pip install -r requirements.txt

dev:
	. venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

worker:
	. venv/bin/activate && celery -A services.celery_app worker --loglevel=info

flower:
	. venv/bin/activate && celery -A services.celery_app flower --port=5555

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose up -d --build

migrate:
	. venv/bin/activate && alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	. venv/bin/activate && alembic revision --autogenerate -m "$$msg"

db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		. venv/bin/activate && alembic downgrade base && alembic upgrade head; \
		echo "Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

test:
	. venv/bin/activate && pytest

test-cov:
	. venv/bin/activate && pytest --cov=. --cov-report=html --cov-report=term-missing

test-watch:
	. venv/bin/activate && pytest-watch

format:
	. venv/bin/activate && black .

lint:
	. venv/bin/activate && flake8 .

type-check:
	. venv/bin/activate && mypy .

quality: format lint type-check
	@echo "All quality checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"
