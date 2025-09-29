"""
Project Model for WIZARD-2.1

Handles project data structure and operations.
"""

from contextlib import contextmanager
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field


class RollbackTransaction:
    """
    Context manager for safe TOB file operations with automatic rollback.

    Provides backup and restore functionality for TOB files to ensure
    data integrity during complex operations.
    """

    def __init__(self, project_model: "ProjectModel"):
        """
        Initialize rollback transaction.

        Args:
            project_model: The project model to operate on
        """
        self.project_model = project_model
        self.backup_tob_files: List[Dict[str, Any]] = []
        self.initial_tob_files: List[str] = []  # Files that existed before transaction
        self.operations_performed: List[str] = []
        self.rollback_needed = False

    def backup_tob_file(self, file_name: str) -> bool:
        """
        Create a backup of a TOB file.

        Args:
            file_name: Name of the TOB file to backup

        Returns:
            True if backup was created, False otherwise
        """
        tob_file = self.project_model.get_tob_file(file_name)
        if not tob_file:
            return False

        # Create deep copy of TOB file data
        backup = {
            "file_name": tob_file.file_name,
            "file_path": tob_file.file_path,
            "file_size": tob_file.file_size,
            "added_date": tob_file.added_date,
            "data_points": tob_file.data_points,
            "sensors": tob_file.sensors.copy() if tob_file.sensors else [],
            "status": tob_file.status,
            "tob_data": None,
        }

        # Backup TOB data if it exists
        if tob_file.tob_data:
            backup["tob_data"] = {
                "headers": (
                    tob_file.tob_data.headers.copy()
                    if tob_file.tob_data.headers
                    else {}
                ),
                "data": (
                    tob_file.tob_data.data.copy()
                    if tob_file.tob_data.data is not None
                    else None
                ),
                "raw_data": tob_file.tob_data.raw_data,
            }

        self.backup_tob_files.append(backup)
        return True

    def record_operation(self, operation: str) -> None:
        """
        Record an operation that was performed.

        Args:
            operation: Description of the operation
        """
        self.operations_performed.append(operation)

    def rollback(self) -> bool:
        """
        Rollback all changes made during this transaction.

        Returns:
            True if rollback was successful, False otherwise
        """
        try:
            # Get current files
            current_files = [f.file_name for f in self.project_model.tob_files]

            # Remove files that were added during transaction
            for file_name in current_files:
                if file_name not in self.initial_tob_files:
                    self.project_model.remove_tob_file(file_name)

            # Restore backed up TOB files (modified existing files)
            for backup in self.backup_tob_files:
                file_name = backup["file_name"]

                # Remove current version if it exists
                self.project_model.remove_tob_file(file_name)

                # Restore backup
                if backup["tob_data"]:
                    self.project_model.add_tob_file(
                        file_path=backup["file_path"],
                        file_name=backup["file_name"],
                        file_size=backup["file_size"],
                        headers=backup["tob_data"]["headers"],
                        data=backup["tob_data"]["data"],
                        raw_data=backup["tob_data"]["raw_data"],
                        data_points=backup["data_points"],
                        sensors=backup["sensors"],
                    )
                else:
                    # Restore without data
                    self.project_model.add_tob_file(
                        file_path=backup["file_path"],
                        file_name=backup["file_name"],
                        file_size=backup["file_size"],
                        data_points=backup["data_points"],
                        sensors=backup["sensors"],
                    )
                # Restore status
                self.project_model.update_tob_file_status(
                    backup["file_name"], backup["status"]
                )

            return True

        except Exception as e:
            print(f"Error during rollback: {e}")
            return False

    @contextmanager
    def transaction(self):
        """
        Context manager for safe TOB file operations.

        Usage:
            with rollback_transaction.transaction():
                # Perform operations
                project.add_tob_file(...)
                if some_error:
                    raise Exception("Operation failed")
                # Changes are committed automatically on success
        """
        # Record initial state
        self.initial_tob_files = [f.file_name for f in self.project_model.tob_files]
        self.rollback_needed = False

        try:
            yield self
        except Exception as e:
            self.rollback_needed = True
            if self.rollback():
                print(f"Transaction rolled back due to error: {e}")
            else:
                print(f"Failed to rollback transaction after error: {e}")
            raise
        finally:
            if not self.rollback_needed:
                # Transaction successful, clear backups
                self.backup_tob_files.clear()
                self.initial_tob_files.clear()


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


class TOBFileStatus:
    """Enumeration for TOB file processing status."""

    LOADED = "loaded"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    ERROR = "error"


class TOBFileData(BaseModel):
    """Complete TOB file data storage."""

    headers: Dict[str, Any] = Field(
        default_factory=dict, description="TOB file headers"
    )
    data: Optional[Any] = Field(
        None, description="TOB data as pandas DataFrame", exclude=True
    )
    raw_data: Optional[str] = Field(None, description="Raw TOB file content")

    class Config:
        """Pydantic configuration."""

        # Exclude dataframe from JSON serialization to avoid pandas serialization issues
        json_encoders = {
            # Custom encoder for any non-serializable objects
        }


