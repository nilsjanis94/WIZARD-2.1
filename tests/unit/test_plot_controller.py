"""
Unit tests for PlotController.

Tests the plot controller functionality including sensor selection,
axis management, and signal emission.
"""

from unittest.mock import MagicMock, Mock

import pytest

from src.controllers.plot_controller import PlotController
from src.models.tob_data_model import TOBDataModel
from src.services.plot_service import PlotService
from src.services.plot_style_service import PlotStyleService


class TestPlotController:
    """Test cases for PlotController."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        plot_service = Mock(spec=PlotService)
        plot_style_service = Mock(spec=PlotStyleService)
        return plot_service, plot_style_service

    @pytest.fixture
    def plot_controller(self, mock_services):
        """Create a PlotController instance for testing."""
        plot_service, plot_style_service = mock_services
        return PlotController(plot_service, plot_style_service)

    @pytest.fixture
    def sample_tob_data(self):
        """Create sample TOB data for testing."""
        data_model = Mock(spec=TOBDataModel)
        data_model.sensors = ["NTC01", "NTC02", "PT100"]
        # Create a mock data object that supports len()
        mock_data = Mock()
        mock_data.__len__ = Mock(return_value=3)
        data_model.data = mock_data
        data_model.get_sensor_data = Mock(return_value=[1, 2, 3])
        return data_model

    def test_initialization(self, plot_controller, mock_services):
        """Test that PlotController initializes correctly."""
        plot_service, plot_style_service = mock_services

        assert plot_controller.plot_service == plot_service
        assert plot_controller.plot_style_service == plot_style_service
        assert plot_controller.current_tob_data is None
        assert plot_controller.selected_sensors == []
        assert "x" in plot_controller.axis_limits
        assert "y1" in plot_controller.axis_limits
        assert "y2" in plot_controller.axis_limits

    def test_update_plot_data(self, plot_controller, sample_tob_data):
        """Test updating plot data."""
        # Mock the signal emission
        plot_controller.plot_updated = Mock()

        plot_controller.update_plot_data(sample_tob_data)

        assert plot_controller.current_tob_data == sample_tob_data
        # Should auto-select NTC sensors (first 22, but we only have 2)
        assert "NTC01" in plot_controller.selected_sensors
        assert "NTC02" in plot_controller.selected_sensors
        # PT100 might not be included in auto-selection depending on logic
        plot_controller.plot_updated.emit.assert_called_once()

    def test_update_selected_sensors(self, plot_controller):
        """Test updating selected sensors."""
        plot_controller.sensors_updated = Mock()

        selected_sensors = ["NTC01", "PT100"]
        plot_controller.update_selected_sensors(selected_sensors)

        assert plot_controller.selected_sensors == selected_sensors
        plot_controller.sensors_updated.emit.assert_called_once_with(selected_sensors)

    def test_update_axis_limits(self, plot_controller):
        """Test updating axis limits."""
        plot_controller.axis_limits_changed = Mock()

        plot_controller.update_axis_limits("x", 0, 100)

        assert plot_controller.axis_limits["x"]["min"] == 0
        assert plot_controller.axis_limits["x"]["max"] == 100
        plot_controller.axis_limits_changed.emit.assert_called_once_with("x", 0, 100)

    def test_get_plot_info(self, plot_controller, sample_tob_data):
        """Test getting plot information."""
        plot_controller.current_tob_data = sample_tob_data
        plot_controller.selected_sensors = ["NTC01"]

        info = plot_controller.get_plot_info()

        assert info["current_data"] is True
        assert info["selected_sensors"] == ["NTC01"]
        assert "axis_limits" in info
        assert info["data_points"] == 3

    def test_get_available_sensors(self, plot_controller, sample_tob_data):
        """Test getting available sensors."""
        plot_controller.current_tob_data = sample_tob_data

        sensors = plot_controller.get_available_sensors()

        assert sensors == ["NTC01", "NTC02", "PT100"]

    def test_get_available_sensors_no_data(self, plot_controller):
        """Test getting available sensors when no data is loaded."""
        sensors = plot_controller.get_available_sensors()

        assert sensors == []

    def test_handle_sensor_selection_changed(self, plot_controller):
        """Test handling sensor selection changes."""
        # Mock main window with current checkbox states
        main_window = Mock()
        checkbox_ntc01 = Mock(isChecked=Mock(return_value=True))
        checkbox_ntc02 = Mock(
            isChecked=Mock(return_value=False)
        )  # Currently unselected
        checkbox_pt100 = Mock(isChecked=Mock(return_value=True))

        main_window.ntc_checkboxes = {
            "NTC01": checkbox_ntc01,
            "NTC02": checkbox_ntc02,
            "PT100": checkbox_pt100,
        }

        plot_controller.sensors_updated = Mock()

        # Simulate selecting NTC02 (was unselected, now selected)
        plot_controller.handle_sensor_selection_changed("NTC02", True, main_window)

        # Should include all currently checked sensors: NTC01, PT100, and now NTC02
        expected_selection = ["NTC01", "PT100", "NTC02"]
        assert plot_controller.selected_sensors == expected_selection
        plot_controller.sensors_updated.emit.assert_called_once_with(expected_selection)

    def test_update_sensor_checkboxes(self, plot_controller, sample_tob_data):
        """Test updating sensor checkboxes in UI."""
        main_window = Mock()
        checkbox_mock = Mock()
        main_window.ntc_checkboxes = {"NTC01": checkbox_mock}

        plot_controller.current_tob_data = sample_tob_data
        plot_controller.selected_sensors = ["NTC01"]

        plot_controller.update_sensor_checkboxes(main_window)

        # Verify checkbox methods were called
        checkbox_mock.setVisible.assert_called_with(True)
        checkbox_mock.setEnabled.assert_called_with(True)
        checkbox_mock.setChecked.assert_called_with(True)

    def test_update_sensor_checkboxes_no_data(self, plot_controller):
        """Test updating sensor checkboxes when no data is available."""
        main_window = Mock()
        main_window.ntc_checkboxes = {}

        plot_controller.update_sensor_checkboxes(main_window)

        # Should not crash and log warning
        assert True  # If we get here, no exception was raised
