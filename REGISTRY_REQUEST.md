# Registry request — Register New Plugin: Clear Without Saving

Submitted and under review: https://github.com/HiroYokoyama/moleditpy-plugins/issues/61
Born from python_molecular_editor#191, where the maintainer suggested the
plugin approach over a core change; v2026.11.08 is the asset proposed
for registration.

---

**Title:** Register New Plugin: Clear Without Saving

- **Plugin Source URL:** https://github.com/borisiori/moleditpy-clear-without-saving/releases/download/v2026.11.08/clear_without_saving.py
- **Target Action:** Register a New Plugin
- **Plugin ID:** `clear_without_saving`
- **Expected SHA-256 Hash:** 6a7776d456b48d020e94157661ca9b6d31b68b0ee735e141f4ae6fb796a254a3
- **Tags:** Utility
- **Dependencies:** None
- **Visibility:** Yes, make this plugin visible in the registry manager.
- **Supported MoleditPy Version:** >=5.0.0, <6.0.0
- **Supported Python Version:** >=3.10, <3.15

## Release procedure (for future versions)

1. Update `PLUGIN_VERSION` in `clear_without_saving.py` (date format).
2. Commit on `main`; the pytest suite must be green.
3. `git tag v<VERSION>` and push the tag.
4. GitHub Release `v<VERSION>` attaching `clear_without_saving.py`;
   download the asset back and run `sha256sum` over the downloaded file.
5. Open an "Update an Existing Plugin" issue with the new URL + hash,
   keeping the Plugin ID.
6. Sync: `cp clear_without_saving.py ~/.moleditpy/plugins/`
