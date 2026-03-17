"""
ui/components/file_browser.py - File and folder picker widgets
"""

from pathlib import Path

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Signal

from ui.components.drag_drop_input import DragDropLineEdit


class FileBrowserWidget(QWidget):
    """File picker widget with drag-drop support."""
    
    path_changed = Signal(str)
    
    def __init__(self, file_filter="Text Files (*.txt);;All Files (*.*)", parent=None):
        super().__init__(parent)
        self.file_filter = file_filter
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.input = DragDropLineEdit(accept_type='file')
        self.input.setReadOnly(True)
        self.input.setPlaceholderText("Drag & drop .txt file here or click Browse...")
        self.input.setMinimumHeight(36)
        self.input.file_dropped.connect(self.path_changed.emit)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setMinimumHeight(36)
        self.browse_btn.setMaximumWidth(100)
        self.browse_btn.clicked.connect(self._on_browse)
        
        layout.addWidget(self.input, 1)
        layout.addWidget(self.browse_btn)
    
    def _on_browse(self):
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", self.file_filter
        )
        if file_path:
            self.set_path(file_path)
            self.path_changed.emit(file_path)
    
    def set_path(self, path: str):
        """Set the file path."""
        self.input.setText(path)
    
    def get_path(self) -> str:
        """Get the current file path."""
        return self.input.text().strip()


class FolderBrowserWidget(QWidget):
    """Folder picker widget with drag-drop support."""
    
    path_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI."""
        layout = QHBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.input = DragDropLineEdit(accept_type='folder')
        self.input.setReadOnly(True)
        self.input.setPlaceholderText("Drag & drop folder here or click Browse...")
        self.input.setMinimumHeight(36)
        self.input.file_dropped.connect(self.path_changed.emit)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setMinimumHeight(36)
        self.browse_btn.setMaximumWidth(100)
        self.browse_btn.clicked.connect(self._on_browse)
        
        layout.addWidget(self.input, 1)
        layout.addWidget(self.browse_btn)
    
    def _on_browse(self):
        """Handle browse button click."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", "")
        if folder_path:
            self.set_path(folder_path)
            self.path_changed.emit(folder_path)
    
    def set_path(self, path: str):
        """Set the folder path."""
        self.input.setText(path)
    
    def get_path(self) -> str:
        """Get the current folder path."""
        return self.input.text().strip()
