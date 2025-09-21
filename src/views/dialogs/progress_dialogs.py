"""
Progress Dialogs for WIZARD-2.1

Dialog classes for showing progress and status.
"""

from typing import Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)


class ProgressDialog(QDialog):
    """Dialog for showing progress of long-running operations."""

    def __init__(self, title: str, message: str, parent=None, cancellable: bool = True):
        """
        Initialize progress dialog.

        Args:
            title: Dialog title
            message: Progress message
            parent: Parent widget
            cancellable: Whether the operation can be cancelled
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(400, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint)

        self.cancelled = False
        self._setup_ui(message, cancellable)

    def _setup_ui(self, message: str, cancellable: bool) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if cancellable:
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self._cancel)
            button_layout.addWidget(self.cancel_button)
        else:
            self.cancel_button = None

        layout.addLayout(button_layout)

    def _cancel(self) -> None:
        """Handle cancel button click."""
        self.cancelled = True
        self.reject()

    def set_progress(self, value: int, message: Optional[str] = None) -> None:
        """
        Update progress.

        Args:
            value: Progress value (0-100)
            message: Optional progress message
        """
        self.progress_bar.setValue(value)
        if message:
            self.message_label.setText(message)

    def set_indeterminate(self, message: Optional[str] = None) -> None:
        """
        Set progress bar to indeterminate mode.

        Args:
            message: Optional progress message
        """
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        if message:
            self.message_label.setText(message)

    def is_cancelled(self) -> bool:
        """
        Check if operation was cancelled.

        Returns:
            True if cancelled, False otherwise
        """
        return self.cancelled
