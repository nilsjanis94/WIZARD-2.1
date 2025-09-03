"""
Models package for WIZARD-2.1

Contains all data models and business logic classes following the MVC pattern.
"""

from .tob_data_model import TOBDataModel
from .project_model import ProjectModel

__all__ = [
    "TOBDataModel",
    "ProjectModel",
]
