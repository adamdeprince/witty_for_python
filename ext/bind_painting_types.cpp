#include "common.hpp"

#include <Wt/WBorder.h>
#include <Wt/WBrush.h>
#include <Wt/WFont.h>
#include <Wt/WGlobal.h>           // PenStyle, BrushStyle, FontFamily, …
#include <Wt/WGradient.h>
#include <Wt/WLength.h>
#include <Wt/WLineF.h>
#include <Wt/WPainterPath.h>
#include <Wt/WPen.h>
#include <Wt/WPointF.h>
#include <Wt/WRectF.h>
#include <Wt/WShadow.h>
#include <Wt/WTransform.h>

#include <string>

namespace witty_for_python {

void register_painting_types(nb::module_& m) {
    // ---- Geometry value types ----
    //
    // WPointF, WRectF, WLineF, WTransform all inherit
    // WJavaScriptExposableObject in C++ (so they can be the right-hand
    // side of client-side JavaScript expressions). We don't bind that
    // base — Python users won't need it for a long time.

    nb::class_<Wt::WPointF>(m, "WPointF",
        "A point in 2-D space with floating-point coordinates. Used by\n"
        "WPainter for paths and polygons; mutable so you can mutate x/y\n"
        "in place.")
        .def(nb::init<>(),
             "Construct the origin (0, 0).")
        .def(nb::init<double, double>(), "x"_a, "y"_a,
             "Construct the point (x, y).")
        .def_prop_rw("x",
            [](const Wt::WPointF& p) { return p.x(); },
            [](Wt::WPointF& p, double x) { p.setX(x); },
            "Horizontal coordinate.")
        .def_prop_rw("y",
            [](const Wt::WPointF& p) { return p.y(); },
            [](Wt::WPointF& p, double y) { p.setY(y); },
            "Vertical coordinate.")
        .def("__repr__", [](const Wt::WPointF& p) {
            return "WPointF(x=" + std::to_string(p.x())
                + ", y=" + std::to_string(p.y()) + ")";
        });

    nb::class_<Wt::WRectF>(m, "WRectF",
        "Axis-aligned rectangle with floating-point coordinates. Used as\n"
        "a parameter to WPainter draw / clip methods and as the result\n"
        "type of bounding-box queries.")
        .def(nb::init<>(),
             "Construct a degenerate rectangle at the origin with zero "
             "size.")
        .def(nb::init<double, double, double, double>(),
             "x"_a, "y"_a, "width"_a, "height"_a,
             "Construct a rectangle whose top-left corner is at (x, y) "
             "and with the given size.")
        .def_prop_rw("x",
            [](const Wt::WRectF& r) { return r.x(); },
            [](Wt::WRectF& r, double x) { r.setX(x); },
            "Top-left X coordinate.")
        .def_prop_rw("y",
            [](const Wt::WRectF& r) { return r.y(); },
            [](Wt::WRectF& r, double y) { r.setY(y); },
            "Top-left Y coordinate.")
        .def_prop_rw("width",
            [](const Wt::WRectF& r) { return r.width(); },
            [](Wt::WRectF& r, double w) { r.setWidth(w); },
            "Rectangle width.")
        .def_prop_rw("height",
            [](const Wt::WRectF& r) { return r.height(); },
            [](Wt::WRectF& r, double h) { r.setHeight(h); },
            "Rectangle height.")
        .def_prop_ro("is_null", &Wt::WRectF::isNull,
            "True when the rectangle is the default-constructed null "
            "value (distinct from a present-but-empty rect).")
        .def_prop_ro("is_empty", &Wt::WRectF::isEmpty,
            "True when width or height is zero (or negative).")
        .def_prop_ro("left", &Wt::WRectF::left,
            "Left edge (same as `x`).")
        .def_prop_ro("top", &Wt::WRectF::top,
            "Top edge (same as `y`).")
        .def("__repr__", [](const Wt::WRectF& r) {
            return "WRectF(x=" + std::to_string(r.x())
                + ", y=" + std::to_string(r.y())
                + ", w=" + std::to_string(r.width())
                + ", h=" + std::to_string(r.height()) + ")";
        });

    nb::class_<Wt::WLineF>(m, "WLineF",
        "A line segment between two points. Used in bulk-line draws "
        "(`WPainter.draw_lines`).")
        .def(nb::init<>(),
             "Construct a zero-length line at the origin.")
        .def(nb::init<double, double, double, double>(),
             "x1"_a, "y1"_a, "x2"_a, "y2"_a,
             "Construct a line from (x1, y1) to (x2, y2).")
        .def_prop_ro("x1", &Wt::WLineF::x1,
             "X coordinate of the start point.")
        .def_prop_ro("y1", &Wt::WLineF::y1,
             "Y coordinate of the start point.")
        .def_prop_ro("x2", &Wt::WLineF::x2,
             "X coordinate of the end point.")
        .def_prop_ro("y2", &Wt::WLineF::y2,
             "Y coordinate of the end point.")
        .def_prop_ro("p1", &Wt::WLineF::p1,
             "Start point as a WPointF.")
        .def_prop_ro("p2", &Wt::WLineF::p2,
             "End point as a WPointF.");

    nb::class_<Wt::WTransform>(m, "WTransform",
        "Affine 2-D transform as a 2x3 matrix (m11, m12, m21, m22, dx,\n"
        "dy). Applied to coordinates by WPainter operations after\n"
        "`set_world_transform`. Use `WPainter.translate / rotate / scale`\n"
        "for the common cases — construct a WTransform directly only\n"
        "when you need a combined or pre-computed matrix.")
        .def(nb::init<>(),
            "Identity transform.")
        .def_prop_ro("is_identity", &Wt::WTransform::isIdentity,
             "True when this transform leaves coordinates unchanged.")
        .def_prop_ro("m11", &Wt::WTransform::m11,
             "Row 1, column 1 of the matrix (X scale).")
        .def_prop_ro("m12", &Wt::WTransform::m12,
             "Row 1, column 2 of the matrix (Y shear into X).")
        .def_prop_ro("m21", &Wt::WTransform::m21,
             "Row 2, column 1 of the matrix (X shear into Y).")
        .def_prop_ro("m22", &Wt::WTransform::m22,
             "Row 2, column 2 of the matrix (Y scale).")
        .def_prop_ro("dx", &Wt::WTransform::dx,
             "X translation component.")
        .def_prop_ro("dy", &Wt::WTransform::dy,
             "Y translation component.")
        .def("reset", &Wt::WTransform::reset,
             "Restore the identity transform.")
        .def_prop_ro("determinant", &Wt::WTransform::determinant,
             "Matrix determinant — non-zero iff the transform is "
             "invertible.")
        .def("adjoint", &Wt::WTransform::adjoint,
             "Return the adjoint (transposed cofactor) matrix. Useful "
             "when computing inverses manually.")
        .def("map_point",
            // Wraps the void-with-out-pointers form into a returns-tuple
            // form for ergonomics. nb::make_tuple builds a Python tuple
            // directly; the std::pair caster isn't part of common.hpp.
            [](const Wt::WTransform& t, double x, double y) {
                double tx, ty;
                t.map(x, y, &tx, &ty);
                return nb::make_tuple(tx, ty);
            },
            "x"_a, "y"_a,
            "Apply the transform to (x, y) and return (tx, ty).");

    // ---- Font enums + WFont ----

    nb::enum_<Wt::FontFamily>(m, "FontFamily",
        "Generic font-family categories. Maps to the CSS generic family "
        "of the same name. Combine with `WFont.set_family`'s specific "
        "argument to nominate concrete font names.")
        .value("Default",    Wt::FontFamily::Default)
        .value("Serif",      Wt::FontFamily::Serif)
        .value("SansSerif",  Wt::FontFamily::SansSerif)
        .value("Cursive",    Wt::FontFamily::Cursive)
        .value("Fantasy",    Wt::FontFamily::Fantasy)
        .value("Monospace",  Wt::FontFamily::Monospace);

    nb::enum_<Wt::FontStyle>(m, "FontStyle",
        "CSS `font-style` value — upright, italic, or oblique.")
        .value("NormalStyle", Wt::FontStyle::Normal)
        .value("Italic",      Wt::FontStyle::Italic)
        .value("Oblique",     Wt::FontStyle::Oblique);

    nb::enum_<Wt::FontVariant>(m, "FontVariant",
        "CSS `font-variant` value. SmallCaps renders lowercase as "
        "smaller uppercase glyphs.")
        .value("Normal",    Wt::FontVariant::Normal)
        .value("SmallCaps", Wt::FontVariant::SmallCaps);

    nb::enum_<Wt::FontWeight>(m, "FontWeight",
        "CSS `font-weight` value. Pick a preset; Value means an explicit "
        "numeric weight is supplied to `WFont.set_weight`.")
        .value("Normal",  Wt::FontWeight::Normal)
        .value("Bold",    Wt::FontWeight::Bold)
        .value("Bolder",  Wt::FontWeight::Bolder)
        .value("Lighter", Wt::FontWeight::Lighter)
        .value("Value",   Wt::FontWeight::Value);

    nb::enum_<Wt::FontSize>(m, "FontSize",
        "CSS `font-size` keyword sizes. Use FixedSize together with "
        "`WFont.set_size(WLength)` for an explicit numeric size.")
        .value("XXSmall",  Wt::FontSize::XXSmall)
        .value("XSmall",   Wt::FontSize::XSmall)
        .value("Small",    Wt::FontSize::Small)
        .value("Medium",   Wt::FontSize::Medium)
        .value("Large",    Wt::FontSize::Large)
        .value("XLarge",   Wt::FontSize::XLarge)
        .value("XXLarge",  Wt::FontSize::XXLarge)
        .value("Smaller",  Wt::FontSize::Smaller)
        .value("Larger",   Wt::FontSize::Larger)
        .value("FixedSize", Wt::FontSize::FixedSize);

    nb::class_<Wt::WFont>(m, "WFont",
        "Font specification used by WPainter.draw_text and by widget "
        "decoration APIs. Holds family, style, variant, weight, and size "
        "— what CSS would call the `font` shorthand.")
        .def(nb::init<>(),
             "Construct a default-family font at the browser's default "
             "size.")
        .def(nb::init<Wt::FontFamily>(), "family"_a,
             "Construct with the given generic family.")
        .def("set_family", &Wt::WFont::setFamily,
             "family"_a, "specific_families"_a = Wt::WString(),
             "Generic family + optional comma-separated specific font "
             "names (e.g. setFamily(Monospace, \"'Courier New'\")).")
        .def("set_style", &Wt::WFont::setStyle, "style"_a,
             "Set the FontStyle (normal / italic / oblique).")
        .def("set_variant", &Wt::WFont::setVariant, "variant"_a,
             "Set the FontVariant (normal or small caps).")
        .def("set_weight", &Wt::WFont::setWeight,
             "weight"_a, "value"_a = 400,
             "When weight=Value, the second argument is the CSS numeric "
             "weight (100, 200, …, 900).")
        .def("set_size",
            // Overloaded: enum form OR WLength form. Lambda picks the
            // length form so Python callers can pass numbers or strings.
            [](Wt::WFont& f, const Wt::WLength& size) { f.setSize(size); },
            "size"_a,
            "Size as a WLength — accepts a number (treated as pixels), "
            "a WLength('1.2em'), or a parsed CSS string.")
        .def("size_length", &Wt::WFont::sizeLength,
             "medium_size"_a = 16.0,
             "Resolve the current size to a concrete WLength. Keyword "
             "sizes (Small, Large, …) are computed relative to "
             "`medium_size` pixels.");

    // ---- WGradient + GradientStyle ----
    //
    // Bound BEFORE WPen / WBrush because both reference WGradient as a
    // parameter type for set_gradient.

    nb::enum_<Wt::GradientStyle>(m, "GradientStyle",
        "Geometric form of a WGradient — straight axis (Linear) or "
        "concentric (Radial).")
        .value("Linear", Wt::GradientStyle::Linear)
        .value("Radial", Wt::GradientStyle::Radial);

    nb::class_<Wt::WGradient>(m, "WGradient",
        "Multi-stop colour gradient used as a pen stroke or brush fill.\n"
        "Configure geometry first (`set_linear_gradient` or\n"
        "`set_radial_gradient`), then add colour stops in order from 0.0\n"
        "(start) to 1.0 (end).\n"
        "\n"
        "    g = wt.WGradient()\n"
        "    g.set_linear_gradient(0, 0, 100, 0)\n"
        "    g.add_color_stop(0.0, wt.WColor('red'))\n"
        "    g.add_color_stop(1.0, wt.WColor('yellow'))\n"
        "    painter.set_brush(wt.WBrush(g))")
        .def(nb::init<>(),
             "Construct an empty (no-geometry, no-stops) gradient.")
        .def_prop_ro("style", &Wt::WGradient::style,
             "Linear or Radial — set by the last set_* call.")
        .def_prop_ro("is_empty", &Wt::WGradient::isEmpty,
             "True when no colour stops have been added yet.")
        .def("set_linear_gradient", &Wt::WGradient::setLinearGradient,
             "x0"_a, "y0"_a, "x1"_a, "y1"_a,
             "Configure a linear gradient from (x0,y0) to (x1,y1).")
        .def("set_radial_gradient", &Wt::WGradient::setRadialGradient,
             "cx"_a, "cy"_a, "r"_a, "fx"_a, "fy"_a,
             "Configure a radial gradient: bounding circle centred at "
             "(cx,cy) with radius r, focal point at (fx,fy).")
        .def("add_color_stop",
            nb::overload_cast<double, const Wt::WColor&>(
                &Wt::WGradient::addColorStop),
            "position"_a, "color"_a,
            "Add a color stop at `position` (0.0 = start, 1.0 = end).")
        .def("clear_color_stops", &Wt::WGradient::clearColorStops,
             "Remove every previously-added colour stop.");

    // ---- WShadow ----
    //
    // Applied via WPainter.set_shadow (offsets + blur in the painter's
    // current coordinate system; color sets the shadow tint).

    nb::class_<Wt::WShadow>(m, "WShadow",
        "Drop-shadow descriptor — offset, blur radius, and colour. Pass "
        "to `WPainter.set_shadow` to apply to subsequent draws; pass the "
        "default-constructed WShadow() to clear.")
        .def(nb::init<>(),
             "Construct the no-shadow value.")
        .def(nb::init<double, double, const Wt::WColor&, double>(),
             "dx"_a, "dy"_a, "color"_a, "blur"_a,
             "Construct a shadow offset by (dx, dy) in the painter's "
             "current coordinates, tinted `color`, with `blur` blur "
             "radius.")
        .def("set_offsets", &Wt::WShadow::setOffsets, "dx"_a, "dy"_a,
             "Set the shadow's offset.")
        .def("set_color", &Wt::WShadow::setColor, "color"_a,
             "Set the shadow's tint colour.")
        .def("set_blur", &Wt::WShadow::setBlur, "blur"_a,
             "Set the Gaussian blur radius.")
        .def_prop_ro("offset_x", &Wt::WShadow::offsetX,
             "Horizontal shadow offset.")
        .def_prop_ro("offset_y", &Wt::WShadow::offsetY,
             "Vertical shadow offset.")
        .def_prop_ro("color", &Wt::WShadow::color,
             "Shadow tint colour.")
        .def_prop_ro("blur", &Wt::WShadow::blur,
             "Blur radius.")
        .def_prop_ro("none", &Wt::WShadow::none,
             "True for the default (no-shadow) value.");

    // ---- WBorder + BorderStyle + BorderWidth ----
    //
    // CSS-border value type used by WCssDecorationStyle (not yet bound)
    // and a few widget set_decoration methods.

    nb::enum_<Wt::BorderStyle>(m, "BorderStyle",
        "CSS `border-style` value. Mirrors the standard set of CSS "
        "borders — Solid for the common case, Dotted/Dashed for "
        "discontinuous strokes, Groove/Ridge/Inset/Outset for 3-D "
        "effects.")
        .value("None_",   Wt::BorderStyle::None)
        .value("Hidden",  Wt::BorderStyle::Hidden)
        .value("Dotted",  Wt::BorderStyle::Dotted)
        .value("Dashed",  Wt::BorderStyle::Dashed)
        .value("Solid",   Wt::BorderStyle::Solid)
        .value("Double",  Wt::BorderStyle::Double)
        .value("Groove",  Wt::BorderStyle::Groove)
        .value("Ridge",   Wt::BorderStyle::Ridge)
        .value("Inset",   Wt::BorderStyle::Inset)
        .value("Outset",  Wt::BorderStyle::Outset);

    nb::enum_<Wt::BorderWidth>(m, "BorderWidth",
        "CSS `border-width` keyword. Use Explicit together with the "
        "WLength-taking WBorder constructor for a numeric width.")
        .value("Thin",     Wt::BorderWidth::Thin)
        .value("Medium",   Wt::BorderWidth::Medium)
        .value("Thick",    Wt::BorderWidth::Thick)
        .value("Explicit", Wt::BorderWidth::Explicit);

    nb::class_<Wt::WBorder>(m, "WBorder",
        "Value type describing a CSS border — style, width, and colour. "
        "Passed to widget decoration APIs (WCssDecorationStyle etc.).")
        .def(nb::init<>(),
             "Construct the default (no border) value.")
        .def(nb::init<Wt::BorderStyle, Wt::BorderWidth, Wt::WColor>(),
             "style"_a, "width"_a, "color"_a,
             "Construct from a style, a keyword width (Thin/Medium/"
             "Thick), and a colour.")
        .def(nb::init<Wt::BorderStyle, const Wt::WLength&, Wt::WColor>(),
             "style"_a, "width"_a, "color"_a,
             "Explicit-width variant — `width` is a WLength rather than "
             "the Thin/Medium/Thick preset.")
        .def("set_style", &Wt::WBorder::setStyle, "style"_a,
             "Change the border style.")
        .def("set_color", &Wt::WBorder::setColor, "color"_a,
             "Change the border colour.")
        .def_prop_ro("style", &Wt::WBorder::style,
             "Current BorderStyle.")
        .def_prop_ro("color", &Wt::WBorder::color,
             "Current border colour.")
        .def_prop_ro("explicit_width", &Wt::WBorder::explicitWidth,
             "Explicit width as a WLength (meaningful only when the "
             "border was constructed with the WLength-taking ctor).");

    // ---- Pen styles + WPen ----

    nb::enum_<Wt::PenStyle>(m, "PenStyle",
        "Stroke dash pattern. NoPen suppresses the stroke entirely (use "
        "for fill-only draws).")
        .value("NoPen",        Wt::PenStyle::None)
        .value("SolidLine",    Wt::PenStyle::SolidLine)
        .value("DashLine",     Wt::PenStyle::DashLine)
        .value("DotLine",      Wt::PenStyle::DotLine)
        .value("DashDotLine",  Wt::PenStyle::DashDotLine)
        .value("DashDotDotLine", Wt::PenStyle::DashDotDotLine);

    nb::enum_<Wt::PenCapStyle>(m, "PenCapStyle",
        "Shape applied at the ends of stroked open paths — flush "
        "(FlatCap), squared off past the endpoint (SquareCap), or a "
        "semicircle (RoundCap).")
        .value("FlatCap",   Wt::PenCapStyle::Flat)
        .value("SquareCap", Wt::PenCapStyle::Square)
        .value("RoundCap",  Wt::PenCapStyle::Round);

    nb::enum_<Wt::PenJoinStyle>(m, "PenJoinStyle",
        "Shape applied where two stroked segments meet — sharp point "
        "(MiterJoin), flattened (BevelJoin), or rounded (RoundJoin).")
        .value("MiterJoin", Wt::PenJoinStyle::Miter)
        .value("BevelJoin", Wt::PenJoinStyle::Bevel)
        .value("RoundJoin", Wt::PenJoinStyle::Round);

    nb::class_<Wt::WPen>(m, "WPen",
        "Stroke specification — colour or gradient, dash style, line "
        "cap, join style, and width. Assigned to a WPainter via "
        "`set_pen`; affects every subsequent stroke or outline.")
        .def(nb::init<>(),
             "Construct a default black 1-px solid pen.")
        .def(nb::init<Wt::PenStyle>(), "style"_a,
             "Construct a pen with the given dash style (and default "
             "colour and width).")
        .def(nb::init<const Wt::WColor&>(), "color"_a,
             "Construct a solid pen of the given colour.")
        .def("set_style", &Wt::WPen::setStyle, "style"_a,
             "Set the dash pattern.")
        .def("set_cap_style", &Wt::WPen::setCapStyle, "style"_a,
             "Set the line-end cap style.")
        .def("set_join_style", &Wt::WPen::setJoinStyle, "style"_a,
             "Set the join style for connected segments.")
        .def("set_width", &Wt::WPen::setWidth, "width"_a,
             "Set stroke width (a WLength — number for pixels, or a "
             "WLength with explicit units).")
        .def("set_color", &Wt::WPen::setColor, "color"_a,
             "Set the stroke colour.")
        .def("set_gradient", &Wt::WPen::setGradient, "gradient"_a,
             "Use a gradient for the stroke instead of a solid color.")
        .def_prop_ro("color", &Wt::WPen::color,
             "Current stroke colour.")
        .def_prop_ro("style", &Wt::WPen::style,
             "Current dash pattern.")
        .def_prop_ro("cap_style", &Wt::WPen::capStyle,
             "Current line-end cap style.")
        .def_prop_ro("join_style", &Wt::WPen::joinStyle,
             "Current segment join style.")
        .def_prop_ro("width", &Wt::WPen::width,
             "Current stroke width as a WLength.");

    // ---- Brush style + WBrush ----

    nb::enum_<Wt::BrushStyle>(m, "BrushStyle",
        "Fill pattern for a WBrush. NoBrush leaves the interior "
        "unfilled; SolidPattern fills with a single colour; Gradient "
        "uses the brush's attached WGradient.")
        .value("NoBrush",   Wt::BrushStyle::None)
        .value("SolidPattern", Wt::BrushStyle::Solid)
        .value("Gradient",     Wt::BrushStyle::Gradient);

    nb::class_<Wt::WBrush>(m, "WBrush",
        "Fill specification — a solid colour or a gradient. Assigned to "
        "a WPainter via `set_brush`; affects every subsequent filled "
        "shape (rectangle, ellipse, path, etc.).")
        .def(nb::init<>(),
             "Construct the no-fill (NoBrush) value.")
        .def(nb::init<Wt::BrushStyle>(), "style"_a,
             "Construct with the given style and default colour.")
        .def(nb::init<const Wt::WColor&>(), "color"_a,
             "Construct a solid-colour brush.")
        .def(nb::init<const Wt::WGradient&>(), "gradient"_a,
             "Construct a gradient-filled brush. style is set to Gradient.")
        .def("set_style", &Wt::WBrush::setStyle, "style"_a,
             "Switch fill style.")
        .def("set_color", &Wt::WBrush::setColor, "color"_a,
             "Set the solid fill colour (also switches to SolidPattern).")
        .def("set_gradient", &Wt::WBrush::setGradient, "gradient"_a,
             "Use a gradient for the fill. Sets style to Gradient.")
        .def_prop_ro("color", &Wt::WBrush::color,
             "Current fill colour.")
        .def_prop_ro("style", &Wt::WBrush::style,
             "Current fill style.");

    // ---- WPainterPath ----
    //
    // Geometric path used by drawPath / setClipPath. Build incrementally
    // via moveTo / lineTo / cubicTo / arcTo, then hand to a WPainter for
    // stroke or fill.

    nb::class_<Wt::WPainterPath>(m, "WPainterPath",
        "A geometric path built from straight lines, Bézier curves, and\n"
        "arcs — the parametric input to `WPainter.draw_path` and\n"
        "`WPainter.set_clip_path`. Build incrementally: move the pen,\n"
        "draw segments, optionally close back to the start.\n"
        "\n"
        "    path = wt.WPainterPath()\n"
        "    path.move_to(10, 10)\n"
        "    path.line_to(50, 10)\n"
        "    path.cubic_to(80, 10, 80, 80, 50, 80)\n"
        "    path.close_sub_path()\n"
        "    painter.draw_path(path)")
        .def(nb::init<>(),
             "Construct an empty path.")
        .def(nb::init<const Wt::WPointF&>(), "start"_a,
             "Begin the path at the given start point.")
        .def_prop_ro("is_empty", &Wt::WPainterPath::isEmpty,
             "True when no segments have been added yet.")
        .def_prop_ro("current_position",
                     &Wt::WPainterPath::currentPosition,
             "End point of the most recently added segment — the implicit"
             " starting point of the next `line_to` / `cubic_to` / "
             "`arc_to`.")
        .def("close_sub_path", &Wt::WPainterPath::closeSubPath,
             "Close the current sub-path with a line back to its start.")
        .def("move_to",
            nb::overload_cast<double, double>(&Wt::WPainterPath::moveTo),
            "x"_a, "y"_a,
            "Begin a new sub-path at (x, y) without drawing a connecting "
            "segment.")
        .def("line_to",
            nb::overload_cast<double, double>(&Wt::WPainterPath::lineTo),
            "x"_a, "y"_a,
            "Append a straight line from the current position to (x, y).")
        .def("cubic_to",
            nb::overload_cast<double, double, double, double, double, double>(
                &Wt::WPainterPath::cubicTo),
            "c1x"_a, "c1y"_a, "c2x"_a, "c2y"_a, "end_x"_a, "end_y"_a,
            "Cubic Bézier from current position to (end_x, end_y) via "
            "control points (c1x, c1y) and (c2x, c2y).")
        .def("arc_to",
            nb::overload_cast<double, double, double, double, double>(
                &Wt::WPainterPath::arcTo),
            "cx"_a, "cy"_a, "radius"_a,
            "start_angle"_a, "sweep_length"_a,
            "Arc of `radius` centred at (cx, cy); angles in degrees, "
            "0° = 3 o'clock, sweeping counter-clockwise.")
        .def("add_rect",
            [](Wt::WPainterPath& p, double x, double y,
               double w, double h) {
                p.addRect(Wt::WRectF(x, y, w, h));
            },
            "x"_a, "y"_a, "width"_a, "height"_a,
            "Add an axis-aligned rectangle as a closed sub-path.")
        .def("add_ellipse",
            [](Wt::WPainterPath& p, double x, double y,
               double w, double h) {
                p.addEllipse(Wt::WRectF(x, y, w, h));
            },
            "x"_a, "y"_a, "width"_a, "height"_a,
            "Add an ellipse inscribed in the bounding rect as a closed "
            "sub-path.");
}

}  // namespace witty_for_python
