"""
Controllers package for WIZARD-2.1

Contains all controller classes following the MVC pattern.
"""

from .main_controller import MainController
from .tob_controller import TOBController

__all__ = [
    "MainController",
    "TOBController",
]
