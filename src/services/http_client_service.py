"""
HTTP Client Service for WIZARD-2.1

Service for server communication including TOB file uploads and status queries.
Provides structured HTTP client functionality with authentication and error handling.
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.error_handler import ErrorHandler


class HttpMethod(Enum):
    """HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class ServerEndpoint(Enum):
    """Server API endpoints."""

    UPLOAD_TOB = "/api/tob/upload"
    UPLOAD_STATUS = "/api/tob/status/{job_id}"
    PROCESSING_STATUS = "/api/tob/processing/{job_id}"
    HEALTH_CHECK = "/api/health"


@dataclass
class HttpResponse:
    """HTTP response wrapper."""

    status_code: int
    headers: Dict[str, str]
    data: Any
    success: bool
    error_message: Optional[str] = None
    request_time: float = 0.0


@dataclass
class UploadResult:
    """TOB file upload result."""

    success: bool
    job_id: Optional[str] = None
    message: Optional[str] = None
    error_code: Optional[str] = None


@dataclass
class StatusResult:
    """Upload/processing status result."""

    status: str  # "pending", "processing", "completed", "failed"
    progress: Optional[float] = None  # 0.0 to 100.0
    message: Optional[str] = None
    result_url: Optional[str] = None
    error_message: Optional[str] = None


