"""
Main window view for the WIZARD-2.1 application.

This module contains the main window class that serves as the primary interface
for the temperature data analysis application.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox,
                             QDoubleSpinBox, QFileDialog, QFrame, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMainWindow,
                             QMessageBox, QPushButton, QSizePolicy,
                             QSpacerItem, QVBoxLayout, QWidget)

from ..utils.error_handler import ErrorHandler
from ..services.ui_state_manager import UIStateManager, UIState


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

        # Initialize UI state manager
        self.ui_state_manager = UIStateManager()

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

            # Set up fonts for better readability
            self._setup_fonts()

            # Store references to important widgets
            self._store_widget_references()

            # Set up UI state manager with container references
            self.ui_state_manager.set_containers(self.welcome_container, self.plot_container)

            # Initialize UI state
            self._initialize_ui_state()

            self.logger.info("UI loaded successfully from .ui file")

        except Exception as e:
            self.logger.error(f"Failed to load UI: {e}")
            self.error_handler.show_error(
                "UI Loading Error", f"Failed to load the user interface: {e}"
            )
            raise

    def _setup_fonts(self):
        """
        Set up fonts using the UI service for better modularity.
        """
        try:
            from ..services.ui_service import UIService
            
            # Use UI service for font management
            ui_service = UIService()
            success = ui_service.setup_fonts(self)
            
            if success:
                self.logger.info("Fonts configured successfully using UI service")
            else:
                self.logger.warning("Font setup failed, using system default")
                
        except Exception as e:
            self.logger.error(f"Font setup failed: {e}")
            # Fallback to system default
            try:
                from PyQt6.QtGui import QFont
                fallback_font = QFont()
                fallback_font.setStyleHint(QFont.StyleHint.SansSerif)
                fallback_font.setPointSize(10)
                self.setFont(fallback_font)
                self.logger.info("Using system fallback font")
            except Exception as fallback_error:
                self.logger.error(f"Font setup completely failed: {fallback_error}")

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

        # PT100 checkbox
        self.ntc_pt100_checkbox = self.findChild(QCheckBox, "ntc_pt100_checkbox")
        if self.ntc_pt100_checkbox:
            self.ntc_checkboxes["PT100"] = self.ntc_pt100_checkbox

        # Data metrics widgets
        self.mean_hp_power_value = self.findChild(QLineEdit, "mean_hp_power_value")
        self.max_v_accu_value = self.findChild(QLineEdit, "max_v_accu_value")
        self.tilt_status_value = self.findChild(QLineEdit, "tilt_status_value")
        self.mean_press_value = self.findChild(QLineEdit, "mean_press_value")

        # Axis control widgets
        self.y1_axis_combo = self.findChild(QComboBox, "y1_axis_combo")
        self.y2_axis_combo = self.findChild(QComboBox, "y2_axis_combo")
        self.x_axis_combo = self.findChild(QComboBox, "x_axis_combo")

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
        # Fix UI visibility issues first
        self._fix_ui_visibility()

        # Show welcome screen initially (reset to initial state)
        self.ui_state_manager.reset_to_initial_state()

        # Initialize axis controls
        self._initialize_axis_controls()

        # Set default values
        self._reset_data_metrics()
        self._reset_project_info()

        self.logger.debug("UI state initialized")

    def _fix_ui_visibility(self):
        """
        Fix UI visibility issues by ensuring all text widgets are visible and properly styled.
        This addresses the problem where widgets exist but are not visible to the user.
        """
        try:
            from PyQt6.QtWidgets import QLabel, QCheckBox, QPushButton, QLineEdit

            # Fix QLabel widgets
            labels = self.findChildren(QLabel)
            for label in labels:
                label.setVisible(True)
                current_style = label.styleSheet() or ""
                if "color:" not in current_style:
                    label.setStyleSheet(current_style + "color: black;")

            # Fix QCheckBox widgets
            checkboxes = self.findChildren(QCheckBox)
            for checkbox in checkboxes:
                checkbox.setVisible(True)
                current_style = checkbox.styleSheet() or ""
                if "color:" not in current_style:
                    checkbox.setStyleSheet(current_style + "color: black;")

            # Fix QPushButton widgets
            buttons = self.findChildren(QPushButton)
            for button in buttons:
                button.setVisible(True)
                current_style = button.styleSheet() or ""
                if "color:" not in current_style:
                    button.setStyleSheet(current_style + "color: black; background-color: lightgray;")

            # Fix QLineEdit widgets
            line_edits = self.findChildren(QLineEdit)
            for line_edit in line_edits:
                line_edit.setVisible(True)
                current_style = line_edit.styleSheet() or ""
                if "color:" not in current_style:
                    line_edit.setStyleSheet(current_style + "color: black; background-color: white;")

            self.logger.info("UI visibility fixed: %d labels, %d checkboxes, %d buttons, %d line edits", 
                           len(labels), len(checkboxes), len(buttons), len(line_edits))

        except Exception as e:
            self.logger.error("Failed to fix UI visibility: %s", e)

    def _initialize_axis_controls(self):
        """
        Initialize the axis control comboboxes with available options.
        """
        # Y1 and Y2 axis options (temperature sensors)
        sensor_options = [
            "NTC01",
            "NTC02",
            "NTC03",
            "NTC04",
            "NTC05",
            "NTC06",
            "NTC07",
            "NTC08",
            "NTC09",
            "NTC10",
            "NTC11",
            "NTC12",
            "NTC13",
            "NTC14",
            "NTC15",
            "NTC16",
            "NTC17",
            "NTC18",
            "NTC19",
            "NTC20",
            "NTC21",
            "NTC22",
            "PT100",
        ]

        if self.y1_axis_combo:
            self.y1_axis_combo.addItems(sensor_options)
            self.y1_axis_combo.setCurrentText("NTC01")

        if self.y2_axis_combo:
            self.y2_axis_combo.addItems(sensor_options)
            self.y2_axis_combo.setCurrentText("PT100")

        # X axis options (time-based)
        time_options = ["Time", "Depth", "Pressure"]
        if self.x_axis_combo:
            self.x_axis_combo.addItems(time_options)
            self.x_axis_combo.setCurrentText("Time")

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
        metrics_widgets = [
            self.mean_hp_power_value,
            self.max_v_accu_value,
            self.tilt_status_value,
            self.mean_press_value,
        ]

        for widget in metrics_widgets:
            if widget:
                widget.setText("-")

    def _reset_project_info(self):
        """
        Reset project information to default values.
        """
        if self.cruise_info_label:
            self.cruise_info_label.setText("Project: -")

        if self.location_info_label:
            self.location_info_label.setText("Location: -")

        if self.location_comment_value:
            self.location_comment_value.setText("-")

        if self.location_sensorstring_value:
            self.location_sensorstring_value.setText("-")

        if self.location_subcon_spin:
            self.location_subcon_spin.setValue(0.0)

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
                self.logger.info(f"Opening TOB file: {file_path}")
                self.file_opened.emit(file_path)
                # Switch to plot mode when TOB file is loaded
                self.ui_state_manager.show_plot_mode()

        except Exception as e:
            self.logger.error(f"Error opening TOB file: {e}")
            self.error_handler.show_error(
                "File Open Error", f"Failed to open file: {e}"
            )

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
                self.logger.info(f"Opening project file: {file_path}")
                self.project_opened.emit(file_path, password)
                # Switch to plot mode when project is loaded
                self.ui_state_manager.show_plot_mode()

        except Exception as e:
            self.logger.error(f"Error opening project: {e}")
            self.error_handler.show_error(
                "Project Open Error", f"Failed to open project: {e}"
            )

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
                self.logger.info(f"Creating project file: {file_path}")
                self.project_created.emit(file_path, password)

        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            self.error_handler.show_error(
                "Project Creation Error", f"Failed to create project: {e}"
            )

    def _on_sensor_selection_changed(self, sensor_name: str, state: int):
        """
        Handle sensor selection changes.

        Args:
            sensor_name: Name of the sensor (e.g., "NTC01", "PT100")
            state: Checkbox state (0 = unchecked, 2 = checked)
        """
        is_selected = state == 2
        self.logger.debug(f"Sensor {sensor_name} selection changed: {is_selected}")

        # TODO: Update plot visualization
        if self.controller:
            self.controller.update_sensor_selection(sensor_name, is_selected)

    def _on_y1_auto_changed(self, state: int):
        """Handle Y1 axis auto mode change."""
        is_auto = state == 2
        self.logger.debug(f"Y1 axis auto mode: {is_auto}")

        # Enable/disable manual controls
        if self.y1_min_value and self.y1_max_value:
            self.y1_min_value.setEnabled(not is_auto)
            self.y1_max_value.setEnabled(not is_auto)

    def _on_y2_auto_changed(self, state: int):
        """Handle Y2 axis auto mode change."""
        is_auto = state == 2
        self.logger.debug(f"Y2 axis auto mode: {is_auto}")

        # Enable/disable manual controls
        if self.y2_min_value and self.y2_max_value:
            self.y2_min_value.setEnabled(not is_auto)
            self.y2_max_value.setEnabled(not is_auto)

    def _on_x_auto_changed(self, state: int):
        """Handle X axis auto mode change."""
        is_auto = state == 2
        self.logger.debug(f"X axis auto mode: {is_auto}")

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

        self.logger.debug(f"Project info updated: {project_name}, {location}")

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
        self.logger.debug(f"Status message: {message}")

    def closeEvent(self, event):
        """
        Handle application close event.

        Args:
            event: Close event
        """
        self.logger.info("Application closing")

        # TODO: Save settings, cleanup resources

        event.accept()
