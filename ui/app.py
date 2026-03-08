"""
ui/app.py - Main GUI application using PySide6
"""

import logging
import os
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QCheckBox,
    QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QScrollArea
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QColor
from PySide6.QtGui import QCloseEvent

from config.settings import get_settings
from ui.worker import ModProcessorWorker, WorkerThread
from ui.settings_dialog import SettingsDialog


logger = logging.getLogger(__name__)


class FactorioModManagerApp(QMainWindow):
    """
    Main GUI application for Factorio Mod Manager.
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.settings = get_settings()
        
        self.worker = None
        self.worker_thread = None
        self.mod_filenames = []
        
        self.setWindowTitle("Factorio Mod Manager")
        self.setGeometry(100, 100, 900, 750)
        
        self._setup_ui()
        self._setup_logging()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # File selection
        file_layout = QHBoxLayout()
        file_label = QLabel("Mod List File (.txt):")
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_browse_btn = QPushButton("Browse...")
        self.file_browse_btn.clicked.connect(self._on_browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(self.file_browse_btn)
        layout.addLayout(file_layout)
        
        # Options group
        options_group = QGroupBox("Options")
        options_layout = QGridLayout()
        
        self.opt_download_zips = QCheckBox("Download mod ZIP files")
        self.opt_download_zips.setChecked(self.settings.download_zips)
        
        self.opt_save_images = QCheckBox("Save mod images")
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
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress section
        progress_label = QLabel("Progress:")
        progress_font = QFont()
        progress_font.setBold(True)
        progress_label.setFont(progress_font)
        layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Idle")
        layout.addWidget(self.progress_label)
        
        # Operation status (what is currently happening)
        self.status_label = QLabel("Ready")
        status_font = QFont()
        status_font.setItalic(True)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        # Error display (shows errors in real-time)
        self.error_label = QLabel("")
        error_font = QFont()
        error_font.setBold(True)
        self.error_label.setFont(error_font)
        self.error_label.setStyleSheet("color: red; background-color: #ffe0e0; padding: 8px; border-radius: 4px;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        # Log output
        log_label = QLabel("Log Output:")
        log_label.setFont(progress_font)
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(300)
        layout.addWidget(self.log_output)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start")
        self.start_btn.setMinimumWidth(100)
        self.start_btn.clicked.connect(self._on_start)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        
        self.open_csv_btn = QPushButton("Open CSV File")
        self.open_csv_btn.clicked.connect(self._on_open_csv)
        
        self.open_folder_btn = QPushButton("Open Output Folder")
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.clicked.connect(self._on_settings)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.open_csv_btn)
        button_layout.addWidget(self.open_folder_btn)
        button_layout.addWidget(self.settings_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def _setup_logging(self):
        """Setup logging to output to GUI."""
        # Create a handler that emits to the GUI
        class GUILogHandler(logging.Handler):
            def __init__(self, log_signal):
                super().__init__()
                self.log_signal = log_signal
            
            def emit(self, record):
                try:
                    msg = self.format(record)
                    self.log_signal.emit(msg)
                except Exception:
                    pass
        
        # This would require a signal - skip for now
        # Instead, just use file logging which is already setup
    
    @Slot()
    def _on_browse_file(self):
        """Handle browse button click."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Mod List File",
            "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.file_input.setText(file_path)
            logger.info(f"Selected file: {file_path}")
    
    @Slot()
    def _on_start(self):
        """Handle start button click."""
        file_path = self.file_input.text().strip()
        
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(
                self,
                "Error",
                "Please select a valid mod list file"
            )
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.mod_filenames = [
                    line.strip() 
                    for line in f 
                    if line.strip() and not line.startswith('#')
                ]
            
            if not self.mod_filenames:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Mod list file is empty or contains only comments"
                )
                return
        
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Could not read file: {e}")
            return
        
        # Setup UI for processing
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.file_browse_btn.setEnabled(False)
        
        # Clear previous error messages
        self.error_label.setVisible(False)
        self.error_label.setText("")
        self.status_label.setText("Ready")
        
        self.progress_bar.setMaximum(len(self.mod_filenames))
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"Processing 0/{len(self.mod_filenames)}")
        
        # Create worker and thread
        self.worker = ModProcessorWorker(self.settings)
        self.worker_thread = WorkerThread(self.worker, self.settings)
        
        # Connect signals
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.status_updated.connect(self._on_status)
        self.worker.log_message.connect(self._on_log)
        self.worker.finished.connect(self._on_finished)
        self.worker.error_occurred.connect(self._on_error)
        
        # Set mod list and start
        use_multithreading = self.opt_multithreading.isChecked()
        self.worker_thread.set_mod_list(self.mod_filenames, use_multithreading)
        
        logger.info(f"Starting processing of {len(self.mod_filenames)} mods")
        self.worker_thread.start()
    
    @Slot()
    def _on_stop(self):
        """Handle stop button click."""
        if self.worker:
            self.worker.should_stop = True
            logger.warning("Stop requested by user")
    
    @Slot(int, int, str)
    def _on_progress(self, current, total, message):
        """Handle progress update signal."""
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"Processing {current}/{total}")
        self.status_label.setText(f"Current: {message}")
        logger.info(message)
    
    @Slot(str)
    def _on_log(self, message):
        """Handle log message signal."""
        self.log_output.append(message)
    
    @Slot(str)
    def _on_status(self, message):
        """Handle status update signal."""
        self.status_label.setText(f"Current: {message}")
    
    @Slot(dict)
    def _on_finished(self, summary):
        """Handle processing finished signal."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.file_browse_btn.setEnabled(True)
        
        self.progress_label.setText("Processing complete")
        
        result_msg = (
            f"Processing complete!\n\n"
            f"Total: {summary['total']}\n"
            f"Processed: {summary['processed']}\n"
            f"Failed: {summary['failed']}\n"
            f"CSV: {summary['csv_file']}"
        )
        
        logger.info(result_msg.replace('\n', ' | '))
        
        if summary['failed'] > 0:
            QMessageBox.warning(
                self,
                "Processing Complete",
                result_msg
            )
        else:
            QMessageBox.information(
                self,
                "Processing Complete",
                result_msg
            )
    
    @Slot(str)
    def _on_error(self, error_message):
        """Handle error signal."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.file_browse_btn.setEnabled(True)
        
        # Display error in UI with red text
        self.error_label.setText(f"❌ ERROR: {error_message}")
        self.error_label.setVisible(True)
        
        logger.error(f"Error: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred:\n\n{error_message}")
    
    @Slot()
    def _on_open_csv(self):
        """Open the CSV file."""
        csv_path = self.settings.csv_file
        
        if Path(csv_path).exists():
            if os.name == 'nt':  # Windows
                os.startfile(csv_path)
            else:  # Linux/Mac
                os.system(f'xdg-open "{csv_path}"')
            logger.info(f"Opened: {csv_path}")
        else:
            QMessageBox.information(
                self,
                "File Not Found",
                f"CSV file not found: {csv_path}\n\nProcess some mods first."
            )
    
    @Slot()
    def _on_open_folder(self):
        """Open the output folder."""
        folder = Path.cwd()
        
        if folder.exists():
            if os.name == 'nt':  # Windows
                os.startfile(folder)
            else:  # Linux/Mac
                os.system(f'xdg-open "{folder}"')
            logger.info(f"Opened: {folder}")
    
    @Slot()
    def _on_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
        logger.info("Settings dialog closed")
    
    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event.
        Properly cleanup worker thread before closing.
        """
        logger.info("Window close event triggered")
        
        try:
            # Stop worker if running
            if self.worker:
                logger.info("Stopping worker thread...")
                self.worker.should_stop = True
            
            # Wait for worker thread to finish
            if self.worker_thread and self.worker_thread.isRunning():
                logger.info("Waiting for worker thread to finish...")
                # Give it 5 seconds to finish gracefully
                if not self.worker_thread.wait(5000):
                    logger.warning("Worker thread did not finish in time, terminating...")
                    self.worker_thread.terminate()
                    # Wait for termination
                    if not self.worker_thread.wait(2000):
                        logger.error("Worker thread could not be terminated!")
                logger.info("Worker thread stopped")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        # Accept the close event
        event.accept()
        logger.info("Window closed successfully")
