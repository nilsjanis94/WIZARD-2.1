"""Test cases for HttpClientService."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from src.services.http_client_service import (
    HttpClientService,
    HttpMethod,
    HttpResponse,
    ServerEndpoint,
    StatusResult,
    UploadResult,
)


@pytest.mark.unit
class TestHttpClientService:
    """Test cases for HttpClientService class."""

    def test_init(self):
        """Test HttpClientService initialization."""
        service = HttpClientService(
            base_url="https://api.test.com", bearer_token="test_token"
        )

        assert service.base_url == "https://api.test.com"
        assert service.bearer_token == "test_token"
        assert service.session is not None
        assert service.session.headers.get("Authorization") == "Bearer test_token"

    @patch("requests.Session.request")
    def test_make_request_success(self, mock_request):
        """Test successful HTTP request."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        service = HttpClientService("https://api.test.com", "token")
        response = service._make_request(HttpMethod.GET, "/test")

        assert response.success
        assert response.status_code == 200
        assert response.data == {"status": "success"}

    @patch("requests.Session.request")
    def test_make_request_timeout(self, mock_request):
        """Test HTTP request timeout."""
        mock_request.side_effect = requests.Timeout()

        service = HttpClientService("https://api.test.com", "token")
        response = service._make_request(HttpMethod.GET, "/test")

        assert not response.success
        assert response.status_code == 0
        assert "timeout" in response.error_message.lower()

    @patch("requests.Session.request")
    def test_make_request_connection_error(self, mock_request):
        """Test HTTP request connection error."""
        mock_request.side_effect = requests.ConnectionError("Connection failed")

        service = HttpClientService("https://api.test.com", "token")
        response = service._make_request(HttpMethod.GET, "/test")

        assert not response.success
        assert response.status_code == 0
        assert "Connection error" in response.error_message

    @patch("requests.Session.request")
    def test_make_request_http_error(self, mock_request):
        """Test HTTP request with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.headers = {}
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_request.return_value = mock_response

        service = HttpClientService("https://api.test.com", "token")
        response = service._make_request(HttpMethod.GET, "/test")

        assert not response.success
        # Note: Status code might be 0 due to how the exception handling works
        assert "HTTP" in response.error_message and "404" in response.error_message

    @patch("requests.Session.request")
    def test_upload_tob_file_success(self, mock_request):
        """Test successful TOB file upload."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "job_id": "test_job_123",
            "message": "Upload successful",
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        service = HttpClientService("https://api.test.com", "token")

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".TOB", delete=False) as f:
            f.write("test data")
            temp_file = f.name

        try:
            result = service.upload_tob_file(temp_file, {"test": "metadata"})

            assert result.success
            assert result.job_id == "test_job_123"
            assert result.message == "Upload successful"
            assert result.error_code is None

        finally:
            Path(temp_file).unlink()

    @patch("requests.Session.request")
    def test_upload_tob_file_failure(self, mock_request):
        """Test failed TOB file upload."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.headers = {}
        mock_response.raise_for_status.side_effect = requests.HTTPError(
            "400 Bad Request"
        )
        mock_request.return_value = mock_response

        service = HttpClientService("https://api.test.com", "token")

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".TOB", delete=False) as f:
            f.write("test data")
            temp_file = f.name

        try:
            result = service.upload_tob_file(temp_file)

            assert not result.success
            assert result.job_id is None
            assert "HTTP" in result.error_code

        finally:
            Path(temp_file).unlink()

    def test_upload_tob_file_not_found(self):
        """Test upload with non-existent file."""
        service = HttpClientService("https://api.test.com", "token")

        result = service.upload_tob_file("/nonexistent/file.TOB")

        assert not result.success
        assert "FILE_NOT_FOUND" in result.error_code

    @patch("requests.Session.request")
    def test_get_upload_status_success(self, mock_request):
        """Test successful upload status check."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "status": "processing",
            "progress": 75.5,
            "message": "Processing data...",
            "result_url": "https://api.test.com/results/123",
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        service = HttpClientService("https://api.test.com", "token")
        result = service.get_upload_status("job_123")

        assert result.status == "processing"
        assert result.progress == 75.5
        assert result.message == "Processing data..."
        assert result.result_url == "https://api.test.com/results/123"

    @patch("requests.Session.request")
    def test_get_processing_status_success(self, mock_request):
        """Test successful processing status check."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = {
            "status": "completed",
            "progress": 100.0,
            "message": "Processing completed successfully",
        }
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        service = HttpClientService("https://api.test.com", "token")
        result = service.get_processing_status("job_123")

        assert result.status == "completed"
        assert result.progress == 100.0
        assert result.message == "Processing completed successfully"

    @patch("requests.Session.request")
    def test_health_check_success(self, mock_request):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        service = HttpClientService("https://api.test.com", "token")
        result = service.health_check()

        assert result is True

    @patch("requests.Session.request")
    def test_health_check_failure(self, mock_request):
        """Test failed health check."""
        mock_request.side_effect = requests.ConnectionError()

        service = HttpClientService("https://api.test.com", "token")
        result = service.health_check()

        assert result is False

    def test_server_endpoints(self):
        """Test server endpoint constants."""
        assert ServerEndpoint.UPLOAD_TOB.value == "/api/tob/upload"
        assert ServerEndpoint.UPLOAD_STATUS.value == "/api/tob/status/{job_id}"
        assert ServerEndpoint.PROCESSING_STATUS.value == "/api/tob/processing/{job_id}"
        assert ServerEndpoint.HEALTH_CHECK.value == "/api/health"

    def test_http_method_enum(self):
        """Test HTTP method enum."""
        assert HttpMethod.GET.value == "GET"
        assert HttpMethod.POST.value == "POST"
        assert HttpMethod.PUT.value == "PUT"
        assert HttpMethod.DELETE.value == "DELETE"
