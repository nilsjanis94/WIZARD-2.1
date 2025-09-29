import json
from pathlib import Path

import pytest

from src.models.project_model import ProjectModel
from src.services.encryption_service import EncryptionService


@pytest.fixture
def sample_project() -> ProjectModel:
    return ProjectModel(name="Test Project", description="Demo", version="1.0.0")


def test_encrypt_and_decrypt_roundtrip(sample_project: ProjectModel) -> None:
    service = EncryptionService()

    encrypted = service.encrypt_project(sample_project, "pwd123")
    assert isinstance(encrypted, bytes)
    assert len(encrypted) > 0

    decrypted = service.decrypt_project(encrypted, "pwd123")

    assert decrypted.name == sample_project.name
    assert decrypted.description == sample_project.description
    assert decrypted.created_date == sample_project.created_date


def test_decrypt_with_wrong_password_raises(sample_project: ProjectModel) -> None:
    service = EncryptionService()
    encrypted = service.encrypt_project(sample_project, "correct")

    with pytest.raises(Exception):
        service.decrypt_project(encrypted, "wrong")


def test_validate_password(sample_project: ProjectModel) -> None:
    service = EncryptionService()
    encrypted = service.encrypt_project(sample_project, "secret")

    assert service.validate_password(encrypted, "secret") is True
    assert service.validate_password(encrypted, "invalid") is False


def test_save_and_load_encrypted_project(tmp_path: Path, sample_project: ProjectModel) -> None:
    service = EncryptionService()
    file_path = tmp_path / "project.wzp"

    service.save_encrypted_project(sample_project, "topsecret", str(file_path))
    assert file_path.exists()

    loaded_project = service.load_encrypted_project(str(file_path), "topsecret")
    assert loaded_project.name == sample_project.name
    assert loaded_project.description == sample_project.description


def test_get_project_info(sample_project: ProjectModel) -> None:
    service = EncryptionService()
    encrypted = service.encrypt_project(sample_project, "pwd")

    info = service.get_project_info(encrypted)
    assert info["encrypted"] is True
    assert info["size"] == len(encrypted)
    assert "format" in info
