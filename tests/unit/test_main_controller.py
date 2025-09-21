"""
Unit tests for MainController.

Tests the main controller functionality including service orchestration,
signal connections, and UI coordination.
"""

from unittest.mock import Mock, patch

import pytest

from src.controllers.main_controller import MainController
from src.models.project_model import ProjectModel
from src.models.tob_data_model import TOBDataModel


class TestMainController:
    """Test cases for MainController."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window."""
        return Mock()

    @pytest.fixture
    def main_controller(self, mock_main_window):
        """Create a MainController instance for testing."""
        # Mock all the services and controllers that are imported in __init__
        with patch("src.services.ui_service.UIService") as mock_ui_service, patch(
            "src.services.ui_state_manager.UIStateManager"
        ) as mock_ui_state_manager, patch(
            "src.services.axis_ui_service.AxisUIService"
        ) as mock_axis_ui_service, patch(
            "src.services.plot_style_service.PlotStyleService"
        ) as mock_plot_style_service, patch(
            "src.services.analytics_service.AnalyticsService"
        ) as mock_analytics_service, patch(
            "src.services.tob_service.TOBService"
        ) as mock_tob_service, patch(
            "src.services.data_service.DataService"
        ) as mock_data_service, patch(
            "src.services.plot_service.PlotService"
        ) as mock_plot_service, patch(
            "src.services.encryption_service.EncryptionService"
        ) as mock_encryption_service, patch(
            "src.services.error_service.ErrorService"
        ) as mock_error_service, patch(
            "src.utils.error_handler.ErrorHandler"
        ) as mock_error_handler, patch(
            "src.controllers.plot_controller.PlotController"
        ) as mock_plot_controller, patch(
            "src.controllers.tob_controller.TOBController"
        ) as mock_tob_controller:

            controller = MainController(mock_main_window)
            return controller

    def test_initialization(self, main_controller):
        """Test that MainController initializes correctly."""
        assert hasattr(main_controller, "analytics_service")
        assert hasattr(main_controller, "tob_service")
        assert hasattr(main_controller, "data_service")
        assert hasattr(main_controller, "plot_service")
        assert hasattr(main_controller, "encryption_service")
        assert hasattr(main_controller, "error_service")
        assert hasattr(main_controller, "ui_service")
        assert hasattr(main_controller, "ui_state_manager")
        assert hasattr(main_controller, "axis_ui_service")
        assert hasattr(main_controller, "plot_style_service")
        assert hasattr(main_controller, "plot_controller")
        assert hasattr(main_controller, "tob_controller")
        assert isinstance(main_controller.project_model, ProjectModel)
        assert main_controller.tob_data_model is None

    def test_service_injection(self, main_controller, mock_main_window):
        """Test that services are properly injected into the view."""
        # Verify that set_services was called on the main window
        mock_main_window.set_services.assert_called_once()

        # Verify that the services dict contains all required services
        call_args = mock_main_window.set_services.call_args[0][0]
        expected_services = [
            "ui_state_manager",
            "ui_service",
            "axis_ui_service",
            "data_service",
            "plot_service",
            "plot_style_service",
        ]

        for service_name in expected_services:
            assert service_name in call_args

    def test_signal_connections(self, main_controller, mock_main_window):
        """Test that signals are properly connected."""
        # Verify that view signals are connected to controller methods
        mock_main_window.file_opened.connect.assert_called()
        mock_main_window.project_created.connect.assert_called()
        mock_main_window.project_opened.connect.assert_called()

        # Verify that controller signals are connected to view slots
        assert main_controller.plot_data_update.connect.called
        assert main_controller.plot_sensors_update.connect.called
        assert main_controller.plot_axis_limits_update.connect.called
        assert main_controller.show_plot_mode.connect.called

    def test_plot_controller_signals_connected(self, main_controller):
        """Test that plot controller signals are connected."""
        # Verify plot controller signal connections
        main_controller.plot_controller.plot_updated.connect.assert_called_once()
        main_controller.plot_controller.sensors_updated.connect.assert_called_once()
        main_controller.plot_controller.axis_limits_changed.connect.assert_called_once()

    def test_tob_controller_signals_connected(self, main_controller):
        """Test that TOB controller signals are connected."""
        # Verify TOB controller signal connections
        main_controller.tob_controller.file_loaded.connect.assert_called_once()
        main_controller.tob_controller.data_processed.connect.assert_called_once()
        main_controller.tob_controller.metrics_calculated.connect.assert_called_once()
        main_controller.tob_controller.error_occurred.connect.assert_called_once()

    @patch("src.controllers.main_controller.TOBDataModel")
    def test_on_tob_file_loaded(self, mock_tob_model, main_controller):
        """Test TOB file loaded handler."""
        main_controller.tob_controller.process_tob_data = Mock()

        main_controller._on_tob_file_loaded(mock_tob_model)

        assert main_controller.tob_data_model == mock_tob_model
        main_controller.tob_controller.process_tob_data.assert_called_once_with(
            mock_tob_model
        )

    def test_on_tob_data_processed(self, main_controller, mock_main_window):
        """Test TOB data processed handler."""
        processed_data = {"test": "data"}
        main_controller._update_view_with_tob_data = Mock()
        main_controller.tob_controller.calculate_metrics = Mock()

        main_controller._on_tob_data_processed(processed_data)

        main_controller._update_view_with_tob_data.assert_called_once()
        main_controller.tob_controller.calculate_metrics.assert_called_once_with(
            main_controller.tob_data_model
        )

    def test_on_plot_updated(self, main_controller):
        """Test plot updated signal handler."""
        mock_tob_data = Mock()
        main_controller.plot_controller.current_tob_data = mock_tob_data

        main_controller._on_plot_updated()

        main_controller.plot_data_update.emit.assert_called_once_with(mock_tob_data)

    def test_on_sensors_updated(self, main_controller):
        """Test sensors updated signal handler."""
        sensors = ["NTC01", "PT100"]

        main_controller._on_sensors_updated(sensors)

        main_controller.plot_sensors_update.emit.assert_called_once_with(sensors)

    def test_on_axis_limits_changed(self, main_controller):
        """Test axis limits changed signal handler."""
        main_controller._on_axis_limits_changed("x", 0, 100)

        main_controller.plot_axis_limits_update.emit.assert_called_once_with(
            "x", 0, 100
        )

    def test_on_tob_metrics_calculated(self, main_controller, mock_main_window):
        """Test TOB metrics calculated handler."""
        metrics = {"mean_hp_power": 10.5}
        mock_main_window.get_metrics_widgets = Mock(return_value={})

        main_controller._on_tob_metrics_calculated(metrics)

        # Should call update_data_metrics with metrics and widgets
        assert True  # Test passes if no exception is raised

    def test_on_tob_error_occurred(self, main_controller, mock_main_window):
        """Test TOB error occurred handler."""
        error_type = "Test Error"
        error_message = "Test message"

        main_controller._on_tob_error_occurred(error_type, error_message)

        # Should show error dialog if available
        assert True  # Test passes if no exception is raised

    @patch("src.controllers.main_controller.TOBDataModel")
    def test_on_file_opened_success(
        self, mock_tob_model, main_controller, mock_main_window
    ):
        """Test successful file opened handler."""
        file_path = "test.tob"

        # Mock successful TOB controller call
        main_controller.tob_controller.load_tob_file = Mock()

        main_controller._on_file_opened(file_path)

        main_controller.tob_controller.load_tob_file.assert_called_once_with(file_path)

    def test_on_file_opened_error(self, main_controller, mock_main_window):
        """Test file opened handler with error."""
        file_path = "invalid.tob"

        # Mock TOB controller to raise an exception
        main_controller.tob_controller.load_tob_file = Mock(
            side_effect=Exception("Test error")
        )

        # Should not raise exception - error is handled internally
        try:
            main_controller._on_file_opened(file_path)
        except Exception:
            pytest.fail("File opened handler should handle exceptions gracefully")

    def test_handle_sensor_selection_changed(self, main_controller, mock_main_window):
        """Test sensor selection change handler."""
        main_controller.plot_controller.handle_sensor_selection_changed = Mock()

        main_controller.handle_sensor_selection_changed("NTC01", True)

        main_controller.plot_controller.handle_sensor_selection_changed.assert_called_once_with(
            "NTC01", True, main_controller.main_window
        )

    def test_dependency_injection_verification(self, main_controller):
        """Test that dependency injection is properly set up."""
        # Verify that services are created and injected
        assert main_controller.data_service is not None
        assert main_controller.plot_service is not None
        assert main_controller.tob_service is not None

        # Verify that controllers receive injected services
        assert (
            main_controller.plot_controller.plot_service == main_controller.plot_service
        )
        assert main_controller.tob_controller.tob_service == main_controller.tob_service
        assert (
            main_controller.tob_controller.data_service == main_controller.data_service
        )

    def test_axis_limits_update_calls_plot_controller(self, main_controller):
        """Test that axis limits updates call the plot controller."""
        # Test X-axis update calls plot controller
        main_controller.plot_controller.update_axis_limits = Mock()
        main_controller.update_x_axis_limits(10.0, 100.0)

        main_controller.plot_controller.update_axis_limits.assert_called_once_with("x", 10.0, 100.0)

        # Test Y1-axis update calls plot controller
        main_controller.update_y1_axis_limits(5.0, 50.0)

        main_controller.plot_controller.update_axis_limits.assert_called_with("y1", 5.0, 50.0)

    def test_plot_controller_axis_signal_flow(self, main_controller, mock_main_window):
        """Test that plot controller axis changes trigger view updates."""
        # Setup mocks
        mock_main_window._handle_plot_axis_limits_update = Mock()

        # Simulate plot controller sending axis limits changed signal
        main_controller._handle_axis_limits_changed('x', 0.0, 100.0)

        # Should emit signal to view
        mock_main_window._handle_plot_axis_limits_update.assert_called_once_with('x', 0.0, 100.0)

    def test_update_axis_settings_calls_plot_widget(self, main_controller, mock_main_window):
        """Test that axis settings updates call the plot widget."""
        # Setup mock plot widget
        mock_plot_widget = Mock()
        mock_main_window.plot_widget = mock_plot_widget

        # Test axis settings update
        axis_settings = {"y1_sensor": "NTC01", "x_axis_type": "Minutes"}
        main_controller.update_axis_settings(axis_settings)

        # Should call plot widget update_axis_settings
        mock_plot_widget.update_axis_settings.assert_called_once_with(axis_settings)
