"""
Error Handler for WIZARD-2.1

Centralized error handling and user feedback.
"""

import logging
import traceback
from typing import Any, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QWidget


class ErrorHandler(QObject):
    """
    Centralized error handler for the application.

    Signals:
        error_occurred: Emitted when an error occurs
        warning_occurred: Emitted when a warning occurs
        info_message: Emitted when an info message is shown
    """

    # Signals
    error_occurred = pyqtSignal(str, str)  # error_type, error_message
    warning_occurred = pyqtSignal(str)  # warning_message
    info_message = pyqtSignal(str)  # info_message

    def __init__(self):
        """Initialize the error handler."""
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def handle_error(
        self,
        error: Exception,
        context: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Handle an error and show appropriate user feedback.

        Args:
            error: Exception to handle
            context: Optional context information
            parent: Parent widget for dialogs
        """
        try:
            error_type = type(error).__name__
            error_message = str(error)

            # Log the error
            log_message = f"Error: {error_type} - {error_message}"
            if context:
                log_message = f"{context}: {log_message}"

            self.logger.error(log_message, exc_info=True)

            # Emit signal
            self.error_occurred.emit(error_type, error_message)

            # Show user-friendly error dialog
            self._show_error_dialog(error_type, error_message, parent)

        except Exception as e:
            self.logger.error("Error in error handling: %s", e)

    def handle_warning(
        self,
        message: str,
        context: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Handle a warning and show user feedback.

        Args:
            message: Warning message
            context: Optional context information
            parent: Parent widget for dialogs
        """
        try:
            # Log the warning
            log_message = f"Warning: {message}"
            if context:
                log_message = f"{context}: {log_message}"

            self.logger.warning(log_message)

            # Emit signal
            self.warning_occurred.emit(message)

            # Show warning dialog
            self._show_warning_dialog(message, parent)

        except Exception as e:
            self.logger.error("Error in warning handling: %s", e)

    def handle_info(
        self,
        message: str,
        context: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Handle an info message and show user feedback.

        Args:
            message: Info message
            context: Optional context information
            parent: Parent widget for dialogs
        """
        try:
            # Log the info
            log_message = f"Info: {message}"
            if context:
                log_message = f"{context}: {log_message}"

            self.logger.info(log_message)

            # Emit signal
            self.info_message.emit(message)

            # Show info dialog
            self._show_info_dialog(message, parent)

        except Exception as e:
            self.logger.error("Error in info handling: %s", e)

    def _show_error_dialog(
        self, error_type: str, error_message: str, parent: Optional[QWidget] = None
    ) -> None:
        """
        Show error dialog to user.

        Args:
            error_type: Type of error
            error_message: Error message
            parent: Parent widget
        """
        try:
            # Create user-friendly error message
            user_message = self._create_user_message(error_type, error_message)

            # Show message box
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Error")
            msg_box.setText(user_message)
            msg_box.setDetailedText(
                f"Error Type: {error_type}\nDetails: {error_message}"
            )
            msg_box.exec()

        except Exception as e:
            self.logger.error("Error showing error dialog: %s", e)

    def _show_warning_dialog(
        self, message: str, parent: Optional[QWidget] = None
    ) -> None:
        """
        Show warning dialog to user.

        Args:
            message: Warning message
            parent: Parent widget
        """
        try:
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(message)
            msg_box.exec()

        except Exception as e:
            self.logger.error("Error showing warning dialog: %s", e)

    def _show_info_dialog(self, message: str, parent: Optional[QWidget] = None) -> None:
        """
        Show info dialog to user.

        Args:
            message: Info message
            parent: Parent widget
        """
        try:
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Information")
            msg_box.setText(message)
            msg_box.exec()

        except Exception as e:
            self.logger.error("Error showing info dialog: %s", e)

    def _create_user_message(self, error_type: str, error_message: str) -> str:
        """
        Create user-friendly error message.

        Args:
            error_type: Type of error
            error_message: Technical error message

        Returns:
            User-friendly error message
        """
        # Map error types to user-friendly messages
        error_messages = {
            "TOBFileNotFoundError": (
                "The TOB file could not be found. Please check the file path and try again."
            ),
            "TOBParsingError": (
                "There was an error reading the TOB file. The file may be corrupted or "
                "in an unsupported format."
            ),
            "ServerConnectionError": (
                "Could not connect to the server. Please check your internet connection "
                "and try again."
            ),
            "ServerTimeoutError": "The server request timed out. Please try again later.",
            "FileNotFoundError": (
                "The specified file could not be found. Please check the file path and "
                "try again."
            ),
            "PermissionError": (
                "You don't have permission to access this file. Please check the file "
                "permissions."
            ),
            "ValueError": "Invalid data format. Please check your input and try again.",
            "KeyError": "Required data is missing. Please check your input and try again.",
            "ConnectionError": "Network connection error. Please check your internet connection and try again.",
            "TimeoutError": "Operation timed out. Please try again later.",
            "MemoryError": (
                "Insufficient memory to complete the operation. "
                "Please try with a smaller file or close other applications."
            ),
            "OSError": "System error occurred. Please try again or contact support if the problem persists.",
        }

        # Return user-friendly message or fallback to technical message
        return error_messages.get(error_type, f"An error occurred: {error_message}")

    def log_exception(self, error: Exception, context: Optional[str] = None) -> None:
        """
        Log an exception with full traceback.

        Args:
            error: Exception to log
            context: Optional context information
        """
        try:
            error_type = type(error).__name__
            error_message = str(error)
            traceback_str = traceback.format_exc()

            log_message = f"Exception: {error_type} - {error_message}"
            if context:
                log_message = f"{context}: {log_message}"

            self.logger.error("%s\n%s", log_message, traceback_str)

        except Exception as e:
            self.logger.error("Error in exception logging: %s", e)

    def get_error_summary(self, error: Exception) -> Dict[str, Any]:
        """
        Get a summary of an error.

        Args:
            error: Exception to summarize

        Returns:
            Dictionary containing error summary
        """
        try:
            return {
                "type": type(error).__name__,
                "message": str(error),
                "module": getattr(error, "__module__", "unknown"),
                "traceback": traceback.format_exc(),
            }
        except Exception as e:
            self.logger.error("Error creating error summary: %s", e)
            return {
                "type": "UnknownError",
                "message": "Error creating error summary",
                "module": "unknown",
                "traceback": "",
            }
