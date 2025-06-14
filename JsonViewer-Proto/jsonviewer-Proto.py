import sys
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog, QLabel, QSlider
from PyQt6.QtCore import QTimer, Qt

class PlotterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("JSON Data Plotter")
        self.setGeometry(100, 100, 600, 450)

        self.layout = QVBoxLayout()

        self.loadButton = QPushButton("Load JSON File")
        self.fileLabel = QLabel("No file loaded")

        self.xLabel = QLabel("Select X Axis:")
        self.xAxisCombo = QComboBox()
        self.yLabel = QLabel("Select Y Axis:")
        self.yAxisCombo = QComboBox()

        self.plotButton = QPushButton("Plot Data")
        self.animateButton = QPushButton("Animate Plot")
        self.cancelButton = QPushButton("Cancel Animation")

        self.speedLabel = QLabel("Animation Speed:")
        self.speedSlider = QSlider(Qt.Orientation.Horizontal)
        self.speedSlider.setMinimum(100)
        self.speedSlider.setMaximum(2000)
        self.speedSlider.setValue(500)
        self.speedSlider.setTickInterval(100)
        self.speedSlider.setSingleStep(100)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.loadButton)
        self.layout.addWidget(self.fileLabel)
        self.layout.addWidget(self.xLabel)
        self.layout.addWidget(self.xAxisCombo)
        self.layout.addWidget(self.yLabel)
        self.layout.addWidget(self.yAxisCombo)
        self.layout.addWidget(self.plotButton)
        self.layout.addWidget(self.animateButton)
        self.layout.addWidget(self.cancelButton)
        self.layout.addWidget(self.speedLabel)
        self.layout.addWidget(self.speedSlider)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        self.loadButton.clicked.connect(self.loadJson)
        self.plotButton.clicked.connect(self.plotData)
        self.animateButton.clicked.connect(self.animatePlot)
        self.cancelButton.clicked.connect(self.cancelAnimation)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updatePlot)
        self.index = 0

    def loadJson(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")

        if file_path:
            with open(file_path, "r") as file:
                self.data = json.load(file)

            self.keys = list(self.data[0][1].keys())

            self.xAxisCombo.clear()
            self.yAxisCombo.clear()
            self.xAxisCombo.addItems(["Timestamp"] + self.keys)
            self.yAxisCombo.addItems(["Timestamp"] + self.keys)

            self.fileLabel.setText(f"Loaded: {file_path.split('/')[-1]}")

    def plotData(self):
        x_field = self.xAxisCombo.currentText()
        y_field = self.yAxisCombo.currentText()

        if x_field and y_field:
            x_values = [entry[0] if x_field == "Timestamp" else entry[1][x_field] for entry in self.data]
            y_values = [entry[0] if y_field == "Timestamp" else entry[1][y_field] for entry in self.data]

            self.ax.clear()
            self.ax.plot(x_values, y_values, marker="o", linestyle="-")
            self.ax.set_xlabel(x_field)
            self.ax.set_ylabel(y_field)
            self.ax.set_title(f"{x_field} vs {y_field}")
            self.ax.grid()

            self.canvas.draw()

    def animatePlot(self):
        self.index = 0
        self.timer.start(self.speedSlider.value())

    def updatePlot(self):
        if self.index < len(self.data):
            x_field = self.xAxisCombo.currentText()
            y_field = self.yAxisCombo.currentText()

            x_values = [entry[0] if x_field == "Timestamp" else entry[1][x_field] for entry in self.data[:self.index+1]]
            y_values = [entry[0] if y_field == "Timestamp" else entry[1][y_field] for entry in self.data[:self.index+1]]

            self.ax.clear()
            self.ax.plot(x_values, y_values, marker="o", linestyle="-")
            self.ax.set_xlabel(x_field)
            self.ax.set_ylabel(y_field)
            self.ax.set_title(f"{x_field} vs {y_field}")
            self.ax.grid()

            self.canvas.draw()
            self.index += 1
        else:
            self.timer.stop()

    def cancelAnimation(self):
        self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotterApp()
    window.show()
    sys.exit(app.exec())
