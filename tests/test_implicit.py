"""Implicit primitive→wrapper conversions.

Uses `wt._link_url`, a tiny test-only helper at module scope that takes a
`Wt::WLink` and returns its URL. Calling it with a Python `str` exercises
the `nb::init_implicit<std::string>` on `WLink` — i.e. it confirms that
*any* binding endpoint taking a `WLink` accepts a `str`.
"""

from __future__ import annotations

import witty_for_python as wt
from witty_for_python._witty_for_python import _link_url


def test_str_becomes_wlink_via_implicit_conversion() -> None:
    assert _link_url("http://example.com") == "http://example.com"


def test_explicit_wlink_still_works() -> None:
    """Adding the implicit conversion doesn't break the explicit path."""
    assert _link_url(wt.WLink("http://example.com")) == "http://example.com"


def test_same_wlink_reusable_across_calls() -> None:
    """User pattern: build a WLink once, pass it to multiple WLink-taking endpoints."""
    link = wt.WLink("http://shared.example")
    for _ in range(3):
        assert _link_url(link) == "http://shared.example"


def test_wlink_url_property_round_trip() -> None:
    """The WLink class itself is bound — url is read/write."""
    link = wt.WLink("http://a")
    assert link.url == "http://a"
    link.url = "http://b"
    assert link.url == "http://b"


def test_wstring_str_round_trip_via_coordinates() -> None:
    """Coordinates uses int, not str, but its repr exercises WString-free path —
    use it just to confirm the non-widget construction surface is sane."""
    c = wt.Coordinates(3, 4)
    assert c.x == 3
    assert c.y == 4
    assert "Coordinates" in repr(c)
