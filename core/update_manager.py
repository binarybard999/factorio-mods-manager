"""
core/update_manager.py - Handle mod updates and version checking
"""

import logging
from pathlib import Path
from typing import Dict, Tuple, Optional

from services.factorio_api import FactorioAPI
from core.mod_scanner import ModScanner
from services.downloader import Downloader
from utils.helpers import safe_filename
from config.settings import get_settings

logger = logging.getLogger(__name__)


class UpdateManager:
    """
    Manages checking for mod updates and handling downloads with backups.
    """
    
    def __init__(self, settings=None):
        """
        Initialize the update manager.
        
        Args:
            settings (Settings, optional): Configuration object
        """
        self.settings = settings or get_settings()
        self.api = FactorioAPI(self.settings)
        self.downloader = Downloader(self.settings)
    
    def check_and_update_mods(self, mods_folder: str) -> Dict:
        """
        Check mods in a folder for updates and download new versions if available.
        
        Args:
            mods_folder (str): Path to the mods folder
            
        Returns:
            dict: Summary with keys:
                - total: total mods found
                - up_to_date: mods already at latest version
                - updated: mods that were updated
                - failed: mods that failed to update
                - errors: list of error messages from scanning
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"[UPDATE] Starting update check for mods folder: {mods_folder}")
        logger.info(f"{'='*80}\n")
        
        # Scan the folder for mods
        mods, scan_errors = ModScanner.scan_mods_folder(mods_folder)
        
        if scan_errors:
            logger.warning(f"[UPDATE] Scan errors: {scan_errors}")
        
        summary = {
            'total': len(mods),
            'up_to_date': 0,
            'updated': 0,
            'failed': 0,
            'errors': scan_errors,
            'details': []
        }
        
        if not mods:
            logger.warning(f"[UPDATE] No mods found in folder")
            return summary
        
        # Create backup folder
        backup_ok, backup_path = ModScanner.create_backup_folder(mods_folder)
        if not backup_ok:
            logger.error(f"[UPDATE] Could not create backup folder: {backup_path}")
            summary['errors'].append(f"Backup folder creation failed: {backup_path}")
            return summary
        
        logger.info(f"[UPDATE] Processing {len(mods)} mods")
        
        # Check each mod for updates
        for i, mod in enumerate(mods, 1):
            mod_name = mod['mod_name']
            current_version = mod['version']
            mod_path = mod['full_path']
            
            status = self._process_single_mod(
                mod_name, 
                current_version, 
                mod_path, 
                backup_path,
                mods_folder
            )
            
            detail = {
                'mod_name': mod_name,
                'current_version': current_version,
                'status': status['status'],
                'latest_version': status.get('latest_version'),
                'message': status.get('message', '')
            }
            summary['details'].append(detail)
            
            if status['status'] == 'up_to_date':
                summary['up_to_date'] += 1
                logger.info(f"[UPDATE] [{i}/{len(mods)}] UP_TO_DATE: {mod_name} v{current_version}")
            elif status['status'] == 'updated':
                summary['updated'] += 1
                logger.info(f"[UPDATE] [{i}/{len(mods)}] UPDATED: {mod_name} v{current_version} -> v{status['latest_version']}")
            else:  # failed
                summary['failed'] += 1
                logger.error(f"[UPDATE] [{i}/{len(mods)}] FAILED: {mod_name} - {status.get('message', 'Unknown error')}")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"[UPDATE] Update check complete")
        logger.info(f"[UPDATE] Summary: {summary['up_to_date']} up-to-date, {summary['updated']} updated, {summary['failed']} failed")
        logger.info(f"{'='*80}\n")
        
        return summary
    
    def _process_single_mod(
        self, 
        mod_name: str, 
        current_version: Optional[str], 
        mod_path: str, 
        backup_folder: str,
        mods_folder: str
    ) -> Dict:
        """
        Check and update a single mod.
        
        Args:
            mod_name (str): Name of the mod
            current_version (Optional[str]): Current version (None if unknown)
            mod_path (str): Full path to the mod ZIP file
            backup_folder (str): Path to backup folder
            mods_folder (str): Path to the mods folder (for saving downloads)
            
        Returns:
            dict: Status with keys: status, latest_version, message
                status: 'up_to_date', 'updated', or 'failed'
        """
        logger.debug(f"[UPDATE] Checking {mod_name} (current: {current_version or 'unknown'})")
        
        # Fetch mod info from API
        mod_data = self.api.get_mod_full(mod_name)
        if not mod_data:
            return {
                'status': 'failed',
                'message': f"Could not fetch mod data from API"
            }
        
        # Get latest version
        releases = mod_data.get('releases', []) or []
        if not releases:
            return {
                'status': 'failed',
                'message': 'No releases found for mod'
            }
        
        latest_version = releases[-1].get('version', '')
        if not latest_version:
            return {
                'status': 'failed',
                'message': 'Could not determine latest version'
            }
        
        logger.debug(f"[UPDATE] {mod_name}: current={current_version}, latest={latest_version}")
        
        # Prepare destination path in the mods folder
        destination = Path(mods_folder) / f"{safe_filename(mod_name)}_{latest_version}.zip"
        
        # If no current version specified, treat as needs update
        if not current_version:
            logger.info(f"[UPDATE] {mod_name}: No version specified, will download latest ({latest_version})")
            
            # Download the mod to the mods folder
            success, path = self.downloader.download_mod_zip(
                mod_name, 
                latest_version,
                destination=str(destination)
            )
            if success and path:
                return {
                    'status': 'updated',
                    'latest_version': latest_version,
                    'message': f'Downloaded {mod_name} v{latest_version} to folder'
                }
            else:
                return {
                    'status': 'failed',
                    'latest_version': latest_version,
                    'message': f'Failed to download {mod_name} v{latest_version}'
                }
        
        # Compare versions
        if self._compare_versions(current_version, latest_version) >= 0:
            # Current version is up-to-date
            return {
                'status': 'up_to_date',
                'latest_version': latest_version,
                'message': f'{mod_name} is at latest version'
            }
        
        # Update is available - download new version to the mods folder
        logger.info(f"[UPDATE] Update available for {mod_name}: {current_version} -> {latest_version}")
        
        # Download new version to the mods folder
        success, download_path = self.downloader.download_mod_zip(
            mod_name, 
            latest_version,
            destination=str(destination)
        )
        if not success:
            return {
                'status': 'failed',
                'latest_version': latest_version,
                'message': f'Failed to download {mod_name} v{latest_version}'
            }
        
        # Backup old version
        backup_ok, backup_result = ModScanner.move_mod_to_backup(mod_path, backup_folder)
        if not backup_ok:
            logger.error(f"[UPDATE] Failed to backup old version: {backup_result}")
            # Don't fail completely, the new version is downloaded
        
        return {
            'status': 'updated',
            'latest_version': latest_version,
            'message': f'Updated {mod_name} v{current_version} -> v{latest_version}'
        }
    
    @staticmethod
    def _compare_versions(ver1: str, ver2: str) -> int:
        """
        Compare two version strings.
        
        Args:
            ver1 (str): First version (e.g., '1.2.3')
            ver2 (str): Second version (e.g., '1.2.4')
            
        Returns:
            int: -1 if ver1 < ver2, 0 if equal, 1 if ver1 > ver2
        """
        try:
            v1_parts = [int(x) for x in ver1.split('.')]
            v2_parts = [int(x) for x in ver2.split('.')]
            
            # Pad with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            if v1_parts > v2_parts:
                return 1
            elif v1_parts < v2_parts:
                return -1
            else:
                return 0
        except (ValueError, AttributeError):
            # If parsing fails, compare as strings
            if ver1 > ver2:
                return 1
            elif ver1 < ver2:
                return -1
            else:
                return 0
    
    def close(self):
        """Close API session."""
        if self.api:
            try:
                self.api.close()
            except Exception as e:
                logger.error(f"Error closing API: {e}")
