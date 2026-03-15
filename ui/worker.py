"""
ui/worker.py - Background worker for processing mods without blocking GUI
"""

import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QObject, Signal, QThread, QCoreApplication
from PySide6.QtWidgets import QApplication

from config.settings import get_settings
from core.mod_manager import ModManager
from core.mod_scanner import ModScanner


logger = logging.getLogger(__name__)


class ModProcessorWorker(QObject):
    """
    Worker that runs mod processing in background threads.
    Emits signals for GUI updates.
    """
    
    # Signals
    progress_updated = Signal(int, int, str)  # current, total, message
    log_message = Signal(str)  # log message
    status_updated = Signal(str)  # detailed operation status
    finished = Signal(dict)  # summary dict
    error_occurred = Signal(str)  # error message
    
    def __init__(self, settings=None):
        """
        Initialize the worker.
        
        Args:
            settings (Settings, optional): Configuration object
        """
        super().__init__()
        self.settings = settings or get_settings()
        self.mod_manager = None
        self.should_stop = False
    
    def run(self, mod_filenames, use_multithreading=False):
        """
        Process a list of mods.
        
        Args:
            mod_filenames (list): List of mod filenames to process
            use_multithreading (bool): Whether to use thread pool
        """
        self.should_stop = False
        logger.info(f"\n{'='*80}")
        logger.info(f"[WORKER] Starting processing of {len(mod_filenames)} mods")
        logger.info(f"[WORKER] Multithreading: {use_multithreading}")
        logger.info(f"{'='*80}\n")
        
        try:
            self.mod_manager = ModManager(self.settings)
            logger.info(f"[WORKER] ModManager initialized successfully")
            
            if use_multithreading:
                logger.info(f"[WORKER] Using multithreaded mode with {self.settings.max_workers} workers")
                self._run_multithreaded(mod_filenames)
            else:
                logger.info(f"[WORKER] Using sequential (single-threaded) mode")
                self._run_sequential(mod_filenames)
        
        except Exception as e:
            logger.error(f"[WORKER ERROR] Exception in run(): {e}", exc_info=True)
            logger.error(f"[WORKER ERROR] Traceback:\n{traceback.format_exc()}")
            self.error_occurred.emit(str(e))
        
        finally:
            logger.info(f"[WORKER] Cleaning up resources")
            if self.mod_manager:
                try:
                    self.mod_manager.close()
                    logger.info(f"[WORKER] ModManager closed successfully")
                except Exception as e:
                    logger.error(f"[WORKER] Error closing ModManager: {e}", exc_info=True)
    
    def _run_sequential(self, mod_filenames):
        """Process mods sequentially."""
        total = len(mod_filenames)
        logger.info(f"[SEQUENTIAL] Starting sequential processing of {total} mods\n")
        
        # Emit initial log message
        self.log_message.emit(f"\n{'='*60}")
        self.log_message.emit(f"Starting Sequential Processing")
        self.log_message.emit(f"{'='*60}")
        self.log_message.emit(f"Total mods to process: {total}\n")
        
        for i, filename in enumerate(mod_filenames):
            if self.should_stop:
                logger.warning(f"[SEQUENTIAL] Processing stopped by user at mod {i+1}/{total}")
                self.log_message.emit("\n[STOP] Processing stopped by user")
                break
            
            current = i + 1
            
            try:
                # Log and emit detailed status before processing
                status_msg = f"[{current}/{total}] Processing: {filename}"
                logger.debug(f"[SEQUENTIAL] {status_msg}")
                self.status_updated.emit(status_msg)
                self.progress_updated.emit(current, total, status_msg)
                
                # Force GUI to process pending events (real-time display)
                app = QApplication.instance()
                if app:
                    app.processEvents()
                
                logger.info(f"[SEQUENTIAL] Starting: {filename}")
                
                # Process the mod with error handling
                success = self.mod_manager.process_mod(filename)
                
                if success:
                    logger.info(f"[SEQUENTIAL] SUCCESS: {filename}")
                    self.log_message.emit(f"✅ SUCCESS: {filename}")
                else:
                    logger.warning(f"[SEQUENTIAL] FAILED: {filename}")
                    self.log_message.emit(f"❌ FAILED: {filename}")
                
                # Force GUI to process (real-time display)
                if app:
                    app.processEvents()
                    
            except Exception as e:
                error_msg = f"[SEQUENTIAL] EXCEPTION processing {filename}: {str(e)}"
                logger.error(error_msg)
                logger.error(f"[SEQUENTIAL] Traceback:\n{traceback.format_exc()}")
                self.log_message.emit(f"❌ ERROR in {filename}: {str(e)}")
        
        logger.info(f"[SEQUENTIAL] Processing complete")
        self.log_message.emit(f"\n{'='*60}")
        self.log_message.emit(f"Processing Complete!")
        self.log_message.emit(f"{'='*60}")
        
        try:
            summary = {
                'total': total,
                'processed': self.mod_manager.processed_count,
                'failed': self.mod_manager.failed_count,
                'failed_mods': self.mod_manager.failed_mods,
                'csv_file': self.mod_manager.settings.csv_file
            }
            
            # Emit summary to UI
            self.log_message.emit(f"\n📊 Summary:")
            self.log_message.emit(f"  Total: {summary['total']}")
            self.log_message.emit(f"  ✅ Processed: {summary['processed']}")
            self.log_message.emit(f"  ❌ Failed: {summary['failed']}")
            if summary['failed_mods']:
                self.log_message.emit(f"\n⚠️  Failed mods:")
                for mod in summary['failed_mods']:
                    self.log_message.emit(f"  - {mod}")
            
            logger.info(f"[SEQUENTIAL] Summary: {summary}")
            self.finished.emit(summary)
        except Exception as e:
            logger.error(f"[SEQUENTIAL] Error emitting finished signal: {e}")
            self.error_occurred.emit(f"Error finalizing: {str(e)}")
    
    def _run_multithreaded(self, mod_filenames):
        """Process mods using thread pool."""
        import threading
        
        total = len(mod_filenames)
        processed = 0
        logger.info(f"[MULTITHREADED] Starting multithreaded processing of {total} mods")
        logger.info(f"[MULTITHREADED] Max workers: {self.settings.max_workers}\n")
        
        # Emit initial log message
        self.log_message.emit(f"\n{'='*60}")
        self.log_message.emit(f"Starting Multithreaded Processing")
        self.log_message.emit(f"{'='*60}")
        self.log_message.emit(f"Total mods: {total}")
        self.log_message.emit(f"Workers: {self.settings.max_workers}\n")
        
        # Use lock to protect shared mod_manager access
        mod_lock = threading.Lock()
        
        with ThreadPoolExecutor(max_workers=self.settings.max_workers) as executor:
            futures = {}
            
            for i, filename in enumerate(mod_filenames):
                if self.should_stop:
                    logger.warning(f"[MULTITHREADED] Stop requested before submitting mod {i+1}/{total}")
                    break
                
                try:
                    logger.debug(f"[MULTITHREADED] Submitting mod {i+1}/{total}: {filename}")
                    
                    # Create a wrapped function that uses the lock
                    def process_with_lock(fname):
                        with mod_lock:
                            return self.mod_manager.process_mod(fname)
                    
                    future = executor.submit(process_with_lock, filename)
                    futures[future] = (i + 1, filename)
                    
                    # Force GUI to process (real-time display)
                    app = QApplication.instance()
                    if app:
                        app.processEvents()
                        
                except Exception as e:
                    logger.error(f"[MULTITHREADED] Error submitting task for {filename}: {e}")
                    logger.error(f"[MULTITHREADED] Traceback:\n{traceback.format_exc()}")
            
            logger.info(f"[MULTITHREADED] Submitted {len(futures)} tasks, waiting for completion...")
            
            for future in as_completed(futures):
                if self.should_stop:
                    logger.warning(f"[MULTITHREADED] Stop requested during processing")
                    break
                
                current, filename = futures[future]
                
                try:
                    logger.debug(f"[MULTITHREADED] [{current}/{total}] Waiting for result: {filename}")
                    status_msg = f"[{current}/{total}] Processing: {filename}"
                    self.status_updated.emit(status_msg)
                    
                    success = future.result(timeout=300)  # 5 minute timeout per mod
                    if success:
                        logger.info(f"[MULTITHREADED] [{current}/{total}] SUCCESS: {filename}")
                        self.log_message.emit(f"✅ SUCCESS: {filename}")
                        processed += 1
                    else:
                        logger.warning(f"[MULTITHREADED] [{current}/{total}] FAILED: {filename}")
                        self.log_message.emit(f"❌ FAILED: {filename}")
                        
                except TimeoutError as e:
                    error_msg = f"TIMEOUT: Operation took too long for {filename} (>5min)"
                    logger.error(f"[MULTITHREADED] [{current}/{total}] {error_msg}")
                    self.log_message.emit(f"❌ {error_msg}")
                    
                except Exception as e:
                    error_msg = f"[MULTITHREADED] [{current}/{total}] EXCEPTION in {filename}: {str(e)}"
                    logger.error(error_msg)
                    logger.error(f"[MULTITHREADED] Traceback:\n{traceback.format_exc()}")
                    self.log_message.emit(f"❌ ERROR in {filename}: {str(e)}")
                
                self.progress_updated.emit(current, total, f"Processed {filename}")
                
                # Force GUI to process (real-time display)
                app = QApplication.instance()
                if app:
                    app.processEvents()
        
        logger.info(f"[MULTITHREADED] Processing complete. Processed {processed} mods successfully")
        self.log_message.emit(f"\n{'='*60}")
        self.log_message.emit(f"Processing Complete!")
        self.log_message.emit(f"{'='*60}")
        
        try:
            summary = {
                'total': total,
                'processed': self.mod_manager.processed_count,
                'failed': self.mod_manager.failed_count,
                'failed_mods': self.mod_manager.failed_mods,
                'csv_file': self.mod_manager.settings.csv_file
            }
            
            # Emit summary to UI
            self.log_message.emit(f"\n📊 Summary:")
            self.log_message.emit(f"  Total: {summary['total']}")
            self.log_message.emit(f"  ✅ Processed: {summary['processed']}")
            self.log_message.emit(f"  ❌ Failed: {summary['failed']}")
            if summary['failed_mods']:
                self.log_message.emit(f"\n⚠️  Failed mods:")
                for mod in summary['failed_mods']:
                    self.log_message.emit(f"  - {mod}")
            
            logger.info(f"[MULTITHREADED] Summary: {summary}")
            self.finished.emit(summary)
        except Exception as e:
            logger.error(f"[MULTITHREADED] Error emitting finished signal: {e}")
            self.error_occurred.emit(f"Error finalizing: {str(e)}")
    
    def stop(self):
        """Request graceful stop."""
        self.should_stop = True
        logger.warning(f"[WORKER] Stop signal received from user")
        self.log_message.emit("[STOP] Stop requested")


