from PyQt6.QtWidgets import (
    QLabel, QHBoxLayout, QPushButton, 
    QTreeWidget, QVBoxLayout, QWidget, QSplitter 
)
from PyQt6.QtCore import Qt
from utils import add_header_plus_button

def ui(main_window):
    main_window.setWindowTitle("Proto Dashboard")
    main_window.showFullScreen()

    central_widget = QWidget()
    main_window.setCentralWidget(central_widget)
    layout = QHBoxLayout(central_widget)
    dashboard_widget = QWidget()
    main_window.dashboard = QVBoxLayout(dashboard_widget)
    graph_widget = QWidget()
    main_window.grapharea = QVBoxLayout(graph_widget)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    layout.addWidget(splitter)
    main_window.treeWidget = QTreeWidget()
    main_window.treeWidget.setHeaderLabel("DLT Files")
    add_header_plus_button(
        main_window.treeWidget,
        slot=main_window.addDLT,
        tooltip="Add a new DLT file"
    )

    main_window.addProtoBtn = QPushButton("Add Proto")
    main_window.addProtoBtn.clicked.connect(main_window.addProto)
    main_window.protoLabel = QLabel("No Proto Added")

    main_window.dashboard.addWidget(main_window.addProtoBtn)
    main_window.dashboard.addWidget(main_window.protoLabel)
    main_window.dashboard.addWidget(main_window.treeWidget)

    splitter.addWidget(dashboard_widget)
    splitter.addWidget(graph_widget)
    splitter.setSizes([80, 500])

    main_window.treeWidget.itemSelectionChanged.connect(main_window.onSelectionChanged)