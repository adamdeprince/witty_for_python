"""Topic mapping for documentation generators.

Both `build_docs.py` (Markdown / llms.txt) and `build_html.py` (HTML) consume
this. Adjust the groupings here and rerun the generators — nothing else needs
to change.

Topic IDs become file names (`docs/api/<id>.md`), so keep them URL-safe.
Order in TOPICS controls navigation order in both the llms.txt index and the
HTML side nav.

A class appears in exactly one topic. If the same name is used in multiple
modules (e.g. a `Type` enum in `Json` and chart), qualify with the submodule
prefix in the `classes` list (`"Json.Type"`).
"""

from __future__ import annotations

# (module-on-disk) → (qualified-prefix-for-class-keys)
#
# build_docs walks every .pyi listed here, indexes its classes under the
# qualified-prefix namespace, then matches each TOPICS entry's class names
# against that index.
MODULES: list[tuple[str, str]] = [
    ("src/witty_for_python/_witty_for_python/__init__.pyi", ""),
    ("src/witty_for_python/_witty_for_python/chart.pyi",    "chart."),
    ("src/witty_for_python/_witty_for_python/Http.pyi",     "Http."),
    ("src/witty_for_python/_witty_for_python/Json.pyi",     "Json."),
]


TOPICS: list[dict] = [
    {
        "id": "application",
        "title": "Application & Core Types",
        "summary": (
            "The per-session WApplication, the base widget classes every "
            "concrete widget inherits, the threading-aware UpdateLock, and "
            "the WServer entry point."
        ),
        "classes": [
            "WApplication", "WEnvironment", "WObject", "WWidget",
            "WInteractWidget", "WFormWidget", "UpdateLock",
            "WServer", "EntryPointType",
        ],
    },
    {
        "id": "widgets",
        "title": "Basic Widgets",
        "summary": (
            "The everyday building blocks: text spans, buttons, line edits, "
            "checkboxes, hyperlinks, images."
        ),
        "classes": [
            "WText", "WPushButton", "WLineEdit", "WCheckBox",
            "WAnchor", "WImage",
        ],
    },
    {
        "id": "containers-layouts",
        "title": "Containers & Layouts",
        "summary": (
            "Container widgets and the layout managers that arrange their "
            "children — boxes, grids, borders, fit-to-parent."
        ),
        "classes": [
            "WContainerWidget",
            "WLayout", "LayoutDirection", "WBoxLayout",
            "WHBoxLayout", "WVBoxLayout", "WGridLayout",
            "LayoutPosition", "WBorderLayout", "WFitLayout",
        ],
    },
    {
        "id": "forms",
        "title": "Form Widgets",
        "summary": (
            "Input controls beyond the basics: text areas, spin boxes, "
            "sliders, selectors, button groups, progress bars, labels."
        ),
        "classes": [
            "WLabel", "WBreak", "WTextArea",
            "WSpinBox", "WDoubleSpinBox", "WSlider",
            "WComboBox", "WSelectionBox",
            "WRadioButton", "WButtonGroup", "WProgressBar",
            "Orientation", "SelectionMode",
        ],
    },
    {
        "id": "validators",
        "title": "Form Validation",
        "summary": (
            "Validators attached to WFormWidget inputs. Each rejects with a "
            "ValidationResult; the form widget exposes a `validated` signal."
        ),
        "classes": [
            "ValidationState", "ValidationResult", "ValidationResultSignal",
            "WValidator", "WIntValidator", "WDoubleValidator",
            "WLengthValidator", "WRegExpValidator", "WEmailValidator",
            "WStackedValidator",
        ],
    },
    {
        "id": "signals-events",
        "title": "Signals & Events",
        "summary": (
            "Wt's signal/slot machinery, the Connection handle, and the "
            "event payloads carried by DOM-level signals (mouse, key, touch, "
            "gesture, scroll, drag/drop)."
        ),
        "classes": [
            # Connection + arity helpers
            "Connection",
            # Generic signal types
            "Signal", "IntSignal", "BoolSignal", "DoubleSignal", "StringSignal",
            "EventSignal", "MouseEventSignal", "KeyEventSignal",
            "JSignal", "JSignal0", "JIntSignal", "JInt64Signal", "JDoubleSignal",
            "Uint64PairSignal",
            # Event payloads
            "Coordinates", "MouseButton", "KeyboardModifier", "Key",
            "WMouseEvent", "WKeyEvent",
            "Touch", "WTouchEvent", "WGestureEvent",
            "WScrollEvent", "DropEventOriginalEventType", "WDropEvent",
        ],
    },
    {
        "id": "navigation",
        "title": "Navigation, Dialogs & Menus",
        "summary": (
            "Page-flow widgets: stacked pages, menus and tabs, collapsible "
            "panels and group boxes, modal dialogs and message boxes."
        ),
        "classes": [
            "DialogCode", "StandardButton",
            "DialogCodeSignal", "StandardButtonSignal", "MenuItemSignal",
            "WStackedWidget", "WMenuItem", "WMenu", "WTabWidget",
            "WPanel", "WGroupBox", "WDialog", "WMessageBox",
        ],
    },
    {
        "id": "datetime",
        "title": "Dates, Times & Timers",
        "summary": (
            "Date/time input widgets and validators, the calendar picker, "
            "and the WTimer that fires server-side callbacks on a schedule."
        ),
        "classes": [
            "DateSignal", "WDateEdit", "WTimeEdit", "WCalendar",
            "WDateValidator", "WTimeValidator", "WTimer",
        ],
    },
    {
        "id": "modelview",
        "title": "Models, Views & Tables",
        "summary": (
            "Wt's MVC machinery: WStandardItemModel and friends for the "
            "data side, WTableView / WTreeView for the views, proxy models "
            "for sorting and filtering, and the simpler hand-built WTable."
        ),
        "classes": [
            "ItemDataRole", "WModelIndex", "ModelIndexMouseSignal",
            "WAbstractItemModel", "WAbstractListModel", "WStringListModel",
            "WStandardItem", "WStandardItemModel",
            "SelectionBehavior", "SortOrder", "ScrollHint",
            "WAbstractItemView", "WTableView", "WTreeView",
            "WAbstractProxyModel", "WIdentityProxyModel",
            "WReadOnlyProxyModel", "WSortFilterProxyModel",
            "WTableCell", "WTableRow", "WTableColumn", "WTable",
        ],
    },
    {
        "id": "resources-io",
        "title": "Resources & I/O",
        "summary": (
            "Server-mounted resources, hyperlinks, file uploads and the "
            "drag-and-drop file widget. Pair with the Http submodule for "
            "outbound HTTP and the Request/Response handler API."
        ),
        "classes": [
            "ContentDisposition",
            "WResource", "WStreamResource", "WMemoryResource",
            "WFileResource", "CallbackResource", "WLink",
            "UploadedFile", "WFileUpload",
            "FilePickerType",
            "WFileDropWidgetFile", "WFileDropWidgetDirectory",
            "FileSignal", "FileListSignal", "FileSizeSignal",
            "WFileDropWidget",
        ],
    },
    {
        "id": "painting",
        "title": "Painting & Geometry",
        "summary": (
            "WPainter (the 2D drawing surface), the geometry value types it "
            "consumes, the pen/brush/font/gradient palette, and the paint "
            "device backends (SVG, PNG-on-canvas, PDF, measure-only)."
        ),
        "classes": [
            # Universal value types
            "LengthUnit", "WLength",
            "AnimationEffect", "TimingFunction", "WAnimation",
            # Geometry value types
            "WPointF", "WRectF", "WLineF", "WTransform",
            # Painter knobs
            "FontFamily", "FontStyle", "FontVariant",
            "FontWeight", "FontSize", "WFont",
            "GradientStyle", "WGradient", "WShadow",
            "BorderStyle", "BorderWidth", "WBorder",
            "PenStyle", "PenCapStyle", "PenJoinStyle", "WPen",
            "BrushStyle", "WBrush",
            "WPainterPath", "PainterImage",
            # Surface
            "WPainter", "WPaintedWidget", "RenderMethod",
            # Areas (image-map style)
            "WAbstractArea", "WCircleArea", "WRectArea", "WPolygonArea",
            # Devices
            "PaintDeviceFeatureFlag", "WPaintDevice",
            "WVectorImage", "WSvgImage",
            "WCanvasPaintDevice", "WMeasurePaintDevice",
            "WPdfImage",
        ],
    },
    {
        "id": "media",
        "title": "Media",
        "summary": (
            "HTML5 audio and video, the skinned WMediaPlayer, and the "
            "play-once WSound."
        ),
        "classes": [
            "PlayerOption", "MediaPreloadMode",
            "MediaEncoding", "MediaType",
            "MediaPlayerButtonId", "MediaPlayerProgressBarId", "MediaPlayerTextId",
            "WAbstractMedia", "WAudio", "WVideo",
            "WMediaPlayer", "WSound",
        ],
    },
    {
        "id": "richtext-extras",
        "title": "Rich Form Widgets",
        "summary": (
            "Extra form controls beyond the basics: rich-text editor "
            "(TinyMCE-backed), in-place edit, password edit, autocomplete "
            "popup, color picker."
        ),
        "classes": [
            "WColor",
            "WPasswordEdit", "WInPlaceEdit",
            "PopupTrigger",
            "IntFormWidgetSignal", "WSuggestionPopup",
            "Options", "WSuggestionPopup.Options",
            "WColorPicker", "WTextEdit",
        ],
    },
    {
        "id": "theming-templates",
        "title": "Theming & Templates",
        "summary": (
            "The pluggable WTheme system and the WTemplate engine for "
            "string-templated layouts with slot binding."
        ),
        "classes": [
            "TextFormat", "TemplateWidgetIdMode", "WTemplate",
            "WTheme", "WCssTheme",
            "WBootstrap2Theme", "WBootstrap3Theme", "WBootstrap5Theme",
        ],
    },
    {
        "id": "chrome",
        "title": "Chrome — Icons, Toolbars, Notifications",
        "summary": (
            "Auxiliary UI: badges, toolbars, popup menus, icons, navigation "
            "bars, notifications, loading indicators."
        ),
        "classes": [
            "AlignmentFlag", "WPoint",
            "WIcon", "IconType", "WIconPair",
            "WPopupWidget", "WPopupMenu",
            "WBadge", "WToolBar", "WSplitButton", "WNavigationBar",
            "WLoadingIndicator", "WDefaultLoadingIndicator",
            "WOverlayLoadingIndicator",
            "NotificationPermission", "WNotification",
        ],
    },
    {
        "id": "maps",
        "title": "Maps & QR",
        "summary": (
            "Interactive maps (Leaflet, Google Maps) and QR-code rendering."
        ),
        "classes": [
            "ErrorCorrectionLevel", "WQrCode",
            "GoogleMapsVersion", "MapTypeControl",
            "GoogleMapCoordinate", "WGoogleMap",
            "LeafletMapCoordinate", "WLeafletMap",
            "WLeafletMapAbstractMapItem", "WLeafletMapAbstractOverlayItem",
            "WLeafletMapPopup", "WLeafletMapTooltip",
            "WLeafletMapMarker", "WLeafletMapLeafletMarker",
            "WLeafletMapWidgetMarker",
        ],
    },
    {
        "id": "chart",
        "title": "Charts (submodule)",
        "summary": (
            "The `witty_for_python.chart` subsystem — Cartesian and pie "
            "charts driven by a WStandardItemModel data source."
        ),
        "classes": [
            "chart.SeriesType", "chart.MarkerType", "chart.FillRangeType",
            "chart.ChartType", "chart.LegendLocation",
            "chart.AxisScale", "chart.AxisValue", "chart.Axis",
            "chart.LabelOption",
            "chart.WAxis", "chart.WDataSeries", "chart.WAbstractChart",
            "chart.WCartesianChart", "chart.WPieChart",
        ],
    },
    {
        "id": "http",
        "title": "HTTP (submodule)",
        "summary": (
            "The `witty_for_python.Http` subsystem — the Request/Response "
            "pair passed to WResource handlers, and the outbound HTTP "
            "Client/Message types."
        ),
        "classes": [
            "Http.Request", "Http.Response",
            "Http.Method", "Http.Header", "Http.Message",
            "Http.Message.Header",
            "Http.ClientURL", "Http.Client",
        ],
    },
    {
        "id": "json",
        "title": "JSON (submodule)",
        "summary": (
            "Small JSON value model exposed by the `witty_for_python.Json` "
            "subsystem — used by a handful of bindings (e.g. WLeafletMap "
            "options) that take structured JSON config."
        ),
        "classes": [
            "Json.Type", "Json.Object", "Json.Array", "Json.Value",
        ],
    },
]


def all_topic_ids() -> list[str]:
    return [t["id"] for t in TOPICS]


def topic_for_class(qualified_name: str) -> str | None:
    """Return the topic id that owns `qualified_name`, or None if unmapped."""
    for t in TOPICS:
        if qualified_name in t["classes"]:
            return t["id"]
    return None
