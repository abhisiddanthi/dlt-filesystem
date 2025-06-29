"""User interface setup."""
from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QPushButton, 
    QTreeWidget, QVBoxLayout, QWidget, QSplitter
)
from PyQt6.QtCore import Qt
from utils import add_header_plus_button


def setup_ui(main_window):
    """Initialize main window UI."""
    main_window.setWindowTitle("Proto Dashboard")
    main_window.resize(1200, 800)
    
    # Central widget
    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    main_layout = QHBoxLayout(central_widget)
    
    # Create splitter
    splitter = QSplitter(Qt.Orientation.Horizontal)
    main_layout.addWidget(splitter)
    
    # Left panel (dashboard)
    dashboard_widget = QWidget()
    dashboard_layout = QVBoxLayout(dashboard_widget)
    dashboard_layout.setContentsMargins(5, 5, 5, 5)
    
    # Proto controls
    main_window.addProtoBtn = QPushButton("Add Proto")
    main_window.addProtoBtn.clicked.connect(main_window.add_proto)
    main_window.protoLabel = QLabel("No Proto Added")
    dashboard_layout.addWidget(main_window.addProtoBtn)
    dashboard_layout.addWidget(main_window.protoLabel)
    
    # DLT tree widget
    main_window.treeWidget = QTreeWidget()
    main_window.treeWidget.setHeaderLabel("DLT Files")
    add_header_plus_button(
        main_window.treeWidget,
        slot=main_window.add_dlt,
        tooltip="Add DLT file"
    )
    dashboard_layout.addWidget(main_window.treeWidget)
    
    # Right panel (graph area)
    graph_widget = QWidget()
    main_window.grapharea = QVBoxLayout(graph_widget)
    main_window.grapharea.setContentsMargins(5, 5, 5, 5)
    
    # Add to splitter
    splitter.addWidget(dashboard_widget)
    splitter.addWidget(graph_widget)
    splitter.setSizes([300, 700])
    
    # Connect signals
    main_window.treeWidget.itemSelectionChanged.connect(
        main_window.on_selection_changed
    )