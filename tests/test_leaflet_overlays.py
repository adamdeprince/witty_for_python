"""WLeafletMap marker / popup / tooltip hierarchy.

All these classes are constructed by Wt to be inserted into a live map.
Several of them (Popup(WString), Tooltip(WString), WidgetMarker, etc.)
internally construct WText/WContainerWidget instances that touch
WApplication::instance() — so standalone construction segfaults outside
a session.

We verify:
  - the nested-class hierarchy is correctly exposed under WLeafletMap.*
  - inheritance chains: Popup → AbstractOverlayItem → AbstractMapItem → WObject
  - LeafletMarker(coord) constructs (no session — it just stores the coord)

The gallery boot test exercises actual instantiation + signal wiring
inside a real Wt session.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


M = wt.WLeafletMap


# ---- Nested classes exposed --------------------------------------------

@pytest.mark.parametrize("name", [
    "Coordinate", "AbstractMapItem", "AbstractOverlayItem",
    "Popup", "Tooltip", "Marker", "LeafletMarker", "WidgetMarker",
])
def test_nested_class_exposed(name: str) -> None:
    assert hasattr(M, name), f"WLeafletMap.{name} missing"
    assert isinstance(getattr(M, name), type)


# ---- Inheritance chain --------------------------------------------------

@pytest.mark.parametrize("cls,base", [
    (M.AbstractMapItem,     wt.WObject),
    (M.AbstractOverlayItem, M.AbstractMapItem),
    (M.Popup,               M.AbstractOverlayItem),
    (M.Tooltip,             M.AbstractOverlayItem),
    (M.Marker,              M.AbstractMapItem),
    (M.LeafletMarker,       M.Marker),
    (M.WidgetMarker,        M.Marker),
])
def test_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base)


# ---- AbstractMapItem signal surface ------------------------------------

@pytest.mark.parametrize("name", [
    "clicked", "double_clicked", "mouse_went_down", "mouse_went_up",
    "mouse_went_over", "mouse_went_out", "position", "move",
])
def test_abstract_map_item_attribute(name: str) -> None:
    assert hasattr(M.AbstractMapItem, name), (
        f"AbstractMapItem missing: {name}")


# ---- AbstractOverlayItem additional surface ----------------------------

@pytest.mark.parametrize("name", [
    "set_options", "set_content", "set_content_text",
    "open", "close", "toggle", "is_open",
    "opened_signal", "closed_signal",
])
def test_abstract_overlay_item_attribute(name: str) -> None:
    assert hasattr(M.AbstractOverlayItem, name)


# ---- Marker-specific surface -------------------------------------------

@pytest.mark.parametrize("name", [
    "add_popup", "remove_popup", "popup",
    "add_tooltip", "remove_tooltip", "tooltip",
])
def test_marker_attribute(name: str) -> None:
    assert hasattr(M.Marker, name), f"Marker missing: {name}"


# ---- WidgetMarker surface ----------------------------------------------

@pytest.mark.parametrize("name", ["widget", "set_anchor_point"])
def test_widget_marker_attribute(name: str) -> None:
    assert hasattr(M.WidgetMarker, name)


# ---- LeafletMarker surface ---------------------------------------------

def test_leaflet_marker_has_set_options() -> None:
    assert hasattr(M.LeafletMarker, "set_options")


# ---- LeafletMarker construction (session-free — just stores coord) ----

def test_leaflet_marker_construct_at_coord() -> None:
    pos = M.Coordinate(40.7128, -74.0060)
    marker = M.LeafletMarker(pos)
    p = marker.position
    assert p.latitude == pytest.approx(40.7128)
    assert p.longitude == pytest.approx(-74.0060)


def test_leaflet_marker_move() -> None:
    """Moving an unattached marker just updates its stored position."""
    marker = M.LeafletMarker(M.Coordinate(0, 0))
    marker.move(M.Coordinate(51.5, -0.1))
    assert marker.position.latitude == pytest.approx(51.5)


# ---- WLeafletMap.add_marker / add_popup / add_tooltip surfaces --------

@pytest.mark.parametrize("name", [
    "add_marker", "add_popup", "add_tooltip",
])
def test_wleafletmap_overlay_methods(name: str) -> None:
    assert hasattr(wt.WLeafletMap, name)
