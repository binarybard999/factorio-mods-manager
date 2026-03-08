"""
services/retry.py - Retry and delay logic for resilient API/download operations
"""

import time
import random
from config.settings import get_settings


def backoff_sleep(attempt, settings=None):
    """
    Sleep with exponential backoff plus randomization.
    
    Args:
        attempt (int): Attempt number (1-indexed)
        settings (Settings, optional): Configuration object. Uses global if None.
    """
    if settings is None:
        settings = get_settings()
    
    # Exponential backoff: base^attempt + small random jitter
    backoff_time = (settings.backoff_base ** attempt) + random.uniform(0, 0.5)
    time.sleep(backoff_time)


def random_delay(settings=None):
    """
    Apply a random delay to avoid rate limiting and detection.
    
    Args:
        settings (Settings, optional): Configuration object. Uses global if None.
    """
    if settings is None:
        settings = get_settings()
    
    delay = random.uniform(settings.random_delay_min, settings.random_delay_max)
    time.sleep(delay)
