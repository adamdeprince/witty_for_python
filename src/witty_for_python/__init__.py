"""Python bindings for the Wt (Web Toolkit) C++ library."""

from __future__ import annotations

import atexit as _atexit
import contextlib as _contextlib
from typing import Iterator as _Iterator

from ._witty_for_python import (
    UpdateLock,
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
    WMouseEvent,
    WObject,
    WPanel,
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
    WTableRow,
    WTabWidget,
    WText,
    WTextArea,
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
    """Disconnect every Python-callable slot pywitty is holding.

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
    "BoolSignal",
    "Connection",
    "Coordinates",
    "DialogCode",
    "DialogCodeSignal",
    "DoubleSignal",
    "EntryPointType",
    "EventSignal",
    "IntSignal",
    "Key",
    "KeyEventSignal",
    "KeyboardModifier",
    "LayoutDirection",
    "MenuItemSignal",
    "MouseButton",
    "MouseEventSignal",
    "Orientation",
    "SelectionMode",
    "Signal",
    "StandardButton",
    "StandardButtonSignal",
    "StringSignal",
    "UpdateLock",
    "WAnchor",
    "WApplication",
    "WBoxLayout",
    "WBreak",
    "WButtonGroup",
    "WCheckBox",
    "WComboBox",
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
    "WMouseEvent",
    "WObject",
    "WPanel",
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
    "WTabWidget",
    "WText",
    "WTextArea",
    "WVBoxLayout",
    "WWidget",
    "__version__",
    "update_lock",
]
