"""Enum values and module-level constants are exposed correctly.

These tests don't need a WApplication context — they just verify what's
visible after `import witty_for_python`.
"""

from __future__ import annotations

import witty_for_python as wt


# ---- module surface --------------------------------------------------------

def test_version_string_present() -> None:
    assert isinstance(wt.__version__, str)
    assert wt.__version__  # not empty


def test_all_lists_at_least_the_basics() -> None:
    """Spot-check that `__all__` covers the major classes / enums."""
    must_have = {
        "WApplication", "WServer", "WEnvironment", "EntryPointType",
        "WContainerWidget", "WText", "WPushButton", "WLineEdit",
        "WLink", "WMouseEvent", "WKeyEvent", "Coordinates",
        "Signal", "IntSignal", "BoolSignal", "DoubleSignal", "StringSignal",
        "EventSignal", "MouseEventSignal", "KeyEventSignal",
        "Key", "MouseButton", "KeyboardModifier",
        "Orientation", "LayoutDirection", "SelectionMode",
        "DialogCode", "StandardButton",
        "UpdateLock", "update_lock",
    }
    missing = must_have - set(wt.__all__)
    assert missing == set(), f"missing from __all__: {sorted(missing)}"


# ---- enum value sanity -----------------------------------------------------

def test_mouse_button_values() -> None:
    assert wt.MouseButton.Left
    assert wt.MouseButton.Right
    assert wt.MouseButton.Middle


def test_key_enum_has_expected_names() -> None:
    for name in ("Enter", "Tab", "Escape", "Left", "Right", "Up", "Down", "F1", "A", "Space"):
        assert hasattr(wt.Key, name), f"wt.Key.{name} missing"


def test_orientation_enum() -> None:
    assert wt.Orientation.Horizontal != wt.Orientation.Vertical


def test_layout_direction_enum() -> None:
    assert hasattr(wt.LayoutDirection, "LeftToRight")
    assert hasattr(wt.LayoutDirection, "TopToBottom")


def test_dialog_code_enum() -> None:
    assert wt.DialogCode.Accepted != wt.DialogCode.Rejected


def test_standard_button_is_bitwise_or_friendly() -> None:
    """StandardButton is bound with nb::is_arithmetic, so | yields an int
    that set_standard_buttons() accepts."""
    combined = wt.StandardButton.Ok | wt.StandardButton.Cancel
    assert isinstance(combined, int)
    assert combined == int(wt.StandardButton.Ok) + int(wt.StandardButton.Cancel)


def test_entry_point_type_values() -> None:
    assert wt.EntryPointType.Application
    assert wt.EntryPointType.WidgetSet
    assert wt.EntryPointType.StaticResource


# ---- non-widget construction -----------------------------------------------

def test_wlink_constructible_outside_app_context() -> None:
    """WLink is a value type — doesn't need WApplication::instance() to construct."""
    link = wt.WLink("http://example")
    assert link.url == "http://example"


def test_coordinates_construct_and_access() -> None:
    c = wt.Coordinates(10, 20)
    assert c.x == 10 and c.y == 20
