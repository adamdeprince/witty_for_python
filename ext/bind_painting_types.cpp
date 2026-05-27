#include "common.hpp"

#include <Wt/WBrush.h>
#include <Wt/WFont.h>
#include <Wt/WGlobal.h>           // PenStyle, BrushStyle, FontFamily, …
#include <Wt/WLength.h>
#include <Wt/WLineF.h>
#include <Wt/WPainterPath.h>
#include <Wt/WPen.h>
#include <Wt/WPointF.h>
#include <Wt/WRectF.h>
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

    nb::class_<Wt::WPointF>(m, "WPointF")
        .def(nb::init<>())
        .def(nb::init<double, double>(), "x"_a, "y"_a)
        .def_prop_rw("x",
            [](const Wt::WPointF& p) { return p.x(); },
            [](Wt::WPointF& p, double x) { p.setX(x); })
        .def_prop_rw("y",
            [](const Wt::WPointF& p) { return p.y(); },
            [](Wt::WPointF& p, double y) { p.setY(y); })
        .def("__repr__", [](const Wt::WPointF& p) {
            return "WPointF(x=" + std::to_string(p.x())
                + ", y=" + std::to_string(p.y()) + ")";
        });

    nb::class_<Wt::WRectF>(m, "WRectF")
        .def(nb::init<>())
        .def(nb::init<double, double, double, double>(),
             "x"_a, "y"_a, "width"_a, "height"_a)
        .def_prop_rw("x",
            [](const Wt::WRectF& r) { return r.x(); },
            [](Wt::WRectF& r, double x) { r.setX(x); })
        .def_prop_rw("y",
            [](const Wt::WRectF& r) { return r.y(); },
            [](Wt::WRectF& r, double y) { r.setY(y); })
        .def_prop_rw("width",
            [](const Wt::WRectF& r) { return r.width(); },
            [](Wt::WRectF& r, double w) { r.setWidth(w); })
        .def_prop_rw("height",
            [](const Wt::WRectF& r) { return r.height(); },
            [](Wt::WRectF& r, double h) { r.setHeight(h); })
        .def_prop_ro("is_null", &Wt::WRectF::isNull)
        .def_prop_ro("is_empty", &Wt::WRectF::isEmpty)
        .def_prop_ro("left", &Wt::WRectF::left)
        .def_prop_ro("top", &Wt::WRectF::top)
        .def("__repr__", [](const Wt::WRectF& r) {
            return "WRectF(x=" + std::to_string(r.x())
                + ", y=" + std::to_string(r.y())
                + ", w=" + std::to_string(r.width())
                + ", h=" + std::to_string(r.height()) + ")";
        });

    nb::class_<Wt::WLineF>(m, "WLineF")
        .def(nb::init<>())
        .def(nb::init<double, double, double, double>(),
             "x1"_a, "y1"_a, "x2"_a, "y2"_a)
        .def_prop_ro("x1", &Wt::WLineF::x1)
        .def_prop_ro("y1", &Wt::WLineF::y1)
        .def_prop_ro("x2", &Wt::WLineF::x2)
        .def_prop_ro("y2", &Wt::WLineF::y2)
        .def_prop_ro("p1", &Wt::WLineF::p1)
        .def_prop_ro("p2", &Wt::WLineF::p2);

    nb::class_<Wt::WTransform>(m, "WTransform")
        .def(nb::init<>(),
            "Identity transform.")
        .def_prop_ro("is_identity", &Wt::WTransform::isIdentity)
        .def_prop_ro("m11", &Wt::WTransform::m11)
        .def_prop_ro("m12", &Wt::WTransform::m12)
        .def_prop_ro("m21", &Wt::WTransform::m21)
        .def_prop_ro("m22", &Wt::WTransform::m22)
        .def_prop_ro("dx", &Wt::WTransform::dx)
        .def_prop_ro("dy", &Wt::WTransform::dy)
        .def("reset", &Wt::WTransform::reset,
             "Restore the identity transform.")
        .def_prop_ro("determinant", &Wt::WTransform::determinant)
        .def("adjoint", &Wt::WTransform::adjoint)
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

    nb::enum_<Wt::FontFamily>(m, "FontFamily")
        .value("Default",    Wt::FontFamily::Default)
        .value("Serif",      Wt::FontFamily::Serif)
        .value("SansSerif",  Wt::FontFamily::SansSerif)
        .value("Cursive",    Wt::FontFamily::Cursive)
        .value("Fantasy",    Wt::FontFamily::Fantasy)
        .value("Monospace",  Wt::FontFamily::Monospace);

    nb::enum_<Wt::FontStyle>(m, "FontStyle")
        .value("NormalStyle", Wt::FontStyle::Normal)
        .value("Italic",      Wt::FontStyle::Italic)
        .value("Oblique",     Wt::FontStyle::Oblique);

    nb::enum_<Wt::FontVariant>(m, "FontVariant")
        .value("Normal",    Wt::FontVariant::Normal)
        .value("SmallCaps", Wt::FontVariant::SmallCaps);

    nb::enum_<Wt::FontWeight>(m, "FontWeight")
        .value("Normal",  Wt::FontWeight::Normal)
        .value("Bold",    Wt::FontWeight::Bold)
        .value("Bolder",  Wt::FontWeight::Bolder)
        .value("Lighter", Wt::FontWeight::Lighter)
        .value("Value",   Wt::FontWeight::Value);

    nb::enum_<Wt::FontSize>(m, "FontSize")
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

    nb::class_<Wt::WFont>(m, "WFont")
        .def(nb::init<>())
        .def(nb::init<Wt::FontFamily>(), "family"_a)
        .def("set_family", &Wt::WFont::setFamily,
             "family"_a, "specific_families"_a = Wt::WString(),
             "Generic family + optional comma-separated specific font "
             "names (e.g. setFamily(Monospace, \"'Courier New'\")).")
        .def("set_style", &Wt::WFont::setStyle, "style"_a)
        .def("set_variant", &Wt::WFont::setVariant, "variant"_a)
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
             "medium_size"_a = 16.0);

    // ---- Pen styles + WPen ----

    nb::enum_<Wt::PenStyle>(m, "PenStyle")
        .value("NoPen",        Wt::PenStyle::None)
        .value("SolidLine",    Wt::PenStyle::SolidLine)
        .value("DashLine",     Wt::PenStyle::DashLine)
        .value("DotLine",      Wt::PenStyle::DotLine)
        .value("DashDotLine",  Wt::PenStyle::DashDotLine)
        .value("DashDotDotLine", Wt::PenStyle::DashDotDotLine);

    nb::enum_<Wt::PenCapStyle>(m, "PenCapStyle")
        .value("FlatCap",   Wt::PenCapStyle::Flat)
        .value("SquareCap", Wt::PenCapStyle::Square)
        .value("RoundCap",  Wt::PenCapStyle::Round);

    nb::enum_<Wt::PenJoinStyle>(m, "PenJoinStyle")
        .value("MiterJoin", Wt::PenJoinStyle::Miter)
        .value("BevelJoin", Wt::PenJoinStyle::Bevel)
        .value("RoundJoin", Wt::PenJoinStyle::Round);

    nb::class_<Wt::WPen>(m, "WPen")
        .def(nb::init<>())
        .def(nb::init<Wt::PenStyle>(), "style"_a)
        .def(nb::init<const Wt::WColor&>(), "color"_a)
        .def("set_style", &Wt::WPen::setStyle, "style"_a)
        .def("set_cap_style", &Wt::WPen::setCapStyle, "style"_a)
        .def("set_join_style", &Wt::WPen::setJoinStyle, "style"_a)
        .def("set_width", &Wt::WPen::setWidth, "width"_a)
        .def("set_color", &Wt::WPen::setColor, "color"_a)
        .def_prop_ro("color", &Wt::WPen::color)
        .def_prop_ro("style", &Wt::WPen::style)
        .def_prop_ro("cap_style", &Wt::WPen::capStyle)
        .def_prop_ro("join_style", &Wt::WPen::joinStyle)
        .def_prop_ro("width", &Wt::WPen::width);

    // ---- Brush style + WBrush ----

    nb::enum_<Wt::BrushStyle>(m, "BrushStyle")
        .value("NoBrush",   Wt::BrushStyle::None)
        .value("SolidPattern", Wt::BrushStyle::Solid)
        .value("Gradient",     Wt::BrushStyle::Gradient);

    nb::class_<Wt::WBrush>(m, "WBrush")
        .def(nb::init<>())
        .def(nb::init<Wt::BrushStyle>(), "style"_a)
        .def(nb::init<const Wt::WColor&>(), "color"_a)
        .def("set_style", &Wt::WBrush::setStyle, "style"_a)
        .def("set_color", &Wt::WBrush::setColor, "color"_a)
        .def_prop_ro("color", &Wt::WBrush::color)
        .def_prop_ro("style", &Wt::WBrush::style);

    // ---- WPainterPath ----
    //
    // Geometric path used by drawPath / setClipPath. Build incrementally
    // via moveTo / lineTo / cubicTo / arcTo, then hand to a WPainter for
    // stroke or fill.

    nb::class_<Wt::WPainterPath>(m, "WPainterPath")
        .def(nb::init<>())
        .def(nb::init<const Wt::WPointF&>(), "start"_a,
             "Begin the path at the given start point.")
        .def_prop_ro("is_empty", &Wt::WPainterPath::isEmpty)
        .def_prop_ro("current_position",
                     &Wt::WPainterPath::currentPosition)
        .def("close_sub_path", &Wt::WPainterPath::closeSubPath,
             "Close the current sub-path with a line back to its start.")
        .def("move_to",
            nb::overload_cast<double, double>(&Wt::WPainterPath::moveTo),
            "x"_a, "y"_a)
        .def("line_to",
            nb::overload_cast<double, double>(&Wt::WPainterPath::lineTo),
            "x"_a, "y"_a)
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
            "x"_a, "y"_a, "width"_a, "height"_a)
        .def("add_ellipse",
            [](Wt::WPainterPath& p, double x, double y,
               double w, double h) {
                p.addEllipse(Wt::WRectF(x, y, w, h));
            },
            "x"_a, "y"_a, "width"_a, "height"_a);
}

}  // namespace witty_for_python
