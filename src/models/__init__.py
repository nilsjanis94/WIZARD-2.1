"""
Models package for WIZARD-2.1

Contains all data models and business logic classes following the MVC pattern.
"""

from .project_model import ProjectModel
from .tob_data_model import TOBDataModel

__all__ = [
    "TOBDataModel",
    "ProjectModel",
]
