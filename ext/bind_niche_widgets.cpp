#include "common.hpp"

#include <Wt/WBrush.h>
#include <Wt/WGoogleMap.h>
#include <Wt/WPen.h>
#include <Wt/WQrCode.h>

#include <string>
#include <vector>

namespace witty_for_python {

void register_niche_widgets(nb::module_& m) {
    // ---- WQrCode ----
    //
    // Renders a QR code as a painted widget. Inherits WPaintedWidget in
    // C++ but, like the charts, we bind it as inheriting WInteractWidget
    // directly to avoid the PyPaintedWidget Python-type mismatch. The
    // built-in paintEvent handles all rendering — users just set the
    // message + style.

    nb::enum_<Wt::WQrCode::ErrorCorrectionLevel>(m, "ErrorCorrectionLevel")
        .value("Low",      Wt::WQrCode::ErrorCorrectionLevel::LOW)
        .value("Medium",   Wt::WQrCode::ErrorCorrectionLevel::MEDIUM)
        .value("Quartile", Wt::WQrCode::ErrorCorrectionLevel::QUARTILE)
        .value("High",     Wt::WQrCode::ErrorCorrectionLevel::HIGH);

    nb::class_<Wt::WQrCode, Wt::WInteractWidget>(m, "WQrCode")
        .def(nb::init<>())
        .def(nb::init<const std::string&, double>(),
             "message"_a, "square_size"_a)
        .def(nb::init<const std::string&,
                      Wt::WQrCode::ErrorCorrectionLevel, double>(),
             "message"_a, "ecl"_a, "square_size"_a,
             "Construct with text, error-correction level, and the size "
             "in pixels of each QR-code square.")
        .def_prop_rw("message",
            &Wt::WQrCode::message,
            &Wt::WQrCode::setMessage,
            "The text encoded. Mutating triggers a re-paint.")
        .def_prop_rw("square_size",
            &Wt::WQrCode::squareSize,
            &Wt::WQrCode::setSquareSize)
        .def("set_error_correction_level",
             &Wt::WQrCode::setErrorCorrectionLevel, "ecl"_a)
        .def_prop_rw("brush",
            &Wt::WQrCode::brush,
            &Wt::WQrCode::setBrush,
            "Brush used to paint the QR squares (default black solid). "
            "Tint with a colored brush; the background stays transparent.")
        .def_prop_ro("error", &Wt::WQrCode::error,
             "True if the encoder couldn't fit the message at the "
             "configured ECL — try Low or shorten the message.")
        .def("update",
            [](Wt::WQrCode& self) { self.update(); });

    // ---- WGoogleMap ----
    //
    // Embeds Google Maps. Requires a `google_api_key` config property
    // set at server startup (in Wt's config XML), so the widget renders
    // an empty/error pane until that's in place.

    nb::enum_<Wt::GoogleMapsVersion>(m, "GoogleMapsVersion")
        .value("v3", Wt::GoogleMapsVersion::v3);

    nb::enum_<Wt::MapTypeControl>(m, "MapTypeControl")
        .value("None_",         Wt::MapTypeControl::None)
        .value("Default",       Wt::MapTypeControl::Default)
        .value("Menu",          Wt::MapTypeControl::Menu)
        .value("Hierarchical",  Wt::MapTypeControl::Hierarchical)
        .value("HorizontalBar", Wt::MapTypeControl::HorizontalBar);

    auto coord_cls = nb::class_<Wt::WGoogleMap::Coordinate>(
        m, "GoogleMapCoordinate")
        .def(nb::init<>())
        .def(nb::init<double, double>(), "latitude"_a, "longitude"_a)
        .def_prop_rw("latitude",
            &Wt::WGoogleMap::Coordinate::latitude,
            &Wt::WGoogleMap::Coordinate::setLatitude)
        .def_prop_rw("longitude",
            &Wt::WGoogleMap::Coordinate::longitude,
            &Wt::WGoogleMap::Coordinate::setLongitude)
        .def("distance_to", &Wt::WGoogleMap::Coordinate::distanceTo,
             "other"_a,
             "Great-circle distance to `other` in kilometres "
             "(despite Wt's docs naming metres).")
        .def("__repr__",
            [](const Wt::WGoogleMap::Coordinate& c) {
                return "GoogleMapCoordinate(lat=" + std::to_string(c.latitude())
                     + ", lon=" + std::to_string(c.longitude()) + ")";
            });

    auto gmap_cls = nb::class_<Wt::WGoogleMap, Wt::WWidget>(m, "WGoogleMap")
        // No default value for the version arg — nanobind has trouble
        // casting value-typed defaults (WColor() etc.) at module init.
        .def(nb::init<Wt::GoogleMapsVersion>(), "version"_a)
        .def("set_center",
            nb::overload_cast<const Wt::WGoogleMap::Coordinate&>(
                &Wt::WGoogleMap::setCenter),
            "center"_a)
        .def("set_center",
            nb::overload_cast<const Wt::WGoogleMap::Coordinate&, int>(
                &Wt::WGoogleMap::setCenter),
            "center"_a, "zoom"_a,
            "Pan to `center` and set the zoom level in one call.")
        .def("pan_to", &Wt::WGoogleMap::panTo, "center"_a)
        .def("set_zoom", &Wt::WGoogleMap::setZoom, "level"_a)
        .def("zoom_in",  &Wt::WGoogleMap::zoomIn)
        .def("zoom_out", &Wt::WGoogleMap::zoomOut)
        .def("save_position", &Wt::WGoogleMap::savePosition,
             "Remember the current centre + zoom. Restore with "
             "return_to_saved_position.")
        .def("return_to_saved_position",
             &Wt::WGoogleMap::returnToSavedPosition)
        .def("add_marker", &Wt::WGoogleMap::addMarker, "position"_a)
        .def("add_icon_marker", &Wt::WGoogleMap::addIconMarker,
             "position"_a, "icon_url"_a,
             "Marker with a custom icon image at `icon_url`.")
        .def("add_polyline", &Wt::WGoogleMap::addPolyline,
             "points"_a, "color"_a, "width"_a, "opacity"_a,
             "All four arguments mandatory — pass wt.WColor(...) and "
             "your line width / opacity explicitly.")
        .def("add_circle", &Wt::WGoogleMap::addCircle,
             "center"_a, "radius_metres"_a,
             "stroke_color"_a, "stroke_width"_a, "fill_color"_a,
             "Circle of `radius_metres` (a real distance, not pixels) "
             "around `center`.")
        .def("clear_overlays", &Wt::WGoogleMap::clearOverlays,
             "Remove every marker, polyline, circle, etc. added so far.")
        .def("open_info_window", &Wt::WGoogleMap::openInfoWindow,
             "position"_a, "html"_a,
             "Show a Google-Maps info window with HTML content.")
        .def("zoom_window",
            nb::overload_cast<const Wt::WGoogleMap::Coordinate&,
                              const Wt::WGoogleMap::Coordinate&>(
                &Wt::WGoogleMap::zoomWindow),
            "top_left"_a, "bottom_right"_a,
            "Zoom to fit the bounding box (top_left, bottom_right).");

    // Re-attach the Coordinate value type as WGoogleMap.Coordinate.
    gmap_cls.attr("Coordinate") = coord_cls;
}

}  // namespace witty_for_python
