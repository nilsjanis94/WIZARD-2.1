"""
Processing List Dialog for WIZARD-2.1

Dialog for managing TOB files in a project.
"""

from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (QAbstractItemView, QDialog, QFileDialog,
                             QHBoxLayout, QHeaderView, QLabel, QMenu,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)


class ProcessingListDialog(QDialog):
    """
    Dialog for managing TOB files in a project.

    Signals:
        file_selected: Emitted when a file is selected for plotting
        file_removed: Emitted when a file is removed from the project
        file_added: Emitted when a file is added to the project
    """

    # Signals
    file_selected = pyqtSignal(str)  # file_path
    file_removed = pyqtSignal(str)  # file_name
    file_added = pyqtSignal(str)  # file_path

    def __init__(self, parent=None):
        """
        Initialize processing list dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Processing List")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel("TOB Files in Project")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title_label)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["File Name", "Size", "Data Points", "Sensors", "Added Date"]
        )

        # Configure table
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_widget.setAlternatingRowColors(True)

        # Context menu
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table_widget)

        # Buttons
        button_layout = QHBoxLayout()

        # Add file button
        add_button = QPushButton("Add TOB File")
        add_button.clicked.connect(self._add_file)
        button_layout.addWidget(add_button)

        # Remove file button
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self._remove_selected_file)
        button_layout.addWidget(remove_button)

        button_layout.addStretch()

        # Plot file button
        plot_button = QPushButton("Plot Selected")
        plot_button.clicked.connect(self._plot_selected_file)
        button_layout.addWidget(plot_button)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel("TOB Files in Project")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title_label)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["File Name", "Size", "Data Points", "Sensors", "Added Date"]
        )

        # Configure table
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.table_widget.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table_widget.setAlternatingRowColors(True)

        # Context menu
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table_widget)

        # Buttons
        button_layout = QHBoxLayout()

        # Add file button
        add_button = QPushButton("Add TOB File")
        add_button.clicked.connect(self._add_file)
        button_layout.addWidget(add_button)

        # Remove file button
        remove_button = QPushButton("Remove Selected")
        remove_button.clicked.connect(self._remove_selected_file)
        button_layout.addWidget(remove_button)

        button_layout.addStretch()

        # Plot file button
        plot_button = QPushButton("Plot Selected")
        plot_button.clicked.connect(self._plot_selected_file)
        button_layout.addWidget(plot_button)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _show_context_menu(self, position) -> None:
        """Show context menu for table items."""
        if self.table_widget.itemAt(position) is None:
            return

        menu = QMenu(self)

        # Plot action
        plot_action = QAction("Plot File", self)
        plot_action.triggered.connect(self._plot_selected_file)
        menu.addAction(plot_action)

        # Remove action
        remove_action = QAction("Remove File", self)
        remove_action.triggered.connect(self._remove_selected_file)
        menu.addAction(remove_action)

        menu.exec(self.table_widget.mapToGlobal(position))

    def _add_file(self) -> None:
        """Add a TOB file to the project."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select TOB File", "", "TOB Files (*.tob *.TOB);;All Files (*)"
        )

        if file_path:
            self.file_added.emit(file_path)

    def _remove_selected_file(self) -> None:
        """Remove the selected file from the project."""
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            file_name_item = self.table_widget.item(current_row, 0)
            if file_name_item:
                file_name = file_name_item.text()

                # Confirm removal
                reply = QMessageBox.question(
                    self,
                    "Remove File",
                    f"Are you sure you want to remove '{file_name}' from the project?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    self.file_removed.emit(file_name)

    def _plot_selected_file(self) -> None:
        """Plot the selected file."""
        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            file_name_item = self.table_widget.item(current_row, 0)
            if file_name_item:
                file_name = file_name_item.text()
                # TODO: Get actual file path from project data
                self.file_selected.emit(file_name)

    def update_file_list(self, files: List[dict]) -> None:
        """
        Update the file list in the table.

        Args:
            files: List of file dictionaries with keys: name, size, data_points, sensors, added_date
        """
        self.table_widget.setRowCount(len(files))

        for row, file_info in enumerate(files):
            # File name
            self.table_widget.setItem(
                row, 0, QTableWidgetItem(file_info.get("name", ""))
            )

            # File size
            size = file_info.get("size", 0)
            size_str = f"{size:,} bytes" if size else "Unknown"
            self.table_widget.setItem(row, 1, QTableWidgetItem(size_str))

            # Data points
            data_points = file_info.get("data_points", 0)
            data_points_str = f"{data_points:,}" if data_points else "Unknown"
            self.table_widget.setItem(row, 2, QTableWidgetItem(data_points_str))

            # Sensors
            sensors = file_info.get("sensors", [])
            sensors_str = f"{len(sensors)} sensors" if sensors else "Unknown"
            self.table_widget.setItem(row, 3, QTableWidgetItem(sensors_str))

            # Added date
            added_date = file_info.get("added_date", "")
            self.table_widget.setItem(row, 4, QTableWidgetItem(str(added_date)))
