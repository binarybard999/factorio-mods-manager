# Factorio Mod Manager

A modern desktop application for downloading, updating, and collecting metadata for Factorio mods without requiring login to the Factorio mod portal.

## Features

- ✅ **GUI-Based Interface** - User-friendly PySide6 desktop application
- ✅ **Bulk Mod Processing** - Process multiple mods from a text file
- ✅ **API Integration** - Fetch mod metadata from Factorio Mod Portal API
- ✅ **Mirror Downloads** - Download mod ZIPs from mirror servers with fallback
- ✅ **Image Downloads** - Automatically save mod thumbnail images
- ✅ **Metadata Storage** - Export mod information to CSV
- ✅ **Retry Logic** - Exponential backoff with configurable retries
- ✅ **Anti-Detection** - Randomized delays to avoid rate limiting
- ✅ **Multithreading** - Optional concurrent processing for faster downloads
- ✅ **Failure Tracking** - Log failed mods for later retry
- ✅ **Configuration** - Fully configurable via `.env` file
- ✅ **Modular Architecture** - Clean separation of concerns across layers

## Architecture

The application follows a layered architecture:

```
GUI Layer
    ↓
Worker Layer (Threading)
    ↓
Core Logic (ModManager)
    ↓
Service Layer (API, Downloads, Parser)
    ↓
Storage Layer (CSV, Filesystem)
    ↓
Utility Layer (Helpers, Retry)
```

## Project Structure

```
factorio_mods_manager/
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Configuration (create after first run)
├── README.md                    # This file
│
├── config/
│   ├── __init__.py
│   └── settings.py              # Central configuration management
│
├── services/
│   ├── __init__.py
│   ├── retry.py                 # Retry and delay logic
│   ├── factorio_api.py          # API communication
│   └── downloader.py            # File downloads with mirror fallback
│
├── core/
│   ├── __init__.py
│   ├── parser.py                # Filename parsing (regex)
│   └── mod_manager.py           # Main orchestration logic
│
├── storage/
│   ├── __init__.py
│   ├── csv_store.py             # CSV metadata storage
│   └── file_store.py            # Filesystem utilities
│
├── utils/
│   ├── __init__.py
│   └── helpers.py               # Generic utility functions
│
├── ui/
│   ├── __init__.py
│   ├── app.py                   # Main GUI window (PySide6)
│   └── worker.py                # Background worker thread
│
└── data/                        # Runtime data directories
    ├── downloads/               # Downloaded mod ZIP files
    ├── images/                  # Downloaded mod images
    ├── releases/                # Release information CSV files
    └── failed/                  # Failed mod lists
```

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**

```bash
cd factorio_mods_manager
```

2. **Create a virtual environment (recommended)**

```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
source venv/bin/activate      # Linux/Mac
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Run the application**

```bash
python main.py
```

## Configuration

The application is configured via a `.env` file in the project root. A default `.env` is provided with recommended settings.

### Key Configuration Variables

```env
# Mirror URLs for mod downloads
MIRROR_URLS=https://mods-storage.re146.dev

# Retry and timeout settings
MAX_RETRIES=5
REQUEST_TIMEOUT=12
BACKOFF_BASE=1.4

# Delay settings (seconds) to avoid rate limiting
RANDOM_DELAY_MIN=0.5
RANDOM_DELAY_MAX=2.0

# Concurrency
MAX_WORKERS=4

# Directory paths
DOWNLOAD_DIR=data/downloads
IMAGES_DIR=data/images
RELEASES_DIR=data/releases
FAILED_DIR=data/failed

# Output CSV file
CSV_FILE=factorio_mods.csv

# Feature flags
SAVE_IMAGES=true
SAVE_RELEASES=false
DOWNLOAD_ZIPS=true
SAVE_CHANGELOG=false
```

## Usage

### Preparing Your Mod List

1. Create a text file (e.g., `mods.txt`) with one mod filename per line:

```
aai-vehicles-hauler_0.7.3.zip
aai-vehicles-flame-tumbler_0.7.2.zip
bobsgoldfurnace_0.18.0.zip
```

Comments starting with `#` are ignored:

```
# Mining mods
bob_modules_0.18.0.zip
bobplates_4.2.0.zip

# Vehicles
aai-vehicles-hauler_0.7.3.zip
```

### Running the Application

1. **Start the GUI**

```bash
python main.py
```

2. **Load Mod List**
   - Click "Browse..." to select your mod list file
   - Or drag and drop a text file into the text field

3. **Configure Options**
   - Enable/disable features as needed
   - Adjust multithreading if desired

4. **Start Processing**
   - Click "Start" to begin processing
   - Watch progress in the log output
   - Use "Stop" to gracefully halt processing

5. **Review Results**
   - Open the CSV file to view metadata
   - Check data/failed/ for any failed mods
   - Download images and ZIPs are in data/downloads/

## CSV Output Format

The main output file (`factorio_mods.csv`) contains:

