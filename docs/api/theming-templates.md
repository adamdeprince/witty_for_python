# Theming & Templates

> The pluggable WTheme system and the WTemplate engine for string-templated layouts with slot binding.

**Classes in this section:**

- [`TextFormat`](#TextFormat)
- [`TemplateWidgetIdMode`](#TemplateWidgetIdMode)
- [`WTemplate`](#WTemplate)
- [`WTheme`](#WTheme)
- [`WCssTheme`](#WCssTheme)
- [`WBootstrap2Theme`](#WBootstrap2Theme)
- [`WBootstrap3Theme`](#WBootstrap3Theme)
- [`WBootstrap5Theme`](#WBootstrap5Theme)

---

### TextFormat {#TextFormat}

*Inherits:* `enum.Enum`

How a piece of text should be interpreted when rendered.
`XHTML` is sanitised XHTML — tags allowed but checked for
common XSS vectors. `UnsafeXHTML` is raw, unfiltered XHTML —
use only with content you trust completely. `Plain` escapes
everything so the string appears verbatim in the page.

### TemplateWidgetIdMode {#TemplateWidgetIdMode}

*Inherits:* `enum.Enum`

Policy WTemplate uses when stamping ids on bound widgets.
`None_` leaves the widget's id alone; `SetObjectName` sets the
Wt object name to the bind var; `SetId` sets the DOM `id`
attribute to it.

### WTemplate {#WTemplate}

*Inherits:* `WInteractWidget`

Renders an XHTML template with `${var}` placeholders that get
replaced by bound strings, integers, or live child widgets.
Separates layout (the template text) from behavior (the bound
widgets and their signal handlers).

    tpl = container.add_widget(wt.WTemplate(
        '<div>${greeting}, ${name}! ${ok-button}</div>'))
    tpl.bind_string('greeting', 'Hello')
    tpl.bind_string('name', user_name)
    tpl.bind_widget('ok-button', wt.WPushButton('OK')
    ).clicked.connect(submit)

Templates also support conditional blocks: a region wrapped in
`${<flag>}…${</flag>}` renders only when `set_condition('flag',
True)` has been called.

**Constructors**

- `__init__(self) -> None`
  Construct an empty template. Set `template_text` later.

- `__init__(self, text: str) -> None`
  Construct a template using `text` as the source markup.

**Properties**

- `template_text: str` *(read/write)*
  The template source. Assigning re-renders on the next
  round-trip, preserving any current bindings.

- `widget_id_mode: TemplateWidgetIdMode` *(read/write)*
  Controls how bound widgets pick up the bind variable as an
  id. See TemplateWidgetIdMode.

**Methods**

- `set_template_text(self, text: str, format: TextFormat = TextFormat.XHTML) -> None`
  Replace the template source. `format` controls how `text`
  itself is sanitised (the default XHTML strips XSS-prone
  constructs from the template body).

- `bind_widget(self, var_name: str, widget: _T_Widget) -> _T_Widget`
  Substitute `${var_name}` in the template with a live
  `widget`. Takes ownership and re-arms the Python wrapper
  as a non-owning alias; returns the same wrapper for fluent
  chaining:

      tpl.bind_widget('ok', wt.WPushButton('OK')).clicked.connect(go)

- `bind_string(self, var_name: str, value: str, format: TextFormat = TextFormat.XHTML) -> None`
  Substitute `${var_name}` with `value`, rendered according
  to `format`. Use this for static text content; pick
  `bind_widget` instead when you need a widget to wire
  signals to.

- `bind_int(self, var_name: str, value: int) -> None`
  Substitute `${var_name}` with the decimal rendering of
  `value`.

- `bind_empty(self, var_name: str) -> None`
  Bind `${var_name}` to nothing — useful for clearing a
  placeholder without removing the surrounding template
  markup.

- `resolve_widget(self, var_name: str) -> WWidget`
  Return a non-owning handle to the widget currently bound
  to `var_name`, or None if no widget is bound there.

- `clear(self) -> None`
  Drop every binding and condition. The template source
  stays as-is.

- `refresh(self) -> None`
  Force a re-render. Normally called automatically after
  bindings change; useful when external state the template
  depends on has shifted.

- `set_condition(self, name: str, value: bool) -> None`
  Set the value of a named condition flag. Regions wrapped
  in `${<name>}…${</name>}` render only while the flag is
  True.

- `condition_value(self, name: str) -> bool`
  Read the current value of a named condition flag.

### WTheme {#WTheme}

*Inherits:* `WObject`

Abstract base for everything assignable to `WApplication.theme`.
A theme decides the CSS classes Wt's widgets receive, what extra
stylesheets/scripts the application pulls in, and how form-state
decorations (disabled, focus, validation) render.

Not directly instantiable from Python — pick one of the bundled
subclasses (WCssTheme, WBootstrap5Theme, WBootstrap3Theme,
WBootstrap2Theme) and hand it to the application:

    app.theme = wt.WBootstrap5Theme()

**Methods**

- `name(self) -> str`
  Theme identifier — e.g. 'polished', 'bootstrap5'.

- `resources_url(self) -> str`
  URL prefix where the theme's CSS / asset files are served from.

### WCssTheme {#WCssTheme}

*Inherits:* `WTheme`

A plain-CSS theme keyed by name. The name selects which CSS
bundle Wt loads from `<resources>/themes/<name>/wt.css`. Two
names — `'default'` and `'polished'` — refer to the bundled
stylesheets that ship with Wt.

    app.theme = wt.WCssTheme('polished')

For richer presets, use one of the Bootstrap themes.

**Constructors**

- `__init__(self, name: str) -> None`
  Construct a plain-CSS theme — pass 'default' or 'polished' to use Wt's built-in styles, or any name that matches a CSS file you serve at <resources>/themes/<name>/wt.css.

### WBootstrap2Theme {#WBootstrap2Theme}

*Inherits:* `WTheme`

Legacy Bootstrap 2 visual style. Kept around for applications
that haven't migrated to a newer Bootstrap; pick WBootstrap5Theme
for new code.

**Constructors**

- `__init__(self) -> None`
  Bootstrap 2 theme. Useful for older apps; new code should prefer WBootstrap5Theme.

### WBootstrap3Theme {#WBootstrap3Theme}

*Inherits:* `WTheme`

Bootstrap 3 visual style. Useful when the surrounding ecosystem
(plugins, third-party widgets) is still on Bootstrap 3; new code
should prefer WBootstrap5Theme.

**Constructors**

- `__init__(self) -> None`
  Bootstrap 3 theme. Useful for apps tracking the Bootstrap-3 ecosystem; new code should prefer WBootstrap5Theme.

### WBootstrap5Theme {#WBootstrap5Theme}

*Inherits:* `WTheme`

Bootstrap 5 visual style. The most current of the bundled themes;
preferred for new applications. Bootstrap's CSS and JS are served
automatically from Wt's bundled resources tree — no extra setup.

    app.theme = wt.WBootstrap5Theme()

**Constructors**

- `__init__(self) -> None`
  Construct a Bootstrap 5 theme. Attach it to an application with `app.theme = wt.WBootstrap5Theme()`.
