"""
Error Dialogs for WIZARD-2.1

Custom error dialog classes for user feedback.
"""

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                             QTextEdit, QVBoxLayout)


class ErrorDialog(QDialog):
    """Error dialog for displaying error messages."""

    def __init__(
        self, title: str, message: str, details: Optional[str] = None, parent=None
    ):
        """
        Initialize error dialog.

        Args:
            title: Dialog title
            message: Error message
            details: Optional detailed error information
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(400, 200)

        self._setup_ui(title, message, details)

    def _setup_ui(self, title: str, message: str, details: Optional[str]) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #d32f2f;")
        layout.addWidget(title_label)

        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("margin: 10px 0;")
        layout.addWidget(message_label)

        # Details (if provided)
        if details:
            details_text = QTextEdit()
            details_text.setPlainText(details)
            details_text.setReadOnly(True)
            details_text.setMaximumHeight(150)
            layout.addWidget(details_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)


class WarningDialog(QDialog):
    """Warning dialog for displaying warning messages."""

    def __init__(
        self, title: str, message: str, details: Optional[str] = None, parent=None
    ):
        """
        Initialize warning dialog.

        Args:
            title: Dialog title
            message: Warning message
            details: Optional detailed warning information
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(400, 200)

        self._setup_ui(title, message, details)

    def _setup_ui(self, title: str, message: str, details: Optional[str]) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #f57c00;")
        layout.addWidget(title_label)

        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("margin: 10px 0;")
        layout.addWidget(message_label)

        # Details (if provided)
        if details:
            details_text = QTextEdit()
            details_text.setPlainText(details)
            details_text.setReadOnly(True)
            details_text.setMaximumHeight(150)
            layout.addWidget(details_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)


class InfoDialog(QDialog):
    """Info dialog for displaying informational messages."""

    def __init__(
        self, title: str, message: str, details: Optional[str] = None, parent=None
    ):
        """
        Initialize info dialog.

        Args:
            title: Dialog title
            message: Info message
            details: Optional detailed information
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(400, 200)

        self._setup_ui(title, message, details)

    def _setup_ui(self, title: str, message: str, details: Optional[str]) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1976d2;")
        layout.addWidget(title_label)

        # Message label
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("margin: 10px 0;")
        layout.addWidget(message_label)

        # Details (if provided)
        if details:
            details_text = QTextEdit()
            details_text.setPlainText(details)
            details_text.setReadOnly(True)
            details_text.setMaximumHeight(150)
            layout.addWidget(details_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
