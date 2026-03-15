"""
Modern theme and styling system for the Factorio Mod Manager UI
With enhanced visual feedback for all interactive elements
"""

from enum import Enum
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication, QCheckBox, QPushButton


class ModernColors:
    """Modern color schemes with proper contrast ratios."""
    
    light = type('', (), {
        'primary': '#2563EB',
        'hover': '#1D4ED8',
        'active': '#1E40AF',
        'secondary': '#7C3AED',
        'background': '#FFFFFF',
        'surface': '#F8FAFC',
        'input_bg': '#F1F5F9',
        'text': '#0F172A',
        'subtitle_text': '#475569',
        'border': '#E2E8F0',
        'disabled': '#E2E8F0',
        'disabled_text': '#A0AEC0',
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
    })()
    
    dark = type('', (), {
        'primary': '#60A5FA',
        'hover': '#93C5FD',
        'active': '#BFDBFE',
        'secondary': '#A78BFA',
        'background': '#0F172A',
        'surface': '#1E293B',
        'input_bg': '#1E293B',
        'text': '#F8FAFC',
        'subtitle_text': '#CBD5E1',
        'border': '#334155',
        'disabled': '#334155',
        'disabled_text': '#64748B',
        'success': '#34D399',
        'warning': '#FBBF24',
        'error': '#F87171',
    })()


