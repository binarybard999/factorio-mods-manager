# Factorio Mod Manager – Full Autonomous Development Specification

This document is a **complete task specification** intended to be given to an autonomous coding agent. The agent should read this document and then **design, plan, and implement the entire project automatically**.

The goal is to build a **desktop application for downloading, updating, and collecting metadata for Factorio mods** without requiring a login to the Factorio mod portal.

The system must be **modular, configurable, resilient to failures, and maintainable**.

---

# 1. Project Goal

Create a **GUI-based desktop application** that:

1. Reads a list of Factorio mod filenames.
2. Extracts mod names and versions.
3. Queries the Factorio Mod Portal API for metadata.
4. Downloads:

   * mod ZIP files
   * mod images
5. Saves metadata to a CSV file.
6. Uses mirror servers to download mods **without login**.
7. Retries downloads with exponential backoff.
8. Adds randomized delays to avoid detection / rate limiting.
9. Stores any failed downloads in a **failed list file**.

The application must be:

* desktop GUI based
* multi-thread capable
* configurable via `.env`
* structured into modular components

---

# 2. Technology Stack

Language:

Python 3.10+

Libraries to use:

GUI

PySide6

Networking

requests

Configuration

python-dotenv

Data

csv (standard library)

Concurrency

concurrent.futures
threading

Utilities

pathlib
os
random
re
json
logging

Optional later:

pyinstaller (for building executable)

---

# 3. High Level Architecture

The application must follow **layered architecture**.

```
GUI Layer

Worker Layer

Core Logic Layer

Service Layer

Storage Layer

Utility Layer
```

Flow:

```
User selects mod list
        ↓
GUI triggers worker
        ↓
Worker processes list in threads
        ↓
ModManager coordinates logic
        ↓
Parser extracts mod info
        ↓
FactorioAPI fetches metadata
        ↓
Downloader retrieves files
        ↓
CSVStore saves metadata
```

---

# 4. Required Features

## GUI

The GUI must provide:

* file selector for mod list
* start button
* stop button
* progress bar
* log viewer
* option toggles

Options include:

* Download mod ZIP
* Save images
* Save release JSON
* Enable multithreading

The GUI **must not contain business logic**.

It only communicates with the Worker.

---

## Worker System

Workers must:

* run processing in background threads
* prevent GUI freezing
* report progress
* send log messages

Concurrency must use:

```
ThreadPoolExecutor
```

Worker must support stopping safely.

---

# 5. Configuration System

Configuration must be stored in `.env`.

Example variables:

```
MIRROR_URLS=https://mods-storage.re146.dev

MAX_RETRIES=5
REQUEST_TIMEOUT=10

RANDOM_DELAY_MIN=0.5
RANDOM_DELAY_MAX=2.0

MAX_WORKERS=4

DOWNLOAD_DIR=data/downloads
IMAGES_DIR=data/images
RELEASES_DIR=data/releases
FAILED_DIR=data/failed

CSV_FILE=factorio_mods.csv

SAVE_IMAGES=true
SAVE_RELEASES=false
DOWNLOAD_ZIPS=true
```

The system must load environment variables via:

```
python-dotenv
```

---

# 6. Folder Structure

The project must follow this structure.

```
factorio_mod_manager/

main.py

.env
requirements.txt
README.md

config/
    settings.py

services/
    factorio_api.py
    downloader.py
    retry.py

core/
    mod_manager.py
    parser.py

storage/
    csv_store.py
    file_store.py

utils/
    helpers.py

ui/
    app.py
    worker.py


data/
    images/
    downloads/
    releases/
    failed/
```

---

# 7. Module Responsibilities

## main.py

Entry point.

Responsibilities:

* load `.env`
* initialize configuration
* ensure data directories exist
* start GUI

---

## config/settings.py

Central configuration class.

Responsibilities:

* read environment variables
* expose configuration to rest of system

Example:

```
class Settings
```

Fields include:

* mirror servers
* retry counts
* timeouts
* folder paths

---

## services/retry.py

Handles retry and delay logic.

Functions:

```
backoff_sleep()
random_delay()
```

Features:

* exponential backoff
* randomized delay

---

## services/factorio_api.py

Handles communication with Factorio Mod Portal.

API endpoint:

```
https://mods.factorio.com/api/mods/<mod>/full
```

Responsibilities:

* fetch mod metadata
* parse releases

Example method:

```
get_mod_full(mod_name)
```

Must implement retry logic.

---

## services/downloader.py

Responsible for all file downloads.

Responsibilities:

* download mod ZIP
* download images
* support mirror fallback

Mirrors example:

```
https://mods-storage.re146.dev
```

Download order:

1 mirror
2 fallback to official portal

Features:

* streaming downloads
* retries
* partial file handling

---

## core/parser.py

Parses filenames.

Example input:

```
aai-vehicles-hauler_0.7.3.zip
```

Output:

```
mod_name = aai-vehicles-hauler
version = 0.7.3
```

Use regex.

---

## core/mod_manager.py

Main application logic.

Responsibilities:

* process mod list
* coordinate API calls
* coordinate downloads
* store metadata

Workflow:

```
parse filename
↓
fetch API data
↓
save CSV row
↓
download assets
```

Must handle errors gracefully.

---

## storage/csv_store.py

Handles CSV operations.

Responsibilities:

* create CSV header
* append rows
* read existing entries

CSV fields include:

* file name
* version
* title
* summary
* owner
* latest version
* dependencies
* downloads
* homepage
* category
* tags
* created date
* updated date
* license

---

## storage/file_store.py

Handles filesystem utilities.

Responsibilities:

* create directories
* manage paths

---

## utils/helpers.py

Generic helpers.

Examples:

```
safe_filename()
timestamp()
```

---

## ui/app.py

Main GUI window.

Must include:

* file selector
* start button
* progress bar
* log output

Must use:

```
PySide6
```

---

## ui/worker.py

Background execution.

Responsibilities:

* run ModManager
* manage thread pool
* report progress
* report logs

Must write failed mods to:

```
data/failed/<timestamp>.txt
```

---

# 8. Failure Handling

If a mod fails after maximum retries:

1 write mod filename to a failed list

Example:

```
data/failed/failed_2026-03-08.txt
```

---

# 9. Anti Detection Behavior

To reduce server blocking:

System must include:

* randomized delay between requests
* configurable delay range
* exponential retry backoff

Configured via `.env`.

---

# 10. CSV Output

Metadata must be stored in:

```
factorio_mods.csv
```

Each processed mod produces one row.

---

# 11. Future Expandability

The architecture must allow future additions:

Possible features:

* CLI interface
* FastAPI server
* automated mod update scanning
* scheduled downloads
* mod dependency graph

This must be possible without rewriting core logic.

---

# 12. Development Rules

The coding agent must follow these rules:

1 All business logic must be outside GUI

2 Each module must have clear responsibility

3 Network code must implement retries

4 File downloads must use streaming

5 The project must run with:

```
pip install -r requirements.txt
python main.py
```

6 Code must be clean and documented

---

# 13. Expected Final Result

The final result should be:

A fully working Python desktop application that:

* reads a list of mod filenames
* fetches metadata
* downloads mods
* saves CSV
* logs progress
* handles failures

All implemented with modular architecture and `.env` configuration.

---

END OF SPECIFICATION