class HttpClientService:
    """
    HTTP client service for server communication.

    Provides authenticated HTTP requests with retry logic, timeout handling,
    and structured error responses for TOB file upload and status operations.
    """

    # Default timeouts in seconds
    CONNECT_TIMEOUT = 10.0
    READ_TIMEOUT = 30.0
    UPLOAD_TIMEOUT = 300.0  # 5 minutes for file uploads

    # Retry configuration
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0

    def __init__(
        self,
        base_url: str,
        bearer_token: str,
        error_handler: Optional[ErrorHandler] = None,
    ):
        """
        Initialize HTTP client service.

        Args:
            base_url: Base URL of the server (e.g., "https://api.example.com")
            bearer_token: Bearer token for authentication
            error_handler: Optional error handler for user notifications
        """
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url.rstrip("/")
        self.bearer_token = bearer_token
        self.error_handler = error_handler

        # Setup HTTP session with retry strategy
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=self.RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
                "POST",
            ],
        )

        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": "WIZARD-2.1-Client/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        self.logger.info(f"HTTP client initialized for {self.base_url}")

    def upload_tob_file(
        self, file_path: str, metadata: Optional[Dict[str, Any]] = None
    ) -> UploadResult:
        """
        Upload a TOB file to the server.

        Args:
            file_path: Path to the TOB file to upload
            metadata: Optional metadata to include with upload

        Returns:
            UploadResult with success status and job ID
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return UploadResult(
                    success=False,
                    message=f"File not found: {file_path}",
                    error_code="FILE_NOT_FOUND",
                )

            # Prepare multipart form data
            files = {
                "file": (
                    file_path.name,
                    open(file_path, "rb"),
                    "application/octet-stream",
                )
            }

            # Prepare metadata
            data = {}
            if metadata:
                # Convert metadata to form fields (simple key-value pairs)
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        data[f"metadata[{key}]"] = str(value)

            url = f"{self.base_url}{ServerEndpoint.UPLOAD_TOB.value}"

            self.logger.info(f"Uploading TOB file: {file_path.name}")

            # Upload with longer timeout
            response = self._make_request(
                HttpMethod.POST,
                url,
                files=files,
                data=data,
                timeout=self.UPLOAD_TIMEOUT,
            )

            if response.success:
                # Parse response for job ID
                response_data = response.data
                if isinstance(response_data, dict):
                    job_id = response_data.get("job_id") or response_data.get("id")
                    message = response_data.get("message", "Upload successful")

                    return UploadResult(success=True, job_id=job_id, message=message)
                else:
                    return UploadResult(
                        success=True, message="Upload completed (no job ID returned)"
                    )
            else:
                return UploadResult(
                    success=False,
                    message=response.error_message or "Upload failed",
                    error_code=f"HTTP_{response.status_code}",
                )

        except Exception as e:
            self.logger.error(f"Error uploading TOB file: {e}")
            return UploadResult(
                success=False,
                message=f"Upload error: {str(e)}",
                error_code="UPLOAD_ERROR",
            )

    def get_upload_status(self, job_id: str) -> StatusResult:
        """
        Get the status of an upload job.

        Args:
            job_id: Job ID from upload

        Returns:
            StatusResult with current job status
        """
        try:
            url = f"{self.base_url}{ServerEndpoint.UPLOAD_STATUS.value.format(job_id=job_id)}"

            response = self._make_request(HttpMethod.GET, url)

            if response.success:
                response_data = response.data
                if isinstance(response_data, dict):
                    status = response_data.get("status", "unknown")
                    progress = response_data.get("progress")
                    message = response_data.get("message")
                    result_url = response_data.get("result_url")
                    error_message = response_data.get("error_message")

                    return StatusResult(
                        status=status,
                        progress=float(progress) if progress is not None else None,
                        message=message,
                        result_url=result_url,
                        error_message=error_message,
                    )
                else:
                    return StatusResult(
                        status="unknown", message="Invalid response format"
                    )
            else:
                return StatusResult(
                    status="error",
                    message=response.error_message
                    or f"Status check failed (HTTP {response.status_code})",
                )

        except Exception as e:
            self.logger.error(f"Error checking upload status: {e}")
            return StatusResult(status="error", message=f"Status check error: {str(e)}")

    def get_processing_status(self, job_id: str) -> StatusResult:
        """
        Get the processing status of a TOB file.

        Args:
            job_id: Job ID from upload

        Returns:
            StatusResult with processing status
        """
        try:
            url = f"{self.base_url}{ServerEndpoint.PROCESSING_STATUS.value.format(job_id=job_id)}"

            response = self._make_request(HttpMethod.GET, url)

            if response.success:
                response_data = response.data
                if isinstance(response_data, dict):
                    status = response_data.get("status", "unknown")
                    progress = response_data.get("progress")
                    message = response_data.get("message")
                    result_url = response_data.get("result_url")
                    error_message = response_data.get("error_message")

                    return StatusResult(
                        status=status,
                        progress=float(progress) if progress is not None else None,
                        message=message,
                        result_url=result_url,
                        error_message=error_message,
                    )
                else:
                    return StatusResult(
                        status="unknown", message="Invalid response format"
                    )
            else:
                return StatusResult(
                    status="error",
                    message=response.error_message
                    or f"Processing status check failed (HTTP {response.status_code})",
                )

        except Exception as e:
            self.logger.error(f"Error checking processing status: {e}")
            return StatusResult(
                status="error", message=f"Processing status error: {str(e)}"
            )

    def health_check(self) -> bool:
        """
        Perform a health check on the server.

        Returns:
            True if server is healthy, False otherwise
        """
        try:
            url = f"{self.base_url}{ServerEndpoint.HEALTH_CHECK.value}"

            response = self._make_request(HttpMethod.GET, url, timeout=5.0)

            return response.success and response.status_code == 200

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    def _make_request(self, method: HttpMethod, url: str, **kwargs) -> HttpResponse:
        """
        Make an HTTP request with error handling and timing.

        Args:
            method: HTTP method to use
            url: URL to request
            **kwargs: Additional arguments for requests

        Returns:
            HttpResponse with status and data
        """
        start_time = time.time()

        try:
            # Set default timeout if not specified
            if "timeout" not in kwargs:
                if "files" in kwargs:  # File upload
                    kwargs["timeout"] = (self.CONNECT_TIMEOUT, self.UPLOAD_TIMEOUT)
                else:  # Regular request
                    kwargs["timeout"] = (self.CONNECT_TIMEOUT, self.READ_TIMEOUT)

            self.logger.debug(f"Making {method.value} request to {url}")

            # Make request
            response = self.session.request(method.value, url, **kwargs)

            request_time = time.time() - start_time

            # Try to parse JSON response
            try:
                data = response.json()
            except ValueError:
                data = response.text

            # Check for HTTP errors
            response.raise_for_status()

            return HttpResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=data,
                success=True,
                request_time=request_time,
            )

        except requests.exceptions.Timeout as e:
            request_time = time.time() - start_time
            return HttpResponse(
                status_code=0,
                headers={},
                data=None,
                success=False,
                error_message=f"Request timeout after {request_time:.1f}s",
                request_time=request_time,
            )

        except requests.exceptions.ConnectionError as e:
            request_time = time.time() - start_time
            return HttpResponse(
                status_code=0,
                headers={},
                data=None,
                success=False,
                error_message=f"Connection error: {str(e)}",
                request_time=request_time,
            )

        except requests.exceptions.HTTPError as e:
            request_time = time.time() - start_time
            return HttpResponse(
                status_code=e.response.status_code if e.response else 0,
                headers=dict(e.response.headers) if e.response else {},
                data=None,
                success=False,
                error_message=f"HTTP {e.response.status_code if e.response else 'unknown'}: {str(e)}",
                request_time=request_time,
            )

        except requests.exceptions.RequestException as e:
            request_time = time.time() - start_time
            return HttpResponse(
                status_code=0,
                headers={},
                data=None,
                success=False,
                error_message=f"Request error: {str(e)}",
                request_time=request_time,
            )

        except Exception as e:
            request_time = time.time() - start_time
            self.logger.error(f"Unexpected error in HTTP request: {e}")
            return HttpResponse(
                status_code=0,
                headers={},
                data=None,
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                request_time=request_time,
            )

    def __del__(self):
        """Cleanup session on destruction."""
        try:
            self.session.close()
        except:
            pass
