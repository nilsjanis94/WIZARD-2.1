"""
TOB Service for WIZARD-2.1

Service for TOB file operations and data processing.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np

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

from ..exceptions.tob_exceptions import (TOBError, TOBFileNotFoundError as WizTOBFileNotFoundError,
                                         TOBParsingError, TOBValidationError,
                                         TOBDataError, TOBHeaderError)
from ..models.tob_data_model import TOBDataModel


class TOBService:
    """Service for TOB file operations."""

    def __init__(self):
        """Initialize the TOB service."""
        self.logger = logging.getLogger(__name__)

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
                raise TOBParsingError("TOB DataLoader package not available - please install tob_dataloader")

            # Use the existing tob_dataloader package
            loader = TOBDataLoader()
            headers, data = loader.load_data(str(file_path))

            self.logger.debug("Parsed headers with %d keys", len(headers))
            self.logger.debug("Parsed data shape: %s", data.shape if data is not None else "None")

            # Extract sensors from DataFrame columns
            sensors = []
            if data is not None and not data.empty:
                # Filter out non-sensor columns
                non_sensor_columns = [
                    'time', 'timestamp', 'datasets', 'date', 'datetime',
                    'vbatt', 'vaccu', 'press', 'vheat', 'iheat',
                    'tiltx', 'tilty', 'accz', 'stat',
                    'intt_time', 'intt_date'
                ]

                for column in data.columns:
                    column_str = str(column).strip().lower()
                    if column_str and column_str not in non_sensor_columns:
                        sensors.append(str(column).strip())

            sensors = sorted(list(set(sensors)))  # Remove duplicates and sort
            self.logger.debug("Detected %d sensors: %s", len(sensors), sensors[:5] if sensors else [])

            # Create data model
            data_model = TOBDataModel(
                file_path=str(file_path),
                file_size=file_path.stat().st_size,
                headers=headers,
                data=data,
                sensors=sensors,
                data_points=len(data) if data is not None else 0,
            )

            # Validate data integrity
            validation_results = data_model.validate_data_integrity()
            if not validation_results["is_valid"]:
                self.logger.warning("Data integrity issues found: %s", validation_results["errors"])

            self.logger.info("Successfully loaded TOB file: %s (%d data points, %d sensors)",
                           file_path.name, len(data) if data is not None else 0, len(sensors))
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
            raise TOBFileNotFoundError(f"TOB file not found or inaccessible: {file_path}") from e
        except (ValueError, IOError) as e:
            self.logger.error("Data format or IO error loading TOB file %s: %s", file_path, e)
            raise TOBParsingError(f"Failed to parse TOB file: {e}") from e
        except Exception as e:
            self.logger.error("Unexpected error loading TOB file %s: %s", file_path, e)
            raise TOBError(f"An unexpected error occurred while loading TOB file: {e}") from e

    def parse_headers(self, file_path: str) -> Dict[str, Any]:
        """
        DEPRECATED: This method is no longer used.
        Headers are now parsed by the tob_dataloader package in load_tob_file().
        """
        self.logger.warning("parse_headers() is deprecated - headers are parsed by tob_dataloader")
        return {}

    def parse_data(self, file_path: str) -> pd.DataFrame:
        """
        DEPRECATED: This method is no longer used.
        Data is now parsed by the tob_dataloader package in load_tob_file().
        """
        self.logger.warning("parse_data() is deprecated - data is parsed by tob_dataloader")
        return pd.DataFrame()

    def validate_tob_file(self, file_path: str) -> bool:
        """
        Validate if a file is a valid TOB file.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if valid TOB file, False otherwise
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
            self.logger.error("Unexpected error validating TOB file %s: %s", file_path, e)
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