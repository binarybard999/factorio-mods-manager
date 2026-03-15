"""
core/parser.py - Parse Factorio mod filenames and mod names
"""

import re
import logging

logger = logging.getLogger(__name__)


class ModParser:
    """
    Parser for Factorio mod filenames and mod names.
    Handles both:
    - Versioned filenames: aai-vehicles-hauler_0.7.3.zip
    - Unversioned filenames: aai-vehicles-hauler.zip
    - Simple mod names: aai-vehicles-hauler
    """
    
    # Regex pattern for versioned filename: captures mod name and version
    # Mod names can contain letters, numbers, hyphens, underscores
    # Versions follow the mod name after an underscore
    VERSIONED_PATTERN = r'^(?P<mod_name>.+?)_(?P<version>[0-9][0-9.]*[0-9])\.zip$'
    
    # Regex pattern for unversioned filename: just mod name
    UNVERSIONED_PATTERN = r'^(?P<mod_name>.+?)\.zip$'
    
    # Regex pattern for simple mod name (no extension)
    MOD_NAME_PATTERN = r'^(?P<mod_name>[a-zA-Z0-9\-_]+)$'
    
    @staticmethod
    def parse(filename_or_name):
        """
        Parse a mod filename or mod name and extract name and version.
        
        Handles:
        - 'aai-vehicles-hauler_0.7.3.zip' -> versioned filename
        - 'aai-vehicles-hauler.zip' -> unversioned filename
        - 'aai-vehicles-hauler' -> simple mod name
        
        Args:
            filename_or_name (str): Mod filename or name
            
        Returns:
            dict: {
                'input': str,
                'mod_name': str or None,
                'version': str or None,
                'valid': bool,
                'error': str or None,
                'is_filename': bool  # True if input was a .zip filename
            }
        """
        if not filename_or_name or not isinstance(filename_or_name, str):
            return {
                'input': str(filename_or_name),
                'mod_name': None,
                'version': None,
                'valid': False,
                'error': 'Invalid input: must be non-empty string',
                'is_filename': False
            }
        
        # Try versioned filename pattern first
        match = re.match(ModParser.VERSIONED_PATTERN, filename_or_name)
        if match:
            return {
                'input': filename_or_name,
                'mod_name': match.group('mod_name'),
                'version': match.group('version'),
                'valid': True,
                'error': None,
                'is_filename': True
            }
        
        # Try unversioned filename pattern
        match = re.match(ModParser.UNVERSIONED_PATTERN, filename_or_name)
        if match:
            return {
                'input': filename_or_name,
                'mod_name': match.group('mod_name'),
                'version': None,
                'valid': True,
                'error': None,
                'is_filename': True
            }
        
        # Try simple mod name pattern (no .zip extension)
        match = re.match(ModParser.MOD_NAME_PATTERN, filename_or_name)
        if match:
            return {
                'input': filename_or_name,
                'mod_name': match.group('mod_name'),
                'version': None,
                'valid': True,
                'error': None,
                'is_filename': False
            }
        
        return {
            'input': filename_or_name,
            'mod_name': None,
            'version': None,
            'valid': False,
            'error': f'Invalid format: {filename_or_name}',
            'is_filename': False
        }


# Convenience function
def parse_mod_filename(filename):
    """
    Parse a Factorio mod filename.
    
    Args:
        filename (str): The filename to parse
        
    Returns:
        dict: Parsing result with keys: input, mod_name, version, valid, error, is_filename
    """
    return ModParser.parse(filename)
