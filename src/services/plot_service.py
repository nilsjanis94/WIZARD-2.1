"""
Plot service for data visualization in the WIZARD-2.1 application.

This module provides comprehensive plotting functionality for temperature sensor data,
including NTC and PT100 sensors, with interactive controls and professional styling.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import QWidget

from ..models.tob_data_model import TOBDataModel


class PlotService:
    """
    Service for handling data visualization and plotting operations.

    This service provides comprehensive plotting functionality for temperature
    sensor data with professional styling, interactive controls, and support
    for both NTC and PT100 sensors.
    """

    def __init__(self, plot_style_service=None):
        """Initialize the plot service."""
        self.logger = logging.getLogger(__name__)

        # Use provided style service or create default one
        self.plot_style_service = plot_style_service
        if not self.plot_style_service:
            from .plot_style_service import PlotStyleService

            self.plot_style_service = PlotStyleService()

        self.logger.info("PlotService initialized")

    def get_sensor_style(self, sensor_name: str) -> Dict[str, Any]:
        """
        Get the visual style information for a sensor from the style service.

        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'Temp')

        Returns:
            Dictionary with 'color', 'line_style', and 'line_width'
        """
        return self.plot_style_service.get_sensor_style(sensor_name)

    def create_plot_widget(self, parent: QWidget) -> "PlotWidget":
        """
        Create a new plot widget for data visualization.

        Args:
            parent: Parent widget for the plot widget

        Returns:
            PlotWidget: Configured plot widget instance
        """
        try:
            self.logger.info("Creating plot widget with parent: %s", parent)
            plot_widget = PlotWidget(parent, self)
            self.logger.info("Plot widget created successfully")
            return plot_widget
        except Exception as e:
            self.logger.error("Failed to create plot widget: %s", e)
            raise

    def get_sensor_color(self, sensor_name: str) -> str:
        """
        Get the appropriate color for a sensor.

        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'Temp' for PT100)

        Returns:
            str: Color code for the sensor
        """
        style = self.plot_style_service.get_sensor_style(sensor_name)
        return style["color"]

    def get_line_style(self, sensor_name: str) -> str:
        """
        Get the appropriate line style for a sensor.

        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'Temp' for PT100)

        Returns:
            str: Line style for the sensor
        """
        style = self.plot_style_service.get_sensor_style(sensor_name)
        return style["line_style"]

    def get_line_width(self, sensor_name: str) -> float:
        """
        Get the appropriate line width for a sensor.

        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'Temp' for PT100)

        Returns:
            float: Line width for the sensor
        """
        style = self.plot_style_service.get_sensor_style(sensor_name)
        return style["line_width"]

    def format_time_axis(
        self, time_data: pd.Series, time_unit: str = "Seconds"
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Format time data for plotting with different time units.

        Args:
            time_data: Time series data
            time_unit: Time unit ("Seconds", "Minutes", "Hours")

        Returns:
            Tuple of formatted time values and labels
        """
        try:
            if time_data.empty:
                return np.array([]), []

            # Convert time data based on unit
            if time_unit == "Minutes":
                time_values = time_data.values / 60.0
                unit_label = "min"
            elif time_unit == "Hours":
                time_values = time_data.values / 3600.0
                unit_label = "h"
            else:  # Seconds (default)
                time_values = time_data.values
                unit_label = "s"

            # Create time labels (every 10th point for readability)
            step = max(1, len(time_values) // 10)
            time_labels = [
                f"{time_values[i]:.1f}{unit_label}"
                for i in range(0, len(time_values), step)
            ]

            return time_values, time_labels
        except Exception as e:
            self.logger.error("Failed to format time axis: %s", e)
            return np.array([]), []

    def calculate_plot_limits(
        self, data: pd.Series, margin: float = 0.1
    ) -> Tuple[float, float]:
        """
        Calculate appropriate plot limits for data.

        Args:
            data: Data series to calculate limits for
            margin: Margin as fraction of data range

        Returns:
            Tuple of (min_limit, max_limit)
        """
        try:
            if data.empty or data.isna().all():
                return 0.0, 1.0

            data_min = data.min()
            data_max = data.max()
            data_range = data_max - data_min

            if data_range == 0:
                return data_min - 1, data_max + 1

            margin_value = data_range * margin
            return data_min - margin_value, data_max + margin_value
        except Exception as e:
            self.logger.error("Failed to calculate plot limits: %s", e)
            return 0.0, 1.0

    def _get_y_axis_label(self, sensor_name: str) -> str:
        """
        Get the appropriate Y-axis label based on the selected sensor.

        Args:
            sensor_name: Name of the selected sensor

        Returns:
            Appropriate Y-axis label with unit
        """
        # Define labels for different sensor types
        sensor_labels = {
            # NTC sensors
            "NTCs": "Temperature (°C)",
            # Individual NTC sensors also use temperature
            **{f"NTC{i:02d}": "Temperature (°C)" for i in range(1, 23)},
            # PT100
            "Temp": "Temperature (°C)",
            # Voltage sensors
            "Vheat": "Heating Voltage (V)",
            "Vbatt": "Battery Voltage (V)",
            "Vaccu": "Accumulator Voltage (V)",
            # Current sensors
            "Iheat": "Heating Current (A)",
            # Pressure sensors
            "Press": "Pressure (hPa)",
            # Tilt sensors
            "TiltX": "Tilt X-Axis (°)",
            "TiltY": "Tilt Y-Axis (°)",
            "ACCz": "Acceleration Z-Axis (m/s²)",
            # Calculated values
            "HP-Power": "Heating Power (W)",
        }

        return sensor_labels.get(sensor_name, "Value")



class PlotWidget(QWidget):
    """
    Custom plot widget for displaying temperature sensor data.

    This widget integrates matplotlib with PyQt6 to provide interactive
    plotting capabilities for the WIZARD-2.1 application.
    """

    def __init__(self, parent: QWidget, plot_service: PlotService):
        """
        Initialize the plot widget.

        Args:
            parent: Parent widget
            plot_service: Plot service instance for styling and configuration
        """
        super().__init__(parent)
        self.plot_service = plot_service
        self.logger = logging.getLogger(__name__)

        self.logger.info("Initializing PlotWidget...")

        # Data storage
        self.tob_data_model: Optional[TOBDataModel] = None
        self.selected_sensors: List[str] = []
        self.axis_settings: Dict[str, Any] = {
            "x_axis": "Time",
            "y1_axis": "NTC01",
            "y2_axis": "Temp",  # PT100 data is in 'Temp' column
            "x_auto": True,
            "y1_auto": True,
            "y2_auto": True,
        }

        # Plot mode management
        self.plot_mode = "single"  # "single" | "dual"
        self.y1_sensor = "NTC01"   # Primary sensor for main plot
        self.y2_sensor = None      # Secondary sensor for secondary plot (None = disabled)

        # NTC sensor filtering for when y1_sensor == "NTCs"
        self.active_ntc_sensors = None  # None = all NTCs active, or list of active NTCs

        # Matplotlib setup
        self.logger.info("Setting up matplotlib...")
        self._setup_matplotlib()
        self.logger.info("Creating plot canvas...")
        self._create_plot_canvas()
        self.logger.info("Setting up plot layout...")
        self._setup_plot_layout()

        self.logger.info("PlotWidget initialized successfully")

    def _setup_matplotlib(self):
        """Configure matplotlib for professional plotting."""
        try:
            # Set matplotlib style
            plt.style.use("default")

            # Configure matplotlib parameters for better appearance
            plt.rcParams.update(
                {
                    "font.size": 10,
                    "font.family": "sans-serif",
                    "axes.linewidth": 1.2,
                    "axes.grid": True,
                    "grid.alpha": 0.3,
                    "figure.facecolor": "white",
                    "axes.facecolor": "white",
                    "axes.edgecolor": "#333333",
                    "xtick.color": "#333333",
                    "ytick.color": "#333333",
                    "text.color": "#333333",
                    "axes.labelcolor": "#333333",
                    "axes.titlesize": 12,
                    "axes.labelsize": 10,
                    "xtick.labelsize": 9,
                    "ytick.labelsize": 9,
                }
            )

            self.logger.debug("Matplotlib configured successfully")
        except Exception as e:
            self.logger.error("Failed to configure matplotlib: %s", e)
            raise

    def _create_plot_canvas(self):
        """Create the matplotlib canvas with support for dual plots."""
        try:
            # Create figure with subplots
            self.figure = Figure(figsize=(12, 8), dpi=100)
            self.figure.patch.set_facecolor("white")

            # Set tight layout and minimal margins by default
            self.figure.tight_layout(pad=0.5)

            # Create primary subplot (always visible)
            self.ax1 = self.figure.add_subplot(111)

            # Create secondary subplot (initially hidden)
            self.ax2 = None  # Will be created when needed for dual mode

            # Set minimal margins for primary axis
            self.ax1.margins(x=0, y=0.05)

            # Create canvas
            self.canvas = FigureCanvas(self.figure)

            self.logger.debug("Plot canvas created successfully")
        except Exception as e:
            self.logger.error("Failed to create plot canvas: %s", e)
            raise

    def _setup_plot_layout(self):
        """Setup the plot layout and styling."""
        try:
            # Configure axes
            self.ax1.set_xlabel("Time", fontweight="bold")

            # Set initial Y-axis label (will be updated dynamically when sensors are selected)
            if self.selected_sensors:
                primary_sensor = self.selected_sensors[0]
                y_label = self.plot_service._get_y_axis_label(primary_sensor)
            else:
                y_label = "Value"

            self.ax1.set_ylabel(y_label, fontweight="bold", color="black")

            # Set axis colors
            self.ax1.tick_params(axis="y", labelcolor="black")

            # Configure grid
            self.ax1.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

            # Add canvas to existing layout (from UI file)
            if self.layout() is not None:
                # Use existing layout from UI file
                self.layout().addWidget(self.canvas)
                self.logger.debug("Canvas added to existing layout")
            else:
                # Fallback: create new layout if none exists
                from PyQt6.QtWidgets import QVBoxLayout

                layout = QVBoxLayout()
                layout.addWidget(self.canvas)
                self.setLayout(layout)
                self.logger.debug("Canvas added to new layout (fallback)")

            self.logger.debug("Plot layout configured successfully")
        except Exception as e:
            self.logger.error("Failed to setup plot layout: %s", e)
            raise

    def update_data(self, tob_data_model: TOBDataModel):
        """
        Update the plot with new TOB data.

        Args:
            tob_data_model: TOB data model containing sensor data
        """
        try:
            self.tob_data_model = tob_data_model
            self.logger.debug("Plot data updated with TOB model")
            self._refresh_plot()
        except Exception as e:
            self.logger.error("Failed to update plot data: %s", e)
            raise

    def update_sensor_selection(self, selected_sensors: List[str]):
        """
        Update the selected sensors for plotting.

        Args:
            selected_sensors: List of selected sensor names
        """
        try:
            self.logger.debug(
                "PlotWidget: updating sensor selection from %s to %s",
                self.selected_sensors,
                selected_sensors,
            )
            self.selected_sensors = selected_sensors.copy()
            self.logger.debug("Sensor selection updated: %s", selected_sensors)
            self._refresh_plot()
        except Exception as e:
            self.logger.error("Failed to update sensor selection: %s", e)
            raise

    def _refresh_plot(self):
        """Refresh the plot with current data and settings."""
        try:
            if not self.tob_data_model or self.tob_data_model.data is None:
                self._clear_plot()
                return

            # Clear previous plots
            if self.plot_mode == "dual":
                # Clear both axes in dual mode
                self.ax1.clear()
                self.ax2.clear()
                self.logger.debug("Cleared dual plot axes")
            else:
                # Clear only main axis in single mode
                lines_before = len(self.ax1.get_lines())
                self.ax1.clear()
                lines_after_clear = len(self.ax1.get_lines())
                self.logger.debug(
                    "Cleared single plot: %d lines before, %d lines after",
                    lines_before,
                    lines_after_clear,
                )

            # Get time data
            time_data = self.tob_data_model.get_time_column()
            if time_data is None or time_data.empty:
                self._clear_plot()
                return

            # Get time unit from settings
            time_unit = self.axis_settings.get("x_axis_type", "Seconds")

            # Format time axis
            time_values, time_labels = self.plot_service.format_time_axis(
                time_data, time_unit
            )

            # Plot sensors based on current mode
            if self.plot_mode == "dual":
                self._plot_dual_sensors(time_values)
            else:
                self._plot_single_sensor(time_values)

            # Configure axes
            self._configure_axes(time_values, time_unit)

            # Legend removed for cleaner visualization
            # self._add_legend()

            # Refresh canvas - multiple approaches for reliable updates
            self.canvas.draw_idle()
            self.canvas.flush_events()

            # Force Qt event processing to ensure GUI updates
            from PyQt6.QtWidgets import QApplication

            app = QApplication.instance()
            if app:
                app.processEvents()

            # Additional canvas update to ensure changes are visible
            self.canvas.update()
            self.canvas.repaint()  # Force immediate repaint

            # Force figure redraw as additional measure
            self.figure.canvas.draw()
            self.figure.canvas.flush_events()

            self.logger.debug("Plot refreshed successfully")
        except Exception as e:
            self.logger.error("Failed to refresh plot: %s", e)
            raise

    # Delegate axis limit updates to the plot service
    def update_x_limits(self, min_value: float, max_value: float):
        """Delegate X-axis limit updates to plot service."""
        self.plot_service.update_x_limits(min_value, max_value)

    def update_y1_limits(self, min_value: float, max_value: float):
        """Delegate Y1-axis limit updates to plot service."""
        self.plot_service.update_y1_limits(min_value, max_value)

    def update_y2_limits(self, min_value: float, max_value: float):
        """Delegate Y2-axis limit updates to plot service."""
        self.plot_service.update_y2_limits(min_value, max_value)

    def update_axis_settings(self, axis_settings: Dict[str, Any]):
        """Delegate axis settings updates to plot service."""
        self.plot_service.update_axis_settings(axis_settings)

    def _plot_sensors(self, time_values: np.ndarray):
        """Plot the selected sensors."""
        try:
            if not self.tob_data_model or self.tob_data_model.data is None:
                return

            data = self.tob_data_model.data

            for sensor in self.selected_sensors:
                # Special handling for NTCs group - plot all NTC sensors
                if sensor == "NTCs":
                    ntc_sensors = [
                        col
                        for col in data.columns
                        if col.startswith("NTC") and col[3:].isdigit()
                    ]
                    for ntc_sensor in ntc_sensors:
                        if ntc_sensor not in data.columns:
                            continue

                        sensor_data = data[ntc_sensor].dropna()
                        if sensor_data.empty:
                            continue

                        # Get styling for individual NTC sensor
                        color = self.plot_service.get_sensor_color(ntc_sensor)
                        line_style = self.plot_service.get_line_style(ntc_sensor)
                        line_width = self.plot_service.get_line_width(ntc_sensor)

                        # All sensors plot on main axis (ax1)
                        ax = self.ax1

                        # Plot the data
                        ax.plot(
                            time_values[: len(sensor_data)],
                            sensor_data.values,
                            color=color,
                            linestyle=line_style,
                            linewidth=line_width,
                            label=ntc_sensor,
                            alpha=0.8,
                        )

                    continue  # Skip to next sensor in selected_sensors

                # Normal sensor handling
                if sensor not in data.columns:
                    continue

                sensor_data = data[sensor].dropna()
                if sensor_data.empty:
                    continue

                # Get styling
                color = self.plot_service.get_sensor_color(sensor)
                line_style = self.plot_service.get_line_style(sensor)
                line_width = self.plot_service.get_line_width(sensor)

                # All sensors plot on main axis (ax1)
                ax = self.ax1

                # Plot the data
                ax.plot(
                    time_values[: len(sensor_data)],
                    sensor_data.values,
                    color=color,
                    linestyle=line_style,
                    linewidth=line_width,
                    label=sensor,
                    alpha=0.8,
                )

            self.logger.debug("Sensors plotted successfully")
        except Exception as e:
            self.logger.error("Failed to plot sensors: %s", e)
            raise

    def _configure_axes(self, time_values: np.ndarray, time_unit: str = "Seconds"):
        """Configure the plot axes."""
        try:
            # X-axis configuration for both axes (if dual mode)
            if self.axis_settings.get("x_auto", True):
                # Always start from 0, not from data minimum
                if len(time_values) > 0:
                    x_max = time_values.max()
                    self.ax1.set_xlim(0, x_max)
                    if self.plot_mode == "dual" and hasattr(self, 'ax2'):
                        self.ax2.set_xlim(0, x_max)  # Sync x-axis in dual mode
                else:
                    self.ax1.set_xlim(auto=True)
                    if self.plot_mode == "dual" and hasattr(self, 'ax2'):
                        self.ax2.set_xlim(auto=True)
            else:
                # Manual x-axis limits would be set here
                pass

            # Y-axis configuration for primary axis (ax1)
            if self.axis_settings.get("y1_auto", True):
                self.ax1.set_ylim(auto=True)
            else:
                # Manual y1-axis limits would be set here
                pass

            # Configure secondary axis in dual mode
            if self.plot_mode == "dual" and hasattr(self, 'ax2'):
                if self.axis_settings.get("y2_auto", True):
                    self.ax2.set_ylim(auto=True)
                else:
                    # Manual y2-axis limits would be set here
                    pass

            # Set labels based on current sensors
            x_label = f"Time ({time_unit})"

            if self.plot_mode == "dual":
                # Dual mode: X-label only on bottom plot
                self.ax1.set_xlabel("")  # No x-label on top plot
                self.ax2.set_xlabel(x_label, fontweight="bold")

                # Y-labels for both plots
                if self.y1_sensor:
                    if self.y1_sensor == "NTCs":
                        y1_label = "Temperature (°C)"  # All NTC sensors are temperature
                    else:
                        y1_label = self.plot_service._get_y_axis_label(self.y1_sensor)
                    self.ax1.set_ylabel(y1_label, fontweight="bold", color="black")

                if self.y2_sensor:
                    if self.y2_sensor == "NTCs":
                        y2_label = "Temperature (°C)"  # All NTC sensors are temperature
                    else:
                        y2_label = self.plot_service._get_y_axis_label(self.y2_sensor)
                    self.ax2.set_ylabel(y2_label, fontweight="bold", color="black")

                # Configure grids for both axes
                self.ax1.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)
                self.ax2.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

                # Set margins
                self.ax1.margins(x=0, y=0.05)  # No bottom margin for top plot
                self.ax2.margins(x=0, y=0.05)  # No top margin for bottom plot

            else:
                # Single mode: Standard configuration
                self.ax1.set_xlabel(x_label, fontweight="bold")

                # Determine Y-axis label based on primary sensor
                if self.y1_sensor:
                    if self.y1_sensor == "NTCs":
                        y_label = "Temperature (°C)"  # All NTC sensors are temperature
                    else:
                        y_label = self.plot_service._get_y_axis_label(self.y1_sensor)
                else:
                    y_label = "Value"

                self.ax1.set_ylabel(y_label, fontweight="bold", color="black")

                # Configure grid
                self.ax1.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

                # Remove margins and use tight layout for no wasted space
                self.ax1.margins(x=0, y=0.05)  # Small y-margin for labels, no x-margin

            # Use tight layout for no wasted space
            self.figure.tight_layout(pad=0.5)  # Minimal padding

            self.logger.debug("Axes configured successfully for mode: %s", self.plot_mode)
        except Exception as e:
            self.logger.error("Failed to configure axes: %s", e)
            raise

    def _add_legend(self):
        """Add legend to the plot."""
        try:
            # Get legend from main axis only
            lines1, labels1 = self.ax1.get_legend_handles_labels()

            if lines1:
                self.ax1.legend(
                    lines1,
                    labels1,
                    loc="upper right",
                    frameon=True,
                    fancybox=True,
                    shadow=True,
                    framealpha=0.9,
                )

            self.logger.debug("Legend added successfully")
        except Exception as e:
            self.logger.error("Failed to add legend: %s", e)
            raise

    def _clear_plot(self):
        """Clear the plot and show placeholder."""
        try:
            self.ax1.clear()
            self.ax2.clear()

            # Show placeholder message
            self.ax1.text(
                0.5,
                0.5,
                "No data available for plotting",
                transform=self.ax1.transAxes,
                ha="center",
                va="center",
                fontsize=14,
                color="#666666",
            )

            # Configure empty plot
            self.ax1.set_xlabel("Time", fontweight="bold")
            # Use default label for empty plot
            self.ax1.set_ylabel("Value", fontweight="bold", color="black")

            self.canvas.draw()

            self.logger.debug("Plot cleared successfully")
        except Exception as e:
            self.logger.error("Failed to clear plot: %s", e)
            raise

    def export_plot(self, filename: str, format: str = "png", dpi: int = 300):
        """
        Export the current plot to a file.

        Args:
            filename: Output filename
            format: Export format (png, pdf, svg, etc.)
            dpi: Resolution for raster formats
        """
        try:
            self.figure.savefig(
                filename, format=format, dpi=dpi, bbox_inches="tight", facecolor="white"
            )
            self.logger.info("Plot exported to %s", filename)
        except Exception as e:
            self.logger.error("Failed to export plot: %s", e)
            raise

    def get_plot_info(self) -> Dict[str, Any]:
        """
        Get information about the current plot.

        Returns:
            Dictionary containing plot information
        """
        try:
            return {
                "sensors_plotted": len(self.selected_sensors),
                "data_points": (
                    len(self.tob_data_model.data)
                    if self.tob_data_model and self.tob_data_model.data is not None
                    else 0
                ),
                "axis_settings": self.axis_settings.copy(),
                "has_data": self.tob_data_model is not None
                and self.tob_data_model.data is not None,
            }
        except Exception as e:
            self.logger.error("Failed to get plot info: %s", e)
            return {}

    def update_axis_settings(self, axis_settings: Dict[str, Any]):
        """
        Update axis settings for plotting.

        Args:
            axis_settings: Dictionary containing axis configuration
        """
        try:
            # Extract sensor selections from axis settings
            sensor_updates = []
            if "y1_sensor" in axis_settings:
                sensor_updates.append(axis_settings["y1_sensor"])
            if "y2_sensor" in axis_settings and axis_settings["y2_sensor"] != "None":
                sensor_updates.append(axis_settings["y2_sensor"])

            # Update sensor selection if sensors changed
            if sensor_updates:
                self.update_sensor_selection(sensor_updates)
                self.logger.debug(
                    "Sensor selection updated from axis settings: %s", sensor_updates
                )

            # Update axis settings
            self.axis_settings.update(axis_settings)
            self.logger.debug("Axis settings updated: %s", axis_settings)

            # Always refresh plot when axis settings change
            # This ensures time scaling and labels are updated correctly
            self._refresh_plot()

            # Also update axis labels immediately for better responsiveness
            self._update_axis_labels()
        except Exception as e:
            self.logger.error("Failed to update axis settings: %s", e)
            raise

    def update_x_limits(self, min_value: float, max_value: float):
        """
        Update X-axis limits manually.

        Args:
            min_value: Minimum X-axis value in seconds
            max_value: Maximum X-axis value in seconds
        """
        try:
            if not self.ax1:
                self.logger.warning("No axes available for X-limits update")
                return

            self.logger.debug(
                "Updating X-axis limits: min=%.2f, max=%.2f", min_value, max_value
            )

            # Set X-axis limits
            self.ax1.set_xlim(min_value, max_value)

            # Apply tight layout and margins for no wasted space
            self.ax1.margins(x=0, y=0.05)  # No x-margin, small y-margin
            self.figure.tight_layout(pad=0.5)  # Minimal padding

            # Redraw the plot
            self.canvas.draw_idle()
            self.canvas.flush_events()

            self.logger.info("X-axis limits updated successfully")
        except Exception as e:
            self.logger.error("Failed to update X-axis limits: %s", e)
            raise

    def _update_axis_labels(self):
        """Update axis labels without full plot refresh."""
        try:
            if not self.ax1:
                return

            # Update X-axis label based on time unit
            time_unit = self.axis_settings.get("x_axis_type", "Seconds")
            x_label = f"Time ({time_unit})"
            self.ax1.set_xlabel(x_label, fontweight="bold")

            # Update Y-axis labels based on selected sensors
            if self.selected_sensors:
                primary_sensor = self.selected_sensors[0]
                y_label = self.plot_service._get_y_axis_label(primary_sensor)
            else:
                y_label = "Value"

            self.ax1.set_ylabel(y_label, fontweight="bold", color="black")

            # Force redraw of labels
            self.canvas.draw_idle()
            self.canvas.flush_events()

        except Exception as e:
            self.logger.error("Failed to update axis labels: %s", e)

    def update_y1_limits(self, min_value: float, max_value: float):
        """
        Update Y1-axis limits manually.

        Args:
            min_value: Minimum Y1-axis value
            max_value: Maximum Y1-axis value
        """
        try:
            if not self.ax1:
                self.logger.warning("No axes available for Y1-limits update")
                return

            self.logger.debug(
                "Updating Y1-axis limits: min=%.2f, max=%.2f", min_value, max_value
            )

            # Set Y1-axis limits
            self.ax1.set_ylim(min_value, max_value)

            # Apply margins
            self.ax1.margins(x=0.05, y=0)  # Small x-margin, no y-margin

            # Redraw the plot
            self.canvas.draw_idle()
            self.canvas.flush_events()

            self.logger.info("Y1-axis limits updated successfully")

        except Exception as e:
            self.logger.error("Failed to update Y1-axis limits: %s", e)
            raise

    def update_y2_limits(self, min_value: float, max_value: float):
        """
        Update Y2-axis limits manually.

        Args:
            min_value: Minimum Y2-axis value
            max_value: Maximum Y2-axis value
        """
        try:
            if not self.ax2:
                self.logger.warning("No axes available for Y2-limits update")
                return

            self.logger.debug(
                "Updating Y2-axis limits: min=%.2f, max=%.2f", min_value, max_value
            )

            # Set Y2-axis limits
            self.ax2.set_ylim(min_value, max_value)

            # Apply margins
            self.ax2.margins(x=0.05, y=0)  # Small x-margin, no y-margin

            # Redraw the plot
            self.canvas.draw_idle()
            self.canvas.flush_events()

            self.logger.info("Y2-axis limits updated successfully")

        except Exception as e:
            self.logger.error("Failed to update Y2-axis limits: %s", e)
            raise

    # ===== DUAL PLOT MODE MANAGEMENT =====

    def set_single_mode(self):
        """
        Activate single plot mode with main plot taking full space.
        """
        try:
            self.logger.info("Switching to single plot mode")
            self.plot_mode = "single"
            self.y2_sensor = None

            # Remove secondary axis if it exists
            if self.ax2 is not None:
                self.ax2.set_visible(False)
                self.ax2 = None

                # Clear the figure and recreate single subplot
                self.figure.clear()
                self.ax1 = self.figure.add_subplot(111)
                self.ax1.margins(x=0, y=0.05)

                # Re-setup layout for single mode
                self._setup_plot_layout()

            # Set full-size layout for main plot
            self.ax1.set_position([0.1, 0.1, 0.8, 0.8])  # Full height

            # Plot single sensor and update layout
            if self.tob_data_model and self.tob_data_model.data is not None:
                time_data = self.tob_data_model.get_time_column()
                if time_data is not None:
                    time_unit = self.axis_settings.get("x_axis_type", "Seconds")
                    time_values, _ = self.plot_service.format_time_axis(time_data, time_unit)
                    self._plot_single_sensor(time_values)
                    self._configure_axes(time_values, time_unit)
                    self._update_axis_labels()

            # Redraw
            self.canvas.draw_idle()
            self.canvas.flush_events()

            self.logger.info("Single plot mode activated successfully")

        except Exception as e:
            self.logger.error("Failed to set single mode: %s", e)
            raise

    def set_dual_mode(self, secondary_sensor: str):
        """
        Activate dual plot mode with two separate plots.

        Args:
            secondary_sensor: Sensor name for the secondary plot
        """
        try:
            self.logger.info("Switching to dual plot mode with sensor: %s", secondary_sensor)
            self.plot_mode = "dual"
            self.y2_sensor = secondary_sensor

            # Clear existing layout
            self.figure.clear()

            # Create two subplots vertically stacked
            self.ax1 = self.figure.add_subplot(211)  # Top plot
            self.ax2 = self.figure.add_subplot(212)  # Bottom plot

            # Configure both axes
            for ax in [self.ax1, self.ax2]:
                ax.margins(x=0, y=0.05)
                ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

            # Set positions for dual layout (50/50 split with small gap)
            self.ax1.set_position([0.1, 0.55, 0.8, 0.35])  # Top half
            self.ax2.set_position([0.1, 0.1, 0.8, 0.35])   # Bottom half

            # Setup axis labels and titles
            self._setup_dual_plot_layout()

            # Plot data on both axes using the same logic as _refresh_plot
            if self.tob_data_model and self.tob_data_model.data is not None:
                time_data = self.tob_data_model.get_time_column()
                if time_data is not None:
                    time_unit = self.axis_settings.get("x_axis_type", "Seconds")
                    time_values, _ = self.plot_service.format_time_axis(time_data, time_unit)
                    self._plot_dual_sensors(time_values)
                    self._configure_axes(time_values, time_unit)

            # Redraw
            self.canvas.draw_idle()
            self.canvas.flush_events()

            self.logger.info("Dual plot mode activated successfully")

        except Exception as e:
            self.logger.error("Failed to set dual mode: %s", e)
            raise

    def _setup_dual_plot_layout(self):
        """Setup axis labels and styling for dual plot mode."""
        try:
            # Setup primary axis (top)
            self.ax1.set_xlabel("")  # No x-label for top plot
            self.ax1.set_ylabel(self.plot_service._get_y_axis_label(self.y1_sensor),
                               fontweight="bold", color="black")
            self.ax1.set_title(f"Primär: {self.y1_sensor}", fontsize=11, fontweight="bold")
            self.ax1.tick_params(axis="y", labelcolor="black")

            # Setup secondary axis (bottom)
            self.ax2.set_xlabel("Time", fontweight="bold")
            self.ax2.set_ylabel(self.plot_service._get_y_axis_label(self.y2_sensor),
                               fontweight="bold", color="black")
            self.ax2.set_title(f"Sekundär: {self.y2_sensor}", fontsize=11, fontweight="bold")
            self.ax2.tick_params(axis="y", labelcolor="black")

        except Exception as e:
            self.logger.error("Failed to setup dual plot layout: %s", e)
            raise

    def _plot_dual_data(self):
        """Plot data on both axes in dual mode."""
        try:
            if not self.tob_data_model or self.tob_data_model.data is None:
                self.logger.warning("No data available for dual plotting")
                return

            data = self.tob_data_model.data

            # Plot primary sensor (top plot)
            if self.y1_sensor in data.columns:
                time_data = self.tob_data_model.get_time_column()
                if time_data is not None:
                    self.ax1.clear()
                    self.ax1.plot(time_data, data[self.y1_sensor],
                                color='blue', linewidth=2, label=self.y1_sensor)
                    self.ax1.legend()
                    self.ax1.grid(True, alpha=0.3)

            # Plot secondary sensor (bottom plot)
            if self.y2_sensor in data.columns:
                time_data = self.tob_data_model.get_time_column()
                if time_data is not None:
                    self.ax2.clear()
                    self.ax2.plot(time_data, data[self.y2_sensor],
                                color='red', linewidth=2, label=self.y2_sensor)
                    self.ax2.legend()
                    self.ax2.grid(True, alpha=0.3)

            # Sync x-axis ranges
            if hasattr(self.ax1, 'get_xlim') and hasattr(self.ax2, 'get_xlim'):
                xlims = self.ax1.get_xlim()
                self.ax2.set_xlim(xlims)

        except Exception as e:
            self.logger.error("Failed to plot dual data: %s", e)
            raise

    def _plot_single_sensor(self, time_values: np.ndarray):
        """Plot the primary sensor(s) for single mode."""
        try:
            if not self.tob_data_model or self.tob_data_model.data is None:
                return

            data = self.tob_data_model.data

            # Handle NTCs group - plot filtered NTC sensors
            if self.y1_sensor == "NTCs":
                ntc_sensors = [
                    col for col in data.columns
                    if col.startswith("NTC") and col[3:].isdigit()
                ]

                # Filter active NTC sensors if specified
                if self.active_ntc_sensors is not None:
                    ntc_sensors = [s for s in ntc_sensors if s in self.active_ntc_sensors]

                for ntc_sensor in ntc_sensors:
                    if ntc_sensor not in data.columns:
                        continue

                    sensor_data = data[ntc_sensor].dropna()
                    if sensor_data.empty:
                        continue

                    # Get styling for individual NTC sensor
                    color = self.plot_service.get_sensor_color(ntc_sensor)
                    line_style = self.plot_service.get_line_style(ntc_sensor)
                    line_width = self.plot_service.get_line_width(ntc_sensor)

                    # Plot on main axis
                    self.ax1.plot(
                        time_values[: len(sensor_data)],
                        sensor_data.values,
                        color=color,
                        linestyle=line_style,
                        linewidth=line_width,
                        label=ntc_sensor,
                        alpha=0.8,
                    )
                self.logger.debug("Plotted %d NTC sensors for primary axis", len(ntc_sensors))

            # Handle normal single sensor
            elif self.y1_sensor and self.y1_sensor in data.columns:
                sensor_data = data[self.y1_sensor].dropna()
                if not sensor_data.empty:
                    # Get styling
                    color = self.plot_service.get_sensor_color(self.y1_sensor)
                    line_style = self.plot_service.get_line_style(self.y1_sensor)
                    line_width = self.plot_service.get_line_width(self.y1_sensor)

                    # Plot on main axis
                    self.ax1.plot(
                        time_values[: len(sensor_data)],
                        sensor_data.values,
                        color=color,
                        linestyle=line_style,
                        linewidth=line_width,
                        label=self.y1_sensor,
                        alpha=0.8,
                    )
                    self.logger.debug("Plotted primary sensor: %s", self.y1_sensor)

        except Exception as e:
            self.logger.error("Failed to plot single sensor: %s", e)
            raise

    def _plot_dual_sensors(self, time_values: np.ndarray):
        """Plot primary and secondary sensors for dual mode."""
        try:
            self.logger.debug("_plot_dual_sensors called with y1_sensor=%s, y2_sensor=%s",
                            self.y1_sensor, self.y2_sensor)

            if not self.tob_data_model or self.tob_data_model.data is None:
                self.logger.warning("No data available for dual plotting")
                return

            data = self.tob_data_model.data
            self.logger.debug("Data available with %d columns", len(data.columns))

            # Plot primary sensor(s) (y1_sensor) on top axis
            if self.y1_sensor == "NTCs":
                # Handle NTCs group - plot filtered NTC sensors on top axis
                ntc_sensors = [
                    col for col in data.columns
                    if col.startswith("NTC") and col[3:].isdigit()
                ]

                # Filter active NTC sensors if specified
                if self.active_ntc_sensors is not None:
                    ntc_sensors = [s for s in ntc_sensors if s in self.active_ntc_sensors]

                for ntc_sensor in ntc_sensors:
                    if ntc_sensor not in data.columns:
                        continue

                    sensor_data = data[ntc_sensor].dropna()
                    if sensor_data.empty:
                        continue

                    # Get styling for individual NTC sensor
                    color = self.plot_service.get_sensor_color(ntc_sensor)
                    line_style = self.plot_service.get_line_style(ntc_sensor)
                    line_width = self.plot_service.get_line_width(ntc_sensor)

                    # Plot on top axis
                    self.ax1.plot(
                        time_values[: len(sensor_data)],
                        sensor_data.values,
                        color=color,
                        linestyle=line_style,
                        linewidth=line_width,
                        label=ntc_sensor,
                        alpha=0.8,
                    )
                    self.logger.debug("Plotted NTC sensor %s on top axis", ntc_sensor)
                self.logger.debug("Plotted all NTC sensors for primary axis")

            elif self.y1_sensor and self.y1_sensor in data.columns:
                # Handle normal single sensor on top axis
                sensor_data = data[self.y1_sensor].dropna()
                if not sensor_data.empty:
                    # Get styling
                    color = self.plot_service.get_sensor_color(self.y1_sensor)
                    line_style = self.plot_service.get_line_style(self.y1_sensor)
                    line_width = self.plot_service.get_line_width(self.y1_sensor)

                    # Plot on top axis
                    self.ax1.plot(
                        time_values[: len(sensor_data)],
                        sensor_data.values,
                        color=color,
                        linestyle=line_style,
                        linewidth=line_width,
                        label=self.y1_sensor,
                        alpha=0.8,
                    )
                    self.logger.debug("Plotted primary sensor: %s", self.y1_sensor)

            # Plot secondary sensor(s) (y2_sensor) on bottom axis
            if self.y2_sensor == "NTCs":
                # Handle NTCs group - plot all NTC sensors on bottom axis
                ntc_sensors = [
                    col for col in data.columns
                    if col.startswith("NTC") and col[3:].isdigit()
                ]
                for ntc_sensor in ntc_sensors:
                    if ntc_sensor not in data.columns:
                        continue

                    sensor_data = data[ntc_sensor].dropna()
                    if sensor_data.empty:
                        continue

                    # Get styling for individual NTC sensor
                    color = self.plot_service.get_sensor_color(ntc_sensor)
                    line_style = self.plot_service.get_line_style(ntc_sensor)
                    line_width = self.plot_service.get_line_width(ntc_sensor)

                    # Plot on bottom axis
                    self.ax2.plot(
                        time_values[: len(sensor_data)],
                        sensor_data.values,
                        color=color,
                        linestyle=line_style,
                        linewidth=line_width,
                        label=ntc_sensor,
                        alpha=0.8,
                    )
                    self.logger.debug("Plotted NTC sensor %s on bottom axis", ntc_sensor)
                self.logger.debug("Plotted all NTC sensors for secondary axis")

            elif self.y2_sensor and self.y2_sensor in data.columns:
                # Handle normal single sensor on bottom axis
                sensor_data = data[self.y2_sensor].dropna()
                if not sensor_data.empty:
                    # Get styling
                    color = self.plot_service.get_sensor_color(self.y2_sensor)
                    line_style = self.plot_service.get_line_style(self.y2_sensor)
                    line_width = self.plot_service.get_line_width(self.y2_sensor)

                    # Plot on bottom axis
                    self.ax2.plot(
                        time_values[: len(sensor_data)],
                        sensor_data.values,
                        color=color,
                        linestyle=line_style,
                        linewidth=line_width,
                        label=self.y2_sensor,
                        alpha=0.8,
                    )
                    self.logger.debug("Plotted secondary sensor: %s", self.y2_sensor)

        except Exception as e:
            self.logger.error("Failed to plot dual sensors: %s", e)
            raise

    def set_active_ntc_sensors(self, active_sensors: list = None):
        """
        Set which NTC sensors should be active when y1_sensor is "NTCs".

        Args:
            active_sensors: List of NTC sensor names to show, or None for all
        """
        try:
            self.active_ntc_sensors = active_sensors
            self.logger.debug("Active NTC sensors set to: %s", active_sensors)

            # Refresh plot if we have data
            if self.tob_data_model and self.tob_data_model.data is not None:
                self._refresh_plot()

        except Exception as e:
            self.logger.error("Failed to set active NTC sensors: %s", e)
            raise
