"""
Plot Style Service for WIZARD-2.1

Centralized style management for all plot elements.
Provides consistent styling across plots and UI indicators.
"""

import logging
from typing import Dict, Any


class PlotStyleService:
    """
    Centralized service for managing plot styles.

    Defines fixed styles for all sensors to ensure consistency
    between plot visualization and UI indicators.
    """

    def __init__(self):
        """Initialize the plot style service with predefined styles."""
        self.logger = logging.getLogger(__name__)

        # Define fixed color palette for NTC sensors
        self.ntc_colors = [
            '#1f77b4',  # blue
            '#ff7f0e',  # orange
            '#2ca02c',  # green
            '#d62728',  # red
            '#9467bd',  # purple
            '#8c564b',  # brown
            '#e377c2',  # pink
            '#7f7f7f',  # gray
            '#bcbd22',  # olive
            '#17becf',  # cyan
            '#aec7e8',  # light blue
            '#ffbb78',  # light orange
            '#98df8a',  # light green
            '#ff9896',  # light red
            '#c5b0d5',  # light purple
            '#c49c94',  # light brown
            '#f7b6d3',  # light pink
            '#c7c7c7',  # light gray
            '#dbdb8d',  # light olive
            '#9edae5',  # light cyan
            '#ad494a',  # dark red
            '#8c6d31'   # dark brown
        ]

        # Fixed styles for all sensors
        self._sensor_styles = self._define_sensor_styles()

        self.logger.info("PlotStyleService initialized with fixed sensor styles")

    def get_sensor_style(self, sensor_name: str) -> Dict[str, Any]:
        """
        Get the fixed style for a specific sensor.

        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'Temp')

        Returns:
            Dictionary with 'color', 'line_style', and 'line_width'
        """
        return self._sensor_styles.get(sensor_name, self._get_default_style())

    def get_all_sensor_styles(self) -> Dict[str, Dict[str, Any]]:
        """
        Get styles for all defined sensors.

        Returns:
            Dictionary mapping all sensor names to their styles
        """
        return self._sensor_styles.copy()

    def _define_sensor_styles(self) -> Dict[str, Dict[str, Any]]:
        """
        Define fixed styles for all sensors based on user-defined color and pattern groups.

        Color groups:
        - NTC 1-5: Black
        - NTC 6-8: Gray
        - NTC 9-12: Dark Blue
        - NTC 13-16: Light Blue
        - NTC 17-18: Red
        - NTC 19-22: Dark Red
        - PT100: Yellow

        Line style pattern (repeating every 5 NTCs):
        - NTC x1: '-' (solid)
        - NTC x2: '--' (dashed)
        - NTC x3: ':' (dotted)
        - NTC x4: '-.' (dash-dot)
        - NTC x5: '-' (solid)

        Returns:
            Dictionary mapping sensor names to style configurations
        """
        # Line style pattern that repeats every 5 NTCs
        line_patterns = ['-', '--', ':', '-.', '-']

        styles = {}

        # NTC sensors with user-defined color groups and line patterns
        for i in range(1, 23):
            sensor_name = f"NTC{i:02d}"

            # Determine color based on NTC number groups
            if 1 <= i <= 5:
                color = '#000000'  # Black
            elif 6 <= i <= 8:
                color = '#808080'  # Gray
            elif 9 <= i <= 12:
                color = '#000080'  # Dark Blue
            elif 13 <= i <= 16:
                color = '#4169E1'  # Light Blue
            elif 17 <= i <= 18:
                color = '#FF0000'  # Red
            elif 19 <= i <= 22:
                color = '#8B0000'  # Dark Red
            else:
                color = '#000000'  # Default black

            # Determine line style based on position in repeating pattern
            line_style_index = i % len(line_patterns)  # 1-based index for correct offset
            line_style = line_patterns[line_style_index]

            styles[sensor_name] = {
                'color': color,
                'line_style': line_style,
                'line_width': 1.5
            }

        # PT100/Temp sensor - user specified yellow and solid line
        styles['Temp'] = {
            'color': '#FFFF00',  # Yellow
            'line_style': '-',   # Solid line as requested
            'line_width': 2.0
        }

        # Time axis (if needed)
        styles['Time'] = {
            'color': '#2c3e50',  # dark blue-gray
            'line_style': '-',
            'line_width': 1.0
        }

        return styles

    def _get_default_style(self) -> Dict[str, Any]:
        """
        Get default fallback style.

        Returns:
            Default style for unknown sensors
        """
        return {
            'color': '#1f77b4',  # default blue
            'line_style': '-',
            'line_width': 1.5
        }
