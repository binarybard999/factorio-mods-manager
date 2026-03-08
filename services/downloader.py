"""
services/downloader.py - File download handling with mirror fallback
"""

import logging
import os
from pathlib import Path
from requests.exceptions import RequestException
import requests

from config.settings import get_settings
from services.retry import backoff_sleep, random_delay
from utils.helpers import safe_filename


logger = logging.getLogger(__name__)


class Downloader:
    """
    Handles downloading files (mod ZIPs, images, etc.) with retry logic
    and mirror fallback support.
    """
    
    def __init__(self, settings=None):
        """
        Initialize the downloader.
        
        Args:
            settings (Settings, optional): Configuration object. Uses global if None.
        """
        self.settings = settings or get_settings()
        self.session = requests.Session()
    
    def download_file(self, url, destination, description="file"):
        """
        Download a file with retry logic and streaming.
        
        Args:
            url (str): URL to download from
            destination (str or Path): Where to save the file
            description (str): Description for logging
            
        Returns:
            bool: True if successful, False otherwise
        """
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Use tuple timeout: (connect_timeout, read_timeout)
        # Connect: 10 seconds, Read: 120 seconds (for large files)
        timeout = (10, self.settings.request_timeout)
        
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                logger.debug(f"[DL] {description} from {url} (attempt {attempt}/{self.settings.max_retries})")
                
                response = self.session.get(
                    url,
                    stream=True,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    # Stream download to avoid loading entire file in memory
                    with open(destination, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    logger.info(f"[DL] Saved {description} to {destination}")
                    random_delay(self.settings)
                    return True
                else:
                    logger.warning(f"[DL] HTTP {response.status_code} for {url}")
            
            except RequestException as e:
                logger.warning(f"[DL] Download error (attempt {attempt}): {e}")
            
            except Exception as e:
                logger.warning(f"[DL] Unexpected error (attempt {attempt}): {e}")
            
            # Backoff before retry
            if attempt < self.settings.max_retries:
                backoff_sleep(attempt, self.settings)
        
        logger.error(f"[DL] Failed to download {description} after {self.settings.max_retries} attempts")
        return False
    
    def download_mod_zip(self, mod_name, version, destination=None):
        """
        Download a mod ZIP file using mirror servers.
        
        Attempts mirrors in order, then falls back to official portal.
        
        Args:
            mod_name (str): Name of the mod
            version (str): Version of the mod
            destination (str or Path, optional): Where to save. Auto-generated if None.
            
        Returns:
            tuple: (success: bool, path: str or None)
        """
        if destination is None:
            destination = Path(self.settings.download_dir) / f"{safe_filename(mod_name)}_{version}.zip"
        
        destination = Path(destination)
        
        # Try each mirror
        for mirror in self.settings.mirror_urls:
            url = f"{mirror}/{mod_name}/{version}.zip"
            logger.debug(f"[ZIP] Trying mirror: {url}")
            
            success = self.download_file(url, destination, f"mod {mod_name} v{version}")
            if success:
                return True, str(destination)
        
        # Fallback: Try official Factorio portal (requires download_url from API)
        logger.debug(f"[ZIP] All mirrors failed, would need download_url from API for fallback")
        return False, None
    
    def download_image(self, url, mod_name, destination=None):
        """
        Download a mod image (thumbnail or full-size).
        
        Args:
            url (str): Image URL
            mod_name (str): Name of the mod (for filename)
            destination (str or Path, optional): Where to save. Auto-generated if None.
            
        Returns:
            tuple: (success: bool, path: str or None)
        """
        if destination is None:
            destination = Path(self.settings.images_dir) / f"{safe_filename(mod_name)}.png"
        
        destination = Path(destination)
        
        success = self.download_file(url, destination, f"image for {mod_name}")
        
        if success:
            return True, str(destination)
        return False, None
    
    def close(self):
        """Close the HTTP session."""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
