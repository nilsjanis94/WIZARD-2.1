"""
Unit tests for ProjectService.
"""

import os
import tempfile
from pathlib import Path

import pytest

from src.services.project_service import ProjectService
from src.models.project_model import ProjectModel
from src.services.secret_manager import SecretManager
from src.services.secret_manager import SecretManagerError
from unittest.mock import MagicMock, patch


@pytest.fixture
def project_service():
    return ProjectService(secret_manager=SecretManager(use_keyring=False))


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

    @patch("src.services.project_service.SecretManager")
    def test_create_project_generates_secret(self, mock_secret_manager):
        mock_manager = MagicMock()
        mock_manager.store_secret.return_value = None
        mock_secret_manager.return_value = mock_manager

        service = ProjectService()

        project = service.create_project("Proj", "token", "example.com")

        assert project.encryption_key is not None
        mock_manager.store_secret.assert_called_once()


    @patch("src.services.project_service.SecretManager")
    def test_create_project_secret_failure_raises(self, mock_secret_manager):
        mock_manager = MagicMock()
        mock_manager.store_secret.side_effect = SecretManagerError("boom")
        mock_secret_manager.return_value = mock_manager

        service = ProjectService()

        with pytest.raises(SecretManagerError):
            service.create_project("Proj", "token", "example.com")


    def test_save_project_generates_metadata(self, tmp_path: Path):
        secret_manager = SecretManager(use_keyring=False, storage_dir=tmp_path / "keys")
        service = ProjectService(secret_manager=secret_manager)
        project = service.create_project("Proj", "token", "example.com")

        project_path = tmp_path / "proj.wzp"
        service.save_project(project, str(project_path))

        metadata_path = project_path.with_suffix(".wzp.meta")
        assert metadata_path.exists()
        assert metadata_path.stat().st_mode & 0o777 == 0o600


    def test_load_project_legacy_fallback(self, tmp_path: Path, monkeypatch):
        secret_manager = SecretManager(use_keyring=False, storage_dir=tmp_path / "keys")
        service = ProjectService(secret_manager=secret_manager)
        project = service.create_project("Proj", "token", "example.com")

        project_path = tmp_path / "proj.wzp"
        service.save_project(project, str(project_path))

        metadata_path = project_path.with_suffix(".wzp.meta")
        metadata_path.unlink()

        monkeypatch.setenv("WIZARD_LEGACY_KEY", "legacy-key")

        legacy_service = ProjectService(secret_manager=secret_manager)
        legacy_service.encryption_service.save_encrypted_project(
            project, "legacy-key", str(project_path)
        )

        loaded = service.load_project(str(project_path))
        assert loaded.name == "Proj"
        assert loaded.encryption_key == "legacy"


    def test_validate_project_file(self, tmp_path: Path):
        secret_manager = SecretManager(use_keyring=False, storage_dir=tmp_path / "keys")
        service = ProjectService(secret_manager=secret_manager)
        project = service.create_project("Proj", "token", "example.com")

        project_path = tmp_path / "proj.wzp"
        service.save_project(project, str(project_path))

        assert service.validate_project_file(str(project_path)) is True
        assert service.validate_project_file(str(tmp_path / "not_exist.wzp")) is False
        assert service.validate_project_file(str(tmp_path / "wrong.txt")) is False


    def test_get_project_info(self, tmp_path: Path):
        secret_manager = SecretManager(use_keyring=False, storage_dir=tmp_path / "keys")
        service = ProjectService(secret_manager=secret_manager)
        project = service.create_project("Proj", "token", "example.com")
        project_path = tmp_path / "proj.wzp"
        service.save_project(project, str(project_path))

        info = service.get_project_info(str(project_path))
        assert info["exists"] is True
        assert info["is_valid_extension"] is True
        assert info["file_size"] > 0
        assert info["is_valid"] is True


    def test_update_project_server_config_normalizes_url(self, tmp_path: Path):
        service = ProjectService(
            secret_manager=SecretManager(use_keyring=False, storage_dir=tmp_path / "keys")
        )
        project = service.create_project("Proj", "token", "example.com")

        service.update_project_server_config(project, server_url="plain-domain.com")

        assert project.server_config.url == "https://plain-domain.com"


    def test_update_project_server_config_sets_enter_key(self, tmp_path: Path):
        service = ProjectService(
            secret_manager=SecretManager(use_keyring=False, storage_dir=tmp_path / "keys")
        )
        project = service.create_project("Proj", "token", "example.com")

        service.update_project_server_config(project, enter_key="new-token")

        assert project.server_config.bearer_token == "new-token"


    def test_validate_project_inputs_invalid(self):
        service = ProjectService()

        with pytest.raises(ValueError):
            service._validate_project_inputs("", "k", "https://example.com")

        with pytest.raises(ValueError):
            service._validate_project_inputs("Proj", "", "https://example.com")

        with pytest.raises(ValueError):
            service._validate_project_inputs("Proj", "token", "")

        with pytest.raises(ValueError):
            service._validate_project_inputs("Proj", "token", "invalid-url")


    def test_get_project_info_handles_missing_file(self, tmp_path: Path):
        service = ProjectService(
            secret_manager=SecretManager(use_keyring=False, storage_dir=tmp_path / "keys")
        )

        info = service.get_project_info(str(tmp_path / "missing.wzp"))
        assert info["exists"] is False
        assert info["is_valid"] is False
        assert info["file_size"] == 0
