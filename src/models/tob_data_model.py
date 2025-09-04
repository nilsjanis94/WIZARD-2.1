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
        pt100_sensors = [sensor for sensor in self.sensors if sensor == "PT100"]
        return pt100_sensors[0] if pt100_sensors else None

    def get_time_column(self) -> Optional[str]:
        """
        Get the time column name.

        Returns:
            Time column name or None if not found
        """
        time_columns = ["Time", "time", "TIMESTAMP", "timestamp"]
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
        if time_col:
            result["time_range"] = {
                "min": self.data[time_col].min(),
                "max": self.data[time_col].max(),
            }

        for sensor in self.sensors:
            if sensor in self.data.columns:
                result["sensor_ranges"][sensor] = {
                    "min": self.data[sensor].min(),
                    "max": self.data[sensor].max(),
                }

        return result
