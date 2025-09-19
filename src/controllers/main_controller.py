"""
Main controller for the WIZARD-2.1 application.

This module contains the main controller class that coordinates between
the models, views, and services.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal

from ..models.project_model import ProjectModel
from ..models.tob_data_model import TOBDataModel
from ..services.data_service import DataService
from ..services.encryption_service import EncryptionService
from ..services.error_service import ErrorService
from ..services.plot_service import PlotService
from ..services.tob_service import TOBService
from ..utils.error_handler import ErrorHandler


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

    def __init__(self, main_window=None):
        """
        Initialize the main controller.

        Args:
            main_window: Main window instance (optional, for dependency injection)
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)

        # Initialize services
        self.tob_service = TOBService()
        self.data_service = DataService()
        self.plot_service = PlotService()
        self.encryption_service = EncryptionService()
        self.error_service = ErrorService()
        self.error_handler = ErrorHandler()

        # Initialize models
        self.tob_data_model: Optional[TOBDataModel] = None
        self.project_model = ProjectModel(name="Untitled Project")

        # Initialize view
        if main_window is not None:
            self.main_window = main_window
            # Connect controller to window
            self.main_window.set_controller(self)
        else:
            # Fallback: create window (backward compatibility)
            from ..views.main_window import MainWindow
            self.main_window = MainWindow(controller=self)

        # Connect signals
        self._connect_signals()

        self.logger.info("Main controller initialized successfully")

    def _connect_signals(self):
        """
        Connect signals between view and controller.
        """
        # Connect view signals to controller methods
        self.main_window.file_opened.connect(self._on_file_opened)
        self.main_window.project_created.connect(self._on_project_created)
        self.main_window.project_opened.connect(self._on_project_opened)

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

            # Validate file before loading
            if not self.tob_service.validate_tob_file(file_path):
                raise ValueError(f"Invalid TOB file format: {file_path}")

            self.file_load_progress.emit(30)

            # Load TOB data using service
            self.tob_data_model = self.tob_service.load_tob_file(file_path)
            self.file_load_progress.emit(60)

            # Process the loaded data
            processed_data = self.data_service.process_tob_data(self.tob_data_model)
            self.file_load_progress.emit(80)

            # Update view with loaded data
            self._update_view_with_tob_data()

            # Emit signals for UI updates
            self.file_loaded.emit(file_path, self.tob_data_model)
            self.data_processed.emit(processed_data)
            self.sensors_updated.emit(self.tob_data_model.sensors)

            self.file_load_progress.emit(100)
            self.main_window.display_status_message("File loaded successfully", 2000)
            self.logger.info("TOB file loaded successfully: %s", file_path)

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

    def _update_view_with_tob_data(self):
        """
        Update the view with loaded TOB data.
        """
        try:
            if not self.tob_data_model:
                self.logger.warning("No TOB data model available for view update")
                return

            # Update project information
            metadata = self.tob_data_model.get_metadata()
            self.main_window.update_project_info(
                project_name=Path(metadata.get("file_path", "")).stem,
                location="TOB Data",
                comment=f"Data points: {metadata.get('data_points', 0)}"
            )

            # Update data metrics
            if self.tob_data_model.data is not None:
                metrics = self.data_service._calculate_metrics(self.tob_data_model)
                self.main_window.update_data_metrics(metrics)

            # Update sensor checkboxes
            self._update_sensor_checkboxes()

            # Update plot with data
            self.main_window.update_plot_data(self.tob_data_model)

            # Update sensor selection for plotting (automatically select all NTC sensors and PT100)
            selected_sensors = [sensor for sensor in self.tob_data_model.sensors if sensor.startswith('NTC')]

            # Add PT100 sensor if available
            pt100_sensor = self.tob_data_model.get_pt100_sensor()
            if pt100_sensor:
                selected_sensors.append(pt100_sensor)
                self.logger.debug("PT100 sensor added to selection: %s", pt100_sensor)

            if selected_sensors:
                self.main_window.update_plot_sensors(selected_sensors)
                self.logger.debug("Auto-selected %d sensors for plotting: %s", len(selected_sensors), selected_sensors)

            # Switch to plot mode and show data loaded
            self.main_window.ui_state_manager.show_plot_mode()
            self.main_window.show_data_loaded()

            self.logger.debug("View updated with TOB data successfully")

        except Exception as e:
            self.logger.error("Error updating view with TOB data: %s", e)
            self.error_handler.handle_error(e, self.main_window, "View Update Error")

    def _update_sensor_checkboxes(self):
        """
        Update sensor checkboxes based on available sensors.
        """
        try:
            if not self.tob_data_model or not self.tob_data_model.sensors:
                self.logger.warning("No sensors available for checkbox update")
                return

            # Get available sensors
            available_sensors = self.tob_data_model.sensors
            
            # Update NTC checkboxes
            for sensor_name, checkbox in self.main_window.ntc_checkboxes.items():
                if sensor_name in available_sensors:
                    checkbox.setVisible(True)
                    checkbox.setEnabled(True)
                    checkbox.setChecked(True)  # Default to selected
                else:
                    checkbox.setVisible(False)
                    checkbox.setEnabled(False)
                    checkbox.setChecked(False)

            # Update PT100 checkbox
            if hasattr(self.main_window, 'ntc_pt100_checkbox') and self.main_window.ntc_pt100_checkbox:
                pt100_sensor = self.tob_data_model.get_pt100_sensor()
                if pt100_sensor:
                    self.main_window.ntc_pt100_checkbox.setVisible(True)
                    self.main_window.ntc_pt100_checkbox.setEnabled(True)
                    self.main_window.ntc_pt100_checkbox.setChecked(True)
                else:
                    self.main_window.ntc_pt100_checkbox.setVisible(False)
                    self.main_window.ntc_pt100_checkbox.setEnabled(False)
                    self.main_window.ntc_pt100_checkbox.setChecked(False)

            self.logger.debug("Sensor checkboxes updated successfully")

        except Exception as e:
            self.logger.error("Error updating sensor checkboxes: %s", e)
            self.error_handler.handle_error(e, self.main_window, "Sensor Update Error")

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
            self.logger.debug("Controller: handling sensor selection change: %s = %s", sensor_name, is_selected)

            # Get current selected sensors from the view
            current_selected = self._get_selected_sensors()
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

            # Update the plot view with new sensor selection
            if self.main_window:
                self.main_window.update_plot_sensors(new_selected)

            if is_selected:
                self.logger.info("Sensor %s selected for visualization", sensor_name)
            else:
                self.logger.info("Sensor %s deselected from visualization", sensor_name)

        except Exception as e:
            self.logger.error("Failed to handle sensor selection change: %s", e)
            raise

    def _get_selected_sensors(self) -> List[str]:
        """
        Get list of currently selected sensors.
        
        Returns:
            List of selected sensor names
        """
        try:
            selected_sensors = []
            
            # Check all NTC checkboxes (including PT100 which is registered as "Temp")
            for sensor_name, checkbox in self.main_window.ntc_checkboxes.items():
                if checkbox and checkbox.isChecked():
                    selected_sensors.append(sensor_name)
            
            self.logger.debug("Selected sensors: %s", selected_sensors)
            return selected_sensors
            
        except Exception as e:
            self.logger.error("Error getting selected sensors: %s", e)
            return []

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
            axis_settings = {
                f'{axis_name}_auto': is_auto
            }
            
            # Update plot with new axis settings
            self.main_window.update_plot_axis_settings(axis_settings)
            
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

            # Update plot with new axis settings
            self.main_window.update_plot_axis_settings(axis_settings)

            self.logger.info("Axis settings updated: %s", axis_settings)

        except Exception as e:
            self.logger.error("Error updating axis settings: %s", e)
            self.error_handler.handle_error(e, self.main_window, "Axis Settings Update Error")

    def update_x_axis_limits(self, min_value: float, max_value: float):
        """
        Update X-axis limits manually.

        Args:
            min_value: Minimum X-axis value in seconds
            max_value: Maximum X-axis value in seconds
        """
        try:
            self.logger.debug("Updating X-axis limits: min=%.2f, max=%.2f", min_value, max_value)

            # Update plot with new X-axis limits
            self.main_window.update_plot_x_limits(min_value, max_value)

            self.logger.info("X-axis limits updated: min=%.2f, max=%.2f", min_value, max_value)

        except Exception as e:
            self.logger.error("Error updating X-axis limits: %s", e)
            self.error_handler.handle_error(e, self.main_window, "X-Axis Limits Update Error")

    def update_y1_axis_limits(self, min_value: float, max_value: float):
        """
        Update Y1-axis limits manually.

        Args:
            min_value: Minimum Y1-axis value
            max_value: Maximum Y1-axis value
        """
        try:
            self.logger.debug("Updating Y1-axis limits: min=%.2f, max=%.2f", min_value, max_value)

            # Update plot with new Y1-axis limits
            self.main_window.update_plot_y1_limits(min_value, max_value)

            self.logger.info("Y1-axis limits updated: min=%.2f, max=%.2f", min_value, max_value)

        except Exception as e:
            self.logger.error("Error updating Y1-axis limits: %s", e)
            self.error_handler.handle_error(e, self.main_window, "Y1-Axis Limits Update Error")

    def update_y2_axis_limits(self, min_value: float, max_value: float):
        """
        Update Y2-axis limits manually.

        Args:
            min_value: Minimum Y2-axis value
            max_value: Maximum Y2-axis value
        """
        try:
            self.logger.debug("Updating Y2-axis limits: min=%.2f, max=%.2f", min_value, max_value)

            # Update plot with new Y2-axis limits
            self.main_window.update_plot_y2_limits(min_value, max_value)

            self.logger.info("Y2-axis limits updated: min=%.2f, max=%.2f", min_value, max_value)

        except Exception as e:
            self.logger.error("Error updating Y2-axis limits: %s", e)
            self.error_handler.handle_error(e, self.main_window, "Y2-Axis Limits Update Error")

    def _on_project_created(self, project_path: str, password: str):
        """
        Handle project created signal from view.

        Args:
            project_path: Path to the project file
            password: Project password
        """
        try:
            self.logger.info("Creating project: %s", project_path)
            self.main_window.show_status_message("Creating project...")

            # Create project using encryption service
            self.encryption_service.create_project(
                project_path, password, self.tob_data_model
            )

            self.main_window.show_status_message("Project created successfully")
            self.logger.info("Project created successfully")

        except Exception as e:
            self.logger.error("Error creating project: %s", e)
            self.error_handler.show_error(
                "Project Creation Error", f"Failed to create project: {e}"
            )
            self.main_window.show_status_message("Error creating project")

    def _on_project_opened(self, project_path: str, password: str):
        """
        Handle project opened signal from view.

        Args:
            project_path: Path to the project file
            password: Project password
        """
        try:
            self.logger.info("Opening project: %s", project_path)
            self.main_window.show_status_message("Opening project...")

            # Load project using encryption service
            project_data = self.encryption_service.load_project(project_path, password)

            # Update models
            self.project_model.set_data(project_data)
            if project_data.get("tob_data"):
                self.tob_data_model.set_data(project_data["tob_data"])

            # Update view
            self._update_view_with_data()
            self._update_view_with_project_info()

            self.main_window.show_status_message("Project opened successfully")
            self.logger.info("Project opened successfully")

        except Exception as e:
            self.logger.error("Error opening project: %s", e)
            self.error_handler.show_error(
                "Project Opening Error", f"Failed to open project: {e}"
            )
            self.main_window.show_status_message("Error opening project")

    def _update_view_with_data(self):
        """
        Update the view with loaded data.
        """
        if not self.tob_data_model.has_data():
            return

        # Calculate data metrics
        metrics = self.data_service.calculate_metrics(self.tob_data_model.get_data())

        # Update view
        self.main_window.update_data_metrics(metrics)
        self.main_window.show_data_loaded()

        self.logger.debug("View updated with data")

    def _update_view_with_project_info(self):
        """
        Update the view with project information.
        """
        if not self.project_model.has_data():
            return

        project_data = self.project_model.get_data()

        # Update project info in view
        project_name = project_data.get("name", "Unknown Project")
        location = project_data.get("location", "Unknown Location")
        comment = project_data.get("comment", "")

        self.main_window.update_project_info(project_name, location, comment)

        self.logger.debug("View updated with project info")

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
