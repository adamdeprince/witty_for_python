# Deferred bindings

Inventory of Wt classes / methods that have been deliberately punted
during prior binding work. Each entry says *what* was skipped, *where*
its dependents live in our binding, and *why* the deferral made sense
at the time. Pull-requests welcome — most of these are well-scoped
single-class jobs.

## Painting

Skipped while binding the painting subsystem (see
`ext/bind_painting_types.cpp` + `ext/bind_painting.cpp`).

| Class / method | Why it was skipped | Estimated LOC |
|---|---|---|
| ~~`WGradient`~~ | ✅ Bound (with `WPen.set_gradient` / `WBrush.set_gradient`). | done |
| ~~`WShadow`~~ | ✅ Bound (`WPainter.set_shadow`). | done |
| ~~`WBorder`~~ | ✅ Bound. Note: multi-arg constructors require all args explicit — nanobind has trouble casting `WColor()` value-typed defaults at module init. | done |
| `WMatrix4x4`, `WVector3`, `WVector4` | 3-D types — only `WGLWidget` consumes these. | ~150 |
| `WGLWidget` | Separate WebGL subsystem. | ~200+ |
| `WPainter::Image` + `drawImage()` overloads | Image-drawing nested class. Needs URL + size handling. | ~60 |
| `WPainter::setOpacity` | Declared in some Wt builds but absent in 4.13.x's source. Skip until Wt restores it. | trivial |
| Paint devices (`WCanvasPaintDevice`, `WSvgImage`, `WPdfImage`, `WRasterImage`, `WVectorImage`, `WMeasurePaintDevice`) | Off-screen rendering targets. Useful for charts and PDF export. | ~250 |

## Model / view

Skipped while binding `ext/bind_modelview.cpp` and `ext/bind_modelview_proxy.cpp`.

| Class / method | Why it was skipped | Estimated LOC |
|---|---|---|
| `WBatchEditProxyModel` | Buffered-edit proxy. Niche; needs `cpp17::any` glue for setData. | ~80 |
| `WAggregateProxyModel` | Aggregate-column proxy. Niche; needs nested `Aggregate` struct. | ~80 |
| `WItemSelectionModel` | Selection state object. View widgets already expose select / clear_selection / selection_changed inline, which is enough for most cases. | ~60 |
| `WAbstractItemDelegate`, `WItemDelegate` | Custom cell renderers. Needs trampoline support for Python subclassing. | ~150 |
| `WTree`, `WTreeNode`, `WTreeTable`, `WTreeTableNode` | The older non-model-based tree widgets. Mostly superseded by `WTreeView` over a model. | ~250 |
| `cpp17::any`-typed `data()` / `setData()` on `WAbstractItemModel` | Currently exposed as a string-only convenience via `display_data` / `set_header_data`. Full any-typed access needs a richer marshaller. | ~80 |

## Form widgets

| Class / method | Why it was skipped | Estimated LOC |
|---|---|---|
| `WSuggestionPopup.activated` | Skipped, then bound. ✅ |
| `WTextEdit`'s richer TinyMCE plugin API | We expose set_extra_plugins / set_tool_bar / set_configuration_setting. The deeper customisation surface (`setReadOnly` etc) is inherited from WTextArea. |  |
| `WFileUpload.data_received` / `file_too_large` signals | Skipped initially, then bound after binding the JInt64Signal / Uint64PairSignal types. ✅ |

## Events

| Class / method | Why it was skipped | Estimated LOC |
|---|---|---|
| `WDropEvent::eventType()` (vs `originalEventType`) | The base WEvent::eventType returns a different enum. We bind originalEventType; the base getter remains. | trivial |
| Touch/gesture/scroll-event default constructors | Skipped — these events are constructed by Wt internally; Python receives them via signal slots. | trivial |

## Other

| Class / method | Why it was skipped | Estimated LOC |
|---|---|---|
| `WLength` sweep through existing bindings | We bound `WLength` but most existing `width` / `height` setters still take a bare number. A sweep would let callers pass `WLength('50%')` everywhere. | depends |
| `WCssDecorationStyle`, `WCssStyleSheet` | Cascading-stylesheet helpers. Niche compared to direct `set_style_class` on widgets. | ~80 |
| `WMessageResourceBundle`, `WCombinedLocalizedStrings` | i18n loader. Apps that need translations would want this. | ~60 |
| `WSocketNotifier` | File-descriptor watching. Low-level. | trivial |
| `WFavicon` family (`WUrlFavicon`, `WRasterFavicon`, `WResourceFavicon`, `WFaviconPair`) | Favicon support. Self-contained. | ~80 |
| `WWebSocketConnection`, `WWebSocketResource` | WebSocket primitives. | ~100 |
| ~~`WBootstrap2Theme`, `WBootstrap3Theme`~~ | ✅ Bound. `WBootstrapTheme` (the older, version-configurable wrapper) remains skipped — the version-specific classes cover its use cases. | done |
| `WAbstractSpinBox`, `WAbstractToggleButton` | Abstract bases; concrete subclasses (`WSpinBox`, `WDoubleSpinBox`, `WCheckBox`, `WRadioButton`) are bound. | trivial |
| ~~`WQrCode`~~ | ✅ Bound. | done |
| ~~`WGoogleMap`~~ | ✅ Bound (caveat: needs `google_api_key` config property at server startup). Note: `Coordinate.distance_to` returns kilometres, not metres as the Wt docs claim. | done |
| `WLeafletMap` | Skipped: `addTileLayer` takes a `Wt::Json::Object` and the rich `AbstractMapItem`/`Marker`/`Popup` hierarchy. Binding it cleanly requires first binding `Wt::Json`. | ~250 |
| `WFlashObject` | Deprecated browser tech. Not worth binding. | n/a |
| Custom user types via nanobind trampolines | Python subclassing of `WPaintedWidget` / `WAbstractItemModel` / `WAbstractItemDelegate`. Currently each provides a callback-shim path instead. | per-class |
