"""
UI Service for WIZARD-2.1

Cross-platform UI styling, font management, and widget operations.
"""

import logging
import platform
from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QPixmap
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QLabel, QLineEdit,
                             QPushButton, QWidget)


class UIService:
    """
    Service for managing UI styling and fonts across platforms.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.current_platform = platform.system()

    def setup_fonts(self, widget: QWidget) -> bool:
        """
        Set up cross-platform fonts for a widget and all its children.

        Args:
            widget: The widget to apply fonts to

        Returns:
            True if fonts were applied successfully, False otherwise
        """
        try:
            # Get platform-appropriate font
            font = self._get_platform_font()

            # Apply font to widget and all children
            self._apply_font_recursively(widget, font)

            self.logger.info(
                "Fonts applied successfully: %s on %s",
                font.family(),
                self.current_platform,
            )
            return True

        except (AttributeError, TypeError) as e:
            self.logger.error("Font setup attribute error: %s", e)
            return False
        except Exception as e:
            self.logger.error("Unexpected error setting up fonts: %s", e)
            return False

    def _get_platform_font(self) -> QFont:
        """
        Get the appropriate font for the current platform.
        Uses fonts that actually work based on testing.

        Returns:
            QFont configured for the current platform
        """
        font = QFont()

        # Use fonts that actually work (based on testing)
        if self.current_platform == "Darwin":  # macOS
            # Arial works reliably on macOS
            font.setFamily("Arial")
        elif self.current_platform == "Windows":
            # Arial works on Windows
            font.setFamily("Arial")
        elif self.current_platform == "Linux":
            # Arial works on Linux
            font.setFamily("Arial")
        else:
            # Generic fallback
            font.setFamily("Arial")

        # Set consistent properties
        font.setPointSize(11)  # Slightly larger for better visibility
        font.setWeight(QFont.Weight.Normal)
        font.setStyleHint(QFont.StyleHint.SansSerif)

        return font

    def _apply_font_recursively(self, widget: QWidget, font: QFont) -> None:
        """
        Apply font to widget and all its children recursively.

        Args:
            widget: The widget to apply font to
            font: The font to apply
        """
        try:
            # Apply font to current widget
            widget.setFont(font)

            # Apply font to all child widgets
            for child in widget.findChildren(QWidget):
                child.setFont(font)

        except Exception as e:
            self.logger.debug("Could not apply font to widget: %s", e)

    def fix_ui_visibility(self, widget: QWidget) -> None:
        """
        Fix UI visibility issues by ensuring all text widgets are visible and properly styled.
        This addresses the problem where widgets exist but are not visible to the user.

        Args:
            widget: The main widget to fix visibility for
        """
        try:
            # Fix QLabel widgets - only ensure visibility
            labels = widget.findChildren(QLabel)
            for label in labels:
                label.setVisible(True)

            # Fix QCheckBox widgets - only ensure visibility
            checkboxes = widget.findChildren(QCheckBox)
            for checkbox in checkboxes:
                checkbox.setVisible(True)

            # Fix QPushButton widgets - only ensure visibility
            buttons = widget.findChildren(QPushButton)
            for button in buttons:
                button.setVisible(True)

            # Fix QLineEdit widgets - only ensure visibility
            line_edits = widget.findChildren(QLineEdit)
            for line_edit in line_edits:
                line_edit.setVisible(True)

            self.logger.info(
                "UI visibility fixed: %d labels, %d checkboxes, %d buttons, %d line edits",
                len(labels),
                len(checkboxes),
                len(buttons),
                len(line_edits),
            )

        except Exception as e:
            self.logger.error("Failed to fix UI visibility: %s", e)

    def setup_axis_controls(self, axis_combos: Dict[str, QComboBox]) -> None:
        """
        Initialize the axis control comboboxes with available options.

        Args:
            axis_combos: Dictionary containing axis combo boxes
        """
        try:
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
                "Temp",  # PT100 data is in 'Temp' column
            ]

            # Setup Y1 and Y2 axis combos
            for axis_name in ["y1_axis_combo", "y2_axis_combo"]:
                if axis_name in axis_combos and axis_combos[axis_name] is not None:
                    axis_combos[axis_name].addItems(sensor_options)
                    if axis_name == "y1_axis_combo":
                        axis_combos[axis_name].setCurrentText("NTC01")
                    else:  # y2_axis_combo
                        axis_combos[axis_name].setCurrentText("Temp")  # PT100 data is in 'Temp' column

            # X axis options (time-based)
            time_options = ["Seconds", "Minutes", "Hours"]
            if "x_axis_combo" in axis_combos and axis_combos["x_axis_combo"] is not None:
                axis_combos["x_axis_combo"].addItems(time_options)
                axis_combos["x_axis_combo"].setCurrentText("Seconds")

            self.logger.debug("Axis controls setup completed")

        except Exception as e:
            self.logger.error("Failed to setup axis controls: %s", e)

    def reset_ui_widgets(self, widgets: Dict[str, Any]) -> None:
        """
        Reset UI widgets to their default state.

        Args:
            widgets: Dictionary containing widget references
        """
        try:
            # Reset data metrics widgets
            metrics_widgets = [
                "mean_hp_power_value",
                "max_v_accu_value",
                "tilt_status_value",
                "mean_press_value",
            ]

            for widget_name in metrics_widgets:
                if widget_name in widgets and widgets[widget_name]:
                    widgets[widget_name].setText("-")

            # Reset project info widgets
            if "cruise_info_label" in widgets and widgets["cruise_info_label"]:
                widgets["cruise_info_label"].setText("Project: -")

            if "location_info_label" in widgets and widgets["location_info_label"]:
                widgets["location_info_label"].setText("Location: -")

            if (
                "location_comment_value" in widgets
                and widgets["location_comment_value"]
            ):
                widgets["location_comment_value"].setText("-")

            if (
                "location_sensorstring_value" in widgets
                and widgets["location_sensorstring_value"]
            ):
                widgets["location_sensorstring_value"].setText("-")

            if "location_subcon_spin" in widgets and widgets["location_subcon_spin"]:
                widgets["location_subcon_spin"].setValue(0.0)

            self.logger.debug("UI widgets reset to default state")

        except Exception as e:
            self.logger.error("Failed to reset UI widgets: %s", e)

    def get_available_fonts(self) -> list[str]:
        """
        Get list of available fonts on the current system.

        Returns:
            List of available font family names
        """
        try:
            return QFont.families()
        except Exception as e:
            self.logger.error("Could not get available fonts: %s", e)
            return []

    def test_font_availability(self, font_name: str) -> bool:
        """
        Test if a specific font is available on the system.

        Args:
            font_name: Name of the font to test

        Returns:
            True if font is available, False otherwise
        """
        try:
            available_fonts = self.get_available_fonts()
            return font_name in available_fonts
        except Exception as e:
            self.logger.error("Could not test font availability: %s", e)
            return False

    def update_label_pixmap(self, label: QLabel, style_info: Dict[str, Any]):
        """
        Update a QLabel with a pixmap showing the styled line.

        Args:
            label: The QLabel to update
            style_info: Style information (color, line_style, line_width)
        """
        # Get label dimensions
        width = label.width()
        height = label.height()

        if width <= 0 or height <= 0:
            # If dimensions are not set yet, use default values
            width = 30
            height = 16

        # Create pixmap
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)  # Transparent background

        # Paint the line
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        color = QColor(style_info.get('color', '#000000'))
        line_style_str = style_info.get('line_style', '-')
        line_width = style_info.get('line_width', 1.5)

        qt_line_style = Qt.PenStyle.SolidLine
        if line_style_str == '--':
            qt_line_style = Qt.PenStyle.DashLine
        elif line_style_str == ':':
            qt_line_style = Qt.PenStyle.DotLine
        elif line_style_str == '-.':
            qt_line_style = Qt.PenStyle.DashDotLine

        pen = QPen(color, line_width)
        pen.setStyle(qt_line_style)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        y_center = height / 2
        painter.drawLine(2, int(y_center), width - 2, int(y_center))

        painter.end()

        # Set pixmap on label
        label.setPixmap(pixmap)
        label.setScaledContents(True)  # Scale pixmap to label size

        self.logger.debug(f"Updated pixmap for label with style: {style_info}")

    def setup_label_indicator(self, label: QLabel, style_info: Dict[str, Any]) -> QLabel:
        """
        Set up a QLabel as a style indicator with automatic resize handling.

        Args:
            label: The QLabel to set up
            style_info: Initial style information

        Returns:
            The configured QLabel
        """
        # Store style info on the label
        label._style_info = style_info

        # Set initial pixmap
        self.update_label_pixmap(label, style_info)

        # Handle resize events
        original_resize_event = label.resizeEvent

        def styled_resize_event(event):
            if original_resize_event:
                original_resize_event(event)
            # Update pixmap when label is resized
            if hasattr(label, '_style_info'):
                self.update_label_pixmap(label, label._style_info)

        label.resizeEvent = styled_resize_event

        self.logger.debug(f"Set up label indicator with initial style: {style_info}")
        return label
