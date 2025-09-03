# WIZARD-2.1

**Scientific Data Analysis and Visualization Tool**

A professional desktop application for processing and analyzing .TOB temperature data files from scientific instruments. Built with PyQt6 and following enterprise-grade development standards.

[![Python](https://img.shields.io/badge/Python-3.13.7+-blue.svg)](https://python.org)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6.0+-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-nilsjanis94%2FWIZARD--2.1-black.svg)](https://github.com/nilsjanis94/WIZARD-2.1)

## 🚀 Features

- **📊 TOB File Processing**: Load and analyze .TOB temperature data files
- **📈 Data Visualization**: Interactive plots with matplotlib and dual-plot system
- **🔐 Project Management**: Encrypted project files (.wzp) with AES-256 encryption
- **🌐 Server Communication**: Upload data to servers via cURL commands
- **🖥️ Cross-Platform**: Runs on macOS, Windows, and Linux
- **🌍 Internationalization**: English and German language support
- **🎨 Professional UI**: Modern PyQt6 interface with Qt Designer
- **📝 Comprehensive Logging**: Structured logging with rotation and categories
- **🛡️ Error Handling**: Robust error handling with user-friendly dialogs
- **⚡ Performance**: Optimized for large datasets with memory management

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

The application follows the **MVC (Model-View-Controller)** pattern:

```
src/
├── models/          # Data models and business logic
│   ├── tob_data_model.py
│   └── project_model.py
├── views/           # UI components and dialogs
│   ├── main_window.py
│   └── dialogs/
├── controllers/     # Application logic and coordination
│   ├── main_controller.py
│   └── tob_controller.py
├── services/        # External integrations and utilities
│   ├── tob_service.py
│   ├── data_service.py
│   ├── encryption_service.py
│   └── error_service.py
├── utils/           # Utility functions and helpers
│   ├── logging_config.py
│   ├── error_handler.py
│   └── helpers.py
└── exceptions/      # Custom exception classes
    ├── tob_exceptions.py
    ├── server_exceptions.py
    └── database_exceptions.py
```

## 🧪 Development

### Code Quality Tools

- **Black**: Code formatting (`black src/`)
- **Pylint**: Code analysis (`pylint src/`)
- **mypy**: Type checking (`mypy src/`)
- **pytest**: Testing framework (`pytest tests/`)

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest tests/unit/     # Unit tests
pytest tests/integration/  # Integration tests
pytest tests/ui/       # UI tests
```

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

- **AES-256 encryption** for project files
- **PBKDF2 key derivation** with 100,000 iterations
- **HMAC-SHA256** for data integrity
- **Secure password handling** with proper key management
- **No sensitive data** in logs or configuration

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

## 🤝 Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software. See the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: See [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md)
- **Issues**: [GitHub Issues](https://github.com/nilsjanis94/WIZARD-2.1/issues)
- **Email**: dev@fielax.com
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)

## 🏢 About

**WIZARD-2.1** is developed by the **FIELAX Development Team** for scientific data analysis and visualization. The application is designed for researchers and scientists working with temperature data from scientific instruments.

---

**Made with ❤️ by FIELAX Development Team**
