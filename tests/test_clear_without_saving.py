"""Headless tests for the Clear Without Saving plugin."""
import importlib.util
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PLUGIN_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "clear_without_saving.py"
)


def load_plugin():
    spec = importlib.util.spec_from_file_location(
        "clear_without_saving", PLUGIN_FILE
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeContext:
    """Minimal stand-in for the MoleditPy PluginContext."""

    def __init__(self, mw):
        self.mw = mw
        self.menu_actions = []
        self.status_messages = []

    def add_menu_action(self, path, callback, shortcut=None):
        self.menu_actions.append((path, callback, shortcut))

    def get_main_window(self):
        return self.mw

    def show_status_message(self, text, msec=0):
        self.status_messages.append((text, msec))


class FakeEditActionsManager:
    """Records how clear_all is invoked."""

    def __init__(self, supports_skip_check=True):
        self.supports_skip_check = supports_skip_check
        self.calls = []

    def clear_all(self, skip_check=False):
        if not self.supports_skip_check and skip_check:
            # Simulate an older build without the skip_check parameter.
            raise TypeError(
                "clear_all() got an unexpected keyword argument 'skip_check'"
            )
        self.calls.append(skip_check)
        return True


class FakeMainWindow:
    def __init__(self, manager=None):
        self.edit_actions_manager = manager


# --- Metadata -----------------------------------------------------------


def test_metadata_fields():
    """All PLUGIN_* metadata required by the registry is present."""
    clear = load_plugin()
    for field in (
        "PLUGIN_NAME",
        "PLUGIN_VERSION",
        "PLUGIN_SUPPORTED_MOLEDITPY_VERSION",
        "PLUGIN_AUTHOR",
        "PLUGIN_LICENSE",
        "PLUGIN_DESCRIPTION",
        "PLUGIN_TAGS",
    ):
        value = getattr(clear, field, None)
        assert value, f"missing or empty metadata: {field}"
    # An empty dependency list is valid: the plugin needs nothing extra.
    assert isinstance(clear.PLUGIN_DEPENDENCIES, list)


def test_no_run_function():
    """No run(): keeps the destructive action out of the generic Plugins
    menu (same decision as the accepted copy_xyz plugin)."""
    clear = load_plugin()
    assert not hasattr(clear, "run")
    assert hasattr(clear, "initialize")


# --- Registration -------------------------------------------------------


def test_initialize_registers_file_action_with_shortcut():
    """initialize() registers File/Clear without Saving with Ctrl+Shift+X."""
    clear = load_plugin()
    context = FakeContext(FakeMainWindow())

    clear.initialize(context)

    assert len(context.menu_actions) == 1
    path, callback, shortcut = context.menu_actions[0]
    assert path == "File/" + clear.ACTION_LABEL
    assert shortcut == "Ctrl+Shift+X"
    assert callable(callback)


# --- Clear behaviour ----------------------------------------------------


def test_clear_passes_skip_check_true():
    """The clear bypasses the prompt: clear_all(skip_check=True)."""
    clear = load_plugin()
    manager = FakeEditActionsManager(supports_skip_check=True)
    context = FakeContext(FakeMainWindow(manager))

    clear.clear_without_saving(context)

    assert manager.calls == [True]
    assert context.status_messages == []


def test_clear_falls_back_on_older_builds():
    """Without skip_check support the plugin falls back to the prompted
    clear instead of failing."""
    clear = load_plugin()
    manager = FakeEditActionsManager(supports_skip_check=False)
    context = FakeContext(FakeMainWindow(manager))

    clear.clear_without_saving(context)

    # First call raised TypeError, fallback call ran without the argument.
    assert manager.calls == [False]
    assert context.status_messages == []


def test_clear_reports_missing_api():
    """A build without edit_actions_manager.clear_all reports instead of
    crashing."""
    clear = load_plugin()
    context = FakeContext(FakeMainWindow(manager=None))

    clear.clear_without_saving(context)

    assert len(context.status_messages) == 1
    assert "not supported" in context.status_messages[0][0]


def test_clear_reports_failure():
    """An exception inside clear_all is reported, never crashes."""
    clear = load_plugin()

    class BrokenManager:
        def clear_all(self, skip_check=False):
            raise RuntimeError("boom")

    context = FakeContext(FakeMainWindow(BrokenManager()))

    clear.clear_without_saving(context)

    assert len(context.status_messages) == 1
    assert "failed to clear" in context.status_messages[0][0]


# --- Menu placement -----------------------------------------------------


def test_menu_placement_below_new():
    """place_below_new() relocates the entry directly below File > New,
    cleaning up the plugin-section separator it detached from."""
    clear = load_plugin()
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QApplication, QMainWindow

    app = QApplication.instance() or QApplication([])
    win = QMainWindow()
    file_menu = win.menuBar().addMenu("File")

    new_action = QAction("&New", win)
    open_action = QAction("&Open Project...", win)
    quit_action = QAction("Quit", win)
    plugin_action = QAction(clear.ACTION_LABEL, win)

    for a in (new_action, open_action, quit_action):
        file_menu.addAction(a)
    file_menu.addSeparator()  # plugin section, as the menu manager builds it
    file_menu.addAction(plugin_action)

    clear.place_below_new(win)

    labels = [a.text().replace("&", "") for a in file_menu.actions()]
    assert labels == [
        "New",
        "Clear without Saving",
        "Open Project...",
        "Quit",
    ], f"unexpected order: {labels}"


def test_menu_placement_unexpected_layout_falls_back_to_end():
    """If File has no New entry the action is kept at the end instead of
    being lost."""
    clear = load_plugin()
    from PySide6.QtGui import QAction
    from PySide6.QtWidgets import QApplication, QMainWindow

    app = QApplication.instance() or QApplication([])
    win = QMainWindow()
    file_menu = win.menuBar().addMenu("File")
    file_menu.addAction(QAction("&Open Project...", win))
    plugin_action = QAction(clear.ACTION_LABEL, win)
    file_menu.addAction(plugin_action)

    clear.place_below_new(win)

    labels = [a.text().replace("&", "") for a in file_menu.actions()]
    assert clear.ACTION_LABEL in labels, "action was lost"
    assert labels[-1] == clear.ACTION_LABEL
