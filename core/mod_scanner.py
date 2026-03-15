"""
core/mod_scanner.py - Scan and detect mods in a folder
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class ModScanner:
    """
    Scans a folder for existing mod ZIP files and extracts mod information.
    Handles both versioned (mod_name_version.zip) and unversioned mods.
    """
    
    # Pattern for versioned mods: mod_name_version.zip
    VERSIONED_PATTERN = r'^(?P<mod_name>.+?)_(?P<version>[0-9][0-9.]*[0-9])\.zip$'
    
    # Pattern for simple mods without versions
    SIMPLE_PATTERN = r'^(?P<mod_name>.+?)\.zip$'
    
    @staticmethod
    def scan_mods_folder(folder_path: str) -> Tuple[List[Dict], List[str]]:
        """
        Scan a folder for mod ZIP files and extract mod information.
        
        Args:
            folder_path (str): Path to the mods folder
            
        Returns:
            tuple: (mods_list, errors)
                mods_list: List of dicts with keys: mod_name, version (or None), filename, full_path
                errors: List of error messages
        """
        folder = Path(folder_path)
        errors = []
        mods = []
        
        if not folder.exists():
            return [], [f"Folder does not exist: {folder_path}"]
        
        if not folder.is_dir():
            return [], [f"Not a directory: {folder_path}"]
        
        logger.info(f"[SCANNER] Scanning folder: {folder}")
        
        # Find all .zip files
        zip_files = list(folder.glob('*.zip'))
        logger.info(f"[SCANNER] Found {len(zip_files)} ZIP files")
        
        for zip_file in zip_files:
            filename = zip_file.name
            
            # Try versioned pattern first
            match = re.match(ModScanner.VERSIONED_PATTERN, filename)
            if match:
                mod_info = {
                    'mod_name': match.group('mod_name'),
                    'version': match.group('version'),
                    'filename': filename,
                    'full_path': str(zip_file)
                }
                mods.append(mod_info)
                logger.debug(f"[SCANNER] Versioned mod: {mod_info['mod_name']} v{mod_info['version']}")
                continue
            
            # Try simple pattern (just mod name)
            match = re.match(ModScanner.SIMPLE_PATTERN, filename)
            if match:
                mod_info = {
                    'mod_name': match.group('mod_name'),
                    'version': None,
                    'filename': filename,
                    'full_path': str(zip_file)
                }
                mods.append(mod_info)
                logger.debug(f"[SCANNER] Unversioned mod: {mod_info['mod_name']}")
                continue
            
            # Couldn't parse this file
            error_msg = f"Could not parse filename: {filename}"
            errors.append(error_msg)
            logger.warning(f"[SCANNER] {error_msg}")
        
        logger.info(f"[SCANNER] Scanned complete: {len(mods)} mods found, {len(errors)} errors")
        return mods, errors
    
    @staticmethod
    def create_backup_folder(mods_folder: str) -> Tuple[bool, str]:
        """
        Create old_mods backup folder if it doesn't exist.
        
        Args:
            mods_folder (str): Path to the mods folder
            
        Returns:
            tuple: (success, path_or_error)
        """
        mods_path = Path(mods_folder)
        backup_path = mods_path / 'old_mods'
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[SCANNER] Backup folder ready: {backup_path}")
            return True, str(backup_path)
        except OSError as e:
            error = f"Failed to create backup folder: {e}"
            logger.error(f"[SCANNER] {error}")
            return False, error
    
    @staticmethod
    def move_mod_to_backup(mod_path: str, backup_folder: str) -> Tuple[bool, str]:
        """
        Move a mod ZIP file to the backup folder.
        
        Args:
            mod_path (str): Full path to the mod ZIP file
            backup_folder (str): Path to backup folder
            
        Returns:
            tuple: (success, new_path_or_error)
        """
        try:
            source = Path(mod_path)
            if not source.exists():
                return False, f"File not found: {mod_path}"
            
            dest = Path(backup_folder) / source.name
            
            # Handle name conflicts
            counter = 1
            stem = dest.stem
            while dest.exists():
                dest = dest.parent / f"{stem}_old_{counter}.zip"
                counter += 1
            
            source.rename(dest)
            logger.info(f"[SCANNER] Moved to backup: {source.name} -> {dest.name}")
            return True, str(dest)
        except OSError as e:
            error = f"Failed to move mod to backup: {e}"
            logger.error(f"[SCANNER] {error}")
            return False, error
