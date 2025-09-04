"""
Encryption Service for WIZARD-2.1

Service for project encryption and decryption operations.
"""

import base64
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..models.project_model import ProjectModel


class EncryptionService:
    """Service for project encryption and decryption."""

    def __init__(self):
        """Initialize the encryption service."""
        self.logger = logging.getLogger(__name__)

    def encrypt_project(self, project: ProjectModel, password: str) -> bytes:
        """
        Encrypt a project with a password.

        Args:
            project: ProjectModel instance to encrypt
            password: Password for encryption

        Returns:
            Encrypted project data as bytes
        """
        try:
            self.logger.info("Encrypting project: %s", project.name)

            # Convert project to JSON
            project_json = project.model_dump_json()
            project_bytes = project_json.encode("utf-8")

            # Generate encryption key from password
            key = self._derive_key_from_password(password)

            # Encrypt the data
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(project_bytes)

            self.logger.info("Successfully encrypted project: %s", project.name)
            return encrypted_data

        except Exception as e:
            self.logger.error("Error encrypting project %s: %s", project.name, e)
            raise

    def decrypt_project(self, encrypted_data: bytes, password: str) -> ProjectModel:
        """
        Decrypt a project with a password.

        Args:
            encrypted_data: Encrypted project data
            password: Password for decryption

        Returns:
            Decrypted ProjectModel instance
        """
        try:
            self.logger.info("Decrypting project")

            # Generate decryption key from password
            key = self._derive_key_from_password(password)

            # Decrypt the data
            fernet = Fernet(key)
            decrypted_bytes = fernet.decrypt(encrypted_data)

            # Convert back to JSON and create ProjectModel
            project_json = decrypted_bytes.decode("utf-8")
            project_data = json.loads(project_json)

            project = ProjectModel(**project_data)

            self.logger.info("Successfully decrypted project: %s", project.name)
            return project

        except Exception as e:
            self.logger.error("Error decrypting project: %s", e)
            raise

    def _derive_key_from_password(self, password: str) -> bytes:
        """
        Derive encryption key from password using PBKDF2.

        Args:
            password: Password string

        Returns:
            Derived encryption key
        """
        try:
            # Use a fixed salt for consistency (in production, use random salt)
            salt = b"wizard_salt_2024"  # TODO: Use random salt in production

            # Derive key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )

            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key

        except Exception as e:
            self.logger.error("Error deriving key from password: %s", e)
            raise

    def save_encrypted_project(
        self, project: ProjectModel, password: str, file_path: str
    ) -> None:
        """
        Save an encrypted project to file.

        Args:
            project: ProjectModel instance to save
            password: Password for encryption
            file_path: Path where to save the encrypted project
        """
        try:
            self.logger.info("Saving encrypted project to: %s", file_path)

            # Encrypt the project
            encrypted_data = self.encrypt_project(project, password)

            # Save to file
            with open(file_path, "wb") as f:
                f.write(encrypted_data)

            self.logger.info("Successfully saved encrypted project to: %s", file_path)

        except Exception as e:
            self.logger.error("Error saving encrypted project to %s: %s", file_path, e)
            raise

    def load_encrypted_project(self, file_path: str, password: str) -> ProjectModel:
        """
        Load an encrypted project from file.

        Args:
            file_path: Path to the encrypted project file
            password: Password for decryption

        Returns:
            Decrypted ProjectModel instance
        """
        try:
            self.logger.info("Loading encrypted project from: %s", file_path)

            # Read encrypted data from file
            with open(file_path, "rb") as f:
                encrypted_data = f.read()

            # Decrypt the project
            project = self.decrypt_project(encrypted_data, password)

            self.logger.info("Successfully loaded encrypted project: %s", project.name)
            return project

        except Exception as e:
            self.logger.error(
                "Error loading encrypted project from %s: %s", file_path, e
            )
            raise

    def validate_password(self, encrypted_data: bytes, password: str) -> bool:
        """
        Validate if a password is correct for encrypted data.

        Args:
            encrypted_data: Encrypted project data
            password: Password to validate

        Returns:
            True if password is correct, False otherwise
        """
        try:
            # Try to decrypt with the password
            self.decrypt_project(encrypted_data, password)
            return True

        except Exception:
            return False

    def get_project_info(self, encrypted_data: bytes) -> Dict[str, Any]:
        """
        Get project information without decrypting the full project.

        Args:
            encrypted_data: Encrypted project data

        Returns:
            Dictionary containing project information
        """
        try:
            # This is a simplified version - in production, you might want to
            # store metadata separately or use a different approach
            return {
                "encrypted": True,
                "size": len(encrypted_data),
                "format": "WIZARD-2.1 Encrypted Project",
            }

        except Exception as e:
            self.logger.error("Error getting project info: %s", e)
            return {}
