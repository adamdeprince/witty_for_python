"""Python bindings for the Wt (Web Toolkit) C++ library."""

from __future__ import annotations

import atexit as _atexit
import contextlib as _contextlib
from pathlib import Path as _Path
from typing import Iterator as _Iterator

# Import the C++ extension first so `_ext.__file__` resolves to the actual
# installed `.so` — which is where the bundled `_libs/` and `_wt_resources/`
# siblings also live. Using `__file__` of this module instead would resolve
# to the source-tree `__init__.py` under editable installs, where those
# bundled directories don't exist.
from . import _witty_for_python as _ext


# Wt's static assets (themes, JS, CSS, icons) shipped alongside the extension.
# The wheel install layout puts them at <package>/_wt_resources/. Wt's wthttpd
# needs to be told where to find them via its `--resources-dir` CLI flag.
resources_dir: str = str(_Path(_ext.__file__).resolve().parent / "_wt_resources")
"""Filesystem path to Wt's static resources bundled with this wheel.

Pass this to wthttpd via `--resources-dir`:

    server.set_server_configuration([
        "...", "--resources-dir", wt.resources_dir, ...,
    ])

The path resolves to a directory inside the installed package; nothing
to install or download at runtime.
"""

from ._witty_for_python import (
    AlignmentFlag,
    ContentDisposition,
    DateSignal,
    FileListSignal,
    FilePickerType,
    FileSignal,
    FileSizeSignal,
    ItemDataRole,
    JInt64Signal,
    ModelIndexMouseSignal,
    PopupTrigger,
    ScrollHint,
    SelectionBehavior,
    SortOrder,
    TemplateWidgetIdMode,
    TextFormat,
    Uint64PairSignal,
    UpdateLock,
    UploadedFile,
    ValidationResult,
    ValidationResultSignal,
    ValidationState,
    WBootstrap5Theme,
    WCalendar,
    WColor,
    WColorPicker,
    WCssTheme,
    WDateEdit,
    WDateValidator,
    WDoubleValidator,
    WEmailValidator,
    WFileDropWidget,
    WFileResource,
    WFileUpload,
    WInPlaceEdit,
    WIntValidator,
    WLengthValidator,
    WMemoryResource,
    WPasswordEdit,
    WRegExpValidator,
    WResource,
    WSplitButton,
    WStackedValidator,
    WStreamResource,
    WSuggestionPopup,
    WTemplate,
    WTextEdit,
    WTheme,
    WTimeEdit,
    WTimeValidator,
    WTimer,
    WValidator,
    _cleanup_all_connections,
    _live_connection_count,
    BoolSignal,
    Connection,
    Coordinates,
    DialogCode,
    DialogCodeSignal,
    DoubleSignal,
    EntryPointType,
    EventSignal,
    IntSignal,
    Key,
    KeyboardModifier,
    KeyEventSignal,
    LayoutDirection,
    MenuItemSignal,
    MouseButton,
    MouseEventSignal,
    Orientation,
    SelectionMode,
    Signal,
    StandardButton,
    StandardButtonSignal,
    StringSignal,
    WAnchor,
    WApplication,
    WBadge,
    WBoxLayout,
    WBreak,
    WButtonGroup,
    WCheckBox,
    WComboBox,
    WContainerWidget,
    WDialog,
    WDoubleSpinBox,
    WEnvironment,
    WFormWidget,
    WGridLayout,
    WGroupBox,
    WHBoxLayout,
    WImage,
    WInteractWidget,
    WKeyEvent,
    WLabel,
    WLayout,
    WLineEdit,
    WLink,
    WMenu,
    WMenuItem,
    WMessageBox,
    WModelIndex,
    WMouseEvent,
    WNavigationBar,
    WObject,
    WPanel,
    WPoint,
    WPopupMenu,
    WProgressBar,
    WPushButton,
    WRadioButton,
    WSelectionBox,
    WServer,
    WSlider,
    WSpinBox,
    WStackedWidget,
    WTable,
    WTableCell,
    WTableColumn,
    WAbstractItemModel,
    WAbstractItemView,
    WAbstractListModel,
    WStandardItem,
    WStandardItemModel,
    WStringListModel,
    WTableRow,
    WTableView,
    WTabWidget,
    WText,
    WTextArea,
    WToolBar,
    WTreeView,
    WVBoxLayout,
    WWidget,
)

__version__ = "0.1.0"


# Every Signal/EventSignal/payload-typed Signal binding exposes
# `disconnect_all_slots()` to drop the C++ connections we opened through
# py_connect, releasing the Python-callable holder references they captured.
# Because nanobind-bound instances are not GC-tracked, the Python side
# cannot enumerate live signals to call that on — instead the C++ extension
# maintains a process-wide connection registry, and the atexit handler below
# tells it to disconnect every connection at once. See README "Shutdown
# warnings" for the (still-present) cosmetic leak diagnostic that remains.


