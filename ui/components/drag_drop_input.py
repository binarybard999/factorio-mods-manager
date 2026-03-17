"""
ui/components/drag_drop_input.py - Drag-drop enabled line edit widgets
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import QLineEdit, QMessageBox
from PySide6.QtCore import Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent


logger = logging.getLogger(__name__)


class DragDropLineEdit(QLineEdit):
    """QLineEdit with drag-drop support for files/folders."""
    
    file_dropped = Signal(str)
    
    def __init__(self, accept_type='file', parent=None):
        """
        Args:
            accept_type: 'file' for .txt files, 'folder' for directories
            parent: Parent widget
        """
        super().__init__(parent)
        self.accept_type = accept_type
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events for URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            
            if self.accept_type == 'file':
                if path.endswith('.txt'):
                    self.setText(path)
                    self.file_dropped.emit(path)
                    logger.info(f"Dropped file: {path}")
                else:
                    QMessageBox.warning(None, "Invalid File", "Please drop a .txt file")
            
            elif self.accept_type == 'folder':
                if Path(path).is_dir():
                    self.setText(path)
                    self.file_dropped.emit(path)
                    logger.info(f"Dropped folder: {path}")
                else:
                    parent = Path(path).parent
                    self.setText(str(parent))
                    self.file_dropped.emit(str(parent))
                    logger.info(f"Dropped file, using parent folder: {parent}")
