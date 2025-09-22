"""Test cases for RollbackTransaction."""

import pandas as pd
import pytest

from src.models.project_model import ProjectModel, RollbackTransaction


@pytest.mark.unit
class TestRollbackTransaction:
    """Test cases for RollbackTransaction class."""

    def test_init(self):
        """Test RollbackTransaction initialization."""
        project = ProjectModel(name="Test Project")
        transaction = RollbackTransaction(project)

        assert transaction.project_model == project
        assert transaction.backup_tob_files == []
        assert transaction.operations_performed == []
        assert not transaction.rollback_needed

    def test_backup_tob_file(self):
        """Test backing up a TOB file."""
        project = ProjectModel(name="Test Project")

        # Add a TOB file
        test_data = pd.DataFrame({'time': [1, 2], 'sensor': [20.1, 20.5]})
        project.add_tob_file(
            file_path="/test/file.TOB",
            file_name="test.TOB",
            file_size=1024,
            headers={'version': '1.0'},
            dataframe=test_data,
            data_points=2,
            sensors=['sensor']
        )

        transaction = RollbackTransaction(project)

        # Backup the file
        success = transaction.backup_tob_file("test.TOB")
        assert success
        assert len(transaction.backup_tob_files) == 1

        backup = transaction.backup_tob_files[0]
        assert backup['file_name'] == 'test.TOB'
        assert backup['file_path'] == '/test/file.TOB'
        assert backup['data_points'] == 2
        assert backup['sensors'] == ['sensor']
        assert backup['tob_data'] is not None

    def test_backup_nonexistent_file(self):
        """Test backing up a non-existent TOB file."""
        project = ProjectModel(name="Test Project")
        transaction = RollbackTransaction(project)

        success = transaction.backup_tob_file("nonexistent.TOB")
        assert not success
        assert len(transaction.backup_tob_files) == 0

    def test_record_operation(self):
        """Test recording operations."""
        project = ProjectModel(name="Test Project")
        transaction = RollbackTransaction(project)

        transaction.record_operation("Test operation 1")
        transaction.record_operation("Test operation 2")

        assert len(transaction.operations_performed) == 2
        assert transaction.operations_performed[0] == "Test operation 1"
        assert transaction.operations_performed[1] == "Test operation 2"

    def test_successful_transaction(self):
        """Test successful transaction (no rollback)."""
        project = ProjectModel(name="Test Project")
        transaction = RollbackTransaction(project)

        with transaction.transaction():
            # Add a file
            project.add_tob_file(
                file_path="/test/file.TOB",
                file_name="test.TOB",
                file_size=1024,
                data_points=1,
                sensors=['sensor']
            )
            transaction.record_operation("Added file")

        # Transaction should complete without rollback
        assert not transaction.rollback_needed
        assert len(transaction.backup_tob_files) == 0  # Cleared after success
        assert len(project.tob_files) == 1  # File should still exist

    def test_failed_transaction_rollback(self):
        """Test failed transaction with rollback."""
        project = ProjectModel(name="Test Project")

        # Add initial file
        project.add_tob_file(
            file_path="/test/initial.TOB",
            file_name="initial.TOB",
            file_size=512,
            data_points=1,
            sensors=['initial']
        )

        transaction = RollbackTransaction(project)

        try:
            with transaction.transaction():
                # Modify existing file
                test_data = pd.DataFrame({'time': [1], 'sensor': [25.0]})
                project.update_tob_file_data(
                    file_name="initial.TOB",
                    dataframe=test_data,
                    data_points=1,
                    sensors=['modified']
                )
                transaction.record_operation("Modified file")

                # Add new file
                project.add_tob_file(
                    file_path="/test/new.TOB",
                    file_name="new.TOB",
                    file_size=1024,
                    data_points=1,
                    sensors=['new']
                )
                transaction.record_operation("Added new file")

                # Simulate failure
                raise ValueError("Simulated transaction failure")

        except ValueError:
            pass  # Expected

        # Check rollback occurred
        assert transaction.rollback_needed

        # Check that rollback worked
        initial_file = project.get_tob_file("initial.TOB")
        new_file = project.get_tob_file("new.TOB")

        assert initial_file is not None
        assert initial_file.sensors == ['initial']  # Should be restored
        assert initial_file.data_points == 1  # Should be restored
        assert new_file is None  # Should be removed

    def test_rollback_without_backups(self):
        """Test rollback when no backups exist."""
        project = ProjectModel(name="Test Project")
        transaction = RollbackTransaction(project)

        # Add a file after transaction start (should be removed since it's not in initial_tob_files)
        project.add_tob_file(
            file_path="/test/file.TOB",
            file_name="file.TOB",
            file_size=1024,
            data_points=1,
            sensors=['sensor']
        )

        success = transaction.rollback()

        assert success
        # File should be removed since it was added during transaction and not backed up
        assert len(project.tob_files) == 0

    def test_rollback_with_empty_project(self):
        """Test rollback with empty project."""
        project = ProjectModel(name="Test Project")
        transaction = RollbackTransaction(project)

        success = transaction.rollback()
        assert success

    def test_context_manager_exception_handling(self):
        """Test that context manager properly handles exceptions."""
        project = ProjectModel(name="Test Project")
        transaction = RollbackTransaction(project)

        with pytest.raises(RuntimeError):
            with transaction.transaction():
                raise RuntimeError("Test exception")

        # Should have attempted rollback
        assert transaction.rollback_needed
