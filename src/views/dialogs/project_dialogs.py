"""
Project Dialogs for WIZARD-2.1

Dialog classes for project management.
"""

from typing import Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class ProjectDialog(QDialog):
    """Dialog for creating or editing projects."""

    def __init__(
        self, parent=None, project_name: str = "", project_description: str = ""
    ):
        """
        Initialize project dialog.

        Args:
            parent: Parent widget
            project_name: Initial project name
            project_description: Initial project description
        """
        super().__init__(parent)
        self.setWindowTitle("Project Settings")
        self.setModal(True)
        self.setMinimumSize(400, 300)

        self._setup_ui(project_name, project_description)

    def _setup_ui(self, project_name: str, project_description: str) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Project name
        self.name_edit = QLineEdit(project_name)
        self.name_edit.setPlaceholderText("Enter project name")
        form_layout.addRow("Project Name:", self.name_edit)

        # Project description
        self.description_edit = QTextEdit(project_description)
        self.description_edit.setPlaceholderText("Enter project description (optional)")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Description:", self.description_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_project_data(self) -> Tuple[str, str]:
        """
        Get project data from the dialog.

        Returns:
            Tuple of (project_name, project_description)
        """
        return (
            self.name_edit.text().strip(),
            self.description_edit.toPlainText().strip(),
        )


class PasswordDialog(QDialog):
    """Dialog for entering project password."""

    def __init__(self, parent=None, is_new_project: bool = False):
        """
        Initialize password dialog.

        Args:
            parent: Parent widget
            is_new_project: Whether this is for a new project
        """
        super().__init__(parent)
        self.is_new_project = is_new_project

        title = "Set Project Password" if is_new_project else "Enter Project Password"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(350, 200)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Info label
        info_text = (
            "Set a password to encrypt your project data."
            if self.is_new_project
            else "Enter the password to decrypt your project data."
        )
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Form layout
        form_layout = QFormLayout()

        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter password")
        form_layout.addRow("Password:", self.password_edit)

        # Confirm password field (for new projects)
        if self.is_new_project:
            self.confirm_password_edit = QLineEdit()
            self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_password_edit.setPlaceholderText("Confirm password")
            form_layout.addRow("Confirm:", self.confirm_password_edit)
        else:
            self.confirm_password_edit = None

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _validate_and_accept(self) -> None:
        """Validate password and accept dialog."""
        password = self.password_edit.text()

        if not password:
            # TODO: Show error message
            return

        if self.is_new_project and self.confirm_password_edit:
            confirm_password = self.confirm_password_edit.text()
            if password != confirm_password:
                # TODO: Show error message
                return

        self.accept()

    def get_password(self) -> str:
        """
        Get the entered password.

        Returns:
            The entered password
        """
        return self.password_edit.text()
