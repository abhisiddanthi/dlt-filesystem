"""Graph creation and management utilities."""
import numpy as np
from datetime import datetime
import pyqtgraph as pg
from pyqtgraph import PlotWidget, DateAxisItem
from animate import PlotAnimator
from PyQt6.QtWidgets import (
    QMessageBox, QInputDialog, QStyle, QToolButton, QHBoxLayout, QWidget,
    QVBoxLayout, QListWidgetItem, QLabel, QSlider
)
from PyQt6.QtCore import Qt
from utils import prompt_graph_name
from dateutil.parser import parse as parse_dt


def try_parse_value(value):
    """Attempt to parse value into float or timestamp.
    
    Args:
        value: Input value to parse
        
    Returns:
        Parsed numeric value or None
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


def add_graph(self, identifiers, container, selected_key):
    """Add a new graph to the UI.
    
    Args:
        identifiers: (dltpath, app_id, ctx_id)
        container: List widget container
        selected_key: Data key to visualize
    """
    dltpath, app_id, ctx_id = identifiers

    try:
        # Extract data based on selected key
        keys = selected_key.split(" > ")
        base = self.struct_dictionary[dltpath][app_id][ctx_id]

        # Validate root key
        root_key = keys[0]
        if root_key not in base or not isinstance(base[root_key], list):
            raise ValueError(f'No data found for "{root_key}"')
        root_list = [item for item in base[root_key] if isinstance(item, dict)]
        if not root_list:
            raise ValueError(f'No entries under "{root_key}"')

        # Traverse nested structure
        pairs = [(item, item) for item in root_list]
        for key in keys[1:]:
            new_pairs = []
            for root_item, curr in pairs:
                # Handle dictionaries
                if isinstance(curr, dict) and key in curr:
                    val = curr[key]
                    if isinstance(val, dict):
                        new_pairs.append((root_item, val))
                    elif isinstance(val, list):
                        for elem in val:
                            if isinstance(elem, dict):
                                new_pairs.append((root_item, elem))
                # Handle lists
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
            raise ValueError(f'No data at "{selected_key}"')

        inner_data_list = [root_item for root_item, _ in pairs]
        first_leaf = pairs[0][1]

        # Find plottable fields
        def is_number_list(x):
            return isinstance(x, list) and all(isinstance(e, (int, float, str)) for e in x)

        available_fields = []
        for k, v in first_leaf.items():
            if k == "timestamp" or k.startswith('@'):
                continue
            if isinstance(v, (int, float, str)) or is_number_list(v):
                available_fields.append(k)

        if not available_fields:
            raise ValueError(f'No plottable fields in "{selected_key}"')

        # Prompt for Y-axis field
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

        # Extract data points
        x_values, y_values = [], []
        for root_item, leaf_item in pairs:
            raw_x = root_item.get(x_field)
            if raw_x is None:
                continue

            # Parse X value
            try:
                if isinstance(raw_x, str):
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

            # Handle single values and lists
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
            raise ValueError("No valid numeric data extracted")

        # Prompt for graph mode
        graph_mode, ok_mode = QInputDialog.getItem(
            self,
            "Graph Mode",
            "Create new graph or add to existing?",
            ["New Graph", "Existing Graph"],
            editable=False
        )
        if not ok_mode:
            return
        
        # Downsample large datasets
        x_arr = np.array(x_values)
        y_arr = np.array(y_values)
        max_points = 10000
        if len(x_arr) > max_points:
            idx = np.linspace(0, len(x_arr) - 1, max_points).astype(int)
            x_arr, y_arr = x_arr[idx], y_arr[idx]

        # Create plot item
        line = pg.PlotDataItem(
            x=x_arr, y=y_arr,
            pen=pg.mkPen(color='g', width=1),
            symbol='o', symbolSize=3,
            symbolPen=None,
            symbolBrush=pg.mkBrush(0, 0, 0, 255),
            name=y_field
        )

        if graph_mode == "New Graph":
            # Prompt for graph name
            clean_key = selected_key.replace('>', '').strip()
            default_name = f"{clean_key} {y_field}"
            while True:
                graph_name = prompt_graph_name(self, default_name)
                if not graph_name:
                    return
                key = (dltpath, app_id, ctx_id, graph_name)
                if key in self.graph_canvas_mapping:
                    QMessageBox.warning(
                        self, "Duplicate Name",
                        f"Graph '{graph_name}' already exists"
                    )
                    continue
                break

            # Create plot widget
            if isinstance(inner_data_list[0].get(x_field), str):
                axis = DateAxisItem(orientation='bottom')
                plot_widget = PlotWidget(axisItems={'bottom': axis})
            else:
                plot_widget = PlotWidget()
                
            plot_widget.addLegend()
            plot_widget.addItem(line)
            plot_widget.setLabel('bottom', x_field)
            plot_widget.setLabel('left', "Data")
            plot_widget.setTitle(graph_name)
            plot_widget.showGrid(x=True, y=True)
            plot_widget.setFixedHeight(300)
            plot_widget.setBackground('white')
            plot_widget.enableAutoRange(enable=True)
            
            # Store references
            self.graph_canvas_mapping[key] = plot_widget
            if not hasattr(self, 'animators'):
                self.animators = {}
            self.animators[key] = []
            
            # Create animator
            animator = PlotAnimator(plot_widget, x_values, y_values)
            self.animators[key].append(animator)
            
            # Create control buttons
            btn_play = self._create_tool_button(
                QStyle.StandardPixmap.SP_MediaPlay,
                "Play Graph",
                lambda: [a.play() for a in self.animators[key]]
            )
            btn_pause = self._create_tool_button(
                QStyle.StandardPixmap.SP_MediaPause,
                "Pause Graph",
                lambda: [a.pause() for a in self.animators[key]]
            )
            btn_reset = self._create_tool_button(
                QStyle.StandardPixmap.SP_BrowserReload,
                "Reset Graph",
                lambda: [a.reset() for a in self.animators[key]]
            )
            
            # Create speed slider
            lbl_speed = QLabel("Speed:")
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(10, 200)
            slider.setValue(animator.speed)
            slider.setTickPosition(QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(10)
            slider.valueChanged.connect(
                lambda val: [a.set_speed(val) for a in self.animators[key]]
            )
            
            # Create delete button
            delete_btn = self._create_tool_button(
                QStyle.StandardPixmap.SP_TitleBarCloseButton,
                "Delete Graph",
                lambda: self._delete_graph(
                    dltpath, app_id, ctx_id, graph_name, container
                )
            )
            
            # Assemble header
            header_widget = QWidget()
            header = QHBoxLayout(header_widget)
            header.setContentsMargins(15, 0, 15, 0)
            header.addStretch()
            header.addWidget(btn_play)
            header.addWidget(btn_pause)
            header.addWidget(btn_reset)
            header.addWidget(lbl_speed)
            header.addWidget(slider)
            header.addWidget(delete_btn)
            
            # Create container widget
            item_widget = QWidget()
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(15, 0, 15, 0)
            item_layout.addWidget(header_widget)
            item_layout.addWidget(plot_widget)
            
            # Add to list
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            container.addItem(item)
            container.setItemWidget(item, item_widget)
            
        else:  # Add to existing graph
            existing_graphs = [
                key for key in self.graph_canvas_mapping.keys() 
                if key[0] == dltpath
            ]
            if not existing_graphs:
                QMessageBox.information(
                    self, "No Graphs", 
                    "No existing graphs found. Creating new graph"
                )
                # Recursively create new graph
                return add_graph(self, identifiers, container, selected_key)
                
            # Select existing graph
            existing_names = [key[3] for key in existing_graphs]
            selected_name, ok_sel = QInputDialog.getItem(
                self, "Select Graph", "Choose graph:", existing_names, editable=False
            )
            if not ok_sel:
                return
                
            # Find selected graph
            selected_key = next(
                (k for k in existing_graphs if k[3] == selected_name), None
            )
            if not selected_key:
                raise ValueError("Selected graph not found")
                
            # Add to existing plot
            plot_widget = self.graph_canvas_mapping[selected_key]
            if not plot_widget.getPlotItem().legend:
                plot_widget.addLegend()
            plot_widget.addItem(line)
            
            # Create animator
            if not hasattr(self, 'animators'):
                self.animators = {}
            if selected_key not in self.animators:
                self.animators[selected_key] = []
                
            animator = PlotAnimator(plot_widget, x_values, y_values)
            self.animators[selected_key].append(animator)
            
    except Exception as e:
        QMessageBox.critical(self, "Graph Error", f"Failed to add graph:\n{e}")


def delete_selected_graph(self, identifiers, graph_name, container):
    """Remove graph from UI and internal mappings.
    
    Args:
        identifiers: (dltpath, app_id, ctx_id)
        graph_name: Name of graph to delete
        container: List widget container
    """
    dltpath, app_id, ctx_id = identifiers
    key = (dltpath, app_id, ctx_id, graph_name)
    
    # Remove from mappings
    canvas = self.graph_canvas_mapping.pop(key, None)
    if not canvas:
        return
        
    # Remove from animators
    if hasattr(self, 'animators') and key in self.animators:
        del self.animators[key]
    
    # Remove from UI
    for row in range(container.count()):
        item = container.item(row)
        item_widget = container.itemWidget(item)
        if not item_widget:
            continue
            
        # Find matching canvas
        layout = item_widget.layout()
        if layout and layout.count() > 1:
            graph_child = layout.itemAt(1).widget()
            if graph_child is canvas:
                container.takeItem(row)
                item_widget.deleteLater()
                break

    # Clean up
    canvas.deleteLater()