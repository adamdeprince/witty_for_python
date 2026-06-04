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
#include <Wt/WResource.h>
#include <Wt/WPainter.h>
#include <Wt/WPainterPath.h>
#include <Wt/WPen.h>
#include <Wt/WShadow.h>
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
    // ---- WPainter::Image (nested value type used by drawImage) ----
    //
    // Bound BEFORE WPainter itself so the drawImage overloads below can
    // reference it as a registered parameter type. Re-attached as
    // WPainter.Image at the bottom of the WPainter binding for the
    // natural nested-class form.

    auto image_cls = nb::class_<Wt::WPainter::Image>(m, "PainterImage",
        "Value type describing an image that a WPainter can draw. Holds\n"
        "the URL the browser will fetch and the intrinsic pixel size\n"
        "needed for layout. Pass an instance to `WPainter.draw_image`;\n"
        "also re-exported on the WPainter class as `WPainter.Image` for\n"
        "the natural nested-class form.")
        .def(nb::init<const std::string&, int, int>(),
             "url"_a, "width"_a, "height"_a,
             "Reference an external image at `url` with explicit pixel "
             "dimensions.")
        .def(nb::init<const std::string&, const std::string&>(),
             "url"_a, "file"_a,
             "Reference an image whose pixel dimensions Wt should read "
             "from local file `file` (the URL is what the browser uses; "
             "the file is where Wt looks for size metadata).")
        .def_prop_ro("uri", &Wt::WPainter::Image::uri,
             "The URL the browser will load to render this image.")
        .def_prop_ro("width", &Wt::WPainter::Image::width,
             "Intrinsic image width in pixels.")
        .def_prop_ro("height", &Wt::WPainter::Image::height,
             "Intrinsic image height in pixels.");

    // ---- WPainter ----
    //
    // The verb interface. Method names match Wt's C++ surface in
    // snake_case. drawText forms take a WRectF and an AlignmentFlag-int
    // bitmask (e.g. AlignmentFlag.Center | AlignmentFlag.Middle).

    auto painter_cls = nb::class_<Wt::WPainter>(m, "WPainter",
        "2-D drawing context. Receives geometric draw commands and turns\n"
        "them into output on a paint device — an HTML canvas, an SVG\n"
        "document, a PDF page, etc. Modelled on the same verb surface as\n"
        "Cairo or HTML5 Canvas: configure pen / brush / font, then call\n"
        "draw_* methods.\n"
        "\n"
        "    pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))\n"
        "    painter = wt.WPainter(pdf)\n"
        "    painter.set_pen(wt.WPen(wt.WColor('black')))\n"
        "    painter.draw_line(0, 0, 100, 100)\n"
        "    painter.draw_text(10, 10, 200, 30, wt.AlignmentFlag.Left,\n"
        "                      'Report')\n"
        "    app.add_resource(pdf, '/report.pdf')\n"
        "\n"
        "Inside a WPaintedWidget's paint callback the painter is handed\n"
        "to you already bound to the right device — don't construct one.\n"
        "The painter does NOT own its device; keep the device alive for\n"
        "the painter's lifetime. Drop the painter (or let it go out of\n"
        "scope) to flush any pending output to the device.")
        // No public default constructor exposed — Python users receive
        // a WPainter from the WPaintedWidget callback. We expose the
        // device-taking constructor for direct off-screen use.
        .def(nb::init<Wt::WPaintDevice*>(), "device"_a,
            "Construct a painter bound to a paint device. The device is "
            "not owned; the painter borrows it for its lifetime.")
        // Fallback overload for WResource-derived paint devices
        // (WPdfImage, WSvgImage). These inherit BOTH WResource and
        // WPaintDevice in C++, but nanobind's `class_<T, Base>` only
        // accepts a single base, so we bind them as WResource subclasses
        // for the resource-mounting path (`app.add_resource(pdf, ...)`).
        // The C++ object IS still a WPaintDevice; we recover that view
        // via dynamic_cast and construct the painter directly.
        .def("__init__",
             [](Wt::WPainter* self, Wt::WResource* res) {
                 auto* dev = dynamic_cast<Wt::WPaintDevice*>(res);
                 if (!dev) {
                     throw nb::type_error(
                         "device must be a WPaintDevice or a WResource "
                         "that also implements WPaintDevice (e.g. "
                         "WPdfImage, WSvgImage)");
                 }
                 new (self) Wt::WPainter(dev);
             },
             "device"_a,
             "Construct from a WResource that also implements "
             "WPaintDevice (WPdfImage / WSvgImage). Equivalent to "
             "passing the WPaintDevice view of the same object.")
        // ---- state ----
        .def("save", &Wt::WPainter::save,
             "Push the current state (pen, brush, font, transform, "
             "clipping) onto an internal stack. Pair with restore().")
        .def("restore", &Wt::WPainter::restore,
             "Pop the most recently saved state, undoing any pen / brush /"
             " font / transform / clipping changes made since the matching"
             " save().")
        .def("set_pen", &Wt::WPainter::setPen, "pen"_a,
             "Set the stroke style for subsequent line / outline draws.")
        .def("set_brush", &Wt::WPainter::setBrush, "brush"_a,
             "Set the fill style for subsequent filled-shape draws.")
        .def("set_font", &Wt::WPainter::setFont, "font"_a,
             "Set the font used by draw_text.")
        .def("set_shadow", &Wt::WPainter::setShadow, "shadow"_a,
             "Apply a drop-shadow effect to subsequent draw operations. "
             "Pass `wt.WShadow()` to clear.")
        .def_prop_ro("pen", &Wt::WPainter::pen,
                     nb::rv_policy::reference_internal,
                     "The current pen — what strokes use.")
        .def_prop_ro("brush", &Wt::WPainter::brush,
                     nb::rv_policy::reference_internal,
                     "The current brush — what fills use.")
        // ---- transform ----
        .def("set_world_transform",
             nb::overload_cast<const Wt::WTransform&, bool>(
                 &Wt::WPainter::setWorldTransform),
             "transform"_a, "combine"_a = false,
             "Replace the painter's current transform with `transform`. "
             "Pass combine=True to multiply onto the existing transform "
             "instead of replacing it.")
        .def("translate",
             nb::overload_cast<double, double>(&Wt::WPainter::translate),
             "dx"_a, "dy"_a,
             "Shift the origin of subsequent draws by (dx, dy).")
        .def("rotate", &Wt::WPainter::rotate, "angle"_a,
             "Rotate by `angle` degrees about the origin of the local "
             "coordinate system.")
        .def("scale", &Wt::WPainter::scale, "sx"_a, "sy"_a,
             "Scale subsequent draws by sx in X and sy in Y. Pass "
             "sx=sy=-1 to flip about the origin.")
        // ---- clipping ----
        .def("set_clipping", &Wt::WPainter::setClipping, "enabled"_a,
             "Enable or disable the active clip path. Use set_clip_path "
             "first to define the clip region.")
        .def("set_clip_path", &Wt::WPainter::setClipPath, "path"_a,
             "Restrict subsequent draws to the area inside `path` (a "
             "WPainterPath). Does not enable clipping by itself — call "
             "set_clipping(True) too.")
        // ---- draw primitives (numeric, value-type-free) ----
        .def("draw_line",
             nb::overload_cast<double, double, double, double>(
                 &Wt::WPainter::drawLine),
             "x1"_a, "y1"_a, "x2"_a, "y2"_a,
             "Stroke a straight line from (x1, y1) to (x2, y2) using the "
             "current pen.")
        .def("draw_rect",
             nb::overload_cast<double, double, double, double>(
                 &Wt::WPainter::drawRect),
             "x"_a, "y"_a, "width"_a, "height"_a,
             "Stroke and fill an axis-aligned rectangle with the current "
             "pen and brush.")
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
             "start_angle"_a, "span_angle"_a,
             "Pie slice — arc closed back to the centre. Angles in "
             "1/16-degree units like draw_arc.")
        .def("draw_chord",
             nb::overload_cast<double, double, double, double, int, int>(
                 &Wt::WPainter::drawChord),
             "x"_a, "y"_a, "width"_a, "height"_a,
             "start_angle"_a, "span_angle"_a,
             "Chord — arc closed by a straight line between its endpoints"
             " (not the centre). Angles in 1/16-degree units.")
        .def("draw_point",
             nb::overload_cast<double, double>(&Wt::WPainter::drawPoint),
             "x"_a, "y"_a,
             "Draw a single point at (x, y) with the current pen.")
        .def("draw_path", &Wt::WPainter::drawPath, "path"_a,
             "Stroke and fill a WPainterPath using the current pen and "
             "brush.")
        .def("draw_lines",
             nb::overload_cast<const std::vector<Wt::WLineF>&>(
                 &Wt::WPainter::drawLines),
             "lines"_a,
             "Stroke each WLineF in `lines` with the current pen — one "
             "round-trip into the device, cheaper than many draw_line "
             "calls.")
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
        // ---- images ----
        .def("draw_image",
            nb::overload_cast<const Wt::WPointF&, const Wt::WPainter::Image&>(
                &Wt::WPainter::drawImage),
            "point"_a, "image"_a,
            "Draw the image at its intrinsic size with top-left at point.")
        .def("draw_image",
            nb::overload_cast<const Wt::WPointF&, const Wt::WPainter::Image&,
                              const Wt::WRectF&>(
                &Wt::WPainter::drawImage),
            "point"_a, "image"_a, "source_rect"_a,
            "Draw a sub-region of the image at its intrinsic size. "
            "source_rect is in the image's pixel coordinates.")
        .def("draw_image",
            nb::overload_cast<const Wt::WRectF&, const Wt::WPainter::Image&>(
                &Wt::WPainter::drawImage),
            "dest_rect"_a, "image"_a,
            "Stretch / shrink the image to fill dest_rect.")
        .def("draw_image",
            nb::overload_cast<const Wt::WRectF&, const Wt::WPainter::Image&,
                              const Wt::WRectF&>(
                &Wt::WPainter::drawImage),
            "dest_rect"_a, "image"_a, "source_rect"_a,
            "Stretch a sub-region of the image into dest_rect.")
        // ---- device / state ----
        .def_prop_ro("is_active", &Wt::WPainter::isActive,
             "True if the painter is currently bound to a device and can "
             "accept draw calls.");

    // Re-attach the Image nested class for the natural form.
    painter_cls.attr("Image") = image_cls;

    // ---- WPaintedWidget (callback shim) ----
    //
    // Bound as the C++ trampoline subclass PyPaintedWidget. Python users
    // see it as `wt.WPaintedWidget`. Override the paint behaviour by
    // passing a callable at construction (or via set_paint_callback).
    // Wt's paintEvent fires from a worker thread; the trampoline
    // acquires the GIL before calling Python.

    nb::class_<PyPaintedWidget, Wt::WInteractWidget>(m, "WPaintedWidget",
        "A widget whose contents are produced by Python code running\n"
        "against a WPainter. Pass a callable at construction; it will be\n"
        "invoked each time the widget needs to repaint, with a freshly-\n"
        "bound WPainter as its only argument.\n"
        "\n"
        "    def paint(p):\n"
        "        p.set_pen(wt.WPen(wt.WColor('navy')))\n"
        "        p.draw_line(0, 0, 200, 100)\n"
        "        p.draw_ellipse(20, 20, 60, 60)\n"
        "    container.add_widget(wt.WPaintedWidget(paint))\n"
        "\n"
        "Call `update()` to request a repaint after model changes. The\n"
        "WPainter handed to the callback is a non-owning view of a\n"
        "stack-allocated object — don't stash it beyond the callback's\n"
        "return. The paint callback may run on a worker thread; the\n"
        "binding acquires the GIL before calling into Python.")
        .def(nb::new_([]() {
            return std::make_unique<PyPaintedWidget>();
        }),
            "Construct an empty painted widget with no paint callback. "
            "Set one later via `set_paint_callback` before calling "
            "`update()`.")
        .def(nb::new_([](nb::callable paint) {
            auto w = std::make_unique<PyPaintedWidget>();
            w->setPaintCallback(std::move(paint));
            return w;
        }), "paint"_a,
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
            &Wt::WPaintedWidget::preferredMethod,
            "The currently selected render backend (RenderMethod enum).")
        .def("add_area",
            [](PyPaintedWidget& self, nb::object py_area) -> nb::object {
                auto a = nb::cast<std::unique_ptr<Wt::WAbstractArea>>(py_area);
                self.addArea(std::move(a));
                nb::inst_set_state(py_area, /*ready*/ true,
                                   /*destruct*/ false);
                return py_area;
            },
            "area"_a,
            "Attach an image-map area (WRectArea / WCircleArea / "
            "WPolygonArea) that becomes a clickable region on top of "
            "the painted output.")
        .def("insert_area",
            [](PyPaintedWidget& self, int index, nb::object py_area)
                -> nb::object {
                auto a = nb::cast<std::unique_ptr<Wt::WAbstractArea>>(py_area);
                self.insertArea(index, std::move(a));
                nb::inst_set_state(py_area, /*ready*/ true,
                                   /*destruct*/ false);
                return py_area;
            },
            "index"_a, "area"_a,
            "Insert an image-map area at position `index`. Earlier areas "
            "in the list receive clicks first when regions overlap.");

    // ---- RenderMethod (used by setPreferredMethod) ----

    nb::enum_<Wt::RenderMethod>(m, "RenderMethod",
        "Backend a WPaintedWidget uses to render. HtmlCanvas is the "
        "default; InlineSvgVml emits inline SVG (legacy IE: VML); PngImage "
        "rasterises server-side and serves a PNG.")
        .value("InlineSvgVml", Wt::RenderMethod::InlineSvgVml)
        .value("HtmlCanvas",   Wt::RenderMethod::HtmlCanvas)
        .value("PngImage",     Wt::RenderMethod::PngImage);

    // ---- Image-map areas ----
    //
    // WAbstractArea is the base for clickable regions overlaid on a
    // WPaintedWidget (or WImage). Each area can carry a WLink, alternate
    // text, and a tooltip — the area renders as an HTML <area> element
    // inside a <map>.

    nb::class_<Wt::WAbstractArea, Wt::WObject>(m, "WAbstractArea",
        "Base class for clickable regions in an image map. Concrete\n"
        "subclasses define the region's shape: WRectArea, WCircleArea,\n"
        "WPolygonArea. Attach one to a WPaintedWidget or WImage via\n"
        "`add_area` to make part of the rendered output respond to clicks.")
        .def("set_link", &Wt::WAbstractArea::setLink, "link"_a,
             "Navigate to `link` when the area is clicked (WLink — URL, "
             "internal path, or WResource).")
        .def("set_alternate_text", &Wt::WAbstractArea::setAlternateText,
             "text"_a,
             "Text used by screen readers and shown when the underlying "
             "image fails to load.")
        .def("set_tool_tip", &Wt::WAbstractArea::setToolTip, "text"_a,
             "Hover-tooltip text shown while the cursor is over this area.")
        .def("set_style_class",
            // Disambiguate the WT_USTRING form from the `const char*` form.
            [](Wt::WAbstractArea& self, const Wt::WString& style_class) {
                self.setStyleClass(style_class);
            },
            "style_class"_a,
            "CSS class for the underlying `<area>` element.")
        .def_prop_rw("hole",
            &Wt::WAbstractArea::isHole,
            &Wt::WAbstractArea::setHole,
            "When True, this area is treated as a hole (transparent to "
            "clicks) cut out of the surrounding map.")
        .def_prop_rw("transformable",
            &Wt::WAbstractArea::isTransformable,
            &Wt::WAbstractArea::setTransformable,
            "When True, the area's coordinates are interpreted in the "
            "painter's local coordinate system and follow any transforms "
            "applied to the widget. When False, coordinates stay fixed "
            "in widget pixels.");

    nb::class_<Wt::WCircleArea, Wt::WAbstractArea>(m, "WCircleArea",
        "Circular clickable region for an image map. Coordinates are in "
        "the widget's pixel space (or local coordinates if "
        "`transformable` is True).")
        .def(heap_init<Wt::WCircleArea>(),
             "Construct an empty circle area — set centre and radius "
             "afterwards.")
        .def(heap_init<Wt::WCircleArea, int, int, int>(),
             "x"_a, "y"_a, "radius"_a,
             "Construct a circle centred at (x, y) with the given radius.")
        .def("set_center",
            nb::overload_cast<int, int>(&Wt::WCircleArea::setCenter),
            "x"_a, "y"_a,
            "Move the circle's centre to (x, y).")
        .def_prop_ro("center_x", &Wt::WCircleArea::centerX,
            "X coordinate of the circle's centre.")
        .def_prop_ro("center_y", &Wt::WCircleArea::centerY,
            "Y coordinate of the circle's centre.")
        .def_prop_rw("radius",
            &Wt::WCircleArea::radius,
            &Wt::WCircleArea::setRadius,
            "Circle radius in pixels (or local coordinate units).");

    nb::class_<Wt::WRectArea, Wt::WAbstractArea>(m, "WRectArea",
        "Rectangular clickable region for an image map.")
        .def(heap_init<Wt::WRectArea>(),
             "Construct a degenerate (zero-size) rectangle. Set bounds "
             "afterwards by reconstructing.")
        .def(heap_init<Wt::WRectArea, int, int, int, int>(),
             "x"_a, "y"_a, "width"_a, "height"_a,
             "Construct an axis-aligned rectangle with top-left at "
             "(x, y).")
        .def(heap_init<Wt::WRectArea, const Wt::WRectF&>(), "rect"_a,
             "Construct from an existing WRectF.");

    nb::class_<Wt::WPolygonArea, Wt::WAbstractArea>(m, "WPolygonArea",
        "Polygon-shaped clickable region. Build by passing a list of "
        "vertices, or extend a polygon incrementally via `add_point`.")
        .def(heap_init<Wt::WPolygonArea>(),
             "Construct an empty polygon area — add vertices afterwards.")
        .def(heap_init<Wt::WPolygonArea,
                       const std::vector<Wt::WPointF>&>(), "points"_a,
             "Construct from a sequence of WPointF vertices.")
        .def("add_point",
            nb::overload_cast<double, double>(&Wt::WPolygonArea::addPoint),
            "x"_a, "y"_a,
            "Append a vertex at (x, y) to the polygon.")
        .def("set_points",
            nb::overload_cast<const std::vector<Wt::WPointF>&>(
                &Wt::WPolygonArea::setPoints),
            "points"_a,
            "Replace the polygon's vertices with `points`.");
}

}  // namespace witty_for_python