class TOBFileInfo(BaseModel):
    """Complete information about a TOB file in the project."""

    # Basic file information
    file_path: str = Field(..., description="Original path to the TOB file")
    file_name: str = Field(..., description="Name of the TOB file")
    file_size: int = Field(..., description="Size of the file in bytes")
    added_date: datetime = Field(
        default_factory=datetime.now, description="Date when file was added"
    )

    # TOB data and metadata
    data_points: Optional[int] = Field(None, description="Number of data points")
    sensors: List[str] = Field(default_factory=list, description="Available sensors")
    tob_data: Optional[TOBFileData] = Field(None, description="Complete TOB file data")

    # Modified headers (for persistence of user changes)
    modified_headers: Dict[str, Any] = Field(
        default_factory=dict, description="Headers modified by user (persistent)"
    )

    # Processing status
    status: str = Field(
        default=TOBFileStatus.LOADED, description="Current processing status"
    )
    server_job_id: Optional[str] = Field(None, description="Server job ID after upload")
    server_status: Optional[str] = Field(
        None, description="Status from server processing"
    )
    upload_date: Optional[datetime] = Field(
        None, description="Date when uploaded to server"
    )
    error_message: Optional[str] = Field(
        None, description="Error message if status is ERROR"
    )

    # UI state
    is_active: bool = Field(
        default=False, description="Whether file is currently displayed"
    )

    def update_status(self, new_status: str, error_msg: Optional[str] = None) -> None:
        """Update the processing status."""
        self.status = new_status
        if error_msg:
            self.error_message = error_msg
        if new_status == TOBFileStatus.UPLOADED:
            self.upload_date = datetime.now()


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
    active_tob_file: Optional[str] = Field(
        None, description="Name of currently active TOB file for display"
    )

    # Project limits (ClassVar to avoid Pydantic field detection)
    MAX_TOB_FILES: ClassVar[int] = 20
    MAX_TOB_FILE_SIZE_MB: ClassVar[int] = 100
    MAX_TOTAL_MEMORY_GB: ClassVar[int] = 2

    def can_add_tob_file(self, file_size: int) -> tuple[bool, str]:
        """
        Check if a TOB file can be added to the project.

        Args:
            file_size: Size of the file in bytes

        Returns:
            Tuple of (can_add, reason_if_not)
        """
        if len(self.tob_files) >= self.MAX_TOB_FILES:
            return (
                False,
                f"Maximum of {self.MAX_TOB_FILES} TOB files per project reached",
            )

        max_size_bytes = self.MAX_TOB_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            return False, f"TOB file too large (max {self.MAX_TOB_FILE_SIZE_MB}MB)"

        # Check for duplicate file names
        return True, ""

    def add_tob_file(
        self,
        file_path: str,
        file_name: str,
        file_size: int,
        headers: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        raw_data: Optional[str] = None,
        data_points: Optional[int] = None,
        sensors: Optional[List[str]] = None,
    ) -> bool:
        """
        Add a complete TOB file to the project.

        Args:
            file_path: Path to the TOB file
            file_name: Name of the TOB file
            file_size: Size of the file in bytes
            headers: TOB file headers
            data: TOB data as pandas DataFrame
            raw_data: Raw TOB file content
            data_points: Number of data points (optional)
            sensors: List of available sensors (optional)

        Returns:
            True if added successfully, False if limits exceeded
        """
        # Check limits
        can_add, reason = self.can_add_tob_file(file_size)
        if not can_add:
            return False

        # Create TOB data object
        tob_data = None
        if headers or data is not None or raw_data:
            tob_data = TOBFileData(headers=headers or {}, data=data, raw_data=raw_data)

        # Check for duplicate file names
        if any(tob.file_name == file_name for tob in self.tob_files):
            # Update existing file
            for tob in self.tob_files:
                if tob.file_name == file_name:
                    tob.file_path = file_path
                    tob.file_size = file_size
                    tob.tob_data = tob_data
                    tob.modified_headers = {}
                    tob.data_points = data_points
                    tob.sensors = sensors or []
                    tob.status = TOBFileStatus.LOADED
                    break
        else:
            # Add new file
            tob_file = TOBFileInfo(
                file_path=file_path,
                file_name=file_name,
                file_size=file_size,
                tob_data=tob_data,
                data_points=data_points,
                sensors=sensors or [],
                status=TOBFileStatus.LOADED,
            )
            self.tob_files.append(tob_file)

        self.modified_date = datetime.now()
        return True

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

    def get_active_tob_file(self) -> Optional["TOBFileInfo"]:
        """
        Get the currently active TOB file for plotting.

        Returns:
            TOBFileInfo of active file or None if no active file
        """
        if not self.active_tob_file:
            return None

        return self.get_tob_file(self.active_tob_file)

    def clear_active_tob_file(self) -> None:
        """
        Clear the active TOB file selection.
        """
        self.active_tob_file = None

    def update_tob_file_data(
        self,
        file_name: str,
        headers: Optional[Dict] = None,
        data: Optional[Any] = None,
        data_points: Optional[int] = None,
        sensors: Optional[List[str]] = None,
    ) -> bool:
        """
        Update the data of an existing TOB file in the project.

        Args:
            file_name: Name of the TOB file to update
            headers: New headers (optional)
            data: New DataFrame (optional)
            data_points: New data point count (optional)
            sensors: New sensor list (optional)

        Returns:
            True if update was successful, False otherwise
        """
        for tob_file in self.tob_files:
            if tob_file.file_name == file_name:
                # Update provided fields
                if headers is not None:
                    tob_file.headers = headers
                if data is not None:
                    if tob_file.tob_data is None:
                        tob_file.tob_data = TOBFileData(headers=headers or {}, data=data)
                    else:
                        tob_file.tob_data.data = data
                if data_points is not None:
                    tob_file.data_points = data_points
                if sensors is not None:
                    tob_file.sensors = sensors

                # Update modification date
                tob_file.added_date = datetime.now()

                return True

        return False

    def create_rollback_transaction(self) -> RollbackTransaction:
        """
        Create a new rollback transaction for safe TOB file operations.

        Returns:
            RollbackTransaction instance
        """
        return RollbackTransaction(self)

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

    def set_active_tob_file(self, file_name: str) -> bool:
        """
        Set the active TOB file for display.

        Args:
            file_name: Name of the TOB file to activate

        Returns:
            True if file was found and activated, False otherwise
        """
        if any(tob.file_name == file_name for tob in self.tob_files):
            self.active_tob_file = file_name
            # Update is_active flags
            for tob in self.tob_files:
                tob.is_active = tob.file_name == file_name
            return True
        return False

    def get_active_tob_file(self) -> Optional[TOBFileInfo]:
        """
        Get the currently active TOB file.

        Returns:
            TOBFileInfo object or None if no active file
        """
        if not self.active_tob_file:
            return None
        return self.get_tob_file(self.active_tob_file)

    def update_tob_file_status(
        self, file_name: str, status: str, error_msg: Optional[str] = None
    ) -> bool:
        """
        Update the status of a TOB file.

        Args:
            file_name: Name of the TOB file
            status: New status
            error_msg: Error message if status is ERROR

        Returns:
            True if file was found and updated, False otherwise
        """
        tob_file = self.get_tob_file(file_name)
        if tob_file:
            tob_file.update_status(status, error_msg)
            self.modified_date = datetime.now()
            return True
        return False

    def get_memory_usage_mb(self) -> float:
        """
        Calculate approximate memory usage of all TOB files.

        Returns:
            Memory usage in MB
        """
        # Rough estimation: assume DataFrame uses ~2-3x file size in memory
        total_file_size_mb = sum(tob.file_size for tob in self.tob_files) / (
            1024 * 1024
        )
        # Estimate DataFrame overhead
        estimated_memory_mb = total_file_size_mb * 2.5
        return estimated_memory_mb

    def check_memory_limits(self) -> tuple[bool, str]:
        """
        Check if current memory usage exceeds limits.

        Returns:
            Tuple of (within_limits, warning_message)
        """
        memory_mb = self.get_memory_usage_mb()
        max_memory_gb = self.MAX_TOTAL_MEMORY_GB
        max_memory_mb = max_memory_gb * 1024

        if memory_mb > max_memory_mb * 0.8:  # Warning at 80%
            return (
                False,
                f"Memory usage high: {memory_mb:.1f}MB of {max_memory_mb:.0f}MB limit",
            )
        elif memory_mb > max_memory_mb:
            return (
                False,
                f"Memory limit exceeded: {memory_mb:.1f}MB > {max_memory_mb:.0f}MB",
            )

        return True, ""

    def get_project_summary(self) -> Dict[str, Any]:
        """
        Get project summary information.

        Returns:
            Dictionary containing project summary
        """
        memory_mb = self.get_memory_usage_mb()
        memory_ok, memory_msg = self.check_memory_limits()

        return {
            "name": self.name,
            "description": self.description,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "tob_files_count": len(self.tob_files),
            "total_data_points": sum(tob.data_points or 0 for tob in self.tob_files),
            "total_file_size_mb": sum(tob.file_size for tob in self.tob_files)
            / (1024 * 1024),
            "memory_usage_mb": memory_mb,
            "memory_status": "OK" if memory_ok else "WARNING",
            "memory_message": memory_msg if not memory_ok else "",
            "active_tob_file": self.active_tob_file,
            "has_server_config": self.server_config is not None,
            "is_encrypted": self.encryption_key is not None,
            "limits": {
                "max_tob_files": self.MAX_TOB_FILES,
                "max_file_size_mb": self.MAX_TOB_FILE_SIZE_MB,
                "max_memory_gb": self.MAX_TOTAL_MEMORY_GB,
            },
        }
