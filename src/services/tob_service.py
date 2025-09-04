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

from ..exceptions.tob_exceptions import (TOBError, TOBFileNotFoundError,
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
        Load a TOB file and return a TOBDataModel.

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
                raise TOBFileNotFoundError(f"TOB file not found: {file_path}")

            self.logger.info("Loading TOB file: %s", file_path)

            # Validate file format
            if not self.validate_tob_file(str(file_path)):
                raise TOBValidationError(f"Invalid TOB file format: {file_path}")

            # Parse headers
            headers = self.parse_headers(str(file_path))
            self.logger.debug("Parsed %d headers", len(headers))

            # Parse data
            data = self.parse_data(str(file_path))
            self.logger.debug("Parsed data shape: %s", data.shape)

            # Detect sensors
            sensors = self.get_available_sensors(data)
            self.logger.debug("Detected %d sensors: %s", len(sensors), sensors)

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
                           file_path, len(data) if data is not None else 0, len(sensors))
            return data_model

        except (TOBError, TOBFileNotFoundError, TOBParsingError, TOBValidationError):
            raise
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
        Parse TOB file headers.

        Args:
            file_path: Path to the TOB file

        Returns:
            Dictionary containing parsed headers

        Raises:
            TOBHeaderError: If header parsing fails
        """
        try:
            self.logger.info("Parsing headers from: %s", file_path)
            
            headers = {}
            file_path = Path(file_path)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                line_count = 0
                for line in file:
                    line_count += 1
                    line = line.strip()
                    
                    # Stop at data section (usually starts with numeric data)
                    # But only if we've already parsed some headers
                    if self._is_data_line(line) and len(headers) > 0:
                        break
                    
                    # Parse header lines
                    if ':' in line and not line.startswith('#'):
                        try:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            
                            # Convert numeric values
                            if value.replace('.', '').replace('-', '').replace('+', '').isdigit():
                                try:
                                    if '.' in value:
                                        headers[key] = float(value)
                                    else:
                                        headers[key] = int(value)
                                except ValueError:
                                    headers[key] = value
                            else:
                                headers[key] = value
                                
                        except ValueError:
                            # Skip malformed header lines
                            self.logger.debug("Skipping malformed header line %d: %s", line_count, line)
                            continue
                    
                    # Limit header parsing to prevent infinite loops
                    if line_count > 1000:
                        self.logger.warning("Header parsing stopped after 1000 lines")
                        break
            
            self.logger.debug("Parsed %d header fields", len(headers))
            return headers
            
        except (UnicodeDecodeError, IOError) as e:
            self.logger.error("File reading error parsing headers from %s: %s", file_path, e)
            raise TOBHeaderError(f"Failed to read file for header parsing: {e}") from e
        except Exception as e:
            self.logger.error("Error parsing headers from %s: %s", file_path, e)
            raise TOBHeaderError(f"Failed to parse headers: {e}") from e

    def parse_data(self, file_path: str) -> pd.DataFrame:
        """
        Parse TOB file data into a DataFrame.

        Args:
            file_path: Path to the TOB file

        Returns:
            DataFrame containing the data

        Raises:
            TOBDataError: If data parsing fails
        """
        try:
            self.logger.info("Parsing data from: %s", file_path)
            
            file_path = Path(file_path)
            data_lines = []
            column_names = None
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                line_count = 0
                in_data_section = False
                
                for line in file:
                    line_count += 1
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Skip header lines (contain colons)
                    if ':' in line:
                        continue
                    
                    # Check if we've reached the data section
                    if self._is_data_line(line):
                        in_data_section = True
                        
                        # Try to detect column names from the first data line
                        if column_names is None:
                            column_names = self._detect_column_names(line)
                            if column_names:
                                self.logger.debug("Detected columns: %s", column_names)
                                continue
                    
                    # Parse data lines
                    if in_data_section and self._is_data_line(line):
                        try:
                            data_row = self._parse_data_line(line)
                            if data_row:
                                data_lines.append(data_row)
                        except ValueError as e:
                            self.logger.debug("Skipping malformed data line %d: %s", line_count, e)
                            continue
                    
                    # Limit data parsing to prevent memory issues
                    if len(data_lines) > 1000000:  # 1M rows max
                        self.logger.warning("Data parsing stopped after 1M rows")
                        break
            
            if not data_lines:
                self.logger.warning("No data found in file: %s", file_path)
                return pd.DataFrame()
            
            # Create DataFrame
            if column_names and len(column_names) > 0:
                # Ensure all rows have the same number of columns
                max_cols = max(len(row) for row in data_lines)
                padded_data = []
                for row in data_lines:
                    padded_row = row + [np.nan] * (max_cols - len(row))
                    padded_data.append(padded_row)
                
                # Truncate or extend column names as needed
                if len(column_names) > max_cols:
                    column_names = column_names[:max_cols]
                elif len(column_names) < max_cols:
                    column_names.extend([f"Column_{i}" for i in range(len(column_names), max_cols)])
                
                df = pd.DataFrame(padded_data, columns=column_names)
            else:
                # Fallback: create DataFrame with generic column names
                max_cols = max(len(row) for row in data_lines) if data_lines else 0
                column_names = [f"Column_{i}" for i in range(max_cols)]
                df = pd.DataFrame(data_lines, columns=column_names)
            
            # Clean up the data
            df = self._clean_dataframe(df)
            
            self.logger.info("Successfully parsed %d rows and %d columns", len(df), len(df.columns))
            return df
            
        except (UnicodeDecodeError, IOError) as e:
            self.logger.error("File reading error parsing data from %s: %s", file_path, e)
            raise TOBDataError(f"Failed to read file for data parsing: {e}") from e
        except Exception as e:
            self.logger.error("Error parsing data from %s: %s", file_path, e)
            raise TOBDataError(f"Failed to parse data: {e}") from e

    def get_available_sensors(self, data: pd.DataFrame) -> List[str]:
        """
        Get list of available sensors from data.

        Args:
            data: DataFrame containing sensor data

        Returns:
            List of sensor names
        """
        try:
            self.logger.info("Detecting available sensors")
            
            if data is None or data.empty:
                return []
            
            sensors = []
            
            # Common sensor patterns
            sensor_patterns = [
                r'^NTC\d{2}$',  # NTC01, NTC02, etc.
                r'^PT100$',     # PT100 sensor
                r'^T\d+$',      # T1, T2, etc.
                r'^Temp\d+$',   # Temp1, Temp2, etc.
                r'^Temperature\d+$',  # Temperature1, etc.
                r'^Sensor\d+$', # Sensor1, Sensor2, etc.
            ]
            
            for column in data.columns:
                column_str = str(column).strip()
                
                # Check against sensor patterns
                for pattern in sensor_patterns:
                    if re.match(pattern, column_str, re.IGNORECASE):
                        sensors.append(column_str)
                        break
                
                # Check for temperature-related keywords
                temp_keywords = ['temp', 'temperature', 'ntc', 'pt100', 'sensor']
                if any(keyword in column_str.lower() for keyword in temp_keywords):
                    if column_str not in sensors:
                        sensors.append(column_str)
            
            # Remove duplicates and sort
            sensors = sorted(list(set(sensors)))
            
            self.logger.debug("Detected sensors: %s", sensors)
            return sensors
            
        except Exception as e:
            self.logger.error("Error detecting sensors: %s", e)
            return []

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

    def _is_data_line(self, line: str) -> bool:
        """
        Check if a line contains data (numeric values).

        Args:
            line: Line to check

        Returns:
            True if line contains data, False otherwise
        """
        if not line or line.startswith('#'):
            return False
        
        # Check if line contains mostly numeric values
        parts = line.split()
        if len(parts) < 2:
            return False
        
        # Skip lines that look like headers (contain common header keywords)
        header_keywords = ['time', 'timestamp', 'date', 'sensor', 'ntc', 'pt100', 'temp', 'temperature']
        if any(keyword in line.lower() for keyword in header_keywords):
            return False
        
        numeric_count = 0
        for part in parts:
            try:
                float(part)
                numeric_count += 1
            except ValueError:
                # Check if it's a timestamp or other valid data
                if any(char.isdigit() for char in part):
                    numeric_count += 1
        
        # Consider it a data line if at least 50% of parts are numeric
        return numeric_count >= len(parts) * 0.5

    def _detect_column_names(self, line: str) -> Optional[List[str]]:
        """
        Detect column names from a header line.

        Args:
            line: Header line to analyze

        Returns:
            List of column names or None if not detected
        """
        try:
            # Common header patterns - only detect if line contains time-related keywords
            time_keywords = ['time', 'timestamp', 'date']
            if any(keyword in line.lower() for keyword in time_keywords):
                parts = line.split()
                if len(parts) > 1:
                    return parts
            return None
        except Exception:
            return None

    def _parse_data_line(self, line: str) -> List[float]:
        """
        Parse a single data line into numeric values.

        Args:
            line: Data line to parse

        Returns:
            List of numeric values
        """
        try:
            parts = line.split()
            values = []
            
            for part in parts:
                try:
                    # Try to convert to float
                    value = float(part)
                    values.append(value)
                except ValueError:
                    # Skip non-numeric parts
                    continue
            
            return values
        except Exception:
            return []

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and optimize the DataFrame.

        Args:
            df: DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        try:
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Convert numeric columns to appropriate types
            for column in df.columns:
                if df[column].dtype == 'object':
                    # Try to convert to numeric
                    try:
                        df[column] = pd.to_numeric(df[column], errors='ignore')
                    except Exception:
                        pass
            
            # Remove duplicate rows
            df = df.drop_duplicates()
            
            # Reset index
            df = df.reset_index(drop=True)
            
            return df
            
        except Exception as e:
            self.logger.warning("Error cleaning DataFrame: %s", e)
            return df

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
                raise TOBFileNotFoundError(f"File not found: {file_path}")
            
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
            
        except TOBFileNotFoundError:
            raise
        except Exception as e:
            self.logger.error("Error getting file info for %s: %s", file_path, e)
            raise TOBFileNotFoundError(f"Error accessing file: {file_path}") from e

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
