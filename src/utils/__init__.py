"""
Utils package for WIZARD-2.1

Contains utility functions and helper classes.
"""

from .logging_config import setup_logging
from .error_handler import ErrorHandler
from .helpers import *

__all__ = [
    "setup_logging",
    "ErrorHandler",
]
