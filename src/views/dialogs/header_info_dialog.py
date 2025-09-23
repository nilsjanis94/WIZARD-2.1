"""
Header Info Dialog for WIZARD-2.1

Dialog for displaying TOB file header information.
"""

from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...models.tob_data_model import TOBDataModel


class HeaderInfoDialog(QDialog):
    """
    Dialog for displaying TOB file header information.

    This dialog shows the header metadata from a loaded TOB file
    in a formatted, readable way.
    """

    def __init__(self, tob_data_model: TOBDataModel, parent=None):
        """
        Initialize header info dialog.

        Args:
            tob_data_model: TOBDataModel instance containing header data
            parent: Parent widget
        """
        super().__init__(parent)
        self.tob_data_model = tob_data_model
        self.setWindowTitle("TOB Header Information")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("TOB File Header Information")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #3AAA35;")
        layout.addWidget(title_label)

        # File info section
        file_info_widget = self._create_file_info_widget()
        layout.addWidget(file_info_widget)

        # Header content
        header_content_label = QLabel("Header Content:")
        header_content_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(header_content_label)

        # Text area for header data
        self.header_text = QTextEdit()
        self.header_text.setReadOnly(True)
        self.header_text.setPlainText(self._format_header_data())
        layout.addWidget(self.header_text)

        # Buttons
        button_layout = QHBoxLayout()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _create_file_info_widget(self) -> QWidget:
        """Create widget displaying basic file information."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # File name
        file_name = self.tob_data_model.file_name or "Unknown"
        file_label = QLabel(f"<b>File:</b> {file_name}")
        layout.addWidget(file_label)

        # File size
        if self.tob_data_model.file_size:
            size_mb = self.tob_data_model.file_size / (1024 * 1024)
            size_label = QLabel(".2f")
            layout.addWidget(size_label)

        # Data points
        if self.tob_data_model.data_points:
            points_label = QLabel(
                f"<b>Data Points:</b> {self.tob_data_model.data_points:,}"
            )
            layout.addWidget(points_label)

        # Sensors
        if self.tob_data_model.sensors:
            sensors_text = ", ".join(
                self.tob_data_model.sensors[:10]
            )  # Show first 10 sensors
            if len(self.tob_data_model.sensors) > 10:
                sensors_text += f" ... (+{len(self.tob_data_model.sensors) - 10} more)"
            sensors_label = QLabel(f"<b>Sensors:</b> {sensors_text}")
            sensors_label.setWordWrap(True)
            layout.addWidget(sensors_label)

        return widget

    def _format_header_data(self) -> str:
        """
        Format header data for display.

        Returns:
            Formatted header data as string
        """
        if not self.tob_data_model.headers:
            return "No header information available."

        formatted_lines = []
        formatted_lines.append("=" * 50)
        formatted_lines.append("TOB FILE HEADER INFORMATION")
        formatted_lines.append("=" * 50)
        formatted_lines.append("")

        # Sort headers for consistent display
        sorted_headers = sorted(self.tob_data_model.headers.items())

        for key, value in sorted_headers:
            formatted_lines.append(f"{key}:")
            formatted_lines.append(f"  {value}")
            formatted_lines.append("")

        return "\n".join(formatted_lines)

    @staticmethod
    def format_header_data_for_model(tob_data_model: TOBDataModel) -> str:
        """
        Static method to format header data for a given TOBDataModel.

        Args:
            tob_data_model: TOBDataModel instance

        Returns:
            Formatted header data as string
        """
        if not tob_data_model.headers:
            return "No header information available."

        formatted_lines = []
        formatted_lines.append("=" * 50)
        formatted_lines.append("TOB FILE HEADER INFORMATION")
        formatted_lines.append("=" * 50)
        formatted_lines.append("")

        # Sort headers for consistent display
        sorted_headers = sorted(tob_data_model.headers.items())

        for key, value in sorted_headers:
            formatted_lines.append(f"{key}:")
            formatted_lines.append(f"  {value}")
            formatted_lines.append("")

        return "\n".join(formatted_lines)
