# Basic Widgets

> The everyday building blocks: text spans, buttons, line edits, checkboxes, hyperlinks, images.

**Classes in this section:**

- [`WText`](#WText)
- [`WPushButton`](#WPushButton)
- [`WLineEdit`](#WLineEdit)
- [`WCheckBox`](#WCheckBox)
- [`WAnchor`](#WAnchor)
- [`WImage`](#WImage)

---

### WText {#WText}

*Inherits:* `WInteractWidget`

Static text content. Renders a span of XHTML in the page; the
simplest building block for displaying text or inline markup.

    label = container.add_widget(wt.WText('Loading…'))
    label.text = 'Loaded 42 rows.'

Text is interpreted as XHTML by default — passing untrusted
user input is XSS-unsafe. Wrap with HTML escaping before
assigning, or use a future PlainText TextFormat binding.

**Constructors**

- `__init__(self) -> None`
  Construct an empty WText with no content. Set `text` later.

- `__init__(self, text: str) -> None`
  Construct a WText displaying `text` (interpreted as XHTML).

**Properties**

- `text: str` *(read/write)*
  The widget's displayed text (XHTML). Assigning re-renders
  the widget on the next client round-trip; no need to call
  any refresh method.

### WPushButton {#WPushButton}

*Inherits:* `WFormWidget`

A clickable button. Connect to `clicked` for an action button,
or set `link` for navigation (the button renders as a styled
anchor).

    container.add_widget(wt.WPushButton('Save')).clicked.connect(save)

    home = container.add_widget(wt.WPushButton('Home'))
    home.link = wt.WLink('/')

**Constructors**

- `__init__(self) -> None`
  Construct an empty button with no caption.

- `__init__(self, text: str) -> None`
  Construct a button captioned `text`.

**Properties**

- `text: str` *(read/write)*
  The button's caption (XHTML).

- `link: WLink` *(read/write)*
  URL the button navigates to when clicked. Setting a link
  makes the button render as an anchor under the hood; if you
  want pure action behavior, leave `link` unset and connect
  to `clicked` instead.

### WLineEdit {#WLineEdit}

*Inherits:* `WFormWidget`

Single-line text input.

    edit = container.add_widget(wt.WLineEdit())
    edit.placeholder = 'Email…'
    edit.max_length = 64
    container.add_widget(wt.WPushButton('Send')).clicked.connect(
        lambda: send(edit.text))

**Constructors**

- `__init__(self) -> None`
  Construct an empty line edit.

- `__init__(self, text: str) -> None`
  Construct a line edit with initial value `text`.

**Properties**

- `text: str` *(read/write)*
  The current input value. Reads what the user has typed;
  assigning replaces the current contents.

- `placeholder: str` *(read/write)*
  Greyed-out hint shown when the field is empty (the standard
  browser `placeholder` attribute).

- `max_length: int` *(read/write)*
  Maximum number of characters the browser will accept.
  Negative (the default) means no limit. Enforced client-side
  only — re-validate server-side if it matters.

- `text_input: EventSignal` *(read-only)*
  Per-keystroke signal (`EventSignal<>`). Fires as
  the user types, before the change is committed.
  Use `changed` instead for the standard
  blur/Enter-fires-once semantics.

### WCheckBox {#WCheckBox}

*Inherits:* `WFormWidget`

Bistable boolean control with an optional caption.

    container.add_widget(wt.WCheckBox('Subscribe')).on_check.connect(subscribe)

    box = container.add_widget(wt.WCheckBox('Remember me'))
    box.checked = True
    box.on_check.connect(lambda: store('remember', True))
    box.on_uncheck.connect(lambda: store('remember', False))

Inherits all WFormWidget validation/state plumbing — wire to
`set_validator` if the value participates in a form submit.

**Constructors**

- `__init__(self) -> None`
  Construct an unlabelled checkbox in the unchecked state.

- `__init__(self, text: str) -> None`
  Construct a labelled checkbox; `text` renders next to the box.

**Properties**

- `checked: bool` *(read/write)*
  The current boolean state. Assigning programmatically does
  NOT fire `on_check`/`on_uncheck` — those are user-input
  events.

- `on_check: EventSignal` *(read-only)*
  Fires when the user checks the box. No-arg signal.
  Programmatic `checked = True` does not fire it.

- `on_uncheck: EventSignal` *(read-only)*
  Fires when the user unchecks the box. Mirror of `on_check`.

### WAnchor {#WAnchor}

*Inherits:* `WContainerWidget`

A hyperlink. Inherits WContainerWidget so the visible body can
be arbitrary widgets, not just text — wrap an image to make a
clickable banner, etc.

    container.add_widget(wt.WAnchor(wt.WLink('https://example.com'), 'Visit'))

    container.add_widget(wt.WAnchor(wt.WLink('/landing'))).add_widget(
        wt.WImage(wt.WLink('/banner.png'), 'Promo'))

**Constructors**

- `__init__(self) -> None`
  Construct an empty anchor with no link or content.

- `__init__(self, link: WLink) -> None`
  Construct an anchor pointing to `link` with no visible text.
  Useful when the body will be set up via `add_widget`.

- `__init__(self, link: WLink, text: str) -> None`
  Construct an anchor whose visible body is the plain text
  `text` and which targets `link` on click.

**Properties**

- `link: WLink` *(read/write)*
  The hyperlink target. A WLink wraps a URL string, an
  internal-path reference, or a server-side WResource.

### WImage {#WImage}

*Inherits:* `WInteractWidget`

An `<img>` element. The image source can be any WLink — a URL
string, a static resource path, or a dynamically-served
WResource (e.g. a WPdfImage or chart rendered to PNG).

    container.add_widget(
        wt.WImage(wt.WLink('/logo.png'), 'Logo')
    ).clicked.connect(zoom_logo)

    server.add_resource(MyChartResource(), '/chart.png')
    container.add_widget(wt.WImage(wt.WLink('/chart.png'), 'Live chart'))

**Constructors**

- `__init__(self) -> None`
  Construct an empty image with no source.

- `__init__(self, link: WLink) -> None`
  Construct an image sourced from `link` with no alt text.
  Set `alt_text` afterwards for accessibility.

- `__init__(self, link: WLink, alt_text: str) -> None`
  Construct an image sourced from `link` with the given
  alt text (used by screen readers and shown if the image
  fails to load).

**Properties**

- `image_link: WLink` *(read/write)*
  The image source. Assigning swaps the displayed image on
  the next client round-trip.

- `alt_text: str` *(read/write)*
  Text shown if the image fails to load and read aloud by
  screen readers. Set it on any image whose meaning matters.
