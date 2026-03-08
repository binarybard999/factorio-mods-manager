"""
ui/settings_dialog.py - Settings configuration dialog for user customization
"""

import json
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QCheckBox, QPushButton, QGroupBox,
    QGridLayout, QMessageBox, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    """
    Dialog for customizing user settings.
    Stores settings in config/user_settings.json.
    """
    
    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.setWindowTitle("Settings - Configuration")
        self.setGeometry(200, 200, 600, 500)
        self.user_settings_file = Path(__file__).parent.parent / 'config' / 'user_settings.json'
        self.user_settings = {}
        
        try:
            self._load_user_settings()
            self._setup_ui()
        except Exception as e:
            logger.error(f"Error initializing settings dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize settings dialog:\n{str(e)}")
            self.close()
    
    def _load_user_settings(self):
        """Load settings from user_settings.json."""
        try:
            if self.user_settings_file.exists():
                with open(self.user_settings_file, 'r') as f:
                    self.user_settings = json.load(f)
                logger.debug(f"Loaded user settings from {self.user_settings_file}")
            else:
                self.user_settings = {}
                logger.debug(f"No user settings file found, using defaults")
        except Exception as e:
            logger.error(f"Failed to load user settings: {e}")
            self.user_settings = {}
    
    def _get_setting(self, key, default):
        """Get setting value from user settings or use default."""
        return self.user_settings.get(key, default)
    
    def _setup_ui(self):
        """Setup the settings dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Settings")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Network Settings Group
        network_group = QGroupBox("Network Settings")
        network_layout = QGridLayout()
        
        # REQUEST_TIMEOUT
        network_layout.addWidget(QLabel("Request Timeout (seconds):"), 0, 0)
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setMinimum(5)
        self.timeout_spinbox.setMaximum(300)
        self.timeout_spinbox.setValue(self._get_setting('REQUEST_TIMEOUT', 120))
        self.timeout_spinbox.setSuffix(" sec")
        network_layout.addWidget(self.timeout_spinbox, 0, 1)
        
        # MAX_RETRIES
        network_layout.addWidget(QLabel("Max Retries:"), 1, 0)
        self.retries_spinbox = QSpinBox()
        self.retries_spinbox.setMinimum(1)
        self.retries_spinbox.setMaximum(20)
        self.retries_spinbox.setValue(self._get_setting('MAX_RETRIES', 5))
        network_layout.addWidget(self.retries_spinbox, 1, 1)
        
        # BACKOFF_BASE
        network_layout.addWidget(QLabel("Backoff Base:"), 2, 0)
        self.backoff_spinbox = QDoubleSpinBox()
        self.backoff_spinbox.setMinimum(1.0)
        self.backoff_spinbox.setMaximum(3.0)
        self.backoff_spinbox.setSingleStep(0.1)
        self.backoff_spinbox.setValue(self._get_setting('BACKOFF_BASE', 1.4))
        network_layout.addWidget(self.backoff_spinbox, 2, 1)
        
        # RANDOM_DELAY_MIN
        network_layout.addWidget(QLabel("Random Delay Min (sec):"), 3, 0)
        self.delay_min_spinbox = QDoubleSpinBox()
        self.delay_min_spinbox.setMinimum(0.0)
        self.delay_min_spinbox.setMaximum(10.0)
        self.delay_min_spinbox.setSingleStep(0.1)
        self.delay_min_spinbox.setValue(self._get_setting('RANDOM_DELAY_MIN', 0.5))
        network_layout.addWidget(self.delay_min_spinbox, 3, 1)
        
        # RANDOM_DELAY_MAX
        network_layout.addWidget(QLabel("Random Delay Max (sec):"), 4, 0)
        self.delay_max_spinbox = QDoubleSpinBox()
        self.delay_max_spinbox.setMinimum(0.1)
        self.delay_max_spinbox.setMaximum(10.0)
        self.delay_max_spinbox.setSingleStep(0.1)
        self.delay_max_spinbox.setValue(self._get_setting('RANDOM_DELAY_MAX', 2.0))
        network_layout.addWidget(self.delay_max_spinbox, 4, 1)
        
        network_group.setLayout(network_layout)
        scroll_layout.addWidget(network_group)
        
        # Performance Settings Group
        perf_group = QGroupBox("Performance Settings")
        perf_layout = QGridLayout()
        
        # MAX_WORKERS
        perf_layout.addWidget(QLabel("Max Workers (concurrent):"), 0, 0)
        self.workers_spinbox = QSpinBox()
        self.workers_spinbox.setMinimum(1)
        self.workers_spinbox.setMaximum(16)
        self.workers_spinbox.setValue(self._get_setting('MAX_WORKERS', 4))
        perf_layout.addWidget(self.workers_spinbox, 0, 1)
        
        perf_group.setLayout(perf_layout)
        scroll_layout.addWidget(perf_group)
        
        # Feature Flags Group
        features_group = QGroupBox("Feature Flags")
        features_layout = QGridLayout()
        
        self.flag_save_images = QCheckBox("Save Images")
        self.flag_save_images.setChecked(self._get_setting('SAVE_IMAGES', True))
        features_layout.addWidget(self.flag_save_images, 0, 0)
        
        self.flag_save_releases = QCheckBox("Save Releases")
        self.flag_save_releases.setChecked(self._get_setting('SAVE_RELEASES', False))
        features_layout.addWidget(self.flag_save_releases, 0, 1)
        
        self.flag_download_zips = QCheckBox("Download ZIPs")
        self.flag_download_zips.setChecked(self._get_setting('DOWNLOAD_ZIPS', True))
        features_layout.addWidget(self.flag_download_zips, 1, 0)
        
        self.flag_save_changelog = QCheckBox("Save Changelog")
        self.flag_save_changelog.setChecked(self._get_setting('SAVE_CHANGELOG', False))
        features_layout.addWidget(self.flag_save_changelog, 1, 1)
        
        features_group.setLayout(features_layout)
        scroll_layout.addWidget(features_group)
        
        # Mirror URLs Group
        mirror_group = QGroupBox("Mirror URLs")
        mirror_layout = QVBoxLayout()
        
        mirror_layout.addWidget(QLabel("Primary Mirror URL:"))
        self.mirror_lineedit = QLineEdit()
        self.mirror_lineedit.setText(self._get_setting('MIRROR_URLS', 'https://mods-storage.re146.dev'))
        mirror_layout.addWidget(self.mirror_lineedit)
        
        mirror_group.setLayout(mirror_layout)
        scroll_layout.addWidget(mirror_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self._on_save)
        button_layout.addWidget(self.save_btn)
        
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self._on_reset)
        button_layout.addWidget(self.reset_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def _on_save(self):
        """Save settings to user_settings.json."""
        try:
            # Prepare updated values
            updated_values = {
                'REQUEST_TIMEOUT': self.timeout_spinbox.value(),
                'MAX_RETRIES': self.retries_spinbox.value(),
                'BACKOFF_BASE': self.backoff_spinbox.value(),
                'RANDOM_DELAY_MIN': self.delay_min_spinbox.value(),
                'RANDOM_DELAY_MAX': self.delay_max_spinbox.value(),
                'MAX_WORKERS': self.workers_spinbox.value(),
                'SAVE_IMAGES': self.flag_save_images.isChecked(),
                'SAVE_RELEASES': self.flag_save_releases.isChecked(),
                'DOWNLOAD_ZIPS': self.flag_download_zips.isChecked(),
                'SAVE_CHANGELOG': self.flag_save_changelog.isChecked(),
                'MIRROR_URLS': self.mirror_lineedit.text(),
            }
            
            # Ensure directory exists
            self.user_settings_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON file
            with open(self.user_settings_file, 'w') as f:
                json.dump(updated_values, f, indent=2)
            
            logger.info(f"Settings saved to {self.user_settings_file}")
            QMessageBox.information(
                self, 
                "Success", 
                "Settings saved successfully!\nRestart the application to apply changes."
            )
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save settings:\n{str(e)}"
            )
    
    def _on_reset(self):
        """Reset settings to defaults."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Delete user settings file if it exists
                if self.user_settings_file.exists():
                    self.user_settings_file.unlink()
                    logger.info("User settings file deleted")
                
                # Reset UI to defaults
                self.timeout_spinbox.setValue(120)
                self.retries_spinbox.setValue(5)
                self.backoff_spinbox.setValue(1.4)
                self.delay_min_spinbox.setValue(0.5)
                self.delay_max_spinbox.setValue(2.0)
                self.workers_spinbox.setValue(4)
                self.flag_save_images.setChecked(True)
                self.flag_save_releases.setChecked(False)
                self.flag_download_zips.setChecked(True)
                self.flag_save_changelog.setChecked(False)
                self.mirror_lineedit.setText('https://mods-storage.re146.dev')
                
                QMessageBox.information(
                    self,
                    "Reset Successful",
                    "Settings reset to defaults.\nRestart the application for changes to take effect."
                )
            except Exception as e:
                logger.error(f"Failed to reset settings: {e}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to reset settings:\n{str(e)}"
                )
