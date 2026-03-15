"""
ui/theme.py - Theme management for light/dark/system modes
"""

import logging
from enum import Enum
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

logger = logging.getLogger(__name__)


class ThemeMode(Enum):
    """Theme mode enumeration."""
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"


class ThemeManager:
    """
    Manages application themes with support for light, dark, and system modes.
    """
    
    # Light theme colors
    LIGHT_COLORS = {
        'window_bg': QColor(255, 255, 255),
        'widget_bg': QColor(245, 245, 245),
        'text': QColor(0, 0, 0),
        'alt_text': QColor(60, 60, 60),
        'button_bg': QColor(235, 235, 235),
        'button_hover': QColor(220, 220, 220),
        'button_pressed': QColor(200, 200, 200),
        'highlight': QColor(0, 120, 215),
        'disabled_text': QColor(150, 150, 150),
        'error': QColor(229, 57, 53),
        'error_bg': QColor(255, 224, 224),
    }
    
    # Dark theme colors
    DARK_COLORS = {
        'window_bg': QColor(30, 30, 30),
        'widget_bg': QColor(45, 45, 45),
        'text': QColor(230, 230, 230),
        'alt_text': QColor(190, 190, 190),
        'button_bg': QColor(60, 60, 60),
        'button_hover': QColor(80, 80, 80),
        'button_pressed': QColor(100, 100, 100),
        'highlight': QColor(0, 150, 255),
        'disabled_text': QColor(100, 100, 100),
        'error': QColor(239, 83, 80),
        'error_bg': QColor(80, 30, 30),
    }
    
    @staticmethod
    def get_theme_stylesheet(theme_mode: ThemeMode) -> str:
        """
        Generate stylesheet for the given theme mode.
        
        Args:
            theme_mode (ThemeMode): The theme mode to use
            
        Returns:
            str: QSS stylesheet string
        """
        if theme_mode == ThemeMode.SYSTEM:
            # Use system colors - return minimal stylesheet
            return ThemeManager._get_system_stylesheet()
        
        colors = ThemeManager.DARK_COLORS if theme_mode == ThemeMode.DARK else ThemeManager.LIGHT_COLORS
        
        window_bg = colors['window_bg'].name()
        widget_bg = colors['widget_bg'].name()
        text = colors['text'].name()
        button_bg = colors['button_bg'].name()
        button_hover = colors['button_hover'].name()
        highlight = colors['highlight'].name()
        error_text = colors['error'].name()
        error_bg = colors['error_bg'].name()
        
        stylesheet = f"""
        QMainWindow, QWidget {{
            background-color: {window_bg};
            color: {text};
        }}
        
        QGroupBox {{
            background-color: {widget_bg};
            color: {text};
            border: 1px solid {button_bg};
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 2px;
        }}
        
        QPushButton {{
            background-color: {button_bg};
            color: {text};
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }}
        
        QPushButton:hover {{
            background-color: {button_hover};
        }}
        
        QPushButton:pressed {{
            background-color: {highlight};
        }}
        
        QPushButton:disabled {{
            background-color: {button_bg};
            color: {colors['disabled_text'].name()};
        }}
        
        QLineEdit {{
            background-color: {widget_bg};
            color: {text};
            border: 1px solid {button_bg};
            border-radius: 4px;
            padding: 6px;
            selection-background-color: {highlight};
        }}
        
        QLineEdit:focus {{
            border: 2px solid {highlight};
        }}
        
        QTextEdit {{
            background-color: {widget_bg};
            color: {text};
            border: 1px solid {button_bg};
            border-radius: 4px;
            padding: 6px;
        }}
        
        QCheckBox {{
            color: {text};
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {highlight};
            border: 2px solid {highlight};
            border-radius: 2px;
        }}
        
        QProgressBar {{
            background-color: {widget_bg};
            border: 1px solid {button_bg};
            border-radius: 4px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {highlight};
            border-radius: 4px;
        }}
        
        QLabel {{
            color: {text};
        }}
        
        QFileDialog {{
            background-color: {window_bg};
        }}
        
        QMenuItem {{
            padding: 4px 24px 4px 24px;
        }}
        
        QMenuBar {{
            background-color: {window_bg};
            color: {text};
        }}
        
        QMenuBar::item:selected {{
            background-color: {button_hover};
        }}
        
        QMenu {{
            background-color: {widget_bg};
            color: {text};
            border: 1px solid {button_bg};
        }}
        
        QMenu::item:selected {{
            background-color: {highlight};
            color: white;
        }}
        """
        
        return stylesheet
    
    @staticmethod
    def _get_system_stylesheet() -> str:
        """Get minimal stylesheet that respects system theme."""
        return """
        QGroupBox {
            border: 1px solid gray;
            border-radius: 4px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 2px;
        }
        
        QPushButton {
            border-radius: 4px;
            padding: 6px 12px;
        }
        
        QLineEdit {
            border-radius: 4px;
            padding: 6px;
        }
        
        QTextEdit {
            border-radius: 4px;
            padding: 6px;
        }
        """
    
    @staticmethod
    def apply_theme(theme_mode: ThemeMode) -> None:
        """
        Apply the specified theme to the application.
        
        Args:
            theme_mode (ThemeMode): The theme mode to apply
        """
        app = QApplication.instance()
        if app is None:
            logger.warning("No QApplication instance found")
            return
        
        stylesheet = ThemeManager.get_theme_stylesheet(theme_mode)
        app.setStyle('Fusion')  # Use Fusion style for consistent appearance
        app.setStyleSheet(stylesheet)
        
        logger.info(f"Applied theme: {theme_mode.value}")
    
    @staticmethod
    def is_system_dark_mode() -> bool:
        """
        Check if system is in dark mode (approximate).
        
        Returns:
            bool: True if system appears to be in dark mode
        """
        # This is a simple heuristic - you can improve this
        app = QApplication.instance()
        if app is None:
            return False
        
        palette = app.palette()
        window_color = palette.color(QPalette.Window)
        
        # Calculate luminance
        luminance = (0.299 * window_color.red() + 0.587 * window_color.green() + 0.114 * window_color.blue()) / 255
        return luminance < 0.5
