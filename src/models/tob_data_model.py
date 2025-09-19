"""
TOB Data Model for WIZARD-2.1

Handles TOB file data structure and operations.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
from pydantic import BaseModel, Field


class TOBDataModel(BaseModel):
    """
    Model for TOB file data structure.

    Attributes:
        headers: Dictionary containing TOB file headers
        data: DataFrame containing temperature and sensor data
        file_path: Path to the original TOB file
        file_size: Size of the TOB file in bytes
        data_points: Number of data points in the file
        sensors: List of available sensors
    """

    headers: Dict[str, Any] = Field(default_factory=dict)
    data: Optional[pd.DataFrame] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    data_points: Optional[int] = None
    sensors: List[str] = Field(default_factory=list)

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    def get_sensor_data(self, sensor_name: str) -> Optional[pd.Series]:
        """
        Get data for a specific sensor.

        Args:
            sensor_name: Name of the sensor

        Returns:
            Series containing sensor data or None if not found
        """
        if self.data is not None and sensor_name in self.data.columns:
            return self.data[sensor_name]
        return None

    def get_ntc_sensors(self) -> List[str]:
        """
        Get list of NTC sensor names.

        Returns:
            List of NTC sensor names
        """
        return [sensor for sensor in self.sensors if sensor.startswith("NTC")]

    def get_pt100_sensor(self) -> Optional[str]:
        """
        Get PT100 sensor name.

        Returns:
            PT100 sensor name or None if not found
        """
        # First check sensors list if available
        if "Temp" in self.sensors:
            return "Temp"

        # Fallback: check data columns if data exists
        if self.data is not None and "Temp" in self.data.columns:
            return "Temp"

        return None

    def get_time_column(self) -> Optional[pd.Series]:
        """
        Get the time column data.

        Returns:
            Time column data or None if not found
        """
        if self.data is None:
            return None

        # Try common time column names
        time_columns = ["Time", "time", "TIMESTAMP", "timestamp", "Datasets"]
        for col in time_columns:
            if col in self.data.columns:
                return self.data[col]

        # If no explicit time column, create index-based time
        if len(self.data) > 0:
            return pd.Series(range(len(self.data)), name="Time")

        return None

    def get_time_column_name(self) -> Optional[str]:
        """
        Get the time column name.

        Returns:
            Time column name or None if not found
        """
        if self.data is None:
            return None

        time_columns = ["Time", "time", "TIMESTAMP", "timestamp", "Datasets"]
        for col in time_columns:
            if col in self.data.columns:
                return col
        return None

    def get_data_range(self) -> Dict[str, Any]:
        """
        Get data range information.

        Returns:
            Dictionary containing min/max values and time range
        """
        if self.data is None:
            return {}

        result = {"time_range": None, "sensor_ranges": {}}

        time_col = self.get_time_column()
        if time_col is not None and not time_col.empty:
            result["time_range"] = {
                "min": time_col.min(),
                "max": time_col.max(),
            }

        for sensor in self.sensors:
            if sensor in self.data.columns:
                result["sensor_ranges"][sensor] = {
                    "min": self.data[sensor].min(),
                    "max": self.data[sensor].max(),
                }

        return result

    def get_metadata(self) -> Dict[str, Any]:
        """
        Get comprehensive metadata about the TOB file.

        Returns:
            Dictionary containing file metadata
        """
        metadata = {
            "file_path": self.file_path,
            "file_size": self.file_size,
            "data_points": self.data_points,
            "sensors": self.sensors,
            "headers": self.headers,
            "data_shape": self.data.shape if self.data is not None else (0, 0),
            "time_range": self.get_data_range().get("time_range"),
            "sensor_count": len(self.sensors),
            "ntc_sensors": self.get_ntc_sensors(),
            "pt100_sensor": self.get_pt100_sensor(),
        }
        return metadata

    def validate_data_integrity(self) -> Dict[str, Any]:
        """
        Validate the integrity of the loaded data.

        Returns:
            Dictionary containing validation results
        """
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "data_quality": "unknown",
        }

        if self.data is None:
            validation_results["is_valid"] = False
            validation_results["errors"].append("No data loaded")
            validation_results["data_quality"] = "poor"
            return validation_results

        # Check for missing values
        missing_data = self.data.isnull().sum()
        if missing_data.any():
            validation_results["warnings"].append(f"Missing data in columns: {missing_data[missing_data > 0].to_dict()}")

        # Check for duplicate timestamps
        time_col_name = self.get_time_column_name()
        if time_col_name and time_col_name in self.data.columns:
            if self.data[time_col_name].duplicated().any():
                validation_results["warnings"].append("Duplicate timestamps found")

        # Check data consistency
        if len(self.data) == 0:
            validation_results["is_valid"] = False
            validation_results["errors"].append("Empty dataset")

        # Assess data quality
        if validation_results["errors"]:
            validation_results["data_quality"] = "poor"
        elif validation_results["warnings"]:
            validation_results["data_quality"] = "fair"
        else:
            validation_results["data_quality"] = "good"

        return validation_results

    def get_sensor_statistics(self) -> Dict[str, Dict[str, float]]:
        """
        Get statistical information for all sensors.

        Returns:
            Dictionary containing sensor statistics
        """
        if self.data is None:
            return {}

        statistics = {}
        for sensor in self.sensors:
            if sensor in self.data.columns:
                sensor_data = self.data[sensor]
                statistics[sensor] = {
                    "mean": float(sensor_data.mean()),
                    "std": float(sensor_data.std()),
                    "min": float(sensor_data.min()),
                    "max": float(sensor_data.max()),
                    "median": float(sensor_data.median()),
                    "count": int(sensor_data.count()),
                }

        return statistics
