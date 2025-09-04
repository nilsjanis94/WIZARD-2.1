"""
Project Model for WIZARD-2.1

Handles project data structure and operations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Server configuration for data upload."""

    url: str = Field(..., description="Server URL for data upload")
    bearer_token: str = Field(..., description="Bearer token for authentication")
    project_field_name: str = Field(
        default="project", description="Form field name for project"
    )
    location_field_name: str = Field(
        default="location", description="Form field name for location"
    )
    tob_file_field_name: str = Field(
        default="tob_file", description="Form field name for TOB file"
    )
    subconn_length_field_name: str = Field(
        default="subcon", description="Form field name for subcon length"
    )
    string_id_field_name: str = Field(
        default="string_id", description="Form field name for string ID"
    )
    comment_field_name: str = Field(
        default="comment", description="Form field name for comment"
    )


class TOBFileInfo(BaseModel):
    """Information about a TOB file in the project."""

    file_path: str = Field(..., description="Path to the TOB file")
    file_name: str = Field(..., description="Name of the TOB file")
    file_size: int = Field(..., description="Size of the file in bytes")
    added_date: datetime = Field(
        default_factory=datetime.now, description="Date when file was added"
    )
    processed: bool = Field(
        default=False, description="Whether file has been processed"
    )
    data_points: Optional[int] = Field(None, description="Number of data points")
    sensors: List[str] = Field(default_factory=list, description="Available sensors")


class ProjectModel(BaseModel):
    """
    Model for project data structure.

    Attributes:
        name: Project name
        description: Project description
        created_date: Creation date
        modified_date: Last modification date
        server_config: Server configuration
        tob_files: List of TOB files in the project
        project_data: Processed project data
        encryption_key: Encryption key for the project
    """

    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    created_date: datetime = Field(
        default_factory=datetime.now, description="Creation date"
    )
    modified_date: datetime = Field(
        default_factory=datetime.now, description="Last modification date"
    )
    server_config: Optional[ServerConfig] = Field(
        None, description="Server configuration"
    )
    tob_files: List[TOBFileInfo] = Field(
        default_factory=list, description="TOB files in project"
    )
    project_data: Dict[str, Any] = Field(
        default_factory=dict, description="Processed project data"
    )
    encryption_key: Optional[str] = Field(
        None, description="Encryption key for the project"
    )

    def add_tob_file(
        self,
        file_path: str,
        file_name: str,
        file_size: int,
        data_points: Optional[int] = None,
        sensors: Optional[List[str]] = None,
    ) -> None:
        """
        Add a TOB file to the project.

        Args:
            file_path: Path to the TOB file
            file_name: Name of the TOB file
            file_size: Size of the file in bytes
            data_points: Number of data points (optional)
            sensors: List of available sensors (optional)
        """
        tob_file = TOBFileInfo(
            file_path=file_path,
            file_name=file_name,
            file_size=file_size,
            data_points=data_points,
            sensors=sensors or [],
        )
        self.tob_files.append(tob_file)
        self.modified_date = datetime.now()

    def remove_tob_file(self, file_name: str) -> bool:
        """
        Remove a TOB file from the project.

        Args:
            file_name: Name of the TOB file to remove

        Returns:
            True if file was removed, False if not found
        """
        for i, tob_file in enumerate(self.tob_files):
            if tob_file.file_name == file_name:
                del self.tob_files[i]
                self.modified_date = datetime.now()
                return True
        return False

    def get_tob_file(self, file_name: str) -> Optional[TOBFileInfo]:
        """
        Get TOB file information by name.

        Args:
            file_name: Name of the TOB file

        Returns:
            TOBFileInfo object or None if not found
        """
        for tob_file in self.tob_files:
            if tob_file.file_name == file_name:
                return tob_file
        return None

    def update_modified_date(self) -> None:
        """Update the modified date to current time."""
        self.modified_date = datetime.now()

    def get_project_summary(self) -> Dict[str, Any]:
        """
        Get project summary information.

        Returns:
            Dictionary containing project summary
        """
        return {
            "name": self.name,
            "description": self.description,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "tob_files_count": len(self.tob_files),
            "total_data_points": sum(tob.data_points or 0 for tob in self.tob_files),
            "has_server_config": self.server_config is not None,
            "is_encrypted": self.encryption_key is not None,
        }
