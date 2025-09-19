"""
Axis UI Service for WIZARD-2.1

Handles axis control UI logic including auto/manual mode switching,
value updates, and limit validation.
"""

import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..views.main_window import MainWindow


class AxisUIService:
    """
    Service for managing axis UI controls and their interactions.

    This service handles the complex logic for axis control widgets,
    including auto/manual mode switching, value updates, and validation.
    """

    def __init__(self):
        """Initialize the Axis UI Service."""
        self.logger = logging.getLogger(__name__)

    def setup_axis_controls(self, main_window: 'MainWindow') -> None:
        """
        Initialize axis control widgets and their states.

        Args:
            main_window: Main window instance with axis controls
        """
        try:
            # Get current data range for initial values
            time_range = None
            if hasattr(main_window, 'controller') and main_window.controller:
                time_range = main_window.controller.get_time_range()

            if time_range:
                self.update_axis_values(main_window, time_range)

            # Set initial control states based on auto checkboxes
            self._update_control_states(main_window)

            self.logger.debug("Axis controls initialized successfully")

        except Exception as e:
            self.logger.error("Failed to setup axis controls: %s", e)
            raise

    def update_axis_values(self, main_window: 'MainWindow', time_range: Dict[str, Any]) -> None:
        """
        Update axis control values with new time range data.

        Args:
            main_window: Main window instance
            time_range: Dictionary with min/max time values
        """
        try:
            if not time_range or 'min' not in time_range or 'max' not in time_range:
                return

            # Get current time unit
            time_unit = "Seconds"
            if hasattr(main_window, 'x_axis_combo') and main_window.x_axis_combo:
                current_text = main_window.x_axis_combo.currentText()
                if current_text:
                    time_unit = current_text

            # Convert time values
            min_value = float(time_range['min'])
            max_value = float(time_range['max'])

            if time_unit == "Minutes":
                min_value = min_value / 60.0
                max_value = max_value / 60.0
            elif time_unit == "Hours":
                min_value = min_value / 3600.0
                max_value = max_value / 3600.0

            # Update X-axis values (always show, enable/disable based on auto mode)
            if hasattr(main_window, 'x_min_value') and main_window.x_min_value:
                main_window.x_min_value.blockSignals(True)
                main_window.x_min_value.setText(f"{min_value:.2f}")
                main_window.x_min_value.blockSignals(False)

            if hasattr(main_window, 'x_max_value') and main_window.x_max_value:
                main_window.x_max_value.blockSignals(True)
                main_window.x_max_value.setText(f"{max_value:.2f}")
                main_window.x_max_value.blockSignals(False)

            # Update control states
            self._update_control_states(main_window)

            self.logger.debug("Axis values updated: min=%.2f, max=%.2f (%s)", min_value, max_value, time_unit)

        except Exception as e:
            self.logger.error("Failed to update axis values: %s", e)

    def handle_axis_auto_mode_changed(self, main_window: 'MainWindow', axis: str, is_auto: bool) -> None:
        """
        Handle auto/manual mode changes for axis controls.

        Args:
            main_window: Main window instance
            axis: Axis identifier ('x', 'y1', 'y2')
            is_auto: True if auto mode is enabled
        """
        try:
            # Update control enable/disable state
            self._set_axis_controls_enabled(main_window, axis, not is_auto)

            # When switching modes, ensure values are updated and plot is refreshed
            if axis == 'x':
                if hasattr(main_window, 'controller') and main_window.controller:
                    time_range = main_window.controller.get_time_range()
                    if time_range:
                        self.update_axis_values(main_window, time_range)

                        # Update axis auto mode setting
                        main_window.controller.update_axis_settings({'x_auto': is_auto})

                        # If switching to manual mode, apply current manual limits
                        if not is_auto:
                            if hasattr(main_window, 'x_min_value') and main_window.x_min_value and \
                               hasattr(main_window, 'x_max_value') and main_window.x_max_value:
                                min_text = main_window.x_min_value.text()
                                max_text = main_window.x_max_value.text()
                                if min_text and max_text:
                                    try:
                                        # Get time unit conversion
                                        time_unit = "Seconds"
                                        if hasattr(main_window, 'x_axis_combo') and main_window.x_axis_combo:
                                            current_text = main_window.x_axis_combo.currentText()
                                            if current_text:
                                                time_unit = current_text

                                        min_val = float(min_text)
                                        max_val = float(max_text)

                                        # Convert to seconds
                                        if time_unit == "Minutes":
                                            min_val *= 60.0
                                            max_val *= 60.0
                                        elif time_unit == "Hours":
                                            min_val *= 3600.0
                                            max_val *= 3600.0

                                        main_window.controller.update_x_axis_limits(min_val, max_val)
                                    except ValueError:
                                        pass  # Ignore invalid values

            self.logger.debug("Axis %s auto mode changed: %s", axis, is_auto)

        except Exception as e:
            self.logger.error("Failed to handle axis auto mode change: %s", e)

    def handle_axis_limits_changed(self, main_window: 'MainWindow', axis: str,
                                 min_text: str, max_text: str) -> None:
        """
        Handle manual changes to axis limits.

        Args:
            main_window: Main window instance
            axis: Axis identifier ('x', 'y1', 'y2')
            min_text: Minimum value as string
            max_text: Maximum value as string
        """
        try:
            # Only process if auto mode is disabled for this axis
            if axis == 'x':
                if (hasattr(main_window, 'x_auto_checkbox') and
                    main_window.x_auto_checkbox and
                    main_window.x_auto_checkbox.isChecked()):
                    return

            if not min_text or not max_text:
                return

            # Validate and convert values
            try:
                min_value = float(min_text)
                max_value = float(max_text)

                # Basic validation
                if min_value >= max_value:
                    self.logger.warning("Invalid %s range: min (%.2f) must be less than max (%.2f)",
                                      axis, min_value, max_value)
                    return

                # Get time unit conversion for X-axis
                if axis == 'x':
                    time_unit = "Seconds"
                    if hasattr(main_window, 'x_axis_combo') and main_window.x_axis_combo:
                        current_text = main_window.x_axis_combo.currentText()
                        if current_text:
                            time_unit = current_text

                    # Convert to seconds for internal use
                    if time_unit == "Minutes":
                        min_value = min_value * 60.0
                        max_value = max_value * 60.0
                    elif time_unit == "Hours":
                        min_value = min_value * 3600.0
                        max_value = max_value * 3600.0

                    # Send to controller
                    if hasattr(main_window, 'controller') and main_window.controller:
                        main_window.controller.update_x_axis_limits(min_value, max_value)
                        self.logger.debug("X-axis limits updated: min=%.2f, max=%.2f (%s)",
                                        min_value, max_value, time_unit)

            except ValueError:
                self.logger.warning("Invalid %s limit values: min='%s', max='%s'",
                                  axis, min_text, max_text)

        except Exception as e:
            self.logger.error("Failed to handle %s axis limits change: %s", axis, e)

    def _update_control_states(self, main_window: 'MainWindow') -> None:
        """
        Update the enabled/disabled state of all axis controls.

        Args:
            main_window: Main window instance
        """
        try:
            # X-axis controls
            if hasattr(main_window, 'x_auto_checkbox') and main_window.x_auto_checkbox:
                x_auto = main_window.x_auto_checkbox.isChecked()
                self._set_axis_controls_enabled(main_window, 'x', not x_auto)

            # Y1-axis controls
            if hasattr(main_window, 'y1_auto_checkbox') and main_window.y1_auto_checkbox:
                y1_auto = main_window.y1_auto_checkbox.isChecked()
                self._set_axis_controls_enabled(main_window, 'y1', not y1_auto)

            # Y2-axis controls
            if hasattr(main_window, 'y2_auto_checkbox') and main_window.y2_auto_checkbox:
                y2_auto = main_window.y2_auto_checkbox.isChecked()
                self._set_axis_controls_enabled(main_window, 'y2', not y2_auto)

        except Exception as e:
            self.logger.error("Failed to update control states: %s", e)

    def _set_axis_controls_enabled(self, main_window: 'MainWindow', axis: str, enabled: bool) -> None:
        """
        Set the enabled state for axis controls.

        Args:
            main_window: Main window instance
            axis: Axis identifier ('x', 'y1', 'y2')
            enabled: True to enable controls, False to disable
        """
        try:
            if axis == 'x':
                if hasattr(main_window, 'x_min_value') and main_window.x_min_value:
                    main_window.x_min_value.setEnabled(enabled)
                if hasattr(main_window, 'x_max_value') and main_window.x_max_value:
                    main_window.x_max_value.setEnabled(enabled)
            elif axis == 'y1':
                if hasattr(main_window, 'y1_min_value') and main_window.y1_min_value:
                    main_window.y1_min_value.setEnabled(enabled)
                if hasattr(main_window, 'y1_max_value') and main_window.y1_max_value:
                    main_window.y1_max_value.setEnabled(enabled)
            elif axis == 'y2':
                if hasattr(main_window, 'y2_min_value') and main_window.y2_min_value:
                    main_window.y2_min_value.setEnabled(enabled)
                if hasattr(main_window, 'y2_max_value') and main_window.y2_max_value:
                    main_window.y2_max_value.setEnabled(enabled)

        except Exception as e:
            self.logger.error("Failed to set axis controls enabled state: %s", e)
