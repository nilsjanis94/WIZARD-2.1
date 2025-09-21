"""
Axis UI Service for WIZARD-2.1

Handles axis control UI logic including auto/manual mode switching,
value updates, and limit validation.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

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

    def setup_axis_controls(self, main_window: "MainWindow") -> None:
        """
        Initialize axis control widgets and their states.

        Args:
            main_window: Main window instance with axis controls
        """
        try:
            # Get current data range for initial values
            time_range = None
            if hasattr(main_window, "controller") and main_window.controller:
                time_range = main_window.controller.get_time_range()

            if time_range:
                # Show current auto range in UI controls
                self.update_axis_values(main_window, time_range)

            # Set initial control states based on auto checkboxes
            self._update_control_states(main_window)

            self.logger.debug("Axis controls initialized successfully")

        except Exception as e:
            self.logger.error("Failed to setup axis controls: %s", e)
            raise

    def update_axis_values(
        self, main_window: "MainWindow", time_range: Dict[str, Any]
    ) -> None:
        """
        Update axis control values with new time range data.

        Args:
            main_window: Main window instance
            time_range: Dictionary with min/max time values
        """
        try:
            # Update X-axis values if time_range provided
            if time_range and "min" in time_range and "max" in time_range:
                # Get current time unit
                time_unit = "Seconds"
                if hasattr(main_window, "x_axis_combo") and main_window.x_axis_combo:
                    current_text = main_window.x_axis_combo.currentText()
                    if current_text:
                        time_unit = current_text

                # Convert time values
                min_value = float(time_range["min"])
                max_value = float(time_range["max"])

                if time_unit == "Minutes":
                    min_value = min_value / 60.0
                    max_value = max_value / 60.0
                elif time_unit == "Hours":
                    min_value = min_value / 3600.0
                    max_value = max_value / 3600.0

                # Update X-axis values (always show, enable/disable based on auto mode)
                if hasattr(main_window, "x_min_value") and main_window.x_min_value:
                    main_window.x_min_value.blockSignals(True)
                    main_window.x_min_value.setText(f"{min_value:.2f}")
                    main_window.x_min_value.blockSignals(False)

                if hasattr(main_window, "x_max_value") and main_window.x_max_value:
                    main_window.x_max_value.blockSignals(True)
                    main_window.x_max_value.setText(f"{max_value:.2f}")
                    main_window.x_max_value.blockSignals(False)

                self.logger.debug(
                    "X-axis values updated: min=%.2f, max=%.2f (%s)",
                    min_value,
                    max_value,
                    time_unit,
                )

            # Update Y-axis values from current plot limits (if plot exists and axes are in manual mode)
            self._update_y_axes_from_plot(main_window)

            # Update control states
            self._update_control_states(main_window)

        except Exception as e:
            self.logger.error("Failed to update axis values: %s", e)

    def handle_axis_auto_mode_changed(
        self, main_window: "MainWindow", axis: str, is_auto: bool
    ) -> None:
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

            # Update axis auto mode setting and handle mode switching
            if (
                axis == "x"
                and hasattr(main_window, "controller")
                and main_window.controller
            ):
                main_window.controller.update_axis_settings({"x_auto": is_auto})

                # When switching modes, ensure values are updated and plot is refreshed
                if is_auto:
                    # In auto mode, show the auto-calculated range
                    time_range = main_window.controller.get_time_range()
                    if time_range:
                        self.update_axis_values(main_window, time_range)
                else:
                    # In manual mode, show the current plot limits in the selected time unit
                    self._update_manual_values_from_plot(main_window, "x")

            elif (
                axis in ["y1", "y2"]
                and hasattr(main_window, "controller")
                and main_window.controller
            ):
                # Update axis auto mode setting
                axis_setting_key = f"{axis}_auto"
                main_window.controller.update_axis_settings({axis_setting_key: is_auto})

                # When switching modes, ensure values are updated and plot is refreshed
                if is_auto:
                    # In auto mode, the plot has been auto-scaled, update LineEdits with new auto values
                    self._update_y_axes_from_plot(main_window)
                else:
                    # In manual mode, show the current plot limits
                    self._update_manual_values_from_plot(main_window, axis)

            self.logger.debug("Axis %s auto mode changed: %s", axis, is_auto)

        except Exception as e:
            self.logger.error("Failed to handle axis auto mode change: %s", e)

    def handle_axis_limits_changed(
        self, main_window: "MainWindow", axis: str, min_text: str, max_text: str
    ) -> None:
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
            if axis == "x":
                if (
                    hasattr(main_window, "x_auto_checkbox")
                    and main_window.x_auto_checkbox
                    and main_window.x_auto_checkbox.isChecked()
                ):
                    return
            elif axis == "y1":
                if (
                    hasattr(main_window, "y1_auto_checkbox")
                    and main_window.y1_auto_checkbox
                    and main_window.y1_auto_checkbox.isChecked()
                ):
                    return
            elif axis == "y2":
                if (
                    hasattr(main_window, "y2_auto_checkbox")
                    and main_window.y2_auto_checkbox
                    and main_window.y2_auto_checkbox.isChecked()
                ):
                    return

            if not min_text or not max_text:
                return

            # Validate and convert values
            try:
                min_value = float(min_text)
                max_value = float(max_text)

                # Basic validation
                if min_value >= max_value:
                    self.logger.warning(
                        "Invalid %s range: min (%.2f) must be less than max (%.2f)",
                        axis,
                        min_value,
                        max_value,
                    )
                    return

                # Handle different axes
                if axis == "x":
                    time_unit = "Seconds"
                    if (
                        hasattr(main_window, "x_axis_combo")
                        and main_window.x_axis_combo
                    ):
                        current_text = main_window.x_axis_combo.currentText()
                        if current_text:
                            time_unit = current_text

                    # The plot data is already converted to the display unit by format_time_axis
                    # So we send the values directly in the display unit

                    # Send to controller - values are already in the correct unit for the plot
                    if hasattr(main_window, "controller") and main_window.controller:
                        main_window.controller.update_x_axis_limits(
                            min_value, max_value
                        )
                        self.logger.debug(
                            "X-axis limits updated: min=%.2f, max=%.2f (%s)",
                            min_value,
                            max_value,
                            time_unit,
                        )

                elif axis in ["y1", "y2"]:
                    # For Y-axes, send values directly to controller (no unit conversion needed)
                    if hasattr(main_window, "controller") and main_window.controller:
                        if axis == "y1":
                            main_window.controller.update_y1_axis_limits(
                                min_value, max_value
                            )
                        elif axis == "y2":
                            main_window.controller.update_y2_axis_limits(
                                min_value, max_value
                            )
                        self.logger.debug(
                            "%s-axis limits updated: min=%.2f, max=%.2f",
                            axis.upper(),
                            min_value,
                            max_value,
                        )

            except ValueError:
                self.logger.warning(
                    "Invalid %s limit values: min='%s', max='%s'",
                    axis,
                    min_text,
                    max_text,
                )

        except Exception as e:
            self.logger.error("Failed to handle %s axis limits change: %s", axis, e)

    def _update_y_axes_from_plot(self, main_window: "MainWindow") -> None:
        """
        Update Y-axis control values from current plot limits.

        Updates axes that are currently in manual mode, or always for initial setup.
        """
        try:
            if not hasattr(main_window, "plot_widget") or not main_window.plot_widget:
                return

            # Update Y1 axis values from current plot limits
            ylim1 = main_window.plot_widget.ax1.get_ylim()
            y1_min, y1_max = ylim1

            if hasattr(main_window, "y1_min_value") and main_window.y1_min_value:
                main_window.y1_min_value.blockSignals(True)
                main_window.y1_min_value.setText(f"{y1_min:.2f}")
                main_window.y1_min_value.blockSignals(False)

            if hasattr(main_window, "y1_max_value") and main_window.y1_max_value:
                main_window.y1_max_value.blockSignals(True)
                main_window.y1_max_value.setText(f"{y1_max:.2f}")
                main_window.y1_max_value.blockSignals(False)

            self.logger.debug(
                "Y1-axis values updated from plot: min=%.2f, max=%.2f", y1_min, y1_max
            )

            # Update Y2 axis values if ax2 exists
            if hasattr(main_window.plot_widget, "ax2") and main_window.plot_widget.ax2:
                ylim2 = main_window.plot_widget.ax2.get_ylim()
                y2_min, y2_max = ylim2

                if hasattr(main_window, "y2_min_value") and main_window.y2_min_value:
                    main_window.y2_min_value.blockSignals(True)
                    main_window.y2_min_value.setText(f"{y2_min:.2f}")
                    main_window.y2_min_value.blockSignals(False)

                if hasattr(main_window, "y2_max_value") and main_window.y2_max_value:
                    main_window.y2_max_value.blockSignals(True)
                    main_window.y2_max_value.setText(f"{y2_max:.2f}")
                    main_window.y2_max_value.blockSignals(False)

                self.logger.debug(
                    "Y2-axis values updated from plot: min=%.2f, max=%.2f",
                    y2_min,
                    y2_max,
                )

        except Exception as e:
            self.logger.error("Failed to update Y-axes from plot: %s", e)

    def _update_control_states(self, main_window: "MainWindow") -> None:
        """
        Update the enabled/disabled state of all axis controls.

        Args:
            main_window: Main window instance
        """
        try:
            # X-axis controls
            if hasattr(main_window, "x_auto_checkbox") and main_window.x_auto_checkbox:
                x_auto = main_window.x_auto_checkbox.isChecked()
                self._set_axis_controls_enabled(main_window, "x", not x_auto)

            # Y1-axis controls
            if (
                hasattr(main_window, "y1_auto_checkbox")
                and main_window.y1_auto_checkbox
            ):
                y1_auto = main_window.y1_auto_checkbox.isChecked()
                self._set_axis_controls_enabled(main_window, "y1", not y1_auto)

            # Y2-axis controls
            if (
                hasattr(main_window, "y2_auto_checkbox")
                and main_window.y2_auto_checkbox
            ):
                y2_auto = main_window.y2_auto_checkbox.isChecked()
                self._set_axis_controls_enabled(main_window, "y2", not y2_auto)

        except Exception as e:
            self.logger.error("Failed to update control states: %s", e)

    def _set_axis_controls_enabled(
        self, main_window: "MainWindow", axis: str, enabled: bool
    ) -> None:
        """
        Set the enabled state for axis controls.

        Args:
            main_window: Main window instance
            axis: Axis identifier ('x', 'y1', 'y2')
            enabled: True to enable controls, False to disable
        """
        try:
            if axis == "x":
                if hasattr(main_window, "x_min_value") and main_window.x_min_value:
                    main_window.x_min_value.setEnabled(enabled)
                if hasattr(main_window, "x_max_value") and main_window.x_max_value:
                    main_window.x_max_value.setEnabled(enabled)
            elif axis == "y1":
                if hasattr(main_window, "y1_min_value") and main_window.y1_min_value:
                    main_window.y1_min_value.setEnabled(enabled)
                if hasattr(main_window, "y1_max_value") and main_window.y1_max_value:
                    main_window.y1_max_value.setEnabled(enabled)
            elif axis == "y2":
                if hasattr(main_window, "y2_min_value") and main_window.y2_min_value:
                    main_window.y2_min_value.setEnabled(enabled)
                if hasattr(main_window, "y2_max_value") and main_window.y2_max_value:
                    main_window.y2_max_value.setEnabled(enabled)

        except Exception as e:
            self.logger.error("Failed to set axis controls enabled state: %s", e)

    def _update_manual_values_from_plot(
        self, main_window: "MainWindow", axis: str
    ) -> None:
        """
        Update manual control values from current plot axis limits for specific axis.

        Args:
            main_window: Main window instance
            axis: Axis to update ('x', 'y1', 'y2')
        """
        try:
            # Get current plot axis limits
            if hasattr(main_window, "plot_widget") and main_window.plot_widget:
                if axis == "x":
                    # Update X-axis values
                    xlim = main_window.plot_widget.ax1.get_xlim()
                    x_min, x_max = xlim

                    # The plot internal values are ALREADY in the display unit (converted by format_time_axis)
                    # So we can use them directly as display values
                    if hasattr(main_window, "x_min_value") and main_window.x_min_value:
                        main_window.x_min_value.blockSignals(True)
                        main_window.x_min_value.setText(f"{x_min:.2f}")
                        main_window.x_min_value.blockSignals(False)

                    if hasattr(main_window, "x_max_value") and main_window.x_max_value:
                        main_window.x_max_value.blockSignals(True)
                        main_window.x_max_value.setText(f"{x_max:.2f}")
                        main_window.x_max_value.blockSignals(False)

                    self.logger.debug(
                        "Updated X-axis manual values from plot: min=%.2f, max=%.2f",
                        x_min,
                        x_max,
                    )

                elif axis == "y1":
                    # Update Y1-axis values
                    ylim1 = main_window.plot_widget.ax1.get_ylim()
                    y1_min, y1_max = ylim1

                    if (
                        hasattr(main_window, "y1_min_value")
                        and main_window.y1_min_value
                    ):
                        main_window.y1_min_value.blockSignals(True)
                        main_window.y1_min_value.setText(f"{y1_min:.2f}")
                        main_window.y1_min_value.blockSignals(False)

                    if (
                        hasattr(main_window, "y1_max_value")
                        and main_window.y1_max_value
                    ):
                        main_window.y1_max_value.blockSignals(True)
                        main_window.y1_max_value.setText(f"{y1_max:.2f}")
                        main_window.y1_max_value.blockSignals(False)

                    self.logger.debug(
                        "Updated Y1-axis manual values from plot: min=%.2f, max=%.2f",
                        y1_min,
                        y1_max,
                    )

                elif axis == "y2":
                    # Update Y2-axis values (if ax2 exists)
                    if (
                        hasattr(main_window.plot_widget, "ax2")
                        and main_window.plot_widget.ax2
                    ):
                        ylim2 = main_window.plot_widget.ax2.get_ylim()
                        y2_min, y2_max = ylim2

                        if (
                            hasattr(main_window, "y2_min_value")
                            and main_window.y2_min_value
                        ):
                            main_window.y2_min_value.blockSignals(True)
                            main_window.y2_min_value.setText(f"{y2_min:.2f}")
                            main_window.y2_min_value.blockSignals(False)

                        if (
                            hasattr(main_window, "y2_max_value")
                            and main_window.y2_max_value
                        ):
                            main_window.y2_max_value.blockSignals(True)
                            main_window.y2_max_value.setText(f"{y2_max:.2f}")
                            main_window.y2_max_value.blockSignals(False)

                        self.logger.debug(
                            "Updated Y2-axis manual values from plot: min=%.2f, max=%.2f",
                            y2_min,
                            y2_max,
                        )
                    else:
                        self.logger.warning("Y2 axis requested but ax2 not available")
            else:
                self.logger.warning("No plot_widget available for manual values update")

        except Exception as e:
            print(f"DEBUG: Exception in _update_manual_values_from_plot: {e}")
            self.logger.error("Failed to update manual values from plot: %s", e)
