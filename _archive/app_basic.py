"""
ui/app.py - Main GUI application using PySide6 with drag-drop and theme support
"""

import logging
import os
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QCheckBox,
    QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QComboBox, QTabWidget
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QColor, QDragEnterEvent, QDropEvent
from PySide6.QtGui import QCloseEvent

from config.settings import get_settings
from ui.worker import ModProcessorWorker, WorkerThread, UpdateWorkerThread
from ui.settings_dialog import SettingsDialog
from ui.theme import ThemeMode, ThemeManager


logger = logging.getLogger(__name__)


class DragDropLineEdit(QLineEdit):
    """QLineEdit that accepts drag-drop for files/folders."""
    
    def __init__(self, accept_type='file', parent=None):
        """
        Initialize drag-drop line edit.
        
        Args:
            accept_type (str): 'file' for files, 'folder' for folders
            parent: Parent widget
        """
        super().__init__(parent)
        self.accept_type = accept_type
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
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
                    logger.info(f"Dropped file: {path}")
                else:
                    QMessageBox.warning(None, "Invalid File", "Please drop a .txt file")
            elif self.accept_type == 'folder':
                if Path(path).is_dir():
                    self.setText(path)
                    logger.info(f"Dropped folder: {path}")
                else:
                    # If it's a file, use its parent directory
                    parent = Path(path).parent
                    self.setText(str(parent))
                    logger.info(f"Dropped file, using parent folder: {parent}")


