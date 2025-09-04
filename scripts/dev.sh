#!/bin/bash
# WIZARD-2.1 Development Script
# Convenient commands for development tasks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if virtual environment is activated
check_venv() {
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Virtual environment not activated!"
        if [[ -d "venv" ]]; then
            print_status "Activating virtual environment..."
            source venv/bin/activate
        else
            print_error "Virtual environment not found! Run: make venv"
            exit 1
        fi
    fi
}

# Function to clear logs
clear_logs() {
    print_status "Clearing log files..."
    python scripts/clear_logs.py
}

# Function to clear cache
clear_cache() {
    print_status "Clearing cache files..."
    python scripts/clear_cache.py
}

# Function to start application
start_app() {
    print_status "Starting WIZARD-2.1 application..."
    python scripts/start_app.py
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    pytest tests/ -v
}

# Function to run linting
run_lint() {
    print_status "Running linting..."
    pylint src/
    mypy src/
}

# Function to format code
format_code() {
    print_status "Formatting code..."
    black src/ tests/
    isort src/ tests/
}

# Function to show help
show_help() {
    echo "WIZARD-2.1 Development Script"
    echo "============================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the application"
    echo "  clean       Clear logs and cache"
    echo "  logs        Clear log files only"
    echo "  cache       Clear cache files only"
    echo "  test        Run tests"
    echo "  lint        Run linting"
    echo "  format      Format code"
    echo "  dev         Clean and start (development cycle)"
    echo "  help        Show this help message"
    echo ""
}

# Main script logic
case "${1:-help}" in
    "start")
        check_venv
        start_app
        ;;
    "clean")
        clear_logs
        clear_cache
        print_success "Cleanup completed!"
        ;;
    "logs")
        clear_logs
        ;;
    "cache")
        clear_cache
        ;;
    "test")
        check_venv
        run_tests
        ;;
    "lint")
        check_venv
        run_lint
        ;;
    "format")
        check_venv
        format_code
        ;;
    "dev")
        check_venv
        clear_logs
        clear_cache
        start_app
        ;;
    "help"|*)
        show_help
        ;;
esac
