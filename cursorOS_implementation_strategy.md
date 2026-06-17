# CursorOS — Phased Implementation Strategy

> A Windows desktop AI overlay agent. Activates via global hotkey, reads OS context via the accessibility tree, and executes AI-decided actions OS-wide.
>
> **Stack:** Python, pywin32, Windows UI Automation, Claude API (claude-sonnet-4-20250514), OmniParser (local), system tray via `pystray`, overlay UI via `tkinter` or `PyQt6`.
>
> **Rule:** Complete all tests for a phase before starting the next. Each phase produces a working, independently testable slice of the system.

---

## Phase 0 — Project Scaffold

### Goal
Set up the project structure, environment, and tooling so every subsequent phase has a clean foundation.

### Tasks
- Create the project directory structure:
  ```
  cursorOS/
  ├── core/
  ├── tasks/
  ├── overlay/
  ├── tests/
  │   ├── unit/
  │   └── system/
  ├── config/
  └── main.py
  ```
- Set up a Python virtual environment (`venv`)
- Create `requirements.txt` with initial dependencies: `pywin32`, `pystray`, `Pillow`, `anthropic`, `pytest`, `python-dotenv`
- Create a `.env` file template with `ANTHROPIC_API_KEY=` as a placeholder
- Create a `config/settings.py` that loads environment variables and holds global constants (hotkey combo, model name, max tokens, OmniParser path)
- Create a `main.py` entry point that does nothing except print "CursorOS booting..." and exit cleanly

### Tests — Phase 0

**Unit tests:**
- Verify `config/settings.py` loads without error
- Verify that accessing `ANTHROPIC_API_KEY` from settings raises a clear error when the `.env` value is missing or empty

**System tests:**
- Run `main.py` and assert it exits with code 0
- Assert the full directory structure exists after setup

---

## Phase 1 — System Tray + Hotkey Activation

### Goal
The agent lives in the system tray. A global hotkey activates it. Nothing else happens yet — just the shell.

### Tasks
- Use `pystray` to create a system tray icon with a right-click menu containing: "Activate" and "Quit"
- Register a global hotkey (e.g. `Ctrl+Shift+Space`) using the `keyboard` library
- When the hotkey fires or "Activate" is clicked, print "Agent activated" to console — this is the activation signal hook that all later phases will attach to
- Ensure the tray icon persists in the background and does not block the main thread
- Tray runs in a separate thread; hotkey listener runs in another; main thread stays alive

### Tests — Phase 1

**Unit tests:**
- Test that the hotkey registration function does not raise an exception
- Test that the activation signal hook is callable and runs without error

**System tests:**
- Launch the app, verify the tray icon appears (check process is running)
- Simulate the hotkey programmatically and assert the activation hook fires
- Click "Quit" from tray menu and assert the process exits cleanly

---

## Phase 2 — Overlay UI

### Goal
When the agent activates, a floating overlay window appears at the center of the screen. The user can type into it and submit. The overlay can be dismissed with `Escape`.

### Tasks
- Build a minimal overlay window using `tkinter` or `PyQt6`:
  - Always-on-top, borderless, centered on screen
  - Contains a single text input field and a submit button
  - Pressing `Enter` or clicking submit captures the input text and prints it to console
  - Pressing `Escape` closes the overlay without action
- Hook overlay launch into the activation signal from Phase 1
- Overlay should open and close cleanly without leaving ghost windows or hanging threads

### Tests — Phase 2

**Unit tests:**
- Test that the overlay window initialises without error
- Test that the submit handler correctly captures and returns the input string
- Test that the escape handler closes the window and returns `None`

**System tests:**
- Trigger activation hotkey and assert the overlay window appears (check window title or process state)
- Programmatically submit a test string and assert it is captured correctly
- Programmatically send `Escape` and assert the overlay closes

---

## Phase 3 — OS Context Layer (Accessibility Tree)

### Goal
When the user submits a query, before calling the LLM, the agent reads OS context — specifically, all open File Explorer windows and their paths.

### Tasks
- Create `core/os_context.py`
- Implement `get_open_explorer_windows()` using the `Shell.Application` COM object via `win32com.client`:
  - Returns a list of dicts: `{ "title": str, "path": str }`
  - Handles the case where no Explorer windows are open (returns empty list)
