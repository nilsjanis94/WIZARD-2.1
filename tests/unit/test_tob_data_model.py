import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock

from src.models.tob_data_model import TOBDataModel


@pytest.mark.unit
class TestTOBDataModel:
    """Test cases for TOBDataModel class."""

    def test_init_default(self):
        """Test TOBDataModel initialization with default values."""
        model = TOBDataModel()
        
        assert model.headers == {}
        assert model.data is None
        assert model.file_path is None
        assert model.file_size is None
        assert model.data_points is None
        assert model.sensors == []

    def test_init_with_data(self):
        """Test TOBDataModel initialization with data."""
        data = pd.DataFrame({
            'Time': [1, 2, 3],
            'NTC01': [20.0, 21.0, 22.0],
            'PT100': [20.5, 21.5, 22.5]
        })
        
        model = TOBDataModel(
            file_path="test.tob",
            file_size=1024,
            headers={"Version": "1.0"},
            data=data,
            sensors=["NTC01", "PT100"],
            data_points=3
        )
        
        assert model.file_path == "test.tob"
        assert model.file_size == 1024
        assert model.headers == {"Version": "1.0"}
        assert model.data is not None
        assert model.sensors == ["NTC01", "PT100"]
        assert model.data_points == 3

    def test_get_sensor_data_existing(self):
        """Test getting data for existing sensor."""
        data = pd.DataFrame({
            'Time': [1, 2, 3],
            'NTC01': [20.0, 21.0, 22.0],
            'PT100': [20.5, 21.5, 22.5]
        })
        
        model = TOBDataModel(data=data, sensors=["NTC01", "PT100"])
        
        ntc_data = model.get_sensor_data("NTC01")
        assert ntc_data is not None
        assert ntc_data.iloc[0] == 20.0
        assert len(ntc_data) == 3

    def test_get_sensor_data_nonexistent(self):
        """Test getting data for non-existent sensor."""
        data = pd.DataFrame({
            'Time': [1, 2, 3],
            'NTC01': [20.0, 21.0, 22.0]
        })
        
        model = TOBDataModel(data=data, sensors=["NTC01"])
        
        result = model.get_sensor_data("NTC02")
        assert result is None

    def test_get_sensor_data_no_data(self):
        """Test getting sensor data when no data is loaded."""
        model = TOBDataModel()
        
        result = model.get_sensor_data("NTC01")
        assert result is None

    def test_get_ntc_sensors(self):
        """Test getting NTC sensor names."""
        model = TOBDataModel(sensors=["NTC01", "NTC02", "PT100", "NTC03"])
        
        ntc_sensors = model.get_ntc_sensors()
        assert ntc_sensors == ["NTC01", "NTC02", "NTC03"]

    def test_get_ntc_sensors_empty(self):
        """Test getting NTC sensors when none exist."""
        model = TOBDataModel(sensors=["PT100", "Other"])
        
        ntc_sensors = model.get_ntc_sensors()
        assert ntc_sensors == []

    def test_get_pt100_sensor(self):
        """Test getting PT100 sensor name."""
        model = TOBDataModel(sensors=["NTC01", "PT100", "NTC02"])
        
        pt100 = model.get_pt100_sensor()
        assert pt100 == "PT100"

    def test_get_pt100_sensor_none(self):
        """Test getting PT100 sensor when none exists."""
        model = TOBDataModel(sensors=["NTC01", "NTC02"])
        
        pt100 = model.get_pt100_sensor()
        assert pt100 is None

    def test_get_time_column_existing(self):
        """Test getting time column name."""
        data = pd.DataFrame({
            'Time': [1, 2, 3],
            'NTC01': [20.0, 21.0, 22.0]
        })
        
        model = TOBDataModel(data=data)
        
        time_col_name = model.get_time_column_name()
        assert time_col_name == "Time"

    def test_get_time_column_timestamp(self):
        """Test getting timestamp column name."""
        data = pd.DataFrame({
            'TIMESTAMP': [1, 2, 3],
            'NTC01': [20.0, 21.0, 22.0]
        })
        
        model = TOBDataModel(data=data)
        
        time_col_name = model.get_time_column_name()
        assert time_col_name == "TIMESTAMP"

    def test_get_time_column_none(self):
        """Test getting time column when none exists."""
        data = pd.DataFrame({
            'NTC01': [20.0, 21.0, 22.0],
            'PT100': [20.5, 21.5, 22.5]
        })
        
        model = TOBDataModel(data=data)
        
        time_col_name = model.get_time_column_name()
        assert time_col_name is None

    def test_get_data_range_with_data(self):
        """Test getting data range with valid data."""
        data = pd.DataFrame({
            'Time': [1, 2, 3, 4, 5],
            'NTC01': [20.0, 21.0, 22.0, 23.0, 24.0],
            'PT100': [20.5, 21.5, 22.5, 23.5, 24.5]
        })
        
        model = TOBDataModel(data=data, sensors=["NTC01", "PT100"])
        
        ranges = model.get_data_range()
        
        assert "time_range" in ranges
        assert "sensor_ranges" in ranges
        assert ranges["time_range"]["min"] == 1
        assert ranges["time_range"]["max"] == 5
        assert "NTC01" in ranges["sensor_ranges"]
        assert ranges["sensor_ranges"]["NTC01"]["min"] == 20.0
        assert ranges["sensor_ranges"]["NTC01"]["max"] == 24.0

    def test_get_data_range_no_data(self):
        """Test getting data range with no data."""
        model = TOBDataModel()
        
        ranges = model.get_data_range()
        assert ranges == {}

    def test_get_metadata(self):
        """Test getting comprehensive metadata."""
        data = pd.DataFrame({
            'Time': [1, 2, 3],
            'NTC01': [20.0, 21.0, 22.0]
        })
        
        model = TOBDataModel(
            file_path="test.tob",
            file_size=1024,
            headers={"Version": "1.0"},
            data=data,
            sensors=["NTC01"],
            data_points=3
        )
        
        metadata = model.get_metadata()
        
        assert metadata["file_path"] == "test.tob"
        assert metadata["file_size"] == 1024
        assert metadata["data_points"] == 3
        assert metadata["sensors"] == ["NTC01"]
        assert metadata["headers"] == {"Version": "1.0"}
        assert metadata["data_shape"] == (3, 2)
        assert metadata["sensor_count"] == 1
        assert metadata["ntc_sensors"] == ["NTC01"]
        assert metadata["pt100_sensor"] is None

    def test_validate_data_integrity_valid(self):
        """Test data integrity validation with valid data."""
        data = pd.DataFrame({
            'Time': [1, 2, 3],
            'NTC01': [20.0, 21.0, 22.0],
            'PT100': [20.5, 21.5, 22.5]
        })
        
        model = TOBDataModel(data=data, sensors=["NTC01", "PT100"])
        
        validation = model.validate_data_integrity()
        
        assert validation["is_valid"] is True
        assert validation["data_quality"] == "good"
        assert len(validation["errors"]) == 0
        assert len(validation["warnings"]) == 0

    def test_validate_data_integrity_no_data(self):
        """Test data integrity validation with no data."""
        model = TOBDataModel()
        
        validation = model.validate_data_integrity()
        
        assert validation["is_valid"] is False
        assert validation["data_quality"] == "poor"
        assert "No data loaded" in validation["errors"]

    def test_validate_data_integrity_missing_values(self):
        """Test data integrity validation with missing values."""
        data = pd.DataFrame({
            'Time': [1, 2, 3],
            'NTC01': [20.0, np.nan, 22.0],
            'PT100': [20.5, 21.5, np.nan]
        })
        
        model = TOBDataModel(data=data, sensors=["NTC01", "PT100"])
        
        validation = model.validate_data_integrity()
        
        assert validation["is_valid"] is True
        assert validation["data_quality"] == "fair"
        assert len(validation["warnings"]) > 0
        assert "Missing data" in str(validation["warnings"])

    def test_validate_data_integrity_duplicate_timestamps(self):
        """Test data integrity validation with duplicate timestamps."""
        data = pd.DataFrame({
            'Time': [1, 1, 3],  # Duplicate timestamp
            'NTC01': [20.0, 21.0, 22.0]
        })
        
        model = TOBDataModel(data=data, sensors=["NTC01"])
        
        validation = model.validate_data_integrity()
        
        assert validation["is_valid"] is True
        assert validation["data_quality"] == "fair"
        assert len(validation["warnings"]) > 0
        assert "Duplicate timestamps" in str(validation["warnings"])

    def test_validate_data_integrity_empty_dataset(self):
        """Test data integrity validation with empty dataset."""
        data = pd.DataFrame()
        
        model = TOBDataModel(data=data)
        
        validation = model.validate_data_integrity()
        
        assert validation["is_valid"] is False
        assert validation["data_quality"] == "poor"
        assert "Empty dataset" in validation["errors"]

    def test_get_sensor_statistics(self):
        """Test getting sensor statistics."""
        data = pd.DataFrame({
            'NTC01': [20.0, 21.0, 22.0, 23.0, 24.0],
            'PT100': [20.5, 21.5, 22.5, 23.5, 24.5]
        })
        
        model = TOBDataModel(data=data, sensors=["NTC01", "PT100"])
        
        stats = model.get_sensor_statistics()
        
        assert "NTC01" in stats
        assert "PT100" in stats
        assert stats["NTC01"]["mean"] == 22.0
        assert stats["NTC01"]["min"] == 20.0
        assert stats["NTC01"]["max"] == 24.0
        assert stats["NTC01"]["count"] == 5

    def test_get_sensor_statistics_no_data(self):
        """Test getting sensor statistics with no data."""
        model = TOBDataModel()
        
        stats = model.get_sensor_statistics()
        assert stats == {}

    def test_get_sensor_statistics_missing_sensor(self):
        """Test getting sensor statistics with missing sensor data."""
        data = pd.DataFrame({
            'NTC01': [20.0, 21.0, 22.0],
            'Other': [1, 2, 3]
        })
        
        model = TOBDataModel(data=data, sensors=["NTC01", "MissingSensor"])
        
        stats = model.get_sensor_statistics()
        
        assert "NTC01" in stats
        assert "MissingSensor" not in stats
        assert len(stats) == 1
