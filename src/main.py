#!/usr/bin/env python3
"""
WIZARD-2.1 - Main Application Entry Point

Scientific Data Analysis and Visualization Tool
Author: FIELAX Development Team
Version: 2.1.0
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add src directory to Python path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTranslator, QLocale
from PyQt6.QtGui import QIcon

from .utils.logging_config import setup_logging
from .utils.error_handler import ErrorHandler
from .controllers.main_controller import MainController
from .views.main_window import MainWindow


def setup_application() -> QApplication:
    """
    Setup and configure the QApplication.
    
    Returns:
        QApplication: Configured application instance
    """
    # High DPI scaling is enabled by default in PyQt6
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("WIZARD-2.1")
    app.setApplicationVersion("2.1.0")
    app.setOrganizationName("FIELAX")
    app.setOrganizationDomain("fielax.com")
    
    # Set application icon
    icon_path = Path(__file__).parent.parent / "resources" / "icons" / "wizard.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app


def setup_translations(app: QApplication) -> None:
    """
    Setup internationalization for the application.
    
    Args:
        app: QApplication instance
    """
    translator = QTranslator()
    
    # Try to load language from settings
    # For now, default to English
    locale = QLocale.system()
    language = locale.name()
    
    # Load translation file
    translations_dir = Path(__file__).parent.parent / "resources" / "translations"
    translation_file = f"wizard_{language}.qm"
    translation_path = translations_dir / translation_file
    
    if translation_path.exists():
        translator.load(str(translation_path))
        app.installTranslator(translator)


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code
    """
    try:
        # Setup logging
        setup_logging()
        
        # Setup error handling
        error_handler = ErrorHandler()
        
        # Create application
        app = setup_application()
        
        # Setup translations
        setup_translations(app)
        
        # Create main controller (which creates the main window)
        main_controller = MainController()
        
        # Show main window
        main_controller.show_main_window()
        
        # Start event loop
        return app.exec()
        
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
