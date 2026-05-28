"""Paint devices + WPainter::Image + drawImage.

PainterImage is a pure value type (no session needed) so we exercise it
fully. The paint devices (WSvgImage, WCanvasPaintDevice,
WMeasurePaintDevice) construct value-typed too, but WSvgImage and
WCanvasPaintDevice touch Wt's resource registry internally; we only
verify the binding surface and inheritance.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- PainterImage ---------------------------------------------------------

def test_painter_image_url_w_h() -> None:
    img = wt.PainterImage("http://example.com/x.png", 200, 100)
    assert img.uri == "http://example.com/x.png"
    assert img.width == 200
    assert img.height == 100


def test_painter_image_url_file_signature_exists() -> None:
    """The (url, file) constructor exists; we don't exercise it with a
    real image file from the tests directory because Wt's image-size
    parser is strict and would need a real PNG/JPG fixture. Surface-
    check only."""
    import inspect
    # nb-bound methods don't expose useful inspect.signature info, so we
    # confirm via the docstring instead.
    doc = wt.PainterImage.__init__.__doc__ or ""
    assert "file" in doc


def test_painter_image_attached_to_wpainter() -> None:
    """WPainter.Image is the natural nested form — same class as the
    module-level PainterImage alias."""
    assert wt.WPainter.Image is wt.PainterImage


# ---- WPainter.draw_image overloads exist --------------------------------

def test_wpainter_has_draw_image() -> None:
    """Five overloads — point/rect destination ± source_rect. From
    Python they're all on the same attribute."""
    assert hasattr(wt.WPainter, "draw_image")


# ---- Paint device inheritance -------------------------------------------

def test_wpaintdevice_is_abstract() -> None:
    """The base is bound non-constructible."""
    with pytest.raises(TypeError):
        wt.WPaintDevice()


@pytest.mark.parametrize("cls,base", [
    (wt.WVectorImage,        wt.WPaintDevice),
    (wt.WSvgImage,           wt.WResource),         # SVG is also a WResource
    (wt.WPdfImage,           wt.WResource),         # so is PDF
    (wt.WCanvasPaintDevice,  wt.WPaintDevice),
    (wt.WMeasurePaintDevice, wt.WPaintDevice),
])
def test_paint_device_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base)


# ---- WSvgImage (constructible standalone) ------------------------------

def test_wsvgimage_construct() -> None:
    svg = wt.WSvgImage(wt.WLength(400), wt.WLength(300))
    assert svg is not None


# ---- WPdfImage (constructible standalone — libharu-backed) -------------

def test_wpdfimage_construct() -> None:
    """A4 portrait in PDF points (1/72 inch): 595 × 842."""
    pdf = wt.WPdfImage(
        wt.WLength(595, wt.LengthUnit.Point),
        wt.WLength(842, wt.LengthUnit.Point))
    assert pdf is not None


def test_wpdfimage_add_font_collection_method() -> None:
    """The method exists; we don't pass a real font directory because
    Wt scans it eagerly. Surface check only."""
    pdf = wt.WPdfImage(wt.WLength(100), wt.WLength(100))
    assert hasattr(pdf, "add_font_collection")


# ---- WCanvasPaintDevice -------------------------------------------------

def test_wcanvas_paint_device_class_exists() -> None:
    """WCanvasPaintDevice's constructor touches Wt's session state —
    it segfaults without an active WApplication. Class binding is
    verified; end-to-end use happens through WPaintedWidget which
    constructs its own canvas device internally."""
    assert wt.WCanvasPaintDevice is not None
    assert issubclass(wt.WCanvasPaintDevice, wt.WPaintDevice)


# ---- WMeasurePaintDevice ------------------------------------------------

def test_wmeasure_paint_device_class_exists() -> None:
    """Same caveat as WCanvasPaintDevice — needs a session to construct
    the delegate device. Class-surface check only."""
    assert wt.WMeasurePaintDevice is not None
    assert hasattr(wt.WMeasurePaintDevice, "bounding_rect")


# ---- PaintDeviceFeatureFlag enum ----------------------------------------

def test_paint_device_feature_flag_members() -> None:
    assert hasattr(wt.PaintDeviceFeatureFlag, "HasFontMetrics")
    assert hasattr(wt.PaintDeviceFeatureFlag, "CanWordWrap")
