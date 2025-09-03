"""
Main Controller for WIZARD-2.1

Main application controller following MVC pattern.
"""

from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal


class MainController(QObject):
    """
    Main application controller.
    
    Signals:
        data_loaded: Emitted when data is loaded
        project_created: Emitted when a project is created
        project_opened: Emitted when a project is opened
        error_occurred: Emitted when an error occurs
    """
    
    # Signals
    data_loaded = pyqtSignal(object)  # TOBDataModel
    project_created = pyqtSignal(object)  # ProjectModel
    project_opened = pyqtSignal(object)  # ProjectModel
    error_occurred = pyqtSignal(str, str)  # error_type, error_message
    
    def __init__(self, main_window):
        """
        Initialize the main controller.
        
        Args:
            main_window: Main window instance
        """
        super().__init__()
        self.main_window = main_window
        self.current_project: Optional[object] = None  # ProjectModel
        self.current_data: Optional[object] = None  # TOBDataModel
        
        # Connect signals
        self._connect_signals()
        
    def _connect_signals(self) -> None:
        """Connect signals between components."""
        # Connect main window signals
        self.main_window.file_opened.connect(self._handle_file_opened)
        self.main_window.project_created.connect(self._handle_project_created)
        self.main_window.project_opened.connect(self._handle_project_opened)
        
    def _handle_file_opened(self, file_path: str) -> None:
        """
        Handle file opened signal.
        
        Args:
            file_path: Path to the opened file
        """
        try:
            # TODO: Implement TOB file loading
            print(f"Loading file: {file_path}")
            # self.current_data = TOBService.load_tob_file(file_path)
            # self.data_loaded.emit(self.current_data)
        except Exception as e:
            self.error_occurred.emit("File Loading Error", str(e))
            
    def _handle_project_created(self, project_name: str) -> None:
        """
        Handle project created signal.
        
        Args:
            project_name: Name of the created project
        """
        try:
            # TODO: Implement project creation
            print(f"Creating project: {project_name}")
            # self.current_project = ProjectService.create_project(project_name)
            # self.project_created.emit(self.current_project)
        except Exception as e:
            self.error_occurred.emit("Project Creation Error", str(e))
            
    def _handle_project_opened(self, project_path: str) -> None:
        """
        Handle project opened signal.
        
        Args:
            project_path: Path to the project file
        """
        try:
            # TODO: Implement project opening
            print(f"Opening project: {project_path}")
            # self.current_project = ProjectService.open_project(project_path)
            # self.project_opened.emit(self.current_project)
        except Exception as e:
            self.error_occurred.emit("Project Opening Error", str(e))
            
    def show_error_dialog(self, error_type: str, error_message: str) -> None:
        """
        Show error dialog.
        
        Args:
            error_type: Type of error
            error_message: Error message
        """
        # TODO: Implement error dialog
        print(f"Error: {error_type} - {error_message}")
        
    def get_current_project(self) -> Optional[object]:
        """
        Get the current project.
        
        Returns:
            Current project or None
        """
        return self.current_project
        
    def get_current_data(self) -> Optional[object]:
        """
        Get the current data.
        
        Returns:
            Current data or None
        """
        return self.current_data
