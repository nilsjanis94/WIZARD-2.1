"""
Main controller for the WIZARD-2.1 application.

This module contains the main controller class that coordinates between
the models, views, and services.
"""

import logging
from typing import Any, Dict, Optional

from ..models.project_model import ProjectModel
from ..models.tob_data_model import TOBDataModel
from ..services.data_service import DataService
from ..services.encryption_service import EncryptionService
from ..services.error_service import ErrorService
from ..services.tob_service import TOBService
from ..utils.error_handler import ErrorHandler


class MainController:
    """
    Main controller class for the WIZARD-2.1 application.

    This class coordinates between the models, views, and services,
    handling the main application logic and user interactions.
    """

    def __init__(self):
        """
        Initialize the main controller.
        """
        self.logger = logging.getLogger(__name__)

        # Initialize services
        self.tob_service = TOBService()
        self.data_service = DataService()
        self.encryption_service = EncryptionService()
        self.error_service = ErrorService()
        self.error_handler = ErrorHandler()

        # Initialize models
        self.tob_data_model = TOBDataModel()
        self.project_model = ProjectModel(name="Untitled Project")

        # Initialize view (import here to avoid circular import)
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
            self.logger.info(f"Loading TOB file: {file_path}")
            self.main_window.show_status_message("Loading file...")

            # Load TOB data using service
            tob_data = self.tob_service.load_tob_file(file_path)

            # Update model
            self.tob_data_model.set_data(tob_data)

            # Update view
            self._update_view_with_data()

            self.main_window.show_status_message("File loaded successfully")
            self.logger.info("TOB file loaded successfully")

        except Exception as e:
            self.logger.error(f"Error loading TOB file: {e}")
            self.error_handler.show_error(
                "File Loading Error", f"Failed to load file: {e}"
            )
            self.main_window.show_status_message("Error loading file")

    def _on_project_created(self, project_path: str, password: str):
        """
        Handle project created signal from view.

        Args:
            project_path: Path to the project file
            password: Project password
        """
        try:
            self.logger.info(f"Creating project: {project_path}")
            self.main_window.show_status_message("Creating project...")

            # Create project using encryption service
            self.encryption_service.create_project(
                project_path, password, self.tob_data_model
            )

            self.main_window.show_status_message("Project created successfully")
            self.logger.info("Project created successfully")

        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
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
            self.logger.info(f"Opening project: {project_path}")
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
            self.logger.error(f"Error opening project: {e}")
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
        self.logger.debug(f"Sensor selection updated: {sensor_name} = {is_selected}")

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
