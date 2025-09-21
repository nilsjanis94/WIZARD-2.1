# WIZARD-2.1 Development Makefile
# Provides convenient commands for development tasks

.PHONY: help install run clean logs cache test test-unit test-integration test-ui test-coverage test-all test-fast lint format format-check import-sort import-check type-check style-check security-check quality docs dev setup

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
	@echo "  test-all    Run unit + integration tests"
	@echo "  test-coverage Run tests with coverage report"
	@echo "  test-fast   Run fast tests (exclude slow tests)"
	@echo ""
	@echo "Code Quality:"
	@echo "  quality     Run all code quality checks"
	@echo "  lint        Run linting (pylint + mypy)"
	@echo "  format      Format code (black + isort)"
	@echo "  format-check Check if code is formatted"
	@echo "  import-sort Sort imports (isort)"
	@echo "  import-check Check import sorting"
	@echo "  type-check  Run type checking (mypy)"
	@echo "  style-check Run style checking (flake8)"
	@echo "  security-check Run security scanning (bandit)"
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

# Test commands
test:
	@echo "Running tests..."
	python -m pytest tests/ -v

test-unit:
	@echo "Running unit tests..."
	python -m pytest tests/unit/ -v -m unit

test-integration:
	@echo "Running integration tests..."
	python -m pytest tests/integration/ -v -m integration

test-ui:
	@echo "Running UI tests..."
	python -m pytest tests/ui/ -v -m ui

test-coverage:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-all:
	@echo "Running all tests (unit + integration)..."
	python -m pytest tests/unit/ tests/integration/ -v

test-fast:
	@echo "Running fast tests (excluding slow tests)..."
	python -m pytest tests/ -v -m "not slow"

# Code quality commands
quality: format-check import-check style-check lint security-check
	@echo "✅ All code quality checks completed!"

format:
	@echo "Formatting code..."
	python -m black src/ tests/
	python -m isort src/ tests/

format-check:
	@echo "Checking code formatting..."
	python -m black --check --diff src/ tests/ || (echo "❌ Code formatting issues found. Run 'make format' to fix."; exit 1)

import-sort:
	@echo "Sorting imports..."
	python -m isort src/ tests/

import-check:
	@echo "Checking import sorting..."
	python -m isort --check-only --diff src/ tests/ || (echo "❌ Import sorting issues found. Run 'make import-sort' to fix."; exit 1)

type-check:
	@echo "Running type checking..."
	python -m mypy src/ --ignore-missing-imports --no-strict-optional

style-check:
	@echo "Running style checking..."
	python -m flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics

security-check:
	@echo "Running security scanning..."
	python -m bandit -r src/ -f json -o security-report.json
	@echo "Security report saved to security-report.json"

lint:
	@echo "Running linting..."
	python -m pylint src/ tests/ --rcfile=.pylintrc || echo "⚠️  Pylint found issues (warnings)"
	python -m mypy src/ --ignore-missing-imports --no-strict-optional || echo "⚠️  MyPy found type issues (warnings)"

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
