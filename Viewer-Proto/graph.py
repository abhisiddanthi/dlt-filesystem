import numpy as np
from datetime import datetime
import pyqtgraph as pg
from pyqtgraph import PlotWidget, DateAxisItem
from animate import PlotAnimator
from PyQt6.QtWidgets import ( QMessageBox, QInputDialog, QStyle, QToolButton, QHBoxLayout, QWidget, QVBoxLayout, QListWidgetItem, QLabel, QSlider )
from PyQt6.QtCore import Qt
from utils import prompt_graph_name
from datetime import datetime
from dateutil.parser import parse as parse_dt  # pip install python-dateutil

def try_parse_value(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        try:
            dt = datetime.strptime(value, "%H:%M:%S.%f")
            dummy_date = datetime(1970, 1, 1, dt.hour, dt.minute, dt.second, dt.microsecond)
            return dummy_date.timestamp()
        except Exception:
            return None

def addGraph(self, identifiers, container, selected_key):
    dltpath, app_id, ctx_id = identifiers

    try:
        # ── BEGIN REPLACEMENT ──
        keys = selected_key.split(" > ")
        base = self.struct_dictionary[dltpath][app_id][ctx_id]

        root_key = keys[0]
        if root_key not in base or not isinstance(base[root_key], list):
            raise ValueError(f'No list found for "{root_key}" in the data.')
        root_list = [item for item in base[root_key] if isinstance(item, dict)]
        if not root_list:
            raise ValueError(f'No entries found under "{root_key}".')

        pairs = [(item, item) for item in root_list]
        for key in keys[1:]:
            new_pairs = []
            for root_item, curr in pairs:
                if isinstance(curr, dict) and key in curr:
                    val = curr[key]
                    if isinstance(val, dict):
                        new_pairs.append((root_item, val))
                    elif isinstance(val, list):
                        for elem in val:
                            if isinstance(elem, dict):
                                new_pairs.append((root_item, elem))
                elif isinstance(curr, list):
                    for elem in curr:
                        if isinstance(elem, dict) and key in elem:
                            val = elem[key]
                            if isinstance(val, dict):
                                new_pairs.append((root_item, val))
                            elif isinstance(val, list):
                                for sub in val:
                                    if isinstance(sub, dict):
                                        new_pairs.append((root_item, sub))
            pairs = new_pairs

        if not pairs:
            raise ValueError(f'No data entries found at "{selected_key}".')

        inner_data_list = [root_item for root_item, _ in pairs]
        first_leaf = pairs[0][1]

        def is_number_list(x):
            return isinstance(x, list) and all(isinstance(e, (int, float, str)) for e in x)

        available_fields = []
        for k, v in first_leaf.items():
            if k == "timestamp" or k.startswith('@'):
                continue
            if isinstance(v, (int, float, str)) or is_number_list(v):
                available_fields.append(k)

        if not available_fields:
            raise ValueError(f'No plottable fields in "{selected_key}".')

        x_field = "timestamp"
        y_field, ok_y = QInputDialog.getItem(
            self,
            "Select Data",
            f"Choose data field from {selected_key}:",
            available_fields,
            editable=False
        )
        if not ok_y:
            return

        x_values, y_values = [], []

        for root_item, leaf_item in pairs:
            raw_x = root_item.get(x_field)
            if raw_x is None:
                continue

            # ─── parse X ───
            try:
                if isinstance(raw_x, str):
                    # parse and convert to float-seconds since epoch
                    dt = parse_dt(raw_x)
                    x_val = dt.timestamp()
                else:
                    x_val = try_parse_value(raw_x)
            except Exception:
                continue
            if x_val is None:
                continue

            raw_y = leaf_item.get(y_field)
            if raw_y is None:
                continue

            def append_point(xv, y_elem):
                try:
                    yv = try_parse_value(y_elem)
                except Exception:
                    return
                if yv is not None:
                    x_values.append(xv)
                    y_values.append(yv)

            if isinstance(raw_y, list):
                for elem in raw_y:
                    append_point(x_val, elem)
            else:
                append_point(x_val, raw_y)

        if not x_values or not y_values:
            raise ValueError("Unable to extract valid numeric data for the selected fields.")
        # ── END REPLACEMENT ──

        graph_mode, ok_mode = QInputDialog.getItem(
            self,
            "Graph Mode",
            "Would you like to create a new graph or add data to an existing graph?",
            ["New Graph", "Existing Graph"],
            editable=False
        )
        if not ok_mode:
            return
        
        x_arr = np.array(x_values)
        y_arr = np.array(y_values)
        max_points = 10000
        if len(x_arr) > max_points:
            idx = np.linspace(0, len(x_arr) - 1, max_points).astype(int)
            x_arr, y_arr = x_arr[idx], y_arr[idx]

        line = pg.PlotDataItem(
            x=x_arr, y=y_arr,
            pen=pg.mkPen(color='g', width=1),
            symbol='o', symbolSize=3,
            symbolPen=None,
            symbolBrush=pg.mkBrush(0, 0, 0, 255),
            name=y_field
        )

        if graph_mode == "New Graph":
            clean_key = selected_key.replace('>', '').strip()
            default_name = f"{clean_key} {y_field}"
            while True:
                graph_name = prompt_graph_name(self, default_name)
                if not graph_name:
                    return
                key = (dltpath, app_id, ctx_id, graph_name)
                if key in self.graph_canvas_mapping:
                    QMessageBox.warning(
                        self, "Duplicate Graph Name",
                        f"A graph named '{graph_name}' already exists for this DLT file. Please choose a different name."
                    )
                    continue
                break

            if isinstance(inner_data_list[0].get(x_field), str):
                axis = DateAxisItem(orientation='bottom')
                self.plot_widget = PlotWidget(axisItems={'bottom': axis})
            else:
                self.plot_widget = PlotWidget()

            self.plot_widget.addLegend()
            self.plot_widget.addItem(line)
            self.plot_widget.getPlotItem().setLabel('bottom', x_field)
            self.plot_widget.getPlotItem().setLabel('left', "Data")
            self.plot_widget.getPlotItem().setTitle(graph_name)
            self.plot_widget.showGrid(x=True, y=True)
            self.plot_widget.setFixedHeight(300)
            self.plot_widget.setBackground('white')
            self.plot_widget.enableAutoRange(enable=True)
            self.graph_canvas_mapping[(dltpath, app_id, ctx_id, graph_name)] = self.plot_widget
            if not hasattr(self, 'animators'):
                self.animators = {}
            self.animators[(dltpath, app_id, ctx_id, graph_name)] = []
            animator = PlotAnimator(self.plot_widget, x_values, y_values)
            self.animators[(dltpath, app_id, ctx_id, graph_name)].append(animator)
            btn_play = QToolButton()
            icon_play = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            btn_play.setIcon(icon_play)
            btn_play.setAutoRaise(True)
            btn_play.setToolTip("Play Graph")
            btn_play.setFixedSize(16, 16)
            btn_play.clicked.connect(lambda: [a.play() for a in self.animators[(dltpath, app_id, ctx_id, graph_name)]])
            btn_pause = QToolButton()
            icon_pause = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            btn_pause.setIcon(icon_pause)
            btn_pause.setAutoRaise(True)
            btn_pause.setToolTip("Pause Graph")
            btn_pause.setFixedSize(16, 16)
            btn_pause.clicked.connect(lambda: [a.pause() for a in self.animators[(dltpath, app_id, ctx_id, graph_name)]])
            btn_reset = QToolButton()
            icon_reset = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
            btn_reset.setIcon(icon_reset)
            btn_reset.setAutoRaise(True)
            btn_reset.setToolTip("Reset Play Graph")
            btn_reset.setFixedSize(16, 16)
            btn_reset.clicked.connect(lambda: [a.reset() for a in self.animators[(dltpath, app_id, ctx_id, graph_name)]])
            lbl_speed = QLabel("Speed:")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(10, 200)
            slider.setValue(animator.speed)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(10)
            slider.valueChanged.connect(lambda val: [a.setSpeed(val) for a in self.animators[(dltpath, app_id, ctx_id, graph_name)]])
            delete_graph_btn = QToolButton()
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
            delete_graph_btn.setIcon(icon)
            delete_graph_btn.setAutoRaise(True)
            delete_graph_btn.setToolTip("Delete Graph")
            delete_graph_btn.setFixedSize(16, 16)
            delete_graph_btn.clicked.connect(lambda _, dp=dltpath, aid=app_id, cid=ctx_id, gn=graph_name, gc=container, btn=delete_graph_btn: (btn.deleteLater(), self.deleteSelectedGraph((dp, aid, cid), gn, gc)))
            header_widget = QWidget()
            header = QHBoxLayout(header_widget)
            header.setContentsMargins(15, 0, 15, 0)
            header.addStretch()
            header.addWidget(btn_play)
            header.addWidget(btn_pause)
            header.addWidget(btn_reset)
            header.addWidget(lbl_speed)
            header.addWidget(slider)
            header.addWidget(delete_graph_btn)
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(15, 0, 15, 0)
            item_layout.addWidget(header_widget)
            item_layout.addWidget(self.plot_widget)
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            container.addItem(item)
            container.setItemWidget(item, item_widget)
        else:
            existing_graphs = [key for key in self.graph_canvas_mapping.keys() if key[0] == dltpath]
            if not existing_graphs:
                QMessageBox.information(self, "No Existing Graph", "No existing graphs found for this file. Creating a new graph instead.")
                clean_key = selected_key.replace('>', '').strip()
                default_name = f"{clean_key} {y_field}"
                while True:
                    graph_name = prompt_graph_name(self, default_name)
                    if not graph_name:
                        return
                    if (dltpath, app_id, ctx_id, graph_name) in self.graph_canvas_mapping:
                        QMessageBox.warning(self, "Duplicate Graph Name", f"A graph named '{graph_name}' already exists for this DLT file. Please choose a different name.")
                        continue
                    break
                if isinstance(inner_data_list[0].get(x_field), str):
                    axis = DateAxisItem(orientation='bottom')
                    self.plot_widget = PlotWidget(axisItems={'bottom': axis})
                else:
                    self.plot_widget = PlotWidget()
                self.plot_widget.addLegend()
                self.plot_widget.addItem(line)
                self.plot_widget.getPlotItem().setLabel('bottom', x_field)
                self.plot_widget.getPlotItem().setLabel('left', "Data")
                self.plot_widget.getPlotItem().setTitle(graph_name)
                self.plot_widget.showGrid(x=True, y=True)
                self.plot_widget.setFixedHeight(300)
                self.plot_widget.setBackground('white')
                self.plot_widget.enableAutoRange(enable=True)
                self.graph_canvas_mapping[(dltpath, app_id, ctx_id, graph_name)] = self.plot_widget
                if not hasattr(self, 'animators'):
                    self.animators = {}
                self.animators[(dltpath, app_id, ctx_id, graph_name)] = []
                animator = PlotAnimator(self.plot_widget, x_values, y_values)
                self.animators[(dltpath, app_id, ctx_id, graph_name)].append(animator)
                btn_play = QToolButton()
                icon_play = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
                btn_play.setIcon(icon_play)
                btn_play.setAutoRaise(True)
                btn_play.setToolTip("Play Graph")
                btn_play.setFixedSize(16, 16)
                btn_play.clicked.connect(lambda: [a.play() for a in self.animators[(dltpath, app_id, ctx_id, graph_name)]])
                btn_pause = QToolButton()
                icon_pause = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
                btn_pause.setIcon(icon_pause)
                btn_pause.setAutoRaise(True)
                btn_pause.setToolTip("Pause Graph")
                btn_pause.setFixedSize(16, 16)
                btn_pause.clicked.connect(lambda: [a.pause() for a in self.animators[(dltpath, app_id, ctx_id, graph_name)]])
                btn_reset = QToolButton()
                icon_reset = self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
                btn_reset.setIcon(icon_reset)
                btn_reset.setAutoRaise(True)
                btn_reset.setToolTip("Reset Play Graph")
                btn_reset.setFixedSize(16, 16)
                btn_reset.clicked.connect(lambda: [a.reset() for a in self.animators[(dltpath, app_id, ctx_id, graph_name)]])
                lbl_speed = QLabel("Speed:")
                slider = QSlider(Qt.Orientation.Horizontal)
                slider.setRange(10, 200)
                slider.setValue(animator.speed)
                slider.setTickPosition(QSlider.TickPosition.TicksBelow)
                slider.setTickInterval(10)
                slider.valueChanged.connect(lambda val: [a.setSpeed(val) for a in self.animators[(dltpath, app_id, ctx_id, graph_name)]])
                delete_graph_btn = QToolButton()
                icon = self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton)
                delete_graph_btn.setIcon(icon)
                delete_graph_btn.setAutoRaise(True)
                delete_graph_btn.setToolTip("Delete Graph")
                delete_graph_btn.setFixedSize(16, 16)
                delete_graph_btn.clicked.connect(lambda _, dp=dltpath, aid=app_id, cid=ctx_id, gn=graph_name, gc=container, btn=delete_graph_btn: (btn.deleteLater(), self.deleteSelectedGraph((dp, aid, cid), gn, gc)))
                header_widget = QWidget()
                header = QHBoxLayout(header_widget)
                header.setContentsMargins(15, 0, 15, 0)
                header.addStretch()
                header.addWidget(btn_play)
                header.addWidget(btn_pause)
                header.addWidget(btn_reset)
                header.addWidget(lbl_speed)
                header.addWidget(slider)
                header.addWidget(delete_graph_btn)
                item_widget = QWidget()
                item_layout = QVBoxLayout(item_widget)
                item_layout.setContentsMargins(15, 0, 15, 0)
                item_layout.addWidget(header_widget)
                item_layout.addWidget(self.plot_widget)
                item = QListWidgetItem()
                item.setSizeHint(item_widget.sizeHint())
                container.addItem(item)
                container.setItemWidget(item, item_widget)
                return
            existing_graph_names = [key[3] for key in existing_graphs]
            selected_graph_name, ok_sel = QInputDialog.getItem(self, "Select Existing Graph", "Select an existing graph to add data:", existing_graph_names, editable=False)
            if not ok_sel:
                return
            selected_graph_key = next((key for key in existing_graphs if key[3] == selected_graph_name), None)
            if selected_graph_key is None:
                raise ValueError("Selected graph not found.")
            self.plot_widget = self.graph_canvas_mapping[selected_graph_key]
            if not self.plot_widget.getPlotItem().legend:
                self.plot_widget.addLegend()
            self.plot_widget.addItem(line)
            if not hasattr(self, 'animators'):
                self.animators = {}
            if selected_graph_key not in self.animators:
                self.animators[selected_graph_key] = []
            animator = PlotAnimator(self.plot_widget, x_values, y_values)
            self.animators[selected_graph_key].append(animator)
    except Exception as e:
        QMessageBox.critical(self, "Error", f"Failed to add graph:\n{e}")

def deleteSelectedGraph(self, identifiers, graph_name, container):
    dltpath, app_id, ctx_id = identifiers
    canvas = self.graph_canvas_mapping.pop(
        (dltpath, app_id, ctx_id, graph_name), 
        None
    )
    if not canvas:
        return
    for row in range(container.count()):
        item      = container.item(row)
        item_wdg  = container.itemWidget(item)
        if not item_wdg:
            continue
        graph_child = None
        layout      = item_wdg.layout()
        if layout and layout.count() > 1:
            graph_child = layout.itemAt(1).widget()
        if graph_child is canvas:
            removed_item = container.takeItem(row)
            item_wdg.setParent(None)
            item_wdg.deleteLater()
            del removed_item
            break

    canvas.setParent(None)
    canvas.deleteLater()

