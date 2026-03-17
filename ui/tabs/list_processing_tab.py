"""
ui/tabs/list_processing_tab.py - List processing tab for batch mod processing
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout, QCheckBox, 
    QPushButton, QLabel, QMessageBox, QApplication
)
from PySide6.QtCore import Slot

from config.settings import get_settings
from ui.tabs.base_tab import BaseTab
from ui.components import ProgressLogPanel, FileBrowserWidget
from ui.modern_theme import ModernUIHelper
from ui.worker import ModProcessorWorker, WorkerThread


logger = logging.getLogger(__name__)


class ListProcessingTab(BaseTab):
    """Tab for processing a list of mods from a text file."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = get_settings()
        
        self.worker = None
        self.worker_thread = None
        self.mod_filenames = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI for list processing tab."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # FILE SELECTION SECTION
        file_group = QGroupBox("Mod List File")
        file_group.setMaximumHeight(100)
        file_layout = QHBoxLayout(file_group)
        
        self.file_browser = FileBrowserWidget()
        self.file_browser.path_changed.connect(self._on_file_changed)
        file_layout.addWidget(self.file_browser)
        main_layout.addWidget(file_group)
        
        # OPTIONS SECTION
        options_group = QGroupBox("Processing Options")
        options_layout = QGridLayout(options_group)
        options_layout.setSpacing(10)
        
        self.opt_download_zips = QCheckBox("Download mod ZIP files")
        self.opt_download_zips.setChecked(self.settings.download_zips)
        
        self.opt_save_images = QCheckBox("Save mod thumbnail images")
        self.opt_save_images.setChecked(self.settings.save_images)
        
        self.opt_save_releases = QCheckBox("Save releases as CSV")
        self.opt_save_releases.setChecked(self.settings.save_releases)
        
        self.opt_save_changelog = QCheckBox("Include changelog in CSV")
        self.opt_save_changelog.setChecked(self.settings.save_changelog)
        
        self.opt_multithreading = QCheckBox("Enable multithreading (faster)")
        self.opt_multithreading.setChecked(False)
        
        options_layout.addWidget(self.opt_download_zips, 0, 0)
        options_layout.addWidget(self.opt_save_images, 0, 1)
        options_layout.addWidget(self.opt_save_releases, 1, 0)
        options_layout.addWidget(self.opt_save_changelog, 1, 1)
        options_layout.addWidget(self.opt_multithreading, 2, 0)
        options_layout.setColumnStretch(0, 1)
        options_layout.setColumnStretch(1, 1)
        
        main_layout.addWidget(options_group)
        
        # PROGRESS & LOG SECTION
        self.progress_panel = ProgressLogPanel()
        main_layout.addWidget(self.progress_panel, 1)
        
        # BUTTON BAR
        button_frame = self._create_button_bar()
        main_layout.addWidget(button_frame)
    
    def _create_button_bar(self):
        """Create button bar with start, stop, and utility buttons."""
        from PySide6.QtWidgets import QFrame, QHBoxLayout
        import os
        
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Start/Stop buttons
        self.start_btn = QPushButton("▶ Start Processing")
        self.start_btn.setMinimumHeight(36)
        self.start_btn.setMinimumWidth(140)
        self.start_btn.clicked.connect(self._on_start)
        ModernUIHelper.apply_button_style(self.start_btn, 'success')
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setMinimumHeight(36)
        self.stop_btn.setMaximumWidth(80)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        ModernUIHelper.apply_button_style(self.stop_btn, 'danger')
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        
        # Utility buttons
        self.open_csv_btn = QPushButton("📊 CSV")
        self.open_csv_btn.setMinimumHeight(36)
        self.open_csv_btn.setMaximumWidth(80)
        self.open_csv_btn.clicked.connect(self._on_open_csv)
        ModernUIHelper.apply_button_style(self.open_csv_btn, 'secondary')
        
        self.open_folder_btn = QPushButton("📁 Folder")
        self.open_folder_btn.setMinimumHeight(36)
        self.open_folder_btn.setMaximumWidth(100)
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        ModernUIHelper.apply_button_style(self.open_folder_btn, 'secondary')
        
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setMinimumHeight(36)
        self.settings_btn.setMaximumWidth(50)
        self.settings_btn.clicked.connect(self._on_settings)
        ModernUIHelper.apply_button_style(self.settings_btn, 'secondary')
        
        button_layout.addWidget(self.open_csv_btn)
        button_layout.addWidget(self.open_folder_btn)
        button_layout.addWidget(self.settings_btn)
        
        return button_frame
    
    @Slot(str)
    def _on_file_changed(self, path: str):
        """Handle file path changed."""
        logger.info(f"Selected file: {path}")
    
    @Slot()
    def _on_start(self):
        """Start processing mods from the list file."""
        file_path = self.file_browser.get_path()
        
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, "Error", "Please select a valid mod list file")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.mod_filenames = [
                    line.strip() for line in f 
                    if line.strip() and not line.startswith('#')
                ]
            
            if not self.mod_filenames:
                QMessageBox.warning(self, "Error", "Mod list file is empty")
                return
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Could not read file: {e}")
            return
        
        # Update UI
        self.on_start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.file_browser.browse_btn.setEnabled(False)
        
        self.progress_panel.hide_error()
        self.progress_panel.set_status("Processing...")
        self.progress_panel.set_progress(0, len(self.mod_filenames))
        
        # Create and start worker
        self.worker = ModProcessorWorker(self.settings)
        self.worker_thread = WorkerThread(self.worker, self.settings)
        
        # Connect signals
        self.worker.progress_updated.connect(self.progress_updated.emit)
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.status_updated.connect(self.status_updated.emit)
        self.worker.status_updated.connect(self._on_status)
        self.worker.log_message.connect(self.log_message.emit)
        self.worker.log_message.connect(self._on_log)
        self.worker.finished.connect(self.finished.emit)
        self.worker.finished.connect(self._on_finished)
        self.worker.error_occurred.connect(self.error_occurred.emit)
        self.worker.error_occurred.connect(self._on_error)
        
        use_multithreading = self.opt_multithreading.isChecked()
        self.worker_thread.set_mod_list(self.mod_filenames, use_multithreading)
        
        logger.info(f"Starting processing of {len(self.mod_filenames)} mods")
        self.worker_thread.start()
    
    @Slot()
    def _on_stop(self):
        """Stop processing."""
        if self.worker:
            self.worker.should_stop = True
            logger.warning("Stop requested")
    
    @Slot(int, int, str)
    def _on_progress(self, current, total, message):
        """Handle progress update."""
        self.progress_panel.set_progress(current, total)
        self.progress_panel.set_status(message)
        logger.info(message)
    
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
        """Handle processing finished."""
        self.on_stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.file_browser.browse_btn.setEnabled(True)
        
        self.progress_panel.progress_label.setText("Complete")
        
        result_msg = (
            f"Processing complete!\n\n"
            f"Total: {summary['total']}\n"
            f"Processed: {summary['processed']}\n"
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
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.file_browser.browse_btn.setEnabled(True)
        
        self.progress_panel.show_error(error_message)
        logger.error(error_message)
        QMessageBox.critical(self, "Error", error_message)
    
    @Slot()
    def _on_open_csv(self):
        """Open CSV file."""
        import os
        
        csv_path = self.settings.csv_file
        if Path(csv_path).exists():
            if os.name == 'nt':
                os.startfile(csv_path)
            else:
                os.system(f'xdg-open "{csv_path}"')
        else:
            QMessageBox.information(self, "Not Found", "CSV file not found")
    
    @Slot()
    def _on_open_folder(self):
        """Open output folder."""
        import os
        
        folder = Path.cwd()
        if folder.exists():
            if os.name == 'nt':
                os.startfile(folder)
            else:
                os.system(f'xdg-open "{folder}"')
    
    @Slot()
    def _on_settings(self):
        """Open settings dialog."""
        from ui.settings_dialog import SettingsDialog
        
        try:
            dialog = SettingsDialog(self)
            dialog.exec()
        except Exception as e:
            logger.warning(f"Could not open settings: {e}")
            QMessageBox.warning(self, "Settings", "Settings dialog not available")
    
    def cleanup(self):
        """Cleanup when tab is closed."""
        if self.worker:
            self.worker.should_stop = True
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.wait(2000)
