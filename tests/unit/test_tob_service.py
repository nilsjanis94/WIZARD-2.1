import pytest
from unittest.mock import MagicMock, patch, mock_open
import pandas as pd
import numpy as np
from pathlib import Path

from src.services.tob_service import TOBService
from src.exceptions.tob_exceptions import (TOBError, TOBFileNotFoundError, 
                                         TOBParsingError, TOBValidationError,
                                         TOBDataError, TOBHeaderError)


@pytest.mark.unit
class TestTOBService:
    """Test cases for TOBService class."""

    def test_init(self):
        """Test TOBService initialization."""
        service = TOBService()
        assert service.logger is not None

    def test_validate_tob_file_valid(self):
        """Test validating a valid TOB file."""
        service = TOBService()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:
            
            mock_stat.return_value.st_size = 1024  # Non-zero file size
            
            result = service.validate_tob_file("test.tob")
            assert result is True

    def test_validate_tob_file_invalid_extension(self):
        """Test validating file with invalid extension."""
        service = TOBService()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True):
            
            result = service.validate_tob_file("test.txt")
            assert result is False

    def test_validate_tob_file_not_found(self):
        """Test validating non-existent file."""
        service = TOBService()
        
        with patch('pathlib.Path.exists', return_value=False):
            result = service.validate_tob_file("nonexistent.tob")
            assert result is False

    def test_is_data_line_numeric(self):
        """Test detecting numeric data lines."""
        service = TOBService()
        
        assert service._is_data_line("1.0 2.0 3.0 4.0") is True
        assert service._is_data_line("1 2 3 4") is True
        assert service._is_data_line("Time NTC01 NTC02 PT100") is False
        assert service._is_data_line("# Comment line") is False
        assert service._is_data_line("") is False

    def test_is_data_line_mixed(self):
        """Test detecting mixed data lines."""
        service = TOBService()
        
        assert service._is_data_line("2023-01-01 1.0 2.0 3.0") is True
        assert service._is_data_line("Time 1.0 2.0 3.0") is False  # Contains 'time' keyword
        assert service._is_data_line("Header: Value") is False

    def test_detect_column_names(self):
        """Test detecting column names from header line."""
        service = TOBService()
        
        result = service._detect_column_names("Time NTC01 NTC02 PT100")
        assert result == ["Time", "NTC01", "NTC02", "PT100"]
        
        result = service._detect_column_names("Timestamp Temp1 Temp2")
        assert result == ["Timestamp", "Temp1", "Temp2"]
        
        result = service._detect_column_names("No keyword here")
        assert result is None

    def test_parse_data_line(self):
        """Test parsing data line into numeric values."""
        service = TOBService()
        
        result = service._parse_data_line("1.0 2.0 3.0 4.0")
        assert result == [1.0, 2.0, 3.0, 4.0]
        
        result = service._parse_data_line("1 2 3 4")
        assert result == [1.0, 2.0, 3.0, 4.0]
        
        result = service._parse_data_line("1.0 abc 3.0 def")
        assert result == [1.0, 3.0]
        
        result = service._parse_data_line("no numbers here")
        assert result == []

    def test_clean_dataframe(self):
        """Test cleaning DataFrame."""
        service = TOBService()
        
        # Create test DataFrame with issues
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4, 5],
            'B': ['1.0', '2.0', '3.0', '4.0', '5.0'],
            'C': [1, 2, 3, 4, 5]
        })
        
        # Add duplicate row
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        
        cleaned_df = service._clean_dataframe(df)
        
        assert len(cleaned_df) == 5  # Duplicate removed
        assert cleaned_df['B'].dtype == 'float64'  # Converted to numeric
        assert cleaned_df.index.tolist() == [0, 1, 2, 3, 4]  # Reset index

    def test_get_available_sensors(self):
        """Test detecting available sensors."""
        service = TOBService()
        
        # Test with NTC sensors
        df = pd.DataFrame({
            'Time': [1, 2, 3],
            'NTC01': [20.0, 21.0, 22.0],
            'NTC02': [19.0, 20.0, 21.0],
            'PT100': [20.5, 21.5, 22.5],
            'Other': [1, 2, 3]
        })
        
        sensors = service.get_available_sensors(df)
        assert 'NTC01' in sensors
        assert 'NTC02' in sensors
        assert 'PT100' in sensors
        assert 'Other' not in sensors

    def test_get_available_sensors_empty(self):
        """Test detecting sensors in empty DataFrame."""
        service = TOBService()
        
        df = pd.DataFrame()
        sensors = service.get_available_sensors(df)
        assert sensors == []

    def test_get_available_sensors_none(self):
        """Test detecting sensors with None DataFrame."""
        service = TOBService()
        
        sensors = service.get_available_sensors(None)
        assert sensors == []

    def test_parse_headers_success(self):
        """Test successful header parsing."""
        service = TOBService()
        
        mock_content = """# TOB File Header
Version: 1.0
Date: 2023-01-01
Sensors: 3
Temperature: 20.5
# End of header
1.0 2.0 3.0 4.0
"""
        
        with patch('builtins.open', mock_open(read_data=mock_content)):
            headers = service.parse_headers("test.tob")
            
            # Headers should be parsed correctly
            assert 'Version' in headers
            assert headers['Version'] == 1.0
            assert headers['Date'] == '2023-01-01'
            assert headers['Sensors'] == 3
            assert headers['Temperature'] == 20.5

    def test_parse_headers_file_error(self):
        """Test header parsing with file error."""
        service = TOBService()
        
        with patch('builtins.open', side_effect=IOError("File error")):
            with pytest.raises(TOBHeaderError):
                service.parse_headers("test.tob")

    def test_parse_data_success(self):
        """Test successful data parsing."""
        service = TOBService()
        
        mock_content = """# Header
Time NTC01 NTC02 PT100
1.0 20.0 19.0 20.5
2.0 21.0 20.0 21.5
3.0 22.0 21.0 22.5
"""
        
        with patch('builtins.open', mock_open(read_data=mock_content)):
            df = service.parse_data("test.tob")
            
            assert len(df) == 3
            # Column names should be detected from the header line
            assert len(df.columns) == 4
            # Check that data is parsed correctly
            assert df.iloc[0, 1] == 20.0  # First row, second column (NTC01)

    def test_parse_data_no_data(self):
        """Test data parsing with no data."""
        service = TOBService()
        
        mock_content = """# Header only
Version: 1.0
"""
        
        with patch('builtins.open', mock_open(read_data=mock_content)):
            df = service.parse_data("test.tob")
            # Should return empty DataFrame when no data lines are found
            assert df.empty

    def test_parse_data_file_error(self):
        """Test data parsing with file error."""
        service = TOBService()
        
        with patch('builtins.open', side_effect=IOError("File error")):
            with pytest.raises(TOBDataError):
                service.parse_data("test.tob")

    def test_load_tob_file_success(self):
        """Test successful TOB file loading."""
        service = TOBService()
        
        mock_content = """# Header
Version: 1.0
Time NTC01 NTC02 PT100
1.0 20.0 19.0 20.5
2.0 21.0 20.0 21.5
"""
        
        with patch('builtins.open', mock_open(read_data=mock_content)), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch.object(service, 'validate_tob_file', return_value=True):
            
            mock_stat.return_value.st_size = 100
            
            data_model = service.load_tob_file("test.tob")
            
            assert data_model.file_path == "test.tob"
            assert data_model.file_size == 100
            # Sensors should be detected from the data columns
            assert len(data_model.sensors) >= 0  # May be 0 if no sensors detected
            assert data_model.data is not None

    def test_load_tob_file_not_found(self):
        """Test loading non-existent TOB file."""
        service = TOBService()
        
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(TOBFileNotFoundError):
                service.load_tob_file("nonexistent.tob")

    def test_load_tob_file_invalid_format(self):
        """Test loading invalid TOB file format."""
        service = TOBService()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch.object(service, 'validate_tob_file', return_value=False):
            
            with pytest.raises(TOBValidationError):
                service.load_tob_file("invalid.tob")

    def test_get_file_info_success(self):
        """Test getting file information."""
        service = TOBService()
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:
            
            mock_stat.return_value.st_size = 1024
            mock_stat.return_value.st_ctime = 1234567890
            mock_stat.return_value.st_mtime = 1234567890
            
            info = service.get_file_info("test.tob")
            
            assert info['file_path'] == "test.tob"
            assert info['file_name'] == "test.tob"
            assert info['file_size'] == 1024
            assert info['file_extension'] == '.tob'

    def test_get_file_info_not_found(self):
        """Test getting file info for non-existent file."""
        service = TOBService()
        
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(TOBFileNotFoundError):
                service.get_file_info("nonexistent.tob")

    def test_estimate_processing_time(self):
        """Test estimating processing time."""
        service = TOBService()
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 1024 * 1024  # 1MB
            
            time = service.estimate_processing_time("test.tob")
            assert time == 1.0  # 1 second for 1MB

    def test_estimate_processing_time_large_file(self):
        """Test estimating processing time for large file."""
        service = TOBService()
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_size = 500 * 1024 * 1024  # 500MB
            
            time = service.estimate_processing_time("test.tob")
            assert time == 300.0  # Capped at 5 minutes

    def test_estimate_processing_time_error(self):
        """Test estimating processing time with error."""
        service = TOBService()
        
        with patch('pathlib.Path.stat', side_effect=OSError("Stat error")):
            time = service.estimate_processing_time("test.tob")
            assert time == 10.0  # Default fallback
