"""
Exceptions package for WIZARD-2.1

Contains all custom exception classes for proper error handling.
"""

from .tob_exceptions import TOBError, TOBFileNotFoundError, TOBParsingError
from .database_exceptions import DatabaseError, DatabaseConnectionError
from .server_exceptions import ServerError, ServerConnectionError, ServerTimeoutError

__all__ = [
    "TOBError",
    "TOBFileNotFoundError", 
    "TOBParsingError",
    "DatabaseError",
    "DatabaseConnectionError",
    "ServerError",
    "ServerConnectionError",
    "ServerTimeoutError",
]
