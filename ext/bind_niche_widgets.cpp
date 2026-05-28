#include "common.hpp"

#include <Wt/Json/Object.h>
#include <Wt/WBrush.h>
#include <Wt/WGoogleMap.h>
#include <Wt/WLeafletMap.h>
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

    // ---- WLeafletMap ----
    //
    // OpenStreetMap-backed map widget. Unlike WGoogleMap, no external
    // API key is required — the widget renders tiles fetched directly
    // from an OpenStreetMap (or compatible) tile server, configured
    // via add_tile_layer. Markers, popups, and tooltips are added via
    // add_marker / add_popup / add_tooltip, taking the corresponding
    // nested classes below.

    auto leaflet_coord_cls = nb::class_<Wt::WLeafletMap::Coordinate>(
        m, "LeafletMapCoordinate")
        .def(nb::init<>())
        .def(nb::init<double, double>(), "latitude"_a, "longitude"_a)
        .def_prop_rw("latitude",
            &Wt::WLeafletMap::Coordinate::latitude,
            &Wt::WLeafletMap::Coordinate::setLatitude)
        .def_prop_rw("longitude",
            &Wt::WLeafletMap::Coordinate::longitude,
            &Wt::WLeafletMap::Coordinate::setLongitude)
        .def("__repr__",
            [](const Wt::WLeafletMap::Coordinate& c) {
                return "LeafletMapCoordinate(lat=" + std::to_string(c.latitude())
                     + ", lon=" + std::to_string(c.longitude()) + ")";
            });

    // ---- WLeafletMap nested overlay hierarchy ----
    //
    // The hierarchy:
    //   AbstractMapItem (WObject)
    //     ├── AbstractOverlayItem
    //     │     ├── Popup
    //     │     └── Tooltip
    //     └── Marker
    //           ├── LeafletMarker
    //           └── WidgetMarker
    //
    // Each item is constructed standalone and handed to the map (or to
    // a parent Marker for Popup / Tooltip nesting) via add_*. Ownership
    // transfers; the Python wrapper becomes a non-owning alias of
    // whatever holds it afterward.

    auto map_item_cls =
        nb::class_<Wt::WLeafletMap::AbstractMapItem, Wt::WObject>(
            m, "WLeafletMapAbstractMapItem")
        .def("move", &Wt::WLeafletMap::AbstractMapItem::move, "pos"_a,
             "Move the item to a new coordinate. Triggers a re-render "
             "if the item is already attached to a map.")
        .def_prop_ro("position",
            &Wt::WLeafletMap::AbstractMapItem::position)
        .def_prop_ro("clicked",
            &Wt::WLeafletMap::AbstractMapItem::clicked,
            nb::rv_policy::reference_internal,
            "Signal[] — user clicked the item. For overlay items "
            "(Popup, Tooltip), `interactive` must be set in options.")
        .def_prop_ro("double_clicked",
            &Wt::WLeafletMap::AbstractMapItem::doubleClicked,
            nb::rv_policy::reference_internal)
        .def_prop_ro("mouse_went_down",
            &Wt::WLeafletMap::AbstractMapItem::mouseWentDown,
            nb::rv_policy::reference_internal)
        .def_prop_ro("mouse_went_up",
            &Wt::WLeafletMap::AbstractMapItem::mouseWentUp,
            nb::rv_policy::reference_internal)
        .def_prop_ro("mouse_went_over",
            &Wt::WLeafletMap::AbstractMapItem::mouseWentOver,
            nb::rv_policy::reference_internal)
        .def_prop_ro("mouse_went_out",
            &Wt::WLeafletMap::AbstractMapItem::mouseWentOut,
            nb::rv_policy::reference_internal);

    auto overlay_cls =
        nb::class_<Wt::WLeafletMap::AbstractOverlayItem,
                   Wt::WLeafletMap::AbstractMapItem>(
            m, "WLeafletMapAbstractOverlayItem")
        .def("set_options",
            &Wt::WLeafletMap::AbstractOverlayItem::setOptions,
            "options"_a,
            "Leaflet-side options for this overlay (autoClose, "
            "closeOnClick, etc.). See "
            "https://leafletjs.com/reference.html for the full list.")
        .def("set_content",
            [](Wt::WLeafletMap::AbstractOverlayItem& self,
               std::unique_ptr<Wt::WWidget> content) {
                self.setContent(std::move(content));
            },
            "content"_a,
            "Replace the overlay's content with a widget. Ownership "
            "transfers — the Python wrapper becomes a non-owning alias.")
        .def("set_content_text",
            [](Wt::WLeafletMap::AbstractOverlayItem& self,
               const Wt::WString& text) {
                self.setContent(text);
            },
            "text"_a,
            "Convenience: set content to a WText wrapping the given "
            "string. Same effect as set_content(WText(text)).")
        .def("open",   &Wt::WLeafletMap::AbstractOverlayItem::open)
        .def("close",  &Wt::WLeafletMap::AbstractOverlayItem::close)
        .def("toggle", &Wt::WLeafletMap::AbstractOverlayItem::toggle)
        .def_prop_ro("is_open",
            &Wt::WLeafletMap::AbstractOverlayItem::isOpen)
        .def_prop_ro("opened_signal",
            &Wt::WLeafletMap::AbstractOverlayItem::opened,
            nb::rv_policy::reference_internal)
        .def_prop_ro("closed_signal",
            &Wt::WLeafletMap::AbstractOverlayItem::closed,
            nb::rv_policy::reference_internal);

    // Popup — opens on user interaction (or programmatically via open()).
    auto popup_cls =
        nb::class_<Wt::WLeafletMap::Popup,
                   Wt::WLeafletMap::AbstractOverlayItem>(
            m, "WLeafletMapPopup")
        .def(nb::init<const Wt::WLeafletMap::Coordinate&>(), "pos"_a)
        .def(nb::init<const Wt::WString&>(), "content"_a,
             "Shortcut: popup whose content is a WText wrapping the "
             "given string.")
        .def(nb::init<const Wt::WLeafletMap::Coordinate&, const Wt::WString&>(),
             "pos"_a, "content"_a)
        .def("__init__",
            [](Wt::WLeafletMap::Popup* self,
               const Wt::WLeafletMap::Coordinate& pos,
               std::unique_ptr<Wt::WWidget> content) {
                new (self) Wt::WLeafletMap::Popup(pos, std::move(content));
            },
            "pos"_a, "content"_a,
            "Popup at `pos` with a widget content. Ownership of "
            "`content` transfers.");

    // Tooltip — like Popup but typically shown on hover.
    auto tooltip_cls =
        nb::class_<Wt::WLeafletMap::Tooltip,
                   Wt::WLeafletMap::AbstractOverlayItem>(
            m, "WLeafletMapTooltip")
        .def(nb::init<const Wt::WLeafletMap::Coordinate&>(), "pos"_a)
        .def(nb::init<const Wt::WString&>(), "content"_a)
        .def(nb::init<const Wt::WLeafletMap::Coordinate&, const Wt::WString&>(),
             "pos"_a, "content"_a)
        .def("__init__",
            [](Wt::WLeafletMap::Tooltip* self,
               const Wt::WLeafletMap::Coordinate& pos,
               std::unique_ptr<Wt::WWidget> content) {
                new (self) Wt::WLeafletMap::Tooltip(pos, std::move(content));
            },
            "pos"_a, "content"_a);

    // Marker (abstract — concrete subclasses below).
    auto marker_cls =
        nb::class_<Wt::WLeafletMap::Marker,
                   Wt::WLeafletMap::AbstractMapItem>(
            m, "WLeafletMapMarker")
        .def("add_popup",
            [](Wt::WLeafletMap::Marker& self,
               std::unique_ptr<Wt::WLeafletMap::Popup> popup)
                -> Wt::WLeafletMap::Popup* {
                Wt::WLeafletMap::Popup* raw = popup.get();
                self.addPopup(std::move(popup));
                return raw;
            },
            "popup"_a, nb::rv_policy::reference_internal,
            "Attach a popup that opens when the marker is clicked. "
            "Replaces any previously-added popup on this marker.")
        .def("remove_popup",
            [](Wt::WLeafletMap::Marker& self) {
                // Discard the returned unique_ptr — Python doesn't need
                // it (the popup wrapper it held is still valid, just
                // detached).
                self.removePopup();
            })
        .def_prop_ro("popup",
            [](Wt::WLeafletMap::Marker& self) { return self.popup(); },
            nb::rv_policy::reference_internal,
            "Current popup, or None if none is attached.")
        .def("add_tooltip",
            [](Wt::WLeafletMap::Marker& self,
               std::unique_ptr<Wt::WLeafletMap::Tooltip> tooltip)
                -> Wt::WLeafletMap::Tooltip* {
                Wt::WLeafletMap::Tooltip* raw = tooltip.get();
                self.addTooltip(std::move(tooltip));
                return raw;
            },
            "tooltip"_a, nb::rv_policy::reference_internal,
            "Attach a tooltip that appears on hover. Replaces any "
            "previously-added tooltip.")
        .def("remove_tooltip",
            [](Wt::WLeafletMap::Marker& self) { self.removeTooltip(); })
        .def_prop_ro("tooltip",
            [](Wt::WLeafletMap::Marker& self) { return self.tooltip(); },
            nb::rv_policy::reference_internal);

    // LeafletMarker — the default Leaflet pin.
    auto leaflet_marker_cls =
        nb::class_<Wt::WLeafletMap::LeafletMarker,
                   Wt::WLeafletMap::Marker>(
            m, "WLeafletMapLeafletMarker")
        .def(nb::init<const Wt::WLeafletMap::Coordinate&>(), "pos"_a,
             "Construct the standard Leaflet pin marker.")
        .def("set_options",
             &Wt::WLeafletMap::LeafletMarker::setOptions, "options"_a,
             "Leaflet marker options (icon, draggable, riseOnHover, …). "
             "See https://leafletjs.com/reference.html#marker.");

    // WidgetMarker — render the marker as an arbitrary Wt widget.
    auto widget_marker_cls =
        nb::class_<Wt::WLeafletMap::WidgetMarker,
                   Wt::WLeafletMap::Marker>(
            m, "WLeafletMapWidgetMarker")
        .def("__init__",
            [](Wt::WLeafletMap::WidgetMarker* self,
               const Wt::WLeafletMap::Coordinate& pos,
               std::unique_ptr<Wt::WWidget> widget) {
                new (self) Wt::WLeafletMap::WidgetMarker(
                    pos, std::move(widget));
            },
            "pos"_a, "widget"_a,
            "Place an arbitrary Wt widget at `pos` on the map. "
            "Ownership of the widget transfers.")
        .def_prop_ro("widget",
            // Disambiguate the const-overloaded widget() accessor.
            [](Wt::WLeafletMap::WidgetMarker& self) {
                return self.widget();
            },
            nb::rv_policy::reference_internal)
        .def("set_anchor_point",
             &Wt::WLeafletMap::WidgetMarker::setAnchorPoint, "x"_a, "y"_a,
             "Anchor (the 'tip' of the marker relative to its top-left "
             "corner) in pixels. Negative x = horizontal center; "
             "negative y = vertical center. Default is centred both ways.");

    auto leaflet_cls = nb::class_<Wt::WLeafletMap, Wt::WWidget>(m, "WLeafletMap")
        .def(nb::init<>())
        .def(nb::init<const Wt::Json::Object&>(), "options"_a,
             "Construct with Leaflet map options (e.g. centre, zoom). "
             "Pass a Json.Object (or use the default ctor + set_options).")
        .def("set_options",
            // Overloaded with the marker classes; pick the no-prefix form.
            nb::overload_cast<const Wt::Json::Object&>(
                &Wt::WLeafletMap::setOptions),
            "options"_a)
        .def("add_tile_layer",
            &Wt::WLeafletMap::addTileLayer,
            "url_template"_a, "options"_a,
            "Add a tile source. `url_template` is a Leaflet URL template "
            "with {z}/{x}/{y} placeholders (e.g. "
            "'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'). "
            "`options` is a Json.Object holding Leaflet tile-layer "
            "options (maxZoom, attribution, subdomains, …).")
        .def("pan_to", &Wt::WLeafletMap::panTo, "center"_a)
        .def_prop_rw("zoom_level",
            &Wt::WLeafletMap::zoomLevel,
            &Wt::WLeafletMap::setZoomLevel)
        .def_prop_ro("position",
            // Wt has both `position()` const and a setter-via-panTo on
            // the widget; expose the read side as a property.
            [](const Wt::WLeafletMap& m) {
                return m.position();
            })
        .def_prop_ro("zoom_level_changed",
            &Wt::WLeafletMap::zoomLevelChanged,
            nb::rv_policy::reference_internal,
            "JIntSignal — fires with the new zoom level when the user "
            "scrolls or pinches.")
        // ---- overlay management ----
        .def("add_marker",
            [](Wt::WLeafletMap& self,
               std::unique_ptr<Wt::WLeafletMap::Marker> marker)
                -> Wt::WLeafletMap::Marker* {
                Wt::WLeafletMap::Marker* raw = marker.get();
                self.addMarker(std::move(marker));
                return raw;
            },
            "marker"_a, nb::rv_policy::reference_internal,
            "Attach a Marker (LeafletMarker or WidgetMarker) to the map. "
            "Ownership transfers; the returned reference can be used to "
            "wire signals or call add_popup/add_tooltip on it.")
        .def("add_popup",
            [](Wt::WLeafletMap& self,
               std::unique_ptr<Wt::WLeafletMap::Popup> popup)
                -> Wt::WLeafletMap::Popup* {
                Wt::WLeafletMap::Popup* raw = popup.get();
                self.addPopup(std::move(popup));
                return raw;
            },
            "popup"_a, nb::rv_policy::reference_internal,
            "Attach a standalone Popup to the map (separate from any "
            "marker). The popup opens at its configured coordinate.")
        .def("add_tooltip",
            [](Wt::WLeafletMap& self,
               std::unique_ptr<Wt::WLeafletMap::Tooltip> tooltip)
                -> Wt::WLeafletMap::Tooltip* {
                Wt::WLeafletMap::Tooltip* raw = tooltip.get();
                self.addTooltip(std::move(tooltip));
                return raw;
            },
            "tooltip"_a, nb::rv_policy::reference_internal);

    // Re-attach all the nested types under their natural names so users
    // can write wt.WLeafletMap.Marker rather than wt.WLeafletMapMarker.
    leaflet_cls.attr("Coordinate")          = leaflet_coord_cls;
    leaflet_cls.attr("AbstractMapItem")     = map_item_cls;
    leaflet_cls.attr("AbstractOverlayItem") = overlay_cls;
    leaflet_cls.attr("Popup")               = popup_cls;
    leaflet_cls.attr("Tooltip")             = tooltip_cls;
    leaflet_cls.attr("Marker")              = marker_cls;
    leaflet_cls.attr("LeafletMarker")       = leaflet_marker_cls;
    leaflet_cls.attr("WidgetMarker")        = widget_marker_cls;
}

}  // namespace witty_for_python
