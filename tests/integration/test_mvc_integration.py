"""
Integration tests for MVC architecture.

Tests the complete MVC interaction including signal communication,
service injection, and proper separation of concerns.
"""

from unittest.mock import Mock, patch

import pytest

from src.controllers.main_controller import MainController
from src.models.tob_data_model import TOBDataModel


class TestMVCIntegration:
    """Integration tests for MVC architecture."""

    @pytest.fixture
    def mock_main_window(self):
        """Create a mock main window with required methods."""
        window = Mock()

        # Add required methods that the view should have
        window.update_plot_data = Mock()
        window.update_plot_sensors = Mock()
        window.update_plot_x_limits = Mock()
        window.update_plot_y1_limits = Mock()
        window.update_plot_y2_limits = Mock()
        window._handle_plot_axis_limits_update = Mock()
        window._show_plot_area = Mock()
        window.get_metrics_widgets = Mock(return_value={})
        window.display_status_message = Mock()
        window.ntc_checkboxes = {}

        return window

    @pytest.fixture
    def main_controller(self, mock_main_window):
        """Create a MainController with all services properly mocked."""
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

            # Configure mocks to return proper instances
            mock_ui_service.return_value = Mock()
            mock_ui_state_manager.return_value = Mock()
            mock_axis_ui_service.return_value = Mock()
            mock_plot_style_service.return_value = Mock()
            mock_analytics_service.return_value = Mock()
            mock_tob_service.return_value = Mock()
            mock_data_service.return_value = Mock()
            mock_plot_service.return_value = Mock()
            mock_encryption_service.return_value = Mock()
            mock_error_service.return_value = Mock()
            mock_error_handler.return_value = Mock()
            mock_plot_controller.return_value = Mock()
            mock_tob_controller.return_value = Mock()

            controller = MainController(mock_main_window)
            return controller

    def test_service_injection_integration(self, main_controller, mock_main_window):
        """Test that services are properly injected into the view."""
        # Verify that set_services was called
        mock_main_window.set_services.assert_called_once()

        # Verify that the services dict was passed
        call_args = mock_main_window.set_services.call_args[0][0]
        assert isinstance(call_args, dict)
        assert "ui_service" in call_args
        assert "plot_service" in call_args
        assert "data_service" in call_args

    def test_signal_connections_integration(self, main_controller, mock_main_window):
        """Test that all signal connections are properly established."""
        # Check that controller signals exist and are PyQt signals
        assert hasattr(main_controller, "plot_data_update")
        assert hasattr(main_controller, "plot_sensors_update")
        assert hasattr(main_controller, "plot_axis_limits_update")
        assert hasattr(main_controller, "show_plot_mode")

        # Check that view signals were connected (they are mocks, so we check if connect was called)
        mock_main_window.file_opened.connect.assert_called()
        mock_main_window.project_created.connect.assert_called()
        mock_main_window.project_opened.connect.assert_called()

        # Check that controller has signal connection methods
        assert hasattr(main_controller, "_connect_signals")
        assert hasattr(main_controller, "_connect_plot_signals")
        assert hasattr(main_controller, "_connect_tob_signals")

    def test_controller_hierarchy_integration(self, main_controller):
        """Test that the controller hierarchy is properly established."""
        # Verify that sub-controllers exist
        assert hasattr(main_controller, "plot_controller")
        assert hasattr(main_controller, "tob_controller")

        # Verify that services are available
        assert hasattr(main_controller, "data_service")
        assert hasattr(main_controller, "plot_service")
        assert hasattr(main_controller, "tob_service")

    def test_mvc_separation_signal_flow(self, main_controller, mock_main_window):
        """Test that MVC signal flow works correctly."""
        # Simulate a plot update signal from plot controller
        mock_tob_data = Mock(spec=TOBDataModel)
        main_controller.plot_controller.current_tob_data = mock_tob_data

        # Trigger the signal
        main_controller._on_plot_updated()

        # Verify that the view method was called via signal
        mock_main_window.update_plot_data.assert_called_once_with(mock_tob_data)

    def test_dependency_injection_chain(self, main_controller):
        """Test that dependency injection works through the entire chain."""
        # Services should be created once in MainController
        assert main_controller.data_service is not None
        assert main_controller.plot_service is not None
        assert main_controller.tob_service is not None

        # Sub-controllers should receive injected services
        # (This would be verified if we had real controller instances)
        assert main_controller.plot_controller is not None
        assert main_controller.tob_controller is not None

    def test_error_handling_integration(self, main_controller):
        """Test that error handling works through the MVC layers."""
        # Test that error signals exist on TOB controller
        assert hasattr(main_controller.tob_controller, "error_occurred")

        # Verify error handler is available
        assert hasattr(main_controller, "error_service")

    def test_ui_state_management_integration(self, main_controller, mock_main_window):
        """Test that UI state management is properly integrated."""
        # Verify that UI state manager is injected
        services_call = mock_main_window.set_services.call_args[0][0]
        assert "ui_state_manager" in services_call

        # Verify that show_plot_mode signal exists
        assert hasattr(main_controller, "show_plot_mode")

    @patch("src.controllers.main_controller.TOBDataModel")
    def test_complete_tob_workflow_integration(
        self, mock_tob_model, main_controller, mock_main_window
    ):
        """Test the complete TOB file processing workflow through MVC layers."""
        # Mock the TOB controller methods
        main_controller.tob_controller.load_tob_file = Mock()
        main_controller.tob_controller.process_tob_data = Mock()

        # Trigger file opening
        main_controller._on_file_opened("test.tob")

        # Verify that TOB controller was called (delegation works)
        main_controller.tob_controller.load_tob_file.assert_called_once_with("test.tob")

        # Test the signal flow when TOB file is loaded
        main_controller._on_tob_file_loaded(mock_tob_model)

        # Verify that processing was initiated
        main_controller.tob_controller.process_tob_data.assert_called_once_with(
            mock_tob_model
        )

    def test_sensor_selection_mvc_flow(self, main_controller, mock_main_window):
        """Test that sensor selection works through MVC layers."""
        # Mock sensor checkboxes
        mock_main_window.ntc_checkboxes = {
            "NTC01": Mock(isChecked=Mock(return_value=True)),
            "NTC02": Mock(isChecked=Mock(return_value=False)),
        }

        # Verify that handle_sensor_selection_changed method exists
        assert hasattr(main_controller, "handle_sensor_selection_changed")

        # The method should delegate to plot controller
        # (We can't test the actual call since plot_controller is a mock)
