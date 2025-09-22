"""
Processing List Dialog for WIZARD-2.1

Dialog for managing TOB files in a project.
"""

from pathlib import Path
from typing import List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QMessageBox,
    QProgressDialog,
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

    def update_tob_file_status(self, file_name: str, new_status: str) -> None:
        """
        Update the status of a TOB file and refresh the display.

        Args:
            file_name: Name of the TOB file
            new_status: New status ('loaded', 'uploading', 'uploaded', 'processing', 'processed', 'error')
        """
        if not self.project_model:
            return

        # Update status in project model
        self.project_model.update_tob_file_status(file_name, new_status)

        # Find and update the row in the table
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)  # File name column
            if item and item.data(Qt.ItemDataRole.UserRole) == file_name:
                # Update status text
                status_item = QTableWidgetItem(self._get_status_text(new_status))
                status_item.setIcon(self._get_status_icon(new_status))
                self.table_widget.setItem(row, 4, status_item)  # Status column
                break

        # Trigger auto-save if connected to controller
        if hasattr(self.parent(), 'controller') and self.parent().controller:
            self.parent().controller._mark_project_modified()

    def get_tob_file_status(self, file_name: str) -> Optional[str]:
        """
        Get the current status of a TOB file.

        Args:
            file_name: Name of the TOB file

        Returns:
            Current status string or None if file not found
        """
        if not self.project_model:
            return None

        tob_file = self.project_model.get_tob_file(file_name)
        return tob_file.status if tob_file else None

    def simulate_status_progression(self, file_name: str) -> None:
        """
        Simulate status progression for testing purposes.
        Cycles through: loaded -> uploading -> uploaded -> processing -> processed

        Args:
            file_name: Name of the TOB file to update
        """
        current_status = self.get_tob_file_status(file_name)
        if not current_status:
            return

        status_cycle = ["loaded", "uploading", "uploaded", "processing", "processed"]
        try:
            current_index = status_cycle.index(current_status)
            next_index = (current_index + 1) % len(status_cycle)
            next_status = status_cycle[next_index]
            self.update_tob_file_status(file_name, next_status)
        except ValueError:
            # Status not in cycle, reset to loaded
            self.update_tob_file_status(file_name, "loaded")

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
            status_icon = self._get_status_icon(tob_file.status)
            if status_icon is not None:
                status_item.setIcon(status_icon)
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

    def _get_status_description(self, status: str) -> str:
        """
        Get detailed description for status tooltip.

        Args:
            status: Status string

        Returns:
            Detailed description of the status
        """
        descriptions = {
            "loaded": "TOB file has been loaded into the project",
            "uploading": "File is currently being uploaded to the server",
            "uploaded": "File has been successfully uploaded to the server",
            "processing": "Server is processing the uploaded file",
            "processed": "File processing has been completed successfully",
            "error": "An error occurred during upload or processing"
        }
        return descriptions.get(status, "Unknown status")

    def _get_status_icon(self, status: str):
        """
        Get appropriate icon for status.

        Args:
            status: Status string

        Returns:
            QIcon for the status (colored circle indicators)
        """
        # Create colored circle icons for different statuses
        icon_size = 16
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.GlobalColor.transparent)

        from PyQt6.QtGui import QPainter, QBrush
        painter = QPainter(pixmap)

        # Define colors for different statuses
        colors = {
            "loaded": QColor("#4CAF50"),      # Green - file loaded successfully
            "uploading": QColor("#FF9800"),   # Orange - currently uploading
            "uploaded": QColor("#2196F3"),    # Blue - uploaded to server
            "processing": QColor("#FF5722"),  # Deep orange - being processed
            "processed": QColor("#9C27B0"),   # Purple - processing complete
            "error": QColor("#F44336"),       # Red - error occurred
        }

        # Get color for status, default to gray if unknown
        color = colors.get(status, QColor("#9E9E9E"))  # Gray for unknown status

        # Draw colored circle
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, icon_size-4, icon_size-4)

        # Add white border for better visibility
        painter.setBrush(Qt.BrushStyle.NoBrush)
        from PyQt6.QtGui import QPen
        painter.setPen(QPen(QColor("#FFFFFF"), 1))
        painter.drawEllipse(1, 1, icon_size-2, icon_size-2)

        painter.end()

        return QIcon(pixmap)

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

        # Status legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Status:"))

        # Create small colored squares with text labels
        status_items = [
            ("loaded", "Loaded", "#4CAF50"),
            ("uploading", "Uploading", "#FF9800"),
            ("uploaded", "Uploaded", "#2196F3"),
            ("processing", "Processing", "#FF5722"),
            ("processed", "Processed", "#9C27B0"),
            ("error", "Error", "#F44336")
        ]

        for status_key, display_text, color in status_items:
            # Create a small colored label
            color_label = QLabel("●")
            color_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
            color_label.setToolTip(f"{display_text}: {self._get_status_description(status_key)}")

            text_label = QLabel(display_text)
            text_label.setStyleSheet("font-size: 11px; margin-left: 2px;")

            item_layout = QHBoxLayout()
            item_layout.addWidget(color_label)
            item_layout.addWidget(text_label)
            item_layout.setSpacing(0)
            item_layout.setContentsMargins(0, 0, 10, 0)

            legend_layout.addLayout(item_layout)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

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

        # Status legend
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Status:"))

        # Create small colored squares with text labels
        status_items = [
            ("loaded", "Loaded", "#4CAF50"),
            ("uploading", "Uploading", "#FF9800"),
            ("uploaded", "Uploaded", "#2196F3"),
            ("processing", "Processing", "#FF5722"),
            ("processed", "Processed", "#9C27B0"),
            ("error", "Error", "#F44336")
        ]

        for status_key, display_text, color in status_items:
            # Create a small colored label
            color_label = QLabel("●")
            color_label.setStyleSheet(f"color: {color}; font-size: 14px; font-weight: bold;")
            color_label.setToolTip(f"{display_text}: {self._get_status_description(status_key)}")

            text_label = QLabel(display_text)
            text_label.setStyleSheet("font-size: 11px; margin-left: 2px;")

            item_layout = QHBoxLayout()
            item_layout.addWidget(color_label)
            item_layout.addWidget(text_label)
            item_layout.setSpacing(0)
            item_layout.setContentsMargins(0, 0, 10, 0)

            legend_layout.addLayout(item_layout)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

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

                    # Validate file before loading
                from ...services.tob_service import TOBService
                tob_service = TOBService()

                validation = tob_service.validate_tob_file(file_path)
                if not validation['valid']:
                    QMessageBox.warning(self, "Validation Failed",
                                      f"Cannot load {file_name}: {validation['error_message']}")
                    skipped_count += 1
                    continue

                # Show progress dialog for loading
                progress = QProgressDialog(f"Loading {file_name}...", "Cancel", 0, 100, self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setAutoClose(True)
                progress.setAutoReset(True)
                progress.show()

                try:
                    # Load TOB file with timeout protection
                    progress.setValue(10)
                    progress.setLabelText("Validating file...")

                    tob_data = tob_service.load_tob_file_with_timeout(file_path)

                    progress.setValue(50)
                    progress.setLabelText("Processing data...")

                    # Extract metadata
                    data_points = len(tob_data.data) if tob_data.data is not None else 0
                    sensors = []
                    if tob_data.data is not None and not tob_data.data.empty:
                        # Extract sensor columns (exclude time, metadata columns)
                        exclude_cols = {'time', 'timestamp', 'datasets', 'date', 'datetime',
                                      'vbatt', 'vaccu', 'press', 'pressure', 'battery'}
                        sensors = [col for col in tob_data.data.columns
                                 if col.lower() not in exclude_cols]

                    progress.setValue(80)
                    progress.setLabelText("Adding to project...")

                    # Add to project with full data
                    success = self.project_model.add_tob_file(
                        file_path=file_path,
                        file_name=file_name,
                        file_size=file_size,
                        headers=tob_data.headers,
                        dataframe=tob_data.data,
                        raw_data="",  # TODO: Store raw data if needed
                        data_points=data_points,
                        sensors=sensors
                    )

                    progress.setValue(100)

                except TimeoutError:
                    QMessageBox.warning(self, "Loading Timeout",
                                      f"Loading {file_name} timed out. File may be too large or corrupted.")
                    skipped_count += 1
                    continue
                except Exception as e:
                    QMessageBox.warning(self, "Loading Failed",
                                      f"Failed to load {file_name}: {str(e)}")
                    skipped_count += 1
                    continue
                finally:
                    progress.close()

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
