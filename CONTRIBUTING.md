# Contributing to WIZARD-2.1

Thank you for your interest in contributing to WIZARD-2.1! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites
- Python 3.13.7 or higher
- Git
- Virtual environment (venv, conda, or similar)

### Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nilsjanis94/WIZARD-2.1.git
   cd WIZARD-2.1
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install package in development mode:**
   ```bash
   pip install -e .
   ```

## Code Style and Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use Black for code formatting: `black src/`
- Use Pylint for code analysis: `pylint src/`
- Use mypy for type checking: `mypy src/`

### Type Hints
- All functions and methods must have type hints
- Use `typing` module for complex types
- Document return types and parameter types

### Documentation
- Use Google-style docstrings
- Document all public functions, classes, and methods
- Include examples in docstrings where appropriate

## Development Workflow

### Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `bugfix/*`: Bug fix branches
- `hotfix/*`: Critical bug fixes

### Commit Messages
Follow the conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Pull Request Process

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Write code following the style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and quality checks:**
   ```bash
   pytest tests/
   black src/
   pylint src/
   mypy src/
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat(scope): add new feature"
   ```

5. **Push and create pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/unit/test_models.py

# Run UI tests
pytest tests/ui/
```

### Writing Tests
- Write unit tests for all new functionality
- Use pytest and pytest-qt for UI testing
- Aim for high test coverage
- Test both success and error cases

## Project Structure

```
WIZARD-2.1/
├── src/                    # Source code
│   ├── models/            # Data models
│   ├── views/             # UI components
│   ├── controllers/       # Application logic
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── exceptions/        # Custom exceptions
├── tests/                 # Test files
├── ui/                    # Qt Designer files
├── docs/                  # Documentation
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
└── setup.py              # Package setup
```

## Architecture Guidelines

### MVC Pattern
- **Models**: Data structures and business logic
- **Views**: UI components and user interaction
- **Controllers**: Application logic and coordination

### Service Layer
- Use services for external integrations
- Keep controllers thin
- Implement proper error handling

### Error Handling
- Use custom exception classes
- Provide user-friendly error messages
- Log errors with appropriate detail

## Internationalization

- Use Qt's translation system
- All user-facing strings must be translatable
- Use `tr()` function for translatable strings
- Update translation files when adding new strings

## Security

- Never commit sensitive data (passwords, API keys)
- Use environment variables for configuration
- Implement proper input validation
- Follow secure coding practices

## Performance

- Profile code for performance bottlenecks
- Use appropriate data structures
- Implement caching where beneficial
- Optimize for large datasets

## Questions and Support

- Create an issue for bugs or feature requests
- Use discussions for questions and ideas
- Follow the code of conduct
- Be respectful and constructive

## License

This project is proprietary software. All contributions are subject to the project's license terms.

---

Thank you for contributing to WIZARD-2.1! 🚀
