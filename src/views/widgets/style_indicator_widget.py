"""
Style Indicator Widget for WIZARD-2.1

A custom QWidget that visually represents plot line styles and colors.
Used as legend indicators next to sensor checkboxes.
Also provides utility methods for updating QLabel pixmaps.
"""

import logging
from typing import Dict, Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt6.QtWidgets import QWidget, QLabel


class StyleIndicatorWidget(QWidget):
    """
    A custom QWidget to visually represent a sensor's line style and color.

    This widget acts as a legend indicator next to sensor checkboxes, showing
    the exact same line style and color that appears in the plot.
    """

    def __init__(self, sensor_name: str, style_info: Dict[str, Any], parent: QWidget = None):
        """
        Initialize the style indicator widget.

        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'Temp')
            style_info: Dictionary with 'color', 'line_style', and 'line_width'
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.sensor_name = sensor_name
        self._style_info = style_info

        # Fixed size for consistency
        self.setFixedSize(32, 16)

        self.logger.debug(f"StyleIndicatorWidget for {sensor_name} initialized with style: {style_info}")

    def update_style(self, style_info: Dict[str, Any]):
        """
        Update the style information for the indicator and trigger a repaint.

        Args:
            style_info: Dictionary with 'color', 'line_style', and 'line_width'
        """
        self._style_info = style_info
        self.update()  # Trigger repaint
        self.logger.debug(f"Style updated for {self.sensor_name}")

    def paintEvent(self, event):
        """
        Custom paint event to draw the line style and color.

        Draws a horizontal line in the center of the widget using the
        specified color, line style, and line width.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get style properties
        color = QColor(self._style_info.get('color', '#000000'))
        line_style_str = self._style_info.get('line_style', '-')
        line_width = self._style_info.get('line_width', 1.5)

        # Convert matplotlib line styles to Qt pen styles
        qt_line_style = Qt.PenStyle.SolidLine
        if line_style_str == '--':
            qt_line_style = Qt.PenStyle.DashLine
        elif line_style_str == ':':
            qt_line_style = Qt.PenStyle.DotLine
        elif line_style_str == '-.':
            qt_line_style = Qt.PenStyle.DashDotLine

        # Create and configure the pen
        pen = QPen(color, line_width)
        pen.setStyle(qt_line_style)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # Draw horizontal line in center of widget
        y_center = self.height() / 2
        painter.drawLine(2, int(y_center), self.width() - 2, int(y_center))

        painter.end()
