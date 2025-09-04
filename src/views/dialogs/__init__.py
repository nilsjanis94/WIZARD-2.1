"""
Dialogs package for WIZARD-2.1

Contains all dialog classes for user interaction.
"""

from .error_dialogs import ErrorDialog, InfoDialog, WarningDialog
from .processing_list_dialog import ProcessingListDialog
from .progress_dialogs import ProgressDialog
from .project_dialogs import PasswordDialog, ProjectDialog

__all__ = [
    "ErrorDialog",
    "WarningDialog",
    "InfoDialog",
    "ProjectDialog",
    "PasswordDialog",
    "ProgressDialog",
    "ProcessingListDialog",
]
