"""
Error Service for WIZARD-2.1

Service for error handling and user feedback.
"""

from typing import Dict, Any, Optional
import logging
from PyQt6.QtWidgets import QMessageBox, QWidget

from ..exceptions.tob_exceptions import TOBError
from ..exceptions.server_exceptions import ServerError


class ErrorService:
    """Service for error handling and user feedback."""
    
    def __init__(self):
        """Initialize the error service."""
        self.logger = logging.getLogger(__name__)
        
    def handle_error(self, error: Exception, parent: Optional[QWidget] = None) -> None:
        """
        Handle an error and show appropriate user feedback.
        
        Args:
            error: Exception to handle
            parent: Parent widget for dialogs
        """
        try:
            error_type = type(error).__name__
            error_message = str(error)
            
            self.logger.error(f"Error occurred: {error_type} - {error_message}")
            
            # Show user-friendly error dialog
            self._show_error_dialog(error_type, error_message, parent)
            
        except Exception as e:
            self.logger.error(f"Error in error handling: {e}")
            
    def _show_error_dialog(self, error_type: str, error_message: str, 
                          parent: Optional[QWidget] = None) -> None:
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
            msg_box.setDetailedText(f"Error Type: {error_type}\nDetails: {error_message}")
            msg_box.exec()
            
        except Exception as e:
            self.logger.error(f"Error showing error dialog: {e}")
            
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
            'TOBFileNotFoundError': "The TOB file could not be found. Please check the file path and try again.",
            'TOBParsingError': "There was an error reading the TOB file. The file may be corrupted or in an unsupported format.",
            'ServerConnectionError': "Could not connect to the server. Please check your internet connection and try again.",
            'ServerTimeoutError': "The server request timed out. Please try again later.",
            'FileNotFoundError': "The specified file could not be found. Please check the file path and try again.",
            'PermissionError': "You don't have permission to access this file. Please check the file permissions.",
            'ValueError': "Invalid data format. Please check your input and try again.",
            'KeyError': "Required data is missing. Please check your input and try again."
        }
        
        # Return user-friendly message or fallback to technical message
        return error_messages.get(error_type, f"An error occurred: {error_message}")
        
    def log_error(self, error: Exception, context: Optional[str] = None) -> None:
        """
        Log an error with context.
        
        Args:
            error: Exception to log
            context: Optional context information
        """
        try:
            error_type = type(error).__name__
            error_message = str(error)
            
            log_message = f"Error: {error_type} - {error_message}"
            if context:
                log_message = f"{context}: {log_message}"
                
            self.logger.error(log_message, exc_info=True)
            
        except Exception as e:
            self.logger.error(f"Error in error logging: {e}")
            
    def handle_warning(self, message: str, parent: Optional[QWidget] = None) -> None:
        """
        Handle a warning and show user feedback.
        
        Args:
            message: Warning message
            parent: Parent widget for dialogs
        """
        try:
            self.logger.warning(message)
            
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(message)
            msg_box.exec()
            
        except Exception as e:
            self.logger.error(f"Error showing warning dialog: {e}")
            
    def handle_info(self, message: str, parent: Optional[QWidget] = None) -> None:
        """
        Handle an info message and show user feedback.
        
        Args:
            message: Info message
            parent: Parent widget for dialogs
        """
        try:
            self.logger.info(message)
            
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Information")
            msg_box.setText(message)
            msg_box.exec()
            
        except Exception as e:
            self.logger.error(f"Error showing info dialog: {e}")
