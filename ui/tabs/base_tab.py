"""
ui/tabs/base_tab.py - Base class for all tab content widgets
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal


class BaseTab(QWidget):
    """Base class for all tab content widgets with common signals."""
    
    # Signals emitted by any tab
    progress_updated = Signal(int, int, str)  # current, total, message
    log_message = Signal(str)
    status_updated = Signal(str)
    finished = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_processing = False
    
    def setup_ui(self):
        """Override in subclasses to setup UI."""
        raise NotImplementedError
    
    def on_start(self):
        """Called when processing starts. Override in subclasses."""
        self.is_processing = True
    
    def on_stop(self):
        """Called when processing stops. Override in subclasses."""
        self.is_processing = False
    
    def cleanup(self):
        """Called when tab is closed. Override in subclasses."""
        pass
