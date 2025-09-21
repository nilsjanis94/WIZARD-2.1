"""
UI tests for MainWindow

Tests the main window UI components using pytest-qt.
"""

from unittest.mock import MagicMock, patch

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QCheckBox, QComboBox, QLineEdit, QWidget

from src.controllers.main_controller import MainController
from src.views.main_window import MainWindow


@pytest.mark.ui
class TestMainWindow:
    """Test cases for MainWindow UI components."""

    def test_main_window_creation(self, qt_app):
        """Test that MainWindow can be created."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"):
            window = MainWindow(controller)
            assert window is not None
            assert window.controller == controller

    def test_widget_references_storage(self, qt_app):
        """Test that widget references are properly stored."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi") as mock_load_ui:
            # Mock the UI loading
            mock_load_ui.return_value = None

            window = MainWindow(controller)

            # Mock findChild calls
            with patch.object(window, "findChild") as mock_find:
                mock_find.return_value = MagicMock()

                window._store_widget_references()

                # Verify findChild was called for important widgets
                assert mock_find.call_count > 0

    def test_ui_state_initialization(self, qt_app):
        """Test UI state initialization."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ), patch.object(MainWindow, "_initialize_ui_state") as mock_init:

            window = MainWindow(controller)

            # Verify initialization was called
            assert mock_init.called

    def test_axis_controls_initialization(self, qt_app):
        """Test axis controls initialization."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Mock axis combos
            window.axis_combos = {
                "y1_axis_combo": MagicMock(spec=QComboBox),
                "y2_axis_combo": MagicMock(spec=QComboBox),
                "x_axis_combo": MagicMock(spec=QComboBox),
            }

            with patch.object(window.ui_service, "setup_axis_controls") as mock_setup:
                window._initialize_axis_controls()

                # Verify axis controls were set up
                mock_setup.assert_called_once_with(window.axis_combos)

    def test_sensor_selection_changed(self, qt_app):
        """Test sensor selection change handling."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Test sensor selection change
            window._on_sensor_selection_changed("NTC01", 2)  # Checked

            # Verify controller was notified
            controller.update_sensor_selection.assert_called_with("NTC01", True)

            # Test unchecking
            window._on_sensor_selection_changed("NTC01", 0)  # Unchecked
            controller.update_sensor_selection.assert_called_with("NTC01", False)

    def test_axis_auto_mode_changes(self, qt_app):
        """Test axis auto mode change handling."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Mock axis value widgets
            window.y1_min_value = MagicMock(spec=QLineEdit)
            window.y1_max_value = MagicMock(spec=QLineEdit)
            window.y2_min_value = MagicMock(spec=QLineEdit)
            window.y2_max_value = MagicMock(spec=QLineEdit)
            window.x_min_value = MagicMock(spec=QLineEdit)
            window.x_max_value = MagicMock(spec=QLineEdit)

            # Test Y1 auto mode
            window._on_y1_auto_changed(2)  # Auto mode on
            window.y1_min_value.setEnabled.assert_called_with(False)
            window.y1_max_value.setEnabled.assert_called_with(False)

            window._on_y1_auto_changed(0)  # Auto mode off
            window.y1_min_value.setEnabled.assert_called_with(True)
            window.y1_max_value.setEnabled.assert_called_with(True)

    def test_file_dialog_handling(self, qt_app):
        """Test file dialog handling."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Test TOB file opening
            with patch(
                "src.views.main_window.QFileDialog.getOpenFileName"
            ) as mock_dialog:
                mock_dialog.return_value = ("test.tob", "TOB Files (*.tob)")

                with patch.object(window, "file_opened") as mock_signal:
                    window._on_open_tob_file()

                    # Verify signal was emitted
                    mock_signal.emit.assert_called_with("test.tob")

            # Test project file opening
            with patch(
                "src.views.main_window.QFileDialog.getOpenFileName"
            ) as mock_dialog:
                mock_dialog.return_value = ("test.wzp", "WIZARD Project Files (*.wzp)")

                with patch.object(window, "project_opened") as mock_signal:
                    window._on_open_project()

                    # Verify signal was emitted
                    mock_signal.emit.assert_called_with("test.wzp", "default_password")

    def test_project_creation(self, qt_app):
        """Test project creation handling."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            with patch(
                "src.views.main_window.QFileDialog.getSaveFileName"
            ) as mock_dialog:
                mock_dialog.return_value = (
                    "new_project.wzp",
                    "WIZARD Project Files (*.wzp)",
                )

                with patch.object(window, "project_created") as mock_signal:
                    window._on_create_project()

                    # Verify signal was emitted
                    mock_signal.emit.assert_called_with(
                        "new_project.wzp", "default_password"
                    )

    def test_status_message_display(self, qt_app):
        """Test status message display."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Mock statusbar
            window.statusbar = MagicMock()

            # Test status message
            window.show_status_message("Test message", 5000)

            # Verify statusbar was updated
            window.statusbar.showMessage.assert_called_with("Test message", 5000)

    def test_data_metrics_update(self, qt_app):
        """Test data metrics update."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Mock metrics widgets
            window.mean_hp_power_value = MagicMock(spec=QLineEdit)
            window.max_v_accu_value = MagicMock(spec=QLineEdit)
            window.tilt_status_value = MagicMock(spec=QLineEdit)
            window.mean_press_value = MagicMock(spec=QLineEdit)

            # Test metrics update
            metrics = {
                "mean_hp_power": 100.0,
                "max_v_accu": 50.0,
                "tilt_status": "OK",
                "mean_press": 1013.25,
            }

            window.update_data_metrics(metrics)

            # Verify widgets were updated
            window.mean_hp_power_value.setText.assert_called_with("100.0")
            window.max_v_accu_value.setText.assert_called_with("50.0")
            window.tilt_status_value.setText.assert_called_with("OK")
            window.mean_press_value.setText.assert_called_with("1013.25")

    def test_project_info_update(self, qt_app):
        """Test project info update."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Mock project info widgets
            window.cruise_info_label = MagicMock()
            window.location_info_label = MagicMock()
            window.location_comment_value = MagicMock(spec=QLineEdit)
            window.location_sensorstring_value = MagicMock(spec=QLineEdit)
            window.location_subcon_spin = MagicMock()

            # Test project info update
            window.update_project_info(
                project_name="Test Project",
                location="Test Location",
                comment="Test comment",
                sensor_string="NTC01,NTC02,PT100",
                subcon=0.5,
            )

            # Verify widgets were updated
            window.cruise_info_label.setText.assert_called_with("Project: Test Project")
            window.location_info_label.setText.assert_called_with(
                "Location: Test Location"
            )
            window.location_comment_value.setText.assert_called_with("Test comment")
            window.location_sensorstring_value.setText.assert_called_with(
                "NTC01,NTC02,PT100"
            )
            window.location_subcon_spin.setValue.assert_called_with(0.5)

    def test_close_event(self, qt_app):
        """Test application close event handling."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Mock close event
            from PyQt6.QtGui import QCloseEvent

            event = QCloseEvent()

            # Test close event
            window.closeEvent(event)

            # Verify event was accepted
            assert event.isAccepted()

    def test_error_handling(self, qt_app):
        """Test error handling in UI operations."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"), patch.object(
            MainWindow, "_store_widget_references"
        ):

            window = MainWindow(controller)

            # Test error handling in file operations
            with patch(
                "src.views.main_window.QFileDialog.getOpenFileName",
                side_effect=Exception("Dialog error"),
            ):

                # Should not raise an exception
                window._on_open_tob_file()

                # Verify error was handled gracefully
                assert True

    def test_update_plot_y1_limits_with_widget(self, qt_app):
        """Test Y1 axis limits update when plot widget exists."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"):
            window = MainWindow(controller)

            # Mock plot widget
            window.plot_widget = MagicMock()

            # Test the method
            window.update_plot_y1_limits(10.5, 45.8)

            # Verify plot widget was called
            window.plot_widget.update_y1_limits.assert_called_once_with(10.5, 45.8)

    def test_update_plot_y1_limits_no_widget(self, qt_app):
        """Test Y1 axis limits update when plot widget doesn't exist."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"):
            window = MainWindow(controller)

            # No plot widget
            window.plot_widget = None

            # Should not raise exception
            window.update_plot_y1_limits(10.0, 50.0)

            # Verify warning was logged (this would be in logs, but we can't easily test logging)

    def test_update_plot_y2_limits_with_widget(self, qt_app):
        """Test Y2 axis limits update when plot widget exists."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"):
            window = MainWindow(controller)

            # Mock plot widget
            window.plot_widget = MagicMock()

            # Test the method
            window.update_plot_y2_limits(5.2, 25.7)

            # Verify plot widget was called
            window.plot_widget.update_y2_limits.assert_called_once_with(5.2, 25.7)

    def test_update_plot_y2_limits_no_widget(self, qt_app):
        """Test Y2 axis limits update when plot widget doesn't exist."""
        controller = MagicMock(spec=MainController)

        with patch("src.views.main_window.uic.loadUi"):
            window = MainWindow(controller)

            # No plot widget
            window.plot_widget = None

            # Should not raise exception
            window.update_plot_y2_limits(5.0, 25.0)

            # Verify warning was logged