class WorkerThread(QThread):
    """
    QThread wrapper for the mod processor worker.
    """
    
    def __init__(self, worker, settings=None):
        """
        Initialize the thread.
        
        Args:
            worker (ModProcessorWorker): The worker to run
            settings (Settings, optional): Configuration
        """
        super().__init__()
        self.worker = worker
        self.settings = settings or get_settings()
        self.mod_filenames = []
        self.use_multithreading = False
    
    def run(self):
        """Run the worker (called by QThread)."""
        self.worker.run(self.mod_filenames, self.use_multithreading)
    
    def set_mod_list(self, filenames, use_multithreading=False):
        """
        Set the list of mods to process.
        
        Args:
            filenames (list): List of mod filenames
            use_multithreading (bool): Whether to use multithreading
        """
        self.mod_filenames = filenames
        self.use_multithreading = use_multithreading
    
    def stop_worker(self):
        """Stop the worker gracefully."""
        self.worker.stop()


class UpdateWorker(QObject):
    """
    Worker that runs mod updates in background thread.
    Emits signals for GUI updates.
    """
    
    # Signals
    progress_updated = Signal(int, int, str)  # current, total, message
    log_message = Signal(str)  # log message
    status_updated = Signal(str)  # detailed operation status
    finished = Signal(dict)  # summary dict
    error_occurred = Signal(str)  # error message
    
    def __init__(self, mods_folder: str, settings=None):
        """
        Initialize the update worker.
        
        Args:
            mods_folder (str): Path to the mods folder
            settings (Settings, optional): Configuration object
        """
        super().__init__()
        self.mods_folder = mods_folder
        self.settings = settings or get_settings()
        self.update_manager = None
        self.should_stop = False
    
    def run(self):
        """
        Check for and apply updates to mods in the folder.
        """
        self.should_stop = False
        
        # Emit initial status
        msg = f"Scanning mods folder: {self.mods_folder}"
        logger.info(f"\n{'='*80}")
        logger.info(f"[UPDATE WORKER] {msg}")
        logger.info(f"{'='*80}\n")
        self.log_message.emit(f"\n📁 {msg}\n")
        self.status_updated.emit("Scanning...")
        
        # Force GUI to process
        app = QApplication.instance()
        if app:
            app.processEvents()
        
        try:
            from core.update_manager import UpdateManager
            from core.mod_scanner import ModScanner
            
            self.update_manager = UpdateManager(self.settings)
            
            # Emit status
            self.log_message.emit("Scanning mods in folder...")
            self.status_updated.emit("Scanning...")
            
            if app:
                app.processEvents()
            
            # Scan the folder for mods
            mods, scan_errors = ModScanner.scan_mods_folder(self.mods_folder)
            
            if scan_errors:
                logger.warning(f"[UPDATE] Scan errors: {scan_errors}")
                for error in scan_errors:
                    self.log_message.emit(f"⚠️  Scan error: {error}")
            
            if not mods:
                self.log_message.emit("⚠️  No mods found in folder")
                self.progress_updated.emit(0, 1, "No mods found")
                self.finished.emit({
                    'total': 0,
                    'up_to_date': 0,
                    'updated': 0,
                    'failed': 0,
                    'errors': scan_errors,
                    'details': []
                })
                return
            
            # Create backup folder
            backup_ok, backup_path = ModScanner.create_backup_folder(self.mods_folder)
            if not backup_ok:
                logger.error(f"[UPDATE] Could not create backup folder: {backup_path}")
                self.log_message.emit(f"❌ Backup folder creation failed: {backup_path}")
            else:
                self.log_message.emit(f"📦 Backup folder: {backup_path}\n")
            
            if app:
                app.processEvents()
            
            # Process each mod with real-time emission
            total = len(mods)
            up_to_date = 0
            updated = 0
            failed = 0
            details = []
            
            self.log_message.emit(f"\n{'='*60}")
            self.log_message.emit(f"Checking {total} mods for updates")
            self.log_message.emit(f"{'='*60}\n")
            
            for i, mod in enumerate(mods, 1):
                if self.should_stop:
                    logger.warning(f"[UPDATE] Stopped by user at mod {i}/{total}")
                    self.log_message.emit(f"\n⏹️  Stopped by user at mod {i}/{total}")
                    break
                
                mod_name = mod['mod_name']
                current_version = mod['version']
                mod_path = mod['full_path']
                
                # Emit current item status
                status_msg = f"[{i}/{total}] Checking: {mod_name}"
                self.status_updated.emit(status_msg)
                self.progress_updated.emit(i, total, status_msg)
                
                # Process single mod
                result = self.update_manager._process_single_mod(
                    mod_name,
                    current_version,
                    mod_path,
                    backup_path,
                    self.mods_folder
                )
                
                # Emit result immediately
                status = result['status']
                latest_version = result.get('latest_version', 'N/A')
                
                if status == 'up_to_date':
                    up_to_date += 1
                    log_msg = f"✅ UP-TO-DATE: {mod_name} (v{current_version})"
                elif status == 'updated':
                    updated += 1
                    log_msg = f"🔄 UPDATED: {mod_name} (v{current_version} → v{latest_version})"
                else:
                    failed += 1
                    log_msg = f"❌ FAILED: {mod_name} - {result.get('message', 'Unknown error')}"
                
                self.log_message.emit(log_msg)
                
                detail = {
                    'mod_name': mod_name,
                    'current_version': current_version,
                    'status': status,
                    'latest_version': latest_version,
                    'message': result.get('message', '')
                }
                details.append(detail)
                
                # Force GUI to process (real-time display)
                if app:
                    app.processEvents()
            
            # Emit final summary
            self.log_message.emit(f"\n{'='*60}")
            self.log_message.emit(f"📊 SUMMARY")
            self.log_message.emit(f"  Total mods: {total}")
            self.log_message.emit(f"  ✅ Up-to-date: {up_to_date}")
            self.log_message.emit(f"  🔄 Updated: {updated}")
            self.log_message.emit(f"  ❌ Failed: {failed}")
            self.log_message.emit(f"{'='*60}")
            self.log_message.emit(f"\n✅ Update check complete!\n")
            
            if app:
                app.processEvents()
            
            logger.info(f"[UPDATE WORKER] Update check complete")
            
            # Emit finished with all details
            summary = {
                'total': total,
                'up_to_date': up_to_date,
                'updated': updated,
                'failed': failed,
                'errors': scan_errors,
                'details': details
            }
            self.finished.emit(summary)
        
        except Exception as e:
            error_msg = f"Update check failed: {str(e)}"
            logger.error(f"[UPDATE WORKER ERROR] {e}", exc_info=True)
            logger.error(f"[UPDATE WORKER ERROR] Traceback:\n{traceback.format_exc()}")
            self.log_message.emit(f"❌ ERROR: {error_msg}")
            self.error_occurred.emit(error_msg)
        
        finally:
            logger.info(f"[UPDATE WORKER] Cleaning up")
            if self.update_manager:
                try:
                    self.update_manager.close()
                except Exception as e:
                    logger.error(f"[UPDATE WORKER] Error closing manager: {e}")


class UpdateWorkerThread(QThread):
    """
    QThread wrapper for the update worker.
    """
    
    # Signals - pass through from worker
    progress_updated = Signal(int, int, str)
    log_message = Signal(str)
    status_updated = Signal(str)
    finished = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, mods_folder: str, settings=None):
        """
        Initialize the thread.
        
        Args:
            mods_folder (str): Path to the mods folder
            settings (Settings, optional): Configuration
        """
        super().__init__()
        self.mods_folder = mods_folder
        self.settings = settings or get_settings()
        self.worker = None
        self.should_stop = False
    
    def run(self):
        """Run the update worker."""
        try:
            self.worker = UpdateWorker(self.mods_folder, self.settings)
            
            # Connect signals
            self.worker.progress_updated.connect(self.progress_updated.emit)
            self.worker.log_message.connect(self.log_message.emit)
            self.worker.status_updated.connect(self.status_updated.emit)
            self.worker.finished.connect(self.finished.emit)
            self.worker.error_occurred.connect(self.error_occurred.emit)
            
            # Run the worker
            self.worker.run()
        
        except Exception as e:
            logger.error(f"[UPDATE THREAD ERROR] {e}", exc_info=True)
            self.error_occurred.emit(f"Update thread error: {str(e)}")

