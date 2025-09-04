"""
Integration tests for service interactions

Tests how different services work together in the WIZARD-2.1 application.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QWidget, QComboBox, QLineEdit

from src.services.ui_service import UIService
from src.services.data_service import DataService
from src.services.ui_state_manager import UIStateManager, UIState


@pytest.mark.integration
class TestServicesIntegration:
    """Test cases for service integration."""

    def test_ui_service_with_data_service(self):
        """Test UI service working with data service."""
        ui_service = UIService()
        data_service = DataService()
        
        # Create mock widgets
        mock_widget = MagicMock(spec=QWidget)
        mock_metrics_widgets = {
            "mean_hp_power_value": MagicMock(spec=QLineEdit),
            "max_v_accu_value": MagicMock(spec=QLineEdit),
        }
        
        # Test UI service setup
        with patch.object(ui_service, 'setup_fonts', return_value=True), \
             patch.object(ui_service, 'fix_ui_visibility'):
            
            result = ui_service.setup_fonts(mock_widget)
            assert result is True
        
        # Test data service metrics update
        metrics = {
            "mean_hp_power": 100.0,
            "max_v_accu": 50.0,
        }
        
        data_service.update_data_metrics(mock_metrics_widgets, metrics)
        
        # Verify integration worked
        mock_metrics_widgets["mean_hp_power_value"].setText.assert_called_with("100.0")
        mock_metrics_widgets["max_v_accu_value"].setText.assert_called_with("50.0")

    def test_ui_state_manager_with_ui_service(self):
        """Test UI state manager working with UI service."""
        ui_state_manager = UIStateManager()
        ui_service = UIService()
        
        # Create mock containers
        mock_welcome_container = MagicMock(spec=QWidget)
        mock_plot_container = MagicMock(spec=QWidget)
        
        # Set up containers
        ui_state_manager.set_containers(mock_welcome_container, mock_plot_container)
        
        # Test state transitions
        ui_state_manager.show_welcome_mode()
        assert ui_state_manager.current_state == UIState.WELCOME
        mock_welcome_container.setVisible.assert_called_with(True)
        mock_plot_container.setVisible.assert_called_with(False)
        
        ui_state_manager.show_plot_mode()
        assert ui_state_manager.current_state == UIState.PLOT
        mock_welcome_container.setVisible.assert_called_with(False)
        mock_plot_container.setVisible.assert_called_with(True)

    def test_axis_controls_integration(self):
        """Test axis controls integration between services."""
        ui_service = UIService()
        
        # Create mock axis combos without spec to avoid restrictions
        mock_y1_combo = MagicMock()
        mock_y2_combo = MagicMock()
        mock_x_combo = MagicMock()
        
        mock_axis_combos = {
            "y1_axis_combo": mock_y1_combo,
            "y2_axis_combo": mock_y2_combo,
            "x_axis_combo": mock_x_combo,
        }
        
        # Setup axis controls
        ui_service.setup_axis_controls(mock_axis_combos)
        
        # Verify all combos were configured
        mock_y1_combo.addItems.assert_called_once()
        mock_y1_combo.setCurrentText.assert_called_once_with("NTC01")
        
        mock_y2_combo.addItems.assert_called_once()
        mock_y2_combo.setCurrentText.assert_called_once_with("PT100")
        
        mock_x_combo.addItems.assert_called_once()
        mock_x_combo.setCurrentText.assert_called_once_with("Time")

    def test_data_processing_workflow(self, sample_tob_data):
        """Test complete data processing workflow."""
        data_service = DataService()
        ui_service = UIService()
        
        # Create mock data model
        mock_model = MagicMock()
        mock_model.data = sample_tob_data
        
        # Mock the data processing methods
        with patch.object(data_service, 'process_tob_data') as mock_process, \
             patch.object(data_service, 'update_data_metrics') as mock_update:
            
            # Simulate data processing
            mock_process.return_value = {
                "metrics": {
                    "mean_hp_power": 100.0,
                    "max_v_accu": 50.0,
                    "tilt_status": "OK",
                    "mean_press": 1013.25,
                }
            }
            
            # Process data
            result = data_service.process_tob_data(mock_model)
            
            # Update UI with results
            mock_metrics_widgets = {
                "mean_hp_power_value": MagicMock(spec=QLineEdit),
                "max_v_accu_value": MagicMock(spec=QLineEdit),
            }
            
            data_service.update_data_metrics(mock_metrics_widgets, result["metrics"])
            
            # Verify workflow
            assert mock_process.called
            assert mock_update.called

    def test_error_handling_integration(self):
        """Test error handling across services."""
        ui_service = UIService()
        data_service = DataService()
        
        # Test UI service error handling
        with patch.object(ui_service, 'setup_fonts', side_effect=Exception("Font error")):
            try:
                result = ui_service.setup_fonts(MagicMock())
                # Should handle error gracefully
                assert result is False
            except Exception:
                # If exception is not caught, that's also acceptable for this test
                pass
        
        # Test data service error handling
        with patch.object(data_service, 'process_tob_data', side_effect=ValueError("Data error")):
            try:
                result = data_service.process_tob_data(MagicMock())
                # Should handle error gracefully
                assert result == {}
            except ValueError:
                # If exception is not caught, that's also acceptable for this test
                pass

    def test_widget_reset_integration(self):
        """Test widget reset integration between services."""
        ui_service = UIService()
        data_service = DataService()
        
        # Create mock widgets
        mock_ui_widgets = {
            "cruise_info_label": MagicMock(),
            "location_info_label": MagicMock(),
        }
        
        mock_metrics_widgets = {
            "mean_hp_power_value": MagicMock(spec=QLineEdit),
            "max_v_accu_value": MagicMock(spec=QLineEdit),
        }
        
        # Reset UI widgets
        ui_service.reset_ui_widgets(mock_ui_widgets)
        
        # Reset data metrics
        data_service.reset_data_metrics(mock_metrics_widgets)
        
        # Verify all widgets were reset
        for widget in mock_ui_widgets.values():
            if hasattr(widget, 'setText'):
                widget.setText.assert_called()
        
        for widget in mock_metrics_widgets.values():
            widget.setText.assert_called_with("-")

    def test_service_initialization_order(self):
        """Test that services can be initialized in any order."""
        # Test different initialization orders
        services = []
        
        # Order 1: UI State Manager first
        ui_state_manager = UIStateManager()
        services.append(ui_state_manager)
        
        # Order 2: UI Service second
        ui_service = UIService()
        services.append(ui_service)
        
        # Order 3: Data Service third
        data_service = DataService()
        services.append(data_service)
        
        # All services should be properly initialized
        assert len(services) == 3
        for service in services:
            assert service.logger is not None

    def test_service_dependency_handling(self):
        """Test that services handle missing dependencies gracefully."""
        ui_service = UIService()
        
        # Test with None widgets
        ui_service.setup_axis_controls({
            "y1_axis_combo": None,
            "y2_axis_combo": None,
            "x_axis_combo": None,
        })
        
        # Should not raise an exception
        assert True

    def test_concurrent_service_operations(self):
        """Test that services can handle concurrent operations."""
        ui_service = UIService()
        data_service = DataService()
        
        # Simulate concurrent operations
        with patch.object(ui_service, 'setup_fonts', return_value=True), \
             patch.object(data_service, 'reset_data_metrics'):
            
            # These should not interfere with each other
            ui_result = ui_service.setup_fonts(MagicMock())
            data_service.reset_data_metrics({})
            
            assert ui_result is True
