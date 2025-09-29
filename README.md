# WIZARD-2.1

**Scientific Data Analysis and Visualization Tool**

A professional desktop application for processing and analyzing .TOB temperature data files from scientific instruments. Built with PyQt6 and following enterprise-grade development standards.

[![Python](https://img.shields.io/badge/Python-3.13.7+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6.0+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-nilsjanis94%2FWIZARD--2.1-black.svg)](https://github.com/nilsjanis94/WIZARD-2.1)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/nilsjanis94/WIZARD-2.1/ci.yml?branch=main&label=CI%2FCD)](https://github.com/nilsjanis94/WIZARD-2.1/actions)
[![Coverage](https://img.shields.io/badge/Coverage-35%25-green.svg)](https://github.com/nilsjanis94/WIZARD-2.1)
[![Code Quality](https://img.shields.io/badge/Pylint-8.67%2F10-green.svg)](https://github.com/nilsjanis94/WIZARD-2.1)
[![Security](https://img.shields.io/badge/Security-Bandit-blue.svg)](https://github.com/nilsjanis94/WIZARD-2.1)

## 🚀 Features

### ✅ **Implemented Core Features**
- **📊 TOB File Processing**: Load and analyze .TOB temperature data files with tob-dataloader
- **📈 Data Visualization**: Interactive matplotlib plots with dual Y-axis system (NTC sensors + additional data)
- **🔐 Project Management**: Encrypted .wzp project files mit SecretManager pro Projekt und Meta-Datei
- **🌐 Server Communication**: cURL-basierte Datenübertragung inkl. Statusabfragen
- **🖥️ Cross-Platform**: Validiert via GitHub Actions auf macOS & Windows
- **🌍 Internationalization**: Englisch und Deutsch, umschaltbar zur Laufzeit
- **🎨 Professionelle UI**: PyQt6-Oberfläche mit Qt Designer (responsive Layout)
- **📝 Audit Logging**: JSON-basierte Audit-Logs mit Daily Rotation & Zugriffsschutz
- **🛡️ Fehlerhandling**: Einheitliches Fehler- und Incident-Handling über ErrorService & ErrorHandler
- **⚡ Performance**: Optimiert für 3,8MB .TOB-Daten (<5s Load, <100MB RAM)

### 🔧 **Architecture & Quality**
- **🎯 Code Quality**: Pylint 8.67/10, mypy type checking, black formatting, isort imports
- **🔧 Modular Architecture**: Clean MVC pattern with dedicated services and controllers
- **🧪 Testing**: 240+ Tests (Unit + Integration), Coverage 35% (Pipeline-Gate 70% Ziel)
- **🔒 Security**: Bandit Security-Scan, SecretManager-based Encryption, Audit-Log-Härtung
- **📚 Documentation**: Sphinx-generated API docs with Google-style docstrings
- **⚙️ CI/CD Pipeline**: GitHub Actions with Ubuntu + Windows testing, quality gates, and deployment ready

### 🎛️ **Advanced UI Features**
- **Dual-Plot System**: Main plot (NTC sensors) + subplot (pressure, voltage, tilt data)
- **Sensor Management**: 22 NTC sensors + PT100 with individual color coding and visibility controls
- **Axis Controls**: Auto/manual scaling with min/max value controls for X, Y1, Y2 axes
- **Data Metrics**: Real-time calculation of Mean HP-Power, Max Vaccu, Tilt Status, Mean Press
- **Processing List**: Complete project file management with server status tracking
- **Project Controls**: Subcon settings, quality control, data sending with visual confirmation

### 🔬 **Scientific Data Processing**
- **TOB Format Support**: Scientific notation parsing, timestamp handling, multi-sensor data
- **Data Integrity**: Comprehensive validation with specific error types and recovery
- **Performance Optimization**: Memory-efficient processing for large datasets (3,750+ data points)
- **Scientific Standards**: Enterprise-grade data processing for research applications

## 📋 Requirements

- **Python**: 3.13.7 or higher
- **PyQt6**: 6.6.0+ for GUI framework
- **pandas**: 2.2.0+ for data processing
- **numpy**: 1.26.0+ for numerical operations
- **matplotlib**: 3.8.0+ for data visualization
- **cryptography**: 42.0.0+ for project encryption

## 🛠️ Installation

### Quick Start

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
   ```

4. **Install package in development mode:**
   ```bash
   pip install -e .
   ```

5. **Run the application:**
   ```bash
   python -m src.main
   ```

### Development Setup

For development, install additional dependencies:
```bash
pip install -r requirements-dev.txt
```

## 🏗️ Architecture

The application follows the **MVC (Model-View-Controller)** pattern with enterprise-grade modular design:

```
src/
├── main.py                 # Application entry point
├── models/                 # Data models and business logic (93% coverage)
│   ├── tob_data_model.py   # TOB data handling & validation
│   └── project_model.py    # Project metadata & configuration
├── views/                  # UI components and dialogs (Qt Designer)
│   ├── main_window.py      # Main application window (1374x776px)
│   └── dialogs/            # Modal dialogs for user interaction
│       ├── error_dialogs.py    # Error/warning/info dialogs
│       ├── project_dialogs.py  # Project creation/management
│       ├── progress_dialogs.py # Progress indicators
│       └── processing_list_dialog.py # TOB file management
├── controllers/            # Application logic and coordination (0% coverage)
│   ├── main_controller.py  # Main application controller
│   └── tob_controller.py   # TOB data processing controller
├── services/               # External integrations and utilities (46% coverage)
│   ├── tob_service.py      # TOB file loading & parsing (50%)
│   ├── data_service.py     # Data processing & metrics (65%)
│   ├── plot_service.py     # Matplotlib plotting engine (23%)
│   ├── encryption_service.py # AES-256 encryption (23%)
│   ├── error_service.py    # Error handling & user feedback (22%)
│   ├── ui_service.py       # UI state management (55%)
│   ├── ui_state_manager.py # UI widget coordination (27%)
│   ├── axis_ui_service.py  # Axis controls & scaling (80%)
│   └── plot_style_service.py # Plot styling & theming (95%)
├── utils/                  # Utility functions and helpers (36% coverage)
│   ├── logging_config.py   # Enterprise logging system (11%)
│   ├── error_handler.py    # Global error handling (20%)
│   └── helpers.py          # Utility functions (21%)
└── exceptions/             # Custom exception classes (48% coverage)
    ├── tob_exceptions.py   # TOB-specific errors (63%)
    ├── server_exceptions.py # Server communication errors (40%)
    └── database_exceptions.py # Data/storage errors (48%)
```

### 📊 **Coverage Breakdown by Layer**

| Layer | Files | Total Coverage | Status |
|-------|-------|----------------|--------|
| **Models** | 2 | **88%** | 🟢 **Excellent** |
| **Services** | 9 | **52%** | 🟢 **Solid** |
| **Utils** | 3 | **41%** | 🟡 **OK** |
| **Exceptions** | 3 | **55%** | 🟢 **Solid** |
| **Views/Controllers** | 6 | **5%** | ⚪ **In Progress (UI Tests geplant)** |
| **Overall** | 23 | **35%** | 🟡 **Stabil** |

### 🎯 **Architecture Highlights**
- **Separation of Concerns**: Clear MVC boundaries with dedicated service layer
- **Testability**: Modular design enables comprehensive unit testing
- **Scalability**: Service-oriented architecture for easy feature extension
- **Maintainability**: Well-documented interfaces and type hints throughout
- **Cross-Platform**: OS-agnostic design with platform-specific optimizations

## 🧪 Development & Quality

### 📊 **Current Quality Metrics**
- **Test Coverage**: 35% (229 Unit + 14 Integration Tests)
- **Code Quality**: Pylint 8.67/10 (Enterprise-Level)
- **Type Safety**: mypy (100% der produktiven Module)
- **Security**: Bandit Security Scan + SecretManager-Audits
- **CI/CD**: GitHub Actions (Ubuntu & Windows) inkl. Coverage- und Audit-Gates

### 🛠️ **Development Tools**

#### **Code Quality & Formatting**
- **Black**: Code formatting (`make format`) - PEP 8 compliance
- **isort**: Import sorting (`make import-sort`) - Clean imports
- **Pylint**: Code analysis (`make lint`) - 8.67/10 professional score
- **mypy**: Type checking (`make type-check`) - Full type safety
- **Bandit**: Security scanning (`make security-check`) - Enterprise security

#### **Testing Framework**
- **pytest**: Comprehensive testing (`make test`) - 123 tests
- **pytest-cov**: Coverage reporting (`make test-coverage`) - 30% coverage
- **pytest-qt**: Qt/GUI testing - Cross-platform compatibility

### 🚀 **Development Workflow**

#### **Quick Start Commands**
```bash
# Install and setup
make setup          # Install all dependencies
make start          # Launch application

# Code quality (run all checks)
make quality        # Format + sort + lint + security + type-check

# Testing
make test           # Run all tests (123 tests)
make test-unit      # Run unit tests only (109 tests)
make test-integration # Run integration tests (14 tests)
make test-coverage  # Run with coverage report

# Maintenance
make clean          # Clear cache and logs
make logs           # Show recent application logs
```

#### **Advanced Testing**
```bash
# Full test suite with different configurations
pytest tests/                          # All tests
pytest tests/unit/ -v                 # Verbose unit tests
pytest tests/integration/ -v          # Integration tests
pytest --cov=src --cov-report=html    # HTML coverage report

# Specific test categories
pytest -m unit                        # Unit tests only
pytest -m integration                 # Integration tests only
pytest -k "test_data_service"         # Specific test file
```

#### **Quality Gates**
```bash
# Individual quality checks
make format           # Format code with black
make format-check     # Check formatting compliance
make import-sort      # Sort imports with isort
make import-check     # Check import sorting
make lint            # Run pylint (8.67/10)
make type-check      # Run mypy type checking
make security-check  # Run bandit security scan
```

### 📈 **Coverage Analysis**

#### **Coverage by Component** (35% overall)
- **Models**: 88% (Core Business Logic sehr gut abgedeckt)
- **Services**: 52% (Business Layer mit Priorisierung auf kritische Pfade)
- **Utils**: 41% (Hilfsfunktionen zunehmend getestet)
- **Exceptions**: 55% (Fehlerbehandlung konsolidiert)
- **Views/Controllers**: 5% (UI über Integrationstests & manuelle QA abgesichert)

#### **Test Distribution**
- **Unit Tests**: 109 tests (89% of total)
- **Integration Tests**: 14 tests (11% of total)
- **UI Tests**: 0 tests (Planned for future)

### 🎯 **Development Standards**
- **Python Version**: 3.13.7 (Latest stable)
- **Code Style**: PEP 8 with Black formatting
- **Documentation**: Google-style docstrings
- **Type Hints**: Full mypy compliance
- **Testing**: pytest with comprehensive coverage
- **Security**: Bandit security scanning
- **CI/CD**: Automated quality gates on every commit

### Building

```bash
# Build executable
pyinstaller --onefile --windowed src/main.py

# Build for specific platform
pyinstaller --onefile --windowed --target-arch=x86_64 src/main.py
```

## 📊 Data Processing

### TOB File Format
- **Scientific temperature data** from research instruments
- **Header information** with project metadata
- **Sensor data** including NTC sensors (NTC01-NTC22) and PT100
- **Time series data** with 1-second intervals
- **Additional measurements** (pressure, tilt, battery voltage)

### Visualization Features
- **Dual-plot system** with main plot and subplot
- **Color-coded sensors**: NTC01-07 (red), NTC08-12 (blue), NTC13-22 (black), PT100 (orange)
- **Interactive controls** for axis scaling (auto/manual)
- **Real-time data metrics** calculation

## 🔐 Security

- **AES-256 encryption** for project files with app-internal key
- **No user passwords** - app manages encryption transparently
- **HMAC-SHA256** for data integrity verification
- **Secure key management** with consistent app-specific encryption
- **No sensitive data** in logs or configuration files

## 🌍 Internationalization

- **English** (default language)
- **German** (Deutsch) support
- **Qt Linguist** integration
- **Dynamic language switching**
- **Persistent language settings**

## 📝 Logging

- **Structured logging** with multiple log files
- **Log rotation** with size limits
- **Categorized logs**: Application, Debug, Error, Server
- **No sensitive data** in log files
- **Performance monitoring** and profiling support

## 🤝 Contributing & Development Standards

### 📋 **Quality Requirements**
Before submitting code, ensure all quality gates pass:
- ✅ **Formatting**: `make format` (Black + isort)
- ✅ **Linting**: `make lint` (Pylint 8.67/10 required)
- ✅ **Type Checking**: `make type-check` (mypy compliance)
- ✅ **Security**: `make security-check` (Bandit scanning)
- ✅ **Testing**: `make test` (All 123 tests pass)
- ✅ **Coverage**: Minimum 30% coverage maintained

### 🚀 **Development Workflow**

#### **1. Environment Setup**
```bash
git clone https://github.com/nilsjanis94/WIZARD-2.1.git
cd WIZARD-2.1
make setup          # Install all dependencies
make quality        # Run all quality checks (baseline)
```

#### **2. Development Process**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes with quality checks
make quality        # Run quality checks frequently
make test          # Run tests after changes

# Commit with conventional format
git commit -m "feat: add amazing feature

- Detailed description of changes
- Reference to issues if applicable
- Quality gate compliance confirmed"

# Push and create PR
git push origin feature/your-feature-name
```

#### **3. Pull Request Requirements**
- [ ] All quality gates pass (CI/CD green)
- [ ] Code coverage maintained or improved
- [ ] Tests added for new functionality
- [ ] Documentation updated if needed
- [ ] Type hints complete for new code
- [ ] Security implications reviewed

### 🎯 **Code Standards**
- **Python**: 3.13.7+ (latest stable)
- **Style**: PEP 8 with Black formatting
- **Imports**: isort for clean import organization
- **Types**: Full mypy type hints required
- **Docs**: Google-style docstrings
- **Testing**: pytest with comprehensive coverage
- **Security**: Bandit security scanning

### 📊 **Current Project Status**
- **Phase**: Konsolidierte Enterprise-Readiness (Security, Ops, Governance geschlossen)
- **Coverage**: 35% (Steigerung + klarer Fahrplan zu 70%)
- **Qualität**: Pylint 8.67/10, mypy + Bandit enforced
- **Testing**: 243 Tests (Unit + Integration) inkl. Audit- und Secrets-Flows
- **CI/CD**: GitHub Actions mit Coverage-Gate, Audit Logging und Secrets-Checks

### 🔧 **Architecture Guidelines**
- **MVC Pattern**: Strict separation of concerns
- **Service Layer**: Business logic in dedicated services
- **Error Handling**: Comprehensive exception handling
- **Logging**: Structured logging with categories
- **Security**: Encryption for sensitive data
- **Cross-Platform**: OS-agnostic design principles

### 📖 **Documentation**
- [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) – Technischer Architektur-Überblick
- [ENTERPRISE_READINESS_PLAN.md](ENTERPRISE_READINESS_PLAN.md) – Gap-Analyse & Maßnahmenkatalog
- [RELEASE_SUPPORT_PLAYBOOK.md](docs/RELEASE_SUPPORT_PLAYBOOK.md) – Release-, Rollback- & Support-Prozesse
- [GOVERNANCE_GUIDE.md](docs/GOVERNANCE_GUIDE.md) – RACI, Datenschutz & Risikomanagement
- [CONTRIBUTING.md](CONTRIBUTING.md) – Contribution Guidelines & Coding Standards
- Sphinx/API-Dokumentation (in Planung)

### 🆘 **Getting Help**
- **Issues**: [GitHub Issues](https://github.com/nilsjanis94/WIZARD-2.1/issues)
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check PROJECT_DOCUMENTATION.md for technical details

## 📄 License

This project is proprietary software. See the [LICENSE](LICENSE) file for details.

## 🆘 Support & Resources

### 📚 **Documentation**
- **[PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)** - Complete technical specifications and architecture
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines and contribution process
- **API Documentation** - Sphinx-generated docs (planned for future release)

### 🐛 **Issue Reporting**
- **Bug Reports**: [GitHub Issues](https://github.com/nilsjanis94/WIZARD-2.1/issues) with "bug" label
- **Feature Requests**: [GitHub Issues](https://github.com/nilsjanis94/WIZARD-2.1/issues) with "enhancement" label
- **Security Issues**: Email dev@fielax.com directly (do not post publicly)

### 💬 **Community & Support**
- **GitHub Discussions**: General questions and community support
- **Email Support**: dev@fielax.com for technical inquiries
- **Development Team**: FIELAX Development Team

## 🏢 About WIZARD-2.1

**WIZARD-2.1** is a professional desktop application developed by the **FIELAX Development Team** for scientific data analysis and visualization in research environments.

### 🎯 **Mission**
To provide researchers and scientists with a powerful, reliable, and user-friendly tool for processing and analyzing temperature data from scientific instruments, following enterprise-grade development standards.

### 🔬 **Target Users**
- Research scientists working with temperature data
- Laboratory technicians processing TOB files
- Quality assurance teams validating sensor data
- Research institutions requiring data integrity and compliance

### 🏗️ **Development Philosophy**
- **Enterprise-Grade Quality**: Professional development standards with comprehensive testing
- **Cross-Platform Compatibility**: Seamless operation on macOS, Windows, and Linux
- **User-Centric Design**: Intuitive interface with powerful capabilities
- **Data Integrity**: Robust validation and error handling for scientific data
- **Security First**: Encrypted project storage and secure data handling
- **Performance Optimized**: Efficient processing of large datasets (3.8MB+ files)

### 📊 **Current Status** (December 2024)
- **Development Phase**: Early implementation with solid foundation
- **Code Quality**: Pylint 8.67/10 (Enterprise standard achieved)
- **Test Coverage**: 30% (109 unit + 14 integration tests)
- **CI/CD Status**: ✅ Ubuntu + Windows pipelines active
- **Architecture**: MVC pattern with comprehensive service layer
- **Features**: Core TOB processing, visualization, and project management implemented

### 🚀 **Roadmap**
- **Phase 1** ✅: Core architecture and basic functionality
- **Phase 2** 🔄: Complete remaining service implementations
- **Phase 3** 📋: Enhanced testing and quality improvements
- **Phase 4** 🎯: Advanced features and optimizations
- **Phase 5** 🚀: Production deployment and user adoption

---

**Developed with ❤️ by the FIELAX Development Team**

**"Advancing scientific research through software excellence"**
