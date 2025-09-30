"""
Main window view for the WIZARD-2.1 application.

This module contains the main window class that serves as the primary interface
for the temperature data analysis application.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFrame,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
)

# Services are injected by controller - no direct imports needed
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
        dict
    )  # Emitted when project is created (project_data dict)
    project_opened = pyqtSignal(
        str
    )  # Emitted when project is opened (file_path only - app-internal encryption)
    tob_file_status_updated = pyqtSignal(
        str, str
    )  # Emitted when TOB file status changes (file_name, status)

    # Project container signals
    send_data_requested = pyqtSignal(str)  # Emitted when send data button is clicked (file_name)
    quality_control_requested = pyqtSignal()  # Emitted when quality control button is clicked
    status_request_requested = pyqtSignal(str)  # Emitted when request status button is clicked (file_name)

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

        # Services are injected by controller
        self.ui_state_manager = None
        self.ui_service = None
        self.axis_ui_service = None
        self.data_service = None
        self.plot_service = None

        # UI state
        self.current_file_path: Optional[str] = None
        self.current_project_path: Optional[str] = None
        self.is_data_loaded = False

        # Setup UI components (services will be injected later if controller is provided)
        if controller:
            self.set_controller(controller)
        else:
            # Load UI without services
            self._setup_ui()
            self._connect_signals()
            self._setup_menu_bar()
            self._setup_status_bar()

    def set_services(self, services: Dict[str, Any]) -> None:
        """
        Inject services from the controller.

        Args:
            services: Dictionary containing service instances
        """
        self.ui_state_manager = services.get("ui_state_manager")
        self.ui_service = services.get("ui_service")
        self.axis_ui_service = services.get("axis_ui_service")
        self.data_service = services.get("data_service")
        self.plot_service = services.get("plot_service")
        self.plot_style_service = services.get("plot_style_service")

        self.logger.info("Services injected successfully")

        # Setup UI components if not already done
        if not hasattr(self, "welcome_container") or self.welcome_container is None:
            self._setup_ui()
            self._connect_signals()
            self._setup_menu_bar()
            self._setup_status_bar()

        # Setup UI state manager with container references
        # This may be called multiple times - once during UI setup, once after service injection
        if self.ui_state_manager and self.welcome_container and self.plot_container:
            self.ui_state_manager.set_containers(
                self.welcome_container, self.plot_container
            )
            self.logger.info(
                "UI state manager containers set - welcome: %s, plot: %s",
                self.welcome_container is not None,
                self.plot_container is not None,
            )
        elif self.welcome_container and self.plot_container:
            # Containers are available but ui_state_manager not yet injected
            self.logger.debug("UI containers available, waiting for ui_state_manager injection")
        else:
            self.logger.debug("UI containers not yet available")

        # Initialize service-dependent UI components now that services are available
        if self._are_services_available():
            self._initialize_ui_state()
        else:
            self.logger.info(
                "Services not available - UI state initialization deferred"
            )

        self.logger.info("Main window initialized successfully")

    def _are_services_available(self) -> bool:
        """
        Check if all required services are available.

        Returns:
            True if all services are injected, False otherwise
        """
        required_services = [
            self.ui_state_manager,
            self.ui_service,
            self.axis_ui_service,
            self.data_service,
            self.plot_service,
            self.plot_style_service,
        ]
        return all(service is not None for service in required_services)

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

            # UI state and service setup will be done when services are available

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
        self.logger.info(
            "Plot canvas container found: %s", self.plot_canvas_container is not None
        )
        self.logger.info(
            "Plot info container found: %s", self.plot_info_container is not None
        )

        # Bottom container widgets
        self.bottom_container = self.findChild(QFrame, "bottom_container")
        self.data_metrics_frame = self.findChild(QFrame, "data_metrics_frame")
        self.secondary_plot_control_frame = self.findChild(QFrame, "secondary_plot_control_frame")
        self.project_control_frame = self.findChild(QFrame, "project_control_frame")

        # Debug logging for bottom containers
        self.logger.info("Bottom container found: %s", self.bottom_container is not None)
        self.logger.info("Data metrics frame found: %s", self.data_metrics_frame is not None)
        self.logger.info("Secondary plot control frame found: %s", self.secondary_plot_control_frame is not None)
        self.logger.info("Project control frame found: %s", self.project_control_frame is not None)

        # Initialize plot widget (lazy initialization)
        self.plot_widget = None

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

        # plot_style_service is now injected by controller

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

        # Initialize project container editability (disabled by default)
        self.update_project_container_editability()

        # Initialize axis controls
        self._initialize_axis_controls()

        # Initialize plot widget (now that services are available)
        # Note: Plot widget is now initialized lazily when first needed
        # self._initialize_plot_widget()

        # Set default values
        self._reset_data_metrics()
        self._reset_project_info()

        self.logger.debug("UI state initialized")

    def _ensure_plot_widget(self):
        """
        Ensure plot widget is initialized and available.
        """
        if not hasattr(self, "plot_widget") or self.plot_widget is None:
            if (
                hasattr(self, "plot_service")
                and self.plot_service
                and self.plot_canvas_container
            ):
                self.logger.info("Creating plot widget on demand...")
                self._initialize_plot_widget()
            else:
                self.logger.warning(
                    "Cannot create plot widget: services or container not available"
                )
                return False
        return self.plot_widget is not None

    def _initialize_plot_widget(self):
        """
        Initialize the plot widget for data visualization.
        """
        try:
            self.logger.info("Initializing plot widget...")

            if self.plot_canvas_container:
                self.logger.info("Plot canvas container found, creating plot widget")

                # Create plot widget
                self.plot_widget = self.plot_service.create_plot_widget(
                    self.plot_canvas_container
                )
                self.logger.info("Plot widget created successfully")

                # Add plot widget to the container layout
                from PyQt6.QtWidgets import QVBoxLayout

                # Check if container already has a layout
                existing_layout = self.plot_canvas_container.layout()
                if existing_layout:
                    # Clear existing layout properly
                    while existing_layout.count():
                        child = existing_layout.takeAt(0)
                        if child.widget():
                            child.widget().setParent(None)
                    # Remove the layout from the widget
                    self.plot_canvas_container.setLayout(None)
                    # Don't delete the layout immediately to avoid issues
                    existing_layout.setParent(None)

                # Create new layout
                layout = QVBoxLayout()
                layout.addWidget(self.plot_widget)
                layout.setContentsMargins(0, 0, 0, 0)
                self.plot_canvas_container.setLayout(layout)

                # Make sure the plot widget is visible
                self.plot_widget.setVisible(True)
                self.plot_canvas_container.setVisible(True)

                self.logger.info(
                    "Plot widget initialized and made visible successfully"
                )
            else:
                self.logger.warning(
                    "Plot canvas container not found, plot widget not initialized"
                )
        except Exception as e:
            self.logger.error("Failed to initialize plot widget: %s", e)
            self.error_handler.handle_error(e, self, "Plot Widget Initialization Error")

    def _initialize_axis_controls(self):
        """
        Initialize the axis control comboboxes with available options.
        """
        # Use UI service for axis control setup
        self.ui_service.setup_axis_controls(self.axis_combos)

        # Use axis UI service for control initialization
        # Get time range if controller is available
        time_range = None
        if hasattr(self, "controller") and self.controller:
            time_range = self.controller.get_time_range()
        self.axis_ui_service.setup_axis_controls(self, time_range)

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

            # Add permanent TOB file info label to status bar
            from PyQt6.QtWidgets import QLabel
            self.tob_file_status_label = QLabel("No TOB file loaded")
            self.tob_file_status_label.setStyleSheet("font-weight: bold; color: #3AAA35;")
            self.statusbar.addPermanentWidget(self.tob_file_status_label)

    def update_tob_file_status_bar(self, file_name: str = None, data_points: int = None, sensors: int = None):
        """
        Update the TOB file information in the status bar and plot info labels.

        Args:
            file_name: Name of the TOB file (None for no file loaded)
            data_points: Number of data points (optional, for logging only)
            sensors: Number of sensors (optional, for logging only)
        """
        try:
            # Update status bar
            if hasattr(self, 'tob_file_status_label') and self.tob_file_status_label:
                if file_name:
                    status_text = f"TOB: {file_name}"
                else:
                    status_text = "No TOB file loaded"

                self.tob_file_status_label.setText(status_text)

            # Update plot info labels with TOB header data
            self._update_plot_info_from_tob_headers(file_name, data_points, sensors)

            # Log additional info for debugging
            if file_name and data_points is not None and sensors is not None:
                self.logger.debug("TOB file loaded: %s (%d points, %d sensors)",
                                file_name, data_points, sensors)
            else:
                self.logger.debug("TOB file status updated: %s", status_text if 'status_text' in locals() else "No TOB file loaded")

        except Exception as e:
            self.logger.error("Error updating TOB file status: %s", e)

    def _update_plot_info_from_tob_headers(self, file_name: str = None, data_points: int = None, sensors: int = None):
        """
        Update plot info labels (cruise and location) with TOB header data.

        Args:
            file_name: Name of the TOB file
            data_points: Number of data points
            sensors: Number of sensors
        """
        try:
            # Get TOB header data from the currently loaded TOB file
            cruise_value = "-"
            station_value = "-"

            if file_name:
                # Try to get header data from plot widget first (currently displayed)
                tob_data_model = None

                if (hasattr(self, 'plot_widget') and self.plot_widget and
                    hasattr(self.plot_widget, 'tob_data_model') and
                    self.plot_widget.tob_data_model):
                    tob_data_model = self.plot_widget.tob_data_model
                    self.logger.debug("Using header data from plot widget")

                # Fallback to controller data
                elif self.controller and self.controller.tob_data_model:
                    tob_data_model = self.controller.tob_data_model
                    self.logger.debug("Using header data from controller")

                # Extract header values
                if tob_data_model and tob_data_model.headers:
                    cruise_value = tob_data_model.headers.get('Cruise', '-')
                    station_value = tob_data_model.headers.get('Station', '-')

                    # Handle different data types (some headers might be lists)
                    if isinstance(cruise_value, list):
                        cruise_value = cruise_value[0] if cruise_value else '-'
                    if isinstance(station_value, list):
                        station_value = station_value[0] if station_value else '-'

            # Update the labels
            if self.cruise_info_label:
                self.cruise_info_label.setText(f"Cruise: {cruise_value}")

            if self.location_info_label:
                self.location_info_label.setText(f"Station: {station_value}")

            self.logger.debug("Plot info labels updated - Cruise: %s, Station: %s",
                            cruise_value, station_value)

        except Exception as e:
            self.logger.error("Error updating plot info from TOB headers: %s", e)

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

        if self.info_action:
            self.info_action.triggered.connect(self._on_show_header_info)

        if self.exit_action:
            self.exit_action.triggered.connect(self.close)

        if self.actionCreate_Project_File:
            self.actionCreate_Project_File.triggered.connect(self._on_create_project)

        if self.actionOpen_Project_File:
            self.actionOpen_Project_File.triggered.connect(self._on_open_project)

        if self.actionEdit_Project_Settings:
            self.actionEdit_Project_Settings.triggered.connect(
                self._on_edit_project_settings
            )

        if self.actionShow_Processing_List:
            self.actionShow_Processing_List.triggered.connect(
                self._on_show_processing_list
            )

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

        # Axis combo box changes - only connect if controller is available
        if self.controller:
            self._connect_axis_signals()

    def _connect_axis_signals(self):
        """
        Connect axis control signals that require controller.
        """
        if hasattr(self, "y1_axis_combo") and self.y1_axis_combo:
            self.y1_axis_combo.currentTextChanged.connect(self._on_y1_axis_changed)

        if hasattr(self, "y2_axis_combo") and self.y2_axis_combo:
            self.y2_axis_combo.currentTextChanged.connect(self._on_y2_axis_changed)

        if hasattr(self, "x_axis_combo") and self.x_axis_combo:
            self.x_axis_combo.currentTextChanged.connect(self._on_x_axis_changed)

        # Connect manual axis value changes
        if hasattr(self, "x_min_value") and self.x_min_value:
            self.x_min_value.textChanged.connect(self._on_x_axis_limits_changed)
        if hasattr(self, "x_max_value") and self.x_max_value:
            self.x_max_value.textChanged.connect(self._on_x_axis_limits_changed)

        if hasattr(self, "y1_min_value") and self.y1_min_value:
            self.y1_min_value.textChanged.connect(self._on_y1_axis_limits_changed)
        if hasattr(self, "y1_max_value") and self.y1_max_value:
            self.y1_max_value.textChanged.connect(self._on_y1_axis_limits_changed)

        if hasattr(self, "y2_min_value") and self.y2_min_value:
            self.y2_min_value.textChanged.connect(self._on_y2_axis_limits_changed)
        if hasattr(self, "y2_max_value") and self.y2_max_value:
            self.y2_max_value.textChanged.connect(self._on_y2_axis_limits_changed)

        self.logger.debug("Axis control signals connected")

    def set_controller(self, controller):
        """
        Set the controller and connect dependent signals.

        Args:
            controller: The main controller instance
        """
        self.controller = controller
        # Connect axis signals now that controller is available
        self._connect_axis_signals()

        # Update project container editability now that controller is available
        self.update_project_container_editability()

        self.logger.debug("Controller set and axis signals connected")

        # Connect GUI operation signals (thread-safe)
        self.controller.show_upload_success.connect(self._on_show_upload_success)
        self.controller.show_server_status.connect(self._on_show_server_status)

        # Connect error handler signals (thread-safe)
        self.error_handler.error_occurred.connect(self._on_error_occurred)
        self.error_handler.warning_occurred.connect(self._on_warning_occurred)
        self.error_handler.info_message.connect(self._on_info_message)

        # Initialize UI state now that services are available
        self._initialize_ui_state()

        # Action buttons
        if self.quality_control_button:
            self.quality_control_button.clicked.connect(self._on_quality_control)

        if self.send_data_button:
            self.send_data_button.clicked.connect(self._on_send_data)

        if self.request_status_button:
            self.request_status_button.clicked.connect(self._on_request_status)

        # Project container widget changes
        if self.location_comment_value:
            self.location_comment_value.editingFinished.connect(self._on_location_comment_changed)

        if self.location_sensorstring_value:
            self.location_sensorstring_value.editingFinished.connect(self._on_location_sensorstring_changed)

        if self.location_subcon_spin:
            self.location_subcon_spin.valueChanged.connect(self._on_location_subcon_changed)

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
        if self.ui_state_manager:
            self.ui_state_manager.show_plot_mode()
        self.logger.debug("Plot area displayed")

    def get_metrics_widgets(self) -> Dict[str, "QLineEdit"]:
        """
        Get dictionary of metrics widget references.

        Returns:
            Dictionary mapping metric names to widget references
        """
        return {
            "mean_hp_power_value": self.mean_hp_power_value,
            "max_v_accu_value": self.max_v_accu_value,
            "tilt_status_value": self.tilt_status_value,
            "mean_press_value": self.mean_press_value,
        }

    def _reset_data_metrics(self):
        """
        Reset data metrics to default values.
        """
        # Use data service for metrics reset
        metrics_widgets = self.get_metrics_widgets()
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

        # Also reset project container widgets
        self.update_project_container(None)
        self.update_project_container_editability()

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

    def _on_show_header_info(self):
        """
        Handle showing TOB file header information.
        """
        try:
            # Get TOB data from plot widget first (currently displayed data),
            # fallback to controller data (last loaded file)
            tob_data_model = None

            # Check plot widget first (currently displayed TOB file)
            if (hasattr(self, 'plot_widget') and self.plot_widget and
                hasattr(self.plot_widget, 'tob_data_model') and
                self.plot_widget.tob_data_model):
                tob_data_model = self.plot_widget.tob_data_model
                self.logger.debug("Using TOB data from plot widget (currently displayed)")

            # Fallback to controller data (last loaded file)
            elif self.controller and self.controller.tob_data_model:
                tob_data_model = self.controller.tob_data_model
                self.logger.debug("Using TOB data from controller (last loaded)")

            # No data available
            if not tob_data_model:
                self.show_error_dialog(
                    "No TOB Data",
                    "Please load a TOB file first before viewing header information.",
                )
                return

            # Import and create header info dialog
            from .dialogs.header_info_dialog import HeaderInfoDialog

            dialog = HeaderInfoDialog(tob_data_model, self)
            dialog.exec()

            self.logger.info("Header info dialog displayed for file: %s",
                           tob_data_model.file_name or "Unknown")

        except ImportError as e:
            self.logger.error("Failed to import HeaderInfoDialog: %s", e)
            self.show_error_dialog(
                "Import Error", f"Could not load header info dialog: {e}"
            )
        except Exception as e:
            self.logger.error("Error showing header info: %s", e)
            self.error_handler.handle_error(e, self, "Header Info Display Error")

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
                self.logger.info("Opening project file: %s", file_path)
                self.project_opened.emit(file_path)
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
            # First show project creation dialog to get project details
            from .dialogs.project_dialogs import ProjectDialog

            project_dialog = ProjectDialog(parent=self)

            if project_dialog.exec() == ProjectDialog.DialogCode.Accepted:
                # Get project data from dialog
                name, enter_key, server_url, description = (
                    project_dialog.get_project_data()
                )

                # Now get file path for saving
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Create Project File",
                    f"{name}.wzp",  # Suggest filename based on project name
                    "WIZARD Project Files (*.wzp);;All Files (*)",
                )

                if file_path:
                    # Ensure .wzp extension
                    if not file_path.lower().endswith(".wzp"):
                        file_path += ".wzp"

                    # Prepare project data dictionary
                    project_data = {
                        "name": name,
                        "enter_key": enter_key,
                        "server_url": server_url,
                        "description": description,
                        "file_path": file_path,
                    }

                    self.logger.info("Creating project: %s at %s", name, file_path)
                    self.project_created.emit(project_data)

        except (OSError, PermissionError) as e:
            self.logger.error("File system error creating project: %s", e)
            self.error_handler.handle_error(e, self, "Project Creation File Error")
        except Exception as e:
            self.logger.error("Unexpected error creating project: %s", e)
            self.error_handler.handle_error(e, self, "Project Creation Error")

    def _on_edit_project_settings(self):
        """
        Handle editing project settings.
        """
        try:
            # Check if a project is currently loaded
            if (
                not self.current_project_path
                or not hasattr(self.controller, "project_model")
                or not self.controller.project_model
            ):
                self.error_handler.handle_error(
                    ValueError(
                        "No project is currently loaded. Please create or open a project first."
                    ),
                    "No Project Loaded",
                    self,
                )
                return

            # Get current project data
            project = self.controller.project_model
            current_name = project.name
            current_enter_key = (
                project.server_config.bearer_token if project.server_config else ""
            )
            current_server_url = (
                project.server_config.url if project.server_config else ""
            )
            current_description = project.description or ""

            # Open project dialog in edit mode
            from .dialogs.project_dialogs import ProjectDialog

            edit_dialog = ProjectDialog(
                parent=self,
                project_name=current_name,
                project_description=current_description,
                enter_key=current_enter_key,
                server_url=current_server_url,
            )
            edit_dialog.setWindowTitle("Edit Project Settings")

            if edit_dialog.exec() == ProjectDialog.DialogCode.Accepted:
                # Get updated data from dialog
                name, enter_key, server_url, description = (
                    edit_dialog.get_project_data()
                )

                # Send update request to controller
                self.controller.update_project_settings(
                    {
                        "name": name,
                        "enter_key": enter_key,
                        "server_url": server_url,
                        "description": description,
                    }
                )

                self.logger.info("Project settings updated successfully")

        except Exception as e:
            self.logger.error("Unexpected error editing project settings: %s", e)
            self.error_handler.handle_error(e, self, "Project Settings Edit Error")

    def _on_show_processing_list(self):
        """
        Show the processing list dialog for managing TOB files.
        """
        try:
            # Check if a project is loaded
            if not self.controller or not self.controller.project_model:
                self.error_handler.handle_error(
                    ValueError(
                        "No project is currently loaded. Please create or open a project first."
                    ),
                    "No Project Loaded",
                    self,
                )
                return

            # Import and create dialog
            from .dialogs.processing_list_dialog import ProcessingListDialog

            dialog = ProcessingListDialog(
                parent=self, project_model=self.controller.project_model
            )

            # Connect signals
            dialog.file_selected.connect(self._on_tob_file_selected_for_plot)
            dialog.file_added.connect(self._on_tob_file_added)
            dialog.file_removed.connect(self._on_tob_file_removed)
            dialog.status_updated.connect(self._on_tob_file_status_updated)

            # Show dialog
            dialog.exec()

        except Exception as e:
            self.logger.error("Unexpected error showing processing list: %s", e)
            self.error_handler.handle_error(e, self, "Processing List Error")

    def _on_tob_file_selected_for_plot(self, file_name: str):
        """
        Handle TOB file selection for plotting.

        Args:
            file_name: Name of the selected TOB file
        """
        try:
            self.logger.info(f"Attempting to plot TOB file: {file_name}")

            if not self.controller or not self.controller.project_model:
                self.logger.error("No project controller available")
                self.error_handler.handle_error(
                    ValueError("No project controller available"), "Project Error", self
                )
                return

            # Get TOB file data
            tob_file = self.controller.project_model.get_tob_file(file_name)
            if not tob_file:
                self.logger.error(f"TOB file '{file_name}' not found in project")
                self.error_handler.handle_error(
                    ValueError(f"TOB file '{file_name}' not found in project"),
                    "File Not Found",
                    self,
                )
                return

            self.logger.info(f"Found TOB file: {tob_file.file_name}")
            self.logger.info(f"TOB data exists: {tob_file.tob_data is not None}")

            if tob_file.tob_data:
                self.logger.info(
                    f"DataFrame exists: {tob_file.tob_data.data is not None}"
                )
                if tob_file.tob_data.data is not None:
                    self.logger.info(f"DataFrame shape: {tob_file.tob_data.data.shape}")
                    self.logger.info(f"DataFrame empty: {tob_file.tob_data.data.empty}")

            if (
                not tob_file.tob_data
                or tob_file.tob_data.data is None
                or tob_file.tob_data.data.empty
            ):
                self.logger.error(f"TOB file '{file_name}' has no data to plot")
                self.error_handler.handle_error(
                    ValueError(f"TOB file '{file_name}' has no data to plot"),
                    "No Plot Data",
                    self,
                )
                return

            # Ensure plot widget is available
            if not self._ensure_plot_widget():
                self.error_handler.handle_error(
                    ValueError("Plot widget is not available"),
                    "Plot System Error",
                    self,
                )
                return

            # Create TOBDataModel from project data
            from ..models.tob_data_model import TOBDataModel

            tob_data_model = TOBDataModel(
                headers=tob_file.tob_data.headers or {},
                data=tob_file.tob_data.data,
                file_path=tob_file.file_path,
                file_name=tob_file.file_name,
            )

            # Check memory usage before loading
            memory_mb = tob_file.tob_data.data.memory_usage(deep=True).sum() / (
                1024 * 1024
            )
            if memory_mb > 500:  # Warn if over 500MB
                # For now, just show a warning but continue loading
                # TODO: Implement proper user confirmation dialog via signals
                self.logger.warning(f"Loading large dataset: {memory_mb:.1f}MB")
                # Continue with loading for now

            # Update plot widget with TOB data
            self.plot_widget.update_data(tob_data_model)

            # Inform controller about the newly active TOB data
            if hasattr(self.controller, "set_current_tob_data"):
                self.controller.set_current_tob_data(tob_data_model)

            # Set as active TOB file
            self.controller.project_model.set_active_tob_file(file_name)

            # Update project container status after changing active file
            if hasattr(self, "update_project_container_status"):
                self.update_project_container_status()

            # Calculate and update data metrics
            if self.controller and hasattr(self.controller, "data_service"):
                try:
                    metrics = self.controller.data_service._calculate_metrics(
                        tob_data_model
                    )
                    self.logger.info("TOB metrics calculated for manual plotting")

                            # Update data metrics in view
                    self.controller.data_service.update_data_metrics(
                        self.get_metrics_widgets(), metrics
                    )
                except Exception as e:
                    self.logger.error(
                        "Failed to calculate data metrics for manual plotting: %s", e
                    )

            # Update status bar with TOB file information
            if hasattr(self, 'update_tob_file_status_bar'):
                file_name = tob_data_model.file_name or "Unknown"
                data_points = tob_data_model.data_points or 0
                sensors_count = len(tob_data_model.sensors) if tob_data_model.sensors else 0
                self.update_tob_file_status_bar(file_name, data_points, sensors_count)

            # Update UI elements
            self._update_ui_for_tob_plot(tob_file)

            # Update project container with TOB header data
            if hasattr(self, "update_project_container"):
                self.update_project_container(tob_data_model)

            # Show status message
            sensor_count = len(tob_file.sensors) if tob_file.sensors else 0
            data_points = (
                len(tob_file.tob_data.data) if tob_file.tob_data.data is not None else 0
            )

            self.show_status_message(
                f"Loaded '{file_name}' for plotting: {data_points} data points, {sensor_count} sensors"
            )

            self.logger.info(
                f"Successfully loaded TOB file '{file_name}' for plotting: "
                f"{data_points} points, {sensor_count} sensors"
            )

        except Exception as e:
            self.logger.error(f"Error selecting TOB file for plot: {e}")
            self.error_handler.handle_error(e, self, "TOB File Selection Error")

    def _update_ui_for_tob_plot(self, tob_file):
        """
        Update UI elements when a TOB file is loaded for plotting.

        Args:
            tob_file: TOBFileInfo object
        """
        try:
            # Update sensor checkboxes - select only available NTC sensors
            # Clear current selections
            for checkbox in self.ntc_checkboxes.values():
                checkbox.setChecked(False)

            # Select only sensors that are actually available in the TOB file
            selected_ntc_sensors = []
            available_sensors = tob_file.sensors or []

            for sensor_name, checkbox in self.ntc_checkboxes.items():
                if sensor_name in available_sensors and (
                    sensor_name.startswith("NTC") or sensor_name == "Temp"
                ):
                    checkbox.setChecked(True)
                    selected_ntc_sensors.append(sensor_name)

            # Update plot widget with active NTC sensors
            if hasattr(self, "plot_widget") and self.plot_widget:
                self.plot_widget.set_active_ntc_sensors(selected_ntc_sensors)

                # If we have multiple NTC sensors selected, switch to NTCs mode for plotting
                if len(selected_ntc_sensors) > 1:
                    # Set y1 sensor to "NTCs" to plot all selected NTC sensors
                    if hasattr(self.plot_widget, "y1_sensor"):
                        self.plot_widget.y1_sensor = "NTCs"
                        self.logger.debug(
                            "Switched to NTCs mode for multi-sensor plotting"
                        )

                    # Also update the y1 axis combo box if it exists
                    if hasattr(self, "y1_axis_combo") and self.y1_axis_combo:
                        self.y1_axis_combo.setCurrentText("NTCs")
                        self.logger.debug("Updated y1 axis combo to NTCs")

            self.logger.debug(
                f"Selected all NTC sensors for '{tob_file.file_name}': {selected_ntc_sensors}"
            )

            # Update X axis limits based on current time unit
            current_time_unit = "Seconds"  # Default
            if hasattr(self, "x_axis_combo") and self.x_axis_combo:
                current_time_unit = self.x_axis_combo.currentText() or "Seconds"
            self._update_x_axis_limits_for_unit(current_time_unit)

            # Update project info display
            if self.controller.project_model:
                location = (
                    self.controller.project_model.server_config.url
                    if self.controller.project_model.server_config
                    else ""
                )
                self.update_project_info(
                    self.controller.project_model.name,
                    location,
                    self.controller.project_model.description,
                )

        except Exception as e:
            self.logger.error(f"Error updating UI for TOB plot: {e}")

    def clear_plot_data(self):
        """
        Clear all data from the plot widget.
        """
        try:
            if hasattr(self, "plot_widget") and self.plot_widget:
                # Clear sensor selections
                for checkbox in self.ntc_checkboxes.values():
                    checkbox.setChecked(False)

                # Clear plot data (if the plot widget supports it)
                if hasattr(self.plot_widget, "clear_plot"):
                    self.plot_widget.clear_plot()
                elif hasattr(self.plot_widget, "_clear_plot"):
                    self.plot_widget._clear_plot()

                # Reset TOB file status in status bar
                if hasattr(self, 'update_tob_file_status_bar'):
                    self.update_tob_file_status_bar()

                self.show_status_message("Plot data cleared")
                self.logger.info("Plot data cleared")

        except Exception as e:
            self.logger.error(f"Error clearing plot data: {e}")
            self.error_handler.handle_error(e, self, "Clear Plot Error")

    def _on_tob_file_added(self, file_path: str):
        """
        Handle TOB file addition notification.

        Args:
            file_path: Path of the added file
        """
        file_name = Path(file_path).name
        self.logger.info(f"TOB file added: {file_name}")

    def _on_tob_file_removed(self, file_name: str):
        """
        Handle TOB file removal notification.

        Args:
            file_name: Name of the removed file
        """
        self.logger.info(f"TOB file removed: {file_name}")

    def _on_tob_file_status_updated(self, file_name: str, status: str):
        """
        Handle TOB file status update notification.

        Args:
            file_name: Name of the file
            status: New status
        """
        self.logger.info(f"TOB file status updated: {file_name} -> {status}")

        # Update status bar message
        status_messages = {
            "loaded": f"'{file_name}' loaded successfully",
            "uploading": f"Uploading '{file_name}'...",
            "uploaded": f"'{file_name}' uploaded to server",
            "processing": f"Processing '{file_name}' on server...",
            "processed": f"'{file_name}' processing completed",
            "error": f"Error with '{file_name}'",
        }

        message = status_messages.get(
            status, f"Status of '{file_name}' changed to {status}"
        )
        self.show_status_message(message)

    def update_tob_file_status(self, file_name: str, status: str) -> None:
        """
        Update the status of a TOB file across all open dialogs.

        Args:
            file_name: Name of the TOB file
            status: New status
        """
        # This method can be called by external components (like server communication)
        # to update TOB file status throughout the application

        if self.controller and self.controller.project_model:
            self.controller.project_model.update_tob_file_status(file_name, status)
            self.logger.info(
                f"TOB file status updated externally: {file_name} -> {status}"
            )

            # Trigger auto-save
            self.controller._mark_project_modified()

            # Emit signal for any open dialogs
            self.tob_file_status_updated.emit(file_name, status)

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
        self.logger.debug(
            "View: sensor %s selection changed: %s", sensor_name, is_selected
        )

        # MVC: View informs Controller about UI event
        # Controller handles the logic and updates views
        if self.controller:
            self.controller.handle_sensor_selection_changed(sensor_name, is_selected)

    def _on_y1_auto_changed(self, state: int):
        """Handle Y1 axis auto mode change."""
        is_auto = state == 2
        self.logger.debug("Y1 axis auto mode: %s", is_auto)

        # Delegate to axis UI service for consistent handling
        if hasattr(self, "axis_ui_service") and self.axis_ui_service:
            self.axis_ui_service.handle_axis_auto_mode_changed(self, "y1", is_auto)
        else:
            # Fallback: Enable/disable manual controls directly
            if self.y1_min_value and self.y1_max_value:
                self.y1_min_value.setEnabled(not is_auto)
                self.y1_max_value.setEnabled(not is_auto)

    def _on_y2_auto_changed(self, state: int):
        """Handle Y2 axis auto mode change."""
        is_auto = state == 2
        self.logger.debug("Y2 axis auto mode: %s", is_auto)

        # Delegate to axis UI service for consistent handling
        if hasattr(self, "axis_ui_service") and self.axis_ui_service:
            self.axis_ui_service.handle_axis_auto_mode_changed(self, "y2", is_auto)
        else:
            # Fallback: Enable/disable manual controls directly
            if self.y2_min_value and self.y2_max_value:
                self.y2_min_value.setEnabled(not is_auto)
                self.y2_max_value.setEnabled(not is_auto)

    def _on_x_auto_changed(self, state: int):
        """Handle X axis auto mode change."""
        is_auto = state == 2
        self.logger.debug("X axis auto mode: %s", is_auto)

        # Use axis UI service to handle the mode change
        self.axis_ui_service.handle_axis_auto_mode_changed(self, "x", is_auto)

    def _update_axis_limits_for_sensor(self, sensor_name: str, axis: str):
        """
        Update min/max values for the specified axis based on the selected sensor.

        Args:
            sensor_name: Name of the selected sensor
            axis: "y1" or "y2"
        """
        try:
            data = None

            # Try to get TOB data from current project first
            if (
                self.controller
                and self.controller.project_model
                and self.controller.project_model.active_tob_file
            ):

                active_tob = self.controller.project_model.get_active_tob_file()
                if (
                    active_tob
                    and active_tob.tob_data
                    and active_tob.tob_data.data is not None
                ):
                    data = active_tob.tob_data.data

            # If no project data, try to get data from plot widget (direct TOB loading)
            elif (
                hasattr(self, "plot_widget")
                and self.plot_widget
                and hasattr(self.plot_widget, "tob_data_model")
                and self.plot_widget.tob_data_model
                and self.plot_widget.tob_data_model.data is not None
            ):
                data = self.plot_widget.tob_data_model.data

            # If we have data, calculate min/max values
            if data is not None:
                # Check if sensor exists in data
                if sensor_name in data.columns:
                    sensor_data = data[sensor_name].dropna()
                    if not sensor_data.empty:
                        min_val = float(sensor_data.min())
                        max_val = float(sensor_data.max())

                        # Set values in UI fields
                        if axis == "y1":
                            if self.y1_min_value:
                                self.y1_min_value.blockSignals(True)
                                self.y1_min_value.setText(f"{min_val:.2f}")
                                self.y1_min_value.blockSignals(False)
                            if self.y1_max_value:
                                self.y1_max_value.blockSignals(True)
                                self.y1_max_value.setText(f"{max_val:.2f}")
                                self.y1_max_value.blockSignals(False)
                        elif axis == "y2":
                            if self.y2_min_value:
                                self.y2_min_value.blockSignals(True)
                                self.y2_min_value.setText(f"{min_val:.2f}")
                                self.y2_min_value.blockSignals(False)
                            if self.y2_max_value:
                                self.y2_max_value.blockSignals(True)
                                self.y2_max_value.setText(f"{max_val:.2f}")
                                self.y2_max_value.blockSignals(False)

                        self.logger.debug(
                            f"Updated {axis} limits for {sensor_name}: {min_val:.2f} - {max_val:.2f}"
                        )
                    else:
                        self.logger.warning(
                            f"No data available for sensor {sensor_name}"
                        )
                else:
                    self.logger.warning(f"Sensor {sensor_name} not found in data")
            else:
                self.logger.debug("No TOB data available for limit calculation")

        except Exception as e:
            self.logger.error(
                f"Error updating {axis} limits for sensor {sensor_name}: {e}"
            )

    def _update_x_axis_limits_for_unit(self, time_unit: str):
        """
        Update X axis min/max values based on TOB data and selected time unit.

        Args:
            time_unit: Time unit ("Seconds", "Minutes", "Hours")
        """
        try:
            data = None

            # Get TOB data from current project or plot widget
            if (
                self.controller
                and self.controller.project_model
                and self.controller.project_model.active_tob_file
            ):

                active_tob = self.controller.project_model.get_active_tob_file()
                if (
                    active_tob
                    and active_tob.tob_data
                    and active_tob.tob_data.data is not None
                ):
                    data = active_tob.tob_data.data

            elif (
                hasattr(self, "plot_widget")
                and self.plot_widget
                and hasattr(self.plot_widget, "tob_data_model")
                and self.plot_widget.tob_data_model
                and self.plot_widget.tob_data_model.data is not None
            ):
                data = self.plot_widget.tob_data_model.data

            if data is not None:
                # Get time column (use same logic as TOBDataModel)
                time_col = None
                time_columns = ["Time", "time", "TIMESTAMP", "timestamp", "Datasets"]
                for col in time_columns:
                    if col in data.columns:
                        time_col = data[col]
                        break

                if time_col is not None and not time_col.empty:
                    time_min = float(time_col.min())
                    time_max = float(time_col.max())

                    # Convert to selected time unit
                    if time_unit == "Minutes":
                        time_min = time_min / 60.0
                        time_max = time_max / 60.0
                    elif time_unit == "Hours":
                        time_min = time_min / 3600.0
                        time_max = time_max / 3600.0
                    # For "Seconds", keep as is

                    # Set values in UI fields
                    if self.x_min_value:
                        self.x_min_value.blockSignals(True)
                        self.x_min_value.setText(f"{time_min:.2f}")
                        self.x_min_value.blockSignals(False)
                    if self.x_max_value:
                        self.x_max_value.blockSignals(True)
                        self.x_max_value.setText(f"{time_max:.2f}")
                        self.x_max_value.blockSignals(False)

                    self.logger.debug(
                        f"Updated X axis limits for {time_unit}: {time_min:.2f} - {time_max:.2f}"
                    )
                else:
                    self.logger.warning("No time column found in TOB data")
            else:
                self.logger.debug("No TOB data available for X axis limit calculation")

        except Exception as e:
            self.logger.error(f"Error updating X axis limits for unit {time_unit}: {e}")

    def _on_y1_axis_changed(self, sensor_name: str):
        """Handle Y1 axis sensor selection - sets primary sensor for main plot."""
        if sensor_name:
            self.logger.debug("Y1 axis changed to: %s", sensor_name)
            # Update primary sensor through controller
            if self.controller:
                self.controller.set_primary_sensor(sensor_name)

            # Update Y1 min/max values based on selected sensor
            self._update_axis_limits_for_sensor(sensor_name, "y1")

    def _on_y2_axis_changed(self, sensor_name: str):
        """Handle Y2 axis selection - controls plot layout mode."""
        if sensor_name == "None":
            # Single mode: Only main plot
            self.logger.debug("Switching to single plot mode")
            if self.controller:
                self.controller.set_plot_mode("single")
        else:
            # Dual mode: Main plot + secondary plot with selected sensor
            self.logger.debug(
                "Switching to dual plot mode with sensor: %s", sensor_name
            )
            if self.controller:
                self.controller.set_secondary_sensor(sensor_name)

            # Update Y2 min/max values based on selected sensor
            self._update_axis_limits_for_sensor(sensor_name, "y2")

    def _on_x_axis_changed(self, axis_type: str):
        """Handle X axis type selection change."""
        if axis_type:
            self.logger.debug("X axis changed to: %s", axis_type)

            # Update X axis limits based on TOB data
            self._update_x_axis_limits_for_unit(axis_type)

            # If in manual mode, convert existing manual limits to new time unit
            if (
                hasattr(self, "x_auto_checkbox")
                and self.x_auto_checkbox
                and not self.x_auto_checkbox.isChecked()
                and hasattr(self, "x_min_value")
                and self.x_min_value
                and hasattr(self, "x_max_value")
                and self.x_max_value
            ):

                # Get current values and convert them to the new unit
                try:
                    current_min = float(self.x_min_value.text() or "0")
                    current_max = float(self.x_max_value.text() or "0")

                    # Get old time unit for conversion
                    old_unit = "Seconds"  # Default
                    if hasattr(self, "x_axis_combo") and self.x_axis_combo:
                        current_text = self.x_axis_combo.currentText()
                        if current_text and current_text != axis_type:
                            old_unit = current_text

                    # Convert from old unit to seconds, then to new unit
                    if old_unit == "Minutes":
                        current_min *= 60.0
                        current_max *= 60.0
                    elif old_unit == "Hours":
                        current_min *= 3600.0
                        current_max *= 3600.0

                    # Convert to new unit
                    if axis_type == "Minutes":
                        current_min /= 60.0
                        current_max /= 60.0
                    elif axis_type == "Hours":
                        current_min /= 3600.0
                        current_max /= 3600.0

                    # Update the values in LineEdits
                    self.x_min_value.blockSignals(True)
                    self.x_max_value.blockSignals(True)
                    self.x_min_value.setText(f"{current_min:.2f}")
                    self.x_max_value.setText(f"{current_max:.2f}")
                    self.x_min_value.blockSignals(False)
                    self.x_max_value.blockSignals(False)

                except ValueError:
                    pass  # Keep existing values if conversion fails

            # Update axis settings through controller
            axis_settings = {"x_axis_type": axis_type}
            if self.controller:
                self.controller.update_axis_settings(axis_settings)

                # If in auto mode, update values to show current range in new unit
                if (
                    hasattr(self, "x_auto_checkbox")
                    and self.x_auto_checkbox
                    and self.x_auto_checkbox.isChecked()
                ):
                    time_range = self.controller.get_time_range()
                    if time_range:
                        self.axis_ui_service.update_axis_values(self, time_range)
                elif (
                    hasattr(self, "x_auto_checkbox")
                    and self.x_auto_checkbox
                    and not self.x_auto_checkbox.isChecked()
                ):
                    # In manual mode, update the displayed values from current plot limits
                    self.axis_ui_service._update_manual_values_from_plot(self)

    def _on_quality_control(self):
        """Handle quality control button click."""
        self.logger.info("Quality control requested")
        self.quality_control_requested.emit()

    def _on_send_data(self):
        """Handle send data button click."""
        self.logger.info("Send data requested")
        # Get the current active TOB file name from controller
        if self.controller and hasattr(self.controller, 'get_current_tob_data'):
            tob_data = self.controller.get_current_tob_data()
            if tob_data and tob_data.file_name:
                self.send_data_requested.emit(tob_data.file_name)
            else:
                self.logger.warning("No active TOB file available for sending")
        else:
            self.logger.warning("No controller available for send data operation")

    def _on_request_status(self):
        """Handle request status button click."""
        self.logger.info("Status request requested")
        # Get the current active TOB file name from controller
        if self.controller and hasattr(self.controller, 'get_current_tob_data'):
            tob_data = self.controller.get_current_tob_data()
            if tob_data and tob_data.file_name:
                self.status_request_requested.emit(tob_data.file_name)
            else:
                self.logger.warning("No active TOB file available for status request")
        else:
            self.logger.warning("No controller available for status request operation")

    # Public methods for controller communication
    def update_project_info(self, project_name: str, location: str, comment: str = ""):
        """
        Update project information display.

        Note: The cruise_info_label and location_info_label are now used for TOB header data.
        This method is kept for backward compatibility but no longer updates those labels.

        Args:
            project_name: Name of the project
            location: Location information
            comment: Additional comment
        """
        # The cruise_info_label and location_info_label are now used for TOB header data
        # They are automatically updated when TOB files are loaded

        if self.location_comment_value:
            self.location_comment_value.setText(comment)

        self.logger.info("Project info updated: %s, %s (labels now show TOB header data)",
                        project_name, location)

    def update_project_container(self, tob_data_model=None):
        """
        Update project container widgets with TOB header data.

        Args:
            tob_data_model: TOBDataModel instance with header information
        """
        try:
            if not tob_data_model or not tob_data_model.headers:
                # Reset to default values
                if self.location_subcon_spin:
                    self.location_subcon_spin.setValue(0.0)
                if self.location_comment_value:
                    self.location_comment_value.setText("-")
                if self.location_sensorstring_value:
                    self.location_sensorstring_value.setText("-")
                return

            headers = tob_data_model.headers

            # Update Subcon Extension (Subconn_Length from project settings or header)
            subcon_value = 0.0
            if "Subconn_Length" in headers:
                try:
                    subcon_value = float(headers["Subconn_Length"])
                except (ValueError, TypeError):
                    subcon_value = 0.0

            if self.location_subcon_spin:
                self.location_subcon_spin.setValue(subcon_value)

            # Update Comment (filter out brackets and quotes)
            comment = headers.get("Comments", "-")
            if comment != "-":
                # Remove brackets and quotes
                comment = re.sub(r'[\[\]\'""]', '', str(comment))
            if self.location_comment_value:
                self.location_comment_value.setText(comment)

            # Update Sensor String (FLX- + string from comment starting with T, ending with SD)
            sensor_string = "-"
            if headers.get("Comments"):
                comment = str(headers["Comments"])
                # Find pattern: T followed by numbers, ending with SD
                match = re.search(r'T(\d+)SD', comment)
                if match:
                    sensor_number = match.group(1)
                    sensor_string = f"FLX-T{sensor_number}SD"

            if self.location_sensorstring_value:
                self.location_sensorstring_value.setText(sensor_string)

            # Update Status
            self.update_project_container_status()

            self.logger.info("Project container updated with TOB header data")

        except Exception as e:
            self.logger.error("Error updating project container: %s", e)

    def update_project_container_editability(self):
        """
        Update the editability of project container widgets based on whether a project is loaded.
        """
        try:
            controller = getattr(self, "controller", None)
            has_real_project = False

            if controller is not None:
                project_model = getattr(controller, "project_model", None)
                main_window_ref = getattr(controller, "main_window", None)
                current_project_path = None
                if main_window_ref is not None:
                    current_project_path = getattr(
                        main_window_ref, "current_project_path", None
                    )

                has_real_project = bool(
                    project_model
                    and current_project_path is not None
                    and current_project_path != ""
                )

            # Enable/disable project container input widgets
            if self.location_subcon_spin is not None:
                self.location_subcon_spin.setEnabled(has_real_project)

            if self.location_comment_value is not None:
                self.location_comment_value.setReadOnly(not has_real_project)

            if self.location_sensorstring_value is not None:
                self.location_sensorstring_value.setReadOnly(not has_real_project)

            # Enable/disable project container buttons
            if self.send_data_button is not None:
                self.send_data_button.setEnabled(has_real_project)

            if self.quality_control_button is not None:
                self.quality_control_button.setEnabled(has_real_project)

            if self.request_status_button is not None:
                self.request_status_button.setEnabled(has_real_project)

            self.logger.debug("Project container editability updated: real_project_loaded=%s", has_real_project)

        except Exception as e:
            print(f"DEBUG: Error in update_project_container_editability: {e}")
            self.logger.error("Error updating project container editability: %s", e)

    def _update_processing_list_dialogs(self):
        """Try to update any open processing list dialogs."""
        try:
            # Find all ProcessingListDialog instances
            # This is a simple approach - we look for widgets of the correct type
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                for widget in app.allWidgets():
                    if hasattr(widget, '_populate_table') and hasattr(widget, 'project_model'):
                        # This looks like a ProcessingListDialog
                        if widget.project_model == self.controller.project_model:
                            # Same project model, update it
                            widget._populate_table()
                            self.logger.debug("Updated processing list dialog")
        except Exception as e:
            self.logger.error("Error updating processing list dialogs: %s", e)

    def _on_location_comment_changed(self):
        """Handle comment value changes in project container."""
        if not self.controller or not self.controller.project_model:
            return

        new_comment = self.location_comment_value.text()
        self.logger.info(f"Comment changed to: {new_comment}")

        # Update comment in active TOB file headers
        active_tob = self.controller.project_model.get_active_tob_file()
        if active_tob and active_tob.tob_data and active_tob.tob_data.headers:
            active_tob.tob_data.headers["Comments"] = new_comment
            # Store in modified headers for persistence
            active_tob.modified_headers["Comments"] = new_comment
            self.logger.info(f"Updated comment in active TOB file: {active_tob.file_name}")

            # Also update the TOBDataModel in the controller if it exists
            current_tob_data = self.controller.get_current_tob_data()
            if current_tob_data and current_tob_data.headers:
                current_tob_data.headers["Comments"] = new_comment
                self.logger.debug("Updated comment in controller TOBDataModel")

            # Mark project as modified for auto-save
            if hasattr(self.controller, '_mark_project_modified'):
                self.controller._mark_project_modified()

            # Try to update any open processing list dialogs
            self._update_processing_list_dialogs()

    def _on_location_sensorstring_changed(self):
        """Handle sensor string changes in project container."""
        # Sensor string is derived from comment, so this shouldn't be directly editable
        # Reset to derived value
        if hasattr(self, 'update_project_container'):
            self.update_project_container(self.controller.get_current_tob_data() if self.controller else None)
        self.logger.debug("Sensor string change ignored - value is derived from comment")

    def _on_location_subcon_changed(self, value: float):
        """Handle subcon extension changes in project container."""
        if not self.controller or not self.controller.project_model:
            return

        self.logger.info(f"Subcon extension changed to: {value}")

        # Update Subconn_Length in active TOB file headers
        active_tob = self.controller.project_model.get_active_tob_file()
        if active_tob and active_tob.tob_data and active_tob.tob_data.headers:
            active_tob.tob_data.headers["Subconn_Length"] = str(value)
            # Store in modified headers for persistence
            active_tob.modified_headers["Subconn_Length"] = str(value)
            self.logger.info(f"Updated Subconn_Length in active TOB file: {active_tob.file_name}")

            # Also update the TOBDataModel in the controller if it exists
            current_tob_data = self.controller.get_current_tob_data()
            if current_tob_data and current_tob_data.headers:
                current_tob_data.headers["Subconn_Length"] = str(value)
                self.logger.debug("Updated Subconn_Length in controller TOBDataModel")

            # Mark project as modified for auto-save
            if hasattr(self.controller, '_mark_project_modified'):
                self.controller._mark_project_modified()

            # Try to update any open processing list dialogs
            self._update_processing_list_dialogs()

    def _get_status_text(self, status: str) -> str:
        """
        Get human-readable status text (same as in Processing List Dialog).

        Args:
            status: Status string

        Returns:
            Human-readable status text
        """
        status_texts = {
            "loaded": "Loaded",
            "uploading": "Uploading...",
            "uploaded": "Uploaded",
            "processing": "Processing...",
            "processed": "Processed",
            "error": "Error",
        }
        return status_texts.get(status, status)

    def update_project_container_status(self):
        """
        Update the status field in the project container based on the active TOB file.
        """
        try:
            status_text = "-"
            if self.controller and hasattr(self.controller, 'project_model') and self.controller.project_model:
                active_tob = self.controller.project_model.get_active_tob_file()
                if active_tob:
                    status_text = self._get_status_text(active_tob.status)

            if self.status_lineEdit:
                self.status_lineEdit.setText(status_text)

            self.logger.debug("Project container status updated: %s", status_text)

        except Exception as e:
            self.logger.error("Error updating project container status: %s", e)

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

    def _on_x_axis_limits_changed(self):
        """
        Handle manual changes to X-axis min/max limits.
        """
        try:
            # Get values from LineEdits
            min_text = self.x_min_value.text() if self.x_min_value else ""
            max_text = self.x_max_value.text() if self.x_max_value else ""

            # Use axis UI service to handle the limits change
            self.axis_ui_service.handle_axis_limits_changed(
                self, "x", min_text, max_text
            )

        except Exception as e:
            self.logger.error("Failed to handle X-axis limits change: %s", e)

    def _on_y1_axis_limits_changed(self):
        """
        Handle manual changes to Y1-axis min/max limits.
        """
        try:
            # Get values from LineEdits
            min_text = self.y1_min_value.text() if self.y1_min_value else ""
            max_text = self.y1_max_value.text() if self.y1_max_value else ""

            # Use axis UI service to handle the limits change
            self.axis_ui_service.handle_axis_limits_changed(
                self, "y1", min_text, max_text
            )

        except Exception as e:
            self.logger.error("Failed to handle Y1-axis limits change: %s", e)

    def _on_y2_axis_limits_changed(self):
        """
        Handle manual changes to Y2-axis min/max limits.
        """
        try:
            # Get values from LineEdits
            min_text = self.y2_min_value.text() if self.y2_min_value else ""
            max_text = self.y2_max_value.text() if self.y2_max_value else ""

            # Use axis UI service to handle the limits change
            self.axis_ui_service.handle_axis_limits_changed(
                self, "y2", min_text, max_text
            )

        except Exception as e:
            self.logger.error("Failed to handle Y2-axis limits change: %s", e)

    def show_data_loaded(self):
        """
        Show that data has been loaded and switch to plot view.
        """
        self.is_data_loaded = True
        self._show_plot_area()

        # Update axis values using axis UI service
        if self.controller:
            time_range = self.controller.get_time_range()
            if time_range:
                self.axis_ui_service.update_axis_values(self, time_range)

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
            if self._ensure_plot_widget():
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
            if hasattr(self, "plot_widget") and self.plot_widget:
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
            if hasattr(self, "plot_widget") and self.plot_widget:
                self.plot_widget.update_axis_settings(axis_settings)
                self.logger.debug("Plot axis settings updated: %s", axis_settings)
            else:
                self.logger.warning("Plot widget not available for axis update")
        except Exception as e:
            self.logger.error("Failed to update plot axis settings: %s", e)
            self.error_handler.handle_error(e, self, "Plot Axis Update Error")

    def update_plot_x_limits(self, min_value: float, max_value: float):
        """
        Update X-axis limits for plotting.

        Args:
            min_value: Minimum X-axis value in seconds
            max_value: Maximum X-axis value in seconds
        """
        try:
            if hasattr(self, "plot_widget") and self.plot_widget:
                self.plot_widget.update_x_limits(min_value, max_value)
                self.logger.debug(
                    "Plot X-axis limits updated: min=%.2f, max=%.2f",
                    min_value,
                    max_value,
                )
            else:
                self.logger.warning(
                    "Plot widget not available for X-axis limits update"
                )
        except Exception as e:
            self.logger.error("Failed to update plot X-axis limits: %s", e)
            self.error_handler.handle_error(e, self, "Plot X-Axis Limits Update Error")

    def update_plot_y1_limits(self, min_value: float, max_value: float):
        """
        Update Y1-axis limits for plotting.

        Args:
            min_value: Minimum Y1-axis value
            max_value: Maximum Y1-axis value
        """
        try:
            if hasattr(self, "plot_widget") and self.plot_widget:
                self.plot_widget.update_y1_limits(min_value, max_value)
                self.logger.debug(
                    "Plot Y1-axis limits updated: min=%.2f, max=%.2f",
                    min_value,
                    max_value,
                )
            else:
                self.logger.warning(
                    "Plot widget not available for Y1-axis limits update"
                )
        except Exception as e:
            self.logger.error("Failed to update plot Y1-axis limits: %s", e)
            self.error_handler.handle_error(e, self, "Plot Y1-Axis Limits Update Error")

    def update_plot_y2_limits(self, min_value: float, max_value: float):
        """
        Update Y2-axis limits for plotting.

        Args:
            min_value: Minimum Y2-axis value
            max_value: Maximum Y2-axis value
        """
        try:
            if hasattr(self, "plot_widget") and self.plot_widget:
                self.plot_widget.update_y2_limits(min_value, max_value)
                self.logger.debug(
                    "Plot Y2-axis limits updated: min=%.2f, max=%.2f",
                    min_value,
                    max_value,
                )
            else:
                self.logger.warning(
                    "Plot widget not available for Y2-axis limits update"
                )
        except Exception as e:
            self.logger.error("Failed to update plot Y2-axis limits: %s", e)

    def _handle_plot_axis_limits_update(
        self, axis: str, min_value: float, max_value: float
    ):
        """
        Handle plot axis limits update signal from controller.

        Args:
            axis: Axis identifier ('x', 'y1', 'y2')
            min_value: Minimum value for axis
            max_value: Maximum value for axis
        """
        try:
            if axis == "x":
                self.update_plot_x_limits(min_value, max_value)
            elif axis == "y1":
                self.update_plot_y1_limits(min_value, max_value)
            elif axis == "y2":
                self.update_plot_y2_limits(min_value, max_value)
            else:
                self.logger.warning("Unknown axis for limits update: %s", axis)
        except Exception as e:
            self.logger.error("Failed to handle plot axis limits update: %s", e)
            self.error_handler.handle_error(e, self, "Plot Y2-Axis Limits Update Error")

    def get_plot_info(self) -> Dict[str, Any]:
        """
        Get information about the current plot.

        Returns:
            Dictionary containing plot information
        """
        try:
            if hasattr(self, "plot_widget") and self.plot_widget:
                return self.plot_widget.get_plot_info()
            else:
                return {"has_plot_widget": False}
        except Exception as e:
            self.logger.error("Failed to get plot info: %s", e)
            return {"error": str(e)}

    def _setup_style_indicators(self):
        """
        Replace UI placeholder labels with visual style indicators for legend functionality.
        """
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QColor, QPainter, QPen
        from PyQt6.QtWidgets import QLabel

        self.style_indicators = {}

        try:
            for sensor_name, checkbox in self.ntc_checkboxes.items():
                # Get style info from plot style service
                style_info = self.plot_style_service.get_sensor_style(sensor_name)

                # Find the corresponding UI placeholder label
                label_name = self._get_style_label_name(sensor_name)
                placeholder_label = self.findChild(QLabel, label_name)

                self.logger.debug(
                    f"Setting up indicator for {sensor_name}: looking for label '{label_name}'"
                )

                if placeholder_label:
                    self.logger.debug(
                        f"Found placeholder label {label_name} with text '{placeholder_label.text()}' at {placeholder_label.geometry()}"
                    )

                    # Set up the label as a style indicator using UI service
                    indicator = self.ui_service.setup_label_indicator(
                        placeholder_label, style_info
                    )

                    self.logger.debug(
                        f"Successfully set up {label_name} as style indicator"
                    )

                else:
                    self.logger.warning(
                        f"UI placeholder label {label_name} not found for sensor {sensor_name}"
                    )
                    # Create hidden fallback
                    indicator = QLabel()
                    indicator.setParent(self)
                    indicator.hide()

                self.style_indicators[sensor_name] = indicator

            self.logger.debug(
                f"Set up style indicators for {len(self.style_indicators)} sensors"
            )

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
        if not hasattr(self, "style_indicators"):
            return

        try:
            for sensor_name, indicator in self.style_indicators.items():
                style_info = self.plot_style_service.get_sensor_style(sensor_name)

                # Update style info and pixmap using UI service
                if hasattr(indicator, "_style_info"):
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

    def _on_show_upload_success(self, title: str, message: str):
        """
        Handle upload success signal - show QMessageBox on main thread.

        Args:
            title: Dialog title
            message: Dialog message
        """
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(self, title, message)

    def _on_show_server_status(self, title: str, message: str):
        """
        Handle server status signal - show QMessageBox on main thread.

        Args:
            title: Dialog title
            message: Dialog message
        """
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(self, title, message)

    def _on_error_occurred(self, error_type: str, error_message: str, parent):
        """
        Handle error signal - show error dialog on main thread.

        Args:
            error_type: Type of error
            error_message: Error message
            parent: Parent widget
        """
        from PyQt6.QtWidgets import QMessageBox

        msg_box = QMessageBox(parent or self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(f"Error - {error_type}")
        msg_box.setText(f"An error occurred:\n\n{error_message}")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def _on_warning_occurred(self, message: str, parent):
        """
        Handle warning signal - show warning dialog on main thread.

        Args:
            message: Warning message
            parent: Parent widget
        """
        from PyQt6.QtWidgets import QMessageBox

        msg_box = QMessageBox(parent or self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Warning")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def _on_info_message(self, message: str, parent):
        """
        Handle info signal - show info dialog on main thread.

        Args:
            message: Info message
            parent: Parent widget
        """
        from PyQt6.QtWidgets import QMessageBox

        msg_box = QMessageBox(parent or self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("Information")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def closeEvent(self, event):
        """
        Handle application close event.

        Args:
            event: Close event
        """
        self.logger.info("Application closing")

        # TODO: Save settings, cleanup resources

        event.accept()
