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


class DataService:
    """Service for data processing and analysis."""

    def __init__(self):
        """Initialize the data service."""
        self.logger = logging.getLogger(__name__)

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
            time_col = data_model.get_time_column()
            if time_col and data_model.data is not None:
                time_data = data_model.data[time_col]
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
        Calculate data metrics.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Dictionary containing calculated metrics
        """
        try:
            metrics = {}

            if data_model.data is not None:
                # Calculate Mean HP-Power (excluding noise during non-heat pulse periods)
                metrics["mean_hp_power"] = self._calculate_mean_hp_power(data_model)

                # Calculate Max Vaccu
                metrics["max_vaccu"] = self._calculate_max_vaccu(data_model)

                # Calculate Tilt Status
                metrics["tilt_status"] = self._calculate_tilt_status(data_model)

                # Calculate Mean Press
                metrics["mean_press"] = self._calculate_mean_press(data_model)

            return metrics

        except Exception as e:
            self.logger.error("Error calculating metrics: %s", e)
            return {}

    def _calculate_mean_hp_power(self, data_model: TOBDataModel) -> float:
        """
        Calculate mean heat pulse power excluding noise.

        Heat pulse power is calculated from temperature sensor data during
        heat pulse periods, excluding noise and non-heat pulse periods.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Mean HP-Power value in watts
        """
        try:
            if data_model.data is None:
                self.logger.warning("No data available for HP-Power calculation")
                return 0.0

            # Get NTC sensors for heat pulse power calculation
            ntc_sensors = data_model.get_ntc_sensors()
            if not ntc_sensors:
                self.logger.warning("No NTC sensors found for HP-Power calculation")
                return 0.0

            # Calculate heat pulse power for each NTC sensor
            hp_power_values = []
            
            for sensor in ntc_sensors:
                sensor_data = data_model.get_sensor_data(sensor)
                if sensor_data is not None and len(sensor_data) > 1:
                    # Calculate temperature difference (delta T)
                    temp_diff = sensor_data.diff().abs()
                    
                    # Filter out noise (values below threshold)
                    noise_threshold = temp_diff.quantile(0.1)  # Bottom 10% as noise
                    heat_pulse_data = temp_diff[temp_diff > noise_threshold]
                    
                    if len(heat_pulse_data) > 0:
                        # Calculate mean heat pulse power (simplified formula)
                        # In real implementation, this would use specific heat capacity
                        # and other physical parameters
                        mean_power = heat_pulse_data.mean()
                        hp_power_values.append(mean_power)

            if hp_power_values:
                mean_hp_power = np.mean(hp_power_values)
                self.logger.info("Calculated mean HP-Power: %.3f W", mean_hp_power)
                return float(mean_hp_power)
            else:
                self.logger.warning("No valid heat pulse data found")
                return 0.0

        except (ValueError, KeyError) as e:
            self.logger.error("Data validation error calculating HP-Power: %s", e)
            return 0.0
        except Exception as e:
            self.logger.error("Unexpected error calculating HP-Power: %s", e)
            return 0.0

    def _calculate_max_vaccu(self, data_model: TOBDataModel) -> float:
        """
        Calculate maximum vacuum value.

        Vacuum is calculated from battery voltage data, as lower voltage
        typically indicates higher vacuum conditions in the system.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Maximum vacuum value (inverted voltage scale)
        """
        try:
            if data_model.data is None:
                self.logger.warning("No data available for vacuum calculation")
                return 0.0

            # Look for battery voltage column
            voltage_columns = ["battery_voltage", "voltage", "battery", "V_batt"]
            voltage_data = None
            
            for col in voltage_columns:
                if col in data_model.data.columns:
                    voltage_data = data_model.data[col]
                    break
            
            if voltage_data is None:
                self.logger.warning("No voltage data found for vacuum calculation")
                return 0.0

            # Calculate vacuum as inverse of voltage (higher vacuum = lower voltage)
            # Normalize to 0-100 scale for vacuum percentage
            min_voltage = voltage_data.min()
            max_voltage = voltage_data.max()
            
            if max_voltage > min_voltage:
                # Invert voltage to get vacuum (0% = max voltage, 100% = min voltage)
                vacuum_data = ((max_voltage - voltage_data) / (max_voltage - min_voltage)) * 100
                max_vacuum = vacuum_data.max()
                
                self.logger.info("Calculated max vacuum: %.2f%%", max_vacuum)
                return float(max_vacuum)
            else:
                self.logger.warning("Insufficient voltage range for vacuum calculation")
                return 0.0

        except (ValueError, KeyError) as e:
            self.logger.error("Data validation error calculating vacuum: %s", e)
            return 0.0
        except Exception as e:
            self.logger.error("Unexpected error calculating vacuum: %s", e)
            return 0.0

    def _calculate_tilt_status(self, data_model: TOBDataModel) -> str:
        """
        Calculate tilt status based on temperature sensor stability.

        Tilt status is determined by analyzing the standard deviation
        of temperature sensors. High variation indicates potential tilt.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Tilt status: "OK", "Warning", "Error", or "Unknown"
        """
        try:
            if data_model.data is None:
                self.logger.warning("No data available for tilt calculation")
                return "Unknown"

            # Get NTC sensors for tilt analysis
            ntc_sensors = data_model.get_ntc_sensors()
            if not ntc_sensors:
                self.logger.warning("No NTC sensors found for tilt calculation")
                return "Unknown"

            # Calculate standard deviation for each sensor
            sensor_stds = []
            
            for sensor in ntc_sensors:
                sensor_data = data_model.get_sensor_data(sensor)
                if sensor_data is not None and len(sensor_data) > 1:
                    std_dev = sensor_data.std()
                    if not np.isnan(std_dev):
                        sensor_stds.append(std_dev)

            if not sensor_stds:
                self.logger.warning("No valid sensor data for tilt calculation")
                return "Unknown"

            # Calculate mean standard deviation
            mean_std = np.mean(sensor_stds)
            
            # Define tilt thresholds based on temperature variation
            # These thresholds should be calibrated based on real data
            if mean_std < 0.5:
                status = "OK"
            elif mean_std < 1.0:
                status = "Warning"
            else:
                status = "Error"

            self.logger.info("Calculated tilt status: %s (std: %.3f)", status, mean_std)
            return status

        except (ValueError, KeyError) as e:
            self.logger.error("Data validation error calculating tilt: %s", e)
            return "Error"
        except Exception as e:
            self.logger.error("Unexpected error calculating tilt: %s", e)
            return "Error"

    def _calculate_mean_press(self, data_model: TOBDataModel) -> float:
        """
        Calculate mean pressure value from pressure sensor data.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Mean pressure value in hPa
        """
        try:
            if data_model.data is None:
                self.logger.warning("No data available for pressure calculation")
                return 0.0

            # Look for pressure column
            pressure_columns = ["pressure", "press", "P", "atm_pressure", "barometric"]
            pressure_data = None
            
            for col in pressure_columns:
                if col in data_model.data.columns:
                    pressure_data = data_model.data[col]
                    break
            
            if pressure_data is None:
                self.logger.warning("No pressure data found for calculation")
                return 0.0

            # Calculate mean pressure
            mean_pressure = pressure_data.mean()
            
            if np.isnan(mean_pressure):
                self.logger.warning("Invalid pressure data (NaN values)")
                return 0.0

            self.logger.info("Calculated mean pressure: %.2f hPa", mean_pressure)
            return float(mean_pressure)

        except (ValueError, KeyError) as e:
            self.logger.error("Data validation error calculating pressure: %s", e)
            return 0.0
        except Exception as e:
            self.logger.error("Unexpected error calculating pressure: %s", e)
            return 0.0

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
