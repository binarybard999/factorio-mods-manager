"""
ui/tabs/folder_updates_tab.py - Folder update tab for checking and updating mods in a directory
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout, QCheckBox, 
    QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Slot

from config.settings import get_settings
from ui.tabs.base_tab import BaseTab
from ui.components import ProgressLogPanel, FolderBrowserWidget
from ui.modern_theme import ModernUIHelper
from ui.worker import UpdateWorkerThread


logger = logging.getLogger(__name__)


class FolderUpdateTab(BaseTab):
    """Tab for checking and updating mods in a folder."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        
        self.update_worker_thread = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for folder update tab."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # FOLDER SELECTION SECTION
        folder_group = QGroupBox("Mods Folder")
        folder_group.setMaximumHeight(100)
        folder_layout = QHBoxLayout(folder_group)
        
        self.folder_browser = FolderBrowserWidget()
        self.folder_browser.path_changed.connect(self._on_folder_changed)
        folder_layout.addWidget(self.folder_browser)
        main_layout.addWidget(folder_group)
        
        # OPTIONS SECTION
        update_group = QGroupBox("Update Options")
        update_layout = QGridLayout(update_group)
        update_layout.setSpacing(10)
        
        self.opt_backup_old = QCheckBox("Backup old mods to 'old_mods' subfolder")
        self.opt_backup_old.setChecked(True)
        
        self.opt_auto_download = QCheckBox("Auto-download latest versions")
        self.opt_auto_download.setChecked(True)
        
        update_layout.addWidget(self.opt_backup_old, 0, 0)
        update_layout.addWidget(self.opt_auto_download, 0, 1)
        
        main_layout.addWidget(update_group)
        
        # INFO SECTION
        info_frame = self._create_info_section()
        main_layout.addWidget(info_frame)
        
        # PROGRESS & LOG SECTION
        self.progress_panel = ProgressLogPanel()
        main_layout.addWidget(self.progress_panel, 1)
        
        # BUTTON BAR
        button_frame = self._create_button_bar()
        main_layout.addWidget(button_frame)
    
    def _create_info_section(self):
        """Create information section."""
        from PySide6.QtWidgets import QFrame, QVBoxLayout
        
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        info_text = QLabel(
            "Scan your mods folder for updates.\n"
            "Old versions will be backed up, new versions downloaded automatically.\n"
            "Supports: modname_1.0.0.zip, modname.zip, modname"
        )
        info_text.setObjectName("subtitleLabel")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        return info_frame
    
    def _create_button_bar(self):
        """Create button bar with start, stop, and utility buttons."""
        from PySide6.QtWidgets import QFrame, QHBoxLayout
        
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Start/Stop buttons
        self.folder_start_btn = QPushButton("✅ Check Updates")
        self.folder_start_btn.setMinimumHeight(36)
        self.folder_start_btn.setMinimumWidth(140)
        self.folder_start_btn.clicked.connect(self._on_start)
        ModernUIHelper.apply_button_style(self.folder_start_btn, 'success')
        
        self.folder_stop_btn = QPushButton("⏹ Stop")
        self.folder_stop_btn.setMinimumHeight(36)
        self.folder_stop_btn.setMaximumWidth(80)
        self.folder_stop_btn.setEnabled(False)
        self.folder_stop_btn.clicked.connect(self._on_stop)
        ModernUIHelper.apply_button_style(self.folder_stop_btn, 'danger')
        
        button_layout.addWidget(self.folder_start_btn)
        button_layout.addWidget(self.folder_stop_btn)
        button_layout.addStretch()
        
        # Utility buttons
        self.folder_open_btn = QPushButton("📁 Open")
        self.folder_open_btn.setMinimumHeight(36)
        self.folder_open_btn.setMaximumWidth(80)
        self.folder_open_btn.clicked.connect(self._on_open_folder)
        ModernUIHelper.apply_button_style(self.folder_open_btn, 'secondary')
        
        button_layout.addWidget(self.folder_open_btn)
        
        return button_frame
    
    @Slot(str)
    def _on_folder_changed(self, path: str):
        """Handle folder path changed."""
        logger.info(f"Selected folder: {path}")
    
    @Slot()
    def _on_start(self):
        """Start checking for updates."""
        folder_path = self.folder_browser.get_path()
        
        if not folder_path or not Path(folder_path).exists():
            QMessageBox.warning(self, "Error", "Please select a valid mods folder")
            return
        
        # Update UI
        self.on_start()
        self.folder_start_btn.setEnabled(False)
        self.folder_stop_btn.setEnabled(True)
        self.folder_browser.browse_btn.setEnabled(False)
        
        self.progress_panel.hide_error()
        self.progress_panel.set_status("Scanning...")
        self.progress_panel.reset()
        
        logger.info(f"Starting folder update: {folder_path}")
        
        self.update_worker_thread = UpdateWorkerThread(folder_path, self.settings)
        
        # Connect signals
        self.update_worker_thread.progress_updated.connect(self.progress_updated.emit)
        self.update_worker_thread.progress_updated.connect(self._on_progress)
        self.update_worker_thread.status_updated.connect(self.status_updated.emit)
        self.update_worker_thread.status_updated.connect(self._on_status)
        self.update_worker_thread.log_message.connect(self.log_message.emit)
        self.update_worker_thread.log_message.connect(self._on_log)
        self.update_worker_thread.finished.connect(self.finished.emit)
        self.update_worker_thread.finished.connect(self._on_finished)
        self.update_worker_thread.error_occurred.connect(self.error_occurred.emit)
        self.update_worker_thread.error_occurred.connect(self._on_error)
        
        self.update_worker_thread.start()
    
    @Slot()
    def _on_stop(self):
        """Stop folder update."""
        if self.update_worker_thread:
            self.update_worker_thread.should_stop = True
            logger.warning("Folder update stopped")
    
    @Slot(int, int, str)
    def _on_progress(self, current, total, message):
        """Handle progress update."""
        if total > 0:
            self.progress_panel.progress_bar.setMaximum(100)
            self.progress_panel.progress_bar.setValue(int((current / total) * 100))
            self.progress_panel.progress_label.setText(f"{current} / {total}")
        self.progress_panel.set_status(message)
    
    @Slot(str)
    def _on_status(self, message):
        """Handle status update."""
        self.progress_panel.set_status(message)
    
    @Slot(str)
    def _on_log(self, message):
        """Handle log message."""
        self.progress_panel.append_log(message)
    
    @Slot(dict)
    def _on_finished(self, summary):
        """Handle folder update finished."""
        self.on_stop()
        self.folder_start_btn.setEnabled(True)
        self.folder_stop_btn.setEnabled(False)
        self.folder_browser.browse_btn.setEnabled(True)
        
        self.progress_panel.progress_label.setText("Complete")
        
        result_msg = (
            f"Update check complete!\n\n"
            f"Total: {summary['total']}\n"
            f"Up-to-date: {summary['up_to_date']}\n"
            f"Updated: {summary['updated']}\n"
            f"Failed: {summary['failed']}"
        )
        
        if summary['failed'] > 0:
            QMessageBox.warning(self, "Complete", result_msg)
        else:
            QMessageBox.information(self, "Complete", result_msg)
    
    @Slot(str)
    def _on_error(self, error_message):
        """Handle error."""
        self.on_stop()
        self.folder_start_btn.setEnabled(True)
        self.folder_stop_btn.setEnabled(False)
        self.folder_browser.browse_btn.setEnabled(True)
        
        self.progress_panel.show_error(error_message)
        logger.error(error_message)
        QMessageBox.critical(self, "Error", error_message)
    
    @Slot()
    def _on_open_folder(self):
        """Open the mods folder."""
        import os
        
        folder_path = self.folder_browser.get_path()
        if folder_path and Path(folder_path).exists():
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                os.system(f'xdg-open "{folder_path}"')
        else:
            QMessageBox.warning(self, "Error", "Please select a valid folder")
    
    def cleanup(self):
        """Cleanup when tab is closed."""
        if self.update_worker_thread and self.update_worker_thread.isRunning():
            self.update_worker_thread.should_stop = True
            self.update_worker_thread.wait(2000)
