"""
ui/controllers/theme_controller.py - Theme management controller
"""

import logging
import json
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.theme import ThemeMode, ThemeManager
from ui.modern_theme import get_modern_stylesheet


logger = logging.getLogger(__name__)


class ThemeController:
    """Controller for managing theme preferences and application."""
    
    THEME_FILE = Path(__file__).parent.parent.parent / 'config' / 'theme_settings.json'
    
    def __init__(self):
        self.current_theme = ThemeMode.SYSTEM
        self.is_dark_mode = False
    
    def load_preference(self) -> ThemeMode:
        """Load theme preference from file."""
        try:
            if self.THEME_FILE.exists():
                with open(self.THEME_FILE, 'r') as f:
                    data = json.load(f)
                    theme_str = data.get('theme', 'system').lower()
                    try:
                        self.current_theme = ThemeMode[theme_str.upper()]
                    except KeyError:
                        self.current_theme = ThemeMode.SYSTEM
            else:
                self.current_theme = ThemeMode.SYSTEM
            
            return self.current_theme
        except Exception as e:
            logger.warning(f"Could not load theme preference: {e}")
            self.current_theme = ThemeMode.SYSTEM
            return self.current_theme
    
    def save_preference(self, theme: ThemeMode):
        """Save theme preference to file."""
        try:
            self.THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.THEME_FILE, 'w') as f:
                json.dump({'theme': theme.value}, f)
            
            self.current_theme = theme
            logger.info(f"Saved theme preference: {theme.value}")
        except Exception as e:
            logger.error(f"Could not save theme preference: {e}")
    
    def apply_theme(self, theme: ThemeMode):
        """Apply theme to application."""
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
    
    def get_stylesheet(self) -> str:
        """Get stylesheet for current theme."""
        return get_modern_stylesheet(self.is_dark_mode)
    
    def get_theme_modes(self) -> list:
        """Get available theme modes."""
        return ["Light", "Dark", "System"]
    
    def get_theme_index(self, theme: ThemeMode) -> int:
        """Get combo box index for theme."""
        theme_map = {
            ThemeMode.LIGHT: 0,
            ThemeMode.DARK: 1,
            ThemeMode.SYSTEM: 2
        }
        return theme_map.get(theme, 2)
    
    def get_theme_from_index(self, index: int) -> ThemeMode:
        """Get theme mode from combo box index."""
        themes = [ThemeMode.LIGHT, ThemeMode.DARK, ThemeMode.SYSTEM]
        return themes[index] if 0 <= index < len(themes) else ThemeMode.SYSTEM