class FactorioModManagerApp(QMainWindow):
    """
    Main GUI application for Factorio Mod Manager with drag-drop and theme support.
    """
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        self.settings = get_settings()
        
        self.worker = None
        self.worker_thread = None
        self.update_worker_thread = None
        self.mod_filenames = []
        
        # Load theme preference
        self.load_theme_preference()
        
        self.setWindowTitle("Factorio Mod Manager")
        self.setGeometry(100, 100, 1100, 900)
        
        self._setup_ui()
        self._setup_logging()
        
        # Enable drag-drop on the main window
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
                # Detect system theme
                if ThemeManager.is_system_dark_mode():
                    actual_theme = ThemeMode.DARK
                else:
                    actual_theme = ThemeMode.LIGHT
                ThemeManager.apply_theme(actual_theme)
            else:
                ThemeManager.apply_theme(theme)
            
            self.current_theme = theme
        except Exception as e:
            logger.warning(f"Could not load theme preference: {e}")
            self.current_theme = ThemeMode.SYSTEM
    
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
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Central widget with tab support
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Theme selector at top
        theme_layout = QHBoxLayout()
        theme_label = QLabel("🎨 Theme:")
        theme_label.setStyleSheet("font-weight: bold;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["☀️  Light", "🌙 Dark", "🖥️  System Default"])
        theme_index = {'light': 0, 'dark': 1, 'system': 2}.get(self.current_theme.value, 2)
        self.theme_combo.setCurrentIndex(theme_index)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        theme_layout.addWidget(theme_label)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        main_layout.addLayout(theme_layout)
        
        # Create tabs for different modes
        self.tabs = QTabWidget()
        
        # Tab 1: List Processing
        self.list_tab_widget = self._create_list_processing_tab()
        self.tabs.addTab(self.list_tab_widget, "📋 Process Mod List")
        
        # Tab 2: Folder Updates
        self.folder_tab_widget = self._create_folder_updates_tab()
        self.tabs.addTab(self.folder_tab_widget, "📁 Update Mods Folder")
        
        main_layout.addWidget(self.tabs)
    
    def _create_list_processing_tab(self):
        """Create the list processing tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        # File selection with drag-drop
        file_layout = QHBoxLayout()
        file_label = QLabel("📄 Mod List File (.txt):")
        file_label.setStyleSheet("font-weight: bold;")
        self.file_input = DragDropLineEdit(accept_type='file')
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("👉 Drag & drop mods.txt file or click Browse...")
        self.file_input.setMinimumHeight(35)
        
        self.file_browse_btn = QPushButton("📁 Browse...")
        self.file_browse_btn.clicked.connect(self._on_browse_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_input, 1)
        file_layout.addWidget(self.file_browse_btn)
        layout.addLayout(file_layout)
        
        # Options group
        options_group = QGroupBox("⚙️ Processing Options")
        options_layout = QGridLayout()
        
        self.opt_download_zips = QCheckBox("⬇️  Download mod ZIP files")
        self.opt_download_zips.setChecked(self.settings.download_zips)
        
        self.opt_save_images = QCheckBox("📸 Save mod thumbnail images")
        self.opt_save_images.setChecked(self.settings.save_images)
        
        self.opt_save_releases = QCheckBox("📊 Save releases as CSV")
        self.opt_save_releases.setChecked(self.settings.save_releases)
        
        self.opt_save_changelog = QCheckBox("📝 Include changelog in CSV")
        self.opt_save_changelog.setChecked(self.settings.save_changelog)
        
        self.opt_multithreading = QCheckBox("⚡ Enable multithreading (faster)")
        self.opt_multithreading.setChecked(False)
        
        options_layout.addWidget(self.opt_download_zips, 0, 0)
        options_layout.addWidget(self.opt_save_images, 0, 1)
        options_layout.addWidget(self.opt_save_releases, 1, 0)
        options_layout.addWidget(self.opt_save_changelog, 1, 1)
        options_layout.addWidget(self.opt_multithreading, 2, 0)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Progress section
        progress_label = QLabel("📈 Progress:")
        progress_font = QFont()
        progress_font.setBold(True)
        progress_label.setFont(progress_font)
        layout.addWidget(progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("⏸️  Idle")
        layout.addWidget(self.progress_label)
        
        # Operation status
        self.status_label = QLabel("✅ Ready")
        status_font = QFont()
        status_font.setItalic(True)
        self.status_label.setFont(status_font)
        layout.addWidget(self.status_label)
        
        # Error display
        self.error_label = QLabel("")
        error_font = QFont()
        error_font.setBold(True)
        self.error_label.setFont(error_font)
        self.error_label.setStyleSheet("color: red; background-color: #ffe0e0; padding: 8px; border-radius: 4px;")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)
        
        # Log output
        log_label = QLabel("📋 Log Output:")
        log_label.setFont(progress_font)
        layout.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(200)
        layout.addWidget(self.log_output)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶️  Start Processing")
        self.start_btn.setMinimumWidth(120)
        self.start_btn.setMinimumHeight(35)
        self.start_btn.clicked.connect(self._on_start)
        
        self.stop_btn = QPushButton("⏹️  Stop")
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.setMinimumHeight(35)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        
        self.open_csv_btn = QPushButton("📊 Open CSV File")
        self.open_csv_btn.clicked.connect(self._on_open_csv)
        
        self.open_folder_btn = QPushButton("📁 Open Output Folder")
        self.open_folder_btn.clicked.connect(self._on_open_folder)
        
        self.settings_btn = QPushButton("⚙️  Settings")
        self.settings_btn.clicked.connect(self._on_settings)
        
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
        """Create the mods folder update tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        
        # Folder selection with drag-drop
        folder_layout = QHBoxLayout()
        folder_label = QLabel("📁 Mods Folder:")
        folder_label.setStyleSheet("font-weight: bold;")
        self.mods_folder_input = DragDropLineEdit(accept_type='folder')
        self.mods_folder_input.setReadOnly(True)
        self.mods_folder_input.setPlaceholderText("👉 Drag & drop your mods folder or click Browse...")
        self.mods_folder_input.setMinimumHeight(35)
        
        self.folder_browse_btn = QPushButton("📁 Browse...")
        self.folder_browse_btn.clicked.connect(self._on_browse_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.mods_folder_input, 1)
        folder_layout.addWidget(self.folder_browse_btn)
        layout.addLayout(folder_layout)
        
        # Update options
        update_options_group = QGroupBox("⚙️ Update Options")
        update_options_layout = QGridLayout()
        
        self.opt_backup_old = QCheckBox("🔄 Backup old mods to 'old_mods' subfolder")
        self.opt_backup_old.setChecked(True)
        
        self.opt_auto_download = QCheckBox("⬇️  Auto-download updates")
        self.opt_auto_download.setChecked(True)
        
        update_options_layout.addWidget(self.opt_backup_old, 0, 0)
        update_options_layout.addWidget(self.opt_auto_download, 0, 1)
        
        update_options_group.setLayout(update_options_layout)
        layout.addWidget(update_options_group)
        
        # Version info label
        self.version_info_label = QLabel("<b>💡 How it works:</b><br>1. Select your mods folder<br>2. Click 'Check Updates'<br>3. Old versions backed up to 'old_mods' subfolder<br>4. New versions downloaded automatically<br><br>Supported mod formats: modname_1.0.0.zip or modname.zip or just modname")
        self.version_info_label.setWordWrap(True)
        self.version_info_label.setStyleSheet("background-color: #e3f2fd; padding: 10px; border-radius: 4px;")
        layout.addWidget(self.version_info_label)
        
        # Progress section for folder update
        progress_label = QLabel("📈 Progress:")
        progress_font = QFont()
        progress_font.setBold(True)
        progress_label.setFont(progress_font)
        layout.addWidget(progress_label)
        
        self.folder_progress_bar = QProgressBar()
        self.folder_progress_bar.setRange(0, 100)
        self.folder_progress_bar.setValue(0)
        self.folder_progress_bar.setMinimumHeight(25)
        layout.addWidget(self.folder_progress_bar)
        
        self.folder_progress_label = QLabel("⏸️  Idle")
        layout.addWidget(self.folder_progress_label)
        
        # Status and error labels
        self.folder_status_label = QLabel("✅ Ready")
        status_font = QFont()
        status_font.setItalic(True)
        self.folder_status_label.setFont(status_font)
        layout.addWidget(self.folder_status_label)
        
        self.folder_error_label = QLabel("")
        error_font = QFont()
        error_font.setBold(True)
        self.folder_error_label.setFont(error_font)
        self.folder_error_label.setStyleSheet("color: red; background-color: #ffe0e0; padding: 8px; border-radius: 4px;")
        self.folder_error_label.setVisible(False)
        layout.addWidget(self.folder_error_label)
        
        # Log output
        log_label = QLabel("📋 Log Output:")
        log_label.setFont(progress_font)
        layout.addWidget(log_label)
        
        self.folder_log_output = QTextEdit()
        self.folder_log_output.setReadOnly(True)
        self.folder_log_output.setMinimumHeight(200)
        layout.addWidget(self.folder_log_output)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.folder_start_btn = QPushButton("✅ Check Updates")
        self.folder_start_btn.setMinimumWidth(120)
        self.folder_start_btn.setMinimumHeight(35)
        self.folder_start_btn.clicked.connect(self._on_start_folder_update)
        
        self.folder_stop_btn = QPushButton("⏹️  Stop")
        self.folder_stop_btn.setMinimumWidth(120)
        self.folder_stop_btn.setMinimumHeight(35)
        self.folder_stop_btn.setEnabled(False)
        self.folder_stop_btn.clicked.connect(self._on_stop_folder_update)
        
        self.folder_open_btn = QPushButton("📁 Open Mods Folder")
        self.folder_open_btn.clicked.connect(self._on_open_mods_folder)
        
        button_layout.addWidget(self.folder_start_btn)
        button_layout.addWidget(self.folder_stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.folder_open_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def _setup_logging(self):
        """Setup logging to output to GUI."""
        # Logging is already configured globally
        pass
    
    @Slot()
    def _on_theme_changed(self, index):
        """Handle theme change."""
        themes = [ThemeMode.LIGHT, ThemeMode.DARK, ThemeMode.SYSTEM]
        theme = themes[index]
        
        if theme == ThemeMode.SYSTEM:
            if ThemeManager.is_system_dark_mode():
                actual_theme = ThemeMode.DARK
            else:
                actual_theme = ThemeMode.LIGHT
            ThemeManager.apply_theme(actual_theme)
        else:
            ThemeManager.apply_theme(theme)
        
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
        self.status_label.setText("🔄 Processing...")
        
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
    
    @Slot()
    def _on_start_folder_update(self):
        """Handle start folder update button."""
        folder_path = self.mods_folder_input.text().strip()
        
        if not folder_path or not Path(folder_path).exists():
            QMessageBox.warning(
                self,
                "Error",
                "Please select a valid mods folder"
            )
            return
        
        # Setup UI for processing
        self.folder_start_btn.setEnabled(False)
        self.folder_stop_btn.setEnabled(True)
        self.folder_browse_btn.setEnabled(False)
        
        # Clear previous error messages
        self.folder_error_label.setVisible(False)
        self.folder_error_label.setText("")
        self.folder_status_label.setText("🔄 Scanning folder...")
        
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
        
        self.progress_label.setText("✅ Processing complete")
        self.status_label.setText("✅ Ready")
        
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
    
    @Slot(int, int, str)
    def _on_folder_progress(self, current, total, message):
        """Handle folder update progress."""
        if total > 0:
            percentage = int((current / total) * 100)
            self.folder_progress_bar.setValue(percentage)
            self.folder_progress_label.setText(f"Processing {current}/{total}")
        self.folder_status_label.setText(f"Current: {message}")
    
    @Slot(str)
    def _on_folder_log(self, message):
        """Handle folder update log message."""
        self.folder_log_output.append(message)
    
    @Slot(str)
    def _on_folder_status(self, message):
        """Handle folder update status."""
        self.folder_status_label.setText(f"Current: {message}")
    
    @Slot(dict)
    def _on_folder_finished(self, summary):
        """Handle folder update finished."""
        self.folder_start_btn.setEnabled(True)
        self.folder_stop_btn.setEnabled(False)
        self.folder_browse_btn.setEnabled(True)
        
        self.folder_progress_label.setText("✅ Update check complete")
        self.folder_status_label.setText("✅ Ready")
        
        result_msg = (
            f"Update check complete!\n\n"
            f"Total mods: {summary['total']}\n"
            f"Up-to-date: {summary['up_to_date']}\n"
            f"Updated: {summary['updated']}\n"
            f"Failed: {summary['failed']}"
        )
        
        logger.info(result_msg.replace('\n', ' | '))
        
        if summary['failed'] > 0:
            QMessageBox.warning(
                self,
                "Update Check Complete",
                result_msg
            )
        else:
            QMessageBox.information(
                self,
                "Update Check Complete",
                result_msg
            )
    
    @Slot(str)
    def _on_folder_error(self, error_message):
        """Handle folder update error."""
        self.folder_start_btn.setEnabled(True)
        self.folder_stop_btn.setEnabled(False)
        self.folder_browse_btn.setEnabled(True)
        
        self.folder_error_label.setText(f"❌ ERROR: {error_message}")
        self.folder_error_label.setVisible(True)
        
        logger.error(f"Folder update error: {error_message}")
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
    def _on_open_mods_folder(self):
        """Open the mods folder."""
        folder_path = self.mods_folder_input.text().strip()
        
        if folder_path and Path(folder_path).exists():
            if os.name == 'nt':  # Windows
                os.startfile(folder_path)
            else:  # Linux/Mac
                os.system(f'xdg-open "{folder_path}"')
            logger.info(f"Opened: {folder_path}")
        else:
            QMessageBox.warning(self, "Invalid Folder", "Please select a valid mods folder first")
    
    @Slot()
    def _on_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()
        logger.info("Settings dialog closed")
    
    def closeEvent(self, event: QCloseEvent):
        """
        Handle window close event.
        Properly cleanup worker threads before closing.
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
                if not self.worker_thread.wait(5000):
                    logger.warning("Worker thread did not finish in time, terminating...")
                    self.worker_thread.terminate()
                    if not self.worker_thread.wait(2000):
                        logger.error("Worker thread could not be terminated!")
                logger.info("Worker thread stopped")
            
            # Stop update worker if running
            if self.update_worker_thread and self.update_worker_thread.isRunning():
                logger.info("Stopping update worker thread...")
                self.update_worker_thread.should_stop = True
                if not self.update_worker_thread.wait(5000):
                    logger.warning("Update worker thread did not finish in time, terminating...")
                    self.update_worker_thread.terminate()
                    if not self.update_worker_thread.wait(2000):
                        logger.error("Update worker thread could not be terminated!")
                logger.info("Update worker thread stopped")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        event.accept()
        logger.info("Window closed successfully")
