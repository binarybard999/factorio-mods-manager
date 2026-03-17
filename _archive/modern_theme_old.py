"""
Modern theme and styling system for the Factorio Mod Manager UI
Uses glassmorphism, gradients, and modern colors for a professional look
"""

from enum import Enum
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton


class ModernColors:
    """Modern color schemes with proper contrast ratios."""
    
    # Light theme colors (soft pastels with dark text)
    LIGHT = {
        'primary': '#2563EB',          # Bright blue
        'primary_hover': '#1D4ED8',    # Darker blue
        'primary_light': '#DBEAFE',    # Light blue background
        
        'secondary': '#7C3AED',        # Purple
        'secondary_light': '#EDE9FE',  # Light purple
        
        'background': '#FFFFFF',        # White
        'surface': '#F8FAFC',          # Very light gray
        'surface_alt': '#F1F5F9',      # Light gray
        
        'text_primary': '#0F172A',     # Almost black
        'text_secondary': '#475569',   # Dark gray
        'text_tertiary': '#64748B',    # Medium gray
        
        'border': '#E2E8F0',           # Light border
        'border_focus': '#2563EB',     # Blue border
        
        'success': '#10B981',          # Green
        'warning': '#F59E0B',          # Amber
        'error': '#EF4444',            # Red
        'info': '#06B6D4',             # Cyan
        
        'shadow': 'rgba(0, 0, 0, 0.1)',
    }
    
    # Dark theme colors (dark with proper contrast)
    DARK = {
        'primary': '#60A5FA',          # Light blue
        'primary_hover': '#93C5FD',    # Lighter blue
        'primary_light': '#1E3A8A',    # Dark blue background
        
        'secondary': '#A78BFA',        # Light purple
        'secondary_light': '#4C1D95',  # Dark purple
        
        'background': '#0F172A',       # Very dark blue
        'surface': '#1E293B',          # Dark gray blue
        'surface_alt': '#334155',      # Medium dark gray
        
        'text_primary': '#F8FAFC',     # Nearly white
        'text_secondary': '#CBD5E1',   # Light gray
        'text_tertiary': '#94A3B8',    # Medium light gray
        
        'border': '#475569',           # Medium border
        'border_focus': '#60A5FA',     # Light blue border
        
        'success': '#34D399',          # Green
        'warning': '#FBBF24',          # Amber
        'error': '#F87171',            # Light red
        'info': '#22D3EE',             # Light cyan
        
        'shadow': 'rgba(0, 0, 0, 0.4)',
    }


