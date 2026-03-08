# Quick Start Guide - Factorio Mod Manager

## Prerequisites
- Python 3.10+
- Internet connection

## 1. Installation (First Time Only)

### Windows
```bash
# Open PowerShell or Command Prompt in the project folder

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Linux/Mac
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Prepare Your Mod List

Create a text file (e.g., `my_mods.txt`) with one mod filename per line:

```
aai-vehicles-hauler_0.7.3.zip
bobsgoldfurnace_0.18.0.zip
factorio-very-beltworks_0.2.1.zip
```

**Format:** `modname_version.zip`
- Mod names can contain letters, numbers, and hyphens
- Version must be present after underscore
- Must end with `.zip`

### Example: example_mods.txt
We've provided an example file. Edit it with your actual mod filenames.

## 3. Run the Application

### Windows
```bash
# Make sure venv is activated
venv\Scripts\activate

# Run the app
python main.py
```

### Linux/Mac
```bash
# Activate venv
source venv/bin/activate

# Run the app
python main.py
```

## 4. Using the GUI

1. **Load File**
   - Click "Browse..." button
   - Select your mod list file (e.g., `my_mods.txt`)

2. **Configure Options** (Optional)
   - ✅ Download mod ZIP files - Download the actual mod ZIPs
   - ✅ Save mod images - Download mod thumbnails
   - ☐ Save releases as CSV - Save detailed release info
   - ☐ Include changelog - Add changelog column to CSV
   - ☐ Enable multithreading - Process faster (unstable on slow networks)

3. **Start Processing**
   - Click "Start" button
   - Watch the progress bar and log output
   - Processing will continue in background

4. **View Results**
   - Open the **CSV file** to see all metadata
   - Check **downloads/** folder for mod ZIPs
   - Check **images/** folder for mod images
   - Check **failed/** folder if any mods failed

## 5. Output Files

After processing, you'll find:

```
factorio_mods.csv          - Main metadata file
data/
  downloads/               - Downloaded mod ZIP files
  images/                  - Mod thumbnail images
  releases/                - Detailed release CSV files
  failed/                  - Failed mods list (if any)
```

## Troubleshooting

### "Invalid filename format"
Make sure filenames match: `modname_version.zip`
- ✅ Valid: `aai-vehicles-hauler_0.7.3.zip`
- ❌ Invalid: `my-mod.zip` (missing version)

### "Could not fetch metadata"
- Check internet connection
- Verify mod exists on https://mods.factorio.com
- Some very old mods might not be in the API

### Download failures
- Check your internet connection
- Try disabling multithreading
- Increase MAX_RETRIES in .env file

### Running slow
- Enable multithreading checkbox
- Reduce number of mods in your list
- Check internet speed

## Configuration (.env)

Edit `.env` file for advanced options:

```env
# Mirrors for downloading (space-separated)
MIRROR_URLS=https://mods-storage.re146.dev

# How many times to retry failed requests
MAX_RETRIES=5

# Request timeout in seconds
REQUEST_TIMEOUT=12

# Add random delays to avoid detection (in seconds)
RANDOM_DELAY_MIN=0.5
RANDOM_DELAY_MAX=2.0

# Number of parallel workers
MAX_WORKERS=4

# Enable/disable features
SAVE_IMAGES=true
SAVE_RELEASES=false
DOWNLOAD_ZIPS=true
SAVE_CHANGELOG=false
```

## Example Workflow

```
1. Edit example_mods.txt with your mod list
2. Run: python main.py
3. Click Browse → select example_mods.txt
4. Click Start
5. Wait for processing to complete
6. Click "Open CSV file" to view results
7. Check data/downloads/ for mod files
```

## Tips

- Start with a small list (5-10 mods) to test
- Don't use multithreading on slow connections
- Processing takes ~2-3 seconds per mod on average
- Failed mods are logged - try again later
- Large ZIPs may take time to download

## Advanced Usage

See [README.md](README.md) for:
- Detailed architecture
- API reference
- Programmatic access
- Custom configuration

---

**Need Help?** Check the main [README.md](README.md) for detailed documentation.
