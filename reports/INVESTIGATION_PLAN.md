# GUI Freeze/Crash Investigation & Fix Plan

## Problem Statement
- GUI crashes or freezes when selecting all options
- Never completes a task
- No visible feedback to user (errors only in log files)
- User has tried multiple times with consistent failures

## Investigation Plan

### Phase 1: Diagnosis (Check Current Code)
1. **UI Flow Analysis** (ui/app.py)
   - How are options captured from user input?
   - How are they passed to the worker?
   - Are there any blocking calls on the main thread?
   - Check signal/slot connections for deadlocks

2. **Worker Thread Analysis** (ui/worker.py)
   - How does it receive options/mods list?
   - Are there proper try-catch blocks?
   - Are errors being properly emitted as signals?
   - Check for infinite loops or blocking I/O on worker thread

3. **Core Processing Analysis** (core/mod_manager.py)
   - Are there long operations without yielding?
   - Are there any deadlocks or race conditions?
   - Check exception handling

4. **Service Layer Analysis** (services/)
   - Download timeouts configured?
   - API call error handling?
   - Network issues being caught and reported?

### Phase 2: Identify Root Causes
Likely issues to look for:
- [ ] Main thread blocked by worker operations
- [ ] Worker thread throwing exceptions not caught/reported
- [ ] Infinite loops in mod processing
- [ ] Memory leaks causing slowdown
- [ ] Event queue being blocked
- [ ] Signals not properly connected
- [ ] Long operations without progress updates

### Phase 3: Implement Fixes
1. **Enhance UI Error Display**
   - Add error/status label in main window
   - Display real-time error messages to user
   - Show progress details (current mod, operation)

2. **Improve Error Handling**
   - Wrap all worker operations in try-catch
   - Emit error signals with descriptive messages
   - Handle cancellation gracefully

3. **Add Timeouts & Safeguards**
   - Set per-operation timeouts
   - Implement worker thread watchdog
   - Add cancellation mechanism

4. **Ensure Proper Threading**
   - Verify no blocking calls on main thread
   - Ensure worker runs in separate thread
   - Proper signal/slot usage

### Phase 4: Testing & Validation
1. Test with various option combinations
2. Verify error messages appear in UI
3. Confirm application doesn't freeze
4. Check logs for any warnings
5. Test cancellation works

## Expected Outcomes
✅ GUI never freezes regardless of options selected
✅ Clear error messages displayed in UI when issues occur
✅ Progress feedback shown in real-time
✅ User can cancel operations at any time
✅ Application handles network errors gracefully
✅ Logs available for detailed debugging

## Timeline
- Phase 1: 10-15 minutes (code analysis)
- Phase 2: 5 minutes (identify issues)
- Phase 3: 20-30 minutes (implement fixes)
- Phase 4: 10 minutes (testing)
Total: ~45-60 minutes

---

## Key Files to Examine
1. `ui/app.py` - Main UI window, option handling
2. `ui/worker.py` - Background worker thread
3. `core/mod_manager.py` - Core processing logic
4. `services/downloader.py` - Download operations
5. `services/factorio_api.py` - API operations
