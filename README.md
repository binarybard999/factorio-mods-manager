# Factorio Mod Manager

**Version: 2.0.1** - Architecture Refactoring Release

A modern, feature-rich desktop application for downloading, updating, and managing Factorio mods without requiring login to the Factorio mod portal.

## ✨ Key Features

### Core Features
- ✅ **GUI-Based Interface** - User-friendly PySide6 application with modern theme support
- ✅ **Drag & Drop Support** - Simply drag and drop `mods.txt` files or mods folders
- ✅ **Bulk Mod Processing** - Process multiple mods from a text file
- ✅ **API Integration** - Fetch mod metadata from Factorio Mod Portal API
- ✅ **Mirror Downloads** - Download mod ZIPs from mirror servers with fallback
- ✅ **Retry Logic** - Exponential backoff with configurable retries
- ✅ **Anti-Detection** - Randomized delays to avoid rate limiting

### New Features 🎉
- ✅ **Flexible Mod Input** - Support three formats:
  - Versioned filenames: `modname_1.2.3.zip`
  - Unversioned filenames: `modname.zip` (fetches latest version)
  - Simple mod names: `modname` (fetches latest version)
- ✅ **Mods Folder Updates** - Scan existing mods folder and check for updates
- ✅ **Smart Version Checking** - Compare versions and auto-download updates
- ✅ **Automatic Backups** - Old mod versions backed up to `old_mods/` folder
- ✅ **Theme Support** - Light, Dark, and System Default themes
- ✅ **Multithreading** - Optional concurrent processing for faster downloads
- ✅ **Image Downloads** - Automatically save mod thumbnail images
- ✅ **Metadata Storage** - Export mod information to CSV
- ✅ **Configuration** - Fully configurable via `.env` file
- ✅ **Modular Architecture** - Clean separation of concerns across layers
- ✅ **Real-Time Logging** - Live progress display during processing

### Version 2.0.0 Updates
- 🎨 **Modern UI Redesign** - Professional layout with proper spacing and section organization
- 👁️ **Visual Feedback** - Clear click states on buttons, checkboxes, and inputs
- 🔄 **Live Progress** - Real-time logging line-by-line as operations progress
- 📊 **Dual Processing Tabs** - Process mods from files OR update existing mods folders
- 🎯 **Improved UX** - Better error messages, progress tracking, and visual hierarchy
- 🌓 **Enhanced Themes** - Light/Dark/System themes with modern color scheme

### Version 2.0.1 Updates (Architecture Refactoring)
- 🏗️ **UI Layer Restructuring** - Refactored monolithic `app.py` (1050 lines) into 8 focused modules:
  - `main_window.py` (125 lines) - Main application window orchestrator
  - `tabs/list_processing_tab.py` (306 lines) - Mod list processing component
  - `tabs/folder_updates_tab.py` (258 lines) - Folder update component
  - `components/` folder - Reusable UI components (progress panel, file browser, drag-drop)
  - `controllers/theme_controller.py` (97 lines) - Centralized theme management
- 📦 **Improved Code Organization** - Each module ≤ 306 lines with clear responsibilities
- 🎯 **Better Separation of Concerns** - Components are now independently testable and reusable
- 🗂️ **Archive System** - Deprecated files safely archived in `_archive/` folder for future reference
- 🚀 **Foundation for Future Phases** - Scalable architecture ready for Phase 2+ refactoring

## 📊 Architecture

The application follows a layered architecture:

```
GUI Layer (PySide6 with Themes)
    ↓
Worker Layer (Threading)
    ↓
Core Logic (ModManager, UpdateManager)
    ↓
Service Layer (API, Downloads, Parser)
    ↓
Storage Layer (CSV, Filesystem)
    ↓
Utility Layer (Helpers, Retry)
```

## 📁 Project Structure