- Implement `get_directory_contents(path: str)` using `os.scandir`:
  - Returns a list of dicts: `{ "name": str, "type": "file"|"folder", "extension": str, "modified": datetime }`
  - Handles permission errors gracefully
  - If the directory has more than 200 items, return the first 200 and include a `"truncated": True` flag
- Context is returned as structured text, not raw objects, so it can be passed directly to the LLM

### Tests — Phase 3

**Unit tests:**
- Test `get_open_explorer_windows()` with a mocked COM object — assert it returns the correct list format
- Test `get_directory_contents()` with a temporary directory containing known files — assert correct types, names, and extensions are returned
- Test `get_directory_contents()` with an empty directory — assert it returns an empty list
- Test `get_directory_contents()` with a directory of 300 items — assert it returns exactly 200 and sets `truncated: True`
- Test `get_directory_contents()` on a path that does not exist — assert it raises a clear, handled exception

**System tests:**
- Open a real File Explorer window to a known path, call `get_open_explorer_windows()`, and assert the path appears in results
- Call `get_directory_contents()` on a real directory and assert all files in that directory appear in the output

---

## Phase 4 — LLM Integration (Core Agent Loop)

### Goal
The agent takes a user query plus OS context and calls Claude to decide what to do. No actions are executed yet — only the decision is returned and printed.

### Tasks
- Create `core/agent.py`
- Implement `think(user_query: str, context: dict) -> dict`:
  - Builds a structured prompt: system prompt (role, available tools, constraints) + user query + OS context as a formatted string
  - Calls Claude API using `claude-sonnet-4-20250514`
  - Parses the response into a structured action plan: `{ "action": str, "params": dict, "explanation": str }`
  - Returns the action plan dict
- The system prompt must tell Claude it can only return one of these actions: `organise_folder`, `find_file`, `change_cursor`, `clarify` (for when the intent is unclear)
- Implement a `clarify` fallback — if Claude returns `clarify`, the overlay should display Claude's clarifying question back to the user
- Add token usage logging to console for every call (useful for cost tracking during development)

### Tests — Phase 4

**Unit tests:**
- Test `think()` with a mocked Anthropic client — assert it calls the API with the correct model and that the response is parsed into the expected dict shape
- Test that an API error is caught and returns a safe fallback response rather than crashing
- Test prompt construction — assert the system prompt, user query, and context all appear in the messages sent to the API

**System tests:**
- Call `think()` with a real API call and a query like "organise my downloads folder" — assert the returned action is `organise_folder`
- Call `think()` with a vague query like "do something" — assert Claude returns `clarify` and includes a question string

---

## Phase 5 — Task 1: Smart Folder Organisation

### Goal
The agent can organise any open folder. User picks from the list of open Explorer windows in the overlay, Claude decides the scheme, files are moved, and an action log is shown.

### Tasks
- Create `tasks/organise_folder.py`
- Implement `run(path: str)`:
  - Calls `get_directory_contents(path)` from Phase 3
  - Sends contents to Claude with a specific prompt: given these files, propose a subfolder structure and assign each file to a subfolder. Return as JSON: `{ "subfolders": [ { "name": str, "files": [str] } ] }`
  - Validates the proposed structure (no files go missing, no invalid folder names)
  - Creates subfolders using `os.makedirs(exist_ok=True)`
  - Moves files using `shutil.move`
  - Returns an action log: list of `{ "action": "created_folder"|"moved_file", "name": str, "destination": str }`
- Update the overlay to display the action log after execution in a scrollable read-only text area
- Update the overlay flow for this task:
  1. User types "organise my folder"
  2. Agent detects open Explorer windows and lists them in the overlay
  3. User clicks or types the number of the folder they want
  4. Agent runs organisation and shows the log

### Tests — Phase 5

**Unit tests:**
- Test `run()` with a mocked Claude response — assert the correct subfolders are created and files are assigned
- Test validation: if Claude proposes a subfolder for a file that doesn't exist in the directory, assert it is skipped with a warning
- Test that `run()` on an already-organised folder (only one file type) creates a single correct subfolder
- Test action log format — assert every move is recorded correctly

**System tests:**
- Create a temporary directory with 10 mixed files (`.pdf`, `.jpg`, `.py`, `.txt`)
- Run `run()` and assert subfolders were created and all 10 files were moved
- Assert no files were lost (total file count before = total after)
- Assert the action log contains an entry for every file moved

