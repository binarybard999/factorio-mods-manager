"""
storage/file_store.py - Filesystem utilities
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileStore:
    """
    Handles filesystem operations like directory creation and file management.
    """
    
    @staticmethod
    def ensure_dir(path):
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path (str or Path): Directory path
            
        Returns:
            Path: The directory path
        """
        p = Path(path)
        try:
            p.mkdir(parents=True, exist_ok=True)
            logger.debug(f"[FS] Ensured directory: {p}")
            return p
        except OSError as e:
            logger.error(f"[FS] Failed to create directory {p}: {e}")
            raise
    
    @staticmethod
    def write_file(path, content, mode='w', encoding='utf-8'):
        """
        Write content to a file.
        
        Args:
            path (str or Path): File path
            content (str or bytes): Content to write
            mode (str): File open mode
            encoding (str): Encoding for text mode
            
        Returns:
            bool: True if successful
        """
        p = Path(path)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            
            if 'b' in mode:
                with open(p, mode) as f:
                    f.write(content)
            else:
                with open(p, mode, encoding=encoding) as f:
                    f.write(content)
            
            logger.debug(f"[FS] Wrote file: {p}")
            return True
        except IOError as e:
            logger.error(f"[FS] Failed to write file {p}: {e}")
            return False
    
    @staticmethod
    def append_file(path, content, encoding='utf-8'):
        """
        Append content to a file.
        
        Args:
            path (str or Path): File path
            content (str): Content to append
            encoding (str): Encoding
            
        Returns:
            bool: True if successful
        """
        return FileStore.write_file(path, content, mode='a', encoding=encoding)
    
    @staticmethod
    def read_file(path, encoding='utf-8'):
        """
        Read entire file content.
        
        Args:
            path (str or Path): File path
            encoding (str): Encoding
            
        Returns:
            str or None: File content or None if failed
        """
        p = Path(path)
        try:
            with open(p, 'r', encoding=encoding) as f:
                content = f.read()
            logger.debug(f"[FS] Read file: {p}")
            return content
        except IOError as e:
            logger.error(f"[FS] Failed to read file {p}: {e}")
            return None
    
    @staticmethod
    def file_exists(path):
        """
        Check if a file exists.
        
        Args:
            path (str or Path): File path
            
        Returns:
            bool: True if file exists
        """
        return Path(path).exists()
    
    @staticmethod
    def remove_file(path):
        """
        Remove a file if it exists.
        
        Args:
            path (str or Path): File path
            
        Returns:
            bool: True if removed, False if didn't exist
        """
        p = Path(path)
        try:
            if p.exists():
                p.unlink()
                logger.debug(f"[FS] Removed file: {p}")
                return True
            return False
        except OSError as e:
            logger.error(f"[FS] Failed to remove file {p}: {e}")
            return False
