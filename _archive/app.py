"""
ui/app.py - Modern GUI application for Factorio Mod Manager
Proper modern layout with clean sections, clear visual hierarchy, and usable design
"""

import logging
import os
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QLineEdit, QCheckBox,
    QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QComboBox, QTabWidget, QFrame, QApplication
)
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QColor, QDragEnterEvent, QDropEvent, QCloseEvent

from config.settings import get_settings
from ui.worker import ModProcessorWorker, WorkerThread, UpdateWorkerThread
from ui.settings_dialog import SettingsDialog
from ui.theme import ThemeMode, ThemeManager
from ui.modern_theme import ModernUIHelper, get_modern_stylesheet, ModernColors


logger = logging.getLogger(__name__)

# Import version from main
try:
    from main import VERSION, VERSION_NAME
except ImportError:
    VERSION = "2.0.0"
    VERSION_NAME = "Modern UI Release"


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
    """Main application window with proper modern layout."""
    
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
        
        self.setWindowTitle(f"Factorio Mod Manager v{VERSION} - {VERSION_NAME}")
        self.setGeometry(100, 100, 1300, 950)
        self.setMinimumSize(1100, 800)
        
        self._setup_ui()
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
        """Setup the user interface with proper modern layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # ===== HEADER BAR =====
        header_widget = QFrame()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setSpacing(16)
        header_layout.setContentsMargins(20, 12, 20, 12)
        
        # App title
        title_label = QLabel("Factorio Mod Manager")
        title_font = ModernUIHelper.create_title_font()
        title_label.setFont(title_font)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Theme selector (compact)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System"])
        theme_index = {'light': 0, 'dark': 1, 'system': 2}.get(self.current_theme.value, 2)
        self.theme_combo.setCurrentIndex(theme_index)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.theme_combo.setMaximumWidth(120)
        header_layout.addWidget(self.theme_combo)
        
        main_layout.addWidget(header_widget)
        
        # ===== TABS CONTENT =====
        self.tabs = QTabWidget()
        self.tabs.setContentsMargins(0, 0, 0, 0)
        
        # Tab 1: List Processing
        self.list_tab_widget = self._create_list_processing_tab()
        self.tabs.addTab(self.list_tab_widget, "📋 Process Mod List")
        
        # Tab 2: Folder Updates
        self.folder_tab_widget = self._create_folder_updates_tab()
        self.tabs.addTab(self.folder_tab_widget, "📁 Update Mods Folder")
        
        main_layout.addWidget(self.tabs, 1)
    
    def _create_list_processing_tab(self):
        """Create the list processing tab with proper modern layout."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # =====  FILE SELECTION SECTION =====
        file_group = QGroupBox("Mod List File")
        file_group.setMaximumHeight(100)
        file_layout = QHBoxLayout(file_group)
        file_layout.setSpacing(8)
        
        self.file_input = DragDropLineEdit(accept_type='file')
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Drag & drop mods.txt here or click Browse...")
        self.file_input.setMinimumHeight(36)
        
        self.file_browse_btn = QPushButton("Browse")
        self.file_browse_btn.setMinimumHeight(36)
        self.file_browse_btn.setMaximumWidth(100)
        self.file_browse_btn.clicked.connect(self._on_browse_file)
        
        file_layout.addWidget(self.file_input, 1)
        file_layout.addWidget(self.file_browse_btn)
        main_layout.addWidget(file_group)
        
        # ===== OPTIONS SECTION =====
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
        
        # ===== PROGRESS SECTION =====
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(8)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        progress_title = QLabel("Progress")
        progress_title.setFont(ModernUIHelper.create_heading_font())
        progress_layout.addWidget(progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(24)
        progress_layout.addWidget(self.progress_bar)
        
        progress_info = QHBoxLayout()
        self.progress_label = QLabel("Ready")
        self.progress_label.setObjectName("statusLabel")
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        progress_info.addWidget(self.progress_label)
        progress_info.addStretch()
        progress_info.addWidget(self.status_label)
        progress_layout.addLayout(progress_info)
        
        # Error display
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        self.error_label.setMinimumHeight(35)
        self.error_label.setObjectName("errorLabel")
        progress_layout.addWidget(self.error_label)
        
        main_layout.addWidget(progress_frame)
        
        # ===== LOG OUTPUT SECTION =====
        log_title = QLabel("Processing Log")
        log_title.setFont(ModernUIHelper.create_heading_font())
        main_layout.addWidget(log_title)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(150)
        main_layout.addWidget(self.log_output, 1)
        
        # ===== BUTTON BAR (SEPARATE SECTION) =====
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        main_layout.addWidget(button_frame)
        
        return widget
    
    def _create_folder_updates_tab(self):
        """Create the folder updates tab with proper modern layout."""
        widget = QWidget()
        main_layout = QVBoxLayout(widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== FOLDER SELECTION SECTION =====
        folder_group = QGroupBox("Mods Folder")
        folder_group.setMaximumHeight(100)
        folder_layout = QHBoxLayout(folder_group)
        folder_layout.setSpacing(8)
        
        self.mods_folder_input = DragDropLineEdit(accept_type='folder')
        self.mods_folder_input.setReadOnly(True)
        self.mods_folder_input.setPlaceholderText("Drag & drop your mods folder here or click Browse...")
        self.mods_folder_input.setMinimumHeight(36)
        
        self.folder_browse_btn = QPushButton("Browse")
        self.folder_browse_btn.setMinimumHeight(36)
        self.folder_browse_btn.setMaximumWidth(100)
        self.folder_browse_btn.clicked.connect(self._on_browse_folder)
        
        folder_layout.addWidget(self.mods_folder_input, 1)
        folder_layout.addWidget(self.folder_browse_btn)
        main_layout.addWidget(folder_group)
        
        # ===== UPDATE OPTIONS SECTION =====
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
        
        # ===== INFO SECTION =====
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
        main_layout.addWidget(info_frame)
        
        # ===== PROGRESS SECTION =====
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(8)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        progress_title = QLabel("Progress")
        progress_title.setFont(ModernUIHelper.create_heading_font())
        progress_layout.addWidget(progress_title)
        
        self.folder_progress_bar = QProgressBar()
        self.folder_progress_bar.setRange(0, 100)
        self.folder_progress_bar.setValue(0)
        self.folder_progress_bar.setMinimumHeight(24)
        progress_layout.addWidget(self.folder_progress_bar)
        
        progress_info = QHBoxLayout()
        self.folder_progress_label = QLabel("Ready")
        self.folder_progress_label.setObjectName("statusLabel")
        self.folder_status_label = QLabel("")
        self.folder_status_label.setObjectName("statusLabel")
        progress_info.addWidget(self.folder_progress_label)
        progress_info.addStretch()
        progress_info.addWidget(self.folder_status_label)
        progress_layout.addLayout(progress_info)
        
        # Error display
        self.folder_error_label = QLabel()
        self.folder_error_label.setWordWrap(True)
        self.folder_error_label.setVisible(False)
        self.folder_error_label.setMinimumHeight(35)
        self.folder_error_label.setObjectName("errorLabel")
        progress_layout.addWidget(self.folder_error_label)
        
        main_layout.addWidget(progress_frame)
        
        # ===== LOG OUTPUT SECTION =====
        log_title = QLabel("Update Log")
        log_title.setFont(ModernUIHelper.create_heading_font())
        main_layout.addWidget(log_title)
        
        self.folder_log_output = QTextEdit()
        self.folder_log_output.setReadOnly(True)
        self.folder_log_output.setMinimumHeight(150)
        main_layout.addWidget(self.folder_log_output, 1)
        
        # ===== BUTTON BAR (SEPARATE SECTION) =====
        button_frame = QFrame()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.folder_start_btn = QPushButton("✅ Check Updates")
        self.folder_start_btn.setMinimumHeight(36)
        self.folder_start_btn.setMinimumWidth(140)
        self.folder_start_btn.clicked.connect(self._on_start_folder_update)
        ModernUIHelper.apply_button_style(self.folder_start_btn, 'success')
        
        self.folder_stop_btn = QPushButton("⏹ Stop")
        self.folder_stop_btn.setMinimumHeight(36)
        self.folder_stop_btn.setMaximumWidth(80)
        self.folder_stop_btn.setEnabled(False)
        self.folder_stop_btn.clicked.connect(self._on_stop_folder_update)
        ModernUIHelper.apply_button_style(self.folder_stop_btn, 'danger')
        
        button_layout.addWidget(self.folder_start_btn)
        button_layout.addWidget(self.folder_stop_btn)
        button_layout.addStretch()
        
        self.folder_open_btn = QPushButton("📁 Open")
        self.folder_open_btn.setMinimumHeight(36)
        self.folder_open_btn.setMaximumWidth(80)
        self.folder_open_btn.clicked.connect(self._on_open_mods_folder)
        ModernUIHelper.apply_button_style(self.folder_open_btn, 'secondary')
        
        button_layout.addWidget(self.folder_open_btn)
        
        main_layout.addWidget(button_frame)
        
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
        """Handle browse file button."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Mod List File", "", "Text Files (*.txt);;All Files (*.*)"
        )
        if file_path:
            self.file_input.setText(file_path)
            logger.info(f"Selected file: {file_path}")
    
    @Slot()
    def _on_browse_folder(self):
        """Handle browse folder button."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Mods Folder", "")
        if folder_path:
            self.mods_folder_input.setText(folder_path)
            logger.info(f"Selected folder: {folder_path}")
    
    @Slot()
    def _on_start(self):
        """Handle start button."""
        file_path = self.file_input.text().strip()
        
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
        
        # Setup UI
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.file_browse_btn.setEnabled(False)
        
        self.error_label.setVisible(False)
        self.status_label.setText("Processing...")
        self.progress_bar.setMaximum(len(self.mod_filenames))
        self.progress_bar.setValue(0)
        self.progress_label.setText("0 / " + str(len(self.mod_filenames)))
        
        # Create and start worker
        self.worker = ModProcessorWorker(self.settings)
        self.worker_thread = WorkerThread(self.worker, self.settings)
        
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.status_updated.connect(self._on_status)
        self.worker.log_message.connect(self._on_log)
        self.worker.finished.connect(self._on_finished)
        self.worker.error_occurred.connect(self._on_error)
        
        use_multithreading = self.opt_multithreading.isChecked()
        self.worker_thread.set_mod_list(self.mod_filenames, use_multithreading)
        
        logger.info(f"Starting processing of {len(self.mod_filenames)} mods")
        self.worker_thread.start()
    
    @Slot()
    def _on_stop(self):
        """Handle stop button."""
        if self.worker:
            self.worker.should_stop = True
            logger.warning("Stop requested")
    
    @Slot()
    def _on_start_folder_update(self):
        """Handle folder update start button."""
        folder_path = self.mods_folder_input.text().strip()
        
        if not folder_path or not Path(folder_path).exists():
            QMessageBox.warning(self, "Error", "Please select a valid mods folder")
            return
        
        self.folder_start_btn.setEnabled(False)
        self.folder_stop_btn.setEnabled(True)
        self.folder_browse_btn.setEnabled(False)
        
        self.folder_error_label.setVisible(False)
        self.folder_status_label.setText("Scanning...")
        self.folder_progress_bar.setMaximum(100)
        self.folder_progress_bar.setValue(0)
        self.folder_progress_label.setText("Initializing...")
        
        logger.info(f"Starting folder update: {folder_path}")
        self.folder_log_output.clear()
        
        self.update_worker_thread = UpdateWorkerThread(folder_path, self.settings)
        
        self.update_worker_thread.progress_updated.connect(self._on_folder_progress)
        self.update_worker_thread.status_updated.connect(self._on_folder_status)
        self.update_worker_thread.log_message.connect(self._on_folder_log)
        self.update_worker_thread.finished.connect(self._on_folder_finished)
        self.update_worker_thread.error_occurred.connect(self._on_folder_error)
        
        self.update_worker_thread.start()
    
    @Slot()
    def _on_stop_folder_update(self):
        """Handle folder update stop button."""
        if self.update_worker_thread:
            self.update_worker_thread.should_stop = True
            logger.warning("Folder update stopped")
    
    @Slot(int, int, str)
    def _on_progress(self, current, total, message):
        """Handle progress signal."""
        self.progress_bar.setValue(current)
        self.progress_label.setText(f"{current} / {total}")
        self.status_label.setText(message[:40])
        logger.info(message)
    
    @Slot(str)
    def _on_log(self, message):
        """Handle log signal."""
        self.log_output.append(message)
    
    @Slot(str)
    def _on_status(self, message):
        """Handle status signal."""
        self.status_label.setText(message[:40])
    
    @Slot(dict)
    def _on_finished(self, summary):
        """Handle finished signal."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.file_browse_btn.setEnabled(True)
        
        self.progress_label.setText("Complete")
        
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
        """Handle error signal."""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.file_browse_btn.setEnabled(True)
        
        self.error_label.setText(f"Error: {error_message}")
        self.error_label.setVisible(True)
        logger.error(error_message)
        QMessageBox.critical(self, "Error", error_message)
    
    @Slot(int, int, str)
    def _on_folder_progress(self, current, total, message):
        """Handle folder progress signal."""
        if total > 0:
            self.folder_progress_bar.setValue(int((current / total) * 100))
            self.folder_progress_label.setText(f"{current} / {total}")
        self.folder_status_label.setText(message[:40])
    
    @Slot(str)
    def _on_folder_log(self, message):
        """Handle folder log signal."""
        self.folder_log_output.append(message)
    
    @Slot(str)
    def _on_folder_status(self, message):
        """Handle folder status signal."""
        self.folder_status_label.setText(message[:40])
    
    @Slot(dict)
    def _on_folder_finished(self, summary):
        """Handle folder finished signal."""
        self.folder_start_btn.setEnabled(True)
        self.folder_stop_btn.setEnabled(False)
        self.folder_browse_btn.setEnabled(True)
        
        self.folder_progress_label.setText("Complete")
        
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
    def _on_folder_error(self, error_message):
        """Handle folder error signal."""
        self.folder_start_btn.setEnabled(True)
        self.folder_stop_btn.setEnabled(False)
        self.folder_browse_btn.setEnabled(True)
        
        self.folder_error_label.setText(f"Error: {error_message}")
        self.folder_error_label.setVisible(True)
        logger.error(error_message)
        QMessageBox.critical(self, "Error", error_message)
    
    @Slot()
    def _on_open_csv(self):
        """Open CSV file."""
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
        folder = Path.cwd()
        if folder.exists():
            if os.name == 'nt':
                os.startfile(folder)
            else:
                os.system(f'xdg-open "{folder}"')
    
    @Slot()
    def _on_open_mods_folder(self):
        """Open mods folder."""
        folder_path = self.mods_folder_input.text().strip()
        if folder_path and Path(folder_path).exists():
            if os.name == 'nt':
                os.startfile(folder_path)
            else:
                os.system(f'xdg-open "{folder_path}"')
        else:
            QMessageBox.warning(self, "Error", "Please select a valid folder")
    
    @Slot()
    def _on_settings(self):
        """Open settings dialog."""
        try:
            dialog = SettingsDialog(self)
            dialog.exec()
        except Exception as e:
            logger.warning(f"Could not open settings: {e}")
            QMessageBox.warning(self, "Settings", "Settings dialog not available")
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close."""
        logger.info("Closing application")
        try:
            if self.worker:
                self.worker.should_stop = True
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.wait(2000)
            if self.update_worker_thread and self.update_worker_thread.isRunning():
                self.update_worker_thread.should_stop = True
                self.update_worker_thread.wait(2000)
        except:
            pass
        event.accept()
