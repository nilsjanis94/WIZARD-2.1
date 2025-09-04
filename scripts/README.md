# WIZARD-2.1 Development Scripts

This directory contains development scripts for the WIZARD-2.1 application.

## Available Scripts

### Python Scripts

#### `clear_logs.py`
Clears all log files from the logs directory.

```bash
python scripts/clear_logs.py
```

#### `clear_cache.py`
Clears all cache files including:
- `__pycache__` directories
- `.pyc` files
- Build directories (`build`, `dist`)
- IDE cache files (`.pytest_cache`, `.mypy_cache`)
- OS specific files (`.DS_Store`, `Thumbs.db`)

```bash
python scripts/clear_cache.py
```

#### `start_app.py`
Starts the WIZARD-2.1 application with proper environment setup:
- Checks virtual environment
- Installs dependencies if needed
- Starts the application

```bash
python scripts/start_app.py
```

#### `dev_cleanup.py`
Comprehensive cleanup script with options:

```bash
# Clear all (logs, cache, temp files)
python scripts/dev_cleanup.py --all

# Clear specific items
python scripts/dev_cleanup.py --logs
python scripts/dev_cleanup.py --cache
python scripts/dev_cleanup.py --temp
python scripts/dev_cleanup.py --deps
```

### Shell Scripts

#### `dev.sh`
Convenient shell script for development tasks:

```bash
# Make executable
chmod +x scripts/dev.sh

# Available commands
./scripts/dev.sh start      # Start the application
./scripts/dev.sh clean      # Clear logs and cache
./scripts/dev.sh logs       # Clear log files only
./scripts/dev.sh cache      # Clear cache files only
./scripts/dev.sh test       # Run tests
./scripts/dev.sh lint       # Run linting
./scripts/dev.sh format     # Format code
./scripts/dev.sh dev        # Clean and start (development cycle)
./scripts/dev.sh help       # Show help
```

## Makefile Commands

The project includes a Makefile for easy development:

```bash
# Setup
make venv        # Create virtual environment
make install     # Install dependencies

# Development
make run         # Start the application
make test        # Run tests
make lint        # Run linting
make format      # Format code

# Cleanup
make clean       # Clean all cache and temp files
make logs        # Clear log files
make cache       # Clear cache files
make deps        # Reinstall dependencies

# Documentation
make docs        # Generate documentation

# Quick development cycle
make dev         # Clean and run
```

## Usage Examples

### Daily Development Workflow

```bash
# Start development session
make clean
make run

# Or use the shell script
./scripts/dev.sh dev
```

### Quick Cleanup

```bash
# Clear everything
make clean

# Or use individual scripts
python scripts/clear_logs.py
python scripts/clear_cache.py
```

### Application Testing

```bash
# Start application for testing
make run

# Or use the Python script
python scripts/start_app.py
```

## Script Features

- **Cross-platform**: Works on Windows, macOS, and Linux
- **Error handling**: Comprehensive error checking and reporting
- **Colored output**: Easy-to-read status messages
- **Dependency checking**: Automatic virtual environment detection
- **Safe operations**: Confirmation before destructive operations
- **Detailed logging**: Clear feedback on what's being done

## Troubleshooting

### Virtual Environment Issues

If you get virtual environment errors:

```bash
# Create new virtual environment
make venv

# Activate it manually
source venv/bin/activate  # Unix/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
make install
```

### Permission Issues

If scripts are not executable:

```bash
chmod +x scripts/*.py scripts/*.sh
```

### Cache Issues

If you have persistent cache issues:

```bash
# Nuclear option - clear everything
python scripts/dev_cleanup.py --all
make clean
```

## Integration with IDE

These scripts can be integrated into your IDE:

- **VS Code**: Add tasks in `.vscode/tasks.json`
- **PyCharm**: Configure as external tools
- **Sublime Text**: Add build systems
- **Vim/Neovim**: Add to your configuration

## Contributing

When adding new scripts:

1. Follow the existing naming convention
2. Add proper error handling
3. Include help/usage information
4. Update this README
5. Make scripts executable
6. Test on multiple platforms
