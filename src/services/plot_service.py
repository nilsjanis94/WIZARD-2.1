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

    def create_plot_widget(self, parent: QWidget) -> 'PlotWidget':
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
        return style['color']

    def get_line_style(self, sensor_name: str) -> str:
        """
        Get the appropriate line style for a sensor.

        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'Temp' for PT100)

        Returns:
            str: Line style for the sensor
        """
        style = self.plot_style_service.get_sensor_style(sensor_name)
        return style['line_style']

    def get_line_width(self, sensor_name: str) -> float:
        """
        Get the appropriate line width for a sensor.

        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'Temp' for PT100)

        Returns:
            float: Line width for the sensor
        """
        style = self.plot_style_service.get_sensor_style(sensor_name)
        return style['line_width']

    def format_time_axis(self, time_data: pd.Series, time_unit: str = "Seconds") -> Tuple[np.ndarray, List[str]]:
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
            time_labels = [f"{time_values[i]:.1f}{unit_label}" for i in range(0, len(time_values), step)]

            return time_values, time_labels
        except Exception as e:
            self.logger.error("Failed to format time axis: %s", e)
            return np.array([]), []

    def calculate_plot_limits(self, data: pd.Series, margin: float = 0.1) -> Tuple[float, float]:
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
            'x_axis': 'Time',
            'y1_axis': 'NTC01',
            'y2_axis': 'Temp',  # PT100 data is in 'Temp' column
            'x_auto': True,
            'y1_auto': True,
            'y2_auto': True
        }
        
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
            plt.style.use('default')
            
            # Configure matplotlib parameters for better appearance
            plt.rcParams.update({
                'font.size': 10,
                'font.family': 'sans-serif',
                'axes.linewidth': 1.2,
                'axes.grid': True,
                'grid.alpha': 0.3,
                'figure.facecolor': 'white',
                'axes.facecolor': 'white',
                'axes.edgecolor': '#333333',
                'xtick.color': '#333333',
                'ytick.color': '#333333',
                'text.color': '#333333',
                'axes.labelcolor': '#333333',
                'axes.titlesize': 12,
                'axes.labelsize': 10,
                'xtick.labelsize': 9,
                'ytick.labelsize': 9
            })
            
            self.logger.debug("Matplotlib configured successfully")
        except Exception as e:
            self.logger.error("Failed to configure matplotlib: %s", e)
            raise

    def _create_plot_canvas(self):
        """Create the matplotlib canvas."""
        try:
            # Create figure with subplots
            self.figure = Figure(figsize=(12, 8), dpi=100)
            self.figure.patch.set_facecolor('white')

            # Set tight layout and minimal margins by default
            self.figure.tight_layout(pad=0.5)

            # Create single subplot (main y-axis only)
            self.ax1 = self.figure.add_subplot(111)
            # ax2 removed for cleaner single-axis visualization

            # Set minimal margins
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
            self.ax1.set_xlabel('Time', fontweight='bold')
            self.ax1.set_ylabel('Temperature (°C)', fontweight='bold', color='black')

            # Set axis colors
            self.ax1.tick_params(axis='y', labelcolor='black')
            
            # Configure grid
            self.ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

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
            self.logger.debug("PlotWidget: updating sensor selection from %s to %s", self.selected_sensors, selected_sensors)
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
            lines_before = len(self.ax1.get_lines())
            self.ax1.clear()
            lines_after_clear = len(self.ax1.get_lines())
            self.logger.debug("Cleared plot: %d lines before, %d lines after", lines_before, lines_after_clear)

            # Get time data
            time_data = self.tob_data_model.get_time_column()
            if time_data is None or time_data.empty:
                self._clear_plot()
                return

            # Get time unit from settings
            time_unit = self.axis_settings.get('x_axis_type', 'Seconds')

            # Format time axis
            time_values, time_labels = self.plot_service.format_time_axis(time_data, time_unit)
            
            # Plot selected sensors
            self._plot_sensors(time_values)
            
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

    def _plot_sensors(self, time_values: np.ndarray):
        """Plot the selected sensors."""
        try:
            if not self.tob_data_model or self.tob_data_model.data is None:
                return
            
            data = self.tob_data_model.data
            
            for sensor in self.selected_sensors:
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
                ax.plot(time_values[:len(sensor_data)], sensor_data.values,
                       color=color, linestyle=line_style, linewidth=line_width,
                       label=sensor, alpha=0.8)
            
            self.logger.debug("Sensors plotted successfully")
        except Exception as e:
            self.logger.error("Failed to plot sensors: %s", e)
            raise

    def _configure_axes(self, time_values: np.ndarray, time_unit: str = "Seconds"):
        """Configure the plot axes."""
        try:
            # X-axis configuration
            if self.axis_settings.get('x_auto', True):
                # Always start from 0, not from data minimum
                if len(time_values) > 0:
                    x_max = time_values.max()
                    self.ax1.set_xlim(0, x_max)
                else:
                    self.ax1.set_xlim(auto=True)
            else:
                # Manual x-axis limits would be set here
                pass

            # Y-axis configuration
            if self.axis_settings.get('y1_auto', True):
                self.ax1.set_ylim(auto=True)
            else:
                # Manual y1-axis limits would be set here
                pass

            # Set labels
            x_label = f"Time ({time_unit})"
            self.ax1.set_xlabel(x_label, fontweight='bold')
            self.ax1.set_ylabel('Temperature (°C)', fontweight='bold', color='black')

            # Configure grid
            self.ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)

            # Remove margins and use tight layout for no wasted space
            self.ax1.margins(x=0, y=0.05)  # Small y-margin for labels, no x-margin
            self.figure.tight_layout(pad=0.5)  # Minimal padding

            self.logger.debug("Axes configured successfully")
        except Exception as e:
            self.logger.error("Failed to configure axes: %s", e)
            raise

    def _add_legend(self):
        """Add legend to the plot."""
        try:
            # Get legend from main axis only
            lines1, labels1 = self.ax1.get_legend_handles_labels()

            if lines1:
                self.ax1.legend(lines1, labels1,
                              loc='upper right', frameon=True, fancybox=True,
                              shadow=True, framealpha=0.9)
            
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
            self.ax1.text(0.5, 0.5, 'No data available for plotting',
                         transform=self.ax1.transAxes, ha='center', va='center',
                         fontsize=14, color='#666666')
            
            # Configure empty plot
            self.ax1.set_xlabel('Time', fontweight='bold')
            self.ax1.set_ylabel('Temperature (°C)', fontweight='bold', color='black')
            
            self.canvas.draw()
            
            self.logger.debug("Plot cleared successfully")
        except Exception as e:
            self.logger.error("Failed to clear plot: %s", e)
            raise

    def export_plot(self, filename: str, format: str = 'png', dpi: int = 300):
        """
        Export the current plot to a file.
        
        Args:
            filename: Output filename
            format: Export format (png, pdf, svg, etc.)
            dpi: Resolution for raster formats
        """
        try:
            self.figure.savefig(filename, format=format, dpi=dpi, 
                              bbox_inches='tight', facecolor='white')
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
                'sensors_plotted': len(self.selected_sensors),
                'data_points': len(self.tob_data_model.data) if self.tob_data_model and self.tob_data_model.data is not None else 0,
                'axis_settings': self.axis_settings.copy(),
                'has_data': self.tob_data_model is not None and self.tob_data_model.data is not None
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

            self.logger.debug("Updating X-axis limits: min=%.2f, max=%.2f", min_value, max_value)

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
            time_unit = self.axis_settings.get('x_axis_type', 'Seconds')
            x_label = f"Time ({time_unit})"
            self.ax1.set_xlabel(x_label, fontweight='bold')

            # Update Y-axis labels (if needed in future)
            self.ax1.set_ylabel('Temperature (°C)', fontweight='bold', color='black')

            # Force redraw of labels
            self.canvas.draw_idle()
            self.canvas.flush_events()

        except Exception as e:
            self.logger.error("Failed to update axis labels: %s", e)