---

## Phase 6 — Task 2: Find a File by Description

### Goal
User describes a file in natural language. Agent searches programmatically first. If not found, falls back to OmniParser vision scan of the visible screen.

### Tasks
- Create `tasks/find_file.py`
- Implement `search_programmatic(query: str) -> list`:
  - Sends the user's natural language query to Claude to extract search parameters: `{ "name_keywords": [str], "extension": str|null, "date_range": { "after": date|null, "before": date|null } }`
  - Uses `os.walk` starting from the user's home directory to find matching files
  - Returns up to 5 best matches as a list of full paths
- Implement `search_visual(query: str) -> list` (vision fallback):
  - Takes a screenshot using `Pillow` (`ImageGrab.grab()`)
  - Passes the screenshot to OmniParser (local) to extract visible file/folder names
  - Asks Claude whether any of the visible items match the query
  - Returns matches found on screen
- Implement `run(query: str)`:
  - Runs `search_programmatic` first
  - If results are found, return them
  - If no results, run `search_visual` as fallback
  - Display results in the overlay with full paths; clicking a result opens the file's location in Explorer

### Tests — Phase 6

**Unit tests:**
- Test `search_programmatic()` with a mocked Claude extraction — assert it produces correct `os.walk` filter parameters
- Test that `search_programmatic()` returns an empty list (not an error) when no files match
- Test `search_visual()` with a mocked OmniParser response — assert it correctly passes visible file names to Claude
- Test `run()` — assert it calls programmatic first and only calls visual if programmatic returns empty

**System tests:**
- Create a temp file with a distinctive name, run `search_programmatic()` with a query describing it, assert it is found
- Simulate OmniParser returning a list of visible filenames and assert `search_visual()` returns the correct match
- Test full `run()` end-to-end: query a file that exists → assert result returned without hitting vision fallback

---

## Phase 7 — Task 3: Change Mouse Cursor

### Goal
User describes a cursor in natural language. Agent searches the internet, downloads a `.cur` or `.ani` file, and applies it system-wide.

### Tasks
- Create `tasks/change_cursor.py`
- Implement `search_cursor(description: str) -> str`:
  - Uses Claude with web search tool enabled to find a direct download URL for a `.cur` or `.ani` file matching the description
  - Returns the download URL or `None` if not found
- Implement `download_cursor(url: str) -> Path`:
  - Downloads the file to a local `cursors/` directory inside the project
  - Validates the downloaded file is a valid `.cur` or `.ani` file (check magic bytes or extension)
  - Returns the local file path
- Implement `apply_cursor(path: Path)`:
  - Calls `ctypes.windll.user32.SystemParametersInfoW` with `SPI_SETCURSORS` to apply the cursor system-wide
  - Stores the previous cursor path so it can be restored
- Implement `restore_cursor()`:
  - Restores the previously saved system cursor
- Implement `run(description: str)`:
  - Runs the full pipeline: search → download → apply
  - Shows the cursor name and source in the overlay action log
  - Adds a "Restore original cursor" button to the overlay after applying

### Tests — Phase 7

**Unit tests:**
- Test `search_cursor()` with a mocked Claude web search response — assert it extracts and returns a valid URL
- Test `download_cursor()` with a real `.cur` file URL — assert the file is saved locally and passes validation
- Test `download_cursor()` with an invalid URL — assert it raises a handled exception, not a crash
- Test `apply_cursor()` with a mocked `ctypes` call — assert `SystemParametersInfoW` is called with the correct parameters
- Test `restore_cursor()` — assert it calls `SystemParametersInfoW` with the saved original path

**System tests:**
- Run the full pipeline with a simple description like "arrow cursor" and assert a `.cur` file is downloaded and the apply call succeeds
- Apply a cursor, call `restore_cursor()`, and assert the system cursor is restored

---

## Phase 8 — Action Log UI + Trust Layer

### Goal
Every action the agent takes is shown to the user in a clear, readable log in the overlay. The user can undo the last action. This directly addresses the 70.8% of survey respondents who cited control and trust as their hesitation.

### Tasks
- Create `core/action_log.py`:
  - Maintains a session log of all actions taken: `{ "timestamp", "task", "action", "detail" }`
  - Persists the log to a local JSON file at the end of each session
