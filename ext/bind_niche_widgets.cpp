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
    // Inherits WPaintedWidget in C++ but bound as inheriting WInteractWidget
    // directly (the same approach as the charts) to avoid the PyPaintedWidget
    // Python-type mismatch. The built-in paintEvent handles all rendering.

    nb::enum_<Wt::WQrCode::ErrorCorrectionLevel>(m, "ErrorCorrectionLevel",
        "QR-code error-correction strength. Higher levels can survive\n"
        "more damage to the printed code but encode less data per pixel.")
        .value("Low",      Wt::WQrCode::ErrorCorrectionLevel::LOW,
               "~7% of codewords can be restored.")
        .value("Medium",   Wt::WQrCode::ErrorCorrectionLevel::MEDIUM,
               "~15% recoverable.")
        .value("Quartile", Wt::WQrCode::ErrorCorrectionLevel::QUARTILE,
               "~25% recoverable.")
        .value("High",     Wt::WQrCode::ErrorCorrectionLevel::HIGH,
               "~30% recoverable.");

    nb::class_<Wt::WQrCode, Wt::WInteractWidget>(m, "WQrCode",
        "A painted QR code. Encodes a text message as a 2D barcode and\n"
        "renders it as a vector image — scales cleanly to any size.\n"
        "\n"
        "    qr = container.add_widget(wt.WQrCode('https://example.com', 4))\n"
        "    qr.brush = wt.WBrush(wt.WColor(0, 64, 128))\n"
        "\n"
        "If the message is too long for the configured error-correction\n"
        "level, the `error` flag turns True — drop to a lower ECL or\n"
        "shorten the input.")
        .def(heap_init<Wt::WQrCode>(),
             "Construct an empty QR code. Set `message` and `square_size`\n"
             "before adding to a container.")
        .def(heap_init<Wt::WQrCode, const std::string&, double>(),
             "message"_a, "square_size"_a,
             "Construct encoding `message`, with each module rendered at\n"
             "`square_size` pixels and the default error-correction level.")
        .def(heap_init<Wt::WQrCode, const std::string&,
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
            &Wt::WQrCode::setSquareSize,
            "Side length in pixels of each QR-code module (the black/white\n"
            "squares). Larger values make a bigger, easier-to-scan code.")
        .def("set_error_correction_level",
             &Wt::WQrCode::setErrorCorrectionLevel, "ecl"_a,
             "Replace the active error-correction level. Triggers a\n"
             "re-encode and re-paint.")
        .def_prop_rw("brush",
            &Wt::WQrCode::brush,
            &Wt::WQrCode::setBrush,
            "Brush used to paint the QR squares (default black solid). "
            "Tint with a colored brush; the background stays transparent.")
        .def_prop_ro("error", &Wt::WQrCode::error,
             "True if the encoder couldn't fit the message at the "
             "configured ECL — try Low or shorten the message.")
        .def("update",
            [](Wt::WQrCode& self) { self.update(); },
            "Force a re-paint. Normally unnecessary — assignments to\n"
            "`message` / `brush` / `square_size` re-paint automatically.");

    // Requires a `google_api_key` config property set at server startup
    // (in Wt's config XML). Without it the widget renders an error pane.

    nb::enum_<Wt::GoogleMapsVersion>(m, "GoogleMapsVersion",
        "Google Maps JavaScript API version to load.")
        .value("v3", Wt::GoogleMapsVersion::v3,
               "The current (v3) Maps JS API.");

    nb::enum_<Wt::MapTypeControl>(m, "MapTypeControl",
        "Style of the map-type selector (roadmap / satellite / hybrid /\n"
        "terrain switch) rendered over the Google Map.")
        .value("None_",         Wt::MapTypeControl::None,
               "Hide the selector entirely.")
        .value("Default",       Wt::MapTypeControl::Default,
               "Whatever the Maps API uses by default for the device.")
        .value("Menu",          Wt::MapTypeControl::Menu,
               "Dropdown menu form.")
        .value("Hierarchical",  Wt::MapTypeControl::Hierarchical,
               "Nested button/menu form for compact displays.")
        .value("HorizontalBar", Wt::MapTypeControl::HorizontalBar,
               "Horizontal row of pill buttons.");

    auto coord_cls = nb::class_<Wt::WGoogleMap::Coordinate>(
        m, "GoogleMapCoordinate",
        "A latitude/longitude pair, used as positions/centres for\n"
        "WGoogleMap operations. Plain value type — copy freely.")
        .def(nb::init<>(),
             "Construct (0, 0) — the null island.")
        .def(nb::init<double, double>(), "latitude"_a, "longitude"_a,
             "Construct from explicit latitude and longitude in decimal\n"
             "degrees (positive N/E, negative S/W).")
        .def_prop_rw("latitude",
            &Wt::WGoogleMap::Coordinate::latitude,
            &Wt::WGoogleMap::Coordinate::setLatitude,
            "Latitude in decimal degrees.")
        .def_prop_rw("longitude",
            &Wt::WGoogleMap::Coordinate::longitude,
            &Wt::WGoogleMap::Coordinate::setLongitude,
            "Longitude in decimal degrees.")
        .def("distance_to", &Wt::WGoogleMap::Coordinate::distanceTo,
             "other"_a,
             "Great-circle distance to `other` in kilometres "
             "(despite Wt's docs naming metres).")
        .def("__repr__",
            [](const Wt::WGoogleMap::Coordinate& c) {
                return "GoogleMapCoordinate(lat=" + std::to_string(c.latitude())
                     + ", lon=" + std::to_string(c.longitude()) + ")";
            });

    auto gmap_cls = nb::class_<Wt::WGoogleMap, Wt::WWidget>(m, "WGoogleMap",
        "Embedded Google Maps widget. Renders an interactive map served\n"
        "by the Google Maps JS API and lets server-side Python add markers,\n"
        "polylines, circles, and info windows.\n"
        "\n"
        "    gmap = container.add_widget(wt.WGoogleMap(wt.GoogleMapsVersion.v3))\n"
        "    gmap.set_center(wt.WGoogleMap.Coordinate(37.7749, -122.4194), 12)\n"
        "    gmap.add_marker(wt.WGoogleMap.Coordinate(37.7749, -122.4194))\n"
        "\n"
        "Requires a Google Maps API key configured server-side via Wt's\n"
        "config XML (`google_api_key` property). Without it the widget\n"
        "renders an error pane.")
        // No default value for the version arg — nanobind has trouble
        // casting value-typed defaults (WColor() etc.) at module init.
        .def(heap_init<Wt::WGoogleMap, Wt::GoogleMapsVersion>(), "version"_a,
             "Construct against the given Google Maps API version.")
        .def("set_center",
            nb::overload_cast<const Wt::WGoogleMap::Coordinate&>(
                &Wt::WGoogleMap::setCenter),
            "center"_a,
            "Pan the map so `center` is at the viewport centre. Keeps\n"
            "the current zoom level.")
        .def("set_center",
            nb::overload_cast<const Wt::WGoogleMap::Coordinate&, int>(
                &Wt::WGoogleMap::setCenter),
            "center"_a, "zoom"_a,
            "Pan to `center` and set the zoom level in one call.")
        .def("pan_to", &Wt::WGoogleMap::panTo, "center"_a,
             "Smoothly animate the viewport to `center` (vs. the snap-jump\n"
             "of `set_center`).")
        .def("set_zoom", &Wt::WGoogleMap::setZoom, "level"_a,
             "Set the zoom level (integer; ~0 = whole world, ~22 = street\n"
             "level depending on the area).")
        .def("zoom_in",  &Wt::WGoogleMap::zoomIn,
             "Increase the zoom level by one.")
        .def("zoom_out", &Wt::WGoogleMap::zoomOut,
             "Decrease the zoom level by one.")
        .def("save_position", &Wt::WGoogleMap::savePosition,
             "Remember the current centre + zoom. Restore with "
             "return_to_saved_position.")
        .def("return_to_saved_position",
             &Wt::WGoogleMap::returnToSavedPosition,
             "Pan/zoom back to whatever was last `save_position`'d.")
        .def("add_marker", &Wt::WGoogleMap::addMarker, "position"_a,
             "Drop the default Google-Maps pin at `position`.")
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

    // OpenStreetMap-backed map widget. Unlike WGoogleMap, no external
    // API key is required — the widget renders tiles fetched directly
    // from an OpenStreetMap (or compatible) tile server, configured
    // via add_tile_layer.

    auto leaflet_coord_cls = nb::class_<Wt::WLeafletMap::Coordinate>(
        m, "LeafletMapCoordinate",
        "A latitude/longitude pair used as the position for WLeafletMap\n"
        "items. Plain value type — copy freely.")
        .def(nb::init<>(),
             "Construct (0, 0).")
        .def(nb::init<double, double>(), "latitude"_a, "longitude"_a,
             "Construct from explicit decimal-degree latitude and longitude.")
        .def_prop_rw("latitude",
            &Wt::WLeafletMap::Coordinate::latitude,
            &Wt::WLeafletMap::Coordinate::setLatitude,
            "Latitude in decimal degrees.")
        .def_prop_rw("longitude",
            &Wt::WLeafletMap::Coordinate::longitude,
            &Wt::WLeafletMap::Coordinate::setLongitude,
            "Longitude in decimal degrees.")
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
            m, "WLeafletMapAbstractMapItem",
            "Abstract base for anything placed on a WLeafletMap — markers,\n"
            "popups, tooltips. Holds a coordinate and the standard set of\n"
            "mouse-interaction signals.")
        .def("move", &Wt::WLeafletMap::AbstractMapItem::move, "pos"_a,
             "Move the item to a new coordinate. Triggers a re-render "
             "if the item is already attached to a map.")
        .def_prop_ro("position",
            &Wt::WLeafletMap::AbstractMapItem::position,
            "The item's current coordinate.")
        .def_prop_ro("clicked",
            &Wt::WLeafletMap::AbstractMapItem::clicked,
            nb::rv_policy::reference_internal,
            "Signal[] — user clicked the item. For overlay items "
            "(Popup, Tooltip), `interactive` must be set in options.")
        .def_prop_ro("double_clicked",
            &Wt::WLeafletMap::AbstractMapItem::doubleClicked,
            nb::rv_policy::reference_internal,
            "Signal[] — user double-clicked the item.")
        .def_prop_ro("mouse_went_down",
            &Wt::WLeafletMap::AbstractMapItem::mouseWentDown,
            nb::rv_policy::reference_internal,
            "Signal[] — mouse button pressed over the item.")
        .def_prop_ro("mouse_went_up",
            &Wt::WLeafletMap::AbstractMapItem::mouseWentUp,
            nb::rv_policy::reference_internal,
            "Signal[] — mouse button released over the item.")
        .def_prop_ro("mouse_went_over",
            &Wt::WLeafletMap::AbstractMapItem::mouseWentOver,
            nb::rv_policy::reference_internal,
            "Signal[] — cursor entered the item.")
        .def_prop_ro("mouse_went_out",
            &Wt::WLeafletMap::AbstractMapItem::mouseWentOut,
            nb::rv_policy::reference_internal,
            "Signal[] — cursor left the item.");

    auto overlay_cls =
        nb::class_<Wt::WLeafletMap::AbstractOverlayItem,
                   Wt::WLeafletMap::AbstractMapItem>(
            m, "WLeafletMapAbstractOverlayItem",
            "Common base for Popup and Tooltip — overlay items that hold a\n"
            "content widget and can be opened/closed.")
        .def("set_options",
            &Wt::WLeafletMap::AbstractOverlayItem::setOptions,
            "options"_a,
            "Leaflet-side options for this overlay (autoClose, "
            "closeOnClick, etc.). See "
            "https://leafletjs.com/reference.html for the full list.")
        .def("set_content",
            [](Wt::WLeafletMap::AbstractOverlayItem& self,
               nb::object py_content) {
                auto c = nb::cast<std::unique_ptr<Wt::WWidget>>(py_content);
                self.setContent(std::move(c));
                nb::inst_set_state(py_content, /*ready*/ true,
                                   /*destruct*/ false);
            },
            "content"_a,
            "Replace the overlay's content with a widget. Ownership "
            "transfers; the Python wrapper is re-armed as a non-owning alias.")
        .def("set_content_text",
            [](Wt::WLeafletMap::AbstractOverlayItem& self,
               const Wt::WString& text) {
                self.setContent(text);
            },
            "text"_a,
            "Convenience: set content to a WText wrapping the given "
            "string. Same effect as set_content(WText(text)).")
        .def("open",   &Wt::WLeafletMap::AbstractOverlayItem::open,
             "Show the overlay programmatically.")
        .def("close",  &Wt::WLeafletMap::AbstractOverlayItem::close,
             "Hide the overlay programmatically.")
        .def("toggle", &Wt::WLeafletMap::AbstractOverlayItem::toggle,
             "Flip between open and closed.")
        .def_prop_ro("is_open",
            &Wt::WLeafletMap::AbstractOverlayItem::isOpen,
            "True if the overlay is currently visible.")
        .def_prop_ro("opened_signal",
            &Wt::WLeafletMap::AbstractOverlayItem::opened,
            nb::rv_policy::reference_internal,
            "Signal[] — fires when the overlay transitions to open.")
        .def_prop_ro("closed_signal",
            &Wt::WLeafletMap::AbstractOverlayItem::closed,
            nb::rv_policy::reference_internal,
            "Signal[] — fires when the overlay transitions to closed.");

    // All construction routes go through nb::new_ (heap allocation) so the
    // Popup can later transfer to std::unique_ptr<WLeafletMap::Popup> via
    // Marker.add_popup; nanobind blocks that transfer for nb::init<>-built
    // instances because their storage is part of the PyObject.
    auto popup_cls =
        nb::class_<Wt::WLeafletMap::Popup,
                   Wt::WLeafletMap::AbstractOverlayItem>(
            m, "WLeafletMapPopup",
            "Floating overlay attached to a coordinate. Typically opens on\n"
            "marker click (when added via Marker.add_popup) or programmatically\n"
            "via open(). Content is either a WText shortcut or any widget.")
        .def(heap_init<Wt::WLeafletMap::Popup,
                       const Wt::WLeafletMap::Coordinate&>(), "pos"_a,
             "Construct an empty popup anchored at `pos`. Set content\n"
             "later via set_content / set_content_text.")
        .def(heap_init<Wt::WLeafletMap::Popup, const Wt::WString&>(),
             "content"_a,
             "Shortcut: popup whose content is a WText wrapping the "
             "given string.")
        .def(heap_init<Wt::WLeafletMap::Popup,
                       const Wt::WLeafletMap::Coordinate&,
                       const Wt::WString&>(),
             "pos"_a, "content"_a,
             "Construct anchored at `pos` with the given text as content.")
        .def(nb::new_(
                [](const Wt::WLeafletMap::Coordinate& pos,
                   std::unique_ptr<Wt::WWidget> content) {
                    return std::make_unique<Wt::WLeafletMap::Popup>(
                        pos, std::move(content));
                }),
            "pos"_a, "content"_a,
            "Popup at `pos` with a widget content. Ownership of "
            "`content` transfers.");

    auto tooltip_cls =
        nb::class_<Wt::WLeafletMap::Tooltip,
                   Wt::WLeafletMap::AbstractOverlayItem>(
            m, "WLeafletMapTooltip",
            "Floating label attached to a coordinate. Like Popup but\n"
            "typically shown on hover instead of click. Same content API\n"
            "(string-shortcut or arbitrary widget).")
        .def(heap_init<Wt::WLeafletMap::Tooltip,
                       const Wt::WLeafletMap::Coordinate&>(), "pos"_a,
             "Construct an empty tooltip anchored at `pos`.")
        .def(heap_init<Wt::WLeafletMap::Tooltip, const Wt::WString&>(),
             "content"_a,
             "Shortcut: tooltip whose content is a WText wrapping the\n"
             "given string.")
        .def(heap_init<Wt::WLeafletMap::Tooltip,
                       const Wt::WLeafletMap::Coordinate&,
                       const Wt::WString&>(),
             "pos"_a, "content"_a,
             "Construct anchored at `pos` with the given text as content.")
        .def(nb::new_(
                [](const Wt::WLeafletMap::Coordinate& pos,
                   std::unique_ptr<Wt::WWidget> content) {
                    return std::make_unique<Wt::WLeafletMap::Tooltip>(
                        pos, std::move(content));
                }),
            "pos"_a, "content"_a,
            "Tooltip at `pos` with a widget content. Ownership of\n"
            "`content` transfers.");

    // Concrete subclasses (LeafletMarker, WidgetMarker) follow below.
    auto marker_cls =
        nb::class_<Wt::WLeafletMap::Marker,
                   Wt::WLeafletMap::AbstractMapItem>(
            m, "WLeafletMapMarker",
            "Abstract base for map markers. Carries an optional Popup and\n"
            "Tooltip; concrete subclasses (LeafletMarker, WidgetMarker)\n"
            "decide what's actually rendered at the marker's position.")
        .def("add_popup",
            [](Wt::WLeafletMap::Marker& self, nb::object py_popup)
                -> nb::object {
                auto p = nb::cast<std::unique_ptr<Wt::WLeafletMap::Popup>>(
                    py_popup);
                self.addPopup(std::move(p));
                nb::inst_set_state(py_popup, /*ready*/ true,
                                   /*destruct*/ false);
                return py_popup;
            },
            "popup"_a,
            "Attach a popup that opens when the marker is clicked. "
            "Replaces any previously-added popup on this marker.")
        .def("remove_popup",
            [](Wt::WLeafletMap::Marker& self) {
                // Discard the returned unique_ptr — Python doesn't need
                // it (the popup wrapper it held is still valid, just
                // detached).
                self.removePopup();
            },
            "Detach the currently-attached popup, if any.")
        .def_prop_ro("popup",
            [](Wt::WLeafletMap::Marker& self) { return self.popup(); },
            nb::rv_policy::reference_internal,
            "Current popup, or None if none is attached.")
        .def("add_tooltip",
            [](Wt::WLeafletMap::Marker& self, nb::object py_tooltip)
                -> nb::object {
                auto t = nb::cast<std::unique_ptr<Wt::WLeafletMap::Tooltip>>(
                    py_tooltip);
                self.addTooltip(std::move(t));
                nb::inst_set_state(py_tooltip, /*ready*/ true,
                                   /*destruct*/ false);
                return py_tooltip;
            },
            "tooltip"_a,
            "Attach a tooltip that appears on hover. Replaces any "
            "previously-added tooltip.")
        .def("remove_tooltip",
            [](Wt::WLeafletMap::Marker& self) { self.removeTooltip(); },
            "Detach the currently-attached tooltip, if any.")
        .def_prop_ro("tooltip",
            [](Wt::WLeafletMap::Marker& self) { return self.tooltip(); },
            nb::rv_policy::reference_internal,
            "Current tooltip, or None if none is attached.");

    auto leaflet_marker_cls =
        nb::class_<Wt::WLeafletMap::LeafletMarker,
                   Wt::WLeafletMap::Marker>(
            m, "WLeafletMapLeafletMarker",
            "Marker rendered as the default Leaflet pin. The standard\n"
            "round-headed marker drop you get from leafletjs by default.")
        .def(heap_init<Wt::WLeafletMap::LeafletMarker,
                       const Wt::WLeafletMap::Coordinate&>(), "pos"_a,
             "Construct the standard Leaflet pin marker.")
        .def("set_options",
             &Wt::WLeafletMap::LeafletMarker::setOptions, "options"_a,
             "Leaflet marker options (icon, draggable, riseOnHover, …). "
             "See https://leafletjs.com/reference.html#marker.");

    auto widget_marker_cls =
        nb::class_<Wt::WLeafletMap::WidgetMarker,
                   Wt::WLeafletMap::Marker>(
            m, "WLeafletMapWidgetMarker",
            "Marker rendered as an arbitrary Wt widget — pin yourself a\n"
            "WImage, a WText, a WContainerWidget with custom HTML, etc.\n"
            "Useful when the default Leaflet pin isn't enough.")
        .def(nb::new_(
                [](const Wt::WLeafletMap::Coordinate& pos,
                   std::unique_ptr<Wt::WWidget> widget) {
                    return std::make_unique<Wt::WLeafletMap::WidgetMarker>(
                        pos, std::move(widget));
                }),
            "pos"_a, "widget"_a,
            "Place an arbitrary Wt widget at `pos` on the map. "
            "Ownership of the widget transfers.")
        .def_prop_ro("widget",
            // Disambiguate the const-overloaded widget() accessor.
            [](Wt::WLeafletMap::WidgetMarker& self) {
                return self.widget();
            },
            nb::rv_policy::reference_internal,
            "The widget rendered at the marker's position.")
        .def("set_anchor_point",
             &Wt::WLeafletMap::WidgetMarker::setAnchorPoint, "x"_a, "y"_a,
             "Anchor (the 'tip' of the marker relative to its top-left "
             "corner) in pixels. Negative x = horizontal center; "
             "negative y = vertical center. Default is centred both ways.");

    auto leaflet_cls = nb::class_<Wt::WLeafletMap, Wt::WWidget>(m, "WLeafletMap",
        "Interactive map widget powered by leafletjs. Unlike WGoogleMap,\n"
        "no API key is required — the widget renders tiles fetched from\n"
        "any compatible tile server (OpenStreetMap, Mapbox, etc.) that\n"
        "you configure via `add_tile_layer`.\n"
        "\n"
        "    leaf = container.add_widget(wt.WLeafletMap())\n"
        "    leaf.add_tile_layer(\n"
        "        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',\n"
        "        tile_options)\n"
        "    leaf.pan_to(wt.WLeafletMap.Coordinate(51.5074, -0.1278))\n"
        "    leaf.zoom_level = 12\n"
        "    leaf.add_marker(wt.WLeafletMap.LeafletMarker(\n"
        "        wt.WLeafletMap.Coordinate(51.5074, -0.1278)))\n"
        "\n"
        "Markers, popups, and tooltips are added via add_marker /\n"
        "add_popup / add_tooltip. Each transfers ownership; the Python\n"
        "wrapper is re-armed as a non-owning alias so chaining works.")
        .def(heap_init<Wt::WLeafletMap>(),
             "Construct an empty map with default options.")
        .def(heap_init<Wt::WLeafletMap, const Wt::Json::Object&>(), "options"_a,
             "Construct with Leaflet map options (e.g. centre, zoom). "
             "Pass a Json.Object (or use the default ctor + set_options).")
        .def("set_options",
            // Overloaded with the marker classes; pick the no-prefix form.
            nb::overload_cast<const Wt::Json::Object&>(
                &Wt::WLeafletMap::setOptions),
            "options"_a,
            "Replace the Leaflet map options. Effective for subsequent\n"
            "re-renders.")
        .def("add_tile_layer",
            &Wt::WLeafletMap::addTileLayer,
            "url_template"_a, "options"_a,
            "Add a tile source. `url_template` is a Leaflet URL template "
            "with {z}/{x}/{y} placeholders (e.g. "
            "'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'). "
            "`options` is a Json.Object holding Leaflet tile-layer "
            "options (maxZoom, attribution, subdomains, …).")
        .def("pan_to", &Wt::WLeafletMap::panTo, "center"_a,
             "Smoothly animate the viewport so `center` is at the middle\n"
             "of the visible area.")
        .def_prop_rw("zoom_level",
            &Wt::WLeafletMap::zoomLevel,
            &Wt::WLeafletMap::setZoomLevel,
            "Current zoom level (integer). Assigning sets it; mutating\n"
            "client-side via scroll/pinch reports back via\n"
            "`zoom_level_changed`.")
        .def_prop_ro("position",
            // Wt has both `position()` const and a setter-via-panTo on
            // the widget; expose the read side as a property.
            [](const Wt::WLeafletMap& m) {
                return m.position();
            },
            "Current map centre coordinate. Use `pan_to` to set.")
        .def_prop_ro("zoom_level_changed",
            &Wt::WLeafletMap::zoomLevelChanged,
            nb::rv_policy::reference_internal,
            "JIntSignal — fires with the new zoom level when the user "
            "scrolls or pinches.")
        // ---- overlay management ----
        .def("add_marker",
            [](Wt::WLeafletMap& self, nb::object py_marker) -> nb::object {
                auto m = nb::cast<std::unique_ptr<Wt::WLeafletMap::Marker>>(
                    py_marker);
                self.addMarker(std::move(m));
                nb::inst_set_state(py_marker, /*ready*/ true,
                                   /*destruct*/ false);
                return py_marker;
            },
            "marker"_a,
            "Attach a Marker (LeafletMarker or WidgetMarker) to the map. "
            "Ownership transfers; the wrapper is re-armed as a non-owning "
            "alias, so chains like `m.add_marker(mkr).add_popup(p)` work.")
        .def("add_popup",
            [](Wt::WLeafletMap& self, nb::object py_popup) -> nb::object {
                auto p = nb::cast<std::unique_ptr<Wt::WLeafletMap::Popup>>(
                    py_popup);
                self.addPopup(std::move(p));
                nb::inst_set_state(py_popup, /*ready*/ true,
                                   /*destruct*/ false);
                return py_popup;
            },
            "popup"_a,
            "Attach a standalone Popup to the map (separate from any "
            "marker). The popup opens at its configured coordinate.")
        .def("add_tooltip",
            [](Wt::WLeafletMap& self, nb::object py_tooltip) -> nb::object {
                auto t = nb::cast<std::unique_ptr<Wt::WLeafletMap::Tooltip>>(
                    py_tooltip);
                self.addTooltip(std::move(t));
                nb::inst_set_state(py_tooltip, /*ready*/ true,
                                   /*destruct*/ false);
                return py_tooltip;
            },
            "tooltip"_a,
            "Attach a standalone Tooltip to the map (separate from any\n"
            "marker). Ownership transfers; the wrapper is re-armed as a\n"
            "non-owning alias.");

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
