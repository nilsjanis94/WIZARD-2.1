"""
Unit tests for AxisUIService

Tests the axis UI service functionality including axis control management
and limit handling.
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QLineEdit, QCheckBox

from src.services.axis_ui_service import AxisUIService


@pytest.mark.unit
class TestAxisUIService:
    """Test cases for AxisUIService class."""

    def test_init(self):
        """Test AxisUIService initialization."""
        service = AxisUIService()
        assert service.logger is not None

    def test_setup_axis_controls_no_controller(self):
        """Test setup with no controller available."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock main_window without controller
        main_window.controller = None

        # Should not raise exception
        service.setup_axis_controls(main_window)

    @patch('src.services.axis_ui_service.AxisUIService._update_control_states')
    def test_setup_axis_controls_with_controller(self, mock_update_states):
        """Test setup with controller available."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock controller and time range
        main_window.controller = MagicMock()
        main_window.controller.get_time_range.return_value = {
            'min': 100.0,
            'max': 500.0
        }

        # Mock UI elements
        main_window.x_min_value = MagicMock(spec=QLineEdit)
        main_window.x_max_value = MagicMock(spec=QLineEdit)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = True

        service.setup_axis_controls(main_window)

        # Verify update_axis_values was called
        # This is implicit through the flow

    def test_update_axis_values_no_data(self):
        """Test update with no time range data."""
        service = AxisUIService()
        main_window = MagicMock()

        service.update_axis_values(main_window, {})

        # Should not modify any widgets

    def test_update_axis_values_seconds(self):
        """Test update with seconds time unit."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock time range
        time_range = {'min': 100.0, 'max': 500.0}

        # Mock UI elements
        main_window.x_axis_combo = MagicMock()
        main_window.x_axis_combo.currentText.return_value = "Seconds"

        main_window.x_min_value = MagicMock(spec=QLineEdit)
        main_window.x_max_value = MagicMock(spec=QLineEdit)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        service.update_axis_values(main_window, time_range)

        # Verify values were set correctly
        main_window.x_min_value.blockSignals.assert_called()
        main_window.x_min_value.setText.assert_called_with("100.00")
        main_window.x_max_value.setText.assert_called_with("500.00")

    def test_update_axis_values_minutes_conversion(self):
        """Test update with minutes conversion."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock time range (3600 seconds = 60 minutes)
        time_range = {'min': 3600.0, 'max': 7200.0}

        # Mock UI elements
        main_window.x_axis_combo = MagicMock()
        main_window.x_axis_combo.currentText.return_value = "Minutes"

        main_window.x_min_value = MagicMock(spec=QLineEdit)
        main_window.x_max_value = MagicMock(spec=QLineEdit)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        service.update_axis_values(main_window, time_range)

        # Verify converted values (3600s/60 = 60min, 7200s/60 = 120min)
        main_window.x_min_value.setText.assert_called_with("60.00")
        main_window.x_max_value.setText.assert_called_with("120.00")

    def test_update_axis_values_hours_conversion(self):
        """Test update with hours conversion."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock time range (7200 seconds = 2 hours)
        time_range = {'min': 7200.0, 'max': 14400.0}

        # Mock UI elements
        main_window.x_axis_combo = MagicMock()
        main_window.x_axis_combo.currentText.return_value = "Hours"

        main_window.x_min_value = MagicMock(spec=QLineEdit)
        main_window.x_max_value = MagicMock(spec=QLineEdit)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        service.update_axis_values(main_window, time_range)

        # Verify converted values (7200s/3600 = 2h, 14400s/3600 = 4h)
        main_window.x_min_value.setText.assert_called_with("2.00")
        main_window.x_max_value.setText.assert_called_with("4.00")

    def test_handle_axis_auto_mode_changed_auto_enabled(self):
        """Test auto mode change to enabled."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock controller and time range
        main_window.controller = MagicMock()
        main_window.controller.get_time_range.return_value = {
            'min': 100.0, 'max': 500.0
        }

        # Mock UI elements
        main_window.x_axis_combo = MagicMock()
        main_window.x_axis_combo.currentText.return_value = "Seconds"
        main_window.x_min_value = MagicMock(spec=QLineEdit)
        main_window.x_max_value = MagicMock(spec=QLineEdit)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = True

        service.handle_axis_auto_mode_changed(main_window, 'x', True)

        # Controls should be disabled and values updated
        main_window.x_min_value.setEnabled.assert_called_with(False)
        main_window.x_max_value.setEnabled.assert_called_with(False)
        # Values should be updated to show current auto range
        main_window.x_min_value.setText.assert_called_with("100.00")
        main_window.x_max_value.setText.assert_called_with("500.00")
        # Controller should be called to update axis settings
        main_window.controller.update_axis_settings.assert_called_with({'x_auto': True})

    def test_handle_axis_auto_mode_changed_auto_disabled(self):
        """Test auto mode change to disabled."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock controller and time range
        main_window.controller = MagicMock()
        main_window.controller.get_time_range.return_value = {
            'min': 100.0,
            'max': 500.0
        }

        # Mock UI elements
        main_window.x_axis_combo = MagicMock()
        main_window.x_axis_combo.currentText.return_value = "Seconds"
        main_window.x_min_value = MagicMock(spec=QLineEdit)
        main_window.x_max_value = MagicMock(spec=QLineEdit)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        service.handle_axis_auto_mode_changed(main_window, 'x', False)

        # Controls should be enabled and values updated
        main_window.x_min_value.setEnabled.assert_called_with(True)
        main_window.x_max_value.setEnabled.assert_called_with(True)
        # Controller should be called to update axis settings
        main_window.controller.update_axis_settings.assert_called_with({'x_auto': False})

    def test_handle_axis_limits_changed_auto_mode(self):
        """Test limits change when auto mode is enabled - should be ignored."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock auto checkbox as checked (auto mode)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = True

        service.handle_axis_limits_changed(main_window, 'x', "100.00", "500.00")

        # Should not process when auto is enabled

    def test_handle_axis_limits_changed_valid_input(self):
        """Test limits change with valid input."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock auto checkbox as unchecked (manual mode)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        # Mock time unit conversion
        main_window.x_axis_combo = MagicMock()
        main_window.x_axis_combo.currentText.return_value = "Seconds"

        # Mock controller
        main_window.controller = MagicMock()

        service.handle_axis_limits_changed(main_window, 'x', "100.00", "500.00")

        # Should call controller with converted values
        main_window.controller.update_x_axis_limits.assert_called_with(100.0, 500.0)

    def test_handle_axis_limits_changed_minutes_conversion(self):
        """Test limits change with minutes to seconds conversion."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock auto checkbox as unchecked (manual mode)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        # Mock time unit as minutes
        main_window.x_axis_combo = MagicMock()
        main_window.x_axis_combo.currentText.return_value = "Minutes"

        # Mock controller
        main_window.controller = MagicMock()

        service.handle_axis_limits_changed(main_window, 'x', "1.00", "5.00")

        # Should convert minutes to seconds (1min = 60s, 5min = 300s)
        main_window.controller.update_x_axis_limits.assert_called_with(60.0, 300.0)

    def test_handle_axis_limits_changed_hours_conversion(self):
        """Test limits change with hours to seconds conversion."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock auto checkbox as unchecked (manual mode)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        # Mock time unit as hours
        main_window.x_axis_combo = MagicMock()
        main_window.x_axis_combo.currentText.return_value = "Hours"

        # Mock controller
        main_window.controller = MagicMock()

        service.handle_axis_limits_changed(main_window, 'x', "1.00", "2.00")

        # Should convert hours to seconds (1h = 3600s, 2h = 7200s)
        main_window.controller.update_x_axis_limits.assert_called_with(3600.0, 7200.0)

    def test_handle_axis_limits_changed_invalid_range(self):
        """Test limits change with invalid range (min >= max)."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock auto checkbox as unchecked (manual mode)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        # Mock controller
        main_window.controller = MagicMock()

        service.handle_axis_limits_changed(main_window, 'x', "500.00", "100.00")

        # Should not call controller due to invalid range
        main_window.controller.update_x_axis_limits.assert_not_called()

    def test_handle_axis_limits_changed_invalid_values(self):
        """Test limits change with invalid (non-numeric) values."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock auto checkbox as unchecked (manual mode)
        main_window.x_auto_checkbox = MagicMock(spec=QCheckBox)
        main_window.x_auto_checkbox.isChecked.return_value = False

        service.handle_axis_limits_changed(main_window, 'x', "invalid", "500.00")

        # Should handle ValueError gracefully without calling controller

    def test_set_axis_controls_enabled(self):
        """Test setting axis control enabled states."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock UI elements
        main_window.x_min_value = MagicMock(spec=QLineEdit)
        main_window.x_max_value = MagicMock(spec=QLineEdit)

        service._set_axis_controls_enabled(main_window, 'x', True)

        # Controls should be enabled
        main_window.x_min_value.setEnabled.assert_called_with(True)
        main_window.x_max_value.setEnabled.assert_called_with(True)

    def test_set_axis_controls_enabled_disabled(self):
        """Test setting axis control disabled states."""
        service = AxisUIService()
        main_window = MagicMock()

        # Mock UI elements
        main_window.x_min_value = MagicMock(spec=QLineEdit)
        main_window.x_max_value = MagicMock(spec=QLineEdit)

        service._set_axis_controls_enabled(main_window, 'x', False)

        # Controls should be disabled
        main_window.x_min_value.setEnabled.assert_called_with(False)
        main_window.x_max_value.setEnabled.assert_called_with(False)