def get_modern_stylesheet(is_dark_mode=False):
    """
    Generate a modern, professional stylesheet with glassmorphism effects.
    
    Args:
        is_dark_mode (bool): Whether to use dark mode colors
        
    Returns:
        str: QSS stylesheet
    """
    colors = ModernColors.DARK if is_dark_mode else ModernColors.LIGHT
    
    stylesheet = f"""
    /* Main Window */
    QMainWindow {{
        background-color: {colors['background']};
    }}
    
    QWidget {{
        background-color: {colors['background']};
        color: {colors['text_primary']};
    }}
    
    /* Tabs */
    QTabWidget::pane {{
        border: 1px solid {colors['border']};
        background-color: {colors['background']};
    }}
    
    QTabBar::tab {{
        background-color: {colors['surface']};
        color: {colors['text_secondary']};
        padding: 8px 20px;
        margin-right: 2px;
        border: 1px solid {colors['border']};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        font-weight: 500;
        font-size: 12px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {colors['background']};
        color: {colors['primary']};
        border: 1px solid {colors['border']};
        border-bottom: 3px solid {colors['primary']};
        padding-bottom: 5px;
        font-weight: 600;
    }}
    
    QTabBar::tab:hover:!selected {{
        background-color: {colors['surface_alt']};
        color: {colors['text_primary']};
    }}
    
    /* Line Edit / Text Input */
    QLineEdit {{
        background-color: {colors['surface']};
        border: 2px solid {colors['border']};
        border-radius: 6px;
        padding: 10px 12px;
        color: {colors['text_primary']};
        selection-background-color: {colors['primary']};
        font-size: 13px;
        font-family: 'Segoe UI', Arial;
    }}
    
    QLineEdit:focus {{
        border: 2px solid {colors['primary']};
        background-color: {colors['surface_alt']};
    }}
    
    QLineEdit:read-only {{
        background-color: {colors['surface_alt']};
        color: {colors['text_tertiary']};
    }}
    
    /* Combo Box */
    QComboBox {{
        background-color: {colors['surface']};
        border: 2px solid {colors['border']};
        border-radius: 6px;
        padding: 8px 12px;
        color: {colors['text_primary']};
        font-size: 13px;
        font-family: 'Segoe UI', Arial;
        min-height: 35px;
    }}
    
    QComboBox:focus {{
        border: 2px solid {colors['primary']};
        background-color: {colors['surface_alt']};
    }}
    
    QComboBox::drop-down {{
        background-color: {colors['primary']};
        border: none;
        border-radius: 4px;
        width: 30px;
        subcontrol-origin: padding;
        subcontrol-position: top right;
        margin: 3px;
    }}
    
    QComboBox::down-arrow {{
        width: 14px;
        height: 14px;
        image: none;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {colors['surface']};
        color: {colors['text_primary']};
        border: 1px solid {colors['border']};
        border-radius: 6px;
        selection-background-color: {colors['primary_light']};
        selection-color: {colors['text_primary']};
        padding: 4px;
    }}
    
    /* Checkbox */
    QCheckBox {{
        color: {colors['text_primary']};
        spacing: 8px;
        background-color: transparent;
        font-size: 13px;
        font-family: 'Segoe UI', Arial;
    }}
    
    QCheckBox::indicator {{
        width: 20px;
        height: 20px;
        border-radius: 4px;
        border: 2px solid {colors['border']};
        background-color: {colors['surface']};
        margin-right: 4px;
    }}
    
    QCheckBox::indicator:hover {{
        border: 2px solid {colors['primary']};
        background-color: {colors['primary_light']};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {colors['primary']};
        border: 2px solid {colors['primary']};
        background-image: url(data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2020%2020%22%3E%3Cpath%20fill%3D%22white%22%20d%3D%22M16.707%204.293a1%201%200%200%200-1.414%201.414l-8%208a1%201%200%200%201-1.414%200l-4-4a1%201%200%200%200-1.414%201.414l4%204a3%203%200%200%200%204.242%200l8-8a1%201%200%200%200%200-1.414z%22%2F%3E%3C%2Fsvg%3E);
        background-repeat: no-repeat;
        background-position: center;
    }}
    
    QCheckBox::indicator:disabled {{
        background-color: {colors['surface_alt']};
        border: 2px solid {colors['border']};
    }}
    
    /* Buttons */
    QPushButton {{
        background-color: {colors['primary']};
        color: white;
        border: none;
        border-radius: 6px;
        padding: 10px 16px;
        font-weight: 600;
        font-size: 13px;
        font-family: 'Segoe UI', Arial;
        min-height: 35px;
        min-width: 80px;
    }}
    
    QPushButton:hover {{
        background-color: {colors['primary_hover']};
        cursor: pointer;
    }}
    
    QPushButton:pressed {{
        background-color: {colors['primary']};
        padding: 11px 15px 9px 17px;
    }}
    
    QPushButton:disabled {{
        background-color: {colors['surface_alt']};
        color: {colors['text_tertiary']};
    }}
    
    /* Secondary Button */
    QPushButton#secondaryButton {{
        background-color: {colors['surface']};
        color: {colors['primary']};
        border: 2px solid {colors['primary']};
        border-radius: 6px;
        padding: 8px 16px;
        min-height: 33px;
    }}
    
    QPushButton#secondaryButton:hover {{
        background-color: {colors['primary_light']};
        color: {colors['primary']};
    }}
    
    /* Success Button */
    QPushButton#successButton {{
        background-color: {colors['success']};
        color: white;
    }}
    
    QPushButton#successButton:hover {{
        background-color: #059669;
    }}
    
    /* Danger Button */
    QPushButton#dangerButton {{
        background-color: {colors['error']};
        color: white;
    }}
    
    QPushButton#dangerButton:hover {{
        background-color: #DC2626;
    }}
    
    /* Progress Bar */
    QProgressBar {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
        border-radius: 6px;
        padding: 2px;
        color: {colors['text_primary']};
        height: 28px;
        font-size: 12px;
        font-weight: 500;
    }}
    
    QProgressBar::chunk {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {colors['primary']},
            stop:1 {colors['primary_hover']}
        );
        border-radius: 4px;
    }}
    
    /* Text Edit */
    QTextEdit {{
        background-color: {colors['surface']};
        border: 2px solid {colors['border']};
        border-radius: 6px;
        padding: 10px 12px;
        color: {colors['text_primary']};
        font-size: 12px;
        font-family: 'Courier New', monospace;
    }}
    
    QTextEdit:focus {{
        border: 2px solid {colors['primary']};
        background-color: {colors['surface_alt']};
    }}
    
    /* Scroll Bar */
    QScrollBar:vertical {{
        background-color: {colors['surface']};
        width: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {colors['border']};
        border-radius: 6px;
        min-height: 20px;
        margin: 2px 2px 2px 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {colors['primary']};
    }}
    
    QScrollBar:horizontal {{
        background-color: {colors['surface']};
        height: 12px;
        border-radius: 6px;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {colors['border']};
        border-radius: 6px;
        min-width: 20px;
        margin: 2px 2px 2px 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {colors['primary']};
    }}
    
    /* Group Box */
    QGroupBox {{
        color: {colors['text_primary']};
        border: 2px solid {colors['border']};
        border-radius: 8px;
        padding-top: 12px;
        padding-left: 12px;
        padding-right: 12px;
        padding-bottom: 8px;
        margin-top: 8px;
        font-weight: 600;
        font-size: 13px;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 6px 0 6px;
        margin-left: 6px;
    }}
    
    /* Labels */
    QLabel {{
        color: {colors['text_primary']};
        font-size: 13px;
    }}
    
    QLabel#titleLabel {{
        color: {colors['text_primary']};
        font-size: 16px;
        font-weight: 700;
    }}
    
    QLabel#subtitleLabel {{
        color: {colors['text_secondary']};
        font-size: 12px;
        font-weight: 400;
    }}
    
    QLabel#statusLabel {{
        color: {colors['text_secondary']};
        font-size: 11px;
        font-weight: 500;
    }}
    
    /* Message Box */
    QMessageBox QLabel {{
        color: {colors['text_primary']};
    }}
    
    /* File Dialog */
    QFileDialog QLabel {{
        color: {colors['text_primary']};
    }}
    
    /* Tooltip */
    QToolTip {{
        background-color: {colors['surface_alt']};
        color: {colors['text_primary']};
        border: 1px solid {colors['border']};
        border-radius: 4px;
        padding: 4px 8px;
    }}
    """
    return stylesheet


