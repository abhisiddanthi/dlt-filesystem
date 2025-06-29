"""Main application entry point."""
import sys
import os
from ui import setup_ui
from logic import (
    add_proto, add_dlt, on_dlt_processed, on_dlt_error,
    on_selection_changed, delete_dlt, convert_to_json
)
from graph import add_graph, delete_selected_graph
from utils import cleanup_temp_files
from PyQt6.QtWidgets import QApplication, QMainWindow


class ProtoDashboard(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        # Initialize data stores
        self.struct_dictionary = {}  # dlt_path: parsed_data
        self.graph_mapping = {}  # (dlt, app, ctx): graph_widget
        self.graph_canvas_mapping = {}  # (dlt, app, ctx, name): plot_widget
        
        # Connect logic methods
        self.add_proto = lambda: add_proto(self)
        self.add_dlt = lambda: add_dlt(self)
        self.on_dlt_processed = lambda path, data: on_dlt_processed(self, path, data)
        self.on_dlt_error = lambda msg: on_dlt_error(self, msg)
        self.on_selection_changed = lambda: on_selection_changed(self)
        self.delete_dlt = lambda item: delete_dlt(self, item)
        self.add_graph = lambda ids, cont, key: add_graph(self, ids, cont, key)
        self.delete_selected_graph = lambda ids, name, cont: delete_selected_graph(self, ids, name, cont)
        self.convert_to_json = lambda path, data: convert_to_json(self, path, data)
        
        # Setup UI
        setup_ui(self)
    
    def closeEvent(self, event):
        """Handle application close event."""
        cleanup_temp_files()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProtoDashboard()
    window.show()
    sys.exit(app.exec())