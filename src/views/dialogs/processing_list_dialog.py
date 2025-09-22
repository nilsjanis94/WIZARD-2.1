"""
Processing List Dialog for WIZARD-2.1

Dialog for managing TOB files in a project.
"""

from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class ProcessingListDialog(QDialog):
    """
    Dialog for managing TOB files in a project.

    Signals:
        file_selected: Emitted when a file is selected for plotting
        file_removed: Emitted when a file is removed from the project
        file_added: Emitted when a file is added to the project
        status_updated: Emitted when TOB file status changes
    """

    # Signals
    file_selected = pyqtSignal(str)  # file_path
    file_removed = pyqtSignal(str)  # file_name
    file_added = pyqtSignal(str)  # file_path
    status_updated = pyqtSignal(str, str)  # file_name, new_status

    def __init__(self, parent=None, project_model=None):
        """
        Initialize processing list dialog.

        Args:
            parent: Parent widget
            project_model: ProjectModel instance to manage TOB files for
        """
        super().__init__(parent)
        self.setWindowTitle("Processing List")
        self.setModal(True)
        self.setMinimumSize(600, 400)

        # Store project model reference
        self.project_model = project_model

        self._setup_ui()
        self._populate_table()

    def set_project_model(self, project_model) -> None:
        """
        Set or update the project model.

        Args:
            project_model: ProjectModel instance
        """
        self.project_model = project_model
        self._populate_table()

    def _populate_table(self) -> None:
        """
        Populate the table with TOB files from the project model.
        """
        self.table_widget.setRowCount(0)  # Clear existing rows

        if not self.project_model or not self.project_model.tob_files:
            return

        for tob_file in self.project_model.tob_files:
            row_position = self.table_widget.rowCount()
            self.table_widget.insertRow(row_position)

            # File name
            self.table_widget.setItem(row_position, 0, QTableWidgetItem(tob_file.file_name))

            # File size (formatted)
            size_mb = tob_file.file_size / (1024 * 1024)
            self.table_widget.setItem(row_position, 1, QTableWidgetItem(f"{size_mb:.1f} MB"))

            # Data points
            data_points = tob_file.data_points or 0
            self.table_widget.setItem(row_position, 2, QTableWidgetItem(str(data_points)))

            # Sensors
            sensors_str = ", ".join(tob_file.sensors) if tob_file.sensors else "None"
            self.table_widget.setItem(row_position, 3, QTableWidgetItem(sensors_str))

            # Status with icon
            status_item = QTableWidgetItem(self._get_status_text(tob_file.status))
            status_item.setIcon(self._get_status_icon(tob_file.status))
            self.table_widget.setItem(row_position, 4, status_item)

            # Store file name for later reference
            self.table_widget.item(row_position, 0).setData(Qt.ItemDataRole.UserRole, tob_file.file_name)

    def _get_status_text(self, status: str) -> str:
        """
        Get human-readable status text.

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
            "error": "Error"
        }
        return status_texts.get(status, status)

    def _get_status_icon(self, status: str):
        """
        Get appropriate icon for status.

        Args:
            status: Status string

        Returns:
            QIcon for the status
        """
        # For now, return None - icons can be added later
        # This would typically load icons from resources
        return None

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Title label
        title_label = QLabel("TOB Files in Project")
        layout.addWidget(title_label)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["File Name", "Size", "Data Points", "Sensors", "Status"]
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
        layout.addWidget(title_label)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["File Name", "Size", "Data Points", "Sensors", "Status"]
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
        if not self.project_model:
            QMessageBox.warning(self, "No Project", "No project is currently loaded.")
            return

        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "Select TOB File(s)", "", "TOB Files (*.tob *.TOB);;All Files (*)"
        )

        if not file_paths:
            return

        added_count = 0
        skipped_count = 0

        for file_path in file_paths:
            try:
                # Get file info
                file_name = Path(file_path).name
                file_size = Path(file_path).stat().st_size

                # Check limits
                can_add, reason = self.project_model.can_add_tob_file(file_size)
                if not can_add:
                    QMessageBox.warning(self, "Cannot Add File",
                                      f"Cannot add {file_name}: {reason}")
                    skipped_count += 1
                    continue

                # TODO: Load TOB file data (headers, dataframe, etc.)
                # For now, add with basic info only
                success = self.project_model.add_tob_file(
                    file_path=file_path,
                    file_name=file_name,
                    file_size=file_size,
                    # TODO: Add actual TOB data loading here
                )

                if success:
                    added_count += 1
                    self.file_added.emit(file_path)
                else:
                    skipped_count += 1

            except Exception as e:
                QMessageBox.warning(self, "Error Adding File",
                                  f"Error adding {Path(file_path).name}: {str(e)}")
                skipped_count += 1

        # Update table
        self._populate_table()

        # Show result
        if added_count > 0:
            QMessageBox.information(self, "Files Added",
                                  f"Successfully added {added_count} file(s)." +
                                  (f" Skipped {skipped_count} file(s)." if skipped_count > 0 else ""))
            # Trigger auto-save
            if hasattr(self.parent(), 'controller') and self.parent().controller:
                self.parent().controller._mark_project_modified()

    def _remove_selected_file(self) -> None:
        """Remove the selected file from the project."""
        if not self.project_model:
            QMessageBox.warning(self, "No Project", "No project is currently loaded.")
            return

        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            file_name_item = self.table_widget.item(current_row, 0)
            if file_name_item:
                file_name = file_name_item.text()

                # Confirm removal
                reply = QMessageBox.question(
                    self,
                    "Remove File",
                    f"Are you sure you want to remove '{file_name}' from the project?\n\n"
                    "This action cannot be undone.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.Yes:
                    # Remove from project model
                    success = self.project_model.remove_tob_file(file_name)
                    if success:
                        self._populate_table()  # Refresh table
                        self.file_removed.emit(file_name)
                        QMessageBox.information(self, "File Removed",
                                              f"'{file_name}' has been removed from the project.")

                        # Trigger auto-save
                        if hasattr(self.parent(), 'controller') and self.parent().controller:
                            self.parent().controller._mark_project_modified()
                    else:
                        QMessageBox.warning(self, "Remove Failed",
                                          f"Could not remove '{file_name}' from the project.")

    def _plot_selected_file(self) -> None:
        """Plot the selected file."""
        if not self.project_model:
            QMessageBox.warning(self, "No Project", "No project is currently loaded.")
            return

        current_row = self.table_widget.currentRow()
        if current_row >= 0:
            file_name_item = self.table_widget.item(current_row, 0)
            if file_name_item:
                file_name = file_name_item.text()

                # Get TOB file info from project
                tob_file = self.project_model.get_tob_file(file_name)
                if tob_file:
                    # Set as active file in project
                    self.project_model.set_active_tob_file(file_name)

                    # Emit signal with file name (parent will handle the plotting)
                    self.file_selected.emit(file_name)

                    # Update table to show active state
                    self._populate_table()
                else:
                    QMessageBox.warning(self, "File Not Found",
                                      f"Could not find file '{file_name}' in project.")

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
