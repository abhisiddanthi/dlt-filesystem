"""Animation controller for plotting time-series data."""
from PyQt6.QtCore import QTimer
import pyqtgraph as pg


class PlotAnimator:
    """Handles animation of plot data with play/pause/reset controls."""
    
    def __init__(self, plot_widget: pg.PlotWidget, x_data, y_data):
        """
        Initialize animator with plot widget and data.
        
        Args:
            plot_widget: Target plot widget
            x_data: X-axis data points
            y_data: Y-axis data points
        """
        self.plot = plot_widget
        self.x_data = x_data
        self.y_data = y_data
        self.speed = 50  # ms between updates
        self.timer = QTimer(self.plot)
        self.timer.timeout.connect(self._update)
        
        # Initialize plot line
        self.line = self.plot.plot([], [], pen='b', name='animation', width=4)
        self.plot.addLegend()
        self.reset()

    def _update(self):
        """Timer callback to update plot with next data point."""
        if self.pointer >= len(self.x_data):
            self.timer.stop()
            return
        self.line.setData(self.x_data[:self.pointer], self.y_data[:self.pointer])
        self.pointer += 1

    def play(self):
        """Start or resume animation."""
        if self.pointer >= len(self.x_data):
            self.reset()
        if not self.timer.isActive():
            self.timer.start(self.speed)

    def pause(self):
        """Pause animation."""
        self.timer.stop()

    def reset(self):
        """Reset animation to start position."""
        self.timer.stop()
        self.pointer = 0
        self.line.setData([], [])

    def set_speed(self, ms: int):
        """Set animation speed in milliseconds.
        
        Args:
            ms: Time between updates (milliseconds)
        """
        self.speed = ms
        if self.timer.isActive():
            self.timer.start(self.speed)