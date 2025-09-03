# WIZARD-2.1

**Scientific Data Analysis and Visualization Tool**

A professional desktop application for processing and analyzing .TOB temperature data files from scientific instruments. Built with PyQt6 and following enterprise-grade development standards.

## Features

- **TOB File Processing**: Load and analyze .TOB temperature data files
- **Data Visualization**: Interactive plots with matplotlib
- **Project Management**: Encrypted project files (.wzp) with password protection
- **Server Communication**: Upload data to servers via cURL commands
- **Cross-Platform**: Runs on macOS, Windows, and Linux
- **Internationalization**: English and German language support
- **Professional UI**: Modern PyQt6 interface with Qt Designer

## Requirements

- Python 3.13.7 or higher
- PyQt6
- pandas, numpy, matplotlib
- cryptography (for project encryption)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/fielax/wizard-2.1.git
cd wizard-2.1
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python src/main.py
```

## Development

For development, install additional dependencies:
```bash
pip install -r requirements-dev.txt
```

### Code Quality Tools

- **Black**: Code formatting
- **Pylint**: Code analysis
- **mypy**: Type checking
- **pytest**: Testing framework

### Running Tests

```bash
pytest tests/
```

### Building

```bash
pyinstaller --onefile --windowed src/main.py
```

## Architecture

The application follows the MVC (Model-View-Controller) pattern:

- **Models**: Data models and business logic
- **Views**: UI components and dialogs
- **Controllers**: Application logic and coordination
- **Services**: External integrations and utilities

## License

Proprietary - FIELAX Development Team

## Support

For support and questions, contact: dev@fielax.com
