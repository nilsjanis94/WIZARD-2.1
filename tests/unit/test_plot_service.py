"""
Unit tests for the PlotService module.

This module contains comprehensive unit tests for the PlotService class,
including tests for plot widget creation, sensor styling, and data visualization.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QWidget

from src.services.plot_service import PlotService, PlotWidget


class TestPlotService:
    """Test cases for PlotService class."""

    def test_init(self):
        """Test PlotService initialization."""
        service = PlotService()
        assert service is not None
        assert hasattr(service, 'plot_style_service')
        assert service.plot_style_service is not None
        # Test that we can get styles
        style = service.get_sensor_style('NTC01')
        assert 'color' in style
        assert 'line_style' in style
        assert 'line_width' in style

    def test_create_plot_widget(self):
        """Test plot widget creation."""
        service = PlotService()
        parent = MagicMock(spec=QWidget)
        
        with patch('src.services.plot_service.PlotWidget') as mock_widget_class:
            mock_widget = MagicMock()
            mock_widget_class.return_value = mock_widget
            
            result = service.create_plot_widget(parent)
            
            assert result == mock_widget
            mock_widget_class.assert_called_once_with(parent, service)

    def test_get_sensor_color_ntc(self):
        """Test color assignment for NTC sensors."""
        service = PlotService()

        # Test NTC01 (group 1-5: black)
        color = service.get_sensor_color('NTC01')
        assert color == '#000000'  # Black

        # Test NTC22 (group 19-22: dark red)
        color = service.get_sensor_color('NTC22')
        assert color == '#8B0000'  # Dark Red
        
        # Test NTC with invalid number (should use default style)
        color = service.get_sensor_color('NTC99')
        assert color == '#1f77b4'  # Default fallback color

    def test_get_sensor_color_pt100(self):
        """Test color assignment for PT100 sensor (mapped to 'Temp' column)."""
        service = PlotService()

        color = service.get_sensor_color('Temp')  # PT100 data is in 'Temp' column
        assert color == '#FFFF00'  # PT100 yellow color

    def test_get_sensor_color_unknown(self):
        """Test color assignment for unknown sensor."""
        service = PlotService()

        color = service.get_sensor_color('UNKNOWN')
        assert color == '#1f77b4'  # Default fallback color

    def test_get_line_style_ntc(self):
        """Test line style for NTC sensors."""
        service = PlotService()

        style = service.get_line_style('NTC01')
        assert style == '--'  # NTC01 uses dashed lines (first in repeating pattern)

    def test_get_line_style_pt100(self):
        """Test line style for PT100 sensor (mapped to 'Temp' column)."""
        service = PlotService()

        style = service.get_line_style('Temp')  # PT100 data is in 'Temp' column
        assert style == '-'  # PT100 uses solid lines

    def test_get_line_width_ntc(self):
        """Test line width for NTC sensors."""
        service = PlotService()

        width = service.get_line_width('NTC01')
        assert width == 1.5  # NTC sensors use 1.5 width

    def test_get_line_width_pt100(self):
        """Test line width for PT100 sensor (mapped to 'Temp' column)."""
        service = PlotService()

        width = service.get_line_width('Temp')  # PT100 data is in 'Temp' column
        assert width == 2.0  # PT100 uses thicker lines (2.0)

    def test_format_time_axis_empty(self):
        """Test time axis formatting with empty data."""
        service = PlotService()
        import pandas as pd
        
        empty_series = pd.Series([], dtype=float)
        time_values, time_labels = service.format_time_axis(empty_series)
        
        assert len(time_values) == 0
        assert len(time_labels) == 0

    def test_format_time_axis_with_data(self):
        """Test time axis formatting with data."""
        service = PlotService()
        import pandas as pd
        import numpy as np
        
        time_data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        time_values, time_labels = service.format_time_axis(time_data)

        assert len(time_values) == 5
        # For 5 data points, step = max(1, 5 // 10) = 1, so every point gets a label
        assert len(time_labels) == 5
        assert time_labels[0] == "1.0s"  # New format with seconds unit

    def test_format_time_axis_minutes(self):
        """Test time axis formatting with minutes unit."""
        service = PlotService()
        import pandas as pd

        time_data = pd.Series([60.0, 120.0, 180.0])  # 1, 2, 3 minutes in seconds
        time_values, time_labels = service.format_time_axis(time_data, "Minutes")

        assert len(time_values) == 3
        assert time_values[0] == 1.0  # 60 seconds = 1 minute
        assert time_values[1] == 2.0  # 120 seconds = 2 minutes
        assert time_labels[0] == "1.0min"

    def test_format_time_axis_hours(self):
        """Test time axis formatting with hours unit."""
        service = PlotService()
        import pandas as pd

        time_data = pd.Series([3600.0, 7200.0])  # 1, 2 hours in seconds
        time_values, time_labels = service.format_time_axis(time_data, "Hours")

        assert len(time_values) == 2
        assert time_values[0] == 1.0  # 3600 seconds = 1 hour
        assert time_values[1] == 2.0  # 7200 seconds = 2 hours
        assert time_labels[0] == "1.0h"


    def test_calculate_plot_limits_empty(self):
        """Test plot limits calculation with empty data."""
        service = PlotService()
        import pandas as pd
        
        empty_series = pd.Series([], dtype=float)
        min_limit, max_limit = service.calculate_plot_limits(empty_series)
        
        assert min_limit == 0.0
        assert max_limit == 1.0

    def test_calculate_plot_limits_with_data(self):
        """Test plot limits calculation with data."""
        service = PlotService()
        import pandas as pd
        
        data = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        min_limit, max_limit = service.calculate_plot_limits(data)
        
        assert min_limit < 1.0  # Should be less than min due to margin
        assert max_limit > 5.0  # Should be greater than max due to margin

    def test_calculate_plot_limits_constant_data(self):
        """Test plot limits calculation with constant data."""
        service = PlotService()
        import pandas as pd
        
        data = pd.Series([5.0, 5.0, 5.0, 5.0])
        min_limit, max_limit = service.calculate_plot_limits(data)
        
        assert min_limit < 5.0
        assert max_limit > 5.0


    # Note: update_y1_limits and update_y2_limits are implemented in PlotWidget, not PlotService
    # because they require canvas operations that are not available in PlotService


# Note: PlotWidget tests are skipped as they require PyQt6 widgets
# which are difficult to mock in unit tests. Integration tests would
# be more appropriate for testing the PlotWidget functionality.
