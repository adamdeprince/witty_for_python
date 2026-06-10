# Chrome — Icons, Toolbars, Notifications

> Auxiliary UI: badges, toolbars, popup menus, icons, navigation bars, notifications, loading indicators.

**Classes in this section:**

- [`AlignmentFlag`](#AlignmentFlag)
- [`WPoint`](#WPoint)
- [`WIcon`](#WIcon)
- [`IconType`](#IconType)
- [`WIconPair`](#WIconPair)
- [`WPopupWidget`](#WPopupWidget)
- [`WPopupMenu`](#WPopupMenu)
- [`WBadge`](#WBadge)
- [`WToolBar`](#WToolBar)
- [`WSplitButton`](#WSplitButton)
- [`WNavigationBar`](#WNavigationBar)
- [`WLoadingIndicator`](#WLoadingIndicator)
- [`WDefaultLoadingIndicator`](#WDefaultLoadingIndicator)
- [`WOverlayLoadingIndicator`](#WOverlayLoadingIndicator)
- [`NotificationPermission`](#NotificationPermission)
- [`WNotification`](#WNotification)

---

### AlignmentFlag {#AlignmentFlag}

*Inherits:* `enum.IntEnum`

Bit flags for positioning items inside containers that support
left/right justification (WNavigationBar, WToolBar) or horizontal/
vertical alignment (WBoxLayout, WGridLayout). The arithmetic trait
lets the values be OR'd together where Wt accepts a combined flag
set.

### WPoint {#WPoint}

Integer (x, y) coordinate pair in page-relative pixels.
Used as the position argument to `WPopupMenu.popup(point)`.

    menu.popup(wt.WPoint(120, 80))

**Constructors**

- `__init__(self) -> None`
  Construct a point at the origin (0, 0).

- `__init__(self, x: int, y: int) -> None`
  Construct a point at (`x`, `y`).

**Properties**

- `x: int` *(read/write)*
  Horizontal coordinate in pixels.

- `y: int` *(read/write)*
  Vertical coordinate in pixels.

**Dunder methods**

- `__repr__(self) -> str`

### WIcon {#WIcon}

*Inherits:* `WInteractWidget`

A Font Awesome icon rendered inline. Inherits WInteractWidget so
`clicked` and the other input signals work without further setup.

    container.add_widget(wt.WIcon('envelope')).clicked.connect(open_inbox)

The icon name is looked up in the bundled Font Awesome stylesheet,
which is added to the page lazily on first WIcon construction (or
explicitly via `load_icon_font`).

**Constructors**

- `__init__(self) -> None`
  Construct with no icon — set `name` later.

- `__init__(self, name: str) -> None`
  Construct with a Font Awesome icon name (e.g. 'play', 'gear').

**Properties**

- `name: str` *(read/write)*
  The Font Awesome icon name. Assigning swaps the rendered
  glyph on the next round-trip.

- `size: float` *(read/write)*
  Multiplier on the default icon size. 1.0 = unchanged; 2.0 = doubled.

**Methods**

- `load_icon_font() -> None`
  Add Font Awesome's CSS stylesheet to the application. Called automatically the first time a WIcon is constructed; expose it here for explicit early-load.

### IconType {#IconType}

*Inherits:* `enum.Enum`

Tells WIconPair how to interpret its two icon strings.

### WIconPair {#WIconPair}

*Inherits:* `WWidget`

Two icons displayed one at a time, with optional click-to-toggle
behavior. Useful for expand/collapse indicators, on/off lamps,
anywhere a small bistable visual cue is wanted.

    pair = container.add_widget(
        wt.WIconPair('plus-square', 'minus-square'))
    pair.set_icons_type(wt.IconType.IconName)
    pair.icon1_clicked.connect(expand)
    pair.icon2_clicked.connect(collapse)

**Constructors**

- `__init__(self, icon1: str, icon2: str, click_is_switch: bool = True) -> None`
  Two icon strings (URLs or Font-Awesome names). When `click_is_switch` is True (default), clicking either icon toggles the visible state.

**Properties**

- `state: int` *(read/write)*
  Active icon: 0 → icon1, 1 → icon2.

- `icon1_clicked: MouseEventSignal` *(read-only)*
  MouseEventSignal — clicks while icon1 is visible.

- `icon2_clicked: MouseEventSignal` *(read-only)*
  MouseEventSignal — clicks while icon2 is visible.

**Methods**

- `show_icon1(self) -> None`
  Equivalent to `state = 0`.

- `show_icon2(self) -> None`
  Equivalent to `state = 1`.

- `set_icon1_type(self, type: IconType) -> None`
  Set whether icon1's string is a URL or a Font Awesome name.

- `set_icon2_type(self, type: IconType) -> None`
  Set whether icon2's string is a URL or a Font Awesome name.

- `set_icons_type(self, type: IconType) -> None`
  Shortcut for setting both icons to the same IconType.

### WPopupWidget {#WPopupWidget}

*Inherits:* `WWidget`

A floating overlay that wraps an arbitrary widget. Anchors to
another widget in the page and pops up over the surrounding
content — useful for custom tooltips, detail callouts, or any
content panel that should appear next to a trigger.

    info = wt.WText('More details here.')
    popup = wt.WPopupWidget(info)
    popup.set_anchor_widget(trigger)
    popup.transient = True

Different from WPopupMenu (which is a menu of selectable items).

**Constructors**

- `__init__(self, contents: WWidget) -> None`
  Construct with the inner widget shown in the popup. Ownership transfers; the contents widget's Python wrapper becomes non-owning.

**Properties**

- `transient: bool` *(read/write)*
  When True, the popup auto-hides on outside click or focus loss.

- `hidden_signal: Signal` *(read-only)*
  Signal[] — fires when the popup transitions to hidden via a client-side event (not via Python `hidden=True`).

- `shown_signal: Signal` *(read-only)*
  Signal[] — fires when the popup transitions to shown.

**Methods**

- `set_anchor_widget(self, anchor: WWidget) -> None`
  Position the popup relative to `anchor` whenever it's shown.

- `set_transient(self, transient: bool, auto_hide_delay_ms: int = 0) -> None`
  Variant of the `transient` setter that also sets the grace period before auto-hide fires after the mouse leaves.

### WPopupMenu {#WPopupMenu}

*Inherits:* `WMenu`

Floating menu that appears at a screen location on demand.
Inherits the full WMenu surface (add_item, etc.) so building
entries works the same; what's added is the ability to summon
the menu at a point, at a mouse event, or anchored to a widget.

    menu = wt.WPopupMenu()
    menu.add_item('Cut')
    menu.add_item('Copy')
    container.add_widget(wt.WPushButton('Edit')).clicked.connect(
        lambda e: menu.popup(e))
    menu.triggered.connect(lambda item: handle(item.text))

Pair with `set_button(btn)` for the typical menu-button UX, or
call `popup(...)` yourself from a slot. With `hide_on_select`
left at its default of True, `triggered` is the signal you watch
for to know the user picked something.

**Constructors**

- `__init__(self) -> None`
  Construct a standalone popup menu with no items. Use the
  inherited `add_item` to populate it.

**Properties**

- `hide_on_select: bool` *(read/write)*
  When True (default), picking an item hides the popup.

- `about_to_hide: Signal` *(read-only)*
  Signal[] — fires once when the popup is about to close, regardless of how (selection, click-outside, auto-hide). Use this for cleanup.

- `triggered: MenuItemSignal` *(read-only)*
  MenuItemSignal — fires when the user picks an item. Unlike WMenu.item_selected, this fires only for interactive selection (programmatic .select() is silent).

**Methods**

- `popup(self, point: WPoint) -> None`
  Show the menu at an absolute screen coordinate (page-relative pixels).

- `popup(self, event: WMouseEvent) -> None`
  Show the menu at the location of a mouse event — convenient from a clicked-handler slot.

- `popup(self, location: WWidget, orientation: Orientation = Orientation.Vertical) -> None`
  Show the menu anchored to a widget; orientation controls drop-direction.

- `set_button(self, button: WInteractWidget) -> None`
  Wire `button.clicked` to popup() so the menu opens when the button is clicked. The button is just associated, not owned.

- `set_auto_hide(self, enabled: bool, auto_hide_delay_ms: int = 0) -> None`
  When True, the popup hides itself after the mouse leaves it; `auto_hide_delay_ms` adds a grace period.

### WBadge {#WBadge}

*Inherits:* `WText`

Small inline label, typically appended to another widget for
counts or status pills (e.g. '12 unread'). Inherits WText, so
set the displayed value via the `text` property.

    btn = container.add_widget(wt.WPushButton('Inbox'))
    btn.add_widget(wt.WBadge('12'))

**Constructors**

- `__init__(self) -> None`
  Construct an empty badge with no caption.

- `__init__(self, text: str) -> None`
  Construct a badge displaying `text`.

**Properties**

- `use_default_style: bool` *(read/write)*
  When True (default), Wt applies its theme's badge CSS class. Disable to style purely via your own classes/CSS.

### WToolBar {#WToolBar}

*Inherits:* `WWidget`

A row (or column) of buttons with optional separators between
groups. Add buttons via `add_button`; mix in arbitrary widgets
with `add_widget` for non-button controls.

    bar = container.add_widget(wt.WToolBar())
    bar.add_button(wt.WPushButton('Save')).clicked.connect(save)
    bar.add_separator()
    bar.add_button(wt.WPushButton('Quit')).clicked.connect(app.quit)

**Constructors**

- `__init__(self) -> None`
  Construct an empty toolbar with horizontal orientation.

**Properties**

- `compact: bool` *(read/write)*
  When True, buttons are visually grouped (no internal margins).

- `count: int` *(read-only)*
  Number of items (buttons or widgets) currently in the toolbar.

**Methods**

- `set_orientation(self, orientation: Orientation) -> None`
  Horizontal or Vertical layout for the buttons. Write-only on the C++ side; no getter is exposed by Wt.

- `add_button(self, button: _T_Button, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Button`
  Transfer ownership of `button` to the toolbar (a WPushButton
  or WSplitButton) and return the same Python wrapper, re-armed
  as a non-owning alias for chaining. `alignment` controls
  left/right placement when the theme supports it.

      bar.add_button(wt.WPushButton('Help'),
                     wt.AlignmentFlag.Right).clicked.connect(open_help)

- `add_widget(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget`
  Add an arbitrary widget (not necessarily a button) to the
  toolbar at the given alignment. Same ownership-transfer +
  re-arm pattern as `add_button`.

- `add_separator(self) -> None`
  Add a visual divider between groups of items.

### WSplitButton {#WSplitButton}

*Inherits:* `WWidget`

A primary action button with a small chevron next to it that
opens a dropdown menu — the typical 'Save / Save As…' split
button found in toolbars. Build a WPopupMenu, attach it via
`set_menu`, then wire `action_button.clicked` for the default
action.

    sb = bar.add_button(wt.WSplitButton('Save'))
    sb.action_button.clicked.connect(save_default)
    menu = wt.WPopupMenu()
    menu.add_item('Save As…')
    menu.add_item('Save All')
    sb.set_menu(menu)

**Constructors**

- `__init__(self) -> None`
  Construct an unlabelled split button with no menu attached.

- `__init__(self, label: str) -> None`
  Construct a split button captioned `label` with no menu
  attached. Use `set_menu` to wire the dropdown.

**Properties**

- `action_button: WPushButton` *(read-only)*
  The primary (left) button — connect `clicked` for the default action.

- `drop_down_button: WPushButton` *(read-only)*
  The chevron (right) button — clicking it opens the attached WPopupMenu.

**Methods**

- `set_menu(self, menu: WPopupMenu) -> None`
  Attach a WPopupMenu as the dropdown. Ownership transfers to the split button; the Python wrapper becomes a non-owning alias of the menu the split button now holds.

### WNavigationBar {#WNavigationBar}

*Inherits:* `WTemplate`

A page-top navigation bar in the Bootstrap idiom: brand on the
left, menus and form fields stacked horizontally, optional
search box. Collapses into a hamburger menu on narrow viewports
when `set_responsive(True)` is set.

    nav = app.root.add_widget(wt.WNavigationBar())
    nav.set_title('My App', wt.WLink('/'))
    nav.set_responsive(True)
    menu = wt.WMenu()
    menu.add_item('Home')
    menu.add_item('About')
    nav.add_menu(menu)

**Constructors**

- `__init__(self) -> None`
  Construct an empty navigation bar. Use `set_title` /
  `add_menu` / `add_search` to populate it.

**Methods**

- `set_title(self, title: str, link: WLink = ...) -> None`
  Set the brand/title shown at the left of the nav bar. Optionally wraps it in a link.

- `set_responsive(self, responsive: bool) -> None`
  When True, collapses the contents into a hamburger menu on narrow viewports (Bootstrap responsive behaviour). Wt has no getter for this — the flag is write-only on the C++ side.

- `add_menu(self, menu: _T_Menu, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Menu`
  Embed a WMenu in the nav bar. Ownership transfers; the
  Python wrapper is re-armed as a non-owning alias of the menu
  the bar now holds.

- `add_form_field(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget`
  Embed a form field (e.g. a small WLineEdit for a search bar). Distinct from the standalone add_search variant only in styling.

- `add_search(self, field: _T_LineEdit, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_LineEdit`
  Add a styled search box (a WLineEdit) to the nav bar.
  Functionally similar to `add_form_field` but themed as a
  search input.

- `add_widget(self, widget: _T_Widget, alignment: AlignmentFlag = AlignmentFlag.Left) -> _T_Widget`
  Add an arbitrary widget to the nav bar at the given
  alignment. Same ownership-transfer + re-arm pattern as
  `add_menu`.

### WLoadingIndicator {#WLoadingIndicator}

*Inherits:* `WWidget`

Abstract base for the spinner / banner shown during a server
round-trip. Concrete subclasses (WDefaultLoadingIndicator,
WOverlayLoadingIndicator) provide the visible UI; plug one into
the application to control the look of the load state.

**Methods**

- `set_message(self, text: str) -> None`
  Replace the loading message shown to the user.

### WDefaultLoadingIndicator {#WDefaultLoadingIndicator}

*Inherits:* `WLoadingIndicator`

The default unobtrusive loading indicator — a small fixed-
position text label in the corner of the page.

**Constructors**

- `__init__(self) -> None`
  Construct the default text-label indicator.

### WOverlayLoadingIndicator {#WOverlayLoadingIndicator}

*Inherits:* `WLoadingIndicator`

A more aggressive loading indicator — dims the entire page with
a translucent overlay and a centered banner during requests.
Useful when the user shouldn't be interacting with stale content
while the server is busy.

**Constructors**

- `__init__(self) -> None`
  Construct the overlay-style indicator.

### NotificationPermission {#NotificationPermission}

*Inherits:* `enum.Enum`

User-granted permission state for the browser Notification API.

### WNotification {#WNotification}

*Inherits:* `WObject`

Browser Notification API wrapper — produces native OS-level
notifications (the toasts the operating system displays outside
the page). Inherits WObject, not a widget, so it's not added to
a container.

    note = wt.WNotification('Build done', 'All tests passed.')
    note.set_icon(wt.WLink('/static/check.png'))
    note.clicked.connect(focus_app)
    note.send()

The browser must have granted notification permission first;
without it `send` fails silently and `error` fires.

**Constructors**

- `__init__(self, title: str = '', body: str = '') -> None`
  Construct a notification with optional title and body. Both
  can be set later via set_title / set_body.

**Properties**

- `silent: bool` *(read/write)*
  When True, the OS suppresses the usual notification sound.

- `require_interaction: bool` *(read/write)*
  When True, the notification stays on screen until the user
  dismisses it instead of auto-fading.

- `clicked: JSignal0` *(read-only)*
  JSignal0 — user clicked on the notification body.

- `closed: JSignal0` *(read-only)*
  JSignal0 — fires when the notification is dismissed,
  either by the user or via `close`.

- `shown: JSignal0` *(read-only)*
  JSignal0 — fires once the OS has accepted and
  displayed the notification.

- `error: JSignal0` *(read-only)*
  JSignal0 — fires when the OS rejects the show request (e.g. permission denied at run time).

**Methods**

- `set_title(self, title: str) -> None`
  Set the notification's heading line.

- `set_body(self, body: str) -> None`
  Set the notification's body text.

- `set_icon(self, icon_link: WLink) -> None`
  Set the small icon shown in the notification (WLink to an
  image URL or resource).

- `set_badge(self, badge_link: WLink) -> None`
  Set the badge image — used on some platforms when the full
  notification can't be shown (e.g. lock screens).

- `send(self) -> None`
  Push the notification to the browser. Permission must be already granted.

- `close(self) -> None`
  Dismiss the notification programmatically.
