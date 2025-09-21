"""
Analytics Service for WIZARD-2.1

Service for physical calculations, sensor analysis, and data metrics computation.
Handles all analytical and computational operations separate from data management.
"""

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from ..models.tob_data_model import TOBDataModel


class AnalyticsService:
    """
    Service for analytical calculations and sensor data analysis.

    This service handles all computational operations including:
    - Physical calculations (power, pressure, vacuum)
    - Sensor analysis (tilt detection, noise filtering)
    - Statistical computations (means, maxima, etc.)
    """

    def __init__(self):
        """Initialize the analytics service."""
        self.logger = logging.getLogger(__name__)

    def calculate_metrics(self, data_model: TOBDataModel) -> Dict[str, Any]:
        """
        Calculate all data metrics for the given TOB data model.

        Args:
            data_model: TOBDataModel instance with loaded data

        Returns:
            Dictionary containing all calculated metrics
        """
        try:
            metrics = {}

            if data_model.data is not None:
                # Calculate Mean HP-Power (excluding noise during non-heat pulse periods)
                metrics["mean_hp_power"] = self._calculate_mean_hp_power(data_model)

                # Calculate Max Vaccu
                metrics["max_v_accu"] = self._calculate_max_vaccu(data_model)

                # Calculate Tilt Status
                metrics["tilt_status"] = self._calculate_tilt_status(data_model)

                # Calculate Mean Press
                metrics["mean_press"] = self._calculate_mean_press(data_model)

            self.logger.info("Calculated metrics: %s", list(metrics.keys()))
            return metrics

        except Exception as e:
            self.logger.error("Error calculating metrics: %s", e)
            return {}

    def _calculate_mean_hp_power(self, data_model: TOBDataModel) -> float:
        """
        Calculate mean heat pulse power from voltage and current data.

        Heat pulse power is calculated as P = U × I (Power = Voltage × Current)
        during heat pulse periods, excluding noise and non-heat pulse periods.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Mean HP-Power value in watts
        """
        try:
            if data_model.data is None:
                self.logger.warning("No data available for HP-Power calculation")
                return 0.0

            # Check for heating voltage and current columns
            voltage_col = None
            current_col = None

            # Look for heating voltage (Vheat) and current (Iheat)
            for col in ["Vheat", "Heating_Voltage", "Heat_Voltage"]:
                if col in data_model.data.columns:
                    voltage_col = col
                    break

            for col in ["Iheat", "Heating_Current", "Heat_Current"]:
                if col in data_model.data.columns:
                    current_col = col
                    break

            if voltage_col is None or current_col is None:
                self.logger.warning(
                    "No heating voltage/current data found for HP-Power calculation"
                )
                return 0.0

            # Get voltage and current data
            voltage_data = data_model.data[voltage_col]
            current_data = data_model.data[current_col]

            # Calculate instantaneous power P = U × I
            power_data = voltage_data * current_data

            # Filter out negative or zero power (invalid measurements)
            valid_power_data = power_data[power_data > 0]

            if len(valid_power_data) == 0:
                self.logger.warning("No valid power data found")
                return 0.0

            # Filter heat pulses using multiple criteria for better noise rejection

            # 1. Absolute minimum power threshold (realistic heat pulse)
            min_power_threshold = 10.0  # Watts - minimum realistic heat pulse power
            realistic_power = valid_power_data[valid_power_data >= min_power_threshold]

            # 2. Additional filtering using power stability (reduce noise from fluctuations)
            if len(realistic_power) > 1:
                power_diff = realistic_power.diff().abs()
                # Use a more aggressive noise threshold for power differences
                diff_threshold = power_diff.quantile(0.3)  # Bottom 30% of differences
                heat_pulse_power = realistic_power[power_diff > diff_threshold]
            else:
                heat_pulse_power = realistic_power

            if len(heat_pulse_power) > 0:
                # Calculate mean heat pulse power
                mean_hp_power = heat_pulse_power.mean()
                # Round to 2 decimal places for meaningful precision
                rounded_hp_power = round(mean_hp_power, 2)
                self.logger.info(
                    "Calculated mean HP-Power: %.2f W (from %d heat pulses, filtered from %d valid measurements)",
                    rounded_hp_power,
                    len(heat_pulse_power),
                    len(valid_power_data),
                )
                return rounded_hp_power
            else:
                self.logger.warning("No significant heat pulse power data found")
                return 0.0

        except (ValueError, KeyError) as e:
            self.logger.error("Data validation error calculating HP-Power: %s", e)
            return 0.0
        except Exception as e:
            self.logger.error("Unexpected error calculating HP-Power: %s", e)
            return 0.0

    def add_calculated_columns(self, data_model: TOBDataModel) -> None:
        """
        Add calculated columns to the TOB data for plotting purposes.

        This method calculates derived values like HP-Power and adds them as new columns
        to the data model, making them available for plotting like regular sensors.

        Args:
            data_model: TOBDataModel instance to add calculated columns to
        """
        try:
            if data_model.data is None:
                self.logger.warning("No data available for calculated columns")
                return

            # Calculate HP-Power column if voltage and current data available
            if "HP-Power" not in data_model.data.columns:
                voltage_col = None
                current_col = None

                # Look for heating voltage (Vheat) and current (Iheat)
                for col in ["Vheat", "Heating_Voltage", "Heat_Voltage"]:
                    if col in data_model.data.columns:
                        voltage_col = col
                        break

                for col in ["Iheat", "Heating_Current", "Heat_Current"]:
                    if col in data_model.data.columns:
                        current_col = col
                        break

                if voltage_col is not None and current_col is not None:
                    # Calculate instantaneous power P = U × I
                    voltage_data = data_model.data[voltage_col]
                    current_data = data_model.data[current_col]
                    hp_power_data = voltage_data * current_data

                    # Add the calculated column to the data
                    data_model.data["HP-Power"] = hp_power_data

                    self.logger.info(
                        f"Added HP-Power column calculated from {voltage_col} × {current_col}"
                    )
                else:
                    self.logger.warning(
                        "Cannot add HP-Power column: voltage/current data not found"
                    )

            # Future: Add other calculated columns here
            # - Efficiency metrics
            # - Derived temperature calculations
            # - Statistical measures over time windows

        except Exception as e:
            self.logger.error("Error adding calculated columns: %s", e)

    def _calculate_max_vaccu(self, data_model: TOBDataModel) -> float:
        """
        Calculate maximum battery voltage value.

        Vaccu represents the battery voltage for the vacuum system.
        Max Vaccu is the highest battery voltage recorded.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Maximum battery voltage in volts
        """
        try:
            if data_model.data is None:
                self.logger.warning("No data available for battery voltage calculation")
                return 0.0

            # Look for battery voltage column
            voltage_columns = [
                "Vaccu",
                "Vbatt",
                "battery_voltage",
                "voltage",
                "battery",
                "V_batt",
            ]
            voltage_data = None

            for col in voltage_columns:
                if col in data_model.data.columns:
                    voltage_data = data_model.data[col]
                    break

            if voltage_data is None:
                self.logger.warning("No battery voltage data found")
                return 0.0

            # Max Vaccu is simply the maximum battery voltage
            max_voltage = voltage_data.max()

            # Round to 2 decimal places for voltage precision
            rounded_voltage = round(max_voltage, 2)
            self.logger.info("Calculated max battery voltage: %.2f V", rounded_voltage)
            return rounded_voltage

        except (ValueError, KeyError) as e:
            self.logger.error(
                "Data validation error calculating battery voltage: %s", e
            )
            return 0.0
        except Exception as e:
            self.logger.error("Unexpected error calculating battery voltage: %s", e)
            return 0.0

    def _calculate_tilt_status(self, data_model: TOBDataModel) -> float:
        """
        Calculate tilt stability based on dedicated tilt sensors.

        Tilt stability is calculated as the mean standard deviation of
        tilt sensors (TiltX, TiltY) and accelerometer (ACCz).
        Lower values indicate higher stability (less tilt/movement).

        Args:
            data_model: TOBDataModel instance

        Returns:
            Mean standard deviation of tilt sensors (stability metric)
        """
        try:
            if data_model.data is None:
                self.logger.warning("No data available for tilt calculation")
                return float("nan")

            # Look for dedicated tilt sensors
            tilt_columns = ["TiltX", "TiltY", "ACCz"]
            available_tilt_sensors = []

            for col in tilt_columns:
                if col in data_model.data.columns:
                    available_tilt_sensors.append(col)

            if not available_tilt_sensors:
                self.logger.warning(
                    "No dedicated tilt sensors found, falling back to NTC analysis"
                )
                # Fallback to NTC analysis if no tilt sensors available
                return self._calculate_tilt_from_ntc(data_model)

            # Calculate stability metrics for each tilt sensor
            sensor_stabilities = []

            for sensor in available_tilt_sensors:
                sensor_data = data_model.data[sensor]
                if len(sensor_data) > 1:
                    # Use standard deviation as stability metric
                    # Lower std = more stable = better (less tilt/movement)
                    std_dev = sensor_data.std()
                    if not np.isnan(std_dev):
                        sensor_stabilities.append(std_dev)

            if not sensor_stabilities:
                self.logger.warning("No valid tilt sensor data found")
                return float("nan")

            # Calculate overall stability (mean of all sensor stabilities)
            overall_stability = np.mean(sensor_stabilities)

            # Round to 4 decimal places for meaningful precision
            rounded_stability = round(overall_stability, 4)

            self.logger.info(
                "Calculated tilt stability: %.4f (from %d sensors)",
                rounded_stability,
                len(sensor_stabilities),
            )
            return rounded_stability

        except (ValueError, KeyError) as e:
            self.logger.error("Data validation error calculating tilt: %s", e)
            return float("nan")
        except Exception as e:
            self.logger.error("Unexpected error calculating tilt: %s", e)
            return float("nan")

    def _calculate_tilt_from_ntc(self, data_model: TOBDataModel) -> float:
        """
        Fallback method: Calculate tilt stability from NTC temperature sensors.

        This is used when no dedicated tilt sensors are available.
        Returns temperature variability as stability metric.

        Args:
            data_model: TOBDataModel instance

        Returns:
            Mean temperature standard deviation (stability metric)
        """
        try:
            # Get NTC sensors for tilt analysis
            ntc_sensors = data_model.get_ntc_sensors()
            if not ntc_sensors:
                return float("nan")

            # Calculate standard deviation for each sensor
            sensor_stds = []

            for sensor in ntc_sensors:
                sensor_data = data_model.get_sensor_data(sensor)
                if sensor_data is not None and len(sensor_data) > 1:
                    std_dev = sensor_data.std()
                    if not np.isnan(std_dev):
                        sensor_stds.append(std_dev)

            if not sensor_stds:
                return float("nan")

            # Return mean temperature standard deviation as stability metric
            mean_temp_stability = np.mean(sensor_stds)
            rounded_stability = round(mean_temp_stability, 4)

            self.logger.info(
                "Calculated tilt stability from NTC: %.4f (temperature variability)",
                rounded_stability,
            )
            return rounded_stability

        except Exception as e:
            self.logger.error("Error in NTC tilt fallback: %s", e)
            return float("nan")

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
            pressure_columns = [
                "Press",
                "pressure",
                "press",
                "P",
                "atm_pressure",
                "barometric",
            ]
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

            # Round to 1 decimal place for pressure readings
            rounded_pressure = round(mean_pressure, 1)
            self.logger.info("Calculated mean pressure: %.1f hPa", rounded_pressure)
            return rounded_pressure

        except (ValueError, KeyError) as e:
            self.logger.error("Data validation error calculating pressure: %s", e)
            return 0.0
        except Exception as e:
            self.logger.error("Unexpected error calculating pressure: %s", e)
            return 0.0
