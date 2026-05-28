"""Small niches: legacy themes, painting completers, WQrCode, WGoogleMap.

The themes are constructible standalone (they're pure value classes
holding metadata). Painting value types (WGradient, WShadow, WBorder)
are also session-free. The two widgets (WQrCode, WGoogleMap) touch
WApplication::instance() in their constructors, so we only check the
binding surface and exercise their helper enums.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- Legacy Bootstrap themes ---------------------------------------------

def test_wbootstrap2_theme_name() -> None:
    assert wt.WBootstrap2Theme().name() == "bootstrap2"


def test_wbootstrap3_theme_name() -> None:
    assert wt.WBootstrap3Theme().name() == "bootstrap3"


@pytest.mark.parametrize("cls", [
    wt.WBootstrap2Theme, wt.WBootstrap3Theme, wt.WBootstrap5Theme,
    wt.WCssTheme,
])
def test_themes_inherit_wtheme(cls: type) -> None:
    assert issubclass(cls, wt.WTheme)


# ---- WGradient -----------------------------------------------------------

def test_wgradient_default_empty() -> None:
    g = wt.WGradient()
    assert g.is_empty is True


def test_wgradient_linear() -> None:
    g = wt.WGradient()
    g.set_linear_gradient(0, 0, 100, 100)
    g.add_color_stop(0.0, wt.WColor(255, 0, 0))
    g.add_color_stop(1.0, wt.WColor(0, 0, 255))
    assert g.style == wt.GradientStyle.Linear


def test_wgradient_radial() -> None:
    g = wt.WGradient()
    g.set_radial_gradient(50, 50, 25, 50, 50)
    assert g.style == wt.GradientStyle.Radial


def test_wgradient_clear_color_stops() -> None:
    g = wt.WGradient()
    g.set_linear_gradient(0, 0, 100, 100)
    g.add_color_stop(0.0, wt.WColor(0, 0, 0))
    g.clear_color_stops()


# ---- WShadow -------------------------------------------------------------

def test_wshadow_default_is_none() -> None:
    assert wt.WShadow().none is True


def test_wshadow_construct_with_offsets() -> None:
    s = wt.WShadow(3.0, 5.0, wt.WColor(0, 0, 0), 4.0)
    assert s.offset_x == 3.0
    assert s.offset_y == 5.0
    assert s.blur == 4.0
    assert s.none is False


def test_wshadow_round_trips() -> None:
    s = wt.WShadow()
    s.set_offsets(2.0, 4.0)
    s.set_blur(3.0)
    s.set_color(wt.WColor(50, 60, 70))
    assert s.offset_x == 2.0
    assert s.offset_y == 4.0
    assert s.blur == 3.0


# ---- WBorder -------------------------------------------------------------

def test_wborder_default_construct() -> None:
    b = wt.WBorder()
    assert b is not None


def test_wborder_style_round_trip() -> None:
    b = wt.WBorder()
    b.set_style(wt.BorderStyle.Solid)
    assert b.style == wt.BorderStyle.Solid


def test_wborder_construct_with_args() -> None:
    """All three args are mandatory in our binding (nanobind has trouble
    with WColor() value-typed defaults at registration time)."""
    b = wt.WBorder(wt.BorderStyle.Solid, wt.BorderWidth.Thick, wt.WColor(255, 0, 0))
    assert b.style == wt.BorderStyle.Solid
    assert b.color.red == 255


def test_wborder_explicit_width_form() -> None:
    """The WLength-taking overload is for explicit pixel/em widths."""
    b = wt.WBorder(wt.BorderStyle.Dashed,
                   wt.WLength(3, wt.LengthUnit.Pixel),
                   wt.WColor(0, 0, 255))
    assert b.style == wt.BorderStyle.Dashed


# ---- WPen / WBrush gradient integration ----------------------------------

def test_wpen_set_gradient() -> None:
    g = wt.WGradient()
    g.set_linear_gradient(0, 0, 100, 100)
    p = wt.WPen()
    p.set_gradient(g)
    # Pen now uses the gradient internally; the C++ side doesn't expose
    # a getter so we just verify the call succeeds.


def test_wbrush_construct_from_gradient() -> None:
    g = wt.WGradient()
    g.set_linear_gradient(0, 0, 100, 100)
    b = wt.WBrush(g)
    assert b.style == wt.BrushStyle.Gradient


# ---- WQrCode + WGoogleMap class binding surface --------------------------

@pytest.mark.parametrize("name", ["Low", "Medium", "Quartile", "High"])
def test_error_correction_level_members(name: str) -> None:
    assert hasattr(wt.ErrorCorrectionLevel, name)


def test_wqrcode_inherits_winteract_widget() -> None:
    assert issubclass(wt.WQrCode, wt.WInteractWidget)


@pytest.mark.parametrize("attr", [
    "message", "square_size", "set_error_correction_level",
    "brush", "error", "update",
])
def test_wqrcode_attribute_present(attr: str) -> None:
    assert hasattr(wt.WQrCode, attr), f"WQrCode missing: {attr}"


def test_google_maps_version_members() -> None:
    assert hasattr(wt.GoogleMapsVersion, "v3")


def test_map_type_control_members() -> None:
    for name in ("None_", "Default", "Menu", "Hierarchical", "HorizontalBar"):
        assert hasattr(wt.MapTypeControl, name)


def test_wgoogle_map_inherits_wwidget() -> None:
    assert issubclass(wt.WGoogleMap, wt.WWidget)


@pytest.mark.parametrize("attr", [
    "set_center", "pan_to", "set_zoom", "zoom_in", "zoom_out",
    "save_position", "return_to_saved_position",
    "add_marker", "add_icon_marker", "add_polyline", "add_circle",
    "clear_overlays", "open_info_window", "zoom_window", "Coordinate",
])
def test_wgoogle_map_attribute_present(attr: str) -> None:
    assert hasattr(wt.WGoogleMap, attr), f"WGoogleMap missing: {attr}"


# ---- GoogleMapCoordinate (value type — fully constructible) -------------

def test_google_map_coordinate_lat_lon_round_trip() -> None:
    c = wt.GoogleMapCoordinate(40.7128, -74.0060)
    assert c.latitude == pytest.approx(40.7128)
    assert c.longitude == pytest.approx(-74.0060)


def test_google_map_coordinate_setters() -> None:
    c = wt.GoogleMapCoordinate()
    c.latitude = 51.5074
    c.longitude = -0.1278
    assert c.latitude == pytest.approx(51.5074)


def test_google_map_coordinate_distance_to() -> None:
    """NYC → London great-circle distance is ~5570 km. Wt's distance_to
    returns kilometres (despite the Wt docs naming `metres` — empirically
    it's km)."""
    nyc = wt.GoogleMapCoordinate(40.7128, -74.0060)
    london = wt.GoogleMapCoordinate(51.5074, -0.1278)
    d = nyc.distance_to(london)
    assert d == pytest.approx(5570, rel=0.05)   # km, ±5 %


def test_google_map_coordinate_repr() -> None:
    assert repr(wt.GoogleMapCoordinate(40.7, -74)).startswith("GoogleMapCoordinate(")
