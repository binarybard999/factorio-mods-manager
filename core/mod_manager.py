"""
core/mod_manager.py - Main orchestration logic for mod processing
"""

import logging
from datetime import datetime
from pathlib import Path

from config.settings import get_settings
from core.parser import parse_mod_filename
from services.factorio_api import FactorioAPI
from services.downloader import Downloader
from storage.csv_store import CSVStore
from storage.file_store import FileStore
from utils.helpers import timestamp_filename

logger = logging.getLogger(__name__)


class ModManager:
    """
    Main application logic that orchestrates:
    - Parsing mod filenames
    - Fetching mod metadata from API
    - Downloading files
    - Storing metadata in CSV
    - Tracking failures
    """
    
    def __init__(self, settings=None):
        """
        Initialize the mod manager.
        
        Args:
            settings (Settings, optional): Configuration object. Uses global if None.
        """
        self.settings = settings or get_settings()
        self.api = FactorioAPI(self.settings)
        self.downloader = Downloader(self.settings)
        self.csv_store = CSVStore(self.settings.csv_file, self.settings.save_changelog)
        
        self.failed_mods = []
        self.processed_count = 0
        self.skipped_count = 0
        self.failed_count = 0
        
        # Ensure all directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        FileStore.ensure_dir(self.settings.download_dir)
        FileStore.ensure_dir(self.settings.images_dir)
        FileStore.ensure_dir(self.settings.releases_dir)
        FileStore.ensure_dir(self.settings.failed_dir)
    
    def process_mod(self, filename):
        """
        Process a single mod file or mod name.
        
        Workflow:
        1. Parse filename/name to extract mod name and version (version optional)
        2. Fetch metadata from API
        3. If version not provided, use latest from API
        4. Save CSV row
        5. Download images if enabled
        6. Download mod ZIP if enabled
        7. Save release information if enabled
        
        Args:
            filename (str): Mod filename or name:
                - 'aai-vehicles-hauler_0.7.3.zip' -> versioned filename
                - 'aai-vehicles-hauler.zip' -> unversioned filename
                - 'aai-vehicles-hauler' -> simple mod name
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"[PROCESS] Starting: {filename}")
        
        # Parse filename/name
        parsed = parse_mod_filename(filename)
        if not parsed['valid']:
            logger.error(f"[PARSE ERROR] {parsed['error']}")
            self.failed_mods.append(filename)
            self.failed_count += 1
            return False
        
        mod_name = parsed['mod_name']
        local_version = parsed['version']
        
        logger.debug(f"[PROCESS] Parsed: mod_name={mod_name}, version={local_version}, is_filename={parsed.get('is_filename', False)}")
        
        # Fetch metadata
        logger.debug(f"[API] Fetching metadata for {mod_name}")
        mod_data = self.api.get_mod_full(mod_name)
        
        if not mod_data:
            logger.error(f"[API ERROR] Could not fetch metadata for {mod_name}")
            self.failed_mods.append(filename)
            self.failed_count += 1
            return False
        
        # Extract key information
        title = mod_data.get('title', '') or ''
        summary = mod_data.get('summary', '') or ''
        description = mod_data.get('description', '') or ''
        owner = mod_data.get('owner', '') or ''
        homepage = mod_data.get('homepage', '') or ''
        category = mod_data.get('category', '') or ''
        tags = ', '.join(mod_data.get('tags', []) or [])
        downloads = mod_data.get('downloads_count', '')
        created_at = mod_data.get('created_at', '')
        updated_at = mod_data.get('updated_at', '')
        
        license_info = mod_data.get('license') or {}
        license_title = license_info.get('title', '') if isinstance(license_info, dict) else ''
        
        # Get latest release info
        releases = mod_data.get('releases', []) or []
        latest = releases[-1] if releases else {}
        latest_version = latest.get('version', '')
        
        # Extract dependencies from latest release
        info_json = latest.get('info_json', {}) or {}
        dependencies = info_json.get('dependencies', []) or []
        latest_deps = '; '.join(dependencies)
        
        download_url = latest.get('download_url')  # For official portal fallback
        
        # Get thumbnail/images
        images = mod_data.get('images', []) or []
        image_urls = [img.get('url') for img in images if isinstance(img, dict) and img.get('url')]
        thumbnail = image_urls[0] if image_urls else (
            f"https://mods.factorio.com{mod_data.get('thumbnail')}" 
            if mod_data.get('thumbnail') else ''
        )
        
        # Prepare CSV row
        csv_row = {
            'filename': filename,
            'local_version': local_version,
            'title': title,
            'summary': summary,
            'owner': owner,
            'latest_version': latest_version,
            'latest_dependencies': latest_deps,
            'downloads': downloads,
            'homepage': homepage,
            'category': category,
            'tags': tags,
            'created_at': created_at,
            'updated_at': updated_at,
            'license': license_title
        }
        
        if self.settings.save_changelog:
            changelog = mod_data.get('changelog', '') or ''
            csv_row['changelog'] = changelog
        
        # Write CSV row
        if not self.csv_store.append_row(csv_row):
            logger.error(f"[CSV ERROR] Failed to write row for {mod_name}")
            self.failed_mods.append(filename)
            self.failed_count += 1
            return False
        
        logger.info(f"[CSV] Saved metadata for {mod_name}")
        
        # Download thumbnail if enabled
        if self.settings.save_images and thumbnail:
            logger.debug(f"[IMAGE] Downloading thumbnail for {mod_name}")
            success, path = self.downloader.download_image(thumbnail, mod_name)
            if success:
                logger.info(f"[IMAGE] Saved image: {path}")
        
        # Save release information if enabled
        if self.settings.save_releases and releases:
            self._save_releases(mod_name, releases)
        
        # Download mod ZIP if enabled
        if self.settings.download_zips:
            final_version = latest_version or local_version
            logger.debug(f"[ZIP] Downloading {mod_name} {final_version}")
            
            success, path = self.downloader.download_mod_zip(mod_name, final_version)
            
            if not success and download_url:
                # Fallback to official portal
                logger.debug(f"[ZIP] Mirror failed, trying official portal")
                fallback_url = f"https://mods.factorio.com{download_url}"
                success, path = self.downloader.download_file(
                    fallback_url,
                    Path(self.settings.download_dir) / f"{mod_name}_{final_version}.zip",
                    f"mod {mod_name} ZIP"
                ), None
            
            if success or path:
                logger.info(f"[ZIP] Downloaded: {path or mod_name} {final_version}")
            else:
                logger.warning(f"[ZIP] Could not download {mod_name} {final_version}")
                self.failed_mods.append(filename)
                self.failed_count += 1
                return False
        
        self.processed_count += 1
        logger.info(f"[SUCCESS] Processed: {filename}")
        return True
    
    def _save_releases(self, mod_name, releases):
        """
        Save release information to a CSV file.
        
        NOTE: This function saves ALL releases for the mod to provide version history.
        The download and version info in the main CSV uses only the LATEST version.
        
        Args:
            mod_name (str): Name of the mod
            releases (list): List of release dictionaries (all versions)
        """
        import csv
        from utils.helpers import safe_filename
        
        release_file = Path(self.settings.releases_dir) / f"releases_{safe_filename(mod_name)}.csv"
        
        try:
            release_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Sort releases by date (most recent first) for easy viewing
            sorted_releases = sorted(
                releases,
                key=lambda x: x.get('released_at', ''),
                reverse=True
            )
            
            with open(release_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['version', 'file_name', 'released_at', 'sha1', 'dependencies', 'is_latest'])
                
                # Mark the latest (first in sorted list) as latest
                for idx, release in enumerate(sorted_releases):
                    info_json = release.get('info_json', {}) or {}
                    deps_list = info_json.get('dependencies', []) or []
                    deps_str = '; '.join(deps_list)
                    is_latest = 'YES' if idx == 0 else ''
                    
                    writer.writerow([
                        release.get('version', ''),
                        release.get('file_name', ''),
                        release.get('released_at', ''),
                        release.get('sha1', ''),
                        deps_str,
                        is_latest
                    ])
            
            logger.info(f"[RELEASES] Saved {len(sorted_releases)} versions for {mod_name}: {release_file}")
        except IOError as e:
            logger.error(f"[RELEASES] Failed to save for {mod_name}: {e}")
    
    def process_mod_list(self, mod_filenames, progress_callback=None):
        """
        Process a list of mod filenames.
        
        Args:
            mod_filenames (list): List of mod filenames
            progress_callback (callable, optional): Callback for progress updates
                Called with (current, total, message)
            
        Returns:
            dict: Summary with counts and failed list
        """
        total = len(mod_filenames)
        self.processed_count = 0
        self.failed_count = 0
        self.failed_mods = []
        
        # Initialize CSV file
        self.csv_store.init_file()
        
        for i, filename in enumerate(mod_filenames):
            current = i + 1
            if progress_callback:
                progress_callback(current, total, f"Processing {filename}")
            
            try:
                self.process_mod(filename)
            except Exception as e:
                logger.error(f"[ERROR] Exception processing {filename}: {e}")
                self.failed_mods.append(filename)
                self.failed_count += 1
        
        # Save failed list
        if self.failed_mods:
            self._save_failed_list()
        
        return {
            'total': total,
            'processed': self.processed_count,
            'failed': self.failed_count,
            'failed_mods': self.failed_mods,
            'csv_file': self.settings.csv_file
        }
    
    def _save_failed_list(self):
        """Save list of failed mods to file."""
        timestamp = timestamp_filename()
        failed_file = Path(self.settings.failed_dir) / f"failed_{timestamp}.txt"
        
        try:
            content = '\n'.join(self.failed_mods) + '\n'
            FileStore.write_file(failed_file, content)
            logger.info(f"[FAILED] Saved failed mods list: {failed_file}")
        except IOError as e:
            logger.error(f"[FAILED] Could not save failed list: {e}")
    
    def close(self):
        """Close API and downloader sessions."""
        self.api.close()
        self.downloader.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
