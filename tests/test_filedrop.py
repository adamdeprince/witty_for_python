"""WFileDropWidget + File* signal types + file_too_large/data_received.

Like other interactive widgets, ``WFileDropWidget`` and its nested
``File`` class can't be standalone-instantiated outside an active
``WApplication`` — the constructors touch session state. The gallery
boot test exercises construction end-to-end inside a real session.

Here we verify the binding surface: classes exist, inherit from the right
bases, expose the expected methods + signals, and the new signal types
(``FileSignal``, ``FileListSignal``, ``FileSizeSignal``, ``JInt64Signal``,
``Uint64PairSignal``) are reachable from the module.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- new signal types ------------------------------------------------------

@pytest.mark.parametrize("name", [
    "FileSignal", "FileListSignal", "FileSizeSignal",
    "JInt64Signal", "Uint64PairSignal",
])
def test_signal_type_is_exposed(name: str) -> None:
    assert hasattr(wt, name), f"missing signal type: {name}"
    assert isinstance(getattr(wt, name), type)


def test_wfiledropwidget_has_nested_Directory() -> None:
    """Directory is a File subclass for folder drops — isinstance check
    against `WFileDropWidget.Directory` works on entries from `drop` when
    the user dropped a folder."""
    assert hasattr(wt.WFileDropWidget, "Directory")
    assert issubclass(wt.WFileDropWidget.Directory,
                      wt.WFileDropWidget.File)


def test_directory_contents_attr() -> None:
    """The folder-only `contents` accessor exposes child File entries."""
    assert hasattr(wt.WFileDropWidget.Directory, "contents")


@pytest.mark.parametrize("name", [
    "FileSignal", "FileListSignal", "FileSizeSignal",
    "JInt64Signal", "Uint64PairSignal",
])
def test_signal_type_exposes_connect_and_disconnect(name: str) -> None:
    """All Wt signal bindings in this project share the same shape:
    connect(callable) + disconnect_all_slots(). Verify the new ones do
    too."""
    cls = getattr(wt, name)
    assert hasattr(cls, "connect")
    assert hasattr(cls, "disconnect_all_slots")


# ---- FilePickerType enum ---------------------------------------------------

def test_file_picker_type_members() -> None:
    # `None` is reserved in Python; bound as `None_`.
    assert wt.FilePickerType.None_ != wt.FilePickerType.FileSelection
    assert wt.FilePickerType.DirectorySelection != wt.FilePickerType.FileSelection


# ---- WFileDropWidget class surface -----------------------------------------

def test_wfiledropwidget_class_exposed() -> None:
    assert wt.WFileDropWidget is not None
    assert isinstance(wt.WFileDropWidget, type)


def test_wfiledropwidget_inherits_wcontainer() -> None:
    """WFileDropWidget IS a WContainerWidget — content placed inside it
    renders as the dropzone's body."""
    assert issubclass(wt.WFileDropWidget, wt.WContainerWidget)


def test_wfiledropwidget_method_surface() -> None:
    for attr in (
        "uploads", "current_index", "cancel_upload", "remove",
        "clean_directory_resources", "set_accept_drops", "set_filters",
        "drop_indication_enabled", "global_drop_enabled",
        "set_on_click_file_picker", "on_click_file_picker",
        "open_file_picker", "open_directory_picker",
        "set_accept_directories",
        "drop", "new_upload", "uploaded", "too_large", "upload_failed",
    ):
        assert hasattr(wt.WFileDropWidget, attr), f"missing: {attr}"


def test_wfiledropwidget_has_nested_File() -> None:
    """The nested `File` class is re-attached under the widget for the
    natural `WFileDropWidget.File` form. The same class is also reachable
    as `WFileDropWidgetFile` at module scope (top-level binding name)."""
    assert hasattr(wt.WFileDropWidget, "File")


# ---- WFileDropWidget.File class surface ------------------------------------

def test_file_class_inherits_wobject() -> None:
    assert issubclass(wt.WFileDropWidget.File, wt.WObject)


def test_file_class_method_surface() -> None:
    cls = wt.WFileDropWidget.File
    for attr in (
        "client_file_name", "path", "directory", "mime_type", "size",
        "upload_finished", "uploaded_file",
        "data_received", "uploaded",
        "filter_enabled", "is_filtered",
    ):
        assert hasattr(cls, attr), f"missing: {attr}"


# ---- WFileUpload picks up new signals --------------------------------------

def test_wfileupload_file_too_large_attr() -> None:
    assert hasattr(wt.WFileUpload, "file_too_large")


def test_wfileupload_data_received_attr() -> None:
    assert hasattr(wt.WFileUpload, "data_received")