- Update all three task modules to write to the action log after every file move, file found, or cursor changed
- Update the overlay to show the log after every task completes in a scrollable panel
- Implement `undo_last_action()`:
  - For folder organisation: reverse the last batch of `shutil.move` calls
  - For cursor change: call `restore_cursor()`
  - For file find: no undo needed (read-only)
- Add an "Undo" button to the overlay that appears after any action that can be undone

### Tests — Phase 8

**Unit tests:**
- Test that every task writes a correctly formatted entry to the action log
- Test `undo_last_action()` for folder organisation — assert files are moved back to their original locations
- Test `undo_last_action()` for cursor change — assert `restore_cursor()` is called
- Test that the log persists correctly to JSON and can be reloaded

**System tests:**
- Run folder organisation on a temp directory, then call `undo_last_action()`, and assert all files are back in their original locations
- Run cursor change, click undo, and assert the system cursor is restored
- Assert that after a full session, the JSON log file exists and contains entries for every action taken

---

## Phase 9 — Integration + End-to-End Hardening

### Goal
All phases work together as a single coherent app. Edge cases are handled. The app is stable enough for a demo.

### Tasks
- Wire up all phases through `main.py`:
  - Tray → hotkey → overlay → agent loop → task execution → action log → undo
- Handle the large directory edge case from Phase 3: if `truncated: True`, show a warning in the overlay before proceeding with organisation
- Add a loading indicator to the overlay while the LLM call is in progress (spinner or animated dots)
- Add error handling at every layer — no unhandled exceptions should crash the app silently; all errors should surface as readable messages in the overlay
- Add a `--debug` CLI flag that enables verbose console logging of all API calls, OS queries, and file operations
- Test the full demo script end-to-end:
  1. Launch app
  2. Open a test folder in Explorer
  3. Trigger "organise my folder" via hotkey
  4. Pick the folder in the overlay
  5. Confirm organisation runs and log appears
  6. Undo and confirm files are restored
  7. Trigger "find my ML PDF from last month"
  8. Confirm file is found and path is shown
  9. Trigger "give me a crosshair cursor"
  10. Confirm cursor changes
  11. Undo cursor change
  12. Quit from tray

### Tests — Phase 9

**Unit tests:**
- Test that all error states (API timeout, file permission error, no Explorer windows open, cursor URL not found) produce user-facing messages in the overlay rather than silent failures
- Test that the `--debug` flag enables logging without affecting behaviour

**System tests:**
- Run the full demo script above manually and assert every step completes without error
- Run the app for 10 consecutive activations with varied queries and assert no memory leaks or hanging threads (check process memory before and after)
- Assert that after quitting from the tray, all background threads terminate and no process remains

---

## Testing Quick Reference

| Phase | Key unit test focus | Key system test focus |
|---|---|---|
| 0 | Config loads, env validation | Entry point exits cleanly |
| 1 | Hotkey registration, activation hook | Hotkey fires, tray quits |
| 2 | Overlay init, submit/escape handlers | Overlay opens, captures input |
| 3 | COM mock, directory listing, truncation | Real Explorer window detected |
| 4 | API mock, prompt shape, error fallback | Real API call returns correct action |
| 5 | Organisation logic, file count preservation | Files moved, none lost |
| 6 | Search param extraction, fallback routing | Real file found programmatically |
| 7 | URL extraction, file validation, ctypes mock | Full cursor pipeline runs |
| 8 | Log format, undo reversal | Undo restores original state |
| 9 | All error paths surface to UI | Full demo script passes |

---

## Notes for the Code Editor

- Use `pytest` for all tests. Each phase's tests live in `tests/unit/test_phaseN.py` and `tests/system/test_phaseN.py`.
- Mock external dependencies (Anthropic API, COM objects, ctypes, OmniParser) in all unit tests. Never make real API calls in unit tests.
- System tests may make real API calls and perform real file operations — always use `tmp_path` (pytest fixture) for file system tests so nothing permanent is touched.
- Do not proceed to the next phase until `pytest tests/` passes with zero failures for the current phase.
- Keep each module focused — `core/` is for infrastructure (context, agent loop, logging), `tasks/` is for task execution, `overlay/` is for UI. No cross-importing between `tasks/` modules.
