"""
Server Exceptions for WIZARD-2.1

Custom exception classes for server communication operations.
"""


class ServerError(Exception):
    """Base exception for server operations."""

    def __init__(self, message: str, error_code: str = None):
        """
        Initialize server error.

        Args:
            message: Error message
            error_code: Optional error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ServerConnectionError(ServerError):
    """Exception raised when server connection fails."""

    def __init__(self, message: str, url: str = None, status_code: int = None):
        """
        Initialize server connection error.

        Args:
            message: Error message
            url: URL that failed to connect
            status_code: HTTP status code
        """
        super().__init__(message, "SERVER_CONNECTION_ERROR")
        self.url = url
        self.status_code = status_code


class ServerTimeoutError(ServerError):
    """Exception raised when server request times out."""

    def __init__(self, message: str, url: str = None, timeout: float = None):
        """
        Initialize server timeout error.

        Args:
            message: Error message
            url: URL that timed out
            timeout: Timeout value in seconds
        """
        super().__init__(message, "SERVER_TIMEOUT_ERROR")
        self.url = url
        self.timeout = timeout


class ServerAuthenticationError(ServerError):
    """Exception raised when server authentication fails."""

    def __init__(self, message: str, url: str = None, status_code: int = None):
        """
        Initialize server authentication error.

        Args:
            message: Error message
            url: URL that failed authentication
            status_code: HTTP status code
        """
        super().__init__(message, "SERVER_AUTHENTICATION_ERROR")
        self.url = url
        self.status_code = status_code


class ServerResponseError(ServerError):
    """Exception raised when server response is invalid."""

    def __init__(self, message: str, url: str = None, response_data: str = None):
        """
        Initialize server response error.

        Args:
            message: Error message
            url: URL that returned invalid response
            response_data: Response data that was invalid
        """
        super().__init__(message, "SERVER_RESPONSE_ERROR")
        self.url = url
        self.response_data = response_data


class ServerUploadError(ServerError):
    """Exception raised when file upload to server fails."""

    def __init__(self, message: str, url: str = None, file_path: str = None):
        """
        Initialize server upload error.

        Args:
            message: Error message
            url: URL that failed to upload
            file_path: Path to the file that failed to upload
        """
        super().__init__(message, "SERVER_UPLOAD_ERROR")
        self.url = url
        self.file_path = file_path


class ServerStatusError(ServerError):
    """Exception raised when server status query fails."""

    def __init__(self, message: str, url: str = None, job_id: str = None):
        """
        Initialize server status error.

        Args:
            message: Error message
            url: URL that failed status query
            job_id: Job ID that failed status query
        """
        super().__init__(message, "SERVER_STATUS_ERROR")
        self.url = url
        self.job_id = job_id
