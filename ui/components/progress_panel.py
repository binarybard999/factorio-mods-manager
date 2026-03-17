"""
ui/components/progress_panel.py - Shared progress bar and log display component
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QTextEdit, QLabel, QFrame
from PySide6.QtCore import Qt

from ui.modern_theme import ModernUIHelper


class ProgressLogPanel(QWidget):
    """Shared progress bar + log display component used by multiple tabs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress section
        progress_title = QLabel("Progress")
        progress_title.setFont(ModernUIHelper.create_heading_font())
        main_layout.addWidget(progress_title)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(24)
        main_layout.addWidget(self.progress_bar)
        
        # Progress info
        progress_info = QHBoxLayout()
        self.progress_label = QLabel("Ready")
        self.progress_label.setObjectName("statusLabel")
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        progress_info.addWidget(self.progress_label)
        progress_info.addStretch()
        progress_info.addWidget(self.status_label)
        main_layout.addLayout(progress_info)
        
        # Error display
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        self.error_label.setMinimumHeight(35)
        self.error_label.setObjectName("errorLabel")
        main_layout.addWidget(self.error_label)
        
        # Log section
        log_title = QLabel("Processing Log")
        log_title.setFont(ModernUIHelper.create_heading_font())
        main_layout.addWidget(log_title)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(150)
        main_layout.addWidget(self.log_output, 1)
    
    def set_progress(self, current: int, total: int):
        """Update progress bar and label."""
        if total > 0:
            self.progress_bar.setMaximum(total)
            self.progress_bar.setValue(current)
        self.progress_label.setText(f"{current} / {total}")
    
    def set_status(self, message: str):
        """Update status label."""
        self.status_label.setText(message[:40])
    
    def append_log(self, message: str):
        """Append message to log."""
        self.log_output.append(message)
    
    def clear_logs(self):
        """Clear log output."""
        self.log_output.clear()
    
    def show_error(self, error_message: str):
        """Show error message."""
        self.error_label.setText(f"Error: {error_message}")
        self.error_label.setVisible(True)
    
    def hide_error(self):
        """Hide error message."""
        self.error_label.setVisible(False)
    
    def reset(self):
        """Reset progress panel to initial state."""
        self.progress_bar.setValue(0)
        self.progress_label.setText("Ready")
        self.status_label.setText("")
        self.clear_logs()
        self.hide_error()
