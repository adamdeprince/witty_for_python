# Maps & QR

> Interactive maps (Leaflet, Google Maps) and QR-code rendering.

**Classes in this section:**

- [`ErrorCorrectionLevel`](#ErrorCorrectionLevel)
- [`WQrCode`](#WQrCode)
- [`GoogleMapsVersion`](#GoogleMapsVersion)
- [`MapTypeControl`](#MapTypeControl)
- [`GoogleMapCoordinate`](#GoogleMapCoordinate)
- [`WGoogleMap`](#WGoogleMap)
- [`LeafletMapCoordinate`](#LeafletMapCoordinate)
- [`WLeafletMap`](#WLeafletMap)
- [`WLeafletMapAbstractMapItem`](#WLeafletMapAbstractMapItem)
- [`WLeafletMapAbstractOverlayItem`](#WLeafletMapAbstractOverlayItem)
- [`WLeafletMapPopup`](#WLeafletMapPopup)
- [`WLeafletMapTooltip`](#WLeafletMapTooltip)
- [`WLeafletMapMarker`](#WLeafletMapMarker)
- [`WLeafletMapLeafletMarker`](#WLeafletMapLeafletMarker)
- [`WLeafletMapWidgetMarker`](#WLeafletMapWidgetMarker)

---

### ErrorCorrectionLevel {#ErrorCorrectionLevel}

*Inherits:* `enum.Enum`

QR-code error-correction strength. Higher levels can survive
more damage to the printed code but encode less data per pixel.

### WQrCode {#WQrCode}

*Inherits:* `WInteractWidget`

A painted QR code. Encodes a text message as a 2D barcode and
renders it as a vector image — scales cleanly to any size.

    qr = container.add_widget(wt.WQrCode('https://example.com', 4))
    qr.brush = wt.WBrush(wt.WColor(0, 64, 128))

If the message is too long for the configured error-correction
level, the `error` flag turns True — drop to a lower ECL or
shorten the input.

**Constructors**

- `__init__(self) -> None`
  Construct an empty QR code. Set `message` and `square_size`
  before adding to a container.

- `__init__(self, message: str, square_size: float) -> None`
  Construct encoding `message`, with each module rendered at
  `square_size` pixels and the default error-correction level.

- `__init__(self, message: str, ecl: ErrorCorrectionLevel, square_size: float) -> None`
  Construct with text, error-correction level, and the size in pixels of each QR-code square.

**Properties**

- `message: str` *(read/write)*
  The text encoded. Mutating triggers a re-paint.

- `square_size: float` *(read/write)*
  Side length in pixels of each QR-code module (the black/white
  squares). Larger values make a bigger, easier-to-scan code.

- `brush: WBrush` *(read/write)*
  Brush used to paint the QR squares (default black solid). Tint with a colored brush; the background stays transparent.

- `error: bool` *(read-only)*
  True if the encoder couldn't fit the message at the configured ECL — try Low or shorten the message.

**Methods**

- `set_error_correction_level(self, ecl: ErrorCorrectionLevel) -> None`
  Replace the active error-correction level. Triggers a
  re-encode and re-paint.

- `update(self) -> None`
  Force a re-paint. Normally unnecessary — assignments to
  `message` / `brush` / `square_size` re-paint automatically.

### GoogleMapsVersion {#GoogleMapsVersion}

*Inherits:* `enum.Enum`

Google Maps JavaScript API version to load.

### MapTypeControl {#MapTypeControl}

*Inherits:* `enum.Enum`

Style of the map-type selector (roadmap / satellite / hybrid /
terrain switch) rendered over the Google Map.

### GoogleMapCoordinate {#GoogleMapCoordinate}

A latitude/longitude pair, used as positions/centres for
WGoogleMap operations. Plain value type — copy freely.

**Constructors**

- `__init__(self) -> None`
  Construct (0, 0) — the null island.

- `__init__(self, latitude: float, longitude: float) -> None`
  Construct from explicit latitude and longitude in decimal
  degrees (positive N/E, negative S/W).

**Properties**

- `latitude: float` *(read/write)*
  Latitude in decimal degrees.

- `longitude: float` *(read/write)*
  Longitude in decimal degrees.

**Methods**

- `distance_to(self, other: GoogleMapCoordinate) -> float`
  Great-circle distance to `other` in kilometres (despite Wt's docs naming metres).

**Dunder methods**

- `__repr__(self) -> str`

### WGoogleMap {#WGoogleMap}

*Inherits:* `WWidget`

Embedded Google Maps widget. Renders an interactive map served
by the Google Maps JS API and lets server-side Python add markers,
polylines, circles, and info windows.

    gmap = container.add_widget(wt.WGoogleMap(wt.GoogleMapsVersion.v3))
    gmap.set_center(wt.WGoogleMap.Coordinate(37.7749, -122.4194), 12)
    gmap.add_marker(wt.WGoogleMap.Coordinate(37.7749, -122.4194))

Requires a Google Maps API key configured server-side via Wt's
config XML (`google_api_key` property). Without it the widget
renders an error pane.

**Constructors**

- `__init__(self, version: GoogleMapsVersion) -> None`
  Construct against the given Google Maps API version.

**Methods**

- `set_center(self, center: GoogleMapCoordinate) -> None`
  Pan the map so `center` is at the viewport centre. Keeps
  the current zoom level.

- `set_center(self, center: GoogleMapCoordinate, zoom: int) -> None`
  Pan to `center` and set the zoom level in one call.

- `pan_to(self, center: GoogleMapCoordinate) -> None`
  Smoothly animate the viewport to `center` (vs. the snap-jump
  of `set_center`).

- `set_zoom(self, level: int) -> None`
  Set the zoom level (integer; ~0 = whole world, ~22 = street
  level depending on the area).

- `zoom_in(self) -> None`
  Increase the zoom level by one.

- `zoom_out(self) -> None`
  Decrease the zoom level by one.

- `save_position(self) -> None`
  Remember the current centre + zoom. Restore with return_to_saved_position.

- `return_to_saved_position(self) -> None`
  Pan/zoom back to whatever was last `save_position`'d.

- `add_marker(self, position: GoogleMapCoordinate) -> None`
  Drop the default Google-Maps pin at `position`.

- `add_icon_marker(self, position: GoogleMapCoordinate, icon_url: str) -> None`
  Marker with a custom icon image at `icon_url`.

- `add_polyline(self, points: Sequence[GoogleMapCoordinate], color: WColor, width: int, opacity: float) -> None`
  All four arguments mandatory — pass wt.WColor(...) and your line width / opacity explicitly.

- `add_circle(self, center: GoogleMapCoordinate, radius_metres: float, stroke_color: WColor, stroke_width: int, fill_color: WColor) -> None`
  Circle of `radius_metres` (a real distance, not pixels) around `center`.

- `clear_overlays(self) -> None`
  Remove every marker, polyline, circle, etc. added so far.

- `open_info_window(self, position: GoogleMapCoordinate, html: str) -> None`
  Show a Google-Maps info window with HTML content.

- `zoom_window(self, top_left: GoogleMapCoordinate, bottom_right: GoogleMapCoordinate) -> None`
  Zoom to fit the bounding box (top_left, bottom_right).

### LeafletMapCoordinate {#LeafletMapCoordinate}

A latitude/longitude pair used as the position for WLeafletMap
items. Plain value type — copy freely.

**Constructors**

- `__init__(self) -> None`
  Construct (0, 0).

- `__init__(self, latitude: float, longitude: float) -> None`
  Construct from explicit decimal-degree latitude and longitude.

**Properties**

- `latitude: float` *(read/write)*
  Latitude in decimal degrees.

- `longitude: float` *(read/write)*
  Longitude in decimal degrees.

**Dunder methods**

- `__repr__(self) -> str`

### WLeafletMap {#WLeafletMap}

*Inherits:* `WWidget`

Interactive map widget powered by leafletjs. Unlike WGoogleMap,
no API key is required — the widget renders tiles fetched from
any compatible tile server (OpenStreetMap, Mapbox, etc.) that
you configure via `add_tile_layer`.

    leaf = container.add_widget(wt.WLeafletMap())
    leaf.add_tile_layer(
        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        tile_options)
    leaf.pan_to(wt.WLeafletMap.Coordinate(51.5074, -0.1278))
    leaf.zoom_level = 12
    leaf.add_marker(wt.WLeafletMap.LeafletMarker(
        wt.WLeafletMap.Coordinate(51.5074, -0.1278)))

Markers, popups, and tooltips are added via add_marker /
add_popup / add_tooltip. Each transfers ownership; the Python
wrapper is re-armed as a non-owning alias so chaining works.

**Constructors**

- `__init__(self) -> None`
  Construct an empty map with default options.

- `__init__(self, options: Json.Object) -> None`
  Construct with Leaflet map options (e.g. centre, zoom). Pass a Json.Object (or use the default ctor + set_options).

**Properties**

- `zoom_level: int` *(read/write)*
  Current zoom level (integer). Assigning sets it; mutating
  client-side via scroll/pinch reports back via
  `zoom_level_changed`.

- `position: LeafletMapCoordinate` *(read-only)*
  Current map centre coordinate. Use `pan_to` to set.

- `zoom_level_changed: JIntSignal` *(read-only)*
  JIntSignal — fires with the new zoom level when the user scrolls or pinches.

**Methods**

- `set_options(self, options: Json.Object) -> None`
  Replace the Leaflet map options. Effective for subsequent
  re-renders.

- `add_tile_layer(self, url_template: str, options: Json.Object) -> None`
  Add a tile source. `url_template` is a Leaflet URL template with {z}/{x}/{y} placeholders (e.g. 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'). `options` is a Json.Object holding Leaflet tile-layer options (maxZoom, attribution, subdomains, …).

- `pan_to(self, center: LeafletMapCoordinate) -> None`
  Smoothly animate the viewport so `center` is at the middle
  of the visible area.

- `add_marker(self, marker: _T_Marker) -> _T_Marker`
  Attach a Marker (LeafletMarker or WidgetMarker) to the map. Ownership transfers; the wrapper is re-armed as a non-owning alias, so chains like `m.add_marker(mkr).add_popup(p)` work.

- `add_popup(self, popup: _T_Popup) -> _T_Popup`
  Attach a standalone Popup to the map (separate from any marker). The popup opens at its configured coordinate.

- `add_tooltip(self, tooltip: _T_Tooltip) -> _T_Tooltip`
  Attach a standalone Tooltip to the map (separate from any
  marker). Ownership transfers; the wrapper is re-armed as a
  non-owning alias.

### WLeafletMapAbstractMapItem {#WLeafletMapAbstractMapItem}

*Inherits:* `WObject`

Abstract base for anything placed on a WLeafletMap — markers,
popups, tooltips. Holds a coordinate and the standard set of
mouse-interaction signals.

**Properties**

- `position: LeafletMapCoordinate` *(read-only)*
  The item's current coordinate.

- `clicked: Signal` *(read-only)*
  Signal[] — user clicked the item. For overlay items (Popup, Tooltip), `interactive` must be set in options.

- `double_clicked: Signal` *(read-only)*
  Signal[] — user double-clicked the item.

- `mouse_went_down: Signal` *(read-only)*
  Signal[] — mouse button pressed over the item.

- `mouse_went_up: Signal` *(read-only)*
  Signal[] — mouse button released over the item.

- `mouse_went_over: Signal` *(read-only)*
  Signal[] — cursor entered the item.

- `mouse_went_out: Signal` *(read-only)*
  Signal[] — cursor left the item.

**Methods**

- `move(self, pos: LeafletMapCoordinate) -> None`
  Move the item to a new coordinate. Triggers a re-render if the item is already attached to a map.

### WLeafletMapAbstractOverlayItem {#WLeafletMapAbstractOverlayItem}

*Inherits:* `WLeafletMapAbstractMapItem`

Common base for Popup and Tooltip — overlay items that hold a
content widget and can be opened/closed.

**Properties**

- `is_open: bool` *(read-only)*
  True if the overlay is currently visible.

- `opened_signal: Signal` *(read-only)*
  Signal[] — fires when the overlay transitions to open.

- `closed_signal: Signal` *(read-only)*
  Signal[] — fires when the overlay transitions to closed.

**Methods**

- `set_options(self, options: Json.Object) -> None`
  Leaflet-side options for this overlay (autoClose, closeOnClick, etc.). See https://leafletjs.com/reference.html for the full list.

- `set_content(self, content: WWidget) -> None`
  Replace the overlay's content with a widget. Ownership transfers; the Python wrapper is re-armed as a non-owning alias.

- `set_content_text(self, text: str) -> None`
  Convenience: set content to a WText wrapping the given string. Same effect as set_content(WText(text)).

- `open(self) -> None`
  Show the overlay programmatically.

- `close(self) -> None`
  Hide the overlay programmatically.

- `toggle(self) -> None`
  Flip between open and closed.

### WLeafletMapPopup {#WLeafletMapPopup}

*Inherits:* `WLeafletMapAbstractOverlayItem`

Floating overlay attached to a coordinate. Typically opens on
marker click (when added via Marker.add_popup) or programmatically
via open(). Content is either a WText shortcut or any widget.

**Constructors**

- `__init__(self, pos: LeafletMapCoordinate) -> None`
  Construct an empty popup anchored at `pos`. Set content
  later via set_content / set_content_text.

- `__init__(self, content: str) -> None`
  Shortcut: popup whose content is a WText wrapping the given string.

- `__init__(self, pos: LeafletMapCoordinate, content: str) -> None`
  Construct anchored at `pos` with the given text as content.

- `__init__(self, pos: LeafletMapCoordinate, content: WWidget) -> None`
  Popup at `pos` with a widget content. Ownership of `content` transfers.

### WLeafletMapTooltip {#WLeafletMapTooltip}

*Inherits:* `WLeafletMapAbstractOverlayItem`

Floating label attached to a coordinate. Like Popup but
typically shown on hover instead of click. Same content API
(string-shortcut or arbitrary widget).

**Constructors**

- `__init__(self, pos: LeafletMapCoordinate) -> None`
  Construct an empty tooltip anchored at `pos`.

- `__init__(self, content: str) -> None`
  Shortcut: tooltip whose content is a WText wrapping the
  given string.

- `__init__(self, pos: LeafletMapCoordinate, content: str) -> None`
  Construct anchored at `pos` with the given text as content.

- `__init__(self, pos: LeafletMapCoordinate, content: WWidget) -> None`
  Tooltip at `pos` with a widget content. Ownership of
  `content` transfers.

### WLeafletMapMarker {#WLeafletMapMarker}

*Inherits:* `WLeafletMapAbstractMapItem`

Abstract base for map markers. Carries an optional Popup and
Tooltip; concrete subclasses (LeafletMarker, WidgetMarker)
decide what's actually rendered at the marker's position.

**Properties**

- `popup: WLeafletMapPopup` *(read-only)*
  Current popup, or None if none is attached.

- `tooltip: WLeafletMapTooltip` *(read-only)*
  Current tooltip, or None if none is attached.

**Methods**

- `add_popup(self, popup: _T_Popup) -> _T_Popup`
  Attach a popup that opens when the marker is clicked. Replaces any previously-added popup on this marker.

- `remove_popup(self) -> None`
  Detach the currently-attached popup, if any.

- `add_tooltip(self, tooltip: _T_Tooltip) -> _T_Tooltip`
  Attach a tooltip that appears on hover. Replaces any previously-added tooltip.

- `remove_tooltip(self) -> None`
  Detach the currently-attached tooltip, if any.

### WLeafletMapLeafletMarker {#WLeafletMapLeafletMarker}

*Inherits:* `WLeafletMapMarker`

Marker rendered as the default Leaflet pin. The standard
round-headed marker drop you get from leafletjs by default.

**Constructors**

- `__init__(self, pos: LeafletMapCoordinate) -> None`
  Construct the standard Leaflet pin marker.

**Methods**

- `set_options(self, options: Json.Object) -> None`
  Leaflet marker options (icon, draggable, riseOnHover, …). See https://leafletjs.com/reference.html#marker.

### WLeafletMapWidgetMarker {#WLeafletMapWidgetMarker}

*Inherits:* `WLeafletMapMarker`

Marker rendered as an arbitrary Wt widget — pin yourself a
WImage, a WText, a WContainerWidget with custom HTML, etc.
Useful when the default Leaflet pin isn't enough.

**Constructors**

- `__init__(self, pos: LeafletMapCoordinate, widget: WWidget) -> None`
  Place an arbitrary Wt widget at `pos` on the map. Ownership of the widget transfers.

**Properties**

- `widget: WWidget` *(read-only)*
  The widget rendered at the marker's position.

**Methods**

- `set_anchor_point(self, x: float, y: float) -> None`
  Anchor (the 'tip' of the marker relative to its top-left corner) in pixels. Negative x = horizontal center; negative y = vertical center. Default is centred both ways.
