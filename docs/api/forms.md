# Form Widgets

> Input controls beyond the basics: text areas, spin boxes, sliders, selectors, button groups, progress bars, labels.

**Classes in this section:**

- [`WLabel`](#WLabel)
- [`WBreak`](#WBreak)
- [`WTextArea`](#WTextArea)
- [`WSpinBox`](#WSpinBox)
- [`WDoubleSpinBox`](#WDoubleSpinBox)
- [`WSlider`](#WSlider)
- [`WComboBox`](#WComboBox)
- [`WSelectionBox`](#WSelectionBox)
- [`WRadioButton`](#WRadioButton)
- [`WButtonGroup`](#WButtonGroup)
- [`WProgressBar`](#WProgressBar)
- [`Orientation`](#Orientation)
- [`SelectionMode`](#SelectionMode)

---

### WLabel {#WLabel}

*Inherits:* `WInteractWidget`

An HTML `<label>` element. Renders short text (or an image) that
describes a sibling form input; clicking the label transfers
focus to the buddy.

    edit = container.add_widget(wt.WLineEdit())
    label = container.add_widget(wt.WLabel('Email:'))
    label.set_buddy(edit)

**Constructors**

- `__init__(self) -> None`
  Construct an empty label with no text or image.

- `__init__(self, text: str) -> None`
  Construct a label displaying `text`.

**Properties**

- `text: str` *(read/write)*
  The label's text. Assigning replaces the current content.

- `word_wrap: bool` *(read/write)*
  Whether long text wraps to multiple lines. When False the
  label is rendered on a single line.

**Methods**

- `set_buddy(self, buddy: WFormWidget) -> None`
  Associate the label with a form widget. Clicking the label
  then forwards focus to `buddy` (the HTML `for` attribute is
  wired to the buddy's id).

- `set_image(self, image: WImage) -> None`
  Display a WImage in place of (or alongside) the label text.
  Takes ownership of `image`; the Python wrapper is re-armed
  as a non-owning alias.

### WBreak {#WBreak}

*Inherits:* `WWidget`

A line break — renders as `<br>`. Drop one into a container to
force the following widget onto a new line.

    container.add_widget(wt.WText('First line'))
    container.add_widget(wt.WBreak())
    container.add_widget(wt.WText('Second line'))

**Constructors**

- `__init__(self) -> None`
  Construct a line break.

### WTextArea {#WTextArea}

*Inherits:* `WFormWidget`

Multi-line text input — renders as `<textarea>`. Use for longer
free-form input that wouldn't fit on a single line.

    notes = container.add_widget(wt.WTextArea())
    notes.rows = 8
    notes.columns = 60
    notes.placeholder = 'Add notes…'

**Constructors**

- `__init__(self) -> None`
  Construct an empty text area.

- `__init__(self, text: str) -> None`
  Construct a text area pre-filled with `text`.

**Properties**

- `text: str` *(read/write)*
  The current input value. Reads what the user has typed;
  assigning replaces the contents.

- `rows: int` *(read/write)*
  Visible row count — the HTML `rows` attribute.

- `columns: int` *(read/write)*
  Visible column count — the HTML `cols` attribute.

- `placeholder: str` *(read/write)*
  Greyed-out hint shown when the field is empty.

- `selection_start: int` *(read-only)*
  Character index where the current text selection begins, or
  -1 if there is no selection.

- `has_selected_text: bool` *(read-only)*
  True if the user currently has text selected.

- `cursor_position: int` *(read-only)*
  Character index of the caret, as of the last client update.

### WSpinBox {#WSpinBox}

*Inherits:* `WLineEdit`

Integer-valued numeric input with up/down stepper buttons.

    qty = container.add_widget(wt.WSpinBox())
    qty.set_range(1, 99)
    qty.single_step = 1
    qty.value_changed.connect(lambda v: print('picked', v))

**Constructors**

- `__init__(self) -> None`
  Construct a spin box at value 0.

**Properties**

- `value: int` *(read/write)*
  The current integer value.

- `minimum: int` *(read/write)*
  Lower bound on `value` enforced by the stepper buttons.

- `maximum: int` *(read/write)*
  Upper bound on `value` enforced by the stepper buttons.

- `single_step: int` *(read/write)*
  Amount the stepper buttons add or subtract per click.

- `wrap_around: bool` *(read/write)*
  Whether stepping past the maximum loops back to the minimum
  (and vice-versa).

- `value_changed: IntSignal` *(read-only)*
  Fires with the new int value whenever the user
  commits a change.

**Methods**

- `set_range(self, minimum: int, maximum: int) -> None`
  Set `minimum` and `maximum` in a single call.

### WDoubleSpinBox {#WDoubleSpinBox}

*Inherits:* `WLineEdit`

Floating-point spin box. Same surface as WSpinBox but the value
is a double and `decimals` controls display precision.

    price = container.add_widget(wt.WDoubleSpinBox())
    price.set_range(0.0, 1000.0)
    price.decimals = 2
    price.single_step = 0.05

**Constructors**

- `__init__(self) -> None`
  Construct a spin box at value 0.0.

**Properties**

- `value: float` *(read/write)*
  The current double value.

- `minimum: float` *(read/write)*
  Lower bound on `value`.

- `maximum: float` *(read/write)*
  Upper bound on `value`.

- `single_step: float` *(read/write)*
  Amount the stepper buttons add or subtract per click.

- `decimals: int` *(read/write)*
  Number of decimal places shown when formatting `value`.

- `value_changed: DoubleSignal` *(read-only)*
  Fires with the new double value whenever the user
  commits a change.

**Methods**

- `set_range(self, minimum: float, maximum: float) -> None`
  Set `minimum` and `maximum` in a single call.

### WSlider {#WSlider}

*Inherits:* `WFormWidget`

Integer slider — a draggable handle along a track. Orientation
can be horizontal (default) or vertical.

    vol = container.add_widget(wt.WSlider(wt.Orientation.Horizontal))
    vol.set_range(0, 100)
    vol.tick_interval = 10
    vol.value_changed.connect(lambda v: mixer.set_volume(v))

**Constructors**

- `__init__(self) -> None`
  Construct a horizontal slider at value 0.

- `__init__(self, orientation: Orientation) -> None`
  Construct a slider with the given orientation.

**Properties**

- `value: int` *(read/write)*
  The current integer position along the track.

- `minimum: int` *(read/write)*
  Value at the leftmost (or bottom-most) end of the track.

- `maximum: int` *(read/write)*
  Value at the rightmost (or top-most) end of the track.

- `step: int` *(read/write)*
  Smallest increment the handle snaps to as the user drags.

- `tick_interval: int` *(read/write)*
  Spacing between visible tick marks along the track. Zero
  disables tick rendering.

- `value_changed: IntSignal` *(read-only)*
  Fires with the new int value when the user moves
  the handle.

**Methods**

- `set_range(self, minimum: int, maximum: int) -> None`
  Set `minimum` and `maximum` in a single call.

- `set_orientation(self, orientation: Orientation) -> None`
  Switch between Horizontal and Vertical layouts.

### WComboBox {#WComboBox}

*Inherits:* `WFormWidget`

Drop-down list — renders as `<select>` with one row visible.
Populate via `add_item` / `add_items` and observe selection
changes through `activated` or `string_activated`.

    cb = container.add_widget(wt.WComboBox())
    cb.add_items(['Red', 'Green', 'Blue'])
    cb.string_activated.connect(lambda s: print('picked', s))

**Constructors**

- `__init__(self) -> None`
  Construct an empty combo box.

**Properties**

- `count: int` *(read-only)*
  Number of items currently in the drop-down.

- `current_index: int` *(read/write)*
  Index of the selected item, or -1 if none is selected.
  Assigning programmatically does NOT fire `activated`.

- `activated: IntSignal` *(read-only)*
  Fires with the int index of the newly-selected item
  when the user picks something.

- `string_activated: StringSignal` *(read-only)*
  Fires with the WString label of the newly-selected
  item. Convenient when you don't need the index.

**Methods**

- `add_item(self, text: str) -> None`
  Append a new item with the given label to the end of the
  drop-down list.

- `add_items(self, items: Sequence[str]) -> None`
  Bulk version of `add_item`. Appends each label in order.

- `insert_item(self, index: int, text: str) -> None`
  Insert a new item at position `index`; existing items at
  and after that position shift down.

- `remove_item(self, index: int) -> None`
  Remove the item at position `index`.

- `item_text(self, index: int) -> str`
  Return the label of the item at position `index`.

- `set_item_text(self, index: int, text: str) -> None`
  Replace the label of the item at position `index`.

- `clear(self) -> None`
  Remove every item; the combo box ends up empty.

### WSelectionBox {#WSelectionBox}

*Inherits:* `WComboBox`

Multi-row list-box — renders as `<select size=N>` showing several
items at once. Inherits the populate / query surface from
WComboBox; adds vertical sizing and multi-select.

    sb = container.add_widget(wt.WSelectionBox())
    sb.add_items(['Apples', 'Pears', 'Plums'])
    sb.vertical_size = 6
    sb.set_selection_mode(wt.SelectionMode.Extended)

**Constructors**

- `__init__(self) -> None`
  Construct an empty selection box.

**Properties**

- `vertical_size: int` *(read/write)*
  Number of rows visible without scrolling — the HTML `size`
  attribute.

**Methods**

- `set_selection_mode(self, mode: SelectionMode) -> None`
  Choose between Single and Extended selection (see
  SelectionMode).

- `set_selected_indexes(self, selection: 'std::set<int, std::less<int>, std::allocator<int> >') -> None`
  Replace the current selection with the given set of int
  indices. Only meaningful in Extended mode.

- `clear_selection(self) -> None`
  Deselect every item.

### WRadioButton {#WRadioButton}

*Inherits:* `WFormWidget`

A single radio button. On its own, a radio acts like a checkbox
with a different glyph; the mutual-exclusion behavior comes from
adding several to the same WButtonGroup.

    group = wt.WButtonGroup()
    red = container.add_widget(wt.WRadioButton('Red'))
    grn = container.add_widget(wt.WRadioButton('Green'))
    group.add_button(red)
    group.add_button(grn)
    red.on_check.connect(lambda: print('red'))

**Constructors**

- `__init__(self) -> None`
  Construct an unlabelled radio button in the unchecked state.

- `__init__(self, text: str) -> None`
  Construct a labelled radio; `text` renders next to the dot.

**Properties**

- `checked: bool` *(read/write)*
  The current boolean state. Assigning programmatically does
  NOT fire `on_check`/`on_uncheck`.

- `on_check: EventSignal` *(read-only)*
  Fires when the user selects this radio.

- `on_uncheck: EventSignal` *(read-only)*
  Fires when this radio loses its selected state because a
  sibling in the same group was picked.

### WButtonGroup {#WButtonGroup}

*Inherits:* `WObject`

Mutual-exclusion group for a set of WRadioButtons. Adding a
radio to a group makes it part of the same logical choice — at
most one button in the group can be checked at a time. The
group itself is not a widget; it's a coordinator.

    group = wt.WButtonGroup()
    for label in ['Free', 'Pro', 'Enterprise']:
        rb = container.add_widget(wt.WRadioButton(label))
        group.add_button(rb)

**Constructors**

- `__init__(self) -> None`
  Construct an empty button group. Add WRadioButtons via
  `add_button`.

**Properties**

- `count: int` *(read-only)*
  Number of buttons currently in the group.

- `checked_id: int` *(read-only)*
  The `id` of the currently-selected button (the value passed
  to `add_button`), or -1 if none is selected.

- `selected_button_index: int` *(read/write)*
  Position in insertion order of the selected button, or -1
  if none is selected. Assigning programmatically toggles the
  corresponding radio's state.

**Methods**

- `add_button(self, button: WRadioButton, id: int = -1) -> None`
  Enroll `button` in the group. `id` is an optional integer
  tag returned by `checked_id` — pass -1 (the default) to
  auto-assign.

- `remove_button(self, button: WRadioButton) -> None`
  Detach `button` from the group. The button keeps existing
  as an independent radio.

### WProgressBar {#WProgressBar}

*Inherits:* `WInteractWidget`

A horizontal progress indicator. Set `value` between `minimum`
and `maximum` to render the fill, optionally annotate with a
format string for the percentage label.

    bar = container.add_widget(wt.WProgressBar())
    bar.set_range(0, 100)
    bar.value = 42

**Constructors**

- `__init__(self) -> None`
  Construct a progress bar with range 0..100 and value 0.

**Properties**

- `value: float` *(read/write)*
  The current fill amount. Should sit between `minimum` and
  `maximum`.

- `minimum: float` *(read/write)*
  Value corresponding to an empty bar.

- `maximum: float` *(read/write)*
  Value corresponding to a full bar.

- `value_changed: DoubleSignal` *(read-only)*
  Fires with the new `value` whenever it changes.

**Methods**

- `set_range(self, minimum: float, maximum: float) -> None`
  Set `minimum` and `maximum` in a single call.

- `set_format(self, format: str) -> None`
  Format string used to render the percentage label inside
  the bar — e.g. `'%.0f%%'`. Pass an empty WString to hide
  the label.

### Orientation {#Orientation}

*Inherits:* `enum.IntEnum`

Layout axis. `Horizontal` lays things out left-to-right;
`Vertical` lays things out top-to-bottom. Used by WSlider and
other widgets that have a natural axis.

### SelectionMode {#SelectionMode}

*Inherits:* `enum.Enum`

Selection policy for list-style widgets. `None_` disables
selection entirely, `Single` allows one selected row at a time,
and `Extended` lets the user pick multiple rows with Ctrl/Shift.
