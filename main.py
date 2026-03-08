"""
main.py - Entry point for Factorio Mod Manager
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

from PySide6.QtWidgets import QApplication, QMessageBox

from config.settings import get_settings
from storage.file_store import FileStore
from ui.app import FactorioModManagerApp


def setup_logging():
    """
    Setup comprehensive logging with both file and console handlers.
    Logs go to: logs/factorio_mod_manager.log
    """
    # Create logs directory
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'factorio_mod_manager.log'
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # File handler - rotating to prevent huge files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-30s | %(funcName)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    
    # Console handler - less verbose
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)-8s - %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


# Configure logging
root_logger = setup_logging()

logger = logging.getLogger(__name__)


def initialize_app():
    """
    Initialize the application.
    
    - Load configuration
    - Validate settings
    - Ensure required directories exist
    
    Returns:
        Settings: The application settings object
    """
    logger.info("\n" + "="*80)
    logger.info("FACTORIO MOD MANAGER - APPLICATION STARTUP")
    logger.info("="*80)
    
    # Load settings from .env
    settings = get_settings()
    logger.info(f"Settings: {settings}")
    
    # Validate settings
    valid, error_msg = settings.validate()
    if not valid:
        logger.error(f"Configuration error: {error_msg}")
        raise ValueError(f"Invalid configuration: {error_msg}")
    
    # Ensure all required directories exist
    logger.info("Creating required directories...")
    FileStore.ensure_dir(settings.download_dir)
    FileStore.ensure_dir(settings.images_dir)
    FileStore.ensure_dir(settings.releases_dir)
    FileStore.ensure_dir(settings.failed_dir)
    
    logger.info("Initialization complete")
    logger.info("="*80 + "\n")
    return settings


def main():
    """
    Main entry point.
    """
    try:
        # Initialize application
        settings = initialize_app()
        
        # Create Qt application
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = FactorioModManagerApp()
        window.show()
        
        logger.info("GUI started successfully")
        
        # Run application
        sys.exit(app.exec())
    
    except Exception as e:
        logger.critical(f"\nFATAL ERROR: {e}", exc_info=True)
        logger.critical("="*80 + "\n")
        
        # Show error dialog if Qt is available
        try:
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            error_msg = (
                f"Failed to start Factorio Mod Manager:\n\n{e}\n\n"
                f"Check logs/factorio_mod_manager.log for details."
            )
            QMessageBox.critical(
                None,
                "Initialization Error",
                error_msg
            )
        except Exception as dialog_error:
            logger.error(f"Could not show error dialog: {dialog_error}")
            print(f"Error: {e}", file=sys.stderr)
        
        sys.exit(1)


if __name__ == "__main__":
    main()
