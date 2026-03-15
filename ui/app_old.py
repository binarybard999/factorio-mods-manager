"""
ui/app.py - Modern GUI application for Factorio Mod Manager
Uses professional dark mode support, modern styling, and glassmorphism effects
"""

import logging
import os
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QCheckBox,
    QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QComboBox, QTabWidget,
    QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QColor, QDragEnterEvent, QDropEvent, QCloseEvent

from config.settings import get_settings
from ui.worker import ModProcessorWorker, WorkerThread, UpdateWorkerThread
from ui.settings_dialog import SettingsDialog
from ui.theme import ThemeMode, ThemeManager
from ui.modern_theme import ModernUIHelper, get_modern_stylesheet, ModernColors


logger = logging.getLogger(__name__)


class DragDropLineEdit(QLineEdit):
    """QLineEdit with drag-drop support for files/folders."""
    
    def __init__(self, accept_type='file', parent=None):
        super().__init__(parent)
        self.accept_type = accept_type
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if self.accept_type == 'file':
                if path.endswith('.txt'):
                    self.setText(path)
                    logger.info(f"Dropped file: {path}")
                else:
                    QMessageBox.warning(None, "Invalid File", "Please drop a .txt file")
            elif self.accept_type == 'folder':
                if Path(path).is_dir():
                    self.setText(path)
                    logger.info(f"Dropped folder: {path}")
                else:
                    parent = Path(path).parent
                    self.setText(str(parent))
                    logger.info(f"Dropped file, using parent folder: {parent}")


