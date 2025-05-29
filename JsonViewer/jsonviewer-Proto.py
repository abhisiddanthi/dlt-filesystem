import sys
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QComboBox, QFileDialog, QLabel

class PlotterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("JSON Data Plotter")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()

        self.loadButton = QPushButton("Load JSON File")
        self.fileLabel = QLabel("No file loaded")

        self.yLabel = QLabel("Select Y Axis:")
        self.yAxisCombo = QComboBox()

        self.plotButton = QPushButton("Plot Data")

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        self.layout.addWidget(self.loadButton)
        self.layout.addWidget(self.fileLabel)  
        self.layout.addWidget(self.yLabel)
        self.layout.addWidget(self.yAxisCombo)
        self.layout.addWidget(self.plotButton)
        self.layout.addWidget(self.canvas) 

        self.setLayout(self.layout)

        self.loadButton.clicked.connect(self.loadJson)
        self.plotButton.clicked.connect(self.plotData)

    def loadJson(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")

        if file_path:
            with open(file_path, "r") as file:
                self.data = json.load(file)

            self.keys = list(self.data[0][1].keys())  # Extract keys from nested dictionary
            self.yAxisCombo.clear()
            self.yAxisCombo.addItems(self.keys)

            self.fileLabel.setText(f"Loaded: {file_path.split('/')[-1]}")

    def plotData(self):
        y_field = self.yAxisCombo.currentText()

        if y_field:
            x_values = [entry[0] for entry in self.data]  # Extract timestamps
            y_values = [entry[1][y_field] for entry in self.data]  # Extract selected field values

            self.ax.clear()
            self.ax.plot(x_values, y_values, marker="o", linestyle="-")
            self.ax.set_xlabel("Timestamp")
            self.ax.set_ylabel(y_field)
            self.ax.set_title(f"Timestamp vs {y_field}")
            self.ax.grid()

            self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotterApp()
    window.show()
    sys.exit(app.exec())
