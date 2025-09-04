"""
Pytest configuration and fixtures for WIZARD-2.1

This module provides shared fixtures and configuration for all tests.
"""

import logging
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator, Optional
from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtWidgets import QApplication

# Add src to Python path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from src.utils.logging_config import setup_logging


@pytest.fixture(scope="session")
def qt_app() -> Generator[QApplication, None, None]:
    """
    Provide a QApplication instance for the entire test session.
    
    This fixture ensures that PyQt6 widgets can be created during tests.
    """
    # Check if QApplication already exists
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    yield app
    
    # Cleanup is handled by pytest-qt


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """
    Provide a temporary directory for test files.
    
    The directory is automatically cleaned up after the test.
    """
    with tempfile.TemporaryDirectory() as temp_path:
        yield Path(temp_path)


@pytest.fixture
def mock_logger():
    """
    Provide a mock logger for testing.
    
    Useful when you want to test logging behavior without actual log output.
    """
    logger = MagicMock(spec=logging.Logger)
    logger.info = MagicMock()
    logger.debug = MagicMock()
    logger.warning = MagicMock()
    logger.error = MagicMock()
    logger.critical = MagicMock()
    return logger


@pytest.fixture
def test_logging_config():
    """
    Provide a test logging configuration.
    
    Sets up logging for tests with a temporary log directory.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override log directory for tests
        with patch('src.utils.logging_config.get_log_dir', return_value=temp_dir):
            setup_logging()
            yield temp_dir


@pytest.fixture
def sample_tob_data():
    """
    Provide sample TOB data for testing.
    
    Returns a dictionary with sample temperature sensor data.
    """
    return {
        "time": [0, 1, 2, 3, 4, 5],
        "NTC01": [20.5, 21.0, 21.5, 22.0, 22.5, 23.0],
        "NTC02": [19.8, 20.3, 20.8, 21.3, 21.8, 22.3],
        "PT100": [20.1, 20.6, 21.1, 21.6, 22.1, 22.6],
        "pressure": [1013.25, 1013.30, 1013.35, 1013.40, 1013.45, 1013.50],
        "battery_voltage": [12.0, 11.9, 11.8, 11.7, 11.6, 11.5],
    }


@pytest.fixture
def sample_project_data():
    """
    Provide sample project data for testing.
    
    Returns a dictionary with sample project information.
    """
    return {
        "name": "Test Project",
        "location": "Test Location",
        "comment": "Test comment",
        "sensor_string": "NTC01,NTC02,PT100",
        "subcon": 0.0,
        "created_at": "2024-01-01T00:00:00Z",
        "modified_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_file_system():
    """
    Provide a mock file system for testing.
    
    Useful for testing file operations without touching the actual file system.
    """
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('pathlib.Path.is_file') as mock_is_file, \
         patch('pathlib.Path.is_dir') as mock_is_dir, \
         patch('builtins.open', create=True) as mock_open:
        
        # Default behavior
        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_is_dir.return_value = False
        
        yield {
            'exists': mock_exists,
            'is_file': mock_is_file,
            'is_dir': mock_is_dir,
            'open': mock_open,
        }


@pytest.fixture
def mock_encryption():
    """
    Provide mock encryption functions for testing.
    
    Useful for testing encryption/decryption without actual cryptographic operations.
    """
    with patch('src.services.encryption_service.encrypt_data') as mock_encrypt, \
         patch('src.services.encryption_service.decrypt_data') as mock_decrypt:
        
        # Default behavior - return the same data
        mock_encrypt.side_effect = lambda data, key: f"encrypted_{data}"
        mock_decrypt.side_effect = lambda data, key: data.replace("encrypted_", "")
        
        yield {
            'encrypt': mock_encrypt,
            'decrypt': mock_decrypt,
        }


# Test markers for different test categories
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual components"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "ui: UI tests using pytest-qt"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "network: Tests requiring network access"
    )
    config.addinivalue_line(
        "markers", "file_io: Tests requiring file system access"
    )
    config.addinivalue_line(
        "markers", "encryption: Tests involving encryption/decryption"
    )
    config.addinivalue_line(
        "markers", "data_processing: Tests for data processing functions"
    )


# Skip tests if required dependencies are not available
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip tests based on available dependencies."""
    skip_qt = pytest.mark.skip(reason="PyQt6 not available")
    skip_crypto = pytest.mark.skip(reason="cryptography not available")
    
    for item in items:
        # Skip UI tests if PyQt6 is not available
        if "ui" in item.keywords and not hasattr(item, "qt_app"):
            item.add_marker(skip_qt)
        
        # Skip encryption tests if cryptography is not available
        if "encryption" in item.keywords:
            try:
                import cryptography
            except ImportError:
                item.add_marker(skip_crypto)
