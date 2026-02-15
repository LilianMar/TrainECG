.PHONY: help install dev test lint format clean docker-build docker-up docker-down

help:
	@echo "ECG Backend - Available Commands"
	@echo "================================"
	@echo "make install       - Install dependencies"
	@echo "make dev           - Run development server"
	@echo "make test          - Run tests"
	@echo "make lint          - Check code style"
	@echo "make format        - Format code"
	@echo "make clean         - Clean cache and temp files"
	@echo "make docker-build  - Build Docker image"
	@echo "make docker-up     - Start Docker containers"
	@echo "make docker-down   - Stop Docker containers"
	@echo "make setup         - Full setup (install + create env)"

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete! Run 'make dev' to start development server"

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app

lint:
	flake8 app/ tests/
	pylint app/

format:
	black app/ tests/
	isort app/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/

docker-build:
	docker build -t ecg-backend:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f backend

migrate:
	alembic upgrade head

migrate-create:
	@read -p "Enter migration name: " name; \
	alembic revision --autogenerate -m "$$name"