class FactorioModManagerApp(QMainWindow):
    """Main application window with modern UI design."""
    
    def __init__(self):
        super().__init__()
        self.settings = get_settings()
        
        self.worker = None
        self.worker_thread = None
        self.update_worker_thread = None
        self.mod_filenames = []
        self.is_dark_mode = False
        
        # Load theme preference
        self.load_theme_preference()
        
        self.setWindowTitle("Factorio Mod Manager")
        self.setGeometry(100, 100, 1200, 950)
        self.setMinimumSize(1000, 800)
        
        self._setup_ui()
        
        # Apply modern stylesheet
        self._apply_modern_style()
        
        self.setAcceptDrops(True)
    
    def load_theme_preference(self):
        """Load and apply saved theme preference."""
        try:
            config_dir = Path(__file__).parent.parent / 'config'
            theme_file = config_dir / 'theme_settings.json'
            
            if theme_file.exists():
                with open(theme_file, 'r') as f:
                    data = json.load(f)
                    theme_str = data.get('theme', 'system').lower()
                    try:
                        theme = ThemeMode[theme_str.upper()]
                    except KeyError:
                        theme = ThemeMode.SYSTEM
            else:
                theme = ThemeMode.SYSTEM
            
            # Apply the theme
            if theme == ThemeMode.SYSTEM:
                if ThemeManager.is_system_dark_mode():
                    actual_theme = ThemeMode.DARK
                    self.is_dark_mode = True
                else:
                    actual_theme = ThemeMode.LIGHT
                    self.is_dark_mode = False
                ThemeManager.apply_theme(actual_theme)
            else:
                self.is_dark_mode = (theme == ThemeMode.DARK)
                ThemeManager.apply_theme(theme)
            
            self.current_theme = theme
        except Exception as e:
            logger.warning(f"Could not load theme preference: {e}")
            self.current_theme = ThemeMode.SYSTEM
            self.is_dark_mode = False
    
    def save_theme_preference(self, theme: ThemeMode):
        """Save theme preference to file."""
        try:
            config_dir = Path(__file__).parent.parent / 'config'
            config_dir.mkdir(exist_ok=True)
            theme_file = config_dir / 'theme_settings.json'
            
            with open(theme_file, 'w') as f:
                json.dump({'theme': theme.value}, f)
            
            self.current_theme = theme
            logger.info(f"Saved theme preference: {theme.value}")
        except Exception as e:
            logger.error(f"Could not save theme preference: {e}")
    
    def _apply_modern_style(self):
        """Apply modern stylesheet to the entire application."""
        stylesheet = get_modern_stylesheet(self.is_dark_mode)
        self.setStyleSheet(stylesheet)
    
    def _setup_ui(self):
        """Setup the user interface with modern layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Header section with theme selector
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # App title
        title_label = QLabel("Factorio Mod Manager")
        title_font = ModernUIHelper.create_title_font()
        title_label.setFont(title_font)
        title_label.setObjectName("titleLabel")
        
        # Tagline
        tagline = QLabel("Professional mod management and updates")
        tagline_font = ModernUIHelper.create_modern_font(11, italic=True)
        tagline.setFont(tagline_font)
        tagline.setObjectName("subtitleLabel")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(tagline)
        header_layout.addStretch()
        
        # Theme selector
        theme_label = QLabel("Theme:")
        theme_label.setFont(ModernUIHelper.create_modern_font(12, bold=True))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["☀️  Light", "🌙 Dark", "🖥️  System Default"])
        theme_index = {'light': 0, 'dark': 1, 'system': 2}.get(self.current_theme.value, 2)
        self.theme_combo.setCurrentIndex(theme_index)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.theme_combo.setMinimumWidth(180)
        
        header_layout.addWidget(theme_label)
        header_layout.addWidget(self.theme_combo)
        
        main_layout.addLayout(header_layout)
        
        # Create tabs for different modes
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(False)
        
        # Tab 1: List Processing
        self.list_tab_widget = self._create_list_processing_tab()
        self.tabs.addTab(self.list_tab_widget, "📋 Process Mod List")
        
        # Tab 2: Folder Updates
        self.folder_tab_widget = self._create_folder_updates_tab()
        self.tabs.addTab(self.folder_tab_widget, "📁 Update Mods Folder")
        
        main_layout.addWidget(self.tabs)
    
    def _create_list_processing_tab(self):
        """Create the list processing tab with modern design."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # File selection section
        file_section = QGroupBox("Select Mod List File")
        file_layout = QHBoxLayout()
        file_layout.setSpacing(8)
        
        self.file_input = DragDropLineEdit(accept_type='file')
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Drag & drop mods.txt here...")
        self.file_input.setMinimumHeight(40)
        
        self.file_browse_btn = QPushButton("Browse")
        self.file_browse_btn.setMinimumWidth(100)
        self.file_browse_btn.setMinimumHeight(40)
        self.file_browse_btn.clicked.connect(self._on_browse_file)
        
        file_layout.addWidget(self.file_input, 1)
        file_layout.addWidget(self.file_browse_btn)
        file_section.setLayout(file_layout)
        layout.addWidget(file_section)
        
        # Options section
        options_group = QGroupBox("Processing Options")
        options_layout = QGridLayout()
        options_layout.setSpacing(12)
        
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
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress section
        progress_label = QLabel("Processing Progress")
        progress_font = ModernUIHelper.create_heading_font()
        progress_label.setFont(progress_font)
        layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(28)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to start")
        self.progress_label.setObjectName("statusLabel")
        layout.addWidget(self.progress_label)
        
        self.status_label = QLabel("No processing in progress")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)
        
        # Error display
        self.error_label = QLabel("")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        self.error_label.setMinimumHeight(40)
        self.error_label.setObjectName("errorLabel")
        layout.addWidget(self.error_label)
        
        # Log output
        log_label = QLabel("Processing Log")
        log_label.setFont(progress_font)
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(180)
        layout.addWidget(self.log_output)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.start_btn = QPushButton("▶ Start Processing")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setMinimumWidth(150)
        self.start_btn.clicked.connect(self._on_start)
        ModernUIHelper.apply_button_style(self.start_btn, 'success')
        
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        ModernUIHelper.apply_button_style(self.stop_btn, 'danger')
        
        self.open_csv_btn = QPushButton("📊 CSV File")
        self.open_csv_btn.setMinimumHeight(40)
        self.open_csv_btn.clicked.connect(self._on_open_csv)
        ModernUIHelper.apply_button_style(self.open_csv_btn, 'secondary')
        
        self.open_folder_btn = QPushButton("📁 Output Folder")
        self.open_folder_btn.setMinimumHeight(40)
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        ModernUIHelper.apply_button_style(self.open_folder_btn, 'secondary')
        
        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.setMinimumHeight(40)
        self.settings_btn.clicked.connect(self._on_settings)
        ModernUIHelper.apply_button_style(self.settings_btn, 'secondary')
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.open_csv_btn)
        button_layout.addWidget(self.open_folder_btn)
        button_layout.addWidget(self.settings_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def _create_folder_updates_tab(self):
        """Create the folder updates tab with modern design."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Folder selection section
        folder_section = QGroupBox("Select Mods Folder")
        folder_layout = QHBoxLayout()
        folder_layout.setSpacing(8)
        
        self.mods_folder_input = DragDropLineEdit(accept_type='folder')
        self.mods_folder_input.setReadOnly(True)
        self.mods_folder_input.setPlaceholderText("Drag & drop your mods folder here...")
        self.mods_folder_input.setMinimumHeight(40)
        
        self.folder_browse_btn = QPushButton("Browse")
        self.folder_browse_btn.setMinimumWidth(100)
        self.folder_browse_btn.setMinimumHeight(40)
        self.folder_browse_btn.clicked.connect(self._on_browse_folder)
        
        folder_layout.addWidget(self.mods_folder_input, 1)
        folder_layout.addWidget(self.folder_browse_btn)
        folder_section.setLayout(folder_layout)
        layout.addWidget(folder_section)
        
        # Update options
        update_options_group = QGroupBox("Update Options")
        update_options_layout = QGridLayout()
        update_options_layout.setSpacing(12)
        
        self.opt_backup_old = QCheckBox("Backup old mods to 'old_mods' subfolder")
        self.opt_backup_old.setChecked(True)
        
        self.opt_auto_download = QCheckBox("Auto-download updates")
        self.opt_auto_download.setChecked(True)
        
        update_options_layout.addWidget(self.opt_backup_old, 0, 0)
        update_options_layout.addWidget(self.opt_auto_download, 0, 1)
        
        update_options_group.setLayout(update_options_layout)
        layout.addWidget(update_options_group)
        
        # Info box - with better styling for dark mode
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel("How It Works")
        info_title.setFont(ModernUIHelper.create_heading_font())
        info_layout.addWidget(info_title)
        
        info_text = QLabel(
            "1. Select your Factorio mods folder\n"
            "2. Choose your update preferences\n"
            "3. Click 'Check Updates' to scan\n"
            "4. Old versions are backed up automatically\n"
            "5. New versions are downloaded\n\n"
            "Supports: aai-vehicles-hauler_0.7.3.zip, bobplates.zip, Krastorio2"
        )
        info_text.setObjectName("subtitleLabel")
        info_text.setWordWrap(True)
        info_layout.addWidget(info_text)
        
        layout.addWidget(info_frame)
        
        # Progress section
        progress_label = QLabel("Update Progress")
        progress_font = ModernUIHelper.create_heading_font()
        progress_label.setFont(progress_font)
        layout.addWidget(progress_label)
        
        self.folder_progress_bar = QProgressBar()
        self.folder_progress_bar.setRange(0, 100)
        self.folder_progress_bar.setValue(0)
        self.folder_progress_bar.setMinimumHeight(28)
        layout.addWidget(self.folder_progress_bar)
        
        self.folder_progress_label = QLabel("Ready to start")
        self.folder_progress_label.setObjectName("statusLabel")
        layout.addWidget(self.folder_progress_label)
        
        self.folder_status_label = QLabel("No update in progress")
        self.folder_status_label.setObjectName("statusLabel")
        layout.addWidget(self.folder_status_label)
        
        # Error display
        self.folder_error_label = QLabel("")
        self.folder_error_label.setWordWrap(True)
        self.folder_error_label.setVisible(False)
        self.folder_error_label.setMinimumHeight(40)
        self.folder_error_label.setObjectName("errorLabel")
        layout.addWidget(self.folder_error_label)
        
        # Log output
        log_label = QLabel("Update Log")
        log_label.setFont(progress_font)
        layout.addWidget(log_label)
        
        self.folder_log_output = QTextEdit()
        self.folder_log_output.setReadOnly(True)
        self.folder_log_output.setMinimumHeight(180)
        layout.addWidget(self.folder_log_output)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        self.folder_start_btn = QPushButton("✅ Check Updates")
        self.folder_start_btn.setMinimumHeight(40)
        self.folder_start_btn.setMinimumWidth(150)
        self.folder_start_btn.clicked.connect(self._on_start_folder_update)
        ModernUIHelper.apply_button_style(self.folder_start_btn, 'success')
        
        self.folder_stop_btn = QPushButton("⏹ Stop")
        self.folder_stop_btn.setMinimumHeight(40)
        self.folder_stop_btn.setMinimumWidth(100)
        self.folder_stop_btn.setEnabled(False)
        self.folder_stop_btn.clicked.connect(self._on_stop_folder_update)
        ModernUIHelper.apply_button_style(self.folder_stop_btn, 'danger')
        
        self.folder_open_btn = QPushButton("📁 Open Folder")
        self.folder_open_btn.setMinimumHeight(40)
        self.folder_open_btn.clicked.connect(self._on_open_mods_folder)
        ModernUIHelper.apply_button_style(self.folder_open_btn, 'secondary')
        
        button_layout.addWidget(self.folder_start_btn)
        button_layout.addWidget(self.folder_stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.folder_open_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    @Slot()
    def _on_theme_changed(self, index):
        """Handle theme change."""
        themes = [ThemeMode.LIGHT, ThemeMode.DARK, ThemeMode.SYSTEM]
        theme = themes[index]
        
        if theme == ThemeMode.SYSTEM:
            if ThemeManager.is_system_dark_mode():
                actual_theme = ThemeMode.DARK
                self.is_dark_mode = True
            else:
                actual_theme = ThemeMode.LIGHT
                self.is_dark_mode = False
            ThemeManager.apply_theme(actual_theme)
        else:
            self.is_dark_mode = (theme == ThemeMode.DARK)
            ThemeManager.apply_theme(theme)
        
        self._apply_modern_style()
        self.save_theme_preference(theme)
    
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
    def _on_browse_folder(self):
        """Handle browse folder button click."""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Mods Folder",
            ""
        )
        
        if folder_path:
            self.mods_folder_input.setText(folder_path)
            logger.info(f"Selected folder: {folder_path}")
    
    @Slot()
    def _on_start(self):
        """Handle start button click for list processing."""
        file_path = self.file_input.text().strip()
        
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, "Error", "Please select a valid mod list file")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.mod_filenames = [
                    line.strip() 
                    for line in f 
                    if line.strip() and not line.startswith('#')
                ]
            
            if not self.mod_filenames:
                QMessageBox.warning(self, "Error", "Mod list file is empty or contains only comments")
                return
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Could not read file: {e}")
            return
        
        # Setup UI for processing
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.file_browse_btn.setEnabled(False)
        
        self.error_label.setVisible(False)
        self.status_label.setText("Processing mods...")
        
        self.progress_bar.setMaximum(len(self.mod_filenames))
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"0 / {len(self.mod_filenames)} mods")
        
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
    
    @Slot()
    def _on_start_folder_update(self):
        """Handle start folder update button."""
        folder_path = self.mods_folder_input.text().strip()
        
        if not folder_path or not Path(folder_path).exists():
            QMessageBox.warning(self, "Error", "Please select a valid mods folder")
            return
        
        self.folder_start_btn.setEnabled(False)
        self.folder_stop_btn.setEnabled(True)
        self.folder_browse_btn.setEnabled(False)
        
        self.folder_error_label.setVisible(False)
        self.folder_status_label.setText("Scanning folder...")
        
        self.folder_progress_bar.setMaximum(100)
        self.folder_progress_bar.setValue(0)
        self.folder_progress_label.setText("Starting scan...")
        
        logger.info(f"Starting folder update check: {folder_path}")
        self.folder_log_output.clear()
        
        # Create and start update worker thread
        self.update_worker_thread = UpdateWorkerThread(folder_path, self.settings)
        
        # Connect signals
        self.update_worker_thread.progress_updated.connect(self._on_folder_progress)
        self.update_worker_thread.status_updated.connect(self._on_folder_status)
        self.update_worker_thread.log_message.connect(self._on_folder_log)
        self.update_worker_thread.finished.connect(self._on_folder_finished)
        self.update_worker_thread.error_occurred.connect(self._on_folder_error)
        
        self.update_worker_thread.start()
    
    @Slot()
    def _on_stop_folder_update(self):
        """Handle stop folder update button."""
        if self.update_worker_thread:
            self.update_worker_thread.should_stop = True
            logger.warning("Folder update stopped by user")
    
    @Slot(int, int, str)
    def _on_progress(self, current, total, message):
        """Handle progress update signal."""
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"{current} / {total} mods")
        self.status_label.setText(f"Processing: {message}")
        logger.info(message)
    
    @Slot(str)
    def _on_log(self, message):
        """Handle log message signal."""
        self.log_output.append(message)
    
    @Slot(str)
    def _on_status(self, message):
        """Handle status update signal."""
        self.status_label.setText(f"Processing: {message}")
    
    @Slot(dict)
    def _on_finished(self, summary):
        """Handle processing finished signal."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.file_browse_btn.setEnabled(True)
        
        self.progress_label.setText("Complete")
        self.status_label.setText("Processing finished successfully")
        
        result_msg = (
            f"Processing complete!\n\n"
            f"Total: {summary['total']}\n"
            f"Processed: {summary['processed']}\n"
            f"Failed: {summary['failed']}"
        )
        
        logger.info(result_msg.replace('\n', ' | '))
        
        if summary['failed'] > 0:
            QMessageBox.warning(self, "Processing Complete", result_msg)
        else:
            QMessageBox.information(self, "Processing Complete", result_msg)
    
    @Slot(str)
    def _on_error(self, error_message):
        """Handle error signal."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.file_browse_btn.setEnabled(True)
        
        self.error_label.setText(f"Error: {error_message}")
        self.error_label.setVisible(True)
        
        logger.error(f"Error: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred:\n\n{error_message}")
    
    @Slot(int, int, str)
    def _on_folder_progress(self, current, total, message):
        """Handle folder update progress."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.folder_progress_bar.setValue(percentage)
            self.folder_progress_label.setText(f"{current} / {total} mods")
        self.folder_status_label.setText(f"Processing: {message}")
    
    @Slot(str)
    def _on_folder_log(self, message):
        """Handle folder update log message."""
        self.folder_log_output.append(message)
    
    @Slot(str)
    def _on_folder_status(self, message):
        """Handle folder update status."""
        self.folder_status_label.setText(f"Processing: {message}")
    
    @Slot(dict)
    def _on_folder_finished(self, summary):
        """Handle folder update finished."""
        self.folder_start_btn.setEnabled(True)
        self.folder_stop_btn.setEnabled(False)
        self.folder_browse_btn.setEnabled(True)
        
        self.folder_progress_label.setText("Complete")
        self.folder_status_label.setText("Update check finished successfully")
        
        result_msg = (
            f"Update check complete!\n\n"
            f"Total mods: {summary['total']}\n"
            f"Up-to-date: {summary['up_to_date']}\n"
            f"Updated: {summary['updated']}\n"
            f"Failed: {summary['failed']}"
        )
        
        logger.info(result_msg.replace('\n', ' | '))
        
        if summary['failed'] > 0:
            QMessageBox.warning(self, "Update Check Complete", result_msg)
        else:
            QMessageBox.information(self, "Update Check Complete", result_msg)
    
    @Slot(str)
    def _on_folder_error(self, error_message):
        """Handle folder update error."""
        self.folder_start_btn.setEnabled(True)
        self.folder_stop_btn.setEnabled(False)
        self.folder_browse_btn.setEnabled(True)
        
        self.folder_error_label.setText(f"Error: {error_message}")
        self.folder_error_label.setVisible(True)
        
        logger.error(f"Folder update error: {error_message}")
        QMessageBox.critical(self, "Error", f"An error occurred:\n\n{error_message}")
    
    @Slot()
    def _on_open_csv(self):
        """Open the CSV file."""
        csv_path = self.settings.csv_file
        
        if Path(csv_path).exists():
            if os.name == 'nt':
                os.startfile(csv_path)
            else:
                os.system(f'xdg-open "{csv_path}"')
            logger.info(f"Opened: {csv_path}")
        else:
            QMessageBox.information(self, "File Not Found", f"CSV file not found:\n{csv_path}")
    
    @Slot()
    def _on_open_folder(self):
        """Open the output folder."""
        folder = Path.cwd()
        
        if folder.exists():
            if os.name == 'nt':
                os.startfile(folder)
            else:
                os.system(f'xdg-open "{folder}"')
            logger.info(f"Opened: {folder}")
    
    @Slot()
    def _on_open_mods_folder(self):
        """Open the mods folder."""
        folder_path = self.mods_folder_input.text().strip()
        
        if folder_path and Path(folder_path).exists():
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                os.system(f'xdg-open "{folder_path}"')
            logger.info(f"Opened: {folder_path}")
        else:
            QMessageBox.warning(self, "Invalid Folder", "Please select a valid mods folder first")
    
    @Slot()
    def _on_settings(self):
        """Open the settings dialog."""
        try:
            dialog = SettingsDialog(self)
            dialog.exec()
            logger.info("Settings dialog closed")
        except Exception as e:
            logger.warning(f"Could not open settings dialog: {e}")
            QMessageBox.warning(self, "Settings", "Settings dialog is not available")
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event with proper cleanup."""
        logger.info("Window close event triggered")
        
        try:
            if self.worker:
                self.worker.should_stop = True
            
            if self.worker_thread and self.worker_thread.isRunning():
                if not self.worker_thread.wait(5000):
                    self.worker_thread.terminate()
                    self.worker_thread.wait(2000)
            
            if self.update_worker_thread and self.update_worker_thread.isRunning():
                self.update_worker_thread.should_stop = True
                if not self.update_worker_thread.wait(5000):
                    self.update_worker_thread.terminate()
                    self.update_worker_thread.wait(2000)
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        event.accept()
        logger.info("Window closed successfully")
