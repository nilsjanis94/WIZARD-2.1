# WIZARD-2.1 Development Makefile
# Provides convenient commands for development tasks

.PHONY: help install run clean logs cache test lint format docs

# Default target
help:
	@echo "WIZARD-2.1 Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install dependencies"
	@echo "  venv        Create virtual environment"
	@echo ""
	@echo "Development:"
	@echo "  run/start   Start the application"
	@echo "  test        Run all tests"
	@echo "  test-unit   Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-ui     Run UI tests only"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  test-fast   Run fast tests (exclude slow tests)"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean       Clean all cache and temp files"
	@echo "  logs        Clear log files"
	@echo "  cache       Clear cache files"
	@echo "  deps        Reinstall dependencies"
	@echo ""
	@echo "Documentation:"
	@echo "  docs        Generate documentation"
	@echo ""

# Setup commands
venv:
	@echo "Creating virtual environment..."
	python -m venv venv
	@echo "Virtual environment created. Activate with:"
	@echo "  source venv/bin/activate  (Unix/macOS)"
	@echo "  venv\\Scripts\\activate     (Windows)"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	@echo "Dependencies installed!"

# Development commands
run:
	@echo "Starting WIZARD-2.1 application..."
	python scripts/start_app.py

start: run
	@echo "Alias for 'run' command"

# Cleanup commands
clean:
	@echo "Performing complete cleanup..."
	python scripts/dev_cleanup.py --all

logs:
	@echo "Clearing log files..."
	python scripts/clear_logs.py

cache:
	@echo "Clearing cache files..."
	python scripts/clear_cache.py

deps:
	@echo "Reinstalling dependencies..."
	python scripts/dev_cleanup.py --deps

# Code quality commands
test:
	@echo "Running tests..."
	pytest tests/ -v

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v -m unit

test-integration:
	@echo "Running integration tests..."
	pytest tests/integration/ -v -m integration

test-ui:
	@echo "Running UI tests..."
	pytest tests/ui/ -v -m ui

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-fast:
	@echo "Running fast tests (excluding slow tests)..."
	pytest tests/ -v -m "not slow"

lint:
	@echo "Running linting..."
	pylint src/
	mypy src/

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/

# Documentation
docs:
	@echo "Generating documentation..."
	sphinx-build -b html docs/ docs/_build/html
	@echo "Documentation generated in docs/_build/html/"

# Quick development cycle
dev: clean run

# Full setup for new developers
setup: venv install
	@echo "Setup complete! Activate venv and run 'make run'"
