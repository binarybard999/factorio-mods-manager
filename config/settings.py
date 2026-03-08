"""
config/settings.py - Central configuration management
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


class Settings:
    """
    Central configuration class that loads settings from:
    1. user_settings.json (if user has customized settings)
    2. Environment variables from .env file (defaults)
    """
    
    def __init__(self, env_path=None):
        """
        Initialize settings by loading from user_settings.json and .env.
        
        Args:
            env_path (str, optional): Path to .env file. Defaults to .env in project root.
        """
        if env_path is None:
            env_path = Path(__file__).parent.parent / ".env"
        
        # Load .env file first (defaults)
        load_dotenv(env_path)
        
        # Load user settings if they exist
        user_settings = self._load_user_settings()
        
        # Mirror URLs
        if 'MIRROR_URLS' in user_settings:
            mirror_str = user_settings['MIRROR_URLS']
            self.mirror_urls = mirror_str.split(",") if isinstance(mirror_str, str) else [mirror_str]
        else:
            mirror_str = os.getenv("MIRROR_URLS", "https://mods-storage.re146.dev")
            self.mirror_urls = mirror_str.split(",")
        self.mirror_urls = [url.strip() for url in self.mirror_urls]
        
        # Retry settings
        self.max_retries = user_settings.get('MAX_RETRIES', int(os.getenv("MAX_RETRIES", "5")))
        self.request_timeout = user_settings.get('REQUEST_TIMEOUT', int(os.getenv("REQUEST_TIMEOUT", "120")))
        self.backoff_base = user_settings.get('BACKOFF_BASE', float(os.getenv("BACKOFF_BASE", "1.4")))
        
        # Delay settings
        self.random_delay_min = user_settings.get('RANDOM_DELAY_MIN', float(os.getenv("RANDOM_DELAY_MIN", "0.5")))
        self.random_delay_max = user_settings.get('RANDOM_DELAY_MAX', float(os.getenv("RANDOM_DELAY_MAX", "2.0")))
        
        # Concurrency
        self.max_workers = user_settings.get('MAX_WORKERS', int(os.getenv("MAX_WORKERS", "4")))
        
        # Directory paths
        self.download_dir = os.getenv("DOWNLOAD_DIR", "data/downloads")
        self.images_dir = os.getenv("IMAGES_DIR", "data/images")
        self.releases_dir = os.getenv("RELEASES_DIR", "data/releases")
        self.failed_dir = os.getenv("FAILED_DIR", "data/failed")
        
        # Output files
        self.csv_file = os.getenv("CSV_FILE", "factorio_mods.csv")
        
        # Feature flags - check user settings first
        if 'SAVE_IMAGES' in user_settings:
            self.save_images = user_settings['SAVE_IMAGES'] if isinstance(user_settings['SAVE_IMAGES'], bool) else str(user_settings['SAVE_IMAGES']).lower() == "true"
        else:
            self.save_images = os.getenv("SAVE_IMAGES", "true").lower() == "true"
        
        if 'SAVE_RELEASES' in user_settings:
            self.save_releases = user_settings['SAVE_RELEASES'] if isinstance(user_settings['SAVE_RELEASES'], bool) else str(user_settings['SAVE_RELEASES']).lower() == "true"
        else:
            self.save_releases = os.getenv("SAVE_RELEASES", "false").lower() == "true"
        
        if 'DOWNLOAD_ZIPS' in user_settings:
            self.download_zips = user_settings['DOWNLOAD_ZIPS'] if isinstance(user_settings['DOWNLOAD_ZIPS'], bool) else str(user_settings['DOWNLOAD_ZIPS']).lower() == "true"
        else:
            self.download_zips = os.getenv("DOWNLOAD_ZIPS", "true").lower() == "true"
        
        if 'SAVE_CHANGELOG' in user_settings:
            self.save_changelog = user_settings['SAVE_CHANGELOG'] if isinstance(user_settings['SAVE_CHANGELOG'], bool) else str(user_settings['SAVE_CHANGELOG']).lower() == "true"
        else:
            self.save_changelog = os.getenv("SAVE_CHANGELOG", "false").lower() == "true"
    
    def _load_user_settings(self):
        """
        Load user-customized settings from config/user_settings.json.
        
        Returns:
            dict: User settings, or empty dict if file doesn't exist
        """
        user_settings_file = Path(__file__).parent / 'user_settings.json'
        
        if not user_settings_file.exists():
            return {}
        
        try:
            with open(user_settings_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not load user settings: {e}")
            return {}
    
    def validate(self):
        """
        Validate settings configuration.
        
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        if not self.mirror_urls:
            return False, "MIRROR_URLS not configured"
        
        if self.max_retries < 1:
            return False, "MAX_RETRIES must be at least 1"
        
        if self.request_timeout < 1:
            return False, "REQUEST_TIMEOUT must be at least 1"
        
        if self.max_workers < 1:
            return False, "MAX_WORKERS must be at least 1"
        
        return True, ""
    
    def __repr__(self):
        """String representation for debugging."""
        return (
            f"Settings(mirrors={len(self.mirror_urls)}, "
            f"retries={self.max_retries}, "
            f"timeout={self.request_timeout}, "
            f"workers={self.max_workers})"
        )


# Global settings instance
_settings = None


def get_settings(env_path=None):
    """
    Get or create the global settings instance.
    
    Args:
        env_path (str, optional): Path to .env file for initialization.
        
    Returns:
        Settings: The global settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings(env_path)
    return _settings
