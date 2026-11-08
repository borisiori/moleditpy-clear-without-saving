# Clear Without Saving – MoleditPy Plugin

A lightweight plugin for [MoleditPy](https://github.com/HiroYokoyama/python_molecular_editor) that resets the whole workspace in one step, skipping the unsaved-changes dialog shown by New and Clear All.

Designed for workflows where you repeatedly import scratch files with no project worth saving: load, use, wipe, repeat — without a confirmation prompt every time.

## Features

- **One-step workspace reset:** Clears the 2D scene, the 3D view, the undo stack and the file state in a single action.
- **No confirmation dialog:** The action label already states the outcome, so the plugin does not ask again.
- **Keyboard shortcut:** `Ctrl+Shift+X`, placed right below **File ▸ New** where the other workspace actions live.
- **Graceful degradation:** On MoleditPy builds whose `clear_all()` has no `skip_check` parameter, it falls back to the standard prompted clear instead of failing.
- **Safe by construction:** The plugin only calls the existing core `clear_all(skip_check=True)` API; no core files are modified and nothing is written to disk.
- **MoleditPy integration:** Registered through the official plugin API (`add_menu_action`), so it appears in the Plugin Manager and can be disabled there at any time.

## Requirements

- MoleditPy >= 5.0.0, < 6.0.0
- Python 3
- PySide6-Essentials (bundled with MoleditPy)

No external command-line tools or extra dependencies.

## Installation

### Manual installation

1. Download [`clear_without_saving.py`](https://github.com/borisiori/moleditpy-clear-without-saving/blob/main/clear_without_saving.py).
2. Copy the file into your MoleditPy plugins directory (`~/.moleditpy/plugins/`).
3. Restart MoleditPy.
4. Use **File ▸ Clear without Saving** or press `Ctrl+Shift+X`.

The plugin may also become available through MoleditPy's official Plugin Installer if accepted into its plugin registry.

## Usage

1. Open, paste or import anything into MoleditPy.
2. When you are done with it, choose **File ▸ Clear without Saving** (or `Ctrl+Shift+X`).
3. The workspace resets immediately; **File ▸ New** and **Edit ▸ Clear All** keep their normal unsaved-changes prompt.

> **Note:** This action discards unsaved changes on purpose. If you ever want the prompt back, simply disable the plugin from the Plugin Manager.

## Tests

Headless pytest suite included:

```bash
QT_QPA_PLATFORM=offscreen python -m pytest tests/
```

## License

Copyright (c) 2026 borisiori

Licensed under the [GNU LGPL v3.0](LICENSE) or later — the same license as MoleditPy.
