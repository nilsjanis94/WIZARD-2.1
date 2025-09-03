"""
Dialogs package for WIZARD-2.1

Contains all dialog classes for user interaction.
"""

from .error_dialogs import ErrorDialog, WarningDialog, InfoDialog
from .project_dialogs import ProjectDialog, PasswordDialog
from .progress_dialogs import ProgressDialog
from .processing_list_dialog import ProcessingListDialog

__all__ = [
    "ErrorDialog",
    "WarningDialog", 
    "InfoDialog",
    "ProjectDialog",
    "PasswordDialog",
    "ProgressDialog",
    "ProcessingListDialog",
]
