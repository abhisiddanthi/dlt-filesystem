"""Utility functions and classes."""
import os
import tempfile
import shutil
import atexit
import sys
import signal
import subprocess
import re
from PyQt6.QtWidgets import (
    QListWidget, QAbstractItemView, QTreeWidget, 
    QHeaderView, QInputDialog, QMessageBox
)
from PyQt6.QtCore import (
    Qt, QEvent, QObject, QEasingCurve, 
    QPropertyAnimation, QTimer
)

# Constants for name validation
INVALID_CHARS_RE = re.compile(r'[^A-Za-z0-9 _-]')
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10))
}

APP_TEMP_DIR = os.path.join(tempfile.gettempdir(), "proto_dashboard_temp")


def prompt_graph_name(parent, default_name: str = "New Graph") -> str | None:
    """Prompt user for graph name with validation.
    
    Args:
        parent: Parent widget
        default_name: Default name suggestion
        
    Returns:
        Validated name or None if canceled
    """
    while True:
        name, ok = QInputDialog.getText(
            parent,
            "Graph Name",
            "Enter graph name:",
            text=default_name,
            flags=Qt.WindowType.WindowTitleHint
        )
        name = name.strip()
        
        # Handle cancellation
        if not ok:
            return None
            
        # Validate name
        if not name:
            QMessageBox.warning(parent, "Invalid", "Name cannot be empty")
            continue
            
        if INVALID_CHARS_RE.search(name):
            QMessageBox.warning(
                parent, "Invalid Characters",
                "Only letters, numbers, spaces, underscores and hyphens allowed"
            )
            continue
            
        if len(name) > 50:
            QMessageBox.warning(
                parent, "Too Long", 
                "Name must be under 50 characters"
            )
            continue
            
        if name.upper() in WINDOWS_RESERVED_NAMES:
            QMessageBox.warning(
                parent, "Reserved Name",
                f"'{name}' is a reserved system name"
            )
            continue
            
        return name


class SmoothListWidget(QListWidget):
    """List widget with smooth scrolling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self._animation = QPropertyAnimation(self.verticalScrollBar(), b"value", self)
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def wheelEvent(self, event):
        """Handle wheel events with smooth scrolling."""
        dy = event.pixelDelta().y()
        if not dy:
            # Fallback for devices without pixelDelta
            dy = event.angleDelta().y() / 120 * self.verticalScrollBar().singleStep()
            
        scroll_bar = self.verticalScrollBar()
        start = scroll_bar.value()
        end = int(start - dy)
        
        self._animation.stop()
        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()
        
        event.accept()


def run_command(command):
    """Run system command with error handling.
    
    Args:
        command: Command list to execute
        
    Returns:
        CompletedProcess object
    """
    try:
        return subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    except FileNotFoundError:
        print(f"Command not found: {command[0]}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Command failed ({e.returncode}): {' '.join(command)}")
        print("Error:", e.stderr)
        return e
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def add_header_plus_button(
    tree_widget: QTreeWidget,
    slot: callable,
    text: str = "+",
    size: tuple = (18, 18),
    margin: int = 0,
    tooltip: str = "Add new"
) -> QPushButton:
    """Add plus button to tree widget header.
    
    Args:
        tree_widget: Target tree widget
        slot: Slot to connect
        text: Button text
        size: Button size
        margin: Right margin
        tooltip: Button tooltip
        
    Returns:
        Created button
    """
    header = tree_widget.header()
    button = QPushButton(text, header)
    button.setFixedSize(*size)
    button.setToolTip(tooltip)
    button.clicked.connect(slot)

    def reposition():
        """Position button at header's right edge."""
        x_pos = (
            header.sectionViewportPosition(0) + 
            header.sectionSize(0) - 
            button.width() - 
            margin
        )
        y_pos = (header.height() - button.height()) // 2
        button.move(x_pos, y_pos)

    class EventFilter(QObject):
        """Event filter to reposition button on resize."""
        
        def eventFilter(self, watched, event):
            try:
                event_types = (
                    QEvent.Type.LayoutRequest,
                    QEvent.Type.UpdateRequest,
                    QEvent.Type.Resize,
                    QEvent.Type.Show
                )
                if watched in (header, tree_widget.viewport()) and event.type() in event_types:
                    QTimer.singleShot(0, reposition)
                if watched in (tree_widget.verticalScrollBar(), tree_widget.horizontalScrollBar()):
                    if event.type() == QEvent.Type.Show:
                        QTimer.singleShot(0, reposition)
            except RuntimeError:
                return False
            return super().eventFilter(watched, event)

    # Install event filters
    event_filter = EventFilter(tree_widget)
    header.installEventFilter(event_filter)
    tree_widget.installEventFilter(event_filter)
    tree_widget.viewport().installEventFilter(event_filter)
    tree_widget.verticalScrollBar().installEventFilter(event_filter)
    tree_widget.horizontalScrollBar().installEventFilter(event_filter)
    
    # Initial positioning
    QTimer.singleShot(0, reposition)
    return button


def ensure_temp_dir():
    """Create application temp directory if needed."""
    os.makedirs(APP_TEMP_DIR, exist_ok=True)


def cleanup_temp_files():
    """Remove all temporary files on exit."""
    if os.path.exists(APP_TEMP_DIR):
        try:
            shutil.rmtree(APP_TEMP_DIR)
            print("Cleaned temporary files")
        except Exception as e:
            print(f"Cleanup error: {e}")


def signal_handler(sig, frame):
    """Handle termination signals."""
    print("Exiting...")
    cleanup_temp_files()
    sys.exit(0)


# Initialize temp directory
ensure_temp_dir()

# Register cleanup handlers
atexit.register(cleanup_temp_files)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)