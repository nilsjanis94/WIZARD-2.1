"""
Helper functions for WIZARD-2.1

Utility functions and helper classes.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to the project root
    """
    return Path(__file__).parent.parent.parent


def get_user_data_dir() -> Path:
    """
    Get the user data directory for the application.

    Returns:
        Path to the user data directory
    """
    if sys.platform == "win32":
        base_dir = Path.home() / "AppData" / "Local" / "WIZARD-2.1"
    elif sys.platform == "darwin":
        base_dir = Path.home() / "Library" / "Application Support" / "WIZARD-2.1"
    else:  # Linux and others
        base_dir = Path.home() / ".local" / "share" / "WIZARD-2.1"

    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def get_projects_dir() -> Path:
    """
    Get the projects directory.

    Returns:
        Path to the projects directory
    """
    projects_dir = get_user_data_dir() / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    return projects_dir


def get_settings_dir() -> Path:
    """
    Get the settings directory.

    Returns:
        Path to the settings directory
    """
    settings_dir = get_user_data_dir() / "settings"
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir


def get_cache_dir() -> Path:
    """
    Get the cache directory.

    Returns:
        Path to the cache directory
    """
    cache_dir = get_user_data_dir() / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def format_number(number: Union[int, float]) -> str:
    """
    Format number with thousand separators.

    Args:
        number: Number to format

    Returns:
        Formatted number string
    """
    return f"{number:,}"


def safe_filename(filename: str) -> str:
    """
    Create a safe filename by removing invalid characters.

    Args:
        filename: Original filename

    Returns:
        Safe filename
    """
    invalid_chars = '<>:"/\\|?*'
    safe_name = filename

    for char in invalid_chars:
        safe_name = safe_name.replace(char, "_")

    return safe_name


def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename.

    Args:
        filename: Filename

    Returns:
        File extension (including dot)
    """
    return Path(filename).suffix.lower()


def is_tob_file(filename: str) -> bool:
    """
    Check if file is a TOB file.

    Args:
        filename: Filename to check

    Returns:
        True if TOB file, False otherwise
    """
    extension = get_file_extension(filename)
    return extension in [".tob", ".flx"]


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Validate if file path exists and is readable.

    Args:
        file_path: Path to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        path = Path(file_path)
        return path.exists() and path.is_file() and os.access(path, os.R_OK)
    except Exception:
        return False


def create_backup(file_path: Union[str, Path]) -> Optional[Path]:
    """
    Create a backup of a file.

    Args:
        file_path: Path to the file to backup

    Returns:
        Path to backup file or None if failed
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None

        backup_path = path.with_suffix(f"{path.suffix}.backup")
        counter = 1

        while backup_path.exists():
            backup_path = path.with_suffix(f"{path.suffix}.backup.{counter}")
            counter += 1

        import shutil

        shutil.copy2(path, backup_path)
        return backup_path

    except Exception as e:
        get_logger(__name__).error(f"Error creating backup: {e}")
        return None


def cleanup_temp_files(temp_dir: Union[str, Path]) -> None:
    """
    Clean up temporary files in a directory.

    Args:
        temp_dir: Directory to clean up
    """
    try:
        temp_path = Path(temp_dir)
        if temp_path.exists() and temp_path.is_dir():
            import shutil

            shutil.rmtree(temp_path)
    except Exception as e:
        get_logger(__name__).error(f"Error cleaning up temp files: {e}")


def get_system_info() -> Dict[str, Any]:
    """
    Get system information.

    Returns:
        Dictionary containing system information
    """
    import platform

    import psutil

    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
    }


def format_duration(seconds: float) -> str:
    """
    Format duration in human readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
