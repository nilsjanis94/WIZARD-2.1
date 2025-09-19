"""
Data Service for WIZARD-2.1

Service for data processing, analysis operations, and data metrics management.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
from PyQt6.QtWidgets import QLineEdit

from ..models.tob_data_model import TOBDataModel
from .analytics_service import AnalyticsService


class DataService:
    """Service for data processing and analysis."""

    def __init__(self, analytics_service: Optional[AnalyticsService] = None):
        """Initialize the data service."""
        self.logger = logging.getLogger(__name__)
        self.analytics_service = analytics_service or AnalyticsService()

    def process_tob_data(self, data_model: TOBDataModel) -> Dict[str, Any]:
        """
        Process TOB data for visualization and analysis.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Dictionary containing processed data
        """
        try:
            self.logger.info("Processing TOB data")

            if data_model.data is None:
                return {}

            processed_data = {
                "raw_data": data_model.data,
                "sensors": data_model.sensors,
                "time_range": self._get_time_range(data_model),
                "sensor_ranges": self._get_sensor_ranges(data_model),
                "metrics": self._calculate_metrics(data_model),
            }

            self.logger.info("Successfully processed TOB data")
            return processed_data

        except (ValueError, KeyError) as e:
            self.logger.error("Data validation error: %s", e)
            return {}
        except Exception as e:
            self.logger.error("Unexpected error processing TOB data: %s", e)
            return {}

    def _get_time_range(self, data_model: TOBDataModel) -> Dict[str, Any]:
        """
        Get time range from data.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Dictionary containing time range information
        """
        try:
            time_col_name = data_model.get_time_column_name()
            if time_col_name and data_model.data is not None:
                time_data = data_model.data[time_col_name]
                if len(time_data) == 0:
                    return {}
                return {
                    "min": time_data.min(),
                    "max": time_data.max(),
                    "duration": time_data.max() - time_data.min(),
                    "count": len(time_data),
                }
            return {}
        except (ValueError, KeyError) as e:
            self.logger.error("Time data validation error: %s", e)
            return {}
        except Exception as e:
            self.logger.error("Unexpected error getting time range: %s", e)
            return {}

    def _get_sensor_ranges(self, data_model: TOBDataModel) -> Dict[str, Dict[str, Any]]:
        """
        Get sensor data ranges.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Dictionary containing sensor ranges
        """
        try:
            ranges = {}
            if data_model.data is not None:
                for sensor in data_model.sensors:
                    if sensor in data_model.data.columns:
                        sensor_data = data_model.data[sensor]
                        ranges[sensor] = {
                            "min": sensor_data.min(),
                            "max": sensor_data.max(),
                            "mean": sensor_data.mean(),
                            "std": sensor_data.std(),
                            "count": len(sensor_data),
                        }
            return ranges
        except Exception as e:
            self.logger.error("Error getting sensor ranges: %s", e)
            return {}

    def _calculate_metrics(self, data_model: TOBDataModel) -> Dict[str, Any]:
        """
        Calculate data metrics using the analytics service.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Dictionary containing calculated metrics
        """
        try:
            return self.analytics_service.calculate_metrics(data_model)
        except Exception as e:
            self.logger.error("Error calculating metrics: %s", e)
            return {}





    def filter_sensor_data(
        self, data: pd.DataFrame, sensor_name: str, time_range: Optional[tuple] = None
    ) -> pd.DataFrame:
        """
        Filter sensor data by time range.

        Args:
            data: DataFrame containing sensor data
            sensor_name: Name of the sensor
            time_range: Optional time range tuple (start, end)

        Returns:
            Filtered DataFrame
        """
        try:
            if sensor_name not in data.columns:
                return pd.DataFrame()

            filtered_data = data[[sensor_name]].copy()

            if time_range:
                # TODO: Implement time filtering
                pass

            return filtered_data

        except Exception as e:
            self.logger.error("Error filtering sensor data: %s", e)
            return pd.DataFrame()

    def reset_data_metrics(self, metrics_widgets: Dict[str, QLineEdit]) -> None:
        """
        Reset data metrics widgets to default values.

        Args:
            metrics_widgets: Dictionary containing metric widget references
        """
        try:
            for widget in metrics_widgets.values():
                if widget:
                    widget.setText("-")

            self.logger.debug("Data metrics reset to default values")

        except Exception as e:
            self.logger.error("Failed to reset data metrics: %s", e)

    def update_data_metrics(
        self, metrics_widgets: Dict[str, QLineEdit], metrics: Dict[str, Any]
    ) -> None:
        """
        Update data metrics widgets with calculated values.

        Args:
            metrics_widgets: Dictionary containing metric widget references
            metrics: Dictionary containing metric values
        """
        try:
            if "mean_hp_power" in metrics and "mean_hp_power_value" in metrics_widgets:
                if metrics_widgets["mean_hp_power_value"]:
                    metrics_widgets["mean_hp_power_value"].setText(
                        str(metrics["mean_hp_power"])
                    )

            if "max_v_accu" in metrics and "max_v_accu_value" in metrics_widgets:
                if metrics_widgets["max_v_accu_value"]:
                    metrics_widgets["max_v_accu_value"].setText(
                        str(metrics["max_v_accu"])
                    )

            if "tilt_status" in metrics and "tilt_status_value" in metrics_widgets:
                if metrics_widgets["tilt_status_value"]:
                    metrics_widgets["tilt_status_value"].setText(
                        str(metrics["tilt_status"])
                    )

            if "mean_press" in metrics and "mean_press_value" in metrics_widgets:
                if metrics_widgets["mean_press_value"]:
                    metrics_widgets["mean_press_value"].setText(
                        str(metrics["mean_press"])
                    )

            self.logger.debug("Data metrics updated successfully")

        except Exception as e:
            self.logger.error("Failed to update data metrics: %s", e)
