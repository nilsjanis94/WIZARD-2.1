"""
Utils package for WIZARD-2.1

Contains utility functions and helper classes.
"""

# Import helpers (Qt-free)
from .helpers import *

# Import logging (Qt-free)
from .logging_config import setup_logging

# Optional PyQt6 imports
try:
    from .error_handler import ErrorHandler
    PYQT6_UTILS_AVAILABLE = True
except ImportError:
    ErrorHandler = None
    PYQT6_UTILS_AVAILABLE = False

__all__ = [
    "setup_logging",
    "ErrorHandler",
]
