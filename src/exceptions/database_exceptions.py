"""
Database Exceptions for WIZARD-2.1

Custom exception classes for database operations.
Note: These are kept for potential future use, as the current
implementation uses encrypted files instead of a database.
"""


class DatabaseError(Exception):
    """Base exception for database operations."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize database error.
        
        Args:
            message: Error message
            error_code: Optional error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""
    
    def __init__(self, message: str, connection_string: str = None):
        """
        Initialize database connection error.
        
        Args:
            message: Error message
            connection_string: Connection string that failed
        """
        super().__init__(message, "DATABASE_CONNECTION_ERROR")
        self.connection_string = connection_string


class DatabaseQueryError(DatabaseError):
    """Exception raised when database query fails."""
    
    def __init__(self, message: str, query: str = None):
        """
        Initialize database query error.
        
        Args:
            message: Error message
            query: Query that failed
        """
        super().__init__(message, "DATABASE_QUERY_ERROR")
        self.query = query


class DatabaseTransactionError(DatabaseError):
    """Exception raised when database transaction fails."""
    
    def __init__(self, message: str, transaction_id: str = None):
        """
        Initialize database transaction error.
        
        Args:
            message: Error message
            transaction_id: ID of the failed transaction
        """
        super().__init__(message, "DATABASE_TRANSACTION_ERROR")
        self.transaction_id = transaction_id


class DatabaseSchemaError(DatabaseError):
    """Exception raised when database schema operations fail."""
    
    def __init__(self, message: str, table_name: str = None):
        """
        Initialize database schema error.
        
        Args:
            message: Error message
            table_name: Name of the table that caused the error
        """
        super().__init__(message, "DATABASE_SCHEMA_ERROR")
        self.table_name = table_name
