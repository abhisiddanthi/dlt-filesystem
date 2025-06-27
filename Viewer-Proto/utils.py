import os
import tempfile
import shutil
import atexit
import sys
import signal
import subprocess
import re
from PyQt6.QtWidgets import QListWidget, QAbstractItemView, QPushButton, QTreeWidget, QHeaderView, QInputDialog, QMessageBox, QWidget
from PyQt6.QtCore import Qt, QEvent, QObject, QEasingCurve, QPropertyAnimation, QTimer
from typing import Callable, Tuple

_invalid_re = re.compile(r'[^A-Za-z0-9 _-]')
_windows_reserved = {
    "CON","PRN","AUX","NUL",
    *(f"COM{i}" for i in range(1,10)),
    *(f"LPT{i}" for i in range(1,10))
}

def prompt_graph_name(parent, default_name: str = "New Graph") -> str | None:
    while True:
        text, ok = QInputDialog.getText(
            parent,
            "Graph Name",
            "Enter a name for the new graph:",
            text=default_name,
            flags=Qt.WindowType.WindowTitleHint
        )
        if not ok:
            return None

        name = text.strip()
        if not name:
            QMessageBox.warning(parent, "Invalid Name", "Graph name cannot be empty.")
            continue

        if _invalid_re.search(name):
            QMessageBox.warning(
                parent, "Invalid Name",
                "Only letters, numbers, spaces, underscores and hyphens are allowed."
            )
            continue

        if len(name) > 50:
            QMessageBox.warning(
                parent, "Name Too Long",
                "Graph name must be under 50 characters."
            )
            continue

        if name.upper() in _windows_reserved:
            QMessageBox.warning(
                parent, "Invalid Name",
                f"“{name}” is a reserved system name."
            )
            continue

        return name

class SmoothListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setVerticalScrollMode(
            QAbstractItemView.ScrollMode.ScrollPerPixel
        )
        self._anim = QPropertyAnimation(self.verticalScrollBar(), b"value", self)
        self._anim.setDuration(300)                          
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def wheelEvent(self, event):
        dy = event.pixelDelta().y()
        if not dy:
            dy = event.angleDelta().y() / 120 * self.verticalScrollBar().singleStep()

        sb = self.verticalScrollBar()
        start = sb.value()
        end = int(start - dy)
        self._anim.stop()
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

        event.accept()


def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return result
    except FileNotFoundError:
        print(f"Error: Command not found: {command[0]}")
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{' '.join(command)}' failed with return code {e.returncode}")
        print("Error output:", e.stderr)
    except Exception as e:
        print(f"Unexpected error: {e}")


def add_header_plus_button(
    tree_widget: QTreeWidget,
    slot: Callable[[], None],
    text: str = "+",
    size: Tuple[int, int] = (18, 18),
    margin: int = 0,
    tooltip: str = "Add new…"
) -> QPushButton:
    header: QHeaderView = tree_widget.header()
    btn = QPushButton(text, header)
    btn.setFixedSize(*size)
    btn.setToolTip(tooltip)
    btn.clicked.connect(slot)

    def _reposition() -> None:
        x = header.sectionViewportPosition(0) + header.sectionSize(0) - btn.width() - margin
        y = (header.height() - btn.height()) // 2
        btn.move(x, y)

    class _Filter(QObject):
        def eventFilter(self, watched, event):
            try:
                if watched in (header, tree_widget.viewport()) and event.type() in (
                    QEvent.Type.LayoutRequest,
                    QEvent.Type.UpdateRequest,
                    QEvent.Type.Resize,
                    QEvent.Type.Show
                ):
                    QTimer.singleShot(0, _reposition)
                if watched in (tree_widget.verticalScrollBar(), tree_widget.horizontalScrollBar()) and event.type() == QEvent.Type.Show:
                    QTimer.singleShot(0, _reposition)
            except RuntimeError:
                return False
            return super().eventFilter(watched, event)


    flt = _Filter(tree_widget)
    header.installEventFilter(flt)
    tree_widget.installEventFilter(flt)
    tree_widget.viewport().installEventFilter(flt)
    tree_widget.verticalScrollBar().installEventFilter(flt)
    tree_widget.horizontalScrollBar().installEventFilter(flt)

    QTimer.singleShot(0, _reposition)
    btn._hdr_filter = flt
    return btn

APP_TEMP_DIR = os.path.join(tempfile.gettempdir(), "proto_dashboard_temp")

def ensure_temp_dir():
    os.makedirs(APP_TEMP_DIR, exist_ok=True)

ensure_temp_dir()

def cleanup_temp_files():
    if os.path.exists(APP_TEMP_DIR):
        try:
            shutil.rmtree(APP_TEMP_DIR)
            print("Temporary files cleaned up.")
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")

atexit.register(cleanup_temp_files)

def signal_handler(sig, frame):
    print("Signal received, cleaning up temp files and exiting.")
    cleanup_temp_files()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

