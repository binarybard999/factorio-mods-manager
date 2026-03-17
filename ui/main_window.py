"""
ui/main_window.py - Main application window (refactored from app.py)
Simplified to coordinate tabs and delegate functionality
"""

import logging

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QTabWidget, QFrame, QApplication
)
from PySide6.QtCore import Qt

from config.settings import get_settings
from ui.controllers.theme_controller import ThemeController
from ui.tabs.list_processing_tab import ListProcessingTab
from ui.tabs.folder_updates_tab import FolderUpdateTab
from ui.modern_theme import ModernUIHelper

# Import version from main
try:
    from main import VERSION, VERSION_NAME
except ImportError:
    VERSION = "2.0.0"
    VERSION_NAME = "Modern UI Release"


logger = logging.getLogger(__name__)


class FactorioModManagerApp(QMainWindow):
    """Main application window - orchestrates tabs and theme management."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        self.theme_controller = ThemeController()
        
        # Load theme
        self.theme_controller.load_preference()
        self.theme_controller.apply_theme(self.theme_controller.current_theme)
        
        # Setup window
        self.setWindowTitle(f"Factorio Mod Manager v{VERSION} - {VERSION_NAME}")
        self.setGeometry(100, 100, 1300, 950)
        self.setMinimumSize(1100, 800)
        
        self._setup_ui()
        self._apply_modern_style()
        
        self.setAcceptDrops(True)
    
    def _setup_ui(self):
        """Setup main window UI with tabs."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # HEADER BAR
        header = self._create_header()
        main_layout.addWidget(header)
        
        # TABS
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(0, 0, 0, 0)
        
        # List Processing Tab
        self.list_tab = ListProcessingTab()
        self.tabs.addTab(self.list_tab, "📋 Process Mod List")
        
        # Folder Updates Tab
        self.folder_tab = FolderUpdateTab()
        self.tabs.addTab(self.folder_tab, "📁 Update Mods Folder")
        
        main_layout.addWidget(self.tabs, 1)
    
    def _create_header(self):
        """Create header bar with title and theme selector."""
        header = QFrame()
        layout = QHBoxLayout(header)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 12, 20, 12)
        
        # Title
        title = QLabel("Factorio Mod Manager")
        title.setFont(ModernUIHelper.create_title_font())
        layout.addWidget(title)
        layout.addStretch()
        
        # Theme selector
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.theme_controller.get_theme_modes())
        self.theme_combo.setCurrentIndex(
            self.theme_controller.get_theme_index(self.theme_controller.current_theme)
        )
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.theme_combo.setMaximumWidth(120)
        layout.addWidget(self.theme_combo)
        
        return header
    
    def _apply_modern_style(self):
        """Apply modern stylesheet to application."""
        stylesheet = self.theme_controller.get_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def _on_theme_changed(self, index):
        """Handle theme change."""
        theme = self.theme_controller.get_theme_from_index(index)
        self.theme_controller.apply_theme(theme)
        self.theme_controller.save_preference(theme)
        self._apply_modern_style()
    
    def closeEvent(self, event):
        """Handle window close - cleanup tabs."""
        logger.info("Closing application")
        try:
            self.list_tab.cleanup()
            self.folder_tab.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        event.accept()
