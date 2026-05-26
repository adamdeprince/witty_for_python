"""WFileUpload + UploadedFile suite.

WFileUpload's constructor calls `WApplication::instance()->environment()`,
which segfaults without an active session — so we can't instantiate it
here. Its real exercise is in the gallery boot test (a live WServer ).

This file tests the binding surface and the standalone-constructible
UploadedFile struct (which has no session dependency since it's just a
value type).
"""

from __future__ import annotations

import witty_for_python as wt


# ---- UploadedFile -----------------------------------------------------------

def test_uploaded_file_is_exposed() -> None:
    assert wt.UploadedFile is not None
    assert isinstance(wt.UploadedFile, type)


def test_uploaded_file_has_expected_props() -> None:
    """UploadedFile exposes spool_file_name / client_file_name / content_type
    — the trio Python code reads to consume an upload."""
    for attr in ("spool_file_name", "client_file_name", "content_type"):
        assert hasattr(wt.UploadedFile, attr), f"missing: {attr}"


# ---- WFileUpload (binding surface only) -------------------------------------

def test_wfileupload_class_exposed() -> None:
    assert wt.WFileUpload is not None
    assert isinstance(wt.WFileUpload, type)


def test_wfileupload_inherits_wwidget() -> None:
    assert issubclass(wt.WFileUpload, wt.WWidget)


def test_wfileupload_method_surface() -> None:
    """Every method/property a typical upload-handling flow needs must be
    bound. Names are checked, not values — we can't construct the widget
    without a session."""
    for attr in ("multiple", "file_text_size", "empty", "can_upload",
                 "spool_file_name", "uploaded_files",
                 "upload", "set_filters",
                 "changed", "uploaded"):
        assert hasattr(wt.WFileUpload, attr), f"missing: {attr}"
