"""
core/parser.py - Parse Factorio mod filenames
"""

import re


class ModParser:
    """
    Parser for Factorio mod filenames.
    Extracts mod name and version from filenames like: aai-vehicles-hauler_0.7.3.zip
    """
    
    # Regex pattern: captures mod name and version
    # Mod names can contain letters, numbers, hyphens, underscores
    # Versions follow the mod name after an underscore
    FILENAME_PATTERN = r'^(?P<mod_name>.+?)_(?P<version>[0-9][0-9.]*[0-9])\.zip$'
    
    @staticmethod
    def parse(filename):
        """
        Parse a mod filename and extract name and version.
        
        Args:
            filename (str): Mod filename (e.g., 'aai-vehicles-hauler_0.7.3.zip')
            
        Returns:
            dict: {
                'filename': str,
                'mod_name': str,
                'version': str,
                'valid': bool,
                'error': str or None
            }
        """
        match = re.match(ModParser.FILENAME_PATTERN, filename)
        
        if not match:
            return {
                'filename': filename,
                'mod_name': None,
                'version': None,
                'valid': False,
                'error': f'Invalid filename format: {filename}'
            }
        
        return {
            'filename': filename,
            'mod_name': match.group('mod_name'),
            'version': match.group('version'),
            'valid': True,
            'error': None
        }


# Convenience function
def parse_mod_filename(filename):
    """
    Parse a Factorio mod filename.
    
    Args:
        filename (str): The filename to parse
        
    Returns:
        dict: Parsing result
    """
    return ModParser.parse(filename)
