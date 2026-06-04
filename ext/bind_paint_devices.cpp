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
                                          nb::is_arithmetic(),
        "Capability bits a paint device can advertise. Combined with "
        "OR into a bitmask. HasFontMetrics means the device can measure "
        "text without rendering it; CanWordWrap means it knows how to "
        "break long strings on word boundaries.")
        .value("HasFontMetrics", Wt::PaintDeviceFeatureFlag::FontMetrics)
        .value("CanWordWrap",    Wt::PaintDeviceFeatureFlag::WordWrap);

    nb::class_<Wt::WPaintDevice>(m, "WPaintDevice",
        "Abstract base for everything a WPainter can draw into — an\n"
        "HTML canvas, an SVG document, a PDF page, an off-screen\n"
        "measurement device. Cannot be constructed directly; pick a\n"
        "concrete subclass.\n"
        "\n"
        "    pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))\n"
        "    painter = wt.WPainter(pdf)\n"
        "    painter.draw_text(...)\n"
        "    app.add_resource(pdf, '/page.pdf')\n"
        "\n"
        "WResource-based devices (WSvgImage, WPdfImage) are typically\n"
        "served to the browser by mounting on a URL; off-screen devices\n"
        "(WMeasurePaintDevice, WCanvasPaintDevice) are used for sizing\n"
        "or capture.")
        .def_prop_ro("width",  &Wt::WPaintDevice::width,
             "Device width as a WLength.")
        .def_prop_ro("height", &Wt::WPaintDevice::height,
             "Device height as a WLength.");

    // ---- WVectorImage (intermediate) ----
    //
    // Common base for WSvgImage and (deferred) WVmlImage. Adds no
    // accessible methods beyond WPaintDevice; exposed so users can
    // type-check via isinstance.

    nb::class_<Wt::WVectorImage, Wt::WPaintDevice>(m, "WVectorImage",
        "Base class for vector-graphics paint devices (WSvgImage today; "
        "a future VML implementation). Exposes no methods of its own — "
        "exists so callers can `isinstance(dev, wt.WVectorImage)` to "
        "test for the vector family.");

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

    nb::class_<Wt::WSvgImage, Wt::WResource>(m, "WSvgImage",
        "SVG paint device backed by a WResource. Paint into it with a\n"
        "WPainter, then mount the device on a URL via\n"
        "`WApplication.add_resource` to serve the resulting SVG document\n"
        "to clients (typically as the source of a WImage or a\n"
        "`<link rel=icon>`).\n"
        "\n"
        "    svg = wt.WSvgImage(wt.WLength(200), wt.WLength(100))\n"
        "    p = wt.WPainter(svg)\n"
        "    p.draw_ellipse(20, 20, 60, 60)\n"
        "    del p  # flush\n"
        "    app.add_resource(svg, '/badge.svg')\n"
        "    container.add_widget(wt.WImage(wt.WLink('/badge.svg'), 'badge'))\n"
        "\n"
        "Because WSvgImage is a WResource the same instance can be\n"
        "served to many clients.")
        .def(heap_init<Wt::WSvgImage, const Wt::WLength&, const Wt::WLength&>(),
             "width"_a, "height"_a,
             "Create an SVG paint surface of the given size. Construct a "
             "WPainter against it, paint, then mount the WSvgImage on a "
             "URL — clients fetch the SVG text.");

    // ---- WCanvasPaintDevice ----
    //
    // The device used internally by WPaintedWidget when render method is
    // HtmlCanvas. Rarely constructed directly by users; exposed for
    // off-screen rendering use cases (capture a canvas to a string).

    nb::class_<Wt::WCanvasPaintDevice, Wt::WPaintDevice>(m, "WCanvasPaintDevice",
        "HTML5-canvas paint device. The same backend a WPaintedWidget "
        "uses when its render method is HtmlCanvas. Construct one "
        "directly only for off-screen / capture scenarios; for normal "
        "drawing into the page, use WPaintedWidget.")
        .def(heap_init<Wt::WCanvasPaintDevice, const Wt::WLength&, const Wt::WLength&>(),
             "width"_a, "height"_a,
             "Create a canvas paint surface of the given size.");

    // ---- WMeasurePaintDevice ----
    //
    // A pass-through device that records the bounding rect of everything
    // painted into it without actually rendering. Useful for computing
    // the size needed to fit a painter's output before allocating a
    // real device.

    nb::class_<Wt::WMeasurePaintDevice, Wt::WPaintDevice>(m, "WMeasurePaintDevice",
        "Pass-through paint device that records the bounding rect of\n"
        "every draw operation without actually rendering. Useful for\n"
        "sizing an output canvas before allocating the real device.\n"
        "\n"
        "    measure = wt.WMeasurePaintDevice(reference_device)\n"
        "    p = wt.WPainter(measure)\n"
        "    render(p)               # whatever paint code\n"
        "    rect = measure.bounding_rect")
        .def(heap_init<Wt::WMeasurePaintDevice, Wt::WPaintDevice*>(), "delegate"_a,
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

    nb::class_<Wt::WPdfImage, Wt::WResource>(m, "WPdfImage",
        "PDF paint device backed by a WResource. Paint into it with a\n"
        "WPainter, then mount it on a URL so clients can download or\n"
        "view the resulting PDF.\n"
        "\n"
        "    pdf = wt.WPdfImage(wt.WLength(595), wt.WLength(842))  # A4\n"
        "    p = wt.WPainter(pdf)\n"
        "    p.draw_text(36, 36, 523, 30, wt.AlignmentFlag.Left, 'Report')\n"
        "    p.draw_rect(36, 80, 523, 200)\n"
        "    del p  # flush\n"
        "    app.add_resource(pdf, '/report.pdf')\n"
        "\n"
        "Rendered by libharu. Only the 14 PDF base fonts are available\n"
        "by default — call `add_font_collection` first if you need a\n"
        "specific TrueType/Type1 font.")
        .def(heap_init<Wt::WPdfImage, const Wt::WLength&, const Wt::WLength&>(),
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
