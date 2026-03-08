# Three New Improvements - Settings, Environment Configuration & Version Management

## 1. VS Code Environment File Support (FIXED)

### The Problem
You received this warning:
```
An environment file is configured but terminal environment injection is disabled. 
Enable "python.terminal.useEnvFile" to use environment variables from .env files in terminals.
```

### The Solution
Created `.vscode/settings.json` with the following configuration:

```json
{
    "python.terminal.useEnvFile": true,
    "python.terminal.executeInFileDir": true,
    ...
}
```

### What This Does
- ✅ Automatically loads environment variables from `.env` file when you open terminals
- ✅ Eliminates the warning message
- ✅ Environment variables (REQUEST_TIMEOUT, MAX_WORKERS, etc.) are available in all terminals
- ✅ Works with `python main.py` and custom commands

### Result
No more warnings. Your terminal inherits all settings from `.env` automatically!

---

## 2. GUI Settings Panel (NEW FEATURE)

### What's New
Added a **Settings button** in the GUI that opens a full settings configuration dialog.

### How to Use

1. **Open the Settings Dialog:**
   - Click the "Settings" button in the bottom-right of the GUI
   - A new window opens with all configurable options

2. **Configure Network Settings:**
   - **Request Timeout** (5-300 seconds, default 120)
     - How long to wait for downloads before timeout
     - Increase for slow connections or large files
   - **Max Retries** (1-20, default 5)
     - How many times to retry failed downloads
   - **Backoff Base** (1.0-3.0, default 1.4)
     - Exponential backoff multiplier for retries
   - **Random Delay Min/Max** (seconds)
     - Delay between requests to avoid rate limiting

3. **Performance Settings:**
   - **Max Workers** (1-16, default 4)
     - Concurrent download threads
     - Higher = faster, but uses more bandwidth/connections

4. **Feature Flags:**
   - ✓ **Save Images** - Download mod thumbnails
   - ✓ **Save Releases** - Save version history
   - ✓ **Download ZIPs** - Download actual mod files
   - ✓ **Save Changelog** - Include changelog in CSV

5. **Mirror URLs:**
   - Primary mirror URL for mod downloads
   - Default: `https://mods-storage.re146.dev`

### Saving Settings

1. **Click "Save Settings"**
   - All changes are written to `.env` file
   - Settings persist across application restarts
   - Confirmation message shows success

2. **Click "Reset to Defaults"**
   - Reverts all settings to factory defaults
   - Asks for confirmation before resetting

3. **Click "Close"**
   - Closes dialog without saving

### Important Note
⚠️ **Restart the application after saving settings** to ensure the new values are used.

---

## 3. Version Management & Release Tracking

### What Changed

#### Download Behavior (Unchanged - Already Correct)
✅ **Only latest version downloads:**
```python
# In mod_manager.py, line 115
releases = mod_data.get('releases', []) or []
latest = releases[-1] if releases else {}  # Only gets LAST (latest) release
final_version = latest_version or local_version
# Downloads only this version, not all versions
```

The application correctly downloads only the **LATEST** version of each mod, not all historical versions.

#### Release Files (IMPROVED)
The releases CSV file now:
1. **Shows ALL version history** (for reference)
2. **Marks the latest version** with "YES" in `is_latest` column
3. **Sorts by date** (newest first)

**Example releases CSV structure:**
```
version,file_name,released_at,sha1,dependencies,is_latest
1.0.5,my-mod_1.0.5.zip,2024-01-15,...,YES
1.0.4,my-mod_1.0.4.zip,2024-01-01,...,
1.0.3,my-mod_1.0.3.zip,2023-12-20,...,
```

**Benefits:**
- You can see version history and release dates
- Easy to identify which version was downloaded (marked with "YES")
- Useful for tracking updates and dependencies
- No extra downloads - still downloads only latest ZIP

---

## Settings File Details

### Location
`.env` file in project root

### Key Settings

```ini
# Network Timeouts
REQUEST_TIMEOUT=120          # Seconds to wait for downloads (increased for large files)
MAX_RETRIES=5               # How many times to retry failed operations
BACKOFF_BASE=1.4            # Exponential backoff multiplier (1.4^attempt * base_delay)

# Concurrency
MAX_WORKERS=4               # Concurrent download threads

# Delays (prevent rate limiting)
RANDOM_DELAY_MIN=0.5        # Minimum delay between requests (seconds)
RANDOM_DELAY_MAX=2.0        # Maximum delay between requests (seconds)

# Download Configuration
MIRROR_URLS=https://mods-storage.re146.dev    # Primary mod source

# Feature Flags
SAVE_IMAGES=true            # Download thumbnails
SAVE_RELEASES=false         # Save version history CSVs
DOWNLOAD_ZIPS=true          # Download actual mod files
SAVE_CHANGELOG=false        # Include changelog in CSV
```

---

## Files Modified

### New Files Created
1. **`.vscode/settings.json`** - VS Code environment configuration
2. **`ui/settings_dialog.py`** - Settings GUI dialog (280+ lines)

### Files Updated
1. **`ui/app.py`** - Added Settings button and handler
2. **`core/mod_manager.py`** - Enhanced release tracking with version markers

---

## Quick Reference

### To Change Settings
1. Click **Settings** button in GUI
2. Adjust values
3. Click **Save Settings**
4. **Restart application**
5. Changes take effect

### To Reset to Defaults
1. Click **Settings** button
2. Click **Reset to Defaults**
3. Click **Save Settings** (to confirm reset)
4. **Restart application**

### To Check Current Settings
Open `.env` file in text editor to see all current values

### To Verify Version Downloads
Check the `data/releases/` folder:
- Each mod gets its own CSV file
- Latest version marked with "YES" in `is_latest` column
- All historical versions shown for reference

---

## Testing

To verify the settings work:

```bash
# Start application
python main.py

# Try different timeout values
# Select Settings → Change Request Timeout → Save
# Download a large mod to see the new timeout in effect

# Or modify .env directly
# REQUEST_TIMEOUT=180
# Then restart and process mods
```

---

## Troubleshooting

### "Settings won't save"
- Check that `.env` file exists and is readable
- Ensure you have write permissions
- Try manually editing `.env` file directly

### "Changes don't take effect"
- ⚠️ **You MUST restart the application** after saving settings
- Changes are not applied to already-running instances

### "How do I know what values to use?"
- **Timeout:** 120 seconds works for most cases, increase to 180+ for slow connections
- **Max Retries:** 5-10 is reasonable, 20 for very unstable connections  
- **Max Workers:** 4-8 is good for most systems, don't exceed your bandwidth
- **Delays:** Increase if you get rate-limited (429 errors)

### "My settings got reset"
- Check if you clicked "Reset to Defaults"
- Or check if `.env` was modified by another process
- Backup important custom settings before testing

---

## Summary of Improvements

| Feature | Before | After |
|---------|--------|-------|
| Env vars in terminal | ❌ Warning | ✅ Works automatically |
| Customize settings | Text editor only | ✅ GUI settings dialog |
| Timeout adjustment | Edit .env file | ✅ GUI slider |
| Version history | Not visible | ✅ Visible in CSV |
| Latest version marked | No indicator | ✅ "is_latest" column |
| Feature toggle | Edit .env | ✅ GUI checkboxes |

All improvements maintain backward compatibility. Your application works exactly as before, but now with better configurability!
