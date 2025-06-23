import sys, os
import subprocess
from PyQt6.QtWidgets import (
    QLabel, QApplication, QHBoxLayout, QMainWindow, QPushButton, 
    QTreeWidget, QTreeWidgetItem, QFileDialog, QMessageBox, QVBoxLayout, QWidget, QListWidget,
    QComboBox, QSplitter, QInputDialog, QMenu
)
from PyQt6.QtCore import Qt
from google.protobuf import symbol_database
from datetime import datetime
import pyqtgraph as pg
from pyqtgraph import PlotWidget, DateAxisItem

def createMessageByType(type_name: str):
    if '.' not in type_name:
        type_name = "logger." + type_name

    sym_db = symbol_database.Default()
    try:
        message_class = sym_db.GetSymbol(type_name)
    except KeyError:
        print(f"Message type \"{type_name}\" not found.")
        return None

    return message_class()

class ProtoDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.proto_directory = os.getcwd()  
        self.graph_mapping = {}  # Stores graph container widgets per DLT
        self.graph_lists = {}  # Stores list widgets tracking graphs per DLT
        self.graph_canvas_mapping = {}  # Maps list items to their canvas widgets
        self.struct_dictionary = {}

    def initUI(self):
        self.setWindowTitle("Proto Dashboard")
        self.showFullScreen()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        dashboard_widget = QWidget()
        self.dashboard = QVBoxLayout(dashboard_widget)
        graph_widget = QWidget()
        self.grapharea = QVBoxLayout(graph_widget)
    
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Dashboard Elements
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabel("DLT Files")
        self.addProtoBtn = QPushButton("Add Proto")
        self.addProtoBtn.clicked.connect(self.addProto)
        self.protoLabel =  QLabel("No Proto Added")
        self.dashboard.addWidget(self.addProtoBtn)
        self.dashboard.addWidget(self.protoLabel)
        self.dashboard.addWidget(self.treeWidget)
        self.addDLTBtn = QPushButton("Add DLT")
        self.addDLTBtn.clicked.connect(self.addDLT)
        self.dashboard.addWidget(self.addDLTBtn)
        self.deleteDLTBtn = QPushButton("Delete DLT")
        self.deleteDLTBtn.clicked.connect(self.deleteDLT)
        self.dashboard.addWidget(self.deleteDLTBtn)

        # Layout
        splitter.addWidget(dashboard_widget)
        splitter.addWidget(graph_widget)

        splitter.setSizes([80, 500])

        # Connect tree item selection change to show relevant graphs
        self.treeWidget.itemSelectionChanged.connect(self.onSelectionChanged)

    def addProto(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Proto File", "", "Proto Files (*.proto)")

        try: 
            if file_path:
                protopath = os.path.dirname(file_path)
                proto = subprocess.run(['protoc', f'--proto_path={protopath}', '--python_out=.', file_path])

                if proto.returncode == 0:
                    self.protoLabel.setText(f"Loaded: {file_path.split('/')[-1]}")
        
        except Exception as e:
            print(f"Proto filepath incorrect: {e}")

    def addDLT(self):
        if self.protoLabel.text() != "No Proto Added":  
            file_dialog = QFileDialog()
            dltpath, _ = file_dialog.getOpenFileName(self, "Open DLT File", "", "DLT Files (*.dlt)")

            protofilename = self.protoLabel.text()[8:].replace(".proto", "") 
            module_name = f"{protofilename}_pb2"

            try:
                if dltpath:
                    import importlib
                    import subprocess, csv, os
                    importlib.import_module(module_name)
                    import binascii
                    from google.protobuf.json_format import MessageToDict

                    if dltpath not in self.struct_dictionary:
                        self.struct_dictionary[dltpath] = {}

                    result = subprocess.run(['dlt-viewer', '-v', '-s', '-csv', '-c', dltpath, 'parsed.csv'])

                    if result.returncode == 0:
                        print("Converting to CSV Success")
                        with open('parsed.csv', newline='') as file:
                            reader = csv.reader(file, delimiter=' ', quotechar='|')

                            for row in reader:
                                try:
                                    if row and row[-1].startswith("ZXd6") and "7pQ3" in row[-1]:  
                                        remainder = row[-1][4:]
                                        sep_index = remainder.find("7pQ3")
                                        messageName = remainder[:sep_index]
                                        decoded_payload = remainder[sep_index + len("7pQ3"):]

                                        if messageName not in self.struct_dictionary[dltpath]:
                                            self.struct_dictionary[dltpath][messageName] = []

                                        binary_data = binascii.unhexlify(decoded_payload)
                                        try: 
                                            decoded_struct = createMessageByType(messageName)
                                            decoded_struct.ParseFromString(binary_data)
                                            jsonObject = MessageToDict(decoded_struct, including_default_value_fields=True)
                                            self.struct_dictionary[dltpath][messageName].append ({
                                                "timestamp": row[2],
                                                **jsonObject
                                            })
                                        
                                        except Exception as e:
                                            print(f"Skipping due to error: {e}")
                                    
                                except Exception as e:
                                    print(f"Incorrect data with pattern error: {e}")
                                    
                        # with open(jsonpath, "w") as file:
                        #     json.dump(data, file, indent = 4)

                        if os.path.exists("parsed.csv"):
                            os.remove("parsed.csv")
                            print("Successfully removed temporary csv")
                        else:
                            print("File not found.")

                    else:
                        print("Failed to Convert to csv")


                    available_keys = set()
                    available_keys.update(self.struct_dictionary[dltpath].keys())
                    available_keys = list(available_keys)  
                    dlt_item = QTreeWidgetItem(self.treeWidget, [os.path.basename(dltpath)])
                    dlt_item.setData(0, 1, dltpath)

                    graph_container = QVBoxLayout()

                    list_widget = QListWidget()
                    self.graph_lists[dltpath] = list_widget

                    graph_type_combo = QComboBox()
                    graph_type_combo.addItems(available_keys)

                    add_graph_btn = QPushButton(f"Add New Graph for {os.path.basename(dltpath)}")
                    add_graph_btn.clicked.connect(
                        lambda: self.addGraph(dltpath, graph_container, graph_type_combo.currentText())
                    )

                    graph_widget = QWidget()
                    graph_layout = QVBoxLayout(graph_widget)
                    graph_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
                    graph_layout.addWidget(graph_type_combo)
                    graph_layout.addWidget(add_graph_btn)
                    graph_layout.addLayout(graph_container)

                    graph_widget.setVisible(False)
                    self.grapharea.addWidget(graph_widget)
                    self.graph_mapping[dltpath] = graph_widget

                else:
                    print("failure")

            except Exception as e:
                print(f"Error: {e}")

    def addGraph(self, dltpath, container, selected_key):
        
        def try_parse_value(value):
            """
            Attempt to convert the value to a float.
            If that fails, try to parse it as a timestamp using the expected format ("%H:%M:%S.%f")
            and return a Unix timestamp (using a dummy date). Otherwise, return None.
            """
            try:
                return float(value)
            except (ValueError, TypeError):
                try:
                    dt = datetime.strptime(value, "%H:%M:%S.%f")
                    dummy_date = datetime(1970, 1, 1, dt.hour, dt.minute, dt.second, dt.microsecond)
                    return dummy_date.timestamp()
                except Exception:
                    return None

        try:
            if selected_key not in self.struct_dictionary[dltpath]:
                raise ValueError(f'No data found for message name "{selected_key}" in the file.')

            inner_data_list = self.struct_dictionary[dltpath][selected_key]
            if not inner_data_list:
                raise ValueError(f'No data entries found for message name "{selected_key}" in the file.')

            # Exclude the timestamp field for y_field proposals.
            available_fields = set(inner_data_list[0].keys()) - {"timestamp"}
            x_field = "timestamp"

            y_field, ok_y = QInputDialog.getItem(
                self,
                "Select Data",
                f"Choose data field from {selected_key}:",
                list(available_fields),
                editable=False
            )
            if not ok_y:
                return

            # Extract x and y values.
            x_values, y_values = [], []
            for item in inner_data_list:
                try:
                    x_val = try_parse_value(item.get(x_field))
                    y_val = try_parse_value(item.get(y_field))
                    if x_val is None or y_val is None:
                        continue
                    x_values.append(x_val)
                    y_values.append(y_val)
                except Exception:
                    continue

            if not x_values or not y_values:
                raise ValueError("Unable to extract valid numeric data for the selected fields.")

            # Ask the user whether to create a new graph or to add to an existing graph.
            graph_mode, ok_mode = QInputDialog.getItem(
                self,
                "Graph Mode",
                "Would you like to create a new graph or add data to an existing graph?",
                ["New Graph", "Existing Graph"],
                editable=False
            )
            if not ok_mode:
                return

            if graph_mode == "New Graph":
                # Offer a chance to customize the new graph's name.
                default_name = f"{selected_key}: {y_field}"
                graph_name, ok_name = QInputDialog.getText(
                    self,
                    "Graph Name",
                    "Enter a name for the new graph:",
                    text=default_name
                )
                if not ok_name or not graph_name:
                    return

                # Create a new PlotWidget. Use DateAxisItem if x_field is a string.
                if isinstance(inner_data_list[0].get(x_field), str):
                    axis = DateAxisItem(orientation='bottom')
                    plot_widget = PlotWidget(axisItems={'bottom': axis})
                else:
                    plot_widget = PlotWidget()

                # Add a legend to the new graph.
                plot_widget.addLegend()
                # Plot data with a curve labeled with the selected y_field.
                plot_widget.plot(x_values, y_values, symbol='o', pen=pg.mkPen(width=2), name=y_field)
                # Set labels and title.
                plot_widget.getPlotItem().setLabel('bottom', x_field)
                plot_widget.getPlotItem().setLabel('left', "Data")
                plot_widget.getPlotItem().setTitle(graph_name)
                plot_widget.showGrid(x=True, y=True)
                plot_widget.setBackground('white')

                # Save the new graph in the mapping.
                self.graph_canvas_mapping[(dltpath, graph_name)] = plot_widget
                container.addWidget(plot_widget)

                # Create a button to allow deletion of the entire graph.
                delete_graph_btn = QPushButton("Delete Graph")
                delete_graph_btn.clicked.connect(lambda: (
                    self.deleteSelectedGraph(dltpath, graph_name, container),
                    delete_graph_btn.deleteLater()
                ))
                container.addWidget(delete_graph_btn)

            else:  # Existing Graph
                # Collect existing graphs for the matching dltpath.
                existing_graphs = [key for key in self.graph_canvas_mapping.keys() if key[0] == dltpath]
                if not existing_graphs:
                    QMessageBox.information(self, "No Existing Graph", 
                                            "No existing graphs found for this file. Creating a new graph instead.")
                    # Same flow as creating a new graph.
                    default_name = f"{selected_key}: {y_field}"
                    graph_name, ok_name = QInputDialog.getText(
                        self,
                        "Graph Name",
                        "Enter a name for the new graph:",
                        text=default_name
                    )
                    if not ok_name or not graph_name:
                        return

                    if isinstance(inner_data_list[0].get(x_field), str):
                        axis = DateAxisItem(orientation='bottom')
                        plot_widget = PlotWidget(axisItems={'bottom': axis})
                    else:
                        plot_widget = PlotWidget()

                    plot_widget.addLegend()
                    plot_widget.plot(x_values, y_values, symbol='o', pen=pg.mkPen(width=2), name=y_field)
                    plot_widget.getPlotItem().setLabel('bottom', x_field)
                    plot_widget.getPlotItem().setLabel('left', "Data")
                    plot_widget.getPlotItem().setTitle(graph_name)
                    plot_widget.showGrid(x=True, y=True)
                    plot_widget.setBackground('white')
                    self.graph_canvas_mapping[(dltpath, graph_name)] = plot_widget
                    container.addWidget(plot_widget)
                    delete_graph_btn = QPushButton("Delete Graph")
                    delete_graph_btn.clicked.connect(lambda: (
                        self.deleteSelectedGraph(dltpath, graph_name, container),
                        delete_graph_btn.deleteLater()
                    ))
                    container.addWidget(delete_graph_btn)
                else:
                    # Let the user pick one of the existing graphs.
                    existing_graph_names = [key[1] for key in existing_graphs]
                    selected_graph_name, ok_sel = QInputDialog.getItem(
                        self,
                        "Select Existing Graph",
                        "Select an existing graph to add data:",
                        existing_graph_names,
                        editable=False
                    )
                    if not ok_sel:
                        return
                    # Retrieve the corresponding PlotWidget.
                    selected_graph_key = next((key for key in existing_graphs if key[1] == selected_graph_name), None)
                    if selected_graph_key is None:
                        raise ValueError("Selected graph not found.")

                    plot_widget = self.graph_canvas_mapping[selected_graph_key]
                    # Ensure a legend exists.
                    if not plot_widget.getPlotItem().legend:
                        plot_widget.addLegend()
                    # Plot a new curve on the existing graph.
                    plot_widget.plot(x_values, y_values, symbol='o', pen=pg.mkPen(width=2), name=y_field)
                    # Optionally, you could update the title or add extra info to indicate multiple data sets.
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add graph:\n{e}")



    def deleteSelectedGraph(self, dltpath, graph_name, container):
        canvas = self.graph_canvas_mapping.pop((dltpath, graph_name), None)
        if canvas:
            container.removeWidget(canvas)
            canvas.setParent(None)  
              

    def onSelectionChanged(self):
        selected_item = self.treeWidget.currentItem()
        if selected_item: 
            file_path = selected_item.data(0, 1)
            if file_path in self.graph_mapping:
                for widget in self.graph_mapping.values():
                    widget.setVisible(False)  

                self.graph_mapping[file_path].setVisible(True)  

    def deleteDLT(self):
        selected_dlt = self.treeWidget.currentItem()
        if selected_dlt and not selected_dlt.parent():  
            file_path = selected_dlt.data(0, 1)

            reply = QMessageBox.question(self, "Confirm Deletion",
                                         f"Are you sure you want to delete {selected_dlt.text(0)}?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                if file_path in self.graph_mapping:
                    widget = self.graph_mapping.pop(file_path, None)
                    if widget:
                        widget.setParent(None)

                if file_path in self.graph_lists:
                    self.graph_lists.pop(file_path, None)
                    del self.struct_dictionary[file_path]

                self.treeWidget.invisibleRootItem().removeChild(selected_dlt)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProtoDashboard()
    window.show()
    sys.exit(app.exec())
