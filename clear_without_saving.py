#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Clear Without Saving Plugin for MoleditPy
Adds a File-menu action (placed right below New) that resets the whole
workspace (2D scene, 3D view, undo stack and file state) without showing
the unsaved-changes prompt.
"""

import logging

PLUGIN_NAME = "Clear Without Saving"
PLUGIN_VERSION = "2026.11.08"
PLUGIN_SUPPORTED_MOLEDITPY_VERSION = ">=5.0.0, <6.0.0"
PLUGIN_AUTHOR = "borisiori"
PLUGIN_LICENSE = "LGPL-3.0-or-later"
PLUGIN_DESCRIPTION = (
    "Reset the 2D/3D workspace in one step (File menu, below New), "
    "skipping the unsaved-changes dialog"
)
PLUGIN_DEPENDENCIES = []
PLUGIN_TAGS = ["Utility"]
PLUGIN_CONTEXT = None

ACTION_LABEL = "Clear without Saving"


def initialize(context):
    """Register the File > Clear without Saving action, below New."""
    global PLUGIN_CONTEXT
    PLUGIN_CONTEXT = context
    context.add_menu_action(
        "File/" + ACTION_LABEL,
        lambda: clear_without_saving(context),
        shortcut="Ctrl+Shift+X",
    )
    _schedule_placement(context)


def _schedule_placement(context):
    """Move our action right below File > New once the menus are built.

    add_menu_action() only registers the entry; the PluginMenuManager turns
    it into a QAction at the end of the File menu only after every plugin's
    initialize() has returned. A zero-timeout timer fires on the next
    event-loop pass, when that QAction already exists and can be moved.
    """
    try:
        from PySide6.QtCore import QCoreApplication, QTimer

        if QCoreApplication.instance() is None:
            return
        mw = context.get_main_window()
        QTimer.singleShot(0, lambda: place_below_new(mw))
    except Exception:
        logging.exception("%s: could not schedule menu placement", PLUGIN_NAME)


def place_below_new(mw):
    """Relocate our File-menu entry so it sits directly below New."""
    try:
        menubar = mw.menuBar()
        for top in menubar.actions():
            if top.text().replace("&", "").lower() != "file":
                continue
            file_menu = top.menu()
            if file_menu is None:
                return
            actions = file_menu.actions()
            mine = next(
                (
                    a
                    for a in actions
                    if a.text().replace("&", "") == ACTION_LABEL
                ),
                None,
            )
            if mine is None:
                # Registration never landed; nothing to move.
                return
            file_menu.removeAction(mine)
            # Drop a divider left dangling when we were the last plugin entry.
            remaining = file_menu.actions()
            if remaining and remaining[-1].isSeparator():
                file_menu.removeAction(remaining[-1])
            labels = [a.text().replace("&", "") for a in file_menu.actions()]
            if "New" not in labels:
                # Unexpected menu layout; fall back to the end.
                file_menu.addAction(mine)
                return
            idx = labels.index("New")
            anchored = file_menu.actions()
            if idx + 1 < len(anchored):
                file_menu.insertAction(anchored[idx + 1], mine)
            else:
                file_menu.addAction(mine)
            return
    except Exception:
        logging.exception("%s: menu placement failed", PLUGIN_NAME)


def clear_without_saving(context):
    """Clear 2D and 3D state directly, bypassing the save prompt."""
    mw = context.get_main_window()
    manager = getattr(mw, "edit_actions_manager", None)
    clear_all = getattr(manager, "clear_all", None)
    if clear_all is None:
        logging.error("%s: main window has no clear_all action", PLUGIN_NAME)
        context.show_status_message(
            f"{PLUGIN_NAME}: not supported by this MoleditPy build", 5000
        )
        return

    try:
        clear_all(skip_check=True)
    except TypeError:
        # Older builds without the skip_check parameter: fall back to the
        # prompting path so the action still clears the document.
        logging.warning(
            "%s: clear_all has no skip_check; falling back to prompted clear",
            PLUGIN_NAME,
        )
        clear_all()
    except Exception:
        logging.exception("%s: failed to clear the document", PLUGIN_NAME)
        context.show_status_message(f"{PLUGIN_NAME}: failed to clear", 5000)
