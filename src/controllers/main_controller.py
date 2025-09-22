"""
Main controller for the WIZARD-2.1 application.

This module contains the main controller class that coordinates between
the models, views, and services.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from ..models.project_model import ProjectModel
from ..models.tob_data_model import TOBDataModel
from ..services.analytics_service import AnalyticsService
from ..services.data_service import DataService
from ..services.encryption_service import EncryptionService
from ..services.error_service import ErrorService
from ..services.http_client_service import HttpClientService
from ..services.memory_monitor_service import MemoryMonitorService
from ..services.plot_service import PlotService
from ..services.project_service import ProjectService
from ..services.tob_service import TOBService
from ..utils.error_handler import ErrorHandler
from .plot_controller import PlotController
from .tob_controller import TOBController


class MainController(QObject):
    """
    Main controller class for the WIZARD-2.1 application.

    This class coordinates between the models, views, and services,
    handling the main application logic and user interactions.
    """

    # Signals for communication with the view
    file_loaded = pyqtSignal(str, object)  # file_path, tob_data_model
    file_load_progress = pyqtSignal(int)  # progress percentage
    file_load_error = pyqtSignal(str, str)  # error_type, error_message
    data_processed = pyqtSignal(object)  # processed_data
    sensors_updated = pyqtSignal(list)  # available_sensors

    # UI update signals
    plot_data_update = pyqtSignal(object)  # tob_data_model
    plot_sensors_update = pyqtSignal(list)  # selected_sensors
    plot_axis_limits_update = pyqtSignal(str, float, float)  # axis, min, max
    show_plot_mode = pyqtSignal()  # signal to show plot mode

    # GUI operation signals (thread-safe)
    show_upload_success = pyqtSignal(str, str)  # title, message
    show_server_status = pyqtSignal(str, str)  # title, message

    def __init__(self, main_window=None):
        """
        Initialize the main controller.

        Args:
            main_window: Main window instance (optional, for dependency injection)
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Initialize services (centralized service creation)
        self.analytics_service = AnalyticsService()

        # Additional services needed by view and sub-controllers
        from ..services.axis_ui_service import AxisUIService
        from ..services.plot_style_service import PlotStyleService
        from ..services.ui_service import UIService
        from ..services.ui_state_manager import UIStateManager

        self.ui_service = UIService()
        self.ui_state_manager = UIStateManager()
        self.axis_ui_service = AxisUIService()
        self.plot_style_service = PlotStyleService()

        # Services that depend on other services
        self.tob_service = TOBService()
        self.data_service = DataService(self.analytics_service)
        self.plot_service = PlotService(self.plot_style_service)
        self.encryption_service = EncryptionService()
        self.project_service = ProjectService()
        self.error_service = ErrorService()
        self.error_handler = ErrorHandler()
        self.memory_monitor = MemoryMonitorService(error_handler=self.error_handler)
        self.http_client: Optional[HttpClientService] = None

        # Initialize sub-controllers with injected services
        self.plot_controller = PlotController(
            self.plot_service, self.plot_style_service
        )
        self.tob_controller = TOBController(self.tob_service, self.data_service)

        # Initialize models
        self.tob_data_model: Optional[TOBDataModel] = None
        self.project_model = ProjectModel(name="Untitled Project")

        # Initialize auto-save
        self._setup_auto_save()

        # Initialize memory monitoring
        self._setup_memory_monitoring()

        # Initialize view
        if main_window is not None:
            self.main_window = main_window
            # Connect controller to window
            self.main_window.set_controller(self)
            # Inject services into view
            self._inject_services_into_view()
        else:
            # Fallback: create window (backward compatibility)
            from ..views.main_window import MainWindow

            self.main_window = MainWindow()  # Create without controller
            # Inject services into view first
            self._inject_services_into_view()
            # Then set controller
            self.main_window.set_controller(self)

        # Connect signals
        self._connect_signals()
        self._connect_plot_signals()
        self._connect_tob_signals()

        self.logger.info("Main controller initialized successfully")

    def _connect_plot_signals(self) -> None:
        """
        Connect plot controller signals to main window slots.
        """
        # Connect plot controller signals to main controller signals
        self.plot_controller.plot_updated.connect(self._on_plot_updated)
        self.plot_controller.sensors_updated.connect(self._on_sensors_updated)
        self.plot_controller.axis_limits_changed.connect(self._on_axis_limits_changed)

        if hasattr(self.main_window, "update_plot_axis_limits"):
            self.plot_controller.axis_limits_changed.connect(
                lambda axis, min_val, max_val: self._handle_axis_limits_changed(
                    axis, min_val, max_val
                )
            )

        self.logger.debug("Plot controller signals connected to main window")

    def _on_plot_updated(self) -> None:
        """Handle plot updated signal from plot controller."""
        if self.plot_controller.current_tob_data:
            self.plot_data_update.emit(self.plot_controller.current_tob_data)

    def _on_sensors_updated(self, selected_sensors: list) -> None:
        """Handle sensors updated signal from plot controller."""
        self.plot_sensors_update.emit(selected_sensors)

    def _on_axis_limits_changed(
        self, axis: str, min_value: float, max_value: float
    ) -> None:
        """Handle axis limits changed signal from plot controller."""
        self.plot_axis_limits_update.emit(axis, min_value, max_value)

    def _handle_axis_limits_changed(
        self, axis: str, min_value: float, max_value: float
    ) -> None:
        """
        Handle axis limits changed signal from plot controller.

        Args:
            axis: Axis that changed ('x', 'y1', 'y2')
            min_value: New minimum value
            max_value: New maximum value
        """
        try:
            # Emit signal to view instead of calling methods directly
            self.plot_axis_limits_update.emit(axis, min_value, max_value)
            self.logger.debug("Axis limits signal emitted: %s = %.2f - %.2f", axis, min_value, max_value)
        except Exception as e:
            self.logger.error("Error handling axis limits change: %s", e)

    def _connect_tob_signals(self) -> None:
        """
        Connect TOB controller signals to main controller slots.
        """
        # Connect TOB controller signals to main controller methods
        self.tob_controller.file_loaded.connect(self._on_tob_file_loaded)
        self.tob_controller.data_processed.connect(self._on_tob_data_processed)
        self.tob_controller.metrics_calculated.connect(self._on_tob_metrics_calculated)
        self.tob_controller.error_occurred.connect(self._on_tob_error_occurred)

        self.logger.debug("TOB controller signals connected")

    def _on_tob_file_loaded(self, tob_data_model: TOBDataModel) -> None:
        """
        Handle TOB file loaded signal from TOB controller.

        Args:
            tob_data_model: Loaded TOBDataModel instance
        """
        try:
            self.logger.info("TOB file loaded by controller")
            self.tob_data_model = tob_data_model
            self.file_load_progress.emit(30)

            # Process the data
            self.tob_controller.process_tob_data(tob_data_model)

        except Exception as e:
            self.logger.error("Error handling TOB file loaded: %s", e)

    def _on_tob_data_processed(self, processed_data: dict) -> None:
        """
        Handle TOB data processed signal from TOB controller.

        Args:
            processed_data: Processed TOB data
        """
        try:
            self.logger.info("TOB data processed by controller")
            self.file_load_progress.emit(60)
            self.data_processed.emit(processed_data)

            self.file_load_progress.emit(80)

            # Calculate metrics
            self.tob_controller.calculate_metrics(self.tob_data_model)

        except Exception as e:
            self.logger.error("Error handling TOB data processed: %s", e)

    def _on_tob_metrics_calculated(self, metrics: dict) -> None:
        """
        Handle metrics calculated signal from TOB controller.

        Args:
            metrics: Calculated metrics
        """
        try:
            self.logger.info("TOB metrics calculated by controller")

            # Update data metrics in view
            self.data_service.update_data_metrics(
                self.main_window.get_metrics_widgets(), metrics
            )

            # Update plot with loaded data
            if self.tob_data_model:
                # Set default Y1 sensor to NTCs for new plot system FIRST
                self.y1_sensor = "NTCs"

                # Update plot widget with correct sensor settings BEFORE plot data
                if hasattr(self.main_window, 'plot_widget') and self.main_window.plot_widget:
                    self.main_window.plot_widget.y1_sensor = "NTCs"
                    self.main_window.plot_widget.tob_data_model = self.tob_data_model
                    # Ensure all NTC sensors are active initially
                    self.main_window.plot_widget.active_ntc_sensors = None

                # Update plot data (old system)
                self.plot_controller.update_plot_data(self.tob_data_model)

                # Auto-select sensors (NTC sensors and PT100)
                selected_sensors = [
                    sensor for sensor in self.tob_data_model.sensors
                    if sensor.startswith("NTC")
                ]
                pt100_sensor = self.tob_data_model.get_pt100_sensor()
                if pt100_sensor:
                    selected_sensors.append(pt100_sensor)

                if selected_sensors:
                    self.plot_controller.update_selected_sensors(selected_sensors)

                # Trigger final plot refresh with NTCs for new plot widget
                if hasattr(self.main_window, 'plot_widget') and self.main_window.plot_widget:
                    if hasattr(self.main_window.plot_widget, '_refresh_plot'):
                        self.main_window.plot_widget._refresh_plot()
                    # Update axis labels after initial plot refresh
                    if hasattr(self.main_window.plot_widget, '_update_axis_labels'):
                        self.main_window.plot_widget._update_axis_labels()

                # Emit sensors updated signal
                self.sensors_updated.emit(self.tob_data_model.sensors)

            # Show plot mode and indicate data loaded
            self.show_plot_mode.emit()
            self.main_window.show_data_loaded()

            self.file_load_progress.emit(100)

        except Exception as e:
            self.logger.error("Error handling TOB metrics calculated: %s", e)

    def _on_tob_error_occurred(self, error_type: str, error_message: str) -> None:
        """
        Handle error signal from TOB controller.

        Args:
            error_type: Type of error
            error_message: Error message
        """
        try:
            self.logger.error(
                "TOB controller error: %s - %s", error_type, error_message
            )

            # Show error to user
            if hasattr(self.main_window, "show_error_dialog"):
                self.main_window.show_error_dialog(error_type, error_message)

        except Exception as e:
            self.logger.error("Error handling TOB controller error: %s", e)

    def _inject_services_into_view(self) -> None:
        """
        Inject services into the main window view.
        """
        if self.main_window is None:
            self.logger.warning("Cannot inject services: main_window is None")
            return

        # Inject services into view (using centralized service instances)
        services = {
            "ui_state_manager": self.ui_state_manager,
            "ui_service": self.ui_service,
            "axis_ui_service": self.axis_ui_service,
            "data_service": self.data_service,
            "plot_service": self.plot_service,
            "plot_style_service": self.plot_style_service,
        }

        self.main_window.set_services(services)
        self.logger.info("Services injected into view successfully")

    def _connect_signals(self):
        """
        Connect signals between view and controller.
        """
        # Connect view signals to controller methods
        self.main_window.file_opened.connect(self._on_file_opened)
        self.main_window.project_created.connect(self._on_project_created)
        self.main_window.project_opened.connect(self._on_project_opened)

        # Connect controller signals to view slots
        self.plot_data_update.connect(self.main_window.update_plot_data)
        self.plot_sensors_update.connect(self.main_window.update_plot_sensors)
        self.plot_axis_limits_update.connect(
            self.main_window._handle_plot_axis_limits_update
        )
        self.show_plot_mode.connect(self.main_window._show_plot_area)

        self.logger.debug("Signals connected successfully")

    def _on_file_opened(self, file_path: str):
        """
        Handle file opened signal from view.

        Args:
            file_path: Path to the opened file
        """
        try:
            self.logger.info("Loading TOB file: %s", file_path)
            self.main_window.display_status_message("Loading file...", 0)
            self.file_load_progress.emit(10)

            # Delegate to TOB controller - it will handle validation, loading, processing
            self.tob_controller.load_tob_file(file_path)

            # Emit signal for UI updates
            self.file_loaded.emit(file_path, self.tob_data_model)
            self.main_window.display_status_message("File loaded successfully", 2000)
            self.logger.info("TOB file loading initiated: %s", file_path)

        except (FileNotFoundError, PermissionError) as e:
            error_msg = f"File access error: {e}"
            self.logger.error("File access error loading TOB file %s: %s", file_path, e)
            self.file_load_error.emit("FileAccessError", error_msg)
            self.error_handler.handle_error(e, self.main_window, "File Access Error")
        except (ValueError, TypeError) as e:
            error_msg = f"File format error: {e}"
            self.logger.error("File format error loading TOB file %s: %s", file_path, e)
            self.file_load_error.emit("FileFormatError", error_msg)
            self.error_handler.handle_error(e, self.main_window, "File Format Error")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            self.logger.error("Unexpected error loading TOB file %s: %s", file_path, e)
            self.file_load_error.emit("UnexpectedError", error_msg)
            self.error_handler.handle_error(e, self.main_window, "File Loading Error")


    def open_tob_file(self, file_path: str):
        """
        Public method to open a TOB file.

        Args:
            file_path: Path to the TOB file
        """
        self._on_file_opened(file_path)

    def get_current_tob_data(self) -> Optional[TOBDataModel]:
        """
        Get the currently loaded TOB data model.

        Returns:
            Current TOB data model or None if no data loaded
        """
        return self.tob_data_model

    def get_time_range(self) -> Dict[str, Any]:
        """
        Get the time range of the currently loaded data.

        Returns:
            Dictionary with min, max, duration, and count or empty dict if no data
        """
        if not self.tob_data_model:
            return {}

        return self.data_service._get_time_range(self.tob_data_model)

    def handle_sensor_selection_changed(self, sensor_name: str, is_selected: bool):
        """
        Handle sensor selection changes from the view.

        This is the proper MVC way: View informs Controller about UI events,
        Controller decides what to do and updates the view accordingly.

        Args:
            sensor_name: Name of the sensor that changed
            is_selected: Whether the sensor is now selected
        """
        try:
            self.logger.debug("Sensor selection changed: %s = %s", sensor_name, is_selected)

            # Handle NTC sensor checkboxes for filtering when Y1 is "NTCs"
            if sensor_name.startswith("NTC") or sensor_name == "Temp":
                # This is an NTC sensor checkbox change
                if hasattr(self.main_window, 'plot_widget') and self.main_window.plot_widget:
                    # Get current active NTC sensors
                    current_active = self.main_window.plot_widget.active_ntc_sensors

                    # If no filter is set, get all available NTC sensors
                    if current_active is None:
                        # Initialize with all NTC sensors that are checked
                        all_ntc_sensors = []
                        if hasattr(self.main_window, 'ntc_checkboxes'):
                            for name, checkbox in self.main_window.ntc_checkboxes.items():
                                if name.startswith("NTC") or name == "Temp":
                                    all_ntc_sensors.append(name)

                        # Start with all NTC sensors as active
                        current_active = all_ntc_sensors.copy()

                    # Update the active list based on checkbox state
                    if is_selected and sensor_name not in current_active:
                        current_active.append(sensor_name)
                    elif not is_selected and sensor_name in current_active:
                        current_active.remove(sensor_name)

                    # Set the filtered NTC sensors
                    self.main_window.plot_widget.set_active_ntc_sensors(current_active)
                    self.logger.debug("NTC sensor filter updated: %s", current_active)

            else:
                # For other sensors, delegate to plot controller (old system)
                self.plot_controller.handle_sensor_selection_changed(
                    sensor_name, is_selected, self.main_window
                )

        except Exception as e:
            self.logger.error("Error handling sensor selection change: %s", e)

    def update_axis_auto_mode(self, axis_name: str, is_auto: bool):
        """
        Update axis auto mode setting.

        Args:
            axis_name: Name of the axis (e.g., 'y1', 'y2', 'x')
            is_auto: Whether auto mode is enabled
        """
        try:
            self.logger.debug("Updating axis auto mode: %s = %s", axis_name, is_auto)

            # Update axis settings
            axis_settings = {f"{axis_name}_auto": is_auto}

            # Update plot with new axis settings
            # Axis settings are handled by plot controller signals

            self.logger.info("Axis %s auto mode: %s", axis_name, is_auto)

        except Exception as e:
            self.logger.error("Error updating axis auto mode: %s", e)
            self.error_handler.handle_error(e, self.main_window, "Axis Update Error")

    def update_axis_settings(self, axis_settings: Dict[str, Any]):
        """
        Update axis settings for plotting.

        Args:
            axis_settings: Dictionary containing axis configuration
        """
        try:
            self.logger.debug("Updating axis settings: %s", axis_settings)

            # Update plot widget with new axis settings
            if self.main_window and hasattr(self.main_window, 'plot_widget') and self.main_window.plot_widget:
                self.main_window.plot_widget.update_axis_settings(axis_settings)
                self.logger.debug("Plot widget axis settings updated")
            else:
                self.logger.warning("No plot widget available for axis settings update")

            self.logger.info("Axis settings updated: %s", axis_settings)

        except Exception as e:
            self.logger.error("Error updating axis settings: %s", e)
            self.error_handler.handle_error(
                e, self.main_window, "Axis Settings Update Error"
            )

    def set_primary_sensor(self, sensor_name: str):
        """
        Set the primary sensor for the main plot.

        Args:
            sensor_name: Name of the sensor to display in main plot
        """
        self.y1_sensor = sensor_name
        self._set_sensor(sensor_name, 'y1_sensor', is_primary=True)

    def _set_sensor(self, sensor_name: str, sensor_attr: str, is_primary: bool = True):
        """
        Common method to set a sensor (primary or secondary).

        Args:
            sensor_name: Name of the sensor to display
            sensor_attr: Attribute name on plot_widget ('y1_sensor' or 'y2_sensor')
            is_primary: Whether this is the primary sensor
        """
        try:
            sensor_type = "primary" if is_primary else "secondary"
            self.logger.info("Setting %s sensor to: %s", sensor_type, sensor_name)

            # Update plot widget if available
            if hasattr(self.main_window, 'plot_widget') and self.main_window.plot_widget:
                setattr(self.main_window.plot_widget, sensor_attr, sensor_name)

                # Refresh the plot to show the new sensor
                if hasattr(self.main_window.plot_widget, '_refresh_plot'):
                    self.main_window.plot_widget._refresh_plot()

                # Update axis labels
                if hasattr(self.main_window.plot_widget, '_update_axis_labels'):
                    self.main_window.plot_widget._update_axis_labels()

            self.logger.info("%s sensor set to: %s", sensor_type.capitalize(), sensor_name)

        except Exception as e:
            sensor_type = "primary" if is_primary else "secondary"
            self.logger.error("Error setting %s sensor: %s", sensor_type, e)
            error_title = f"{sensor_type.capitalize()} Sensor Change Error"
            self.error_handler.handle_error(e, self.main_window, error_title)

    def set_secondary_sensor(self, sensor_name: str):
        """
        Set the secondary sensor for dual plot mode.

        Args:
            sensor_name: Name of the sensor to display in secondary plot
        """
        # Check if we're already in dual mode
        current_mode = getattr(self.main_window.plot_widget, 'plot_mode', 'single') if hasattr(self.main_window, 'plot_widget') and self.main_window.plot_widget else 'single'

        if current_mode != "dual":
            # Switch to dual mode first
            self.set_plot_mode("dual", secondary_sensor=sensor_name)
        else:
            # Already in dual mode, just update the sensor
            self._set_sensor(sensor_name, 'y2_sensor', is_primary=False)

    def set_plot_mode(self, mode: str, secondary_sensor: str = None):
        """
        Set the plot display mode (single or dual).

        Args:
            mode: "single" for one plot, "dual" for two plots
            secondary_sensor: Sensor for secondary plot (only used in dual mode)
        """
        try:
            self.logger.info("Setting plot mode to: %s", mode)

            if mode == "single":
                # Single plot mode - main plot takes full space
                if hasattr(self.main_window, 'plot_widget') and self.main_window.plot_widget:
                    # Ensure y1_sensor and data are set in plot widget
                    if hasattr(self, 'y1_sensor') and self.y1_sensor:
                        self.main_window.plot_widget.y1_sensor = self.y1_sensor
                    if self.tob_data_model:
                        self.main_window.plot_widget.tob_data_model = self.tob_data_model
                    self.main_window.plot_widget.set_single_mode()
                else:
                    self.logger.warning("No plot widget available for single mode")

            elif mode == "dual" and secondary_sensor:
                # Dual plot mode - two separate plots
                if hasattr(self.main_window, 'plot_widget') and self.main_window.plot_widget:
                    # Ensure y1_sensor is set in plot widget
                    if hasattr(self, 'y1_sensor') and self.y1_sensor:
                        self.main_window.plot_widget.y1_sensor = self.y1_sensor
                    # Ensure tob_data_model is available
                    if self.tob_data_model:
                        self.main_window.plot_widget.tob_data_model = self.tob_data_model
                    self.main_window.plot_widget.set_dual_mode(secondary_sensor)
                    # Note: _update_axis_labels() is already called in set_dual_mode() -> _configure_axes()
                else:
                    self.logger.warning("No plot widget available for dual mode")

            else:
                self.logger.warning("Invalid plot mode or missing secondary sensor: mode=%s, sensor=%s", mode, secondary_sensor)
                return

            self.logger.info("Plot mode set successfully to: %s", mode)

        except Exception as e:
            self.logger.error("Error setting plot mode: %s", e)
            self.error_handler.handle_error(
                e, self.main_window, "Plot Mode Change Error"
            )

    def update_x_axis_limits(self, min_value: float, max_value: float):
        """
        Update X-axis limits manually.

        Args:
            min_value: Minimum X-axis value in seconds
            max_value: Maximum X-axis value in seconds
        """
        try:
            self.logger.debug(
                "Updating X-axis limits: min=%.2f, max=%.2f", min_value, max_value
            )

            # Update plot with new X-axis limits (will emit signal)
            self.plot_controller.update_axis_limits("x", min_value, max_value)

            self.logger.info(
                "X-axis limits updated: min=%.2f, max=%.2f", min_value, max_value
            )

        except Exception as e:
            self.logger.error("Error updating X-axis limits: %s", e)
            self.error_handler.handle_error(
                e, self.main_window, "X-Axis Limits Update Error"
            )

    def update_y1_axis_limits(self, min_value: float, max_value: float):
        """
        Update Y1-axis limits manually.

        Args:
            min_value: Minimum Y1-axis value
            max_value: Maximum Y1-axis value
        """
        try:
            self.logger.debug(
                "Updating Y1-axis limits: min=%.2f, max=%.2f", min_value, max_value
            )

            # Update plot with new Y1-axis limits (will emit signal)
            self.plot_controller.update_axis_limits("y1", min_value, max_value)

            self.logger.info(
                "Y1-axis limits updated: min=%.2f, max=%.2f", min_value, max_value
            )

        except Exception as e:
            self.logger.error("Error updating Y1-axis limits: %s", e)
            self.error_handler.handle_error(
                e, self.main_window, "Y1-Axis Limits Update Error"
            )

    def update_y2_axis_limits(self, min_value: float, max_value: float):
        """
        Update Y2-axis limits manually.

        Args:
            min_value: Minimum Y2-axis value
            max_value: Maximum Y2-axis value
        """
        try:
            self.logger.debug(
                "Updating Y2-axis limits: min=%.2f, max=%.2f", min_value, max_value
            )

            # Update plot with new Y2-axis limits (will emit signal)
            self.plot_controller.update_axis_limits("y2", min_value, max_value)

            self.logger.info(
                "Y2-axis limits updated: min=%.2f, max=%.2f", min_value, max_value
            )

        except Exception as e:
            self.logger.error("Error updating Y2-axis limits: %s", e)
            self.error_handler.handle_error(
                e, self.main_window, "Y2-Axis Limits Update Error"
            )

    def _on_project_created(self, project_data: dict):
        """
        Handle project created signal from view.

        Args:
            project_data: Dictionary containing project creation data
                         (name, enter_key, server_url, description, file_path)
        """
        try:
            self.logger.info("Creating new project with data: %s", project_data)
            self.main_window.show_status_message("Creating project...")

            # Extract project data
            name = project_data.get("name", "")
            enter_key = project_data.get("enter_key", "")
            server_url = project_data.get("server_url", "")
            description = project_data.get("description", "")
            file_path = project_data.get("file_path", "")

            # Create project using project service
            project = self.project_service.create_project(
                name=name,
                enter_key=enter_key,
                server_url=server_url,
                description=description
            )

            # Save project to file
            self.project_service.save_project(project, file_path)

            # Update controller's project model
            self.project_model = project

            # Update main window state
            self.main_window.current_project_path = file_path

            # Update UI
            location = project.server_config.url if project.server_config else ""
            self.main_window.update_project_info(name, location, description)

            self.main_window.show_status_message("Project created successfully")
            self.logger.info("Project '%s' created and saved successfully", name)

            # Update memory usage for new project
            self.update_tob_memory_usage()

            # Note: Auto-save not needed for creation since we just saved manually

        except ValueError as e:
            # Validation errors
            self.logger.warning("Project validation error: %s", e)
            self.error_handler.handle_error(
                e, "Project Validation", self.main_window
            )
            self.main_window.show_status_message("Project validation failed")

        except Exception as e:
            self.logger.error("Error creating project: %s", e)
            self.error_handler.handle_error(
                e, "Project Creation", self.main_window
            )
            self.main_window.show_status_message("Error creating project")

    def update_project_settings(self, settings_data: dict):
        """
        Update settings of the currently loaded project.

        Args:
            settings_data: Dictionary containing updated project settings
                           (name, enter_key, server_url, description)
        """
        try:
            self.logger.info("Updating project settings: %s", settings_data)

            if not self.project_model:
                raise ValueError("No project is currently loaded")

            if not self.main_window.current_project_path:
                raise ValueError("No project file path available")

            # Extract updated data
            name = settings_data.get("name", "")
            enter_key = settings_data.get("enter_key", "")
            server_url = settings_data.get("server_url", "")
            description = settings_data.get("description", "")

            # Validate inputs using project service
            name = name.strip()
            enter_key = enter_key.strip()
            server_url = server_url.strip()

            self.project_service._validate_project_inputs(name, enter_key, server_url)

            # Update project model
            self.project_model.name = name
            self.project_model.description = description

            # Update server config (this handles URL normalization internally)
            self.project_service.update_project_server_config(
                self.project_model,
                enter_key=enter_key,
                server_url=server_url
            )

            # Save updated project
            self.project_service.save_project(self.project_model, self.main_window.current_project_path)

            # Update UI
            location = self.project_model.server_config.url if self.project_model.server_config else ""
            self.main_window.update_project_info(name, location, description)

            self.main_window.show_status_message("Project settings updated successfully")
            self.logger.info("Project settings updated and saved successfully")

            # Note: Auto-save not needed here since we just saved manually

        except ValueError as e:
            # Validation errors
            self.logger.warning("Project settings validation error: %s", e)
            self.error_handler.handle_error(
                e, "Project Settings Validation", self.main_window
            )
            self.main_window.show_status_message("Project settings validation failed")

        except Exception as e:
            self.logger.error("Error updating project settings: %s", e)
            self.error_handler.handle_error(
                e, "Project Settings Update", self.main_window
            )
            self.main_window.show_status_message("Error updating project settings")

    def _setup_auto_save(self) -> None:
        """
        Setup auto-save functionality with timer-based saving.
        """
        try:
            # Auto-save configuration
            self.auto_save_enabled = True
            self.auto_save_interval_ms = 5000  # 5 seconds (reduced for TOB file changes)
            self.auto_save_pending = False

            # Create timer for delayed auto-save
            self.auto_save_timer = QTimer()
            self.auto_save_timer.setSingleShot(True)
            self.auto_save_timer.timeout.connect(self._perform_auto_save)

            self.logger.info("Auto-save system initialized (interval: %dms)", self.auto_save_interval_ms)

        except Exception as e:
            self.logger.error("Failed to setup auto-save: %s", e)
            self.auto_save_enabled = False

    def trigger_auto_save(self) -> None:
        """
        Trigger auto-save after a change. Uses debouncing to avoid excessive saves.
        """
        if not self.auto_save_enabled or not self.project_model or not self.main_window.current_project_path:
            return

        try:
            if not self.auto_save_pending:
                self.logger.debug("Auto-save triggered, scheduling in %dms", self.auto_save_interval_ms)
                self.auto_save_pending = True

            # Reset timer (debounce)
            self.auto_save_timer.start(self.auto_save_interval_ms)

        except Exception as e:
            self.logger.error("Error triggering auto-save: %s", e)

    def _perform_auto_save(self) -> None:
        """
        Perform the actual auto-save operation.
        """
        if not self.auto_save_enabled or not self.project_model or not self.main_window.current_project_path:
            return

        try:
            self.logger.info("Performing auto-save...")
            self.auto_save_pending = False

            # Save project
            self.project_service.save_project(self.project_model, self.main_window.current_project_path)

            # Update status (don't show message to avoid spam)
            self.logger.info("Auto-save completed successfully")

        except Exception as e:
            self.logger.error("Auto-save failed: %s", e)
            self.auto_save_pending = False

            # Show error to user
            self.error_handler.handle_error(
                e, "Auto-Save Failed", self.main_window
            )

    def set_auto_save_interval(self, interval_ms: int) -> None:
        """
        Set the auto-save interval.

        Args:
            interval_ms: Interval in milliseconds (minimum 5000ms = 5 seconds)
        """
        try:
            # Enforce minimum interval
            interval_ms = max(interval_ms, 5000)

            self.auto_save_interval_ms = interval_ms
            self.logger.info("Auto-save interval set to %dms", interval_ms)

        except Exception as e:
            self.logger.error("Error setting auto-save interval: %s", e)

    def disable_auto_save(self) -> None:
        """
        Disable auto-save functionality.
        """
        self.auto_save_enabled = False
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()
        self.logger.info("Auto-save disabled")

    def enable_auto_save(self) -> None:
        """
        Enable auto-save functionality.
        """
        self.auto_save_enabled = True
        self.logger.info("Auto-save enabled")

    def _setup_memory_monitoring(self) -> None:
        """
        Setup memory monitoring for TOB file operations.
        """
        try:
            # Add cleanup callbacks for memory management
            self.memory_monitor.add_cleanup_callback(self._cleanup_tob_memory)
            self.memory_monitor.add_cleanup_callback(self._cleanup_plot_memory)

            # Start monitoring
            self.memory_monitor.start_monitoring()

            self.logger.info("Memory monitoring initialized")

        except Exception as e:
            self.logger.error(f"Failed to setup memory monitoring: {e}")

    def _cleanup_tob_memory(self) -> float:
        """
        Cleanup TOB-related memory when memory is critical.

        Returns:
            Amount of memory freed in MB
        """
        freed_mb = 0.0

        try:
            if self.project_model and self.project_model.tob_files:
                # Remove least recently used TOB files (keep only most recent 3)
                tob_files = sorted(
                    self.project_model.tob_files,
                    key=lambda f: f.added_date or datetime.min,
                    reverse=True
                )

                # Remove files beyond the first 3
                for tob_file in tob_files[3:]:
                    # Calculate memory usage of this file
                    file_memory = 0.0
                    if tob_file.tob_data and tob_file.tob_data.data is not None:
                        file_memory = tob_file.tob_data.data.memory_usage(deep=True).sum() / (1024 * 1024)

                    # Remove the file
                    if self.project_model.remove_tob_file(tob_file.file_name):
                        freed_mb += file_memory
                        self.logger.info(f"Cleaned up TOB file '{tob_file.file_name}' ({file_memory:.1f}MB)")

                        # Notify UI about removed file
                        if hasattr(self.main_window, 'show_status_message'):
                            self.main_window.show_status_message(
                                f"Removed '{tob_file.file_name}' to free memory"
                            )

                        # Trigger auto-save
                        self._mark_project_modified()

        except Exception as e:
            self.logger.error(f"Error during TOB memory cleanup: {e}")

        return freed_mb

    def _cleanup_plot_memory(self) -> float:
        """
        Cleanup plot-related memory when memory is critical.

        Returns:
            Amount of memory freed in MB
        """
        freed_mb = 0.0

        try:
            # Clear plot data if possible
            if hasattr(self, 'main_window') and self.main_window and hasattr(self.main_window, 'clear_plot_data'):
                self.main_window.clear_plot_data()
                self.logger.info("Cleared plot data for memory cleanup")

                # Estimate freed memory (rough estimate)
                freed_mb = 100.0  # Assume 100MB freed by clearing plot

        except Exception as e:
            self.logger.error(f"Error during plot memory cleanup: {e}")

        return freed_mb

    def check_memory_for_tob_operation(self, estimated_mb: float) -> bool:
        """
        Check if a TOB operation can proceed based on memory requirements.

        Args:
            estimated_mb: Estimated memory required in MB

        Returns:
            True if operation can proceed, False otherwise
        """
        can_proceed, reason = self.memory_monitor.check_memory_before_operation(estimated_mb)

        if not can_proceed:
            if self.main_window:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self.main_window,
                    "Memory Limit",
                    f"Cannot perform operation: {reason}\n\n"
                    "Try closing other applications or freeing up memory."
                )

        return can_proceed

    def initialize_http_client(self) -> bool:
        """
        Initialize HTTP client based on current project server configuration.

        Returns:
            True if client was initialized, False otherwise
        """
        try:
            if not self.project_model or not self.project_model.server_config:
                self.logger.warning("No project or server configuration available for HTTP client")
                self.http_client = None
                return False

            config = self.project_model.server_config

            # Validate server configuration
            if not config.url or not config.bearer_token:
                self.logger.warning("Incomplete server configuration - missing URL or token")
                self.http_client = None
                return False

            # Create HTTP client
            self.http_client = HttpClientService(
                base_url=config.url,
                bearer_token=config.bearer_token,
                error_handler=self.error_handler
            )

            # Test connection with health check
            if self.http_client.health_check():
                self.logger.info(f"HTTP client initialized successfully for {config.url}")
                return True
            else:
                self.logger.warning("HTTP client health check failed")
                self.http_client = None
                return False

        except Exception as e:
            self.logger.error(f"Failed to initialize HTTP client: {e}")
            self.http_client = None
            return False

    def upload_tob_file_to_server(self, file_name: str) -> bool:
        """
        Upload a TOB file to the configured server.

        Args:
            file_name: Name of the TOB file to upload

        Returns:
            True if upload was initiated successfully, False otherwise
        """
        try:
            if not self.http_client:
                if not self.initialize_http_client():
                    self.error_handler.handle_error(
                        ValueError("Server connection not available. Check server configuration."),
                        "Server Connection Error", self.main_window
                    )
                    return False

            if not self.project_model:
                return False

            # Get TOB file info
            tob_file = self.project_model.get_tob_file(file_name)
            if not tob_file:
                self.error_handler.handle_error(
                    ValueError(f"TOB file '{file_name}' not found in project"),
                    "File Not Found", self.main_window
                )
                return False

            # Check if file path exists
            if not Path(tob_file.file_path).exists():
                self.error_handler.handle_error(
                    ValueError(f"TOB file '{file_name}' not found on disk"),
                    "File Not Found", self.main_window
                )
                return False

            # Update status to uploading
            self.project_model.update_tob_file_status(file_name, "uploading")

            # Prepare metadata for upload
            metadata = {
                "file_name": tob_file.file_name,
                "file_size": tob_file.file_size,
                "data_points": tob_file.data_points,
                "sensors": tob_file.sensors or [],
                "project_name": self.project_model.name,
                "upload_timestamp": tob_file.added_date.isoformat() if tob_file.added_date else None
            }

            # Upload file
            upload_result = self.http_client.upload_tob_file(tob_file.file_path, metadata)

            if upload_result.success:
                # Update file with job ID if available
                if upload_result.job_id:
                    tob_file.server_job_id = upload_result.job_id

                # Update status to uploaded
                self.project_model.update_tob_file_status(file_name, "uploaded")

                # Update upload timestamp
                tob_file.upload_date = datetime.now()

                # Trigger auto-save
                self._mark_project_modified()

                self.logger.info(f"Successfully initiated upload for '{file_name}' (job: {upload_result.job_id})")

                # Emit signal for thread-safe GUI update
                self.show_upload_success.emit(
                    "Upload Started",
                    f"Upload of '{file_name}' to server has been initiated.\n\n"
                    f"Job ID: {upload_result.job_id or 'N/A'}\n"
                    f"Message: {upload_result.message or 'Upload in progress'}"
                )

                return True
            else:
                # Upload failed, reset status
                self.project_model.update_tob_file_status(file_name, "error")
                tob_file.error_message = upload_result.message

                self.error_handler.handle_error(
                    ValueError(f"Upload failed: {upload_result.message}"),
                    "Upload Failed", self.main_window
                )
                return False

        except Exception as e:
            self.logger.error(f"Error uploading TOB file: {e}")

            # Reset status on error
            if self.project_model:
                self.project_model.update_tob_file_status(file_name, "error")

            self.error_handler.handle_error(e, "Upload Error", self.main_window)
            return False

    def check_tob_file_server_status(self, file_name: str) -> None:
        """
        Check the server status of a TOB file upload/processing.

        Args:
            file_name: Name of the TOB file to check
        """
        try:
            if not self.http_client:
                if not self.initialize_http_client():
                    self.error_handler.handle_error(
                        ValueError("Server connection not available"),
                        "Server Connection Error", self.main_window
                    )
                    return

            if not self.project_model:
                return

            # Get TOB file info
            tob_file = self.project_model.get_tob_file(file_name)
            if not tob_file or not tob_file.server_job_id:
                self.error_handler.handle_error(
                    ValueError(f"No server job ID available for '{file_name}'"),
                    "No Job ID", self.main_window
                )
                return

            # Check processing status first (more detailed)
            status_result = self.http_client.get_processing_status(tob_file.server_job_id)

            if status_result.status == "error":
                # Check upload status as fallback
                status_result = self.http_client.get_upload_status(tob_file.server_job_id)

            # Update local status based on server response
            if status_result.status in ["completed", "processed"]:
                self.project_model.update_tob_file_status(file_name, "processed")
            elif status_result.status == "failed":
                self.project_model.update_tob_file_status(file_name, "error")
                tob_file.error_message = status_result.error_message
            elif status_result.status == "processing":
                self.project_model.update_tob_file_status(file_name, "processing")
            # Keep current status for other states

            # Show status to user
            message = f"Server Status for '{file_name}':\n\n"
            message += f"Status: {status_result.status.title()}\n"

            if status_result.progress is not None:
                message += f"Progress: {status_result.progress:.1f}%\n"

            if status_result.message:
                message += f"Message: {status_result.message}\n"

            if status_result.error_message:
                message += f"Error: {status_result.error_message}\n"

            if status_result.result_url:
                message += f"Result URL: {status_result.result_url}\n"

            # Emit signal for thread-safe GUI update
            self.show_server_status.emit("Server Status", message)

        except Exception as e:
            self.logger.error(f"Error checking server status: {e}")
            self.error_handler.handle_error(e, "Status Check Error", self.main_window)

    def update_tob_memory_usage(self) -> None:
        """
        Update the memory monitor with current TOB data memory usage.
        """
        try:
            if not self.project_model:
                return

            total_tob_memory = 0.0

            for tob_file in self.project_model.tob_files:
                if tob_file.tob_data and tob_file.tob_data.data is not None:
                    # Calculate memory usage of this TOB file
                    file_memory = tob_file.tob_data.data.memory_usage(deep=True).sum() / (1024 * 1024)
                    total_tob_memory += file_memory

            # Update memory monitor
            self.memory_monitor.update_tob_memory_usage(total_tob_memory)

            self.logger.debug(f"Updated TOB memory usage: {total_tob_memory:.1f}MB")

        except Exception as e:
            self.logger.error(f"Error updating TOB memory usage: {e}")

    def _mark_project_modified(self) -> None:
        """
        Mark project as modified and trigger auto-save.
        Call this whenever project data changes.
        """
        if self.project_model:
            self.project_model.update_modified_date()
            # For TOB file changes, save immediately instead of waiting
            if hasattr(self, 'auto_save_enabled') and self.auto_save_enabled:
                self._perform_immediate_save()
            else:
                self.trigger_auto_save()

    def _perform_immediate_save(self) -> None:
        """
        Perform immediate save without timer delay.
        Used for critical changes like TOB file additions/removals.
        """
        if not self.project_model or not self.main_window.current_project_path:
            return

        try:
            self.logger.debug("Performing immediate save...")
            self.project_service.save_project(self.project_model, self.main_window.current_project_path)
            self.logger.debug("Immediate save completed successfully")
        except Exception as e:
            self.logger.error("Immediate save failed: %s", e)

    def _on_project_opened(self, project_path: str):
        """
        Handle project opened signal from view.

        Args:
            project_path: Path to the project file (no password needed with app-internal encryption)
        """
        try:
            self.logger.info("Opening project: %s", project_path)
            self.main_window.show_status_message("Opening project...")

            # Load project using project service (app-internal encryption)
            project = self.project_service.load_project(project_path)

            # Update controller's project model
            self.project_model = project

            # Update main window state
            self.main_window.current_project_path = project_path

            # Update UI with project info
            location = project.server_config.url if project.server_config else ""
            self.main_window.update_project_info(project.name, location, project.description or "")

            # If project has TOB files, reload their data from disk
            if project.tob_files:
                self.logger.info("Project has %d TOB files, reloading data...", len(project.tob_files))
                self._reload_tob_files_data(project)

            # Update memory usage for loaded project
            self.update_tob_memory_usage()

            self.main_window.show_status_message("Project opened successfully")
            self.logger.info("Project '%s' opened successfully", project.name)

        except FileNotFoundError as e:
            self.logger.error("Project file not found: %s", e)
            self.error_handler.show_error(
                "Project File Not Found", f"Could not find project file: {project_path}"
            )
            self.main_window.show_status_message("Project file not found")

        except Exception as e:
            self.logger.error("Error opening project: %s", e)
            self.error_handler.show_error(
                "Project Opening Error", f"Failed to open project: {e}"
            )
            self.main_window.show_status_message("Error opening project")

    def _reload_tob_files_data(self, project: ProjectModel) -> None:
        """
        Reload TOB file data from disk for a loaded project.

        Args:
            project: ProjectModel with TOB files to reload
        """
        try:
            from ..services.tob_service import TOBService
            tob_service = TOBService()

            reloaded_count = 0
            failed_count = 0

            for tob_file in project.tob_files:
                try:
                    # Check if file still exists
                    if not Path(tob_file.file_path).exists():
                        self.logger.warning("TOB file no longer exists: %s", tob_file.file_path)
                        tob_file.status = "error"
                        failed_count += 1
                        continue

                    # Reload the TOB data
                    tob_data = tob_service.load_tob_file_with_timeout(tob_file.file_path)

                    # Update the TOB file data
                    tob_file.tob_data = tob_data
                    tob_file.data_points = len(tob_data.data) if tob_data.data is not None else 0
                    tob_file.status = "loaded"

                    reloaded_count += 1
                    self.logger.debug("Reloaded TOB file: %s", tob_file.file_name)

                except Exception as e:
                    self.logger.error("Failed to reload TOB file %s: %s", tob_file.file_name, e)
                    tob_file.status = "error"
                    failed_count += 1

            self.logger.info("TOB file reload complete: %d reloaded, %d failed",
                           reloaded_count, failed_count)

        except Exception as e:
            self.logger.error("Error reloading TOB files: %s", e)

    def update_sensor_selection(self, sensor_name: str, is_selected: bool):
        """
        Update sensor selection for visualization.

        Args:
            sensor_name: Name of the sensor
            is_selected: Whether the sensor is selected
        """
        self.logger.debug("Sensor selection updated: %s = %s", sensor_name, is_selected)

        # TODO: Update plot visualization
        # This will be implemented when we add the plotting functionality

    def show_main_window(self):
        """
        Show the main window.
        """
        self.main_window.show()
        self.logger.info("Main window displayed")

    def get_main_window(self):
        """
        Get the main window instance.

        Returns:
            MainWindow: The main window instance
        """
        return self.main_window
