"""
services/factorio_api.py - Factorio Mod Portal API communication
"""

import logging
import requests
from requests.exceptions import RequestException
from config.settings import get_settings
from services.retry import backoff_sleep, random_delay


logger = logging.getLogger(__name__)


class FactorioAPI:
    """
    Client for communicating with the Factorio Mod Portal API.
    Handles metadata fetching with retry logic.
    """
    
    BASE_URL = "https://mods.factorio.com/api/mods"
    
    def __init__(self, settings=None):
        """
        Initialize the API client.
        
        Args:
            settings (Settings, optional): Configuration object. Uses global if None.
        """
        self.settings = settings or get_settings()
        self.session = requests.Session()
    
    def get_mod_full(self, mod_name):
        """
        Fetch full mod metadata from the Factorio Mod Portal.
        
        Args:
            mod_name (str): Name of the mod (e.g., 'aai-vehicles-hauler')
            
        Returns:
            dict: Mod metadata or None if failed
        """
        url = f"{self.BASE_URL}/{mod_name}/full"
        
        for attempt in range(1, self.settings.max_retries + 1):
            try:
                logger.debug(f"[API] GET {url} (attempt {attempt}/{self.settings.max_retries})")
                
                response = self.session.get(
                    url,
                    timeout=self.settings.request_timeout
                )
                
                if response.status_code == 200:
                    logger.debug(f"[API] Success: {mod_name}")
                    random_delay(self.settings)  # Avoid rate limiting
                    return response.json()
                else:
                    logger.warning(f"[API] HTTP {response.status_code} for {mod_name}")
            
            except RequestException as e:
                logger.warning(f"[API] Request error: {e}")
            
            # Backoff before retry
            if attempt < self.settings.max_retries:
                backoff_sleep(attempt, self.settings)
        
        logger.error(f"[API] Failed to fetch {mod_name} after {self.settings.max_retries} attempts")
        return None
    
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
