"""
Unit tests for AnalyticsService.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock

from src.services.analytics_service import AnalyticsService
from src.models.tob_data_model import TOBDataModel


class TestAnalyticsService:
    """Test cases for AnalyticsService."""

    def test_init(self):
        """Test AnalyticsService initialization."""
        service = AnalyticsService()
        assert service is not None

    def test_calculate_metrics_success(self, sample_tob_data):
        """Test successful metrics calculation."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)

        result = service.calculate_metrics(mock_model)

        assert isinstance(result, dict)
        assert "mean_hp_power" in result
        assert "max_v_accu" in result
        assert "tilt_status" in result
        assert "mean_press" in result

    def test_calculate_mean_hp_power(self, sample_tob_data):
        """Test mean heat pulse power calculation."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)
        mock_model.get_ntc_sensors.return_value = ["NTC01", "NTC02"]
        mock_model.get_sensor_data.return_value = pd.Series([20.5, 21.0, 21.5, 22.0, 22.5, 23.0])

        result = service._calculate_mean_hp_power(mock_model)

        assert isinstance(result, float)
        assert result >= 0.0

    def test_calculate_max_vaccu(self, sample_tob_data):
        """Test max vacuum calculation."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)

        result = service._calculate_max_vaccu(mock_model)

        assert isinstance(result, float)
        assert 0.0 <= result <= 100.0  # Vacuum should be percentage

    def test_calculate_tilt_status(self, sample_tob_data):
        """Test tilt status calculation."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)
        mock_model.get_ntc_sensors.return_value = ["NTC01", "NTC02"]
        mock_model.get_sensor_data.return_value = pd.Series([20.5, 21.0, 21.5, 22.0, 22.5, 23.0])

        result = service._calculate_tilt_status(mock_model)

        assert isinstance(result, str)
        assert result in ["OK", "Warning", "Error", "Unknown"]

    def test_calculate_mean_press(self, sample_tob_data):
        """Test mean pressure calculation."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)

        result = service._calculate_mean_press(mock_model)

        assert isinstance(result, float)
        assert result >= 0.0

    def test_calculate_metrics_no_data(self):
        """Test metrics calculation with no data."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = None

        result = service.calculate_metrics(mock_model)

        assert isinstance(result, dict)
        assert len(result) == 0  # Should return empty dict for no data

    def test_calculate_mean_hp_power_no_ntc_sensors(self):
        """Test HP power calculation with no NTC sensors."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame({"Temp": [20.0, 21.0]})
        mock_model.get_ntc_sensors.return_value = []

        result = service._calculate_mean_hp_power(mock_model)

        assert result == 0.0

    def test_calculate_max_vaccu_no_voltage_data(self):
        """Test vacuum calculation with no voltage data."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame({"NTC01": [20.0, 21.0]})

        result = service._calculate_max_vaccu(mock_model)

        assert result == 0.0

    def test_calculate_tilt_status_no_ntc_sensors(self):
        """Test tilt status calculation with no NTC sensors."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame({"Temp": [20.0, 21.0]})
        mock_model.get_ntc_sensors.return_value = []

        result = service._calculate_tilt_status(mock_model)

        assert result == "Unknown"

    def test_calculate_mean_press_no_pressure_data(self):
        """Test pressure calculation with no pressure data."""
        service = AnalyticsService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame({"NTC01": [20.0, 21.0]})

        result = service._calculate_mean_press(mock_model)

        assert result == 0.0
