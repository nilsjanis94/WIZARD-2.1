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
    
    def __init__(self):
        """Initialize the plot service."""
        self.logger = logging.getLogger(__name__)
        self.logger.debug("PlotService initialized")
        
        # Color schemes for different sensor types
        self.ntc_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            '#aec7e8', '#ffbb78', '#98df8a', '#ff9896', '#c5b0d5',
            '#c49c94', '#f7b6d3', '#c7c7c7', '#dbdb8d', '#9edae5',
            '#ad494a', '#8c6d31'
        ]
        
        self.pt100_color = '#ff6b6b'
        self.time_color = '#2c3e50'
        
        # Line styles for different sensor types
        self.ntc_line_style = '-'
        self.pt100_line_style = '--'
        self.time_line_style = '-'
        
        # Line widths
        self.ntc_line_width = 1.5
        self.pt100_line_width = 2.0
        self.time_line_width = 1.0

    def create_plot_widget(self, parent: QWidget) -> 'PlotWidget':
        """
        Create a new plot widget for data visualization.
        
        Args:
            parent: Parent widget for the plot widget
            
        Returns:
            PlotWidget: Configured plot widget instance
        """
        try:
            plot_widget = PlotWidget(parent, self)
            self.logger.debug("Plot widget created successfully")
            return plot_widget
        except Exception as e:
            self.logger.error("Failed to create plot widget: %s", e)
            raise

    def get_sensor_color(self, sensor_name: str) -> str:
        """
        Get the appropriate color for a sensor.
        
        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'PT100')
            
        Returns:
            str: Color code for the sensor
        """
        if sensor_name.startswith('NTC'):
            try:
                # Extract NTC number and use modulo to cycle through colors
                ntc_num = int(sensor_name[3:])
                return self.ntc_colors[(ntc_num - 1) % len(self.ntc_colors)]
            except (ValueError, IndexError):
                return self.ntc_colors[0]
        elif sensor_name == 'PT100':
            return self.pt100_color
        else:
            return self.ntc_colors[0]

    def get_line_style(self, sensor_name: str) -> str:
        """
        Get the appropriate line style for a sensor.
        
        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'PT100')
            
        Returns:
            str: Line style for the sensor
        """
        if sensor_name.startswith('NTC'):
            return self.ntc_line_style
        elif sensor_name == 'PT100':
            return self.pt100_line_style
        else:
            return self.ntc_line_style

    def get_line_width(self, sensor_name: str) -> float:
        """
        Get the appropriate line width for a sensor.
        
        Args:
            sensor_name: Name of the sensor (e.g., 'NTC01', 'PT100')
            
        Returns:
            float: Line width for the sensor
        """
        if sensor_name.startswith('NTC'):
            return self.ntc_line_width
        elif sensor_name == 'PT100':
            return self.pt100_line_width
        else:
            return self.ntc_line_width

    def format_time_axis(self, time_data: pd.Series) -> Tuple[np.ndarray, List[str]]:
        """
        Format time data for plotting.
        
        Args:
            time_data: Time series data
            
        Returns:
            Tuple of formatted time values and labels
        """
        try:
            if time_data.empty:
                return np.array([]), []
            
            # Convert to numpy array for plotting
            time_values = time_data.values
            
            # Create time labels (every 10th point for readability)
            step = max(1, len(time_values) // 10)
            time_labels = [f"T{i}" for i in range(0, len(time_values), step)]
            
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
        
        # Data storage
        self.tob_data_model: Optional[TOBDataModel] = None
        self.selected_sensors: List[str] = []
        self.axis_settings: Dict[str, Any] = {
            'x_axis': 'Time',
            'y1_axis': 'NTC01',
            'y2_axis': 'PT100',
            'x_auto': True,
            'y1_auto': True,
            'y2_auto': True
        }
        
        # Matplotlib setup
        self._setup_matplotlib()
        self._create_plot_canvas()
        self._setup_plot_layout()
        
        self.logger.debug("PlotWidget initialized")

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
                'ytick.labelsize': 9,
                'legend.fontsize': 9,
                'legend.frameon': True,
                'legend.fancybox': True,
                'legend.shadow': True,
                'legend.framealpha': 0.9,
                'legend.edgecolor': '#cccccc'
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
            
            # Create subplots (dual y-axis setup)
            self.ax1 = self.figure.add_subplot(111)
            self.ax2 = self.ax1.twinx()
            
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
            self.ax1.set_ylabel('Temperature (°C)', fontweight='bold', color='#1f77b4')
            self.ax2.set_ylabel('Temperature (°C)', fontweight='bold', color='#ff6b6b')
            
            # Set axis colors
            self.ax1.tick_params(axis='y', labelcolor='#1f77b4')
            self.ax2.tick_params(axis='y', labelcolor='#ff6b6b')
            
            # Configure grid
            self.ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            
            # Set title
            self.figure.suptitle('Temperature Sensor Data Analysis', 
                               fontsize=14, fontweight='bold', y=0.95)
            
            # Add canvas to layout
            from PyQt6.QtWidgets import QVBoxLayout
            layout = QVBoxLayout()
            layout.addWidget(self.canvas)
            self.setLayout(layout)
            
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
            self.selected_sensors = selected_sensors.copy()
            self.logger.debug("Sensor selection updated: %s", selected_sensors)
            self._refresh_plot()
        except Exception as e:
            self.logger.error("Failed to update sensor selection: %s", e)
            raise

    def update_axis_settings(self, axis_settings: Dict[str, Any]):
        """
        Update axis settings for plotting.
        
        Args:
            axis_settings: Dictionary containing axis configuration
        """
        try:
            self.axis_settings.update(axis_settings)
            self.logger.debug("Axis settings updated: %s", axis_settings)
            self._refresh_plot()
        except Exception as e:
            self.logger.error("Failed to update axis settings: %s", e)
            raise

    def _refresh_plot(self):
        """Refresh the plot with current data and settings."""
        try:
            if not self.tob_data_model or not self.tob_data_model.data is not None:
                self._clear_plot()
                return
            
            # Clear previous plots
            self.ax1.clear()
            self.ax2.clear()
            
            # Get time data
            time_data = self.tob_data_model.get_time_column()
            if time_data is None or time_data.empty:
                self._clear_plot()
                return
            
            time_values, time_labels = self.plot_service.format_time_axis(time_data)
            
            # Plot selected sensors
            self._plot_sensors(time_values)
            
            # Configure axes
            self._configure_axes(time_values)
            
            # Add legend
            self._add_legend()
            
            # Refresh canvas
            self.canvas.draw()
            
            self.logger.debug("Plot refreshed successfully")
        except Exception as e:
            self.logger.error("Failed to refresh plot: %s", e)
            raise

    def _plot_sensors(self, time_values: np.ndarray):
        """Plot the selected sensors."""
        try:
            if not self.tob_data_model or not self.tob_data_model.data is not None:
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
                
                # Determine which axis to use
                if sensor == self.axis_settings.get('y1_axis'):
                    ax = self.ax1
                elif sensor == self.axis_settings.get('y2_axis'):
                    ax = self.ax2
                else:
                    # Default to y1 axis
                    ax = self.ax1
                
                # Plot the data
                ax.plot(time_values[:len(sensor_data)], sensor_data.values,
                       color=color, linestyle=line_style, linewidth=line_width,
                       label=sensor, alpha=0.8)
            
            self.logger.debug("Sensors plotted successfully")
        except Exception as e:
            self.logger.error("Failed to plot sensors: %s", e)
            raise

    def _configure_axes(self, time_values: np.ndarray):
        """Configure the plot axes."""
        try:
            # X-axis configuration
            if self.axis_settings.get('x_auto', True):
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
            
            if self.axis_settings.get('y2_auto', True):
                self.ax2.set_ylim(auto=True)
            else:
                # Manual y2-axis limits would be set here
                pass
            
            # Set labels
            self.ax1.set_xlabel('Time', fontweight='bold')
            self.ax1.set_ylabel('Temperature (°C)', fontweight='bold', color='#1f77b4')
            self.ax2.set_ylabel('Temperature (°C)', fontweight='bold', color='#ff6b6b')
            
            # Configure grid
            self.ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            
            self.logger.debug("Axes configured successfully")
        except Exception as e:
            self.logger.error("Failed to configure axes: %s", e)
            raise

    def _add_legend(self):
        """Add legend to the plot."""
        try:
            # Combine legends from both axes
            lines1, labels1 = self.ax1.get_legend_handles_labels()
            lines2, labels2 = self.ax2.get_legend_handles_labels()
            
            if lines1 or lines2:
                self.ax1.legend(lines1 + lines2, labels1 + labels2,
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
            self.ax1.set_ylabel('Temperature (°C)', fontweight='bold', color='#1f77b4')
            self.ax2.set_ylabel('Temperature (°C)', fontweight='bold', color='#ff6b6b')
            
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
