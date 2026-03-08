"""
storage/csv_store.py - CSV metadata storage
"""

import csv
import logging
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)


class CSVStore:
    """
    Handles CSV file operations for storing mod metadata.
    Thread-safe with locking for concurrent writes.
    """
    
    # CSV header fields
    HEADER_BASIC = [
        "filename",
        "local_version",
        "title",
        "summary",
        "owner",
        "latest_version",
        "latest_dependencies",
        "downloads",
        "homepage",
        "category",
        "tags",
        "created_at",
        "updated_at",
        "license"
    ]
    
    HEADER_WITH_CHANGELOG = HEADER_BASIC + ["changelog"]
    
    def __init__(self, csv_path, include_changelog=False):
        """
        Initialize the CSV store.
        
        Args:
            csv_path (str or Path): Path to CSV file
            include_changelog (bool): Whether to include changelog column
        """
        self.csv_path = Path(csv_path)
        self.include_changelog = include_changelog
        self.lock = Lock()
        self.header = self.HEADER_WITH_CHANGELOG if include_changelog else self.HEADER_BASIC
    
    def init_file(self):
        """
        Initialize the CSV file with header if it doesn't exist.
        
        Returns:
            bool: True if initialized, False if already existed
        """
        if self.csv_path.exists():
            logger.debug(f"[CSV] File already exists: {self.csv_path}")
            return False
        
        try:
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(self.header)
            logger.info(f"[CSV] Initialized: {self.csv_path}")
            return True
        except IOError as e:
            logger.error(f"[CSV] Failed to initialize: {e}")
            raise
    
    def append_row(self, row_dict):
        """
        Append a row to the CSV file. Thread-safe.
        
        Args:
            row_dict (dict): Dictionary with column names as keys
            
        Returns:
            bool: True if successful
        """
        with self.lock:
            try:
                # Ensure file exists first
                if not self.csv_path.exists():
                    self.init_file()
                
                with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.header, restval='')
                    writer.writerow(row_dict)
                
                logger.debug(f"[CSV] Appended row for {row_dict.get('filename', 'unknown')}")
                return True
            except IOError as e:
                logger.error(f"[CSV] Failed to append row: {e}")
                return False
    
    def read_rows(self):
        """
        Read all rows from the CSV file.
        
        Returns:
            list: List of dictionaries, one per row
        """
        if not self.csv_path.exists():
            return []
        
        try:
            rows = []
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            logger.debug(f"[CSV] Read {len(rows)} rows")
            return rows
        except IOError as e:
            logger.error(f"[CSV] Failed to read rows: {e}")
            return []
    
    def get_processed_mods(self):
        """
        Get set of already-processed mod filenames.
        
        Returns:
            set: Set of filenames that have been processed
        """
        rows = self.read_rows()
        return {row.get('filename', '') for row in rows if row.get('filename')}
