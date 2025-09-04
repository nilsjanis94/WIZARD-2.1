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
        assert hasattr(service, 'ntc_colors')
        assert hasattr(service, 'pt100_color')
        assert hasattr(service, 'time_color')
        assert len(service.ntc_colors) == 22  # NTC01 to NTC22

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
        
        # Test NTC01 (first color)
        color = service.get_sensor_color('NTC01')
        assert color == service.ntc_colors[0]
        
        # Test NTC22 (last color)
        color = service.get_sensor_color('NTC22')
        assert color == service.ntc_colors[21]
        
        # Test NTC with invalid number (should cycle through colors)
        color = service.get_sensor_color('NTC99')
        # NTC99 -> 99-1 = 98, 98 % 22 = 10, so should be colors[10]
        expected_index = (99 - 1) % len(service.ntc_colors)
        assert color == service.ntc_colors[expected_index]

    def test_get_sensor_color_pt100(self):
        """Test color assignment for PT100 sensor."""
        service = PlotService()
        
        color = service.get_sensor_color('PT100')
        assert color == service.pt100_color

    def test_get_sensor_color_unknown(self):
        """Test color assignment for unknown sensor."""
        service = PlotService()
        
        color = service.get_sensor_color('UNKNOWN')
        assert color == service.ntc_colors[0]  # Default to first NTC color

    def test_get_line_style_ntc(self):
        """Test line style for NTC sensors."""
        service = PlotService()
        
        style = service.get_line_style('NTC01')
        assert style == service.ntc_line_style

    def test_get_line_style_pt100(self):
        """Test line style for PT100 sensor."""
        service = PlotService()
        
        style = service.get_line_style('PT100')
        assert style == service.pt100_line_style

    def test_get_line_width_ntc(self):
        """Test line width for NTC sensors."""
        service = PlotService()
        
        width = service.get_line_width('NTC01')
        assert width == service.ntc_line_width

    def test_get_line_width_pt100(self):
        """Test line width for PT100 sensor."""
        service = PlotService()
        
        width = service.get_line_width('PT100')
        assert width == service.pt100_line_width

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
        assert time_labels[0] == "T0"

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


# Note: PlotWidget tests are skipped as they require PyQt6 widgets
# which are difficult to mock in unit tests. Integration tests would
# be more appropriate for testing the PlotWidget functionality.
