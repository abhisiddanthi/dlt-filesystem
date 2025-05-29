import sys
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog, QLabel, QSlider
from PyQt6.QtCore import QTimer, Qt

class JSONPlotter(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()  # Initialize timer early
        self.initUI()
        self.data = []
        self.timestamps = []
        self.fields = []
        self.animation_running = False
        self.current_index = 0

    def initUI(self):
        self.setWindowTitle("JSON Data Viewer & Plotter")
        self.setGeometry(100, 100, 600, 500)

        self.layout = QVBoxLayout()

        self.loadButton = QPushButton("Load JSON File")
        self.fileLabel = QLabel("No file loaded")

        self.xLabel = QLabel("Select X Axis:")
        self.xAxisCombo = QComboBox()
        self.yLabel = QLabel("Select Y Axis:")
        self.yAxisCombo = QComboBox()

        self.plotButton = QPushButton("Plot Data")
        self.animateButton = QPushButton("Animate Graph")
        self.cancelButton = QPushButton("Cancel Animation")

        self.speedLabel = QLabel("Speed Control:")
        self.speedSlider = QSlider(Qt.Orientation.Horizontal)
        self.speedSlider.setMinimum(100)
        self.speedSlider.setMaximum(2000)
        self.speedSlider.setValue(500)

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
        self.layout.addWidget(self.speedLabel)
        self.layout.addWidget(self.speedSlider)
        self.layout.addWidget(self.cancelButton)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)

        self.loadButton.clicked.connect(self.loadJson)
        self.plotButton.clicked.connect(self.plotData)
        self.animateButton.clicked.connect(self.animateGraph)
        self.cancelButton.clicked.connect(self.cancelAnimation)
        self.timer.timeout.connect(self.updateAnimation)

    def loadJson(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")

        if file_path:
            with open(file_path, "r") as file:
                raw_data = json.load(file)

            self.timestamps = [entry[0] for entry in raw_data[1:]]
            self.fields = raw_data[0][1]

            self.data = [entry[1] for entry in raw_data[1:]]

            self.xAxisCombo.clear()
            self.yAxisCombo.clear()
            self.xAxisCombo.addItems(["Timestamp"] + self.fields)
            self.yAxisCombo.addItems(["Timestamp"] + self.fields)

            self.fileLabel.setText(f"Loaded: {file_path.split('/')[-1]}")

    def plotData(self):
        if not self.data:
            self.fileLabel.setText("No data to plot")
            return

        x_field = self.xAxisCombo.currentText()
        y_field = self.yAxisCombo.currentText()

        if x_field and y_field:
            x_values = self.timestamps if x_field == "Timestamp" else [entry[self.fields.index(x_field)] for entry in self.data]
            y_values = self.timestamps if y_field == "Timestamp" else [entry[self.fields.index(y_field)] for entry in self.data]

            self.ax.clear()
            self.ax.plot(x_values, y_values, marker="o", linestyle="-")
            self.ax.set_xlabel(x_field)
            self.ax.set_ylabel(y_field)
            self.ax.set_title(f"{x_field} vs {y_field}")
            self.ax.grid()

            self.canvas.draw()

    def animateGraph(self):
        if not self.data:
            self.fileLabel.setText("No data to animate")
            return
        
        self.animation_running = True
        self.current_index = 0
        self.timer.start(self.speedSlider.value())

    def updateAnimation(self):
        if not self.animation_running or self.current_index >= len(self.data):
            self.timer.stop()
            return
        
        y_field = self.yAxisCombo.currentText()
        y_values = self.timestamps[:self.current_index + 1] if y_field == "Timestamp" else [entry[self.fields.index(y_field)] for entry in self.data[:self.current_index + 1]]

        self.ax.clear()
        self.ax.plot(self.timestamps[:self.current_index + 1], y_values, marker="o", linestyle="-")
        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel(y_field)
        self.ax.set_title(f"Animated Graph: Timestamp vs {y_field}")
        self.ax.grid()

        self.canvas.draw()
        self.current_index += 1

    def cancelAnimation(self):
        self.animation_running = False
        self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JSONPlotter()
    window.show()
    sys.exit(app.exec())