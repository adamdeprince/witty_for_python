#include "common.hpp"

#include <Wt/WAbstractArea.h>
#include <Wt/WBrush.h>
#include <Wt/WCircleArea.h>
#include <Wt/WFont.h>
#include <Wt/WGlobal.h>
#include <Wt/WLineF.h>
#include <Wt/WLink.h>
#include <Wt/WPaintedWidget.h>
#include <Wt/WPaintDevice.h>
#include <Wt/WPainter.h>
#include <Wt/WPainterPath.h>
#include <Wt/WPen.h>
#include <Wt/WPointF.h>
#include <Wt/WPolygonArea.h>
#include <Wt/WRectArea.h>
#include <Wt/WRectF.h>
#include <Wt/WTextF.h>
#include <Wt/WTransform.h>

#include <memory>
#include <string>
#include <vector>

namespace witty_for_python {

namespace {

// ---- Trampoline WPaintedWidget ----
//
// WPaintedWidget's paintEvent is pure virtual. Subclassing from Python
// would need a full nanobind trampoline; instead we expose a simpler
// callable-holding subclass that dispatches paintEvent to a stored
// Python callable. From Python:
//
//   def paint(painter):
//       painter.draw_line(0, 0, 100, 100)
//   w = wt.WPaintedWidget(paint)
//
// The painter handed to the callback is a *non-owning* view of a stack-
// allocated WPainter; using it after the call returns is undefined.

class PyPaintedWidget : public Wt::WPaintedWidget {
public:
    PyPaintedWidget() : Wt::WPaintedWidget() {}

