"""WBorderLayout + WFitLayout binding surface.

Both layouts inherit WLayout and are constructible without an active
WApplication. add_widget moves ownership into the layout, so we can't
realistically test it without a container — that's the gallery boot
test's job.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


def test_layout_position_members() -> None:
    for name in ("North", "East", "South", "West", "Center"):
        assert hasattr(wt.LayoutPosition, name)


@pytest.mark.parametrize("cls", [wt.WBorderLayout, wt.WFitLayout])
def test_extra_layout_inherits_wlayout(cls: type) -> None:
    assert issubclass(cls, wt.WLayout)


def test_wborderlayout_construct_default() -> None:
    layout = wt.WBorderLayout()
    assert layout is not None
    assert hasattr(layout, "add_widget")


def test_wfitlayout_construct_default() -> None:
    layout = wt.WFitLayout()
    assert layout is not None
    assert hasattr(layout, "add_widget")
