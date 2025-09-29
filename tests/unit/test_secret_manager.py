import os
import stat
from pathlib import Path

import pytest

from src.services.secret_manager import SecretManager, SecretManagerError


@pytest.fixture
def secret_dir(tmp_path: Path) -> Path:
    return tmp_path / "secrets"


def test_store_and_retrieve_secret_file_backend(secret_dir: Path) -> None:
    manager = SecretManager(use_keyring=False, storage_dir=secret_dir)

    manager.store_secret("project-123", "super-secret")

    secret_path = secret_dir / "project-123"
    assert secret_path.exists()
    assert secret_path.read_text(encoding="utf-8") == "super-secret"

    file_mode = stat.S_IMODE(os.stat(secret_path).st_mode)
    assert file_mode == stat.S_IRUSR | stat.S_IWUSR

    retrieved = manager.retrieve_secret("project-123")
    assert retrieved == "super-secret"


def test_delete_secret_file_backend(secret_dir: Path) -> None:
    manager = SecretManager(use_keyring=False, storage_dir=secret_dir)

    manager.store_secret("to-delete", "value")
    manager.delete_secret("to-delete")

    assert not (secret_dir / "to-delete").exists()
    assert manager.retrieve_secret("to-delete") is None


def test_store_secret_empty_key_raises(secret_dir: Path) -> None:
    manager = SecretManager(use_keyring=False, storage_dir=secret_dir)

    with pytest.raises(SecretManagerError):
        manager.store_secret("", "value")


def test_retrieve_secret_empty_key_returns_none(secret_dir: Path) -> None:
    manager = SecretManager(use_keyring=False, storage_dir=secret_dir)

    assert manager.retrieve_secret("") is None
