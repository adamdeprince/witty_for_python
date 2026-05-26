"""Navigation-chrome widget suite: WPopupMenu, WNavigationBar, WToolBar,
WBadge, WSplitButton.

These are composite widgets — their constructors touch
``WApplication::instance()``, so they segfault without an active session.
Full construction is covered by the gallery boot test (which spawns a
real Wt server). Here we verify the binding surface: classes are
exposed, inherit from the right bases, and expose the expected methods
+ signals.

WPoint (a small value type used by WPopupMenu.popup) and AlignmentFlag
(the enum used for chrome layout) do not need a session, so we fully
exercise them.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- WPoint (value type) ---------------------------------------------------

def test_wpoint_default_construct() -> None:
    p = wt.WPoint()
    assert p.x == 0
    assert p.y == 0


def test_wpoint_xy_round_trip() -> None:
    p = wt.WPoint(7, 11)
    assert p.x == 7
    assert p.y == 11
    p.x = 100
    p.y = 200
    assert (p.x, p.y) == (100, 200)


def test_wpoint_repr() -> None:
    """__repr__ helps debugging by showing constructor-style syntax."""
    assert repr(wt.WPoint(3, 4)) == "WPoint(x=3, y=4)"


# ---- AlignmentFlag enum ----------------------------------------------------

def test_alignment_flag_values_distinct() -> None:
    """Wt's AlignmentFlag has bit-flag semantics; we bind it as arithmetic
    so users can OR values."""
    assert wt.AlignmentFlag.Left != wt.AlignmentFlag.Right
    assert wt.AlignmentFlag.Center != wt.AlignmentFlag.Top


def test_alignment_flag_has_expected_members() -> None:
    for name in ("Left", "Right", "Center", "Justify",
                 "Baseline", "Top", "Middle", "Bottom"):
        assert hasattr(wt.AlignmentFlag, name)


# ---- Chrome widget class binding surface ----------------------------------

@pytest.mark.parametrize("cls,base", [
    (wt.WPopupMenu,     wt.WMenu),
    (wt.WNavigationBar, wt.WTemplate),
    (wt.WToolBar,       wt.WWidget),
    (wt.WBadge,         wt.WText),
    (wt.WSplitButton,   wt.WWidget),
])
def test_chrome_widget_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base), f"{cls.__name__} should extend {base.__name__}"


@pytest.mark.parametrize("cls,attr", [
    # WPopupMenu
    (wt.WPopupMenu, "popup"),
    (wt.WPopupMenu, "set_button"),
    (wt.WPopupMenu, "hide_on_select"),
    (wt.WPopupMenu, "set_auto_hide"),
    (wt.WPopupMenu, "about_to_hide"),
    (wt.WPopupMenu, "triggered"),
    # WNavigationBar
    (wt.WNavigationBar, "set_title"),
    (wt.WNavigationBar, "set_responsive"),
    (wt.WNavigationBar, "add_menu"),
    (wt.WNavigationBar, "add_form_field"),
    (wt.WNavigationBar, "add_search"),
    (wt.WNavigationBar, "add_widget"),
    # WToolBar
    (wt.WToolBar, "set_orientation"),
    (wt.WToolBar, "compact"),
    (wt.WToolBar, "count"),
    (wt.WToolBar, "add_button"),
    (wt.WToolBar, "add_widget"),
    (wt.WToolBar, "add_separator"),
    # WBadge
    (wt.WBadge, "use_default_style"),
    # WSplitButton
    (wt.WSplitButton, "action_button"),
    (wt.WSplitButton, "drop_down_button"),
    (wt.WSplitButton, "set_menu"),
])
def test_chrome_widget_method_present(cls: type, attr: str) -> None:
    assert hasattr(cls, attr), f"{cls.__name__} missing: {attr}"
