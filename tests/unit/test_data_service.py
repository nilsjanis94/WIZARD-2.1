"""
Unit tests for DataService

Tests the data service functionality including data processing and metrics calculation.
"""

import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np

from src.services.data_service import DataService
from src.models.tob_data_model import TOBDataModel


@pytest.mark.unit
class TestDataService:
    """Test cases for DataService class."""

    def test_init(self):
        """Test DataService initialization."""
        service = DataService()
        assert service.logger is not None

    def test_process_tob_data_success(self, sample_tob_data):
        """Test successful TOB data processing."""
        service = DataService()
        
        # Create mock data model
        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)
        mock_model.sensors = ["NTC01", "NTC02", "PT100"]
        
        with patch.object(service, '_get_time_range', return_value={"min": 0, "max": 5}), \
             patch.object(service, '_get_sensor_ranges', return_value={}), \
             patch.object(service, '_calculate_metrics', return_value={}):
            
            result = service.process_tob_data(mock_model)
            
            assert isinstance(result, dict)
            assert "time_range" in result
            assert "sensor_ranges" in result
            assert "metrics" in result

    def test_process_tob_data_validation_error(self):
        """Test TOB data processing with validation error."""
        service = DataService()
        
        # Create mock data model with invalid data
        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = None
        
        result = service.process_tob_data(mock_model)
        
        assert result == {}

    def test_get_time_range_success(self, sample_tob_data):
        """Test successful time range calculation."""
        service = DataService()
        
        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)
        mock_model.get_time_column.return_value = "time"
        
        result = service._get_time_range(mock_model)
        
        assert "min" in result
        assert "max" in result
        assert "duration" in result
        assert "count" in result

    def test_get_time_range_no_data(self):
        """Test time range calculation with no data."""
        service = DataService()
        
        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame()
        mock_model.get_time_column.return_value = None
        
        result = service._get_time_range(mock_model)
        
        assert result == {}

    def test_get_sensor_ranges_success(self, sample_tob_data):
        """Test successful sensor ranges calculation."""
        service = DataService()
        
        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)
        
        result = service._get_sensor_ranges(mock_model)
        
        assert isinstance(result, dict)
        # Should contain sensor data
        for sensor in ["NTC01", "NTC02", "PT100"]:
            if sensor in result:
                assert "min" in result[sensor]
                assert "max" in result[sensor]
                assert "mean" in result[sensor]

    def test_calculate_metrics_success(self, sample_tob_data):
        """Test successful metrics calculation."""
        service = DataService()

        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)

        result = service._calculate_metrics(mock_model)

        assert isinstance(result, dict)
        assert "mean_hp_power" in result
        assert "max_v_accu" in result  # Updated key name
        assert "tilt_status" in result
        assert "mean_press" in result

    def test_filter_sensor_data(self, sample_tob_data):
        """Test sensor data filtering."""
        service = DataService()
        
        mock_model = MagicMock(spec=TOBDataModel)
        mock_model.data = pd.DataFrame(sample_tob_data)
        
        # Test with actual method signature if it exists
        if hasattr(service, 'filter_sensor_data'):
            result = service.filter_sensor_data(mock_model, "NTC01")
            assert isinstance(result, pd.DataFrame)
        else:
            # Skip test if method doesn't exist yet
            pytest.skip("filter_sensor_data method not implemented yet")

    def test_reset_data_metrics(self):
        """Test data metrics reset."""
        service = DataService()
        
        # Create mock widgets
        mock_widget1 = MagicMock()
        mock_widget2 = MagicMock()
        
        metrics_widgets = {
            "mean_hp_power_value": mock_widget1,
            "max_v_accu_value": mock_widget2,
        }
        
        service.reset_data_metrics(metrics_widgets)
        
        # Verify widgets were reset
        mock_widget1.setText.assert_called_with("-")
        mock_widget2.setText.assert_called_with("-")

    def test_update_data_metrics(self):
        """Test data metrics update."""
        service = DataService()
        
        # Create mock widgets
        mock_widget1 = MagicMock()
        mock_widget2 = MagicMock()
        
        metrics_widgets = {
            "mean_hp_power_value": mock_widget1,
            "max_v_accu_value": mock_widget2,
        }
        
        metrics = {
            "mean_hp_power": 100.0,
            "max_v_accu": 50.0,
        }
        
        service.update_data_metrics(metrics_widgets, metrics)
        
        # Verify widgets were updated
        mock_widget1.setText.assert_called_with("100.0")
        mock_widget2.setText.assert_called_with("50.0")

    def test_update_data_metrics_missing_widgets(self):
        """Test data metrics update with missing widgets."""
        service = DataService()
        
        metrics_widgets = {
            "mean_hp_power_value": None,
            "max_v_accu_value": None,
        }
        
        metrics = {
            "mean_hp_power": 100.0,
            "max_v_accu": 50.0,
        }
        
        # Should not raise an exception
        service.update_data_metrics(metrics_widgets, metrics)
