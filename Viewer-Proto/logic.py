import os
import json
from PyQt6.QtCore import Qt
from dlt_worker import DLTWorker
from utils import APP_TEMP_DIR, run_command
from utils import SmoothListWidget
from PyQt6.QtWidgets import ( QPushButton, 
    QTreeWidgetItem, QFileDialog, QMessageBox, 
    QVBoxLayout, QWidget, QComboBox, QAbstractItemView,
    QHBoxLayout, QLabel, QStyle, QToolButton, QFileDialog
)

def addProto(main_window):
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getOpenFileName(main_window, "Open Proto File", "", "Proto Files (*.proto)")

    try: 
        if file_path:
            protopath = os.path.dirname(file_path)
            proto = run_command(['protoc', f'--proto_path={protopath}', f'--python_out={APP_TEMP_DIR}', file_path])

            if proto.returncode == 0:
                main_window.protoLabel.setText(f"Loaded: {file_path.split('/')[-1]}")
    
    except Exception as e:
        print(f"Proto filepath incorrect: {e}")

def addDLT(main_window):
    if main_window.protoLabel.text() == "No Proto Added":
        QMessageBox.critical(main_window, "Proto File Error", "Please add logger.proto file first")
        return

    file_dialog = QFileDialog()
    dltpath, _ = file_dialog.getOpenFileName(main_window, "Open DLT File", "", "DLT Files (*.dlt)")
    if not dltpath:
        return

    protofilename = main_window.protoLabel.text()[8:].replace(".proto", "")
    module_name = f"{protofilename}_pb2"

    if dltpath in main_window.struct_dictionary:
        QMessageBox.critical(main_window, "DLT Processing Error", "This file is already present")
        return

    main_window.struct_dictionary[dltpath] = {}
    main_window.worker = DLTWorker(dltpath, module_name)
    main_window.worker.finished.connect(main_window.onDLTProcessed)
    main_window.worker.error.connect(main_window.onDLTError)
    main_window.worker.start()

def onDLTProcessed(self, dltpath, struct_dict):
    self.struct_dictionary[dltpath] = struct_dict

    grouped_data = {}

    for app_id, ctx_dict in struct_dict.items():
        grouped_data.setdefault(app_id, {})
        for ctx_id in ctx_dict:
            grouped_data[app_id].setdefault(ctx_id, {})

    for app_id, ctx_dict in struct_dict.items():
        for ctx_id, msg_dict in ctx_dict.items():
            for msg_type, entries in msg_dict.items():
                grouped_data[app_id][ctx_id].setdefault(msg_type, [])
                for entry in entries:
                    grouped_data[app_id][ctx_id][msg_type].append(entry)


    dlt_item = QTreeWidgetItem(self.treeWidget)
    dlt_item.setData(0, 1, dltpath)

    container = QWidget()
    hbox = QHBoxLayout(container)
    hbox.setContentsMargins(0, 0, 0, 0)
    hbox.setSpacing(4)

    lbl = QLabel(os.path.basename(dltpath))
    hbox.addWidget(lbl)

    delete_dlt_btn = QToolButton()
    icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
    delete_dlt_btn.setIcon(icon)
    delete_dlt_btn.setAutoRaise(True)           
    delete_dlt_btn.setToolTip("Delete Graph")   
    delete_dlt_btn.setFixedSize(16, 16)  
    delete_dlt_btn.clicked.connect(
        lambda _, selected_dlt=dlt_item: self.deleteDLT(selected_dlt)
    )
    
    json_btn = QPushButton("JSON") 
    json_btn.clicked.connect(lambda _, d=dltpath, s=struct_dict: self.convertToJSON(d, s))

    hbox.addWidget(json_btn)
    hbox.addWidget(delete_dlt_btn)

    self.treeWidget.setItemWidget(dlt_item, 0, container)

    for app_id, ctxs in grouped_data.items():
        app_item = QTreeWidgetItem(dlt_item, [f"AppID: {app_id}"])
        for ctx_id, messages in ctxs.items():
            ctx_item = QTreeWidgetItem(app_item, [f"CxtID: {ctx_id}"])
            ctx_item.setData(0, 1, (dltpath, app_id, ctx_id))
     
            graph_container = SmoothListWidget()
            graph_container.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
            graph_container.setDefaultDropAction(Qt.DropAction.MoveAction)
            graph_container.setSpacing(4)     
            graph_container.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            graph_container.setSpacing(10) 
            graph_container.setAutoScroll(True)
            graph_container.setAutoScrollMargin(80) 

            graph_container.setStyleSheet("""
                SmoothListWidget::item:selected {
                    background: transparent;
                }
            """)

            graph_type_combo = QComboBox()
            graph_type_combo.addItems(messages.keys())

            add_graph_btn = QPushButton(f"Add Graph for {ctx_id}")
            add_graph_btn.clicked.connect(
                lambda _, dp=dltpath, aid=app_id, cid=ctx_id, gc=graph_container, combo=graph_type_combo:
                self.addGraph((dp, aid, cid), gc, combo.currentText())
            )

            graph_widget = QWidget()
            graph_layout = QVBoxLayout(graph_widget)
            graph_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
            graph_layout.addWidget(graph_type_combo)
            graph_layout.addWidget(add_graph_btn)
            graph_layout.addWidget(graph_container)
            graph_widget.setVisible(False)

            self.grapharea.addWidget(graph_widget)
            self.graph_mapping[(dltpath, app_id, ctx_id)] = graph_widget


def onDLTError(main_window, message):
    QMessageBox.critical(main_window, "DLT Processing Error", message)

def convertToJSON(self, dltpath, struct_dict):
    self.struct_dictionary[dltpath] = struct_dict
    file_path, _ = QFileDialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json)")
    if file_path:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(struct_dict, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "Success", f"File saved successfully at:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")
    else:
        QMessageBox.information(self, "Cancelled", "Save operation was cancelled.")


def onSelectionChanged(self):
    selected_item = self.treeWidget.currentItem()
    if selected_item:
        data = selected_item.data(0, 1)
        for widget in self.graph_mapping.values():
            widget.setVisible(False)
        if data in self.graph_mapping:
            self.graph_mapping[data].setVisible(True)

def deleteDLT(main_window, selected_dlt):        
    if selected_dlt and not selected_dlt.parent():  
        file_path = selected_dlt.data(0, 1)  

        reply = QMessageBox.question(
            main_window,
            "Confirm Deletion",
            f"Are you sure you want to delete this file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            keys_to_remove = [
                key for key in list(main_window.graph_canvas_mapping.keys())
                if key[0] == file_path
            ]
            for key in keys_to_remove:
                main_window.graph_canvas_mapping.pop(key, None)

            graph_keys = [
                key for key in list(main_window.graph_mapping.keys())
                if key[0] == file_path
            ]
            for key in graph_keys:
                widget = main_window.graph_mapping.pop(key, None)
                if widget:
                    main_window.grapharea.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()

            if file_path in main_window.struct_dictionary:
                del main_window.struct_dictionary[file_path]

            main_window.treeWidget.invisibleRootItem().removeChild(selected_dlt)