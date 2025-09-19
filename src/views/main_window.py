"""
Main window view for the WIZARD-2.1 application.

This module contains the main window class that serves as the primary interface
for the temperature data analysis application.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog,
                             QFrame, QLabel, QLineEdit, QMainWindow,
                             QPushButton, QWidget)

from ..services.data_service import DataService
from ..services.plot_service import PlotService
from ..services.plot_style_service import PlotStyleService
from ..services.ui_service import UIService
from ..services.ui_state_manager import UIStateManager
from ..utils.error_handler import ErrorHandler


class MainWindow(QMainWindow):
    """
    Main window class for the WIZARD-2.1 application.

    This class represents the primary user interface window and handles
    the main application layout and user interactions. It integrates with
    the Qt Designer .ui file for the visual layout.
    """

    # Signals for communication with controller
    file_opened = pyqtSignal(str)  # Emitted when a file is opened
    project_created = pyqtSignal(
        str, str
    )  # Emitted when project is created (path, password)
    project_opened = pyqtSignal(
        str, str
    )  # Emitted when project is opened (path, password)

    def __init__(self, controller=None):
        """
        Initialize the main window.

        Args:
            controller: The main controller instance for handling business logic
        """
        super().__init__()

        self.logger = logging.getLogger(__name__)
        self.controller = controller
        self.error_handler = ErrorHandler()

        # Initialize services
        self.ui_state_manager = UIStateManager()
        self.ui_service = UIService()
        self.data_service = DataService()
        self.plot_service = PlotService()

        # UI state
        self.current_file_path: Optional[str] = None
        self.current_project_path: Optional[str] = None
        self.is_data_loaded = False

        # Initialize UI components
        self._setup_ui()
        self._connect_signals()
        self._setup_menu_bar()
        self._setup_status_bar()

        self.logger.info("Main window initialized successfully")

    def _setup_ui(self):
        """
        Set up the user interface components using the Qt Designer .ui file.
        """
        try:
            # Load the UI file
            ui_file_path = Path(__file__).parent.parent.parent / "ui" / "main_window.ui"
            uic.loadUi(str(ui_file_path), self)

            # Store references to important widgets
            self._store_widget_references()

            # Set up UI state manager with container references
            self.ui_state_manager.set_containers(
                self.welcome_container, self.plot_container
            )
            
            # Debug logging for UI state manager setup
            self.logger.info("UI state manager containers set - welcome: %s, plot: %s", 
                           self.welcome_container is not None, self.plot_container is not None)

            # Initialize UI state
            self._initialize_ui_state()

            self.logger.info("UI loaded successfully from .ui file")

        except (FileNotFoundError, OSError) as e:
            self.logger.error("UI file not found or inaccessible: %s", e)
            self.error_handler.handle_error(e, self, "UI File Error")
            raise
        except Exception as e:
            self.logger.error("Unexpected error loading UI: %s", e)
            self.error_handler.handle_error(e, self, "UI Loading Error")
            raise

    def _store_widget_references(self):
        """
        Store references to important UI widgets for easy access.
        """
        # Welcome screen widgets
        self.welcome_container = self.findChild(QWidget, "welcome_container")
        self.welcome_open_tob_button = self.findChild(
            QPushButton, "welcome_open_tob_button"
        )
        self.welcome_open_project_button = self.findChild(
            QPushButton, "welcome_open_project_button"
        )

        # Plot area widgets
        self.plot_container = self.findChild(QFrame, "plot_container")
        self.plot_canvas_container = self.findChild(QWidget, "plot_canvas_container")
        self.plot_info_container = self.findChild(QFrame, "plot_info_container")
        
        # Debug logging for plot containers
        self.logger.info("Plot container found: %s", self.plot_container is not None)
        self.logger.info("Plot canvas container found: %s", self.plot_canvas_container is not None)
        self.logger.info("Plot info container found: %s", self.plot_info_container is not None)
        
        # Initialize plot widget
        self.plot_widget = None
        self._initialize_plot_widget()

        # Project info labels
        self.cruise_info_label = self.findChild(QLabel, "cruise_info_label")
        self.location_info_label = self.findChild(QLabel, "location_info_label")

        # NTC sensor checkboxes
        self.ntc_checkboxes = {}
        for i in range(1, 23):  # NTC01 to NTC22
            checkbox_name = f"ntc_{i:02d}_checkbox"
            checkbox = self.findChild(QCheckBox, checkbox_name)
            if checkbox:
                self.ntc_checkboxes[f"NTC{i:02d}"] = checkbox

        # PT100 checkbox (stored as "Temp" in data)
        self.ntc_pt100_checkbox = self.findChild(QCheckBox, "ntc_pt100_checkbox")
        if self.ntc_pt100_checkbox:
            self.ntc_checkboxes["Temp"] = self.ntc_pt100_checkbox

        # Initialize plot style service (central style definitions)
        self.plot_style_service = PlotStyleService()

        # Create style indicators for NTC checkboxes (delayed setup)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self._setup_style_indicators)  # Delay by 100ms

        # Data metrics widgets
        self.mean_hp_power_value = self.findChild(QLineEdit, "mean_hp_power_value")
        self.max_v_accu_value = self.findChild(QLineEdit, "max_v_accu_value")
        self.tilt_status_value = self.findChild(QLineEdit, "tilt_status_value")
        self.mean_press_value = self.findChild(QLineEdit, "mean_press_value")

        # Axis control widgets
        self.y1_axis_combo = self.findChild(QComboBox, "y1_axis_combo")
        self.y2_axis_combo = self.findChild(QComboBox, "y2_axis_combo")
        self.x_axis_combo = self.findChild(QComboBox, "x_axis_combo")

        # Create axis_combos dictionary for service usage
        self.axis_combos = {
            "y1_axis_combo": self.y1_axis_combo,
            "y2_axis_combo": self.y2_axis_combo,
            "x_axis_combo": self.x_axis_combo,
        }

        self.y1_min_value = self.findChild(QLineEdit, "y1_min_value")
        self.y1_max_value = self.findChild(QLineEdit, "y1_max_value")
        self.y2_min_value = self.findChild(QLineEdit, "y2_min_value")
        self.y2_max_value = self.findChild(QLineEdit, "y2_max_value")
        self.x_min_value = self.findChild(QLineEdit, "x_min_value")
        self.x_max_value = self.findChild(QLineEdit, "x_max_value")

        self.y1_auto_checkbox = self.findChild(QCheckBox, "y1_auto_checkbox")
        self.y2_auto_checkbox = self.findChild(QCheckBox, "y2_auto_checkbox")
        self.x_auto_checkbox = self.findChild(QCheckBox, "x_auto_checkbox")

        # Project control widgets
        self.location_subcon_spin = self.findChild(
            QDoubleSpinBox, "location_subcon_spin"
        )
        self.location_comment_value = self.findChild(
            QLineEdit, "location_comment_value"
        )
        self.location_sensorstring_value = self.findChild(
            QLineEdit, "location_sensorstring_value"
        )

        # Action buttons
        self.quality_control_button = self.findChild(
            QPushButton, "quality_control_button"
        )
        self.send_data_button = self.findChild(QPushButton, "send_data_button")
        self.request_status_button = self.findChild(
            QPushButton, "request_status_button"
        )
        self.status_lineEdit = self.findChild(QLineEdit, "status_lineEdit")

        self.logger.debug("Widget references stored successfully")

    def _initialize_ui_state(self):
        """
        Initialize the UI to its default state.
        """
        # Setup fonts and fix visibility using services
        self.ui_service.setup_fonts(self)
        self.ui_service.fix_ui_visibility(self)

        # Show welcome screen initially (reset to initial state)
        self.ui_state_manager.reset_to_initial_state()

        # Initialize axis controls
        self._initialize_axis_controls()

        # Set default values
        self._reset_data_metrics()
        self._reset_project_info()

        self.logger.debug("UI state initialized")

    def _initialize_plot_widget(self):
        """
        Initialize the plot widget for data visualization.
        """
        try:
            self.logger.info("Initializing plot widget...")
            
            if self.plot_canvas_container:
                self.logger.info("Plot canvas container found, creating plot widget")
                
                # Create plot widget
                self.plot_widget = self.plot_service.create_plot_widget(self.plot_canvas_container)
                self.logger.info("Plot widget created successfully")
                
                # Add plot widget to the container layout
                from PyQt6.QtWidgets import QVBoxLayout
                
                # Check if container already has a layout
                existing_layout = self.plot_canvas_container.layout()
                if existing_layout:
                    # Clear existing layout
                    while existing_layout.count():
                        child = existing_layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()
                    existing_layout.deleteLater()
                
                # Create new layout
                layout = QVBoxLayout()
                layout.addWidget(self.plot_widget)
                layout.setContentsMargins(0, 0, 0, 0)
                self.plot_canvas_container.setLayout(layout)
                
                # Make sure the plot widget is visible
                self.plot_widget.setVisible(True)
                self.plot_canvas_container.setVisible(True)
                
                self.logger.info("Plot widget initialized and made visible successfully")
            else:
                self.logger.warning("Plot canvas container not found, plot widget not initialized")
        except Exception as e:
            self.logger.error("Failed to initialize plot widget: %s", e)
            self.error_handler.handle_error(e, self, "Plot Widget Initialization Error")

    def _initialize_axis_controls(self):
        """
        Initialize the axis control comboboxes with available options.
        """
        # Use UI service for axis control setup
        self.ui_service.setup_axis_controls(self.axis_combos)

    def _setup_menu_bar(self):
        """
        Set up the menu bar and connect actions.
        """
        # File menu actions
        self.open_action = self.findChild(QAction, "open_action")
        self.info_action = self.findChild(QAction, "info_action")
        self.exit_action = self.findChild(QAction, "exit_action")

        # Project menu actions
        self.actionCreate_Project_File = self.findChild(
            QAction, "actionCreate_Project_File"
        )
        self.actionOpen_Project_File = self.findChild(
            QAction, "actionOpen_Project_File"
        )
        self.actionEdit_Project_Settings = self.findChild(
            QAction, "actionEdit_Project_Settings"
        )
        self.actionShow_Processing_List = self.findChild(
            QAction, "actionShow_Processing_List"
        )

        # Tools menu actions
        self.actionEnglish = self.findChild(QAction, "actionEnglish")
        self.actionGerman = self.findChild(QAction, "actionGerman")
        self.actionToggle_Sidebar = self.findChild(QAction, "actionToggle_Sidebar")
        self.actionSelect_all = self.findChild(QAction, "actionSelect_all")
        self.actionDeseselct_all = self.findChild(QAction, "actionDeseselct_all")

        self.logger.debug("Menu bar setup completed")

    def _setup_status_bar(self):
        """
        Set up the status bar.
        """
        self.statusbar = self.findChild(QWidget, "statusbar")
        if self.statusbar:
            self.statusbar.showMessage("Ready")

    def _connect_signals(self):
        """
        Connect UI signals to their respective handlers.
        """
        # Welcome screen buttons
        if self.welcome_open_tob_button:
            self.welcome_open_tob_button.clicked.connect(self._on_open_tob_file)

        if self.welcome_open_project_button:
            self.welcome_open_project_button.clicked.connect(self._on_open_project)

        # Menu actions
        if self.open_action:
            self.open_action.triggered.connect(self._on_open_tob_file)

        if self.exit_action:
            self.exit_action.triggered.connect(self.close)

        if self.actionCreate_Project_File:
            self.actionCreate_Project_File.triggered.connect(self._on_create_project)

        if self.actionOpen_Project_File:
            self.actionOpen_Project_File.triggered.connect(self._on_open_project)

        # NTC checkbox changes
        for sensor_name, checkbox in self.ntc_checkboxes.items():
            checkbox.stateChanged.connect(
                lambda state, name=sensor_name: self._on_sensor_selection_changed(
                    name, state
                )
            )

        # Axis control changes
        if self.y1_auto_checkbox:
            self.y1_auto_checkbox.stateChanged.connect(self._on_y1_auto_changed)

        if self.y2_auto_checkbox:
            self.y2_auto_checkbox.stateChanged.connect(self._on_y2_auto_changed)

        if self.x_auto_checkbox:
            self.x_auto_checkbox.stateChanged.connect(self._on_x_auto_changed)

        # Action buttons
        if self.quality_control_button:
            self.quality_control_button.clicked.connect(self._on_quality_control)

        if self.send_data_button:
            self.send_data_button.clicked.connect(self._on_send_data)

        if self.request_status_button:
            self.request_status_button.clicked.connect(self._on_request_status)

        self.logger.debug("Signals connected successfully")

    def _show_welcome_screen(self):
        """
        Show the welcome screen and hide plot area.
        """
        self.ui_state_manager.show_welcome_mode()
        self.logger.debug("Welcome screen displayed")

    def _show_plot_area(self):
        """
        Show the plot area and hide welcome screen.
        """
        self.ui_state_manager.show_plot_mode()
        self.logger.debug("Plot area displayed")

    def _reset_data_metrics(self):
        """
        Reset data metrics to default values.
        """
        # Use data service for metrics reset
        metrics_widgets = {
            "mean_hp_power_value": self.mean_hp_power_value,
            "max_v_accu_value": self.max_v_accu_value,
            "tilt_status_value": self.tilt_status_value,
            "mean_press_value": self.mean_press_value,
        }
        self.data_service.reset_data_metrics(metrics_widgets)

    def _reset_project_info(self):
        """
        Reset project information to default values.
        """
        # Use UI service for project info reset
        project_widgets = {
            "cruise_info_label": self.cruise_info_label,
            "location_info_label": self.location_info_label,
            "location_comment_value": self.location_comment_value,
            "location_sensorstring_value": self.location_sensorstring_value,
            "location_subcon_spin": self.location_subcon_spin,
        }
        self.ui_service.reset_ui_widgets(project_widgets)

    # Event handlers
    def _on_open_tob_file(self):
        """
        Handle opening a TOB file.
        """
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open TOB File", "", "TOB Files (*.tob *.TOB);;All Files (*)"
            )

            if file_path:
                self.logger.info("Opening TOB file: %s", file_path)
                self.file_opened.emit(file_path)
                # The controller will handle switching to plot mode

        except (FileNotFoundError, PermissionError) as e:
            self.logger.error("File access error: %s", e)
            self.error_handler.handle_error(e, self, "File Access Error")
        except Exception as e:
            self.logger.error("Unexpected error opening TOB file: %s", e)
            self.error_handler.handle_error(e, self, "File Open Error")

    def _on_open_project(self):
        """
        Handle opening a project file.
        """
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Project File",
                "",
                "WIZARD Project Files (*.wzp);;All Files (*)",
            )

            if file_path:
                # TODO: Show password dialog
                password = "default_password"  # Placeholder
                self.logger.info("Opening project file: %s", file_path)
                self.project_opened.emit(file_path, password)
                # Switch to plot mode when project is loaded
                self.ui_state_manager.show_plot_mode()

        except (FileNotFoundError, PermissionError) as e:
            self.logger.error("Project file access error: %s", e)
            self.error_handler.handle_error(e, self, "Project File Access Error")
        except Exception as e:
            self.logger.error("Unexpected error opening project: %s", e)
            self.error_handler.handle_error(e, self, "Project Open Error")

    def _on_create_project(self):
        """
        Handle creating a new project.
        """
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Create Project File",
                "",
                "WIZARD Project Files (*.wzp);;All Files (*)",
            )

            if file_path:
                # TODO: Show project creation dialog with password
                password = "default_password"  # Placeholder
                self.logger.info("Creating project file: %s", file_path)
                self.project_created.emit(file_path, password)

        except (OSError, PermissionError) as e:
            self.logger.error("File system error creating project: %s", e)
            self.error_handler.handle_error(e, self, "Project Creation File Error")
        except Exception as e:
            self.logger.error("Unexpected error creating project: %s", e)
            self.error_handler.handle_error(e, self, "Project Creation Error")

    def _on_sensor_selection_changed(self, sensor_name: str, state: int):
        """
        Handle sensor selection changes.

        MVC-compliant: View informs Controller about UI events.
        Controller decides what to do and updates views accordingly.

        Args:
            sensor_name: Name of the sensor (e.g., "NTC01", "Temp")
            state: Checkbox state (0 = unchecked, 2 = checked)
        """
        is_selected = state == 2
        self.logger.debug("View: sensor %s selection changed: %s", sensor_name, is_selected)

        # MVC: View informs Controller about UI event
        # Controller handles the logic and updates views
        if self.controller:
            self.controller.handle_sensor_selection_changed(sensor_name, is_selected)

    def _on_y1_auto_changed(self, state: int):
        """Handle Y1 axis auto mode change."""
        is_auto = state == 2
        self.logger.debug("Y1 axis auto mode: %s", is_auto)

        # Enable/disable manual controls
        if self.y1_min_value and self.y1_max_value:
            self.y1_min_value.setEnabled(not is_auto)
            self.y1_max_value.setEnabled(not is_auto)

    def _on_y2_auto_changed(self, state: int):
        """Handle Y2 axis auto mode change."""
        is_auto = state == 2
        self.logger.debug("Y2 axis auto mode: %s", is_auto)

        # Enable/disable manual controls
        if self.y2_min_value and self.y2_max_value:
            self.y2_min_value.setEnabled(not is_auto)
            self.y2_max_value.setEnabled(not is_auto)

    def _on_x_auto_changed(self, state: int):
        """Handle X axis auto mode change."""
        is_auto = state == 2
        self.logger.debug("X axis auto mode: %s", is_auto)

        # Enable/disable manual controls
        if self.x_min_value and self.x_max_value:
            self.x_min_value.setEnabled(not is_auto)
            self.x_max_value.setEnabled(not is_auto)

    def _on_quality_control(self):
        """Handle quality control button click."""
        self.logger.info("Quality control requested")
        # TODO: Implement quality control dialog

    def _on_send_data(self):
        """Handle send data button click."""
        self.logger.info("Send data requested")
        # TODO: Implement data sending

    def _on_request_status(self):
        """Handle request status button click."""
        self.logger.info("Status request requested")
        # TODO: Implement status request

    # Public methods for controller communication
    def update_project_info(self, project_name: str, location: str, comment: str = ""):
        """
        Update project information display.

        Args:
            project_name: Name of the project
            location: Location information
            comment: Additional comment
        """
        if self.cruise_info_label:
            self.cruise_info_label.setText(f"Project: {project_name}")

        if self.location_info_label:
            self.location_info_label.setText(f"Location: {location}")

        if self.location_comment_value:
            self.location_comment_value.setText(comment)

        self.logger.info("Project info updated: %s, %s", project_name, location)

    def update_data_metrics(self, metrics: Dict[str, Any]):
        """
        Update data metrics display.

        Args:
            metrics: Dictionary containing metric values
        """
        if self.mean_hp_power_value and "mean_hp_power" in metrics:
            self.mean_hp_power_value.setText(str(metrics["mean_hp_power"]))

        if self.max_v_accu_value and "max_v_accu" in metrics:
            self.max_v_accu_value.setText(str(metrics["max_v_accu"]))

        if self.tilt_status_value and "tilt_status" in metrics:
            self.tilt_status_value.setText(str(metrics["tilt_status"]))

        if self.mean_press_value and "mean_press" in metrics:
            self.mean_press_value.setText(str(metrics["mean_press"]))

        self.logger.debug("Data metrics updated")

    def show_data_loaded(self):
        """
        Show that data has been loaded and switch to plot view.
        """
        self.is_data_loaded = True
        self._show_plot_area()
        self.statusbar.showMessage("Data loaded successfully")
        self.logger.info("Data loaded, switched to plot view")

    def show_status_message(self, message: str, timeout: int = 5000):
        """
        Show a status message in the status bar.

        Args:
            message: Message to display
            timeout: Timeout in milliseconds (0 = permanent)
        """
        if self.statusbar:
            self.statusbar.showMessage(message, timeout)
        self.logger.debug("Status message: %s", message)

    def update_plot_data(self, tob_data_model):
        """
        Update the plot widget with new TOB data.
        
        Args:
            tob_data_model: TOB data model containing sensor data
        """
        try:
            if self.plot_widget:
                self.plot_widget.update_data(tob_data_model)
                self.update_style_indicators()  # Update visual indicators
                self.logger.debug("Plot data updated successfully")
            else:
                self.logger.warning("Plot widget not available for data update")
        except Exception as e:
            self.logger.error("Failed to update plot data: %s", e)
            self.error_handler.handle_error(e, self, "Plot Data Update Error")

    def update_plot_sensors(self, selected_sensors: List[str]):
        """
        Update the selected sensors for plotting.
        
        Args:
            selected_sensors: List of selected sensor names
        """
        try:
            if self.plot_widget:
                self.plot_widget.update_sensor_selection(selected_sensors)
                self.update_style_indicators()  # Update visual indicators
                self.logger.debug("Plot sensors updated: %s", selected_sensors)
            else:
                self.logger.warning("Plot widget not available for sensor update")
        except Exception as e:
            self.logger.error("Failed to update plot sensors: %s", e)
            self.error_handler.handle_error(e, self, "Plot Sensor Update Error")

    def update_plot_axis_settings(self, axis_settings: Dict[str, Any]):
        """
        Update axis settings for plotting.
        
        Args:
            axis_settings: Dictionary containing axis configuration
        """
        try:
            if self.plot_widget:
                self.plot_widget.update_axis_settings(axis_settings)
                self.logger.debug("Plot axis settings updated: %s", axis_settings)
            else:
                self.logger.warning("Plot widget not available for axis update")
        except Exception as e:
            self.logger.error("Failed to update plot axis settings: %s", e)
            self.error_handler.handle_error(e, self, "Plot Axis Update Error")

    def get_plot_info(self) -> Dict[str, Any]:
        """
        Get information about the current plot.
        
        Returns:
            Dictionary containing plot information
        """
        try:
            if self.plot_widget:
                return self.plot_widget.get_plot_info()
            else:
                return {'has_plot_widget': False}
        except Exception as e:
            self.logger.error("Failed to get plot info: %s", e)
            return {'error': str(e)}

    def _setup_style_indicators(self):
        """
        Replace UI placeholder labels with visual style indicators for legend functionality.
        """
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QPainter, QPen, QColor
        from PyQt6.QtCore import Qt

        self.style_indicators = {}

        try:
            for sensor_name, checkbox in self.ntc_checkboxes.items():
                # Get style info from plot style service
                style_info = self.plot_style_service.get_sensor_style(sensor_name)

                # Find the corresponding UI placeholder label
                label_name = self._get_style_label_name(sensor_name)
                placeholder_label = self.findChild(QLabel, label_name)

                self.logger.debug(f"Setting up indicator for {sensor_name}: looking for label '{label_name}'")

                if placeholder_label:
                    self.logger.debug(f"Found placeholder label {label_name} with text '{placeholder_label.text()}' at {placeholder_label.geometry()}")

                    # Set up the label as a style indicator using UI service
                    indicator = self.ui_service.setup_label_indicator(placeholder_label, style_info)

                    self.logger.debug(f"Successfully set up {label_name} as style indicator")

                else:
                    self.logger.warning(f"UI placeholder label {label_name} not found for sensor {sensor_name}")
                    # Create hidden fallback
                    indicator = QLabel()
                    indicator.setParent(self)
                    indicator.hide()

                self.style_indicators[sensor_name] = indicator

            self.logger.debug(f"Set up style indicators for {len(self.style_indicators)} sensors")

        except Exception as e:
            self.logger.error(f"Error setting up style indicators: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            ErrorHandler.handle_error(e, "Style Indicator Setup")


    def _get_style_label_name(self, sensor_name: str) -> str:
        """
        Get the UI label name for a sensor.

        Args:
            sensor_name: Sensor name (e.g., 'NTC01', 'Temp')

        Returns:
            UI label name (e.g., 'ntc01_style_label', 'pt100_style_label')
        """
        if sensor_name == "Temp":
            return "pt100_style_label"
        elif sensor_name.startswith("NTC"):
            # Extract number and format as two digits
            number = sensor_name[3:]  # Remove "NTC"
            return f"ntc{number}_style_label"
        else:
            self.logger.warning(f"Unknown sensor name format: {sensor_name}")
            return f"{sensor_name.lower()}_style_label"

    def update_style_indicators(self):
        """
        Update all style indicators when plot styles change.
        """
        if not hasattr(self, 'style_indicators'):
            return

        try:
            for sensor_name, indicator in self.style_indicators.items():
                style_info = self.plot_style_service.get_sensor_style(sensor_name)

                # Update style info and pixmap using UI service
                if hasattr(indicator, '_style_info'):
                    indicator._style_info = style_info
                    self.ui_service.update_label_pixmap(indicator, style_info)

            self.logger.debug("Style indicators updated")

        except Exception as e:
            self.logger.error(f"Error updating style indicators: {e}")
            ErrorHandler.handle_error(e, "Style Indicator Update")

    def display_status_message(self, message: str, timeout: int = 5000):
        """
        Display a status message in the status bar.
        Alias for show_status_message for consistency.

        Args:
            message: Message to display
            timeout: Timeout in milliseconds (0 = permanent)
        """
        self.show_status_message(message, timeout)

    def closeEvent(self, event):
        """
        Handle application close event.

        Args:
            event: Close event
        """
        self.logger.info("Application closing")

        # TODO: Save settings, cleanup resources

        event.accept()
