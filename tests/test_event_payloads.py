"""Event-payload suite.

Touch / WTouchEvent / WGestureEvent / WScrollEvent / WDropEvent are
value-typed classes constructed inside Wt's event delivery machinery —
Python doesn't usually need to instantiate them. These tests just verify
the binding surface and the new DropEventOriginalEventType enum.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


@pytest.mark.parametrize("cls", [
    wt.Touch, wt.WTouchEvent, wt.WGestureEvent, wt.WScrollEvent, wt.WDropEvent,
])
def test_event_class_exposed(cls: type) -> None:
    assert isinstance(cls, type)


def test_drop_event_original_event_type_enum() -> None:
    assert wt.DropEventOriginalEventType.Mouse != wt.DropEventOriginalEventType.Touch


@pytest.mark.parametrize("cls,attr", [
    (wt.Touch,         "document"),
    (wt.Touch,         "window"),
    (wt.Touch,         "screen"),
    (wt.Touch,         "widget"),
    (wt.WTouchEvent,   "touches"),
    (wt.WTouchEvent,   "target_touches"),
    (wt.WTouchEvent,   "changed_touches"),
    (wt.WGestureEvent, "scale"),
    (wt.WGestureEvent, "rotation"),
    (wt.WScrollEvent,  "scroll_x"),
    (wt.WScrollEvent,  "scroll_y"),
    (wt.WScrollEvent,  "viewport_width"),
    (wt.WScrollEvent,  "viewport_height"),
    (wt.WDropEvent,    "source"),
    (wt.WDropEvent,    "mime_type"),
    (wt.WDropEvent,    "event_type"),
    (wt.WDropEvent,    "mouse_event"),
    (wt.WDropEvent,    "touch_event"),
])
def test_event_attribute_present(cls: type, attr: str) -> None:
    assert hasattr(cls, attr), f"{cls.__name__} missing: {attr}"


# These events are constructed by Wt's event-delivery machinery from a
# JavaScriptEvent payload — Python users receive them via signal slots
# but rarely make their own. We don't bind their default constructors,
# so attempting `wt.WScrollEvent()` from Python raises TypeError. End-
# to-end behaviour (events flowing into slots) is exercised by the
# gallery boot test.
