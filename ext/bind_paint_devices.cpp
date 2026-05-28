#include "common.hpp"

#include <Wt/WCanvasPaintDevice.h>
#include <Wt/WMeasurePaintDevice.h>
#include <Wt/WPaintDevice.h>
#include <Wt/WPainter.h>
#include <Wt/WPdfImage.h>
#include <Wt/WRectF.h>
#include <Wt/WSvgImage.h>
#include <Wt/WVectorImage.h>

#include <string>

namespace witty_for_python {

void register_paint_devices(nb::module_& m) {
    // WPainter::Image + drawImage live in bind_painting.cpp — they need
    // to be added to the WPainter binding in the same translation unit
    // that initially registered it (re-opening would trigger nanobind's
    // "type already registered" warning, which the project convention
    // avoids).

    // ---- WPaintDevice (abstract base) ----
    //
    // Bound non-constructible. Concrete devices (WCanvasPaintDevice,
    // WSvgImage, WMeasurePaintDevice) are what callers actually use.
    // The base interface is exposed so a WPainter binding can accept
    // any device as parameter; from Python you rarely call WPaintDevice
    // methods directly.

    nb::enum_<Wt::PaintDeviceFeatureFlag>(m, "PaintDeviceFeatureFlag",
                                          nb::is_arithmetic())
        .value("HasFontMetrics", Wt::PaintDeviceFeatureFlag::FontMetrics)
        .value("CanWordWrap",    Wt::PaintDeviceFeatureFlag::WordWrap);

    nb::class_<Wt::WPaintDevice>(m, "WPaintDevice")
        .def_prop_ro("width",  &Wt::WPaintDevice::width)
        .def_prop_ro("height", &Wt::WPaintDevice::height);

    // ---- WVectorImage (intermediate) ----
    //
    // Common base for WSvgImage and (deferred) WVmlImage. Adds no
    // accessible methods beyond WPaintDevice; exposed so users can
    // type-check via isinstance.

    nb::class_<Wt::WVectorImage, Wt::WPaintDevice>(m, "WVectorImage");

    // ---- WSvgImage ----
    //
    // Renders to an SVG string. Inherits both WResource (so it can be
    // mounted on a URL and served to clients) and WVectorImage (so it's
    // a WPaintDevice). Bound as a WResource subclass — that's the
    // path Python users will primarily touch (mount via WAnchor /
    // WImage / WApplication.add_resource).
    //
    // Construction requires width + height; the actual painting happens
    // inside a WPainter constructed against the WSvgImage as device.

    nb::class_<Wt::WSvgImage, Wt::WResource>(m, "WSvgImage")
        .def(nb::init<const Wt::WLength&, const Wt::WLength&>(),
             "width"_a, "height"_a,
             "Create an SVG paint surface of the given size. Construct a "
             "WPainter against it, paint, then mount the WSvgImage on a "
             "URL — clients fetch the SVG text.");

    // ---- WCanvasPaintDevice ----
    //
    // The device used internally by WPaintedWidget when render method is
    // HtmlCanvas. Rarely constructed directly by users; exposed for
    // off-screen rendering use cases (capture a canvas to a string).

    nb::class_<Wt::WCanvasPaintDevice, Wt::WPaintDevice>(m, "WCanvasPaintDevice")
        .def(nb::init<const Wt::WLength&, const Wt::WLength&>(),
             "width"_a, "height"_a);

    // ---- WMeasurePaintDevice ----
    //
    // A pass-through device that records the bounding rect of everything
    // painted into it without actually rendering. Useful for computing
    // the size needed to fit a painter's output before allocating a
    // real device.

    nb::class_<Wt::WMeasurePaintDevice, Wt::WPaintDevice>(m, "WMeasurePaintDevice")
        .def(nb::init<Wt::WPaintDevice*>(), "delegate"_a,
             "Construct over an underlying device — `delegate` is consulted "
             "for font metrics but no rendering reaches it.")
        .def_prop_ro("bounding_rect", &Wt::WMeasurePaintDevice::boundingRect,
            "Union of every WRectF that's been painted into the measure "
            "device so far.");

    // ---- WPdfImage ----
    //
    // Renders to a PDF document via libharu (zlib-licensed). Inherits
    // both WResource (mount on a URL and serve to clients) and
    // WPaintDevice. Bound as a WResource child — that's the Python-
    // facing path.
    //
    // Typical flow:
    //   pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))  # A4
    //   painter = wt.WPainter(pdf)
    //   painter.draw_rect(...)
    //   del painter  # flush
    //   app.add_resource(pdf, "/report.pdf")

    nb::class_<Wt::WPdfImage, Wt::WResource>(m, "WPdfImage")
        .def(nb::init<const Wt::WLength&, const Wt::WLength&>(),
             "width"_a, "height"_a,
             "Create a PDF paint surface with the given page dimensions "
             "(typically in WLength.Point units — A4 portrait is roughly "
             "595×842 pt).")
        .def("add_font_collection",
             &Wt::WPdfImage::addFontCollection,
             "directory"_a, "recursive"_a = true,
             "Search `directory` for TrueType / Type1 fonts and make them "
             "available to drawText. Pair with WFont.set_family(..., "
             "specific='Some Font') to reference one. Without registered "
             "fonts the PDF uses libharu's built-in 14 base fonts only.");
        // setDeviceTransform is gated by `#ifdef WT_TARGET_JAVA` in Wt's
        // header — not available to C++ callers in 4.13.x.

    // ---- NOT BOUND ----
    //
    //   WRasterImage — needs GD-image / similar raster library. Wt's
    //                  build toggle for this isn't on by default in our
    //                  configuration. To enable, add libgd-dev (or
    //                  equivalent) and flip the Wt CMake option. See
    //                  docs/deferred.md.
}

}  // namespace witty_for_python