```
factorio_mods_manager/
├── main.py                              # Application entry point
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
│
├── config/
│   ├── __init__.py
│   ├── settings.py                      # Central configuration management
│   ├── user_settings.json               # User preferences (auto-generated)
│   └── theme_settings.json              # Theme preference (auto-generated)
│
├── services/
│   ├── __init__.py
│   ├── retry.py                         # Retry and delay logic
│   ├── factorio_api.py                  # API communication
│   └── downloader.py                    # File downloads with mirror fallback
│
├── core/
│   ├── __init__.py
│   ├── parser.py                        # Filename & mod name parsing
│   ├── mod_manager.py                   # Main orchestration logic
│   ├── mod_scanner.py                   # Scan mods folders for existing mods
│   └── update_manager.py                # Handle mod updates & backups
│
├── storage/
│   ├── __init__.py
│   ├── csv_store.py                     # CSV metadata storage
│   └── file_store.py                    # Filesystem utilities
│
├── utils/
│   ├── __init__.py
│   └── helpers.py                       # Generic utility functions
│
├── ui/                                  # GUI Layer (Refactored v2.0.1)
│   ├── main_window.py                   # Main application window orchestrator
│   ├── worker.py                        # Background worker threads
│   ├── theme.py                         # Theme management
│   ├── modern_theme.py                  # Modern theme with colors & styles
│   ├── settings_dialog.py               # Settings dialog
│   │
│   ├── tabs/                            # Tab components (v2.0.1+)
│   │   ├── base_tab.py                  # Base class for all tabs
│   │   ├── list_processing_tab.py       # Mod list processing from files
│   │   └── folder_updates_tab.py        # Update mods in existing folder
│   │
│   ├── components/                      # Reusable UI components (v2.0.1+)
│   │   ├── progress_panel.py            # Progress bar + log display
│   │   ├── drag_drop_input.py           # Drag-drop enabled line edit
│   │   └── file_browser.py              # File & folder picker widgets
│   │
│   └── controllers/                     # UI controllers (v2.0.1+)
│       └── theme_controller.py          # Centralized theme control
│
└── data/                                # Runtime data directories
    ├── downloads/                       # Downloaded mod ZIP files
    ├── images/                          # Downloaded mod images
    ├── releases/                        # Release information CSV files
    └── failed/                          # Failed mod lists

└── _archive/                            # Archive for deprecated files (v2.0.1+)
    ├── app.py                           # Legacy UI (replaced by main_window.py)
    ├── app_basic.py                     # Old version backup
    ├── app_old.py                       # Old version backup
    └── modern_theme_old.py              # Legacy theme file
```

## 🚀 Installation

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

## ⚙️ Configuration

The application is configured via a `.env` file in the project root. A default `.env` is provided with recommended settings.

### Key Configuration Variables

```env
# Mirror URLs for mod downloads
MIRROR_URLS=https://mods-storage.re146.dev

# Retry and timeout settings
MAX_RETRIES=5
REQUEST_TIMEOUT=120
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

## 📖 Usage Guide

### Starting the Application

```bash
python main.py
```

The GUI will launch with two tabs: **Process Mod List** and **Update Mods Folder**

### Tab 1: Process Mod List

Use this tab to process a list of mods from a text file.

#### Preparing Your Mod List

Create a text file (e.g., `mods.txt`) with one mod entry per line:

```
# Versioned mods (specify exact version)
aai-vehicles-hauler_0.7.3.zip
bobsgoldfurnace_0.18.0.zip

# Unversioned mods (will fetch latest version)
aai-vehicles-flame-tumbler.zip
Krastorio2.zip

