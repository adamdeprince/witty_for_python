# API Reference

> Python bindings for the Wt (Web Toolkit) C++ library — write server-side web UIs in widget code.

This reference is grouped by topic. For an LLM-friendly index in [llmstxt.org](https://llmstxt.org/) format, see [llms.txt](llms.txt) (concatenated body in [llms-full.txt](llms-full.txt)).

## Topics

### [Application & Core Types](application.md)

The per-session WApplication, the base widget classes every concrete widget inherits, the threading-aware UpdateLock, and the WServer entry point.

### [Basic Widgets](widgets.md)

The everyday building blocks: text spans, buttons, line edits, checkboxes, hyperlinks, images.

### [Containers & Layouts](containers-layouts.md)

Container widgets and the layout managers that arrange their children — boxes, grids, borders, fit-to-parent.

### [Form Widgets](forms.md)

Input controls beyond the basics: text areas, spin boxes, sliders, selectors, button groups, progress bars, labels.

### [Form Validation](validators.md)

Validators attached to WFormWidget inputs. Each rejects with a ValidationResult; the form widget exposes a `validated` signal.

### [Signals & Events](signals-events.md)

Wt's signal/slot machinery, the Connection handle, and the event payloads carried by DOM-level signals (mouse, key, touch, gesture, scroll, drag/drop).

### [Navigation, Dialogs & Menus](navigation.md)

Page-flow widgets: stacked pages, menus and tabs, collapsible panels and group boxes, modal dialogs and message boxes.

### [Dates, Times & Timers](datetime.md)

Date/time input widgets and validators, the calendar picker, and the WTimer that fires server-side callbacks on a schedule.

### [Models, Views & Tables](modelview.md)

Wt's MVC machinery: WStandardItemModel and friends for the data side, WTableView / WTreeView for the views, proxy models for sorting and filtering, and the simpler hand-built WTable.

### [Resources & I/O](resources-io.md)

Server-mounted resources, hyperlinks, file uploads and the drag-and-drop file widget. Pair with the Http submodule for outbound HTTP and the Request/Response handler API.

### [Painting & Geometry](painting.md)

WPainter (the 2D drawing surface), the geometry value types it consumes, the pen/brush/font/gradient palette, and the paint device backends (SVG, PNG-on-canvas, PDF, measure-only).

### [Media](media.md)

HTML5 audio and video, the skinned WMediaPlayer, and the play-once WSound.

### [Rich Form Widgets](richtext-extras.md)

Extra form controls beyond the basics: rich-text editor (TinyMCE-backed), in-place edit, password edit, autocomplete popup, color picker.

### [Theming & Templates](theming-templates.md)

The pluggable WTheme system and the WTemplate engine for string-templated layouts with slot binding.

### [Chrome — Icons, Toolbars, Notifications](chrome.md)

Auxiliary UI: badges, toolbars, popup menus, icons, navigation bars, notifications, loading indicators.

### [Maps & QR](maps.md)

Interactive maps (Leaflet, Google Maps) and QR-code rendering.

### [Charts (submodule)](chart.md)

The `witty_for_python.chart` subsystem — Cartesian and pie charts driven by a WStandardItemModel data source.

### [HTTP (submodule)](http.md)

The `witty_for_python.Http` subsystem — the Request/Response pair passed to WResource handlers, and the outbound HTTP Client/Message types.

### [JSON (submodule)](json.md)

Small JSON value model exposed by the `witty_for_python.Json` subsystem — used by a handful of bindings (e.g. WLeafletMap options) that take structured JSON config.
