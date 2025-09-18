"""
Unit tests for AnalyticsService.
"""

import pytest
import pandas as pd
import numpy as np
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
        """Test mean heat pulse power calculation from voltage/current data."""
        service = AnalyticsService()

        # Add Vheat and Iheat columns to sample data
        sample_data = sample_tob_data.copy()
        sample_data['Vheat'] = [0.005, 0.005, 0.005, 0.005, 0.005, 0.005]  # Constant low voltage
        sample_data['Iheat'] = [-0.002, -0.002, -0.002, 15.0, 15.0, 15.0]  # Some current pulses

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_data)

        result = service._calculate_mean_hp_power(mock_model)

        assert isinstance(result, float)
        assert result >= 0.0  # Should find some power from the current pulses

    def test_calculate_max_vaccu(self, sample_tob_data):
        """Test max battery voltage calculation."""
        service = AnalyticsService()

        # Add Vaccu column with battery voltage data
        sample_data = sample_tob_data.copy()
        sample_data['Vaccu'] = [23.5, 23.8, 24.0, 24.2, 24.1, 23.9]  # Battery voltage values

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_data)

        result = service._calculate_max_vaccu(mock_model)

        assert isinstance(result, float)
        assert result > 20.0  # Should be battery voltage (> 20V typical)

    def test_calculate_tilt_status(self, sample_tob_data):
        """Test tilt stability calculation from dedicated tilt sensors."""
        service = AnalyticsService()

        # Add tilt sensor columns
        sample_data = sample_tob_data.copy()
        sample_data['TiltX'] = [2.0, 2.1, 2.0, 2.2, 2.1, 2.0]  # Low variation
        sample_data['TiltY'] = [4.0, 4.1, 4.0, 4.2, 4.1, 4.0]  # Low variation
        sample_data['ACCz'] = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0]  # Very stable

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_data)

        result = service._calculate_tilt_status(mock_model)

        assert isinstance(result, float)
        assert not np.isnan(result)
        # With low variation in sensors, should be around 0.054 (mean std)
        assert 0.05 <= result <= 0.06

    def test_calculate_mean_press(self, sample_tob_data):
        """Test mean pressure calculation."""
        service = AnalyticsService()

        # Add Press column with pressure data
        sample_data = sample_tob_data.copy()
        sample_data['Press'] = [15.1, 15.2, 15.0, 15.3, 15.1, 15.2]  # Vacuum pressure values

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_data)

        result = service._calculate_mean_press(mock_model)

        assert isinstance(result, float)
        assert result > 0.0
        # Should be around 15.15 (mean of test values)
        assert 15.0 <= result <= 16.0

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
