# Navigation, Dialogs & Menus

> Page-flow widgets: stacked pages, menus and tabs, collapsible panels and group boxes, modal dialogs and message boxes.

**Classes in this section:**

- [`DialogCode`](#DialogCode)
- [`StandardButton`](#StandardButton)
- [`DialogCodeSignal`](#DialogCodeSignal)
- [`StandardButtonSignal`](#StandardButtonSignal)
- [`MenuItemSignal`](#MenuItemSignal)
- [`WStackedWidget`](#WStackedWidget)
- [`WMenuItem`](#WMenuItem)
- [`WMenu`](#WMenu)
- [`WTabWidget`](#WTabWidget)
- [`WPanel`](#WPanel)
- [`WGroupBox`](#WGroupBox)
- [`WDialog`](#WDialog)
- [`WMessageBox`](#WMessageBox)

---

### DialogCode {#DialogCode}

*Inherits:* `enum.Enum`

Outcome of a closed WDialog. `Accepted` if `accept()` was
called, `Rejected` if `reject()` was called or the dialog was
dismissed via Escape / close button.

### StandardButton {#StandardButton}

*Inherits:* `enum.IntEnum`

Bit-flag enum identifying the standard buttons a WMessageBox
can show. Combine with `|` to request several at once:

    box.set_standard_buttons(wt.StandardButton.Ok | wt.StandardButton.Cancel)

### DialogCodeSignal {#DialogCodeSignal}

Signal payload type for WDialog's `finished` — fires with a
DialogCode when the dialog closes.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable` to the signal. Returns a Connection;
  call `.disconnect()` on it to stop receiving.

- `disconnect_all_slots(self) -> None`
  Disconnect every Python callback currently bound to this
  signal.

### StandardButtonSignal {#StandardButtonSignal}

Signal payload type for WMessageBox's `button_clicked` — fires
with the StandardButton the user picked.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable` to the signal. Returns a Connection;
  call `.disconnect()` on it to stop receiving.

- `disconnect_all_slots(self) -> None`
  Disconnect every Python callback currently bound to this
  signal.

### MenuItemSignal {#MenuItemSignal}

Signal payload type for WMenu's `item_selected` — fires with
the WMenuItem the user picked.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe `callable` to the signal. Returns a Connection;
  call `.disconnect()` on it to stop receiving.

- `disconnect_all_slots(self) -> None`
  Disconnect every Python callback currently bound to this
  signal.

### WStackedWidget {#WStackedWidget}

*Inherits:* `WContainerWidget`

Container that shows exactly one of its children at a time.
Each child added becomes a `page`; switch via `current_index`
or `set_current_widget`. Pair with WMenu for wizard-style or
tabbed navigation that doesn't use WTabWidget's chrome.

    stack = container.add_widget(wt.WStackedWidget())
    stack.add_widget(wt.WText('First page'))
    stack.add_widget(wt.WText('Second page'))
    stack.current_index = 1

**Constructors**

- `__init__(self) -> None`
  Construct an empty stacked widget.

**Properties**

- `current_index: int` *(read/write)*
  Index of the visible page (0-based). All other children
  are hidden but kept alive.

**Methods**

- `set_current_widget(self, widget: WWidget) -> None`
  Show `widget`, which must already be a child of this
  stack.

### WMenuItem {#WMenuItem}

*Inherits:* `WContainerWidget`

A single entry in a WMenu. Has a label and optionally a
`contents` widget that is shown in the menu's associated stack
when this item is selected. Items can be checkable, closeable,
or link to an internal/external URL.

    menu.add_item(wt.WMenuItem('Inbox', wt.WText('No messages.')))

**Constructors**

- `__init__(self, label: str) -> None`
  Construct a menu item with the given label and no contents
  widget. Useful for menus that only fire `item_selected`.

- `__init__(self, label: str, contents: WWidget) -> None`
  Construct a menu item with both a label and a contents
  widget. When the menu is paired with a WStackedWidget, the
  contents widget is shown in that stack on selection.

**Properties**

- `text: str` *(read/write)*
  The item's label.

- `checkable: bool` *(read/write)*
  Whether the item shows a check mark when selected — turns
  it into a toggleable menu entry.

- `checked: bool` *(read/write)*
  The checked state, for a checkable item.

**Methods**

- `set_link(self, link: WLink) -> None`
  Turn the item into a hyperlink — clicking it navigates to
  the given WLink instead of (or in addition to) emitting
  selection.

- `select(self) -> None`
  Select this item programmatically, as if the user had
  clicked it. Fires `item_selected` on the parent menu.

- `set_selectable(self, selectable: bool) -> None`
  Whether the item responds to clicks. Disable for section
  headers or dividers.

- `set_closeable(self, closeable: bool) -> None`
  Whether the item shows a close button. The user can then
  remove it from the menu by clicking that button.

### WMenu {#WMenu}

*Inherits:* `WWidget`

A list of selectable items (sidebar nav, vertical or horizontal
menu, tab strip…). Pair with a WStackedWidget at construction
time to have the selected item's `contents` show up in the
stack automatically.

    stack = container.add_widget(wt.WStackedWidget())
    menu = container.add_widget(wt.WMenu(stack))
    menu.add_item(wt.WMenuItem('Home', wt.WText('Welcome!')))
    menu.add_item(wt.WMenuItem('About', wt.WText('About us.')))
    menu.item_selected.connect(lambda item: print(item.text))

**Constructors**

- `__init__(self) -> None`
  Construct a menu without an associated content stack.

- `__init__(self, contents_stack: WStackedWidget) -> None`
  Construct a menu wired to the given WStackedWidget — when
  the user picks an item, the corresponding `contents` widget
  is made the visible page of `contents_stack`.

**Properties**

- `item_selected: MenuItemSignal` *(read-only)*
  Fires with the WMenuItem the user selected (a
  MenuItemSignal).

**Methods**

- `add_item(self, label: str) -> WMenuItem`
  Convenience for `add_item(WMenuItem(label))`. Returns a
  non-owning handle to the freshly-constructed item.

- `add_item(self, item: _T_MenuItem) -> _T_MenuItem`
  Transfer ownership of `item` to the menu and return the
  same Python wrapper, re-armed as a non-owning alias.

- `add_items(self, items: list[_T_MenuItem]) -> list[_T_MenuItem]`
  Bulk version of the widget-taking `add_item`. Returns the
  same wrappers, each re-armed as a non-owning alias.

- `add_items(self, labels: Sequence[str]) -> None`
  Bulk version of the string-taking `add_item`. Wraps each
  label in a fresh WMenuItem.

- `select(self, index: int) -> None`
  Programmatically select the item at position `index`.
  Fires `item_selected`.

- `current_item(self) -> WMenuItem`
  Return a non-owning handle to the currently-selected item,
  or None if nothing is selected.

### WTabWidget {#WTabWidget}

*Inherits:* `WWidget`

Tab strip on top of a stacked content area. Each `add_tab`
registers one tab whose contents are the widget you pass.

    tabs = container.add_widget(wt.WTabWidget())
    tabs.add_tab(wt.WText('General settings.'), 'General')
    tabs.add_tab(wt.WText('Account settings.'), 'Account')
    tabs.current_changed.connect(lambda i: print('on tab', i))

**Constructors**

- `__init__(self) -> None`
  Construct an empty tab widget.

**Properties**

- `count: int` *(read-only)*
  Number of tabs currently in the widget.

- `current_index: int` *(read/write)*
  Index of the visible tab.

- `current_changed: IntSignal` *(read-only)*
  Fires with the new int index whenever the active
  tab changes.

**Methods**

- `add_tab(self, child: object, label: str) -> WMenuItem`
  Add a new tab whose content is `child` and whose label is
  `label`. Takes ownership of `child` (the Python wrapper is
  re-armed as a non-owning alias). Returns the WMenuItem that
  represents the new tab — useful for further per-tab tweaks.

- `index_of(self, widget: WWidget) -> int`
  Return the tab index whose contents are `widget`, or -1
  if `widget` is not a tab's content.

- `set_tab_enabled(self, index: int, enable: bool) -> None`
  Enable or disable the tab at `index`. Disabled tabs render
  greyed out and can't be selected.

- `set_tab_hidden(self, index: int, hidden: bool) -> None`
  Hide or show the tab at `index`. Hidden tabs keep their
  contents but don't appear in the tab strip.

- `set_tab_closeable(self, index: int, closeable: bool) -> None`
  Whether the tab at `index` shows a close (×) button.

- `set_tab_text(self, index: int, label: str) -> None`
  Set the label shown on the tab at `index`.

- `tab_text(self, index: int) -> str`
  Return the current label of the tab at `index`.

### WPanel {#WPanel}

*Inherits:* `WWidget`

A titled box holding a single central widget. Optionally
collapsible (the user can fold it down to just the title bar).

    panel = container.add_widget(wt.WPanel())
    panel.title = 'Details'
    panel.collapsible = True
    panel.set_central_widget(wt.WText('More info here.'))

**Constructors**

- `__init__(self) -> None`
  Construct an empty panel.

**Properties**

- `title: str` *(read/write)*
  Text shown in the title bar.

- `title_bar: bool` *(read-only)*
  Non-owning handle to the title-bar widget — useful for
  adding extra controls (e.g. action buttons) next to the
  title.

- `collapsible: bool` *(read/write)*
  Whether the panel can be collapsed by the user. Enabling
  adds an expand/collapse toggle to the title bar.

- `collapsed: bool` *(read/write)*
  The current collapsed state. Only meaningful when
  `collapsible` is True.

**Methods**

- `set_title_bar(self, enable: bool) -> None`
  Whether the title bar is rendered. Disabling hides both
  the title and the collapse toggle.

- `collapse(self) -> None`
  Fold the panel down to just its title bar.

- `expand(self) -> None`
  Restore the panel to its full size.

- `set_central_widget(self, widget: WWidget) -> None`
  Install `widget` as the panel's single content widget,
  replacing any previous one. The panel takes ownership; the
  Python wrapper is re-armed as a non-owning alias.

### WGroupBox {#WGroupBox}

*Inherits:* `WContainerWidget`

A container with a border and a caption — renders as HTML
`<fieldset>` with a `<legend>`. Use to visually group a few
related form widgets.

    group = container.add_widget(wt.WGroupBox('Address'))
    group.add_widget(wt.WLineEdit())
    group.add_widget(wt.WLineEdit())

**Constructors**

- `__init__(self) -> None`
  Construct an untitled group box.

- `__init__(self, title: str) -> None`
  Construct a group box captioned `title`.

**Properties**

- `title: str` *(read/write)*
  Caption text — the `<legend>`.

### WDialog {#WDialog}

*Inherits:* `WWidget`

A pop-up window with a title bar, content area, and footer.
Modal by default. Build up the `contents` container, call
`show()`, and react via the `finished` signal (which fires with
a DialogCode).

    dlg = wt.WDialog('Confirm')
    dlg.contents.add_widget(wt.WText('Really delete?'))
    ok = dlg.footer.add_widget(wt.WPushButton('OK'))
    cancel = dlg.footer.add_widget(wt.WPushButton('Cancel'))
    ok.clicked.connect(dlg.accept)
    cancel.clicked.connect(dlg.reject)
    dlg.finished.connect(lambda code: print(code))
    dlg.show()

**Constructors**

- `__init__(self) -> None`
  Construct a dialog with no title.

- `__init__(self, window_title: str) -> None`
  Construct a dialog with the given title bar caption.

**Properties**

- `window_title: str` *(read/write)*
  Caption shown in the dialog's title bar.

- `modal: bool` *(read/write)*
  Whether the dialog blocks interaction with the rest of the
  page while it's shown.

- `closable: bool` *(read/write)*
  Whether the title bar shows a close (×) button that rejects
  the dialog.

- `contents: WContainerWidget` *(read-only)*
  Non-owning handle to the dialog's content container.
  Add the dialog body widgets here.

- `title_bar_widget: WContainerWidget` *(read-only)*
  Non-owning handle to the title-bar container. Use
  to inject custom controls into the title strip.

- `footer: WContainerWidget` *(read-only)*
  Non-owning handle to the footer container. Conventional
  place for the OK / Cancel buttons.

- `result: DialogCode` *(read-only)*
  Final DialogCode after `accept` / `reject` / `done`.

- `finished: DialogCodeSignal` *(read-only)*
  Fires with the DialogCode when the dialog closes
  (a DialogCodeSignal).

**Methods**

- `set_resizable(self, resizable: bool) -> None`
  Whether the user can drag the dialog's edges to resize it.

- `show(self) -> None`
  Display the dialog. If modal, blocks page interaction
  until accepted, rejected, or closed.

- `accept(self) -> None`
  Close with `DialogCode.Accepted`. Convenient slot for an
  OK button's `clicked` signal.

- `reject(self) -> None`
  Close with `DialogCode.Rejected`. Convenient slot for a
  Cancel button's `clicked` signal.

- `done(self, result: DialogCode) -> None`
  Close with an explicit DialogCode.

- `reject_when_escape_pressed(self, enable: bool = True) -> None`
  Whether pressing Escape rejects the dialog.

### WMessageBox {#WMessageBox}

*Inherits:* `WDialog`

Standard alert/confirm dialog — a WDialog preset with a message
and a row of standard buttons.

    box = wt.WMessageBox()
    box.window_title = 'Confirm'
    box.text = 'Discard unsaved changes?'
    box.set_standard_buttons(wt.StandardButton.Yes | wt.StandardButton.No)
    box.button_clicked.connect(lambda btn: print(btn))
    box.show()

**Constructors**

- `__init__(self) -> None`
  Construct an empty message box. Set `text` and `set_standard
  _buttons` before showing.

**Properties**

- `text: str` *(read/write)*
  Message body shown in the dialog.

- `button_result: StandardButton` *(read-only)*
  The StandardButton the user clicked, available after the
  box has closed.

- `button_clicked: StandardButtonSignal` *(read-only)*
  Fires with the StandardButton that was clicked (a
  StandardButtonSignal).

**Methods**

- `set_standard_buttons(self, buttons: int) -> None`
  Configure which buttons to display. `buttons` is an int
  made by OR-ing StandardButton values together — e.g.
  `StandardButton.Ok | StandardButton.Cancel`.
