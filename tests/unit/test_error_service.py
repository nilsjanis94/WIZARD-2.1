import logging
from unittest.mock import MagicMock, patch

import pytest

from src.services.error_service import ErrorService


@pytest.fixture
def error_service() -> ErrorService:
    service = ErrorService()
    logger = logging.getLogger("test.error_service")
    service.logger = logger
    return service


def test_handle_error_shows_dialog(error_service: ErrorService):
    with patch("src.services.error_service.QMessageBox") as mock_box:
        error = ValueError("bad input")
        error_service.handle_error(error, parent=None)

        mock_box.assert_called_once()
        instance = mock_box.return_value
        instance.setIcon.assert_called_once()
        instance.setWindowTitle.assert_called_once_with("Error")
        instance.setText.assert_called_once()
        instance.exec.assert_called_once()


def test_handle_error_logging_failure(error_service: ErrorService):
    error_service._show_error_dialog = MagicMock(side_effect=Exception("dialog fail"))
    error_service.handle_error(RuntimeError("boom"))


def test_handle_warning_shows_dialog(error_service: ErrorService):
    with patch("src.services.error_service.QMessageBox") as mock_box:
        error_service.handle_warning("careful", parent=None)
        instance = mock_box.return_value
        instance.setIcon.assert_called_once()
        instance.setWindowTitle.assert_called_once_with("Warning")
        instance.setText.assert_called_once_with("careful")
        instance.exec.assert_called_once()


def test_handle_info_shows_dialog(error_service: ErrorService):
    with patch("src.services.error_service.QMessageBox") as mock_box:
        error_service.handle_info("hello", parent=None)
        instance = mock_box.return_value
        instance.setIcon.assert_called_once()
        instance.setWindowTitle.assert_called_once_with("Information")
        instance.setText.assert_called_once_with("hello")
        instance.exec.assert_called_once()


def test_create_user_message_custom():
    service = ErrorService()
    message = service._create_user_message("SomeError", "details")
    assert message == "An error occurred: details"


def test_log_error_with_context(caplog):
    service = ErrorService()
    caplog.set_level(logging.ERROR)

    service.log_error(RuntimeError("oops"), context="During save")

    assert any("During save" in record.message for record in caplog.records)
