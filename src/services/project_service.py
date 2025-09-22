"""
Project Service for WIZARD-2.1

Service for project management, creation, and file operations.
Handles project lifecycle with app-internal encryption.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from ..models.project_model import ProjectModel, ServerConfig
from .encryption_service import EncryptionService


class ProjectService:
    """
    Service for project management operations.

    Handles project creation, saving, loading, and validation
    with app-internal encryption for data security.
    """

    # App-internal encryption key - should be moved to config in production
    APP_ENCRYPTION_KEY = "wizard-2.1-internal-key-v1.0-secure"

    def __init__(self):
        """Initialize the project service."""
        self.logger = logging.getLogger(__name__)
        self.encryption_service = EncryptionService()

    def create_project(
        self,
        name: str,
        enter_key: str,
        server_url: str,
        description: Optional[str] = None
    ) -> ProjectModel:
        """
        Create a new project with server configuration.

        Args:
            name: Project name
            enter_key: Enter key for server authentication (no minimum length)
            server_url: Server URL for API communication
            description: Optional project description

        Returns:
            ProjectModel: Newly created project instance

        Raises:
            ValueError: If required parameters are invalid
        """
        try:
            self.logger.info("Creating new project: %s", name)

            # Validate and normalize inputs
            name = name.strip()
            enter_key = enter_key.strip()
            server_url = self._normalize_server_url(server_url.strip())

            self._validate_project_inputs(name, enter_key, server_url)

            # Create server configuration
            server_config = ServerConfig(
                url=server_url,
                bearer_token=enter_key,
                # Default form field names (can be configured later)
                project_field_name="project",
                location_field_name="location",
                tob_file_field_name="tob_file",
                subconn_length_field_name="subcon",
                string_id_field_name="string_id",
                comment_field_name="comment"
            )

            # Create project model
            project = ProjectModel(
                name=name,
                description=description,
                server_config=server_config,
                encryption_key=self.APP_ENCRYPTION_KEY
            )

            self.logger.info("Successfully created project: %s", name)
            return project

        except Exception as e:
            self.logger.error("Error creating project %s: %s", name, e)
            raise

    def save_project(self, project: ProjectModel, file_path: str) -> None:
        """
        Save a project to an encrypted file.

        Args:
            project: ProjectModel instance to save
            file_path: Path where to save the project

        Raises:
            IOError: If file cannot be written
            Exception: If encryption fails
        """
        try:
            self.logger.info("Saving project '%s' to: %s", project.name, file_path)

            # Ensure the directory exists
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)

            # Use app-internal encryption
            self.encryption_service.save_encrypted_project(
                project=project,
                password=self.APP_ENCRYPTION_KEY,
                file_path=file_path
            )

            self.logger.info("Successfully saved project: %s", project.name)

        except Exception as e:
            self.logger.error("Error saving project %s: %s", project.name, e)
            raise

    def load_project(self, file_path: str) -> ProjectModel:
        """
        Load a project from an encrypted file.

        Args:
            file_path: Path to the encrypted project file

        Returns:
            ProjectModel: Decrypted project instance

        Raises:
            FileNotFoundError: If project file doesn't exist
            Exception: If decryption fails or file is invalid
        """
        try:
            self.logger.info("Loading project from: %s", file_path)

            # Check if file exists
            if not Path(file_path).exists():
                raise FileNotFoundError(f"Project file not found: {file_path}")

            # Load with app-internal encryption
            project = self.encryption_service.load_encrypted_project(
                file_path=file_path,
                password=self.APP_ENCRYPTION_KEY
            )

            self.logger.info("Successfully loaded project: %s", project.name)
            return project

        except Exception as e:
            self.logger.error("Error loading project from %s: %s", file_path, e)
            raise

    def validate_project_file(self, file_path: str) -> bool:
        """
        Validate if a file is a valid WIZARD project file.

        Args:
            file_path: Path to check

        Returns:
            bool: True if valid project file, False otherwise
        """
        try:
            file_path_obj = Path(file_path)

            # Check file extension
            if not file_path_obj.suffix.lower() == '.wzp':
                return False

            # Check if file exists and is readable
            if not file_path_obj.exists() or not file_path_obj.is_file():
                return False

            # Check file size (should not be empty)
            if file_path_obj.stat().st_size == 0:
                return False

            # Try to load the project to validate it's properly encrypted and contains valid data
            try:
                self.load_project(str(file_path))
                return True
            except Exception:
                # If loading fails, it's not a valid project file
                return False

        except Exception:
            return False

    def get_project_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get basic project information without full decryption.

        Args:
            file_path: Path to the project file

        Returns:
            Dict containing project metadata
        """
        try:
            file_path_obj = Path(file_path)

            # Basic file information
            exists = file_path_obj.exists()
            is_valid_extension = file_path_obj.suffix.lower() == '.wzp'

            info = {
                'file_path': str(file_path),
                'file_name': file_path_obj.name,
                'file_size': file_path_obj.stat().st_size if exists else 0,
                'exists': exists,
                'is_valid_extension': is_valid_extension,
                'is_valid': False  # Will be set below
            }

            # Only validate if file exists and has correct extension
            if exists and is_valid_extension:
                try:
                    # Quick validation without full decryption
                    info['is_valid'] = file_path_obj.stat().st_size > 0
                except Exception:
                    info['is_valid'] = False
            else:
                info['is_valid'] = False

            return info

        except Exception as e:
            self.logger.error("Error getting project info for %s: %s", file_path, e)
            return {'error': str(e)}

    def _normalize_server_url(self, url: str) -> str:
        """
        Normalize server URL by adding https:// if missing.

        Args:
            url: Raw URL string

        Returns:
            Normalized URL with protocol
        """
        url = url.strip()
        if not url:
            return url

        # If no protocol specified, assume https://
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        return url

    def _validate_project_inputs(self, name: str, enter_key: str, server_url: str) -> None:
        """
        Validate project creation inputs.

        Args:
            name: Project name
            enter_key: Enter key
            server_url: Server URL (already normalized)

        Raises:
            ValueError: If validation fails
        """
        if not name:
            raise ValueError("Project name cannot be empty")

        if not enter_key:
            raise ValueError("Enter key cannot be empty")

        if not server_url:
            raise ValueError("Server URL cannot be empty")

        # Basic enter key validation (just check it's not empty)
        # No minimum length restriction for maximum flexibility

        # Basic URL validation - check if it looks like a valid URL
        if not (server_url.startswith('http://') or server_url.startswith('https://')):
            raise ValueError("Server URL must be a valid URL")

        # Check for basic domain structure
        url_without_protocol = server_url.replace('http://', '').replace('https://', '')
        if not ('.' in url_without_protocol or '/' in url_without_protocol):
            raise ValueError("Server URL must contain a valid domain or path")

    def update_project_server_config(
        self,
        project: ProjectModel,
        enter_key: Optional[str] = None,
        server_url: Optional[str] = None
    ) -> None:
        """
        Update server configuration of an existing project.

        Args:
            project: ProjectModel to update
            enter_key: New enter key (optional)
            server_url: New server URL (optional)
        """
        try:
            if not project.server_config:
                project.server_config = ServerConfig(
                    url="",
                    bearer_token=""
                )

            if enter_key is not None:
                project.server_config.bearer_token = enter_key

            if server_url is not None:
                # Normalize URL if provided
                normalized_url = self._normalize_server_url(server_url)
                project.server_config.url = normalized_url

            project.update_modified_date()
            self.logger.info("Updated server config for project: %s", project.name)

        except Exception as e:
            self.logger.error("Error updating server config for project %s: %s", project.name, e)
            raise