# Simple mod names (will fetch latest version)
bobplates
coal-processing
```

#### Processing Steps

1. **Load File**
   - Click "Browse..." to select your mod list file
   - Or drag and drop a text file into the text field

2. **Configure Options**
   - ☑️ Download mod ZIP files
   - ☑️ Save mod images
   - ☑️ Save releases as CSV
   - ☑️ Include changelog in CSV
   - ☑️ Enable multithreading (for faster processing)

3. **Start Processing**
   - Click "Start" to begin processing
   - Watch progress in the log output
   - Use "Stop" to gracefully halt processing

4. **Review Results**
   - Open the CSV file to view metadata
   - Check data/failed/ for any failed mods
   - Download images and ZIPs are in data/downloads/

### Tab 2: Update Mods Folder

Use this tab to check for and apply updates to existing mods.

#### Updating Mods

1. **Select Mods Folder**
   - Click "Browse..." to select your mods folder (e.g., `C:\factorio\mods`)
   - Or drag and drop a folder directly

2. **Configure Update Options**
   - ☑️ Backup old mods to 'old_mods' folder
   - ☑️ Auto-download updates

3. **Check Updates**
   - Click "Check Updates" to scan and process
   - The system will:
     1. Scan for all .zip files in the folder
     2. Parse mod names and current versions
     3. Fetch latest versions from Factorio API
     4. Download updates if available
     5. Backup old versions to `old_mods/` subfolder
     6. Replace with new version

4. **Review Results**
   - See summary of up-to-date, updated, and failed mods
   - Check logs for detailed operation info
   - Verify old_mods/ folder for backups

### Theme Selection

The application now supports three theme modes:

- **Light** - Light color scheme for daytime use
- **Dark** - Dark color scheme for reduced eye strain
- **System Default** - Automatically matches your OS theme

Change themes from the dropdown at the top of the window. Your preference is automatically saved.

## 📊 CSV Output Format

The main output file (`factorio_mods.csv`) contains:

| Column | Description |
|--------|-------------|
| filename | Original mod filename or name |
| local_version | Version from filename (or empty if not specified) |
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

## 📝 Failure Handling

Failed mods are logged to `data/failed/failed_YYYY-MM-DD_HH-MM-SS.txt`:

```
aai-vehicles-old_0.1.0.zip
invalid-mod-name
network-error-mod_1.0.0.zip
```

## 🔧 API Reference

### ModManager

Main orchestration class for processing mod lists:

```python
from core.mod_manager import ModManager
from config.settings import get_settings

settings = get_settings()
manager = ModManager(settings)

# Process a single mod (supports all formats)
result = manager.process_mod("modname_1.0.0.zip")
result = manager.process_mod("modname.zip")
result = manager.process_mod("modname")
```

### UpdateManager

Handle checking and updating mods in a folder:

```python
from core.update_manager import UpdateManager

update_mgr = UpdateManager()
summary = update_mgr.check_and_update_mods("/path/to/mods")
# Returns: {
#     'total': int,
#     'up_to_date': int,
#     'updated': int,
#     'failed': int,
#     'errors': list,
#     'details': list
# }
```

### ModScanner

Scan and detect mods in a folder:

```python
from core.mod_scanner import ModScanner

mods, errors = ModScanner.scan_mods_folder("/path/to/mods")
# mods = [
#     {'mod_name': 'modname', 'version': '1.0.0', 'filename': 'modname_1.0.0.zip', 'full_path': '...'},
#     ...
# ]
```

### ModParser

Parse mod filenames, names, and paths:

```python
from core.parser import parse_mod_filename

# Parse versioned filename
result = parse_mod_filename("aai-vehicles-hauler_0.7.3.zip")
# Returns: {
#     'input': 'aai-vehicles-hauler_0.7.3.zip',
#     'mod_name': 'aai-vehicles-hauler',
#     'version': '0.7.3',
#     'valid': True,
#     'error': None,
#     'is_filename': True
# }

# Parse unversioned filename
result = parse_mod_filename("modname.zip")
# Returns: {'mod_name': 'modname', 'version': None, ...}

# Parse simple mod name
result = parse_mod_filename("modname")
# Returns: {'mod_name': 'modname', 'version': None, 'is_filename': False, ...}
```

### FactorioAPI

API communication:

```python
from services.factorio_api import FactorioAPI

api = FactorioAPI()
data = api.get_mod_full("modname")
# Returns full mod metadata or None
```

### ThemeManager

Manage application themes:

```python
from ui.theme import ThemeManager, ThemeMode

# Apply a theme
ThemeManager.apply_theme(ThemeMode.DARK)
ThemeManager.apply_theme(ThemeMode.LIGHT)
ThemeManager.apply_theme(ThemeMode.SYSTEM)