class ModernUIHelper:
    """Helper class for modern UI components and styling."""
    
    @staticmethod
    def apply_modern_style(widget, is_dark_mode=False):
        """Apply modern stylesheet to a widget."""
        stylesheet = get_modern_stylesheet(is_dark_mode)
        widget.setStyleSheet(stylesheet)
    
    @staticmethod
    def create_modern_font(size=13, bold=False, italic=False):
        """Create a modern font with consistent styling."""
        font = QFont('Segoe UI', size)
        font.setBold(bold)
        font.setItalic(italic)
        return font
    
    @staticmethod
    def create_title_font():
        """Create a title font."""
        font = QFont('Segoe UI', 16)
        font.setBold(True)
        return font
    
    @staticmethod
    def create_heading_font():
        """Create a heading font."""
        font = QFont('Segoe UI', 14)
        font.setBold(True)
        return font
    
    @staticmethod
    def get_icon_color(is_dark_mode=False):
        """Get the appropriate icon color for the current theme."""
        return ModernColors.DARK['primary'] if is_dark_mode else ModernColors.LIGHT['primary']
    
    @staticmethod
    def apply_button_style(button, style_type='primary'):
        """Apply a specific button style."""
        if style_type == 'secondary':
            button.setObjectName('secondaryButton')
        elif style_type == 'success':
            button.setObjectName('successButton')
        elif style_type == 'danger':
            button.setObjectName('dangerButton')
