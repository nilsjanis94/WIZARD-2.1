from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.controllers.main_controller import MainController
from src.models.tob_data_model import TOBDataModel
from src.services.data_service import DataService
from src.services.tob_service import TOBService


@pytest.mark.integration
class TestTOBIntegration:
    """Test cases for TOB file processing integration."""

    @pytest.fixture
    def mock_controller(self, qt_app):
        """Create a mock controller for testing."""
        # qt_app fixture already skips in headless environment, so this will be skipped too
        with patch("src.views.main_window.MainWindow") as mock_window:
            mock_window.return_value = MagicMock()
            controller = MainController()
            yield controller

    def test_controller_initialization(self, mock_controller):
        """Test MainController initialization with TOB services."""
        controller = mock_controller

        assert controller.tob_service is not None
        assert controller.data_service is not None
        assert controller.tob_data_model is None  # Initially no data loaded
        assert controller.main_window is not None

    def test_open_tob_file_success(self, mock_controller):
        """Test successful TOB file opening."""
        controller = mock_controller

        # Mock the TOB service
        mock_tob_data = MagicMock(spec=TOBDataModel)
        mock_tob_data.sensors = ["NTC01", "NTC02", "PT100"]
        mock_tob_data.get_metadata.return_value = {
            "file_path": "test.tob",
            "data_points": 100,
            "sensors": ["NTC01", "NTC02", "PT100"],
        }
        mock_tob_data.data = MagicMock()

        with patch.object(
            controller.tob_service, "validate_tob_file", return_value=True
        ), patch.object(
            controller.tob_service, "load_tob_file", return_value=mock_tob_data
        ), patch.object(
            controller.data_service, "process_tob_data", return_value={}
        ), patch.object(
            controller.data_service, "_calculate_metrics", return_value={}
        ):

            controller.open_tob_file("test.tob")

            assert controller.tob_data_model is not None
            assert controller.tob_data_model.sensors == ["NTC01", "NTC02", "PT100"]

    def test_open_tob_file_validation_error(self, mock_controller):
        """Test TOB file opening with validation error."""
        controller = mock_controller

        with patch.object(
            controller.tob_service, "validate_tob_file", return_value=False
        ):
            controller.open_tob_file("invalid.tob")

            # Should not load data if validation fails
            assert controller.tob_data_model is None

    def test_open_tob_file_load_error(self, mock_controller):
        """Test TOB file opening with load error."""
        controller = mock_controller

        with patch.object(
            controller.tob_service, "validate_tob_file", return_value=True
        ), patch.object(
            controller.tob_service,
            "load_tob_file",
            side_effect=FileNotFoundError("File not found"),
        ):

            controller.open_tob_file("nonexistent.tob")

            # Should handle error gracefully
            assert controller.tob_data_model is None

    def test_update_sensor_selection(self, mock_controller):
        """Test sensor selection updates."""
        controller = mock_controller

        # Mock TOB data
        mock_tob_data = MagicMock(spec=TOBDataModel)
        mock_tob_data.sensors = ["NTC01", "NTC02", "PT100"]
        controller.tob_data_model = mock_tob_data

        # Test sensor selection
        controller.update_sensor_selection("NTC01", True)
        controller.update_sensor_selection("NTC02", False)

        # Should not raise any errors
        assert True

    def test_update_axis_auto_mode(self, mock_controller):
        """Test axis auto mode updates."""
        controller = mock_controller

        # Test axis mode updates
        controller.update_axis_auto_mode("y1", True)
        controller.update_axis_auto_mode("y2", False)
        controller.update_axis_auto_mode("x", True)

        # Should not raise any errors
        assert True

    def test_get_current_tob_data(self, mock_controller):
        """Test getting current TOB data."""
        controller = mock_controller

        # Initially no data
        assert controller.get_current_tob_data() is None

        # After setting data
        mock_tob_data = MagicMock(spec=TOBDataModel)
        controller.tob_data_model = mock_tob_data

        assert controller.get_current_tob_data() is mock_tob_data

    def test_file_load_progress_signals(self, mock_controller):
        """Test file load progress signals."""
        controller = mock_controller

        # Test file loading with progress signals
        with patch.object(
            controller.tob_service, "validate_tob_file", return_value=True
        ), patch.object(
            controller.tob_service, "load_tob_file"
        ) as mock_load, patch.object(
            controller.data_service, "process_tob_data"
        ) as mock_process:

            mock_load.return_value = MagicMock()
            mock_process.return_value = {"mean_hp_power": 100.0}

            controller.open_tob_file("test.tob")

            # Verify the method was called (progress signals are internal)
            mock_load.assert_called_once()

    def test_file_load_error_signals(self, mock_controller):
        """Test file load error signals."""
        controller = mock_controller

        with patch.object(
            controller.tob_service, "validate_tob_file", return_value=False
        ):
            controller.open_tob_file("invalid.tob")

            # Should handle error gracefully (error signals are internal)
            # The method should complete without raising exceptions

    def test_data_processing_integration(self, mock_controller):
        """Test integration between TOB service and data service."""
        controller = mock_controller

        # Mock TOB data
        mock_tob_data = MagicMock(spec=TOBDataModel)
        mock_tob_data.sensors = ["NTC01", "NTC02"]
        mock_tob_data.data = MagicMock()
        mock_tob_data.get_metadata.return_value = {
            "file_path": "test.tob",
            "data_points": 50,
        }

        with patch.object(
            controller.tob_service, "validate_tob_file", return_value=True
        ), patch.object(
            controller.tob_service, "load_tob_file", return_value=mock_tob_data
        ), patch.object(
            controller.data_service,
            "process_tob_data",
            return_value={"processed": True},
        ), patch.object(
            controller.data_service, "_calculate_metrics", return_value={"metric": 123}
        ):

            controller.open_tob_file("test.tob")

            # Should process data through data service
            assert controller.tob_data_model is not None

    def test_view_update_integration(self, mock_controller):
        """Test integration with view updates."""
        controller = mock_controller

        # Mock TOB data
        mock_tob_data = MagicMock(spec=TOBDataModel)
        mock_tob_data.sensors = ["NTC01", "PT100"]
        mock_tob_data.get_metadata.return_value = {
            "file_path": "test.tob",
            "data_points": 100,
        }
        mock_tob_data.data = MagicMock()

        with patch.object(
            controller.tob_service, "validate_tob_file", return_value=True
        ), patch.object(
            controller.tob_service, "load_tob_file", return_value=mock_tob_data
        ), patch.object(
            controller.data_service, "process_tob_data", return_value={}
        ), patch.object(
            controller.data_service, "_calculate_metrics", return_value={}
        ), patch.object(
            controller.main_window, "update_project_info"
        ) as mock_update_project, patch.object(
            controller.main_window, "update_data_metrics"
        ) as mock_update_metrics, patch.object(
            controller.main_window.ui_state_manager, "show_plot_mode"
        ) as mock_show_plot:

            controller.open_tob_file("test.tob")

            # Should update view components
            mock_update_project.assert_called_once()
            mock_update_metrics.assert_called_once()
            mock_show_plot.assert_called_once()

    def test_error_handling_integration(self, mock_controller):
        """Test error handling integration."""
        controller = mock_controller

        with patch.object(
            controller.tob_service, "validate_tob_file", return_value=True
        ), patch.object(
            controller.tob_service, "load_tob_file", side_effect=Exception("Test error")
        ), patch.object(
            controller.error_handler, "handle_error"
        ) as mock_handle_error:

            controller.open_tob_file("test.tob")

            # Should handle error through error handler
            mock_handle_error.assert_called_once()

    def test_sensor_checkbox_update(self, mock_controller):
        """Test sensor checkbox updates."""
        controller = mock_controller

        # Mock TOB data with sensors
        mock_tob_data = MagicMock(spec=TOBDataModel)
        mock_tob_data.sensors = ["NTC01", "NTC02", "PT100"]
        mock_tob_data.get_pt100_sensor.return_value = "PT100"
        controller.tob_data_model = mock_tob_data

        # Mock main window checkboxes
        mock_checkbox = MagicMock()
        controller.main_window.ntc_checkboxes = {
            "NTC01": mock_checkbox,
            "NTC02": mock_checkbox,
            "NTC03": mock_checkbox,
        }
        controller.main_window.pt100_checkbox = mock_checkbox

        controller._update_sensor_checkboxes()

        # Should update checkboxes based on available sensors
        assert mock_checkbox.setVisible.called
        assert mock_checkbox.setEnabled.called
        assert mock_checkbox.setChecked.called
