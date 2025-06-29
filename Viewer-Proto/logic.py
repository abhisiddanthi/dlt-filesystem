"""Application business logic and workflows."""
import os
import json
from PyQt6.QtCore import Qt
from dlt_worker import DLTWorker
from utils import APP_TEMP_DIR, run_command, SmoothListWidget
from PyQt6.QtWidgets import (
    QPushButton, QTreeWidgetItem, QFileDialog, QMessageBox, 
    QVBoxLayout, QWidget, QComboBox, QAbstractItemView,
    QHBoxLayout, QLabel, QStyle, QToolButton
)


def add_proto(main_window):
    """Add and compile protobuf file."""
    file_path, _ = QFileDialog.getOpenFileName(
        main_window, "Open Proto File", "", "Proto Files (*.proto)"
    )
    
    if not file_path:
        return
        
    try:
        proto_dir = os.path.dirname(file_path)
        result = run_command([
            'protoc', 
            f'--proto_path={proto_dir}', 
            f'--python_out={APP_TEMP_DIR}', 
            file_path
        ])
        
        if result.returncode == 0:
            main_window.protoLabel.setText(f"Loaded: {os.path.basename(file_path)}")
        else:
            QMessageBox.critical(
                main_window, "Compile Error", 
                "Failed to compile protobuf file"
            )
            
    except Exception as e:
        QMessageBox.critical(
            main_window, "Proto Error", 
            f"Error processing protobuf:\n{e}"
        )


def add_dlt(main_window):
    """Add and process DLT file."""
    if main_window.protoLabel.text() == "No Proto Added":
        QMessageBox.critical(
            main_window, "Missing Proto", 
            "Please add logger.proto first"
        )
        return
        
    file_path, _ = QFileDialog.getOpenFileName(
        main_window, "Open DLT File", "", "DLT Files (*.dlt)"
    )
    if not file_path:
        return
        
    # Check for duplicate
    if file_path in main_window.struct_dictionary:
        QMessageBox.critical(
            main_window, "Duplicate File", 
            "This DLT file is already loaded"
        )
        return
        
    # Prepare module name
    proto_text = main_window.protoLabel.text()
    proto_filename = proto_text[8:].replace(".proto", "")
    module_name = f"{proto_filename}_pb2"
    
    # Start worker thread
    main_window.struct_dictionary[file_path] = {}
    worker = DLTWorker(file_path, module_name)
    worker.finished.connect(main_window.on_dlt_processed)
    worker.error.connect(main_window.on_dlt_error)
    worker.start()


