from PyQt6.QtCore import QTimer
import pyqtgraph as pg

class PlotAnimator:
    def __init__(self, plot_widget: pg.PlotWidget, x_data, y_data):
        self.plot  = plot_widget
        self.x     = x_data
        self.y     = y_data
        self.speed = 50                
        self.timer = QTimer(self.plot) 
        self.timer.timeout.connect(self._update)

        self.line = self.plot.plot([], [], pen='b', name='animation', width=4)
        self.plot.addLegend()

        self.reset()

    def _update(self):
        if self.ptr >= len(self.x):
            self.timer.stop()
            return
        self.line.setData(self.x[:self.ptr], self.y[:self.ptr])
        self.ptr += 1

    def play(self):
        if self.ptr >= len(self.x):
            self.reset()
        if not self.timer.isActive():
            self.timer.start(self.speed)

    def pause(self):
        self.timer.stop()

    def reset(self):
        self.timer.stop()
        self.ptr = 0
        self.line.setData([], [])

    def setSpeed(self, ms: int):
        self.speed = ms
        if self.timer.isActive():
            self.timer.start(self.speed)
