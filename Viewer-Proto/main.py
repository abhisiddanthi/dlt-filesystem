import sys, os
from ui import ui
from logic import addProto, addDLT, onDLTProcessed, onDLTError, onSelectionChanged, deleteDLT, convertToJSON
from graph import addGraph, deleteSelectedGraph
from utils import cleanup_temp_files 
from PyQt6.QtWidgets import QApplication, QMainWindow

class ProtoDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.protoModule = None
        self.proto_directory = os.getcwd()  
        self.graph_mapping = {}  
        self.graph_canvas_mapping = {}  
        self.struct_dictionary = {}

        self.addProto = lambda: addProto(self)
        self.addDLT = lambda: addDLT(self)
        self.onDLTProcessed = lambda dltpath, struct_dict: onDLTProcessed(self, dltpath, struct_dict)
        self.onDLTError = lambda message: onDLTError(self, message)
        self.onSelectionChanged = lambda: onSelectionChanged(self)
        self.deleteDLT = lambda selected_dlt: deleteDLT(self, selected_dlt)
        self.addGraph = lambda identifiers, container, selected_key: addGraph(self, identifiers, container, selected_key)
        self.deleteSelectedGraph = lambda identifiers, graph_name, container: deleteSelectedGraph(self, identifiers, graph_name, container)
        self.convertToJSON = lambda dltpath, struct_dict: convertToJSON(self, dltpath, struct_dict)

        ui(self)
    
     
    def closeEvent(self, event):
        cleanup_temp_files()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProtoDashboard()
    window.show()
    sys.exit(app.exec())