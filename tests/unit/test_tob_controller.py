"""
Unit tests for TOBController.

Tests the TOB controller functionality including file loading,
data processing, and metrics calculation.
"""

from unittest.mock import MagicMock, Mock

import pytest

from src.controllers.tob_controller import TOBController
from src.models.tob_data_model import TOBDataModel
from src.services.data_service import DataService
from src.services.tob_service import TOBService


class TestTOBController:
    """Test cases for TOBController."""

    @pytest.fixture
    def mock_services(self):
        """Create mock services for testing."""
        tob_service = Mock(spec=TOBService)
        data_service = Mock(spec=DataService)
        return tob_service, data_service

    @pytest.fixture
    def tob_controller(self, mock_services):
        """Create a TOBController instance for testing."""
        tob_service, data_service = mock_services
        return TOBController(tob_service, data_service)

    @pytest.fixture
    def sample_tob_data(self):
        """Create sample TOB data for testing."""
        data_model = Mock(spec=TOBDataModel)
        data_model.data = Mock()
        data_model.sensors = ["NTC01", "NTC02"]
        return data_model

    def test_initialization(self, tob_controller, mock_services):
        """Test that TOBController initializes correctly."""
        tob_service, data_service = mock_services

        assert tob_controller.tob_service == tob_service
        assert tob_controller.data_service == data_service

    def test_load_tob_file_success(self, tob_controller, mock_services):
        """Test successful TOB file loading."""
        tob_service, data_service = mock_services
        sample_data = Mock(spec=TOBDataModel)

        # Mock successful validation and loading
        tob_service.validate_tob_file.return_value = True
        tob_service.load_tob_file.return_value = sample_data

        tob_controller.file_loaded = Mock()

        tob_controller.load_tob_file("test.tob")

        tob_service.validate_tob_file.assert_called_once_with("test.tob")
        tob_service.load_tob_file.assert_called_once_with("test.tob")
        tob_controller.file_loaded.emit.assert_called_once_with(sample_data)

    def test_load_tob_file_validation_failure(self, tob_controller, mock_services):
        """Test TOB file loading when validation fails."""
        tob_service, data_service = mock_services

        tob_service.validate_tob_file.return_value = False

        tob_controller.error_occurred = Mock()

        tob_controller.load_tob_file("invalid.tob")

        tob_service.validate_tob_file.assert_called_once_with("invalid.tob")
        tob_service.load_tob_file.assert_not_called()
        tob_controller.error_occurred.emit.assert_called_once()
        assert "Invalid TOB file" in tob_controller.error_occurred.emit.call_args[0][1]

    def test_load_tob_file_loading_failure(self, tob_controller, mock_services):
        """Test TOB file loading when loading fails."""
        tob_service, data_service = mock_services

        tob_service.validate_tob_file.return_value = True
        tob_service.load_tob_file.return_value = None

        tob_controller.error_occurred = Mock()

        tob_controller.load_tob_file("test.tob")

        tob_controller.error_occurred.emit.assert_called_once()
        assert (
            "Failed to load TOB file"
            in tob_controller.error_occurred.emit.call_args[0][1]
        )

    def test_process_tob_data_success(
        self, tob_controller, mock_services, sample_tob_data
    ):
        """Test successful TOB data processing."""
        tob_service, data_service = mock_services

        processed_data = {"processed": True}
        data_service.process_tob_data.return_value = processed_data

        tob_controller.data_processed = Mock()

        tob_controller.process_tob_data(sample_tob_data)

        data_service.process_tob_data.assert_called_once_with(sample_tob_data)
        tob_controller.data_processed.emit.assert_called_once_with(processed_data)

    def test_process_tob_data_failure(
        self, tob_controller, mock_services, sample_tob_data
    ):
        """Test TOB data processing failure."""
        tob_service, data_service = mock_services

        data_service.process_tob_data.return_value = None

        tob_controller.error_occurred = Mock()

        tob_controller.process_tob_data(sample_tob_data)

        tob_controller.error_occurred.emit.assert_called_once()
        assert (
            "Failed to process TOB data"
            in tob_controller.error_occurred.emit.call_args[0][1]
        )

    def test_calculate_metrics_success(
        self, tob_controller, mock_services, sample_tob_data
    ):
        """Test successful metrics calculation."""
        tob_service, data_service = mock_services

        metrics = {"mean_hp_power": 10.5, "max_vaccu": 12.0}
        data_service._calculate_metrics.return_value = metrics

        tob_controller.metrics_calculated = Mock()

        result = tob_controller.calculate_metrics(sample_tob_data)

        data_service._calculate_metrics.assert_called_once_with(sample_tob_data)
        tob_controller.metrics_calculated.emit.assert_called_once_with(metrics)
        assert result == metrics

    def test_calculate_metrics_empty_result(
        self, tob_controller, mock_services, sample_tob_data
    ):
        """Test metrics calculation returning empty result."""
        tob_service, data_service = mock_services

        data_service._calculate_metrics.return_value = {}

        tob_controller.error_occurred = Mock()

        result = tob_controller.calculate_metrics(sample_tob_data)

        # Empty result should not trigger error signal, just return empty dict
        tob_controller.error_occurred.emit.assert_not_called()
        assert result == {}

    def test_get_sensor_data_success(self, tob_controller, sample_tob_data):
        """Test successful sensor data retrieval."""
        sensor_data = [1, 2, 3, 4, 5]
        sample_tob_data.get_sensor_data.return_value = sensor_data

        result = tob_controller.get_sensor_data(sample_tob_data, "NTC01")

        sample_tob_data.get_sensor_data.assert_called_once_with("NTC01")
        assert result == sensor_data

    def test_get_sensor_data_not_found(self, tob_controller, sample_tob_data):
        """Test sensor data retrieval when sensor not found."""
        sample_tob_data.get_sensor_data.return_value = None

        result = tob_controller.get_sensor_data(sample_tob_data, "NTC99")

        assert result is None

    def test_get_sensor_data_no_data_model(self, tob_controller):
        """Test sensor data retrieval when no data model is available."""
        result = tob_controller.get_sensor_data(None, "NTC01")

        assert result is None

    def test_get_available_sensors(self, tob_controller, sample_tob_data):
        """Test getting available sensors."""
        result = tob_controller.get_available_sensors(sample_tob_data)

        assert result == ["NTC01", "NTC02"]

    def test_get_available_sensors_no_data(self, tob_controller):
        """Test getting available sensors when no data is available."""
        result = tob_controller.get_available_sensors(None)

        assert result == []

    def test_validate_tob_file(self, tob_controller, mock_services):
        """Test TOB file validation."""
        tob_service, data_service = mock_services

        tob_service.validate_tob_file.return_value = True

        result = tob_controller.validate_tob_file("test.tob")

        tob_service.validate_tob_file.assert_called_once_with("test.tob")
        assert result is True

    def test_error_handling_in_methods(self, tob_controller, mock_services):
        """Test that methods handle exceptions properly."""
        tob_service, data_service = mock_services

        # Make validate_tob_file raise an exception
        tob_service.validate_tob_file.side_effect = Exception("Test error")

        tob_controller.error_occurred = Mock()

        result = tob_controller.validate_tob_file("test.tob")

        tob_controller.error_occurred.emit.assert_called_once()
        assert (
            "Error validating TOB file"
            in tob_controller.error_occurred.emit.call_args[0][1]
        )
        assert result is False
