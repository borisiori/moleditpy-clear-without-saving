# Changelog

## [2026.11.08]

### Changed

- Removed `run()` so the action no longer appears in the generic Plugins
  menu, where an accidental click would wipe the workspace (same decision
  as the copy_xyz plugin). The action is reachable from **File ▸ Clear
  without Saving** and `Ctrl+Shift+X` only.

## [2026.11.05]

### Added

- Initial version: File-menu action below New, `Ctrl+Shift+X`, resetting
  the 2D scene, 3D view, undo stack and file state without the
  unsaved-changes prompt; fallback to the prompted clear on older
  MoleditPy builds without `clear_all(skip_check=...)`.
