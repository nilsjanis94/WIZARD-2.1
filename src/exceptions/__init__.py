"""
Exceptions package for WIZARD-2.1

Contains all custom exception classes for proper error handling.
"""

from .database_exceptions import DatabaseConnectionError, DatabaseError
from .server_exceptions import ServerConnectionError, ServerError, ServerTimeoutError
from .tob_exceptions import TOBError, TOBFileNotFoundError, TOBParsingError

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
