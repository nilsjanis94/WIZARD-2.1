"""
TOB Service for WIZARD-2.1

Service for TOB file operations and data processing.
"""

import logging
import re
import signal
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Use the existing tob_dataloader package
try:
    from tob_dataloader import DataLoader as TOBDataLoader
    from tob_dataloader.exceptions import TOBFileNotFoundError, TOBParseError

    TOB_DATALOADER_AVAILABLE = True
except ImportError:
    # Fallback if package not available
    TOBDataLoader = None
    TOBFileNotFoundError = Exception
    TOBParseError = Exception
    TOB_DATALOADER_AVAILABLE = False

from ..exceptions.tob_exceptions import (
    TOBDataError,
    TOBError,
)
from ..exceptions.tob_exceptions import TOBFileNotFoundError as WizTOBFileNotFoundError
from ..exceptions.tob_exceptions import (
    TOBHeaderError,
    TOBParsingError,
    TOBValidationError,
)
from ..models.tob_data_model import TOBDataModel


class TOBService:
    """Service for TOB file operations."""

    # Validation constants
    MAX_FILE_SIZE_MB = 100
    MAX_MEMORY_MB = 2000  # 2GB
    LOAD_TIMEOUT_SECONDS = 30
    MAX_DATA_POINTS = 1000000  # 1 million data points

    def __init__(self):
        """Initialize the TOB service."""
        self.logger = logging.getLogger(__name__)

    def validate_tob_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a TOB file before loading.

        Args:
            file_path: Path to the TOB file

        Returns:
            Dict with validation results:
            - 'valid': bool
            - 'file_size_mb': float
            - 'estimated_memory_mb': float
            - 'error_message': str (if not valid)

        Raises:
            TOBFileNotFoundError: If file doesn't exist
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise WizTOBFileNotFoundError(f"TOB file not found: {file_path}")

            # Check file size
            file_size_bytes = file_path.stat().st_size
            file_size_mb = file_size_bytes / (1024 * 1024)

            if file_size_mb > self.MAX_FILE_SIZE_MB:
                return {
                    "valid": False,
                    "file_size_mb": file_size_mb,
                    "estimated_memory_mb": 0,
                    "error_message": f"File too large ({file_size_mb:.1f}MB > {self.MAX_FILE_SIZE_MB}MB limit)",
                }

            # Rough estimation of memory usage (DataFrame is typically 2-3x file size)
            estimated_memory_mb = file_size_mb * 2.5

            if estimated_memory_mb > self.MAX_MEMORY_MB:
                return {
                    "valid": False,
                    "file_size_mb": file_size_mb,
                    "estimated_memory_mb": estimated_memory_mb,
                    "error_message": f"Estimated memory usage too high ({estimated_memory_mb:.1f}MB > {self.MAX_MEMORY_MB}MB limit)",
                }

            return {
                "valid": True,
                "file_size_mb": file_size_mb,
                "estimated_memory_mb": estimated_memory_mb,
                "error_message": None,
            }

        except WizTOBFileNotFoundError:
            raise
        except Exception as e:
            return {
                "valid": False,
                "file_size_mb": 0,
                "estimated_memory_mb": 0,
                "error_message": f"Validation error: {str(e)}",
            }

    def _timeout_handler(self, signum, frame):
        """Signal handler for timeout."""
        raise TimeoutError("TOB file loading timed out")

    def load_tob_file_with_timeout(
        self, file_path: str, timeout_seconds: Optional[int] = None
    ) -> TOBDataModel:
        """
        Load a TOB file with timeout protection.

        Args:
            file_path: Path to the TOB file
            timeout_seconds: Timeout in seconds (default: LOAD_TIMEOUT_SECONDS)

        Returns:
            TOBDataModel instance

        Raises:
            TimeoutError: If loading takes too long
            TOBFileNotFoundError: If file doesn't exist
            TOBParsingError: If file parsing fails
            TOBValidationError: If file validation fails
        """
        if timeout_seconds is None:
            timeout_seconds = self.LOAD_TIMEOUT_SECONDS

        self.logger.info(
            "Loading TOB file with %ds timeout: %s", timeout_seconds, file_path
        )

        # Set up timeout signal
        old_handler = signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(timeout_seconds)

        try:
            # Load the file
            result = self.load_tob_file(file_path)
            signal.alarm(0)  # Cancel alarm

            # Additional validation after loading
            self._validate_loaded_data(result)

            return result

        except TimeoutError:
            self.logger.error(
                "TOB file loading timed out after %ds: %s", timeout_seconds, file_path
            )
            raise
        finally:
            # Restore original signal handler
            signal.signal(signal.SIGALRM, old_handler)
            signal.alarm(0)

    def _validate_loaded_data(self, tob_data: TOBDataModel) -> None:
        """
        Validate loaded TOB data for size and quality constraints.

        Args:
            tob_data: Loaded TOBDataModel

        Raises:
            TOBValidationError: If validation fails
        """
        if tob_data.data is None or tob_data.data.empty:
            raise TOBValidationError("TOB file contains no data")

        # Check data points limit
        data_points = len(tob_data.data)
        if data_points > self.MAX_DATA_POINTS:
            raise TOBValidationError(
                f"Too many data points ({data_points} > {self.MAX_DATA_POINTS} limit)"
            )

        # Check memory usage
        memory_usage_mb = tob_data.data.memory_usage(deep=True).sum() / (1024 * 1024)
        if memory_usage_mb > self.MAX_MEMORY_MB:
            raise TOBValidationError(
                f"Data memory usage too high ({memory_usage_mb:.1f}MB > {self.MAX_MEMORY_MB}MB limit)"
            )

        self.logger.debug(
            "TOB data validation passed: %d points, %.1fMB memory",
            data_points,
            memory_usage_mb,
        )

    def load_tob_file(self, file_path: str) -> TOBDataModel:
        """
        Load a TOB file and return a TOBDataModel using the tob_dataloader package.

        Args:
            file_path: Path to the TOB file

        Returns:
            TOBDataModel instance

        Raises:
            TOBFileNotFoundError: If file doesn't exist
            TOBParsingError: If file parsing fails
            TOBValidationError: If file validation fails
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise WizTOBFileNotFoundError(f"TOB file not found: {file_path}")

            self.logger.info("Loading TOB file: %s", file_path)

            if not TOB_DATALOADER_AVAILABLE:
                raise TOBParsingError(
                    "TOB DataLoader package not available - please install tob_dataloader"
                )

            # Use the existing tob_dataloader package
            loader = TOBDataLoader()
            headers, data = loader.load_data(str(file_path))

            self.logger.debug("Parsed headers with %d keys", len(headers))
            self.logger.debug(
                "Parsed data shape: %s", data.shape if data is not None else "None"
            )

            # Extract sensors from DataFrame columns
            sensors = []
            if data is not None and not data.empty:
                # Filter out non-sensor columns
                non_sensor_columns = [
                    "time",
                    "timestamp",
                    "datasets",
                    "date",
                    "datetime",
                    "vbatt",
                    "vaccu",
                    "press",
                    "vheat",
                    "iheat",
                    "tiltx",
                    "tilty",
                    "accz",
                    "stat",
                    "intt_time",
                    "intt_date",
                ]

                for column in data.columns:
                    column_str = str(column).strip().lower()
                    if column_str and column_str not in non_sensor_columns:
                        sensors.append(str(column).strip())

            sensors = sorted(list(set(sensors)))  # Remove duplicates and sort
            self.logger.debug(
                "Detected %d sensors: %s", len(sensors), sensors[:5] if sensors else []
            )

            # Create data model
            data_model = TOBDataModel(
                file_path=str(file_path),
                file_name=file_path.name,
                file_size=file_path.stat().st_size,
                headers=headers,
                data=data,
                sensors=sensors,
                data_points=len(data) if data is not None else 0,
            )

            # Validate data integrity
            validation_results = data_model.validate_data_integrity()
            if not validation_results["is_valid"]:
                self.logger.warning(
                    "Data integrity issues found: %s", validation_results["errors"]
                )

            self.logger.info(
                "Successfully loaded TOB file: %s (%d data points, %d sensors)",
                file_path.name,
                len(data) if data is not None else 0,
                len(sensors),
            )
            return data_model

        except (TOBFileNotFoundError, TOBParseError) as e:
            # Convert tob_dataloader exceptions to our exception types
            if isinstance(e, TOBFileNotFoundError):
                raise WizTOBFileNotFoundError(str(e))
            else:
                raise TOBParsingError(f"Error parsing TOB file: {str(e)}")
        except Exception as e:
            self.logger.error("Unexpected error loading TOB file: %s", e)
            raise TOBParsingError(f"Unexpected error loading TOB file: {str(e)}")
        except (FileNotFoundError, PermissionError) as e:
            self.logger.error("File access error loading TOB file %s: %s", file_path, e)
            raise TOBFileNotFoundError(
                f"TOB file not found or inaccessible: {file_path}"
            ) from e
        except (ValueError, IOError) as e:
            self.logger.error(
                "Data format or IO error loading TOB file %s: %s", file_path, e
            )
            raise TOBParsingError(f"Failed to parse TOB file: {e}") from e
        except Exception as e:
            self.logger.error("Unexpected error loading TOB file %s: %s", file_path, e)
            raise TOBError(
                f"An unexpected error occurred while loading TOB file: {e}"
            ) from e

    def parse_headers(self, file_path: str) -> Dict[str, Any]:
        """
        DEPRECATED: This method is no longer used.
        Headers are now parsed by the tob_dataloader package in load_tob_file().
        """
        self.logger.warning(
            "parse_headers() is deprecated - headers are parsed by tob_dataloader"
        )
        return {}

    def parse_data(self, file_path: str) -> pd.DataFrame:
        """
        DEPRECATED: This method is no longer used.
        Data is now parsed by the tob_dataloader package in load_tob_file().
        """
        self.logger.warning(
            "parse_data() is deprecated - data is parsed by tob_dataloader"
        )
        return pd.DataFrame()

    def is_valid_tob_file_format(self, file_path: str) -> bool:
        """
        Check if a file has a valid TOB file extension.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if valid TOB file extension, False otherwise
        """
        try:
            file_path = Path(file_path)

            # Check file extension
            if file_path.suffix.lower() not in [".tob", ".flx"]:
                return False

            # Check if file exists and is readable
            if not file_path.exists() or not file_path.is_file():
                return False

            # Basic file size check (must be > 0 bytes)
            if file_path.stat().st_size == 0:
                return False

            return True

        except (OSError, ValueError) as e:
            self.logger.error("Error validating TOB file %s: %s", file_path, e)
            return False
        except Exception as e:
            self.logger.error(
                "Unexpected error validating TOB file %s: %s", file_path, e
            )
            return False

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive information about a TOB file.

        Args:
            file_path: Path to the TOB file

        Returns:
            Dictionary containing file information

        Raises:
            TOBFileNotFoundError: If file doesn't exist
        """
        try:
            file_path = Path(file_path)

            if not file_path.exists():
                raise WizTOBFileNotFoundError(f"File not found: {file_path}")

            info = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "file_extension": file_path.suffix.lower(),
                "is_valid": self.validate_tob_file(str(file_path)),
                "created_time": file_path.stat().st_ctime,
                "modified_time": file_path.stat().st_mtime,
            }

            return info

        except WizTOBFileNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Error getting file info for %s: %s", file_path, e)
            raise WizTOBFileNotFoundError(f"Error accessing file: {file_path}") from e

    def estimate_processing_time(self, file_path: str) -> float:
        """
        Estimate processing time for a TOB file.

        Args:
            file_path: Path to the TOB file

        Returns:
            Estimated processing time in seconds
        """
        try:
            file_path = Path(file_path)
            file_size = file_path.stat().st_size

            # Rough estimation: 1MB per second processing time
            estimated_time = file_size / (1024 * 1024)  # Convert to seconds

            # Minimum 1 second, maximum 300 seconds (5 minutes)
            return max(1.0, min(estimated_time, 300.0))

        except Exception:
            return 10.0  # Default fallback
