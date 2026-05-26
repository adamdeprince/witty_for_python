"""WResource family suite.

Tests cover the value-bearing API of the resource hierarchy
(``WMemoryResource`` data round-trips, ``WFileResource`` filename storage,
``ContentDisposition`` enum surface) plus the WLink ↔ resource implicit
conversion path. None of these need a live ``WApplication`` — they exercise
the binding layer's data plumbing, not the HTTP serving.

Actually serving the resource over HTTP is covered by the gallery boot test
(``test_gallery_boot.py``), which spins up a full ``WServer``.
"""

from __future__ import annotations

import witty_for_python as wt
from witty_for_python._witty_for_python import _link_url


# ---- ContentDisposition enum -----------------------------------------------

def test_content_disposition_members() -> None:
    # `None` is reserved in Python; bound as `None_` per project convention.
    assert wt.ContentDisposition.None_ != wt.ContentDisposition.Attachment
    assert wt.ContentDisposition.Inline != wt.ContentDisposition.Attachment


# ---- WMemoryResource: data, mime_type, construction -----------------------

def test_memory_resource_empty_default() -> None:
    r = wt.WMemoryResource()
    assert r.data == b""
    # Default mime type is "text/plain" upstream.
    assert isinstance(r.mime_type, str)


def test_memory_resource_mime_only_ctor() -> None:
    r = wt.WMemoryResource("application/json")
    assert r.mime_type == "application/json"
    assert r.data == b""


def test_memory_resource_full_ctor() -> None:
    r = wt.WMemoryResource("text/csv", b"a,b,c\n1,2,3\n")
    assert r.mime_type == "text/csv"
    assert r.data == b"a,b,c\n1,2,3\n"


def test_memory_resource_data_round_trip() -> None:
    r = wt.WMemoryResource("application/octet-stream")
    payload = bytes(range(256))           # all byte values
    r.data = payload
    assert r.data == payload
    assert len(r.data) == 256


def test_memory_resource_empty_bytes_setter() -> None:
    r = wt.WMemoryResource("text/plain", b"start")
    r.data = b""
    assert r.data == b""


def test_memory_resource_mime_type_assignable() -> None:
    r = wt.WMemoryResource()
    r.mime_type = "image/png"
    assert r.mime_type == "image/png"


# ---- WResource API surface (inherited methods) -----------------------------

def test_set_changed_idempotent() -> None:
    """Cache-invalidation call is harmless even when nothing observes it."""
    r = wt.WMemoryResource("text/plain", b"v1")
    r.set_changed()
    r.data = b"v2"
    r.set_changed()


def test_suggest_file_name_accepts_str() -> None:
    """suggest_file_name takes a WString; str converts via the caster."""
    r = wt.WMemoryResource("text/csv")
    r.suggest_file_name("report.csv")
    # No accessor on the C++ side surfaces the value back, so we only check
    # the call doesn't raise.


def test_set_disposition_type_accepts_enum() -> None:
    r = wt.WMemoryResource("application/pdf")
    r.set_disposition_type(wt.ContentDisposition.Attachment)
    r.set_disposition_type(wt.ContentDisposition.Inline)
    r.set_disposition_type(wt.ContentDisposition.None_)


def test_internal_path_round_trip() -> None:
    r = wt.WMemoryResource("text/plain")
    assert r.internal_path == ""
    r.internal_path = "/downloads/report"
    assert r.internal_path == "/downloads/report"


def test_set_invalid_after_changed_flag() -> None:
    r = wt.WMemoryResource("text/plain")
    r.set_invalid_after_changed(True)
    r.set_invalid_after_changed(False)


def test_set_takes_update_lock_flag() -> None:
    r = wt.WMemoryResource("text/plain")
    r.set_takes_update_lock(True)
    r.set_takes_update_lock(False)


# ---- WFileResource ---------------------------------------------------------

def test_file_resource_filename_round_trip() -> None:
    r = wt.WFileResource()
    assert r.file_name == ""
    r.file_name = "/etc/hostname"
    assert r.file_name == "/etc/hostname"


def test_file_resource_path_only_ctor() -> None:
    r = wt.WFileResource("/etc/hostname")
    assert r.file_name == "/etc/hostname"


def test_file_resource_mime_and_path_ctor() -> None:
    r = wt.WFileResource("text/plain", "/etc/hostname")
    assert r.file_name == "/etc/hostname"
    assert r.mime_type == "text/plain"


def test_file_resource_buffer_size() -> None:
    """WStreamResource::setBufferSize is the inherited streaming knob."""
    r = wt.WFileResource("text/plain", "/etc/hostname")
    r.set_buffer_size(8192)


# ---- WLink ↔ WResource implicit conversion --------------------------------

def test_link_explicit_from_resource() -> None:
    r = wt.WMemoryResource("text/plain", b"x")
    link = wt.WLink(r)
    # The URL is assigned by Wt when the resource is bound to a session;
    # outside an application context it just needs to exist as a string.
    assert isinstance(link.url, str)


def test_link_implicit_resource_at_call_site() -> None:
    """A bare WResource passed where a WLink is expected auto-converts via
    nb::init_implicit<shared_ptr<WResource>>. This is the same pattern the
    str → WLink path uses."""
    r = wt.WMemoryResource("text/plain", b"x")
    url = _link_url(r)
    assert isinstance(url, str)


def test_link_implicit_str_still_works() -> None:
    """Adding the resource implicit constructor must not break the existing
    str → WLink path."""
    url = _link_url("https://example.com/foo")
    assert url == "https://example.com/foo"


# ---- inheritance hierarchy -------------------------------------------------

def test_inheritance_chain() -> None:
    m = wt.WMemoryResource()
    f = wt.WFileResource()
    assert isinstance(m, wt.WResource)
    assert isinstance(f, wt.WResource)
    assert isinstance(f, wt.WStreamResource)
    # WMemoryResource does NOT inherit WStreamResource — they're sibling
    # concrete subclasses of WResource.
    assert not isinstance(m, wt.WStreamResource)
