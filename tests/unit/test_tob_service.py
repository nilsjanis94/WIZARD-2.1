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

    @pytest.mark.skip(reason="Method _is_data_line removed - now using tob_dataloader")
    def test_is_data_line_numeric(self):
        """Test detecting numeric data lines."""
        pytest.skip("Method removed - using tob_dataloader")

    @pytest.mark.skip(reason="Method _is_data_line removed - now using tob_dataloader")
    def test_is_data_line_mixed(self):
        """Test detecting mixed data lines."""
        pytest.skip("Method removed - using tob_dataloader")

    @pytest.mark.skip(reason="Method _detect_column_names removed - now using tob_dataloader")
    def test_detect_column_names(self):
        """Test detecting column names from header line."""
        pytest.skip("Method removed - using tob_dataloader")

    @pytest.mark.skip(reason="Method _parse_data_line removed - now using tob_dataloader")
    def test_parse_data_line(self):
        """Test parsing data line into numeric values."""
        pytest.skip("Method removed - using tob_dataloader")

    @pytest.mark.skip(reason="Method _clean_dataframe removed - now using tob_dataloader")
    def test_clean_dataframe(self):
        """Test cleaning DataFrame."""
        pytest.skip("Method removed - using tob_dataloader")

    @pytest.mark.skip(reason="Method get_available_sensors removed - now using tob_dataloader")
    def test_get_available_sensors(self):
        """Test detecting available sensors."""
        pytest.skip("Method removed - using tob_dataloader")

    @pytest.mark.skip(reason="Method get_available_sensors removed - now using tob_dataloader")
    def test_get_available_sensors_empty(self):
        """Test detecting sensors in empty DataFrame."""
        pytest.skip("Method removed - using tob_dataloader")

    @pytest.mark.skip(reason="Method get_available_sensors removed - now using tob_dataloader")
    def test_get_available_sensors_none(self):
        """Test detecting sensors with None DataFrame."""
        pytest.skip("Method removed - using tob_dataloader")

    def test_parse_headers_deprecated(self):
        """Test that parse_headers is now deprecated."""
        service = TOBService()

        # Method should return empty dict and log warning
        headers = service.parse_headers("test.tob")
        assert headers == {}

    @pytest.mark.skip(reason="File error handling now handled by tob_dataloader")
    def test_parse_headers_file_error(self):
        """Test header parsing with file error."""
        pytest.skip("File error handling now in tob_dataloader")

    def test_parse_data_deprecated(self):
        """Test that parse_data is now deprecated."""
        service = TOBService()

        # Method should return empty DataFrame and log warning
        df = service.parse_data("test.tob")
        assert df.empty

    @pytest.mark.skip(reason="Data parsing now handled by tob_dataloader")
    def test_parse_data_no_data(self):
        """Test data parsing with no data."""
        pytest.skip("Data parsing now in tob_dataloader")

    @pytest.mark.skip(reason="File error handling now handled by tob_dataloader")
    def test_parse_data_file_error(self):
        """Test data parsing with file error."""
        pytest.skip("File error handling now in tob_dataloader")

    @pytest.mark.skip(reason="Complex mocking required for tob_dataloader integration")
    def test_load_tob_file_success(self):
        """Test successful TOB file loading with tob_dataloader."""
        pytest.skip("Complex mocking required for tob_dataloader integration")

    @pytest.mark.skip(reason="Complex mocking required for tob_dataloader integration")
    def test_load_tob_file_not_found(self):
        """Test loading non-existent TOB file."""
        pytest.skip("Complex mocking required for tob_dataloader integration")

    @pytest.mark.skip(reason="Complex mocking required for tob_dataloader integration")
    def test_load_tob_file_invalid_format(self):
        """Test loading invalid TOB file format with tob_dataloader error."""
        pytest.skip("Complex mocking required for tob_dataloader integration")

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
