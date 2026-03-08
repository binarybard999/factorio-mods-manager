"""
ui/worker.py - Background worker for processing mods without blocking GUI
"""

import logging
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from PySide6.QtCore import QObject, Signal, QThread

from config.settings import get_settings
from core.mod_manager import ModManager


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
        
        for i, filename in enumerate(mod_filenames):
            if self.should_stop:
                logger.warning(f"[SEQUENTIAL] Processing stopped by user at mod {i+1}/{total}")
                self.log_message.emit("[STOP] Processing stopped by user")
                break
            
            current = i + 1
            
            try:
                # Log and emit detailed status before processing
                status_msg = f"[{current}/{total}] Processing: {filename}"
                logger.debug(f"[SEQUENTIAL] {status_msg}")
                self.status_updated.emit(status_msg)
                self.progress_updated.emit(current, total, status_msg)
                
                logger.info(f"[SEQUENTIAL] Starting: {filename}")
                
                # Process the mod with error handling
                success = self.mod_manager.process_mod(filename)
                
                if success:
                    logger.info(f"[SEQUENTIAL] SUCCESS: {filename}")
                    self.log_message.emit(f"✅ SUCCESS: {filename}")
                else:
                    logger.warning(f"[SEQUENTIAL] FAILED: {filename}")
                    self.log_message.emit(f"❌ FAILED: {filename}")
                    
            except Exception as e:
                error_msg = f"[SEQUENTIAL] EXCEPTION processing {filename}: {str(e)}"
                logger.error(error_msg)
                logger.error(f"[SEQUENTIAL] Traceback:\n{traceback.format_exc()}")
                self.log_message.emit(f"❌ ERROR in {filename}: {str(e)}")
        
        logger.info(f"[SEQUENTIAL] Processing complete")
        
        try:
            summary = {
                'total': total,
                'processed': self.mod_manager.processed_count,
                'failed': self.mod_manager.failed_count,
                'failed_mods': self.mod_manager.failed_mods,
                'csv_file': self.mod_manager.settings.csv_file
            }
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
        
        logger.info(f"[MULTITHREADED] Processing complete. Processed {processed} mods successfully")
        
        try:
            summary = {
                'total': total,
                'processed': self.mod_manager.processed_count,
                'failed': self.mod_manager.failed_count,
                'failed_mods': self.mod_manager.failed_mods,
                'csv_file': self.mod_manager.settings.csv_file
            }
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
