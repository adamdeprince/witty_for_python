"""Painting-subsystem suite.

Value types (WPointF, WRectF, WLineF, WTransform, WFont, WPen, WBrush,
WPainterPath) construct without a session; we exercise them fully.
Image-map areas (WCircleArea, WRectArea, WPolygonArea) also construct
standalone — they're just data carriers until added to a painted widget.

WPainter and WPaintedWidget need a paint context — verified through the
gallery boot test.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- WPointF / WRectF / WLineF / WTransform -----------------------------

def test_wpointf_round_trip() -> None:
    p = wt.WPointF(3.5, 7.0)
    assert p.x == 3.5
    assert p.y == 7.0
    p.x = 10.0
    assert p.x == 10.0


def test_wrectf_construct_and_query() -> None:
    r = wt.WRectF(0, 0, 100, 50)
    assert r.width == 100
    assert r.height == 50
    assert r.left == 0
    assert r.top == 0
    assert r.is_null is False
    assert r.is_empty is False


def test_wrectf_default_is_null_or_empty() -> None:
    r = wt.WRectF()
    # Wt defines null/empty differently — at least one of them should
    # report True for the default-constructed rect.
    assert r.is_null or r.is_empty


def test_wlinef_endpoints() -> None:
    line = wt.WLineF(0, 0, 100, 100)
    assert line.x1 == 0
    assert line.y2 == 100
    assert line.p1.x == 0
    assert line.p2.y == 100


def test_wtransform_identity_and_map() -> None:
    t = wt.WTransform()
    assert t.is_identity is True
    # Identity maps (x, y) → (x, y)
    assert t.map_point(5, 7) == (5.0, 7.0)


# ---- Font enums + WFont --------------------------------------------------

@pytest.mark.parametrize("name", [
    "Default", "Serif", "SansSerif", "Cursive", "Fantasy", "Monospace",
])
def test_font_family_members(name: str) -> None:
    assert hasattr(wt.FontFamily, name)


def test_wfont_construct() -> None:
    """Construct with the default + family form. Setter methods exist
    but most don't have getters in Wt's public API."""
    f1 = wt.WFont()
    assert f1 is not None
    f2 = wt.WFont(wt.FontFamily.Monospace)
    f2.set_size(wt.WLength(14))


# ---- WPen + WBrush -------------------------------------------------------

def test_wpen_color_round_trip() -> None:
    p = wt.WPen(wt.WColor(255, 100, 50))
    assert p.color.red == 255
    assert p.color.green == 100


def test_wpen_style_round_trip() -> None:
    p = wt.WPen()
    p.set_style(wt.PenStyle.DashLine)
    assert p.style == wt.PenStyle.DashLine


def test_wpen_width_round_trip() -> None:
    p = wt.WPen()
    p.set_width(wt.WLength(3))
    assert p.width.value == 3


def test_wbrush_color_and_style() -> None:
    b = wt.WBrush(wt.WColor(10, 20, 30))
    assert b.color.red == 10
    assert b.style == wt.BrushStyle.SolidPattern   # ctor implies Solid


# ---- WPainterPath --------------------------------------------------------

def test_painter_path_starts_empty() -> None:
    p = wt.WPainterPath()
    assert p.is_empty is True


def test_painter_path_moves_and_lines() -> None:
    p = wt.WPainterPath()
    p.move_to(0, 0)
    p.line_to(50, 50)
    p.line_to(100, 0)
    p.close_sub_path()
    assert p.is_empty is False
    # currentPosition is wherever the last segment ended.
    cur = p.current_position
    assert cur.x == 0   # close_sub_path returns to the start


def test_painter_path_add_rect_and_ellipse() -> None:
    p = wt.WPainterPath()
    p.add_rect(0, 0, 100, 50)
    p.add_ellipse(0, 0, 100, 50)
    assert p.is_empty is False


def test_painter_path_cubic_to() -> None:
    p = wt.WPainterPath()
    p.move_to(0, 0)
    p.cubic_to(10, 10, 20, 20, 30, 30)
    assert p.current_position.x == 30
    assert p.current_position.y == 30


# ---- Image-map areas ----------------------------------------------------

def test_wcirclearea_construct() -> None:
    c = wt.WCircleArea(50, 50, 25)
    assert c.center_x == 50
    assert c.center_y == 50
    assert c.radius == 25


def test_wcirclearea_setters() -> None:
    c = wt.WCircleArea()
    c.set_center(100, 200)
    c.radius = 40
    assert c.center_x == 100
    assert c.radius == 40


def test_wrectarea_construct_from_rectf() -> None:
    """WRectArea has a convenience constructor that takes a WRectF."""
    r = wt.WRectArea(wt.WRectF(10, 20, 100, 50))
    assert r is not None


def test_wpolygonarea_add_points() -> None:
    p = wt.WPolygonArea()
    p.add_point(0, 0)
    p.add_point(100, 0)
    p.add_point(50, 100)


def test_areas_inherit_wabstractarea() -> None:
    assert issubclass(wt.WCircleArea, wt.WAbstractArea)
    assert issubclass(wt.WRectArea,   wt.WAbstractArea)
    assert issubclass(wt.WPolygonArea, wt.WAbstractArea)


# ---- WPainter class binding (no instantiation — needs a device) --------

def test_wpainter_class_methods_present() -> None:
    """We can't construct a WPainter without a paint device, but the
    method surface must be present on the class so callers receiving one
    from a WPaintedWidget callback can use it."""
    for attr in ("draw_line", "draw_rect", "draw_ellipse", "draw_arc",
                 "draw_path", "draw_text", "set_pen", "set_brush",
                 "set_font", "save", "restore", "translate", "rotate",
                 "scale", "set_world_transform", "set_clipping",
                 "set_clip_path"):
        assert hasattr(wt.WPainter, attr), f"WPainter missing: {attr}"


# ---- WPaintedWidget (class only — construction needs a session) -------

def test_wpaintedwidget_inheritance() -> None:
    assert issubclass(wt.WPaintedWidget, wt.WInteractWidget)


def test_wpaintedwidget_method_surface() -> None:
    for attr in ("update", "set_paint_callback", "set_preferred_method",
                 "preferred_method", "add_area", "insert_area"):
        assert hasattr(wt.WPaintedWidget, attr), f"missing: {attr}"


def test_render_method_members() -> None:
    for name in ("InlineSvgVml", "HtmlCanvas", "PngImage"):
        assert hasattr(wt.RenderMethod, name)
