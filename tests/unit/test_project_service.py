"""
Unit tests for ProjectService.
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.services.project_service import ProjectService
from src.services.secret_manager import SecretManager


class TestProjectService:
    """Test cases for ProjectService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.secret_storage = Path(self.temp_dir.name) / "secrets"
        self.secret_manager = SecretManager(use_keyring=False, storage_dir=self.secret_storage)
        self.service = ProjectService(secret_manager=self.secret_manager)

    def teardown_method(self):
        """Clean up temporary directories."""
        self.temp_dir.cleanup()

    def _cleanup_project_files(self, project_path: str) -> None:
        meta_path = Path(f"{project_path}.meta")
        if os.path.exists(project_path):
            os.unlink(project_path)
        if meta_path.exists():
            meta_path.unlink()

    def test_create_project_success(self):
        """Test successful project creation."""
        project = self.service.create_project(
            name="Test Project",
            enter_key="test_key_12345",
            server_url="https://api.example.com/v1",
            description="Test project description",
        )

        assert project.name == "Test Project"
        assert project.description == "Test project description"
        assert project.server_config.url == "https://api.example.com/v1"
        assert project.server_config.bearer_token == "test_key_12345"

    def test_create_project_validation(self):
        """Test project creation validation."""
        # Empty name
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            self.service.create_project("", "any_key", "https://example.com", "")

        # Empty enter key
        with pytest.raises(ValueError, match="Enter key cannot be empty"):
            self.service.create_project("Test", "", "https://example.com", "")

        # Empty server URL
        with pytest.raises(ValueError, match="Server URL cannot be empty"):
            self.service.create_project("Test", "any_key", "", "")

        # Short enter key (now allowed - no minimum length restriction)
        project = self.service.create_project("Test", "abc", "https://example.com", "")
        assert project.server_config.bearer_token == "abc"

        # Invalid URL format (should still fail after normalization)
        with pytest.raises(ValueError, match="Server URL must contain a valid domain"):
            self.service.create_project("Test", "any_key", "no-domain-at-all", "")

    def test_save_and_load_project(self):
        """Test saving and loading projects."""
        # Create project
        project = self.service.create_project(
            name="Save/Load Test",
            enter_key="test_key",
            server_url="https://test.example.com/api",
            description="Test for save/load functionality",
        )

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wzp", delete=False) as f:
            temp_file = f.name

        try:
            self.service.save_project(project, temp_file)

            metadata_path = Path(f"{temp_file}.meta")
            assert metadata_path.exists()

            # Verify file exists
            assert Path(temp_file).exists()
            assert Path(temp_file).stat().st_size > 0

            # Load project
            loaded_project = self.service.load_project(temp_file)

            # Verify data integrity
            assert loaded_project.name == project.name
            assert loaded_project.description == project.description
            assert loaded_project.server_config.url == project.server_config.url
            assert (
                loaded_project.server_config.bearer_token
                == project.server_config.bearer_token
            )

        finally:
            self._cleanup_project_files(temp_file)

    def test_validate_project_file(self):
        """Test project file validation."""
        # Create and save a valid project
        project = self.service.create_project(
            name="Validation Test",
            enter_key="key123",
            server_url="https://validation.example.com",
        )

        with tempfile.NamedTemporaryFile(suffix=".wzp", delete=False) as f:
            temp_file = f.name

        try:
            self.service.save_project(project, temp_file)

            # Test validation
            assert self.service.validate_project_file(temp_file) is True
            assert self.service.validate_project_file("nonexistent.wzp") is False
            assert self.service.validate_project_file("invalid.txt") is False

        finally:
            self._cleanup_project_files(temp_file)

    def test_get_project_info(self):
        """Test getting project information without loading."""
        # Create and save a project
        project = self.service.create_project(
            name="Info Test",
            enter_key="info_key",
            server_url="https://info.example.com",
        )

        with tempfile.NamedTemporaryFile(suffix=".wzp", delete=False) as f:
            temp_file = f.name

        try:
            self.service.save_project(project, temp_file)

            info = self.service.get_project_info(temp_file)
            assert info["exists"] is True
            assert info["is_valid"] is True
            assert info["file_path"] == temp_file
            assert info["file_name"] == Path(temp_file).name

        finally:
            self._cleanup_project_files(temp_file)
