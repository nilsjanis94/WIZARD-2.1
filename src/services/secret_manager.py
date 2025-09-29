"""Secret management utilities for WIZARD-2.1."""

from __future__ import annotations

import logging
import os
import stat
from pathlib import Path
from typing import Optional

try:  # pragma: no cover - optional dependency
    import keyring  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    keyring = None  # type: ignore


class SecretManagerError(RuntimeError):
    """Raised when secrets cannot be stored or retrieved."""


class SecretManager:
    """Manage encryption secrets using OS keyring with file fallback."""

    SERVICE_NAME = "wizard-2.1"

    def __init__(
        self,
        *,
        use_keyring: bool = True,
        storage_dir: Optional[Path] = None,
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self._use_keyring = use_keyring and keyring is not None

        self._storage_dir = storage_dir or Path.home() / ".wizard" / "keys"
        if not self._use_keyring:
            self._ensure_storage_dir()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def store_secret(self, key_id: str, secret_value: str) -> None:
        """Persist a secret value for the given key identifier."""
        if not key_id:
            raise SecretManagerError("key_id must not be empty")

        try:
            if self._use_keyring:
                keyring.set_password(self.SERVICE_NAME, key_id, secret_value)  # type: ignore[arg-type]
                return

            self._write_secret_file(key_id, secret_value)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("Failed to store secret %s: %s", key_id, exc)
            raise SecretManagerError("Unable to store secret") from exc

    def retrieve_secret(self, key_id: str) -> Optional[str]:
        """Fetch the secret value for the given key identifier."""
        if not key_id:
            return None

        try:
            if self._use_keyring:
                value = keyring.get_password(self.SERVICE_NAME, key_id)  # type: ignore[arg-type]
                return value

            return self._read_secret_file(key_id)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("Failed to retrieve secret %s: %s", key_id, exc)
            raise SecretManagerError("Unable to retrieve secret") from exc

    def delete_secret(self, key_id: str) -> None:
        """Remove a stored secret."""
        if not key_id:
            return

        try:
            if self._use_keyring:
                keyring.delete_password(self.SERVICE_NAME, key_id)  # type: ignore[arg-type]
                return

            secret_path = self._storage_dir / key_id
            if secret_path.exists():
                secret_path.unlink()
        except keyring.errors.PasswordDeleteError:  # type: ignore[attr-defined]
            # Secret not present in keyring – treat as success
            self.logger.debug("Secret %s not present in keyring", key_id)
        except FileNotFoundError:
            self.logger.debug("Secret file %s already removed", key_id)
        except Exception as exc:  # pragma: no cover - defensive
            self.logger.error("Failed to delete secret %s: %s", key_id, exc)
            raise SecretManagerError("Unable to delete secret") from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_storage_dir(self) -> None:
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(self._storage_dir, 0o700)

    def _write_secret_file(self, key_id: str, secret_value: str) -> None:
        self._ensure_storage_dir()
        secret_path = self._storage_dir / key_id
        with open(secret_path, "w", encoding="utf-8") as secret_file:
            secret_file.write(secret_value)
        os.chmod(secret_path, stat.S_IRUSR | stat.S_IWUSR)

    def _read_secret_file(self, key_id: str) -> Optional[str]:
        secret_path = self._storage_dir / key_id
        if not secret_path.exists():
            return None

        with open(secret_path, "r", encoding="utf-8") as secret_file:
            return secret_file.read().strip()



