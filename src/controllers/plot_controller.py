"""
Plot Controller for WIZARD-2.1

Controller for plot-related operations and data visualization.
Handles plot data updates, sensor selection, and axis management.
"""

import logging
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..models.tob_data_model import TOBDataModel
from ..services.plot_service import PlotService
from ..services.plot_style_service import PlotStyleService


class PlotController(QObject):
    """
    Controller for plot-related operations.

    This controller handles all plot business logic including:
    - Plot data updates
    - Sensor selection management
    - Axis limit management
    - Plot state management
    """

    # Signals for communication with main controller
    plot_updated = pyqtSignal()  # Emitted when plot data is updated
    sensors_updated = pyqtSignal(list)  # Emitted when sensor selection changes
    axis_limits_changed = pyqtSignal(str, float, float)  # axis, min, max

    def __init__(self, plot_service: PlotService, plot_style_service: PlotStyleService):
        """
        Initialize the plot controller.

        Args:
            plot_service: Plot service instance for plot operations
            plot_style_service: Plot style service instance for styling
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.plot_service = plot_service
        self.plot_style_service = plot_style_service

        # Plot state
        self.current_tob_data: Optional[TOBDataModel] = None
        self.selected_sensors: List[str] = []
        self.axis_limits: Dict[str, Dict[str, float]] = {
            "x": {"min": 0, "max": 100},
            "y1": {"min": 0, "max": 100},
            "y2": {"min": 0, "max": 100},
        }

        self.logger.info("PlotController initialized")

    def update_plot_data(self, tob_data_model: TOBDataModel) -> None:
        """
        Update plot data with new TOB data model.

        Args:
            tob_data_model: TOBDataModel instance with loaded data
        """
        try:
            self.current_tob_data = tob_data_model
            self.logger.info("Plot data updated with TOB data model")

            # Auto-select all NTC sensors initially
            if tob_data_model.sensors:
                ntc_sensors = [
                    s
                    for s in tob_data_model.sensors
                    if s.startswith("NTC") or s == "Temp"
                ]
                self.selected_sensors = ntc_sensors[:22]  # Limit to 22 sensors max
                self.logger.info(
                    f"Auto-selected {len(self.selected_sensors)} sensors: {self.selected_sensors}"
                )

            # Update axis limits based on data
            self._update_axis_limits_from_data()

            self.plot_updated.emit()

        except Exception as e:
            self.logger.error("Error updating plot data: %s", e)

    def update_selected_sensors(
        self, selected_sensors: List[str], main_window=None
    ) -> None:
        """
        Update the list of selected sensors for plotting.

        Args:
            selected_sensors: List of sensor names to display
            main_window: Main window instance to update plot widget
        """
        try:
            self.selected_sensors = selected_sensors
            self.logger.info(f"Selected sensors updated: {selected_sensors}")
            self.sensors_updated.emit(selected_sensors)

            # Update plot widget's active NTC sensors if main window is provided
            if (
                main_window
                and hasattr(main_window, "plot_widget")
                and main_window.plot_widget
            ):
                # Extract NTC sensors from selected sensors
                ntc_sensors = [
                    s for s in selected_sensors if s.startswith("NTC") or s == "Temp"
                ]
                if ntc_sensors:
                    # Set y1_sensor to "NTCs" to show multiple NTC sensors
                    main_window.plot_widget.y1_sensor = "NTCs"
                    # Set active NTC sensors to the selected ones
                    main_window.plot_widget.set_active_ntc_sensors(ntc_sensors)
                    self.logger.debug(
                        f"Set y1_sensor to NTCs and active NTC sensors: {ntc_sensors}"
                    )

                    # Also update the UI combo box if it exists
                    if (
                        hasattr(main_window, "y1_axis_combo")
                        and main_window.y1_axis_combo
                    ):
                        main_window.y1_axis_combo.setCurrentText("NTCs")

        except Exception as e:
            self.logger.error("Error updating selected sensors: %s", e)

    def update_axis_limits(self, axis: str, min_value: float, max_value: float) -> None:
        """
        Update axis limits.

        Args:
            axis: Axis identifier ('x', 'y1', 'y2')
            min_value: Minimum value for axis
            max_value: Maximum value for axis
        """
        try:
            if axis in self.axis_limits:
                self.axis_limits[axis]["min"] = min_value
                self.axis_limits[axis]["max"] = max_value
                self.logger.info(
                    f"{axis.upper()}-axis limits updated: {min_value} - {max_value}"
                )
                self.axis_limits_changed.emit(axis, min_value, max_value)
            else:
                self.logger.warning(f"Unknown axis: {axis}")

        except Exception as e:
            self.logger.error("Error updating axis limits: %s", e)

    def get_plot_info(self) -> Dict[str, Any]:
        """
        Get current plot information.

        Returns:
            Dictionary containing plot state information
        """
        try:
            return {
                "current_data": self.current_tob_data is not None,
                "selected_sensors": self.selected_sensors.copy(),
                "axis_limits": self.axis_limits.copy(),
                "data_points": (
                    len(self.current_tob_data.data)
                    if self.current_tob_data and self.current_tob_data.data is not None
                    else 0
                ),
            }
        except Exception as e:
            self.logger.error("Error getting plot info: %s", e)
            return {}

    def get_available_sensors(self) -> List[str]:
        """
        Get list of available sensors from current TOB data.

        Returns:
            List of available sensor names
        """
        try:
            if self.current_tob_data and self.current_tob_data.sensors:
                return self.current_tob_data.sensors.copy()
            return []
        except Exception as e:
            self.logger.error("Error getting available sensors: %s", e)
            return []

    def handle_sensor_selection_changed(
        self, sensor_name: str, is_selected: bool, main_window
    ) -> None:
        """
        Handle sensor selection change from UI.

        Args:
            sensor_name: Name of the sensor
            is_selected: Whether the sensor is now selected
            main_window: Main window instance for UI access
        """
        try:
            self.logger.debug(
                "PlotController: handling sensor selection change: %s = %s",
                sensor_name,
                is_selected,
            )

            # Get current selected sensors from the view
            current_selected = self._get_selected_sensors(main_window)
            self.logger.debug("Current selected sensors: %s", current_selected)

            # Calculate the new sensor selection based on the event
            # (Checkbox state might not be updated yet, so we calculate based on the event)
            if is_selected and sensor_name not in current_selected:
                # Add sensor to selection
                new_selected = current_selected + [sensor_name]
            elif not is_selected and sensor_name in current_selected:
                # Remove sensor from selection
                new_selected = [s for s in current_selected if s != sensor_name]
            else:
                # No change needed (sensor already in correct state)
                new_selected = current_selected

            self.logger.debug("New selected sensors: %s", new_selected)

            # Update the selected sensors (will emit signal)
            self.update_selected_sensors(new_selected, main_window)

            if is_selected:
                self.logger.info("Sensor %s selected for visualization", sensor_name)
            else:
                self.logger.info("Sensor %s deselected from visualization", sensor_name)

        except Exception as e:
            self.logger.error("Failed to handle sensor selection change: %s", e)
            raise

    def _get_selected_sensors(self, main_window) -> List[str]:
        """
        Get list of currently selected sensors from UI.

        Args:
            main_window: Main window instance

        Returns:
            List of selected sensor names
        """
        try:
            selected_sensors = []

            # Check all NTC checkboxes (including PT100 which is registered as "Temp")
            for sensor_name, checkbox in main_window.ntc_checkboxes.items():
                if checkbox and checkbox.isChecked():
                    selected_sensors.append(sensor_name)

            self.logger.debug("Selected sensors: %s", selected_sensors)
            return selected_sensors

        except Exception as e:
            self.logger.error("Error getting selected sensors: %s", e)
            return []

    def update_sensor_checkboxes(self, main_window) -> None:
        """
        Update sensor checkboxes in the main window based on available sensors.

        Args:
            main_window: Main window instance to update
        """
        try:
            if not self.current_tob_data or not self.current_tob_data.sensors:
                self.logger.warning("No sensors available for checkbox update")
                return

            # Get available sensors
            available_sensors = self.current_tob_data.sensors

            # Update NTC checkboxes
            for sensor_name, checkbox in main_window.ntc_checkboxes.items():
                if sensor_name in available_sensors:
                    checkbox.setVisible(True)
                    checkbox.setEnabled(True)
                    checkbox.setChecked(sensor_name in self.selected_sensors)
                else:
                    checkbox.setVisible(False)
                    checkbox.setEnabled(False)
                    checkbox.setChecked(False)

            # Update PT100 checkbox
            if (
                hasattr(main_window, "ntc_pt100_checkbox")
                and main_window.ntc_pt100_checkbox
            ):
                pt100_sensor = self.current_tob_data.get_pt100_sensor()
                if pt100_sensor and pt100_sensor in available_sensors:
                    main_window.ntc_pt100_checkbox.setVisible(True)
                    main_window.ntc_pt100_checkbox.setEnabled(True)
                    main_window.ntc_pt100_checkbox.setChecked(
                        pt100_sensor in self.selected_sensors
                    )
                else:
                    main_window.ntc_pt100_checkbox.setVisible(False)
                    main_window.ntc_pt100_checkbox.setEnabled(False)
                    main_window.ntc_pt100_checkbox.setChecked(False)

            self.logger.info(
                "Sensor checkboxes updated for %d sensors", len(available_sensors)
            )

        except Exception as e:
            self.logger.error("Error updating sensor checkboxes: %s", e)

    def _update_axis_limits_from_data(self) -> None:
        """
        Update axis limits based on current data ranges.
        """
        try:
            if not self.current_tob_data or not self.current_tob_data.data is not None:
                return

            # Update X-axis (time)
            time_col = self.current_tob_data.get_time_column_name()
            if time_col and time_col in self.current_tob_data.data.columns:
                time_data = self.current_tob_data.data[time_col]
                self.axis_limits["x"]["min"] = float(time_data.min())
                self.axis_limits["x"]["max"] = float(time_data.max())

            # Update Y-axes based on selected sensors
            if self.selected_sensors:
                y_min = float("inf")
                y_max = float("-inf")

                for sensor in self.selected_sensors:
                    sensor_data = self.current_tob_data.get_sensor_data(sensor)
                    if sensor_data is not None and len(sensor_data) > 0:
                        y_min = min(y_min, float(sensor_data.min()))
                        y_max = max(y_max, float(sensor_data.max()))

                if y_min != float("inf") and y_max != float("-inf"):
                    # Add 10% padding
                    padding = (y_max - y_min) * 0.1
                    self.axis_limits["y1"]["min"] = y_min - padding
                    self.axis_limits["y1"]["max"] = y_max + padding

            self.logger.info("Axis limits updated from data")

        except Exception as e:
            self.logger.error("Error updating axis limits from data: %s", e)
