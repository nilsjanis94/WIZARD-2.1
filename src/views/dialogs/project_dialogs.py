"""
Project Dialogs for WIZARD-2.1

Dialog classes for project management.
"""

from typing import Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
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
        self,
        parent=None,
        project_name: str = "",
        project_description: str = "",
        enter_key: str = "",
        server_url: str = ""
    ):
        """
        Initialize project dialog.

        Args:
            parent: Parent widget
            project_name: Initial project name
            project_description: Initial project description
            enter_key: Initial enter key for server authentication
            server_url: Initial server URL
        """
        super().__init__(parent)
        self.setWindowTitle("Create New Project")
        self.setModal(True)
        self.setMinimumSize(450, 350)

        self._setup_ui(project_name, project_description, enter_key, server_url)

    def _setup_ui(self, project_name: str, project_description: str, enter_key: str, server_url: str) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Form layout
        form_layout = QFormLayout()

        # Project name
        self.name_edit = QLineEdit(project_name)
        self.name_edit.setPlaceholderText("Enter project name")
        form_layout.addRow("Project Name:", self.name_edit)

        # Enter key (for server authentication)
        self.enter_key_edit = QLineEdit(enter_key)
        self.enter_key_edit.setPlaceholderText("Enter authentication key for server access")
        self.enter_key_edit.setEchoMode(QLineEdit.EchoMode.Password)  # Hide sensitive data
        form_layout.addRow("Enter Key:", self.enter_key_edit)

        # Server URL
        self.server_url_edit = QLineEdit(server_url)
        self.server_url_edit.setPlaceholderText("https://api.example.com/endpoint")
        form_layout.addRow("Server URL:", self.server_url_edit)

        # Project description
        self.description_edit = QTextEdit(project_description)
        self.description_edit.setPlaceholderText("Enter project description (optional)")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_project_data(self) -> Tuple[str, str, str, str]:
        """
        Get project data from the dialog.

        Returns:
            Tuple of (project_name, enter_key, server_url, project_description)
        """
        return (
            self.name_edit.text().strip(),
            self.enter_key_edit.text().strip(),
            self.server_url_edit.text().strip(),
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


class TOBProjectAssignmentDialog(QDialog):
    """
    Dialog for asking user if a loaded TOB file should be added to the current project.

    This dialog appears after successfully loading a TOB file via File → Open,
    giving the user the option to add the file to the currently open project for
    persistent storage and management.
    """

    def __init__(
        self,
        parent=None,
        file_name: str = "",
        file_size_mb: float = 0.0,
        data_points: int = 0,
        sensor_count: int = 0,
        project_name: str = ""
    ):
        """
        Initialize TOB project assignment dialog.

        Args:
            parent: Parent widget
            file_name: Name of the loaded TOB file
            file_size_mb: Size of the file in MB
            data_points: Number of data points in the file
            sensor_count: Number of sensors available
            project_name: Name of the current project
        """
        super().__init__(parent)
        self.setWindowTitle("Add TOB File to Project")
        self.setModal(True)
        self.setMinimumSize(400, 250)

        self.file_name = file_name
        self.should_add_to_project = False

        self._setup_ui(file_name, file_size_mb, data_points, sensor_count, project_name)

    def _setup_ui(
        self,
        file_name: str,
        file_size_mb: float,
        data_points: int,
        sensor_count: int,
        project_name: str
    ) -> None:
        """Setup the dialog UI components."""
        layout = QVBoxLayout()

        # Header message
        header_label = QLabel("TOB File Successfully Loaded!")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #3AAA35;")
        layout.addWidget(header_label)

        # File information
        info_layout = QFormLayout()
        info_layout.addRow("File:", QLabel(file_name))
        info_layout.addRow("Size:", QLabel(f"{file_size_mb:.1f} MB"))
        info_layout.addRow("Data Points:", QLabel(f"{data_points:,}"))
        info_layout.addRow("Sensors:", QLabel(str(sensor_count)))
        layout.addLayout(info_layout)

        # Spacer
        layout.addSpacing(10)

        # Question to user
        question_label = QLabel(
            f"Do you want to add this TOB file to the current project '{project_name}'?\n\n"
            "• The file will be saved with the project and appear in the Processing List\n"
            "• You can upload it to the server and track its processing status\n"
            "• Changes will be automatically saved"
        )
        question_label.setWordWrap(True)
        layout.addWidget(question_label)

        # Checkbox for "Don't ask again"
        self.dont_ask_checkbox = QCheckBox("Don't ask again for this session")
        layout.addWidget(self.dont_ask_checkbox)

        # Spacer
        layout.addSpacing(10)

        # Buttons
        button_box = QDialogButtonBox()
        self.yes_button = QPushButton("Add to Project")
        self.yes_button.setDefault(True)
        self.no_button = QPushButton("Just Show Plot")

        button_box.addButton(self.yes_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(self.no_button, QDialogButtonBox.ButtonRole.RejectRole)

        self.yes_button.clicked.connect(self._on_yes_clicked)
        self.no_button.clicked.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)

    def _on_yes_clicked(self) -> None:
        """Handle yes button click."""
        self.should_add_to_project = True
        self.accept()

    def should_not_ask_again(self) -> bool:
        """
        Check if user wants to skip this dialog in the future.

        Returns:
            True if user checked "Don't ask again"
        """
        return self.dont_ask_checkbox.isChecked()
