# Module Architecture & Dependencies

## Module Dependency Graph

```
main.py
  └── config.settings (get_settings, Settings)
  └── storage.file_store (FileStore)
  └── ui.app (FactorioModManagerApp)
       └── config.settings
       └── ui.worker (ModProcessorWorker, WorkerThread)
            └── config.settings
            └── core.mod_manager (ModManager)
                 ├── config.settings
                 ├── core.parser (parse_mod_filename)
                 ├── services.factorio_api (FactorioAPI)
                 │    ├── config.settings
                 │    ├── services.retry (backoff_sleep, random_delay)
                 │    └── requests (external)
                 ├── services.downloader (Downloader)
                 │    ├── config.settings
                 │    ├── services.retry
                 │    ├── utils.helpers (safe_filename)
                 │    └── requests (external)
                 ├── storage.csv_store (CSVStore)
                 ├── storage.file_store (FileStore)
                 └── utils.helpers (timestamp_filename)
```

## Layer Architecture

### GUI Layer (ui/)
**Responsibility**: User interaction and display
- `app.py`: Main window, options, progress display
- `worker.py`: Background worker threads, signal emission

**Dependencies**: config, core, logging

### Worker Layer (concurrent execution)
**Responsibility**: Background processing without blocking GUI
- Threading: QThread for background execution
- Signals: Qt signals for communication to GUI

**Dependencies**: core, config

### Core Logic Layer (core/)
**Responsibility**: Business logic and orchestration
- `mod_manager.py`: Main orchestrator that coordinates all services
- `parser.py`: Filename parsing using regex

**Dependencies**: services, storage, config, utils

### Service Layer (services/)
**Responsibility**: External integrations
- `factorio_api.py`: API communication with Factorio Mod Portal
- `downloader.py`: File downloads with retry and mirror fallback
- `retry.py`: Retry logic and delays

**Dependencies**: config, requests (external), logging

### Storage Layer (storage/)
**Responsibility**: Data persistence
- `csv_store.py`: CSV file read/write operations
- `file_store.py`: Filesystem utilities

**Dependencies**: logging, pathlib (stdlib)

### Configuration Layer (config/)
**Responsibility**: Settings management
- `settings.py`: Load and expose configuration from .env

**Dependencies**: python-dotenv (external), pathlib (stdlib)

### Utility Layer (utils/)
**Responsibility**: Generic helper functions
- `helpers.py`: Safe filenames, timestamps, directory operations

**Dependencies**: pathlib (stdlib), datetime (stdlib), re (stdlib)

## Data Flow

### Processing a Mod

```
1. User loads mod list file (UI)
   ↓
2. Worker thread created (Worker)
   ↓
3. ModManager.process_mod(filename) called (Core)
   ↓
4. Parser.parse(filename) → {mod_name, version} (Core)
   ↓
5. FactorioAPI.get_mod_full(mod_name) → metadata (Service)
   ├─ Retry logic applied (Service)
   └─ Random delay applied (Service)
   ↓
6. Downloader.download_image(url, mod_name) (Service)
   ├─ Mirror URL tried
   ├─ Retry logic applied
   └─ Streaming download
   ↓
7. Downloader.download_mod_zip(mod_name, version) (Service)
   ├─ Mirror URL tried (primary)
   └─ Official fallback tried (secondary)
   ↓
8. CSVStore.append_row(metadata) (Storage)
   ├─ Thread-safe write with lock
   └─ File created if needed
   ↓
9. Progress signal emitted (Worker)
   ↓
10. UI updated with progress (GUI)
```

## Configuration Flow

```
Environment Variables (.env)
        ↓
python-dotenv
        ↓
Settings class (config/settings.py)
        ↓
get_settings() singleton
        ↓
Used by all modules
```

## Concurrency Model

### Single-Threaded Mode
```
Main Thread (GUI)
    ↓
Worker Thread
    ├─ Sequential loop
    └─ Process each mod one at a time
```

### Multi-Threaded Mode
```
Main Thread (GUI)
    ↓
Worker Thread
    ├─ ThreadPoolExecutor (max_workers from config)
    ├─ Submit batch of tasks
    └─ Process mods in parallel
```

## Error Handling Strategy

```
User Request
    ↓
Try: process_mod(filename)
    ├─ Parse fail → Add to failed_mods, continue
    ├─ API fail → Retry with backoff
    ├─ Download fail → Retry with backoff
    └─ File write fail → Log error
    ↓
Finally: save_failed_list()
```

## Extension Points

### Adding a New Service

Example: Adding Slack notifications

```python
# services/slack_notifier.py
class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def notify(self, message):
        # Send to Slack

# In core/mod_manager.py
from services.slack_notifier import SlackNotifier

class ModManager:
    def __init__(self, settings=None):
        self.notifier = SlackNotifier(settings.slack_webhook)
    
    def process_mod(self, filename):
        # ... existing code ...
        self.notifier.notify(f"Processed {filename}")
```

### Adding a New Storage Backend

Example: SQLite instead of CSV

```python
# storage/sqlite_store.py
class SQLiteStore:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)
    
    def append_row(self, row_dict):
        # INSERT into database

# In core/mod_manager.py
self.store = SQLiteStore('mods.db')
```

### Adding a New GUI

Example: Web interface using FastAPI

```python
# web/app.py
from fastapi import FastAPI
from core.mod_manager import ModManager

app = FastAPI()

@app.post("/process")
async def process_mods(filenames: List[str]):
    manager = ModManager()
    return manager.process_mod_list(filenames)
```

## Testing Strategy

```
tests/
  ├── test_parser.py       → Test filename parsing
  ├── test_api.py          → Mock API calls
  ├── test_downloader.py   → Mock file downloads
  ├── test_csv_store.py    → Test CSV operations
  └── test_integration.py  → End-to-end testing
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Parse filename | ~1ms | Regex only |
| Fetch metadata | 200-500ms | API call + retry/delay |
| Download image | 500-2000ms | Depends on image size |
| Download mod ZIP | 5-30s | Depends on mod size |
| CSV write | ~5ms | Thread-locked |
| Random delay | 0.5-2s | Anti-detection |

**Total per mod**: ~5-35 seconds (average 10s with downloads)

## Memory Usage

- Per-mod: ~1-2 MB (metadata + download buffer)
- Thread pool: ~1 MB per worker thread
- CSV in memory: Minimal (streaming writes)
- API responses: Parsed and stored temporarily

**Total memory**: ~50-200 MB for 10-20 concurrent mods

---

For more details, see [README.md](README.md) and module docstrings.