    void setPaintCallback(nb::callable cb) {
        nb::gil_scoped_acquire gil;
        paint_callback_ = std::make_shared<nb::object>(std::move(cb));
    }

protected:
    void paintEvent(Wt::WPaintDevice* device) override {
        if (!paint_callback_) return;
        nb::gil_scoped_acquire gil;
        try {
            Wt::WPainter painter(device);
            (*paint_callback_)(&painter);
        } catch (nb::python_error& e) {
            e.restore();
            PyErr_WriteUnraisable(paint_callback_->ptr());
        }
    }

private:
    std::shared_ptr<nb::object> paint_callback_;
};

}  // namespace

void register_painting(nb::module_& m) {
    // ---- WPainter ----
    //
    // The verb interface. Method names match Wt's C++ surface in
    // snake_case. drawText forms take a WRectF and an AlignmentFlag-int
    // bitmask (e.g. AlignmentFlag.Center | AlignmentFlag.Middle).

    nb::class_<Wt::WPainter>(m, "WPainter")
        // No public default constructor exposed — Python users receive
        // a WPainter from the WPaintedWidget callback. We expose the
        // device-taking constructor for direct off-screen use.
        .def(nb::init<Wt::WPaintDevice*>(), "device"_a,
            "Construct a painter bound to a paint device. The device is "
            "not owned; the painter borrows it for its lifetime.")
        // ---- state ----
        .def("save", &Wt::WPainter::save,
             "Push the current state (pen, brush, font, transform, "
             "clipping) onto an internal stack. Pair with restore().")
        .def("restore", &Wt::WPainter::restore)
        .def("set_pen", &Wt::WPainter::setPen, "pen"_a)
        .def("set_brush", &Wt::WPainter::setBrush, "brush"_a)
        .def("set_font", &Wt::WPainter::setFont, "font"_a)
        .def_prop_ro("pen", &Wt::WPainter::pen,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("brush", &Wt::WPainter::brush,
                     nb::rv_policy::reference_internal)
        // ---- transform ----
        .def("set_world_transform",
             nb::overload_cast<const Wt::WTransform&, bool>(
                 &Wt::WPainter::setWorldTransform),
             "transform"_a, "combine"_a = false)
        .def("translate",
             nb::overload_cast<double, double>(&Wt::WPainter::translate),
             "dx"_a, "dy"_a)
        .def("rotate", &Wt::WPainter::rotate, "angle"_a,
             "Rotate by `angle` degrees about the origin of the local "
             "coordinate system.")
        .def("scale", &Wt::WPainter::scale, "sx"_a, "sy"_a)
        // ---- clipping ----
        .def("set_clipping", &Wt::WPainter::setClipping, "enabled"_a)
        .def("set_clip_path", &Wt::WPainter::setClipPath, "path"_a)
        // ---- draw primitives (numeric, value-type-free) ----
        .def("draw_line",
             nb::overload_cast<double, double, double, double>(
                 &Wt::WPainter::drawLine),
             "x1"_a, "y1"_a, "x2"_a, "y2"_a)
        .def("draw_rect",
             nb::overload_cast<double, double, double, double>(
                 &Wt::WPainter::drawRect),
             "x"_a, "y"_a, "width"_a, "height"_a)
        .def("draw_ellipse",
             nb::overload_cast<double, double, double, double>(
                 &Wt::WPainter::drawEllipse),
             "x"_a, "y"_a, "width"_a, "height"_a,
             "Ellipse inscribed in the given bounding rect.")
        .def("draw_arc",
             nb::overload_cast<double, double, double, double, int, int>(
                 &Wt::WPainter::drawArc),
             "x"_a, "y"_a, "width"_a, "height"_a,
             "start_angle"_a, "span_angle"_a,
             "Arc inscribed in the bounding rect, swept from start to "
             "start+span (in 1/16-degree units, Wt convention).")
        .def("draw_pie",
             nb::overload_cast<double, double, double, double, int, int>(
                 &Wt::WPainter::drawPie),
             "x"_a, "y"_a, "width"_a, "height"_a,
             "start_angle"_a, "span_angle"_a)
        .def("draw_chord",
             nb::overload_cast<double, double, double, double, int, int>(
                 &Wt::WPainter::drawChord),
             "x"_a, "y"_a, "width"_a, "height"_a,
             "start_angle"_a, "span_angle"_a)
        .def("draw_point",
             nb::overload_cast<double, double>(&Wt::WPainter::drawPoint),
             "x"_a, "y"_a)
        .def("draw_path", &Wt::WPainter::drawPath, "path"_a)
        .def("draw_lines",
             nb::overload_cast<const std::vector<Wt::WLineF>&>(
                 &Wt::WPainter::drawLines),
             "lines"_a)
        .def("draw_text",
            // Bridge to Wt's WRectF + WFlags<AlignmentFlag> + WTextF form.
            // Python passes a plain str + an int-OR'd alignment.
            [](Wt::WPainter& p, double x, double y,
               double w, double h, int alignment,
               const Wt::WString& text) {
                p.drawText(
                    Wt::WRectF(x, y, w, h),
                    Wt::WFlags<Wt::AlignmentFlag>(
                        static_cast<Wt::AlignmentFlag>(alignment)),
                    Wt::WTextF(text));
            },
            "x"_a, "y"_a, "width"_a, "height"_a,
            "alignment"_a, "text"_a,
            "Draw text into the rect. `alignment` is an OR of "
            "AlignmentFlag values (e.g. Center | Middle).")
        // ---- device / state ----
        .def_prop_ro("is_active", &Wt::WPainter::isActive);

    // ---- WPaintedWidget (callback shim) ----
    //
    // Bound as the C++ trampoline subclass PyPaintedWidget. Python users
    // see it as `wt.WPaintedWidget`. Override the paint behaviour by
    // passing a callable at construction (or via set_paint_callback).
    // Wt's paintEvent fires from a worker thread; the trampoline
    // acquires the GIL before calling Python.

    nb::class_<PyPaintedWidget, Wt::WInteractWidget>(m, "WPaintedWidget")
        .def("__init__", [](PyPaintedWidget* self) {
            new (self) PyPaintedWidget();
        })
        .def("__init__", [](PyPaintedWidget* self, nb::callable paint) {
            new (self) PyPaintedWidget();
            self->setPaintCallback(std::move(paint));
        }, "paint"_a,
           "Construct with the paint callback. The callable takes a single "
           "WPainter argument — use its draw_* methods to render.")
        .def("set_paint_callback", &PyPaintedWidget::setPaintCallback,
             "paint"_a,
             "Replace the paint callback. The new callback will be used "
             "from the next paintEvent onward; call update() to force a "
             "redraw immediately.")
        .def("update",
            [](PyPaintedWidget& self) { self.update(); },
            "Schedule a repaint. Wt batches paint events — the actual "
            "paintEvent fires after the current event loop tick.")
        .def("set_preferred_method",
            &Wt::WPaintedWidget::setPreferredMethod, "method"_a,
            "Render backend: InlineSvgVml, HtmlCanvas, or PngImage. "
            "HtmlCanvas is the default on modern browsers.")
        .def_prop_ro("preferred_method",
            &Wt::WPaintedWidget::preferredMethod)
        .def("add_area",
            // Ownership: move unique_ptr in, return raw pointer for
            // chained access (matches the project's add_widget pattern).
            [](PyPaintedWidget& self,
               std::unique_ptr<Wt::WAbstractArea> area)
                -> Wt::WAbstractArea* {
                Wt::WAbstractArea* raw = area.get();
                self.addArea(std::move(area));
                return raw;
            },
            "area"_a,
            nb::rv_policy::reference_internal,
            "Attach an image-map area (WRectArea / WCircleArea / "
            "WPolygonArea) that becomes a clickable region on top of "
            "the painted output.")
        .def("insert_area",
            [](PyPaintedWidget& self, int index,
               std::unique_ptr<Wt::WAbstractArea> area)
                -> Wt::WAbstractArea* {
                Wt::WAbstractArea* raw = area.get();
                self.insertArea(index, std::move(area));
                return raw;
            },
            "index"_a, "area"_a,
            nb::rv_policy::reference_internal);

    // ---- RenderMethod (used by setPreferredMethod) ----

    nb::enum_<Wt::RenderMethod>(m, "RenderMethod")
        .value("InlineSvgVml", Wt::RenderMethod::InlineSvgVml)
        .value("HtmlCanvas",   Wt::RenderMethod::HtmlCanvas)
        .value("PngImage",     Wt::RenderMethod::PngImage);

    // ---- Image-map areas ----
    //
    // WAbstractArea is the base for clickable regions overlaid on a
    // WPaintedWidget (or WImage). Each area can carry a WLink, alternate
    // text, and a tooltip — the area renders as an HTML <area> element
    // inside a <map>.

    nb::class_<Wt::WAbstractArea, Wt::WObject>(m, "WAbstractArea")
        .def("set_link", &Wt::WAbstractArea::setLink, "link"_a)
        .def("set_alternate_text", &Wt::WAbstractArea::setAlternateText,
             "text"_a)
        .def("set_tool_tip", &Wt::WAbstractArea::setToolTip, "text"_a)
        .def("set_style_class",
            // Disambiguate the WT_USTRING form from the `const char*` form.
            [](Wt::WAbstractArea& self, const Wt::WString& style_class) {
                self.setStyleClass(style_class);
            },
            "style_class"_a)
        .def_prop_rw("hole",
            &Wt::WAbstractArea::isHole,
            &Wt::WAbstractArea::setHole,
            "When True, this area is treated as a hole (transparent to "
            "clicks) cut out of the surrounding map.")
        .def_prop_rw("transformable",
            &Wt::WAbstractArea::isTransformable,
            &Wt::WAbstractArea::setTransformable);

    nb::class_<Wt::WCircleArea, Wt::WAbstractArea>(m, "WCircleArea")
        .def(nb::init<>())
        .def(nb::init<int, int, int>(),
             "x"_a, "y"_a, "radius"_a)
        .def("set_center",
            nb::overload_cast<int, int>(&Wt::WCircleArea::setCenter),
            "x"_a, "y"_a)
        .def_prop_ro("center_x", &Wt::WCircleArea::centerX)
        .def_prop_ro("center_y", &Wt::WCircleArea::centerY)
        .def_prop_rw("radius",
            &Wt::WCircleArea::radius,
            &Wt::WCircleArea::setRadius);

    nb::class_<Wt::WRectArea, Wt::WAbstractArea>(m, "WRectArea")
        .def(nb::init<>())
        .def(nb::init<int, int, int, int>(),
             "x"_a, "y"_a, "width"_a, "height"_a)
        .def(nb::init<const Wt::WRectF&>(), "rect"_a);

    nb::class_<Wt::WPolygonArea, Wt::WAbstractArea>(m, "WPolygonArea")
        .def(nb::init<>())
        .def(nb::init<const std::vector<Wt::WPointF>&>(), "points"_a)
        .def("add_point",
            nb::overload_cast<double, double>(&Wt::WPolygonArea::addPoint),
            "x"_a, "y"_a)
        .def("set_points",
            nb::overload_cast<const std::vector<Wt::WPointF>&>(
                &Wt::WPolygonArea::setPoints),
            "points"_a);
}

}  // namespace witty_for_python
