"""
utils/helpers.py - Generic utility functions
"""

import re
import os
from datetime import datetime
from pathlib import Path


def safe_filename(filename):
    """
    Convert a string to a safe filename by replacing invalid characters.
    
    Args:
        filename (str): The filename to sanitize
        
    Returns:
        str: Sanitized filename safe for filesystem use
    """
    return re.sub(r'[^A-Za-z0-9._\-]', '_', filename)


def timestamp():
    """
    Get current timestamp in ISO format.
    
    Returns:
        str: Current timestamp (YYYY-MM-DD HH:MM:SS)
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def timestamp_filename():
    """
    Get current timestamp suitable for use in filenames.
    
    Returns:
        str: Timestamp in format YYYY-MM-DD_HH-MM-SS
    """
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def ensure_dir(path):
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path (str or Path): Directory path
        
    Returns:
        Path: The directory path as a Path object
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def file_exists(path):
    """
    Check if a file exists.
    
    Args:
        path (str or Path): File path
        
    Returns:
        bool: True if file exists
    """
    return Path(path).exists()


def remove_file(path):
    """
    Remove a file if it exists.
    
    Args:
        path (str or Path): File path
        
    Returns:
        bool: True if file was removed, False if it didn't exist
    """
    try:
        Path(path).unlink()
        return True
    except FileNotFoundError:
        return False
