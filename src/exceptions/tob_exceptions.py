"""
TOB Exceptions for WIZARD-2.1

Custom exception classes for TOB file operations.
"""


class TOBError(Exception):
    """Base exception for TOB file operations."""

    def __init__(self, message: str, error_code: str = None):
        """
        Initialize TOB error.

        Args:
            message: Error message
            error_code: Optional error code
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class TOBFileNotFoundError(TOBError):
    """Exception raised when a TOB file is not found."""

    def __init__(self, message: str, file_path: str = None):
        """
        Initialize TOB file not found error.

        Args:
            message: Error message
            file_path: Path to the file that was not found
        """
        super().__init__(message, "TOB_FILE_NOT_FOUND")
        self.file_path = file_path


class TOBParsingError(TOBError):
    """Exception raised when TOB file parsing fails."""

    def __init__(self, message: str, file_path: str = None, line_number: int = None):
        """
        Initialize TOB parsing error.

        Args:
            message: Error message
            file_path: Path to the file that failed to parse
            line_number: Line number where parsing failed
        """
        super().__init__(message, "TOB_PARSING_ERROR")
        self.file_path = file_path
        self.line_number = line_number


class TOBValidationError(TOBError):
    """Exception raised when TOB file validation fails."""

    def __init__(self, message: str, validation_type: str = None):
        """
        Initialize TOB validation error.

        Args:
            message: Error message
            validation_type: Type of validation that failed
        """
        super().__init__(message, "TOB_VALIDATION_ERROR")
        self.validation_type = validation_type


class TOBDataError(TOBError):
    """Exception raised when TOB data processing fails."""

    def __init__(self, message: str, data_type: str = None):
        """
        Initialize TOB data error.

        Args:
            message: Error message
            data_type: Type of data that caused the error
        """
        super().__init__(message, "TOB_DATA_ERROR")
        self.data_type = data_type


class TOBHeaderError(TOBError):
    """Exception raised when TOB header processing fails."""

    def __init__(self, message: str, header_field: str = None):
        """
        Initialize TOB header error.

        Args:
            message: Error message
            header_field: Header field that caused the error
        """
        super().__init__(message, "TOB_HEADER_ERROR")
        self.header_field = header_field


class TOBSensorError(TOBError):
    """Exception raised when TOB sensor data processing fails."""

    def __init__(self, message: str, sensor_name: str = None):
        """
        Initialize TOB sensor error.

        Args:
            message: Error message
            sensor_name: Name of the sensor that caused the error
        """
        super().__init__(message, "TOB_SENSOR_ERROR")
        self.sensor_name = sensor_name