def _cleanup_signal_slots() -> None:
    """Disconnect every Python-callable slot witty_for_python is holding.

    Called from an ``atexit`` handler registered below. Safe to invoke
    explicitly (e.g. between tests) — it is idempotent.
    """
    try:
        _cleanup_all_connections()
    except Exception:
        pass


_atexit.register(_cleanup_signal_slots)


@_contextlib.contextmanager
def update_lock(application: WApplication) -> _Iterator[bool]:
    """Take ``application``'s update lock for the duration of the ``with`` block.

    Use this from a Python thread that isn't the application's own worker
    thread (e.g. background work pushing updates). Yields ``True`` if the
    lock was acquired, ``False`` if the application is being torn down — in
    which case the body of the ``with`` block should not touch widgets.

    For most cross-thread work prefer :meth:`WServer.post`, which is the
    canonical Wt mechanism (lock-free for the caller; Wt acquires the lock
    on the worker thread before invoking your callback). ``update_lock`` is
    the lower-level escape hatch.
    """
    lock = UpdateLock(application)
    try:
        yield bool(lock)
    finally:
        # Releasing the C++ lock = destroying the Python wrapper. `del`
        # decrefs to zero on CPython, invoking the C++ destructor immediately.
        del lock

__all__ = [
    "AlignmentFlag",
    "BoolSignal",
    "Connection",
    "ContentDisposition",
    "ItemDataRole",
    "ModelIndexMouseSignal",
    "ScrollHint",
    "SelectionBehavior",
    "SortOrder",
    "Coordinates",
    "DateSignal",
    "DialogCode",
    "DialogCodeSignal",
    "DoubleSignal",
    "EntryPointType",
    "EventSignal",
    "FileListSignal",
    "FilePickerType",
    "FileSignal",
    "FileSizeSignal",
    "IntSignal",
    "JInt64Signal",
    "Key",
    "KeyEventSignal",
    "KeyboardModifier",
    "LayoutDirection",
    "MenuItemSignal",
    "MouseButton",
    "MouseEventSignal",
    "Orientation",
    "PopupTrigger",
    "SelectionMode",
    "Signal",
    "StandardButton",
    "StandardButtonSignal",
    "StringSignal",
    "TemplateWidgetIdMode",
    "TextFormat",
    "Uint64PairSignal",
    "UpdateLock",
    "UploadedFile",
    "ValidationResult",
    "ValidationResultSignal",
    "ValidationState",
    "WAbstractItemModel",
    "WAbstractItemView",
    "WAbstractListModel",
    "WAnchor",
    "WApplication",
    "WBadge",
    "WBootstrap5Theme",
    "WBoxLayout",
    "WBreak",
    "WButtonGroup",
    "WCalendar",
    "WCheckBox",
    "WColor",
    "WColorPicker",
    "WComboBox",
    "WCssTheme",
    "WDateEdit",
    "WDateValidator",
    "WDoubleValidator",
    "WEmailValidator",
    "WFileDropWidget",
    "WFileResource",
    "WFileUpload",
    "WInPlaceEdit",
    "WIntValidator",
    "WLengthValidator",
    "WMemoryResource",
    "WPasswordEdit",
    "WRegExpValidator",
    "WResource",
    "WSplitButton",
    "WStackedValidator",
    "WStreamResource",
    "WSuggestionPopup",
    "WTextEdit",
    "WTheme",
    "WTimer",
    "WValidator",
    "WContainerWidget",
    "WDialog",
    "WDoubleSpinBox",
    "WEnvironment",
    "WFormWidget",
    "WGridLayout",
    "WGroupBox",
    "WHBoxLayout",
    "WImage",
    "WInteractWidget",
    "WKeyEvent",
    "WLabel",
    "WLayout",
    "WLineEdit",
    "WLink",
    "WMenu",
    "WMenuItem",
    "WMessageBox",
    "WModelIndex",
    "WMouseEvent",
    "WNavigationBar",
    "WObject",
    "WPanel",
    "WPoint",
    "WPopupMenu",
    "WProgressBar",
    "WPushButton",
    "WRadioButton",
    "WSelectionBox",
    "WServer",
    "WSlider",
    "WSpinBox",
    "WStackedWidget",
    "WTable",
    "WTableCell",
    "WTableColumn",
    "WTableRow",
    "WStandardItem",
    "WStandardItemModel",
    "WStringListModel",
    "WTableView",
    "WTabWidget",
    "WToolBar",
    "WTreeView",
    "WTemplate",
    "WText",
    "WTextArea",
    "WTimeEdit",
    "WTimeValidator",
    "WVBoxLayout",
    "WWidget",
    "__version__",
    "resources_dir",
    "update_lock",
]
