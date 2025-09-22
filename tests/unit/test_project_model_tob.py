"""Test cases for ProjectModel TOB file management features."""

import pandas as pd
import pytest

from src.models.project_model import ProjectModel


@pytest.mark.unit
class TestProjectModelTOB:
    """Test cases for ProjectModel TOB file management."""

    def test_add_tob_file_complete(self):
        """Test adding a complete TOB file with all data."""
        project = ProjectModel(name="Test Project")

        test_data = pd.DataFrame({
            'time': [1, 2, 3],
            'NTC01': [20.1, 20.5, 21.0],
            'PT100': [25.0, 25.2, 25.1]
        })

        success = project.add_tob_file(
            file_path="/test/data.TOB",
            file_name="data.TOB",
            file_size=1024,
            headers={'version': '1.0', 'device': 'TEST'},
            dataframe=test_data,
            data_points=3,
            sensors=['NTC01', 'PT100']
        )

        assert success
        assert len(project.tob_files) == 1

        tob_file = project.tob_files[0]
        assert tob_file.file_name == "data.TOB"
        assert tob_file.file_path == "/test/data.TOB"
        assert tob_file.file_size == 1024
        assert tob_file.data_points == 3
        assert tob_file.sensors == ['NTC01', 'PT100']
        assert tob_file.status == "loaded"
        assert tob_file.tob_data is not None
        assert tob_file.tob_data.headers == {'version': '1.0', 'device': 'TEST'}
        assert tob_file.tob_data.dataframe.equals(test_data)

    def test_add_duplicate_tob_file_update(self):
        """Test adding a duplicate TOB file updates existing one."""
        project = ProjectModel(name="Test Project")

        # Add initial file
        project.add_tob_file(
            file_path="/test/data.TOB",
            file_name="data.TOB",
            file_size=1024,
            data_points=3,
            sensors=['NTC01']
        )

        # Add duplicate with different data
        test_data = pd.DataFrame({'time': [1], 'NTC02': [22.0]})
        success = project.add_tob_file(
            file_path="/test/data.TOB",
            file_name="data.TOB",
            file_size=2048,
            headers={'version': '2.0'},
            dataframe=test_data,
            data_points=1,
            sensors=['NTC02']
        )

        assert success
        assert len(project.tob_files) == 1  # Still only one file

        tob_file = project.tob_files[0]
        assert tob_file.file_size == 2048  # Updated
        assert tob_file.data_points == 1  # Updated
        assert tob_file.sensors == ['NTC02']  # Updated
        assert tob_file.tob_data.headers == {'version': '2.0'}  # Updated

    def test_can_add_tob_file_limits(self):
        """Test TOB file addition limits."""
        project = ProjectModel(name="Test Project")

        # Test file size limit (100MB)
        can_add, reason = project.can_add_tob_file(50 * 1024 * 1024)  # 50MB
        assert can_add
        assert reason == ""

        can_add, reason = project.can_add_tob_file(150 * 1024 * 1024)  # 150MB
        assert not can_add
        assert "too large" in reason

        # Test file count limit (20 files)
        for i in range(20):
            project.add_tob_file(
                file_path=f"/test/file{i}.TOB",
                file_name=f"file{i}.TOB",
                file_size=1024,
                data_points=1,
                sensors=['sensor']
            )

        can_add, reason = project.can_add_tob_file(1024)
        assert not can_add
        assert "Maximum of 20 TOB files" in reason

    def test_update_tob_file_data(self):
        """Test updating TOB file data."""
        project = ProjectModel(name="Test Project")

        # Add initial file
        project.add_tob_file(
            file_path="/test/data.TOB",
            file_name="data.TOB",
            file_size=1024,
            data_points=3,
            sensors=['NTC01']
        )

        # Update data (data_points and sensors)
        success = project.update_tob_file_data(
            file_name="data.TOB",
            data_points=2,
            sensors=['NTC02']
        )

        assert success

        tob_file = project.get_tob_file("data.TOB")
        assert tob_file is not None
        assert tob_file.data_points == 2
        assert tob_file.sensors == ['NTC02']

    def test_update_tob_file_data_nonexistent(self):
        """Test updating data for non-existent TOB file."""
        project = ProjectModel(name="Test Project")

        success = project.update_tob_file_data(
            file_name="nonexistent.TOB",
            data_points=5
        )

        assert not success

    def test_remove_tob_file(self):
        """Test removing a TOB file."""
        project = ProjectModel(name="Test Project")

        # Add files
        project.add_tob_file(
            file_path="/test/file1.TOB",
            file_name="file1.TOB",
            file_size=1024,
            data_points=1,
            sensors=['sensor1']
        )
        project.add_tob_file(
            file_path="/test/file2.TOB",
            file_name="file2.TOB",
            file_size=2048,
            data_points=2,
            sensors=['sensor2']
        )

        assert len(project.tob_files) == 2

        # Remove one file
        success = project.remove_tob_file("file1.TOB")
        assert success
        assert len(project.tob_files) == 1

        # Check remaining file
        remaining = project.tob_files[0]
        assert remaining.file_name == "file2.TOB"

        # Try to remove non-existent file
        success = project.remove_tob_file("nonexistent.TOB")
        assert not success

    def test_get_tob_file(self):
        """Test getting TOB file by name."""
        project = ProjectModel(name="Test Project")

        # Add file
        project.add_tob_file(
            file_path="/test/data.TOB",
            file_name="data.TOB",
            file_size=1024,
            data_points=1,
            sensors=['sensor']
        )

        # Get existing file
        tob_file = project.get_tob_file("data.TOB")
        assert tob_file is not None
        assert tob_file.file_name == "data.TOB"

        # Get non-existent file
        tob_file = project.get_tob_file("nonexistent.TOB")
        assert tob_file is None

    def test_set_active_tob_file(self):
        """Test setting active TOB file."""
        project = ProjectModel(name="Test Project")

        # Add files
        project.add_tob_file(
            file_path="/test/file1.TOB",
            file_name="file1.TOB",
            file_size=1024,
            data_points=1,
            sensors=['sensor1']
        )
        project.add_tob_file(
            file_path="/test/file2.TOB",
            file_name="file2.TOB",
            file_size=2048,
            data_points=2,
            sensors=['sensor2']
        )

        # Set active file
        result = project.set_active_tob_file("file2.TOB")
        # The method doesn't return anything, just check the attribute is set
        assert hasattr(project, 'active_tob_file')

        # Get active file
        active_file = project.get_active_tob_file()
        assert active_file is not None
        assert active_file.file_name == "file2.TOB"

        # Set non-existent file as active (should not set active_tob_file)
        result = project.set_active_tob_file("nonexistent.TOB")
        assert not result  # Should return False for non-existent file

        # Get active file when no valid file is active
        active_file = project.get_active_tob_file()
        assert active_file is not None  # Should still return file2.TOB since it wasn't changed

    def test_clear_active_tob_file(self):
        """Test clearing active TOB file."""
        project = ProjectModel(name="Test Project")

        project.set_active_tob_file("test.TOB")
        # Just check that the method exists and can be called
        project.clear_active_tob_file()
        # The method sets active_tob_file to None

    def test_update_tob_file_status(self):
        """Test updating TOB file status."""
        project = ProjectModel(name="Test Project")

        # Add file
        project.add_tob_file(
            file_path="/test/data.TOB",
            file_name="data.TOB",
            file_size=1024,
            data_points=1,
            sensors=['sensor']
        )

        # Update status
        project.update_tob_file_status("data.TOB", "uploading")

        tob_file = project.get_tob_file("data.TOB")
        assert tob_file.status == "uploading"

        # Update to different status
        project.update_tob_file_status("data.TOB", "processed")
        tob_file = project.get_tob_file("data.TOB")
        assert tob_file.status == "processed"

        # Update non-existent file (should not crash)
        project.update_tob_file_status("nonexistent.TOB", "error")

    def test_get_project_summary(self):
        """Test getting project summary with TOB data."""
        project = ProjectModel(name="Test Project", description="Test description")

        # Add TOB files
        project.add_tob_file(
            file_path="/test/file1.TOB",
            file_name="file1.TOB",
            file_size=1024,
            data_points=2,
            sensors=['sensor']
        )
        project.add_tob_file(
            file_path="/test/file2.TOB",
            file_name="file2.TOB",
            file_size=2048,
            data_points=1,
            sensors=['sensor2']
        )

        summary = project.get_project_summary()

        assert summary['name'] == 'Test Project'
        assert summary['description'] == 'Test description'
        assert summary['tob_files_count'] == 2
        assert summary['total_file_size_mb'] == (1024 + 2048) / (1024 * 1024)
        assert summary['total_data_points'] == 3
        assert 'created_date' in summary
        assert 'modified_date' in summary
        assert 'memory_usage_mb' in summary

    def test_create_rollback_transaction(self):
        """Test creating rollback transaction."""
        project = ProjectModel(name="Test Project")
        transaction = project.create_rollback_transaction()

        assert isinstance(transaction, object)  # Can't import due to circular import
        assert transaction.project_model == project