# Check if system is in dark mode
is_dark = ThemeManager.is_system_dark_mode()
```

## 🚀 Advanced Usage

### Programmatic Access

Use the mod manager in your own Python scripts:

```python
from core.mod_manager import ModManager
from core.update_manager import UpdateManager
from config.settings import get_settings

def process_and_update():
    settings = get_settings()
    
    # Process a list
    manager = ModManager(settings)
    filenames = ["mod1_1.0.0.zip", "mod2.zip", "mod3"]
    for filename in filenames:
        manager.process_mod(filename)
    
    # Update a folder
    updater = UpdateManager(settings)
    summary = updater.check_and_update_mods("/path/to/mods")
    print(f"Updated: {summary['updated']} | Up-to-date: {summary['up_to_date']}")

if __name__ == "__main__":
    process_and_update()
```

### Custom Configuration

Override settings programmatically:

```python
from config.settings import Settings
from core.mod_manager import ModManager

settings = Settings(env_path="/path/to/custom/.env")
manager = ModManager(settings)
```

## 🐛 Troubleshooting

### "Invalid filename format"

Ensure filenames or mod names are in one of these formats:
- ✓ `modname_1.2.3.zip` (with version)
- ✓ `modname.zip` (without version)
- ✓ `modname` (just the name)
- ✗ `my modname_1.0.0.zip` (spaces not allowed)

### "Could not fetch metadata"

1. Check internet connection
2. Verify mod name is correct (case-sensitive)
3. Check if mod exists on https://mods.factorio.com
4. Increase `MAX_RETRIES` in `.env` (default: 5)
5. Increase `REQUEST_TIMEOUT` if on slow connection

### Download failures

1. Check `MIRROR_URLS` in `.env`
2. Increase `REQUEST_TIMEOUT` for slow connections
3. Reduce `MAX_WORKERS` if too many concurrent requests fail
4. Check failed list in `data/failed/`

### Slow processing

1. Enable multithreading: Check "Enable multithreading" in GUI
2. Increase `MAX_WORKERS` in `.env` (default: 4)
3. Reduce `RANDOM_DELAY_MIN` and `RANDOM_DELAY_MAX` (but don't set too low to avoid rate limiting)

### Theme not applying

1. Restart the application
2. Check that `config/theme_settings.json` is readable
3. Try selecting a different theme and restarting

## 🔮 Future Enhancements

Potential additions without major rewrites:

- [ ] CLI interface using Click for headless usage
- [ ] REST API using FastAPI for remote access
- [ ] Scheduled batch downloads and updates
- [ ] Dependency graph visualization
- [ ] SQLite database backend for faster queries
- [ ] Advanced filtering and search
- [ ] Mod comparison tools
- [ ] Load order optimization
- [ ] Automatic conflict detection
- [ ] Web dashboard
- [ ] Docker containerization

## 🛠️ Development

### Code Organization

- **Business Logic**: `core/`, `services/`
- **Data Storage**: `storage/`
- **User Interface**: `ui/`
- **Configuration**: `config/`
- **Utilities**: `utils/`

### Adding New Features

1. Add business logic in `core/` or `services/`
2. Add UI components in `ui/app.py`
3. Add worker threads in `ui/worker.py` if needed
4. Update documentation

### Running Tests

```bash
python -m pytest tests/ -v
```

### Code Style

The project follows PEP 8 conventions. All modules include comprehensive docstrings.

## 📄 License

MIT License - Feel free to use and modify this project.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests when possible
5. Submit a pull request

## 📞 Support

For issues or questions:

1. Check the **Troubleshooting** section above
2. Review application logs in the GUI
3. Check `data/failed/` for processing errors
4. Review `.env` configuration settings

## 🙏 Acknowledgments

- **Factorio Mod Portal**: https://mods.factorio.com
- **Mirror Storage**: https://mods-storage.re146.dev
- **PySide6**: https://wiki.qt.io/Qt_for_Python
- **Requests**: https://requests.readthedocs.io/
- **Python**: https://www.python.org/

---

**Factorio Mod Manager** - Manage your mod collection with ease! 🎮

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