| Column | Description |
|--------|-------------|
| filename | Original mod filename |
| local_version | Version from filename |
| title | Mod title |
| summary | Mod summary |
| owner | Mod author |
| latest_version | Latest version from API |
| latest_dependencies | Dependencies of latest version |
| downloads | Download count |
| homepage | Mod homepage URL |
| category | Mod category |
| tags | Mod tags (comma-separated) |
| created_at | Creation date |
| updated_at | Last update date |
| license | License name |
| changelog | (optional) Full changelog text |

## Failure Handling

Failed mods are logged to `data/failed/failed_YYYY-MM-DD_HH-MM-SS.txt`:

```
aai-vehicles-old_0.1.0.zip
invalid-mod-name_1.0.0.zip
```

## API Reference

### ModManager

Main orchestration class:

```python
from core.mod_manager import ModManager
from config.settings import get_settings

settings = get_settings()
manager = ModManager(settings)

# Process a single mod
result = manager.process_mod("modname_1.0.0.zip")

# Process a list
summary = manager.process_mod_list(filenames)
# Returns: {
#     'total': int,
#     'processed': int,
#     'failed': int,
#     'failed_mods': list,
#     'csv_file': str
# }
```

### FactorioAPI

API communication:

```python
from services.factorio_api import FactorioAPI

api = FactorioAPI()
data = api.get_mod_full("modname")
# Returns full mod metadata or None
```

### Downloader

File downloads:

```python
from services.downloader import Downloader

downloader = Downloader()
success, path = downloader.download_mod_zip("modname", "1.0.0")
success, path = downloader.download_image(url, "modname")
```

### ModParser

Filename parsing:

```python
from core.parser import parse_mod_filename

result = parse_mod_filename("aai-vehicles-hauler_0.7.3.zip")
# Returns: {
#     'filename': 'aai-vehicles-hauler_0.7.3.zip',
#     'mod_name': 'aai-vehicles-hauler',
#     'version': '0.7.3',
#     'valid': True,
#     'error': None
# }
```

## Advanced Usage

### Programmatic Access

Use the mod manager in your own Python scripts:

```python
from core.mod_manager import ModManager
from config.settings import get_settings

def process_mods():
    settings = get_settings()
    with ModManager(settings) as manager:
        filenames = ["mod1_1.0.0.zip", "mod2_2.0.0.zip"]
        summary = manager.process_mod_list(filenames)
        print(f"Processed: {summary['processed']}/{summary['total']}")

if __name__ == "__main__":
    process_mods()
```

### Custom Configuration

Override settings programmatically:

```python
from config.settings import Settings
from core.mod_manager import ModManager

settings = Settings(env_path="/path/to/custom/.env")
manager = ModManager(settings)
```

## Troubleshooting

### "Invalid filename format"

Ensure filenames match the pattern: `modname_version.zip`
- Valid: `aai-vehicles-hauler_0.7.3.zip`
- Invalid: `aai-vehicles-hauler.zip` (missing version)

### "Could not fetch metadata"

1. Check internet connection
2. Verify mod name is correct
3. Check if mod exists on https://mods.factorio.com
4. Increase `MAX_RETRIES` in `.env`

### Download failures

1. Check `MIRROR_URLS` in `.env`
2. Increase `REQUEST_TIMEOUT` for slow connections
3. Reduce `MAX_WORKERS` if too many concurrent requests fail
4. Check failed list in `data/failed/`

### Slow processing

1. Enable multithreading: Check "Enable multithreading" in GUI
2. Increase `MAX_WORKERS` in `.env` (default: 4)
3. Reduce `RANDOM_DELAY_MIN` and `RANDOM_DELAY_MAX`

## Future Enhancements

Possible additions without core rewrites:

- [ ] CLI interface using Click
- [ ] REST API using FastAPI
- [ ] Automated mod update checking
- [ ] Scheduled batch downloads
- [ ] Dependency graph visualization
- [ ] SQLite database backend
- [ ] GUI themes and customization
- [ ] Mod comparison tools
- [ ] Integration with mod load order tools

## Development

### Code Organization

- **Business Logic**: `core/`, `services/`
- **Data Storage**: `storage/`
- **User Interface**: `ui/`
- **Configuration**: `config/`
- **Utilities**: `utils/`

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

The project follows PEP 8 conventions. All modules include docstrings.

## License

MIT License - Feel free to use and modify.

## Contributing

Contributions welcome! Areas for improvement:

- Unit tests
- Integration tests
- Error handling enhancements
- Performance optimizations
- UI improvements

## Support

For issues or questions:

1. Check the Troubleshooting section
2. Review application logs in the GUI
3. Check `data/failed/` for processing errors

## Acknowledgments

- Factorio Mod Portal: https://mods.factorio.com
- Mirror storage by re146: https://mods-storage.re146.dev
- PySide6: https://wiki.qt.io/Qt_for_Python

---

**Factorio Mod Manager** - Manage your mod collection with ease!
