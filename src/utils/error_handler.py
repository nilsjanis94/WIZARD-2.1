"""
Error Handler for WIZARD-2.1

Centralized error handling and user feedback.
"""

import logging
import traceback
from typing import Any, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget


class ErrorHandler(QObject):
    """
    Centralized error handler for the application.

    Signals:
        error_occurred: Emitted when an error occurs
        warning_occurred: Emitted when a warning occurs
        info_message: Emitted when an info message is shown
    """

    # Signals for thread-safe GUI operations
    error_occurred = pyqtSignal(str, str, object)  # error_type, error_message, parent_widget
    warning_occurred = pyqtSignal(str, object)  # warning_message, parent_widget
    info_message = pyqtSignal(str, object)  # info_message, parent_widget

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

            # Emit signal for thread-safe GUI update
            self.error_occurred.emit(error_type, error_message, parent)

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

            # Emit signal for thread-safe GUI update
            self.warning_occurred.emit(message, parent)

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

            # Emit signal for thread-safe GUI update
            self.info_message.emit(message, parent)

        except Exception as e:
            self.logger.error("Error in info handling: %s", e)


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
