.PHONY: help setup install test lint format build start stop clean deploy

PYTHON := python3
PIP := pip3
DOCKER := docker
DOCKER_COMPOSE := docker-compose

help:
	@echo "CarbonTrack Pro - Available Commands:"
	@echo "  setup          - Initial project setup"
	@echo "  install        - Install dependencies"
	@echo "  test           - Run tests"
	@echo "  lint           - Run code linting"
	@echo "  format         - Format code"
	@echo "  build          - Build Docker images"
	@echo "  start          - Start all services"
	@echo "  stop           - Stop all services"
	@echo "  clean          - Clean temporary files"
	@echo "  deploy         - Deploy to production"

setup:
	@echo "Setting up CarbonTrack Pro..."
	$(PYTHON) -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	cp .env.example .env
	@echo "Setup complete! Edit .env file with your configuration."

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

test:
	@echo "Running tests..."
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=html
	@echo "Tests complete! Coverage report in htmlcov/"

lint:
	@echo "Running linting..."
	$(PYTHON) -m flake8 src/ tests/
	$(PYTHON) -m mypy src/
	@echo "Linting complete!"

format:
	@echo "Formatting code..."
	$(PYTHON) -m black src/ tests/
	$(PYTHON) -m isort src/ tests/
	@echo "Formatting complete!"

build:
	@echo "🏗️ Building Docker images..."
	$(DOCKER_COMPOSE) build
	@echo "Build complete!"

start:
	@echo "Starting services..."
	$(DOCKER_COMPOSE) up -d
	@echo "Services started!"
	@echo "Airflow UI: http://localhost:8080"
	@echo "Spark UI: http://localhost:8081"

stop:
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) down
	@echo "Services stopped!"

clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	$(DOCKER) system prune -f
	@echo "Cleanup complete!"

deploy:
	@echo "Deploying to production..."
	./scripts/deploy.sh
	@echo "Deployment complete!"

run-pipeline:
	@echo "Starting emission monitoring pipeline..."
	$(PYTHON) -m src.main producer &
	sleep 5
	$(PYTHON) -m src.main processor &
	@echo "Pipeline running! Press Ctrl+C to stop."

logs:
	$(DOCKER_COMPOSE) logs -f

status:
	$(DOCKER_COMPOSE) ps
	@echo "\nService Status:"
	@curl -s http://localhost:8080/health || echo "❌ Airflow down"
	@curl -s http://localhost:8081 || echo "❌ Spark down"