def on_dlt_processed(self, dlt_path, struct_dict):
    """Handle successfully processed DLT file."""
    self.struct_dictionary[dlt_path] = struct_dict
    
    # Create tree widget item
    dlt_item = QTreeWidgetItem(self.treeWidget)
    dlt_item.setData(0, 1, dlt_path)  # Store path in user data
    
    # Create header widget
    container = QWidget()
    hbox = QHBoxLayout(container)
    hbox.setContentsMargins(0, 0, 0, 0)
    hbox.setSpacing(4)
    
    # Add filename label
    lbl = QLabel(os.path.basename(dlt_path))
    hbox.addWidget(lbl)
    
    # Add JSON export button
    json_btn = QPushButton("JSON") 
    json_btn.clicked.connect(
        lambda _, d=dlt_path, s=struct_dict: self.convert_to_json(d, s)
    )
    hbox.addWidget(json_btn)
    
    # Add delete button
    delete_btn = QToolButton()
    icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
    delete_btn.setIcon(icon)
    delete_btn.setAutoRaise(True)
    delete_btn.setFixedSize(16, 16)
    delete_btn.clicked.connect(
        lambda _, item=dlt_item: self.delete_dlt(item)
    )
    hbox.addWidget(delete_btn)
    
    self.treeWidget.setItemWidget(dlt_item, 0, container)
    
    # Add AppID/CtxID hierarchy
    for app_id, ctx_dict in struct_dict.items():
        app_item = QTreeWidgetItem(dlt_item, [f"AppID: {app_id}"])
        for ctx_id in ctx_dict:
            ctx_item = QTreeWidgetItem(app_item, [f"CtxID: {ctx_id}"])
            ctx_item.setData(0, 1, (dlt_path, app_id, ctx_id))
            
            # Create graph container
            graph_container = SmoothListWidget()
            graph_container.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
            graph_container.setDefaultDropAction(Qt.DropAction.MoveAction)
            graph_container.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            graph_container.setSpacing(10)
            graph_container.setAutoScroll(True)
            graph_container.setAutoScrollMargin(80)
            graph_container.setStyleSheet("""
                SmoothListWidget::item:selected { background: transparent; }
            """)
            
            # Create key selection combo
            graph_combo = QComboBox()
            seen_keys = set()
            
            # Recursively collect keys
            def collect_keys(path, node):
                if isinstance(node, dict):
                    for key, val in node.items():
                        new_path = path + [key]
                        label = " > ".join(new_path)
                        if label not in seen_keys:
                            seen_keys.add(label)
                            graph_combo.addItem(label)
                        collect_keys(new_path, val)
                elif isinstance(node, list):
                    for elem in node:
                        if isinstance(elem, dict):
                            collect_keys(path, elem)
            
            collect_keys([], struct_dict[app_id][ctx_id])
            
            # Add graph button
            add_btn = QPushButton(f"Add Graph for {ctx_id}")
            add_btn.clicked.connect(
                lambda _, dp=dlt_path, aid=app_id, cid=ctx_id, 
                gc=graph_container, combo=graph_combo: 
                    self.add_graph((dp, aid, cid), gc, combo.currentText())
            )
            
            # Create graph area
            graph_widget = QWidget()
            graph_layout = QVBoxLayout(graph_widget)
            graph_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            graph_layout.addWidget(graph_combo)
            graph_layout.addWidget(add_btn)
            graph_layout.addWidget(graph_container)
            graph_widget.setVisible(False)
            
            # Store references
            self.grapharea.addWidget(graph_widget)
            self.graph_mapping[(dlt_path, app_id, ctx_id)] = graph_widget


def on_dlt_error(main_window, message):
    """Handle DLT processing error."""
    QMessageBox.critical(main_window, "Processing Error", message)


def convert_to_json(self, dlt_path, struct_dict):
    """Export structured data to JSON file."""
    file_path, _ = QFileDialog.getSaveFileName(
        self, "Save JSON", "", "JSON Files (*.json)"
    )
    if not file_path:
        return
        
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(struct_dict, f, indent=4, ensure_ascii=False)
        QMessageBox.information(
            self, "Export Success", 
            f"File saved:\n{file_path}"
        )
    except Exception as e:
        QMessageBox.critical(
            self, "Export Error", 
            f"Failed to save JSON:\n{e}"
        )


def on_selection_changed(self):
    """Handle tree widget selection change."""
    selected_item = self.treeWidget.currentItem()
    if not selected_item:
        return
        
    # Hide all graph widgets
    for widget in self.graph_mapping.values():
        widget.setVisible(False)
    
    # Show selected graph widget
    data = selected_item.data(0, 1)
    if data in self.graph_mapping:
        self.graph_mapping[data].setVisible(True)


def delete_dlt(main_window, dlt_item):
    """Remove DLT file and associated data."""
    if not dlt_item or dlt_item.parent():
        return  # Only handle top-level items
        
    file_path = dlt_item.data(0, 1)
    if not file_path:
        return
        
    # Confirm deletion
    reply = QMessageBox.question(
        main_window,
        "Confirm Deletion",
        f"Delete '{os.path.basename(file_path)}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
    if reply != QMessageBox.StandardButton.Yes:
        return
        
    # Remove graph mappings
    keys_to_remove = [
        key for key in list(main_window.graph_canvas_mapping.keys())
        if key[0] == file_path
    ]
    for key in keys_to_remove:
        main_window.graph_canvas_mapping.pop(key, None)
        
    # Remove graph widgets
    graph_keys = [
        key for key in list(main_window.graph_mapping.keys())
        if key[0] == file_path
    ]
    for key in graph_keys:
        widget = main_window.graph_mapping.pop(key, None)
        if widget:
            main_window.grapharea.removeWidget(widget)
            widget.deleteLater()
    
    # Remove data
    if file_path in main_window.struct_dictionary:
        del main_window.struct_dictionary[file_path]
        
    # Remove from tree
    main_window.treeWidget.invisibleRootItem().removeChild(dlt_item)