"""
Main Window for WIZARD-2.1

Main application window with PyQt6 integration.
"""

from typing import Optional
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon


class MainWindow(QMainWindow):
    """
    Main application window.
    
    Signals:
        file_opened: Emitted when a file is opened
        project_created: Emitted when a project is created
        project_opened: Emitted when a project is opened
    """
    
    # Signals
    file_opened = pyqtSignal(str)  # file_path
    project_created = pyqtSignal(str)  # project_name
    project_opened = pyqtSignal(str)  # project_path
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the main window.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("WIZARD-2.1 - Scientific Data Analysis Tool")
        self.setMinimumSize(1200, 800)
        
        # Initialize UI
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        
    def _setup_ui(self) -> None:
        """Setup the main UI components."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Welcome label (placeholder)
        welcome_label = QLabel("Welcome to WIZARD-2.1")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 50px;")
        main_layout.addWidget(welcome_label)
        
        # TODO: Add actual UI components from .ui file
        # This will be implemented when we integrate the Qt Designer file
        
    def _setup_menu_bar(self) -> None:
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Open TOB file action
        open_tob_action = QAction("Open TOB File", self)
        open_tob_action.setShortcut("Ctrl+O")
        open_tob_action.triggered.connect(self._open_tob_file)
        file_menu.addAction(open_tob_action)
        
        file_menu.addSeparator()
        
        # New project action
        new_project_action = QAction("New Project", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)
        
        # Open project action
        open_project_action = QAction("Open Project", self)
        open_project_action.setShortcut("Ctrl+Shift+O")
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Project menu
        project_menu = menubar.addMenu("Project")
        
        # Processing list action
        processing_list_action = QAction("Processing List", self)
        processing_list_action.triggered.connect(self._show_processing_list)
        project_menu.addAction(processing_list_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        # Language submenu
        language_menu = tools_menu.addMenu("Language")
        
        # English action
        english_action = QAction("English", self)
        english_action.setCheckable(True)
        english_action.setChecked(True)  # Default language
        english_action.triggered.connect(lambda: self._change_language("en"))
        language_menu.addAction(english_action)
        
        # German action
        german_action = QAction("Deutsch", self)
        german_action.setCheckable(True)
        german_action.triggered.connect(lambda: self._change_language("de"))
        language_menu.addAction(german_action)
        
    def _setup_status_bar(self) -> None:
        """Setup the status bar."""
        self.statusBar().showMessage("Ready")
        
    def _open_tob_file(self) -> None:
        """Handle opening a TOB file."""
        # TODO: Implement file dialog
        print("Open TOB file - to be implemented")
        
    def _new_project(self) -> None:
        """Handle creating a new project."""
        # TODO: Implement project creation dialog
        print("New project - to be implemented")
        
    def _open_project(self) -> None:
        """Handle opening an existing project."""
        # TODO: Implement project opening dialog
        print("Open project - to be implemented")
        
    def _show_processing_list(self) -> None:
        """Show the processing list dialog."""
        # TODO: Implement processing list dialog
        print("Processing list - to be implemented")
        
    def _change_language(self, language: str) -> None:
        """Change the application language."""
        # TODO: Implement language switching
        print(f"Change language to {language} - to be implemented")
        
    def show_welcome_screen(self) -> None:
        """Show the welcome screen."""
        # TODO: Implement welcome screen
        pass
        
    def show_plot_area(self) -> None:
        """Show the plot area with data visualization."""
        # TODO: Implement plot area
        pass
        
    def update_status(self, message: str) -> None:
        """
        Update the status bar message.
        
        Args:
            message: Status message to display
        """
        self.statusBar().showMessage(message)