def get_modern_stylesheet(is_dark_mode=False):
    """
    Generate a modern stylesheet with proper visual feedback.
    Features: Clear :pressed, :checked, :focus states with visual feedback.
    """
    colors = ModernColors.dark if is_dark_mode else ModernColors.light
    
    stylesheet = f"""
    /* ===== GLOBAL STYLING ===== */
    QMainWindow {{
        background-color: {colors.background};
    }}
    
    QWidget {{
        background-color: {colors.background};
        color: {colors.text};
        font-family: "Segoe UI", Helvetica, sans-serif;
        font-size: 10pt;
    }}
    
    QFrame {{
        background-color: {colors.background};
        border: none;
    }}
    
    /* ===== TABS ===== */
    QTabWidget::pane {{
        border: none;
        background-color: {colors.background};
    }}
    
    QTabBar::tab {{
        background-color: {colors.background};
        color: {colors.text};
        padding: 8px 16px;
        border: none;
        border-bottom: 3px solid transparent;
        margin-right: 4px;
        font-weight: 500;
    }}
    
    QTabBar::tab:selected {{
        background-color: {colors.background};
        border-bottom: 3px solid {colors.primary};
        color: {colors.primary};
        font-weight: 600;
    }}
    
    QTabBar::tab:hover {{
        border-bottom: 3px solid {colors.hover};
        color: {colors.hover};
    }}
    
    /* ===== GROUP BOX ===== */
    QGroupBox {{
        color: {colors.text};
        border: 1px solid {colors.border};
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 10px;
        padding-left: 10px;
        padding-right: 10px;
        padding-bottom: 10px;
        font-weight: 600;
        font-size: 11pt;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 3px 0 3px;
    }}
    
    /* ===== INPUT FIELDS ===== */
    QLineEdit {{
        background-color: {colors.input_bg};
        color: {colors.text};
        border: 2px solid {colors.border};
        border-radius: 4px;
        padding: 6px 8px;
        selection-background-color: {colors.primary};
        selection-color: white;
        font-size: 10pt;
    }}
    
    QLineEdit:focus {{
        border: 2px solid {colors.primary};
        background-color: {colors.input_bg};
        padding: 6px 8px;
    }}
    
    QLineEdit:hover:!focus {{
        border: 2px solid {colors.hover};
    }}
    
    QLineEdit:read-only {{
        background-color: {colors.surface};
        color: {colors.subtitle_text};
    }}
    
    /* ===== BUTTONS ===== */
    QPushButton {{
        background-color: {colors.primary};
        color: white;
        border: none;
        border-radius: 4px;
        padding: 8px 14px;
        font-weight: 600;
        font-size: 10pt;
    }}
    
    QPushButton:hover {{
        background-color: {colors.hover};
    }}
    
    QPushButton:pressed {{
        background-color: {colors.active};
        padding: 9px 13px 7px 15px;
    }}
    
    QPushButton:disabled {{
        background-color: {colors.disabled};
        color: {colors.disabled_text};
    }}
    
    /* Secondary Button */
    QPushButton#secondaryButton {{
        background-color: {colors.surface};
        color: {colors.primary};
        border: 2px solid {colors.border};
        padding: 6px 12px;
    }}
    
    QPushButton#secondaryButton:hover {{
        background-color: {colors.input_bg};
        border: 2px solid {colors.hover};
        color: {colors.hover};
    }}
    
    QPushButton#secondaryButton:pressed {{
        background-color: {colors.input_bg};
        border: 2px solid {colors.active};
        color: {colors.active};
        padding: 7px 11px 5px 13px;
    }}
    
    /* Success Button */
    QPushButton#successButton {{
        background-color: {colors.success};
        color: white;
    }}
    
    QPushButton#successButton:hover {{
        background-color: #059669;
    }}
    
    QPushButton#successButton:pressed {{
        padding: 9px 13px 7px 15px;
    }}
    
    /* Danger Button */
    QPushButton#dangerButton {{
        background-color: {colors.error};
        color: white;
    }}
    
    QPushButton#dangerButton:hover {{
        background-color: #DC2626;
    }}
    
    QPushButton#dangerButton:pressed {{
        padding: 9px 13px 7px 15px;
    }}
    
    /* ===== CHECKBOXES - WITH CLEAR VISUAL FEEDBACK ===== */
    QCheckBox {{
        color: {colors.text};
        spacing: 8px;
        background-color: transparent;
        font-size: 10pt;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {colors.border};
        border-radius: 3px;
        background-color: {colors.input_bg};
        margin-right: 4px;
    }}
    
    QCheckBox::indicator:hover {{
        border: 2px solid {colors.primary};
        background-color: {colors.surface};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {colors.primary};
        border: 2px solid {colors.primary};
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNMTMgMyBMNiAxMCBMMiA2IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIuNSIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
        background-position: center;
        background-repeat: no-repeat;
    }}
    
    QCheckBox::indicator:checked:hover {{
        background-color: {colors.hover};
        border: 2px solid {colors.hover};
    }}
    
    QCheckBox::indicator:disabled {{
        border: 2px solid {colors.disabled};
        background-color: {colors.surface};
    }}
    
    /* ===== PROGRESS BAR ===== */
    QProgressBar {{
        border: 1px solid {colors.border};
        border-radius: 4px;
        background-color: {colors.input_bg};
        color: {colors.text};
        height: 24px;
        text-align: center;
    }}
    
    QProgressBar::chunk {{
        background-color: {colors.primary};
        border-radius: 3px;
        margin: 1px;
    }}
    
    /* ===== TEXT EDIT ===== */
    QTextEdit {{
        background-color: {colors.input_bg};
        color: {colors.text};
        border: 1px solid {colors.border};
        border-radius: 4px;
        padding: 6px 8px;
        font-family: Courier, monospace;
        font-size: 9pt;
    }}
    
    QTextEdit:focus {{
        border: 2px solid {colors.primary};
        padding: 5px 7px;
    }}
    
    QTextEdit:hover:!focus {{
        border: 1px solid {colors.hover};
    }}
    
    /* ===== COMBO BOX ===== */
    QComboBox {{
        background-color: {colors.input_bg};
        color: {colors.text};
        border: 2px solid {colors.border};
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 10pt;
        min-height: 28px;
    }}
    
    QComboBox:focus {{
        border: 2px solid {colors.primary};
    }}
    
    QComboBox:hover:!focus {{
        border: 2px solid {colors.hover};
    }}
    
    QComboBox::drop-down {{
        border: none;
        background: transparent;
        width: 24px;
    }}
    
    QComboBox::down-arrow {{
        image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNNCA2bDQgNCA0LTQiIHN0cm9rZT0iY3VycmVudENvbG9yIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPjwvc3ZnPg==);
        width: 14px;
        height: 14px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {colors.input_bg};
        color: {colors.text};
        border: 1px solid {colors.border};
        border-radius: 4px;
        selection-background-color: {colors.primary};
        outline: none;
    }}
    
    QComboBox QAbstractItemView::item {{
        padding: 4px 8px;
        height: 28px;
    }}
    
    QComboBox QAbstractItemView::item:selected {{
        background-color: {colors.primary};
        color: white;
    }}
    
    /* ===== SCROLLBAR ===== */
    QScrollBar:vertical {{
        width: 12px;
        background-color: {colors.background};
        border: none;
    }}
    
    QScrollBar::handle:vertical {{
        background-color: {colors.border};
        border-radius: 6px;
        min-height: 20px;
        margin: 2px 2px 2px 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background-color: {colors.hover};
    }}
    
    QScrollBar:horizontal {{
        height: 12px;
        background-color: {colors.background};
        border: none;
    }}
    
    QScrollBar::handle:horizontal {{
        background-color: {colors.border};
        border-radius: 6px;
        min-width: 20px;
        margin: 2px 2px 2px 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background-color: {colors.hover};
    }}
    
    /* ===== LABELS ===== */
    QLabel {{
        color: {colors.text};
        background-color: transparent;
        font-size: 10pt;
    }}
    
    QLabel#subtitleLabel {{
        color: {colors.subtitle_text};
        font-size: 9pt;
    }}
    
    QLabel#statusLabel {{
        color: {colors.subtitle_text};
        font-size: 9pt;
    }}
    
    QLabel#errorLabel {{
        color: #FCA5A5;
        background-color: {colors.input_bg};
        border: 1px solid #FCA5A5;
        border-radius: 4px;
        padding: 8px;
        font-size: 9pt;
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
    def create_modern_font(size=10, bold=False, italic=False):
        """Create a modern font with consistent styling."""
        font = QFont('Segoe UI', size)
        font.setBold(bold)
        font.setItalic(italic)
        return font
    
    @staticmethod
    def create_title_font():
        """Create a title font (16pt bold)."""
        font = QFont('Segoe UI', 16)
        font.setBold(True)
        return font
    
    @staticmethod
    def create_heading_font():
        """Create a heading font (12pt bold)."""
        font = QFont('Segoe UI', 12)
        font.setBold(True)
        return font
    
    @staticmethod
    def apply_button_style(button, style_type='primary'):
        """Apply a specific button style."""
        if style_type == 'secondary':
            button.setObjectName('secondaryButton')
        elif style_type == 'success':
            button.setObjectName('successButton')
        elif style_type == 'danger':
            button.setObjectName('dangerButton')
        else:
            button.setObjectName('')  # Primary style is default
