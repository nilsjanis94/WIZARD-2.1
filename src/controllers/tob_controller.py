"""
TOB Controller for WIZARD-2.1

Controller for TOB file operations and data processing.
"""

import logging
from typing import Any, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..models.tob_data_model import TOBDataModel
from ..services.data_service import DataService
from ..services.tob_service import TOBService


class TOBController(QObject):
    """
    Controller for TOB file operations.

    This controller handles all TOB-specific business logic including:
    - File loading and validation
    - Data processing and metrics calculation
    - Sensor data management

    Signals:
        file_loaded: Emitted when a TOB file is loaded successfully
        data_processed: Emitted when TOB data is processed
        metrics_calculated: Emitted when metrics are calculated
        error_occurred: Emitted when an error occurs
    """

    # Signals
    file_loaded = pyqtSignal(object)  # TOBDataModel
    data_processed = pyqtSignal(object)  # Processed data
    metrics_calculated = pyqtSignal(dict)  # Calculated metrics
    error_occurred = pyqtSignal(str, str)  # error_type, error_message

    def __init__(self, tob_service: TOBService, data_service: DataService):
        """
        Initialize the TOB controller.

        Args:
            tob_service: TOB service instance
            data_service: Data service instance
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.tob_service = tob_service
        self.data_service = data_service

        self.logger.info("TOBController initialized")

    def load_tob_file(self, file_path: str) -> None:
        """
        Load and validate a TOB file.

        Args:
            file_path: Path to the TOB file
        """
        try:
            self.logger.info("Loading TOB file: %s", file_path)

            # Validate file first
            if not self.tob_service.validate_tob_file(file_path):
                error_msg = f"Invalid TOB file: {file_path}"
                self.logger.error(error_msg)
                self.error_occurred.emit("TOB Validation Error", error_msg)
                return

            # Load the file
            tob_data_model = self.tob_service.load_tob_file(file_path)

            if tob_data_model:
                self.logger.info("TOB file loaded successfully: %s", file_path)
                self.file_loaded.emit(tob_data_model)
            else:
                error_msg = f"Failed to load TOB file: {file_path}"
                self.logger.error(error_msg)
                self.error_occurred.emit("TOB Loading Error", error_msg)

        except Exception as e:
            error_msg = f"Error loading TOB file: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("TOB Loading Error", error_msg)

    def process_tob_data(self, tob_data_model: TOBDataModel) -> None:
        """
        Process TOB data for visualization and analysis.

        Args:
            tob_data_model: TOBDataModel instance to process
        """
        try:
            self.logger.info("Processing TOB data")

            # Process data using data service
            processed_data = self.data_service.process_tob_data(tob_data_model)

            if processed_data:
                self.logger.info("TOB data processed successfully")
                self.data_processed.emit(processed_data)
            else:
                error_msg = "Failed to process TOB data"
                self.logger.error(error_msg)
                self.error_occurred.emit("Data Processing Error", error_msg)

        except Exception as e:
            error_msg = f"Error processing TOB data: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("Data Processing Error", error_msg)

    def calculate_metrics(self, tob_data_model: TOBDataModel) -> Dict[str, Any]:
        """
        Calculate data metrics for TOB data.

        Args:
            tob_data_model: TOBDataModel instance

        Returns:
            Dictionary containing calculated metrics
        """
        try:
            self.logger.info("Calculating TOB data metrics")

            # Calculate metrics using data service
            metrics = self.data_service._calculate_metrics(tob_data_model)

            if metrics:
                self.logger.info(
                    "Metrics calculated successfully: %s", list(metrics.keys())
                )
                self.metrics_calculated.emit(metrics)
                return metrics
            else:
                self.logger.warning("No metrics calculated")
                return {}

        except Exception as e:
            error_msg = f"Error calculating metrics: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("Metrics Calculation Error", error_msg)
            return {}

    def get_sensor_data(
        self, tob_data_model: TOBDataModel, sensor_name: str
    ) -> Optional[Any]:
        """
        Get data for a specific sensor.

        Args:
            tob_data_model: TOBDataModel instance
            sensor_name: Name of the sensor

        Returns:
            Sensor data or None if not found
        """
        try:
            if tob_data_model and tob_data_model.data is not None:
                sensor_data = tob_data_model.get_sensor_data(sensor_name)
                if sensor_data is not None:
                    self.logger.debug("Retrieved data for sensor: %s", sensor_name)
                    return sensor_data
                else:
                    self.logger.warning("Sensor not found: %s", sensor_name)
                    return None
            else:
                self.logger.warning("No TOB data model available")
                return None

        except Exception as e:
            error_msg = f"Error getting sensor data for {sensor_name}: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("Sensor Data Error", error_msg)
            return None

    def get_available_sensors(self, tob_data_model: TOBDataModel) -> list:
        """
        Get list of available sensors from TOB data.

        Args:
            tob_data_model: TOBDataModel instance

        Returns:
            List of available sensor names
        """
        try:
            if tob_data_model and tob_data_model.sensors:
                sensors = tob_data_model.sensors.copy()
                self.logger.debug("Available sensors: %s", sensors)
                return sensors
            else:
                self.logger.warning("No sensors available in TOB data")
                return []

        except Exception as e:
            error_msg = f"Error getting available sensors: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("Sensor List Error", error_msg)
            return []

    def validate_tob_file(self, file_path: str) -> bool:
        """
        Validate a TOB file.

        Args:
            file_path: Path to the TOB file

        Returns:
            True if file is valid, False otherwise
        """
        try:
            is_valid = self.tob_service.validate_tob_file(file_path)
            self.logger.debug("TOB file validation for %s: %s", file_path, is_valid)
            return is_valid

        except Exception as e:
            error_msg = f"Error validating TOB file: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("TOB Validation Error", error_msg)
            return False
