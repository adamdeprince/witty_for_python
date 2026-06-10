# Rich Form Widgets

> Extra form controls beyond the basics: rich-text editor (TinyMCE-backed), in-place edit, password edit, autocomplete popup, color picker.

**Classes in this section:**

- [`WColor`](#WColor)
- [`WPasswordEdit`](#WPasswordEdit)
- [`WInPlaceEdit`](#WInPlaceEdit)
- [`PopupTrigger`](#PopupTrigger)
- [`IntFormWidgetSignal`](#IntFormWidgetSignal)
- [`WSuggestionPopup`](#WSuggestionPopup)
- [`Options`](#Options)
- [`Options`](#WSuggestionPopup.Options)
- [`WColorPicker`](#WColorPicker)
- [`WTextEdit`](#WTextEdit)

---

### WColor {#WColor}

An RGBA color value. Used wherever Wt asks for a color — most
commonly as the value of WColorPicker.color, but also for brushes,
pens, and chart palettes.

    sky = wt.WColor(135, 206, 235)
    picker = container.add_widget(wt.WColorPicker(sky))

Construct from explicit RGB(A) components or from a CSS color
string ('red', '#a0c0e0', 'rgb(160,192,224)'). Named colors
round-trip via CSS only; the red/green/blue accessors return
useful values only for numeric forms.

**Constructors**

- `__init__(self) -> None`
  Construct the default (transparent / inherit) color.

- `__init__(self, red: int, green: int, blue: int, alpha: int = 255) -> None`
  Construct from 0-255 RGBA components. Alpha defaults to 255
  (fully opaque).

- `__init__(self, name: str) -> None`
  Construct from a CSS color string — a named color ('red'),
  a hex literal ('#a0c0e0'), or an rgb()/rgba() form.

**Properties**

- `red: int` *(read-only)*
  Red component (0-255). Only meaningful for colors built
  from numeric forms.

- `green: int` *(read-only)*
  Green component (0-255).

- `blue: int` *(read-only)*
  Blue component (0-255).

- `alpha: int` *(read-only)*
  Alpha component (0-255). 0 = fully transparent.

- `is_default: bool` *(read-only)*
  True for the default-constructed color (transparent/inherited).

**Methods**

- `set_rgb(self, red: int, green: int, blue: int, alpha: int = 255) -> None`
  Replace the color with the given 0-255 RGBA components.

- `set_name(self, name: str) -> None`
  Replace the color with a CSS string (named color, hex,
  or rgb()/rgba() form).

### WPasswordEdit {#WPasswordEdit}

*Inherits:* `WLineEdit`

A single-line password input — renders as `<input type=password>`
with the characters masked. Inherits WLineEdit, so the standard
.text / .placeholder / .max_length all work. The password-specific
properties (min_length, required, pattern) configure a built-in
validator with its own error messages.

    pw = container.add_widget(wt.WPasswordEdit())
    pw.placeholder = 'Password'
    pw.min_length = 8
    pw.required = True
    container.add_widget(wt.WPushButton('Sign in')).clicked.connect(
        lambda: sign_in(pw.text))

Attaching your own validator via set_validator replaces the
built-in length/pattern checks.

**Constructors**

- `__init__(self) -> None`
  Construct an empty password input with no built-in constraints.

**Properties**

- `native_control: bool` *(read/write)*
  Use the browser's native <input type=password> behavior. Disable for full Wt-styled rendering.

- `min_length: int` *(read/write)*
  Minimum password length. 0 means no minimum.

- `required: bool` *(read/write)*
  When True, an empty field fails validation.

- `pattern: str` *(read/write)*
  Regular expression the password must match. Empty disables.

- `invalid_too_long_text: str` *(read/write)*
  Validation message shown when the entered password exceeds max_length.

- `invalid_too_short_text: str` *(read/write)*
  Validation message shown when shorter than min_length.

- `invalid_no_match_text: str` *(read/write)*
  Validation message when the password doesn't match pattern.

- `invalid_blank_text: str` *(read/write)*
  Validation message when required and left blank.

### WInPlaceEdit {#WInPlaceEdit}

*Inherits:* `WWidget`

Text that turns into a line edit when clicked. Useful for tables
or detail panes where the user toggles between read and edit modes
without a dedicated form.

    cell = container.add_widget(wt.WInPlaceEdit('Untitled'))
    cell.value_changed.connect(lambda new_text: save(new_text))

By default a save/cancel pair of buttons is shown alongside the
active editor; with_buttons=False makes the field auto-save on
Enter or blur.

**Constructors**

- `__init__(self, text: str) -> None`
  Construct displaying `text` initially.

- `__init__(self, with_buttons: bool, text: str) -> None`
  When `with_buttons` is False, the edit auto-saves on blur and no save/cancel buttons are shown.

**Properties**

- `text: str` *(read/write)*
  The currently displayed text. Reads what was last accepted;
  assigning replaces the value programmatically without firing
  value_changed.

- `placeholder_text: str` *(read/write)*
  Greyed-out hint shown in the embedded line edit when the
  value is empty.

- `line_edit: WLineEdit` *(read-only)*
  The internal WLineEdit, exposed for fine-grained styling (placeholder, max length, validator).

- `value_changed: StringSignal` *(read-only)*
  Signal[str] — fires with the new text when the user accepts an edit.

**Methods**

- `set_buttons_enabled(self, enabled: bool = True) -> None`
  Show/hide the save/cancel buttons. When hidden, the edit auto-saves on Enter / blur.

### PopupTrigger {#PopupTrigger}

*Inherits:* `enum.Flag`

Bitfield deciding when a WSuggestionPopup opens against its
attached edit. OR values together when passing to `for_edit`.

### IntFormWidgetSignal {#IntFormWidgetSignal}

Signal carrying an int and a WFormWidget pointer. Used by
WSuggestionPopup.activated — the int is the chosen row index in
the popup's model and the widget is the edit that was being
assisted.

**Methods**

- `connect(self, callable: Callable) -> Connection`
  Subscribe a Python callable. Returns a Connection — call
  `.disconnect()` to stop receiving.

- `disconnect_all_slots(self) -> None`
  Drop every Python subscriber attached via `connect`.

### WSuggestionPopup {#WSuggestionPopup}

*Inherits:* `WWidget`

Autocomplete popup attached to one or more WFormWidgets. Holds a
list of suggestions (either added directly or fed from a
WAbstractItemModel) and offers them as the user types into a
wired-up edit.

    opts = wt.WSuggestionPopup.Options()
    opts.highlight_begin_tag = '<b>'
    opts.highlight_end_tag = '</b>'
    popup = app.root.add_widget(wt.WSuggestionPopup(opts))
    for name in ['Alice', 'Bob', 'Charlie']:
        popup.add_suggestion(name)
    edit = container.add_widget(wt.WLineEdit())
    popup.for_edit(edit)
    popup.activated.connect(lambda row, w: print('picked', row))

A single popup can serve several edits — `for_edit` adds an edit
without detaching the previous ones.

**Constructors**

- `__init__(self, options: Options) -> None`
  Construct with an Options config — see WSuggestionPopup.Options.

**Properties**

- `filter_length: int` *(read/write)*
  Minimum input length before the popup activates.

- `default_index: int` *(read/write)*
  Row index pre-selected when the popup first opens; -1 for none.

- `current_item: int` *(read-only)*
  Index of the currently-highlighted suggestion; -1 if none.

- `activated: IntFormWidgetSignal` *(read-only)*
  IntFormWidgetSignal — fires when the user picks a suggestion. Slot receives (row_index, edit_widget); edit_widget is whichever WFormWidget the popup was for_edit'd against.

- `model: WAbstractItemModel` *(read-only)*
  Current backing model (shared_ptr).

**Methods**

- `for_edit(self, edit: WFormWidget, triggers: int = 1) -> None`
  Attach this popup to a form widget. The popup will offer completions while the user edits the field. Pass triggers as a bitwise OR of PopupTrigger values.

- `remove_edit(self, edit: WFormWidget) -> None`
  Detach the popup from `edit`. Other edits stay wired.

- `show_at(self, edit: WFormWidget) -> None`
  Open the popup against `edit` programmatically, regardless
  of trigger configuration.

- `clear_suggestions(self) -> None`
  Empty the suggestion list.

- `add_suggestion(self, text: str, value: str = '') -> None`
  Add a string to the autocomplete list. If `value` is empty, the displayed `text` is also inserted on selection.

- `set_drop_down_icon_unfiltered(self, unfiltered: bool) -> None`
  When True, clicking the drop-down icon shows all suggestions regardless of current input. Pairs with PopupTrigger.DropDownIcon.

- `set_auto_select_enabled(self, enabled: bool) -> None`
  When True, Enter pressed inside the edit accepts the
  currently-highlighted suggestion.

- `set_model(self, model: WAbstractItemModel) -> None`
  Replace the underlying suggestion source with a custom
  WAbstractItemModel. The default model is a WStringListModel
  populated by `add_suggestion`.

**Nested types**

- `Options`
  Behavior knobs for WSuggestionPopup. Default-construct, fill in
  the fields you care about, then pass to the WSuggestionPopup
  constructor.

      opts = wt.WSuggestionPopup.Options()
      opts.highlight_begin_tag = '<b>'
      opts.highlight_end_tag = '</b>'
      opts.word_separators = ' '
      popup = wt.WSuggestionPopup(opts)

  Empty defaults work for many cases but the runtime warns if a
  field it requires is left blank.

### Options {#Options}

Behavior knobs for WSuggestionPopup. Default-construct, fill in
the fields you care about, then pass to the WSuggestionPopup
constructor.

    opts = wt.WSuggestionPopup.Options()
    opts.highlight_begin_tag = '<b>'
    opts.highlight_end_tag = '</b>'
    opts.word_separators = ' '
    popup = wt.WSuggestionPopup(opts)

Empty defaults work for many cases but the runtime warns if a
field it requires is left blank.

**Constructors**

- `__init__(self) -> None`
  Construct with empty/zeroed fields. Assign the ones you need.

**Properties**

- `highlight_begin_tag: str` *(read/write)*
  Markup wrapped around the matched portion of each suggestion
  (e.g. '<b>'). Empty disables highlighting.

- `highlight_end_tag: str` *(read/write)*
  Closing tag matching highlight_begin_tag.

- `list_separator: str` *(read/write)*
  Separator char for list-of-values fields. Empty/`'\0'` means the field holds a single value (no list).

- `whitespace: str` *(read/write)*
  Characters considered whitespace when locating word
  boundaries in the user's input.

- `word_separators: str` *(read/write)*
  Characters that separate words for the purpose of matching
  the next-typed-word against the suggestion list.

- `append_replaced_text: str` *(read/write)*
  Text appended after the chosen suggestion is inserted.

- `word_start_regexp: str` *(read/write)*
  Regex that identifies the start of a word in the input
  stream. Used when matching mid-string suggestions.

### Options {#WSuggestionPopup.Options}

Behavior knobs for WSuggestionPopup. Default-construct, fill in
the fields you care about, then pass to the WSuggestionPopup
constructor.

    opts = wt.WSuggestionPopup.Options()
    opts.highlight_begin_tag = '<b>'
    opts.highlight_end_tag = '</b>'
    opts.word_separators = ' '
    popup = wt.WSuggestionPopup(opts)

Empty defaults work for many cases but the runtime warns if a
field it requires is left blank.

**Constructors**

- `__init__(self) -> None`
  Construct with empty/zeroed fields. Assign the ones you need.

**Properties**

- `highlight_begin_tag: str` *(read/write)*
  Markup wrapped around the matched portion of each suggestion
  (e.g. '<b>'). Empty disables highlighting.

- `highlight_end_tag: str` *(read/write)*
  Closing tag matching highlight_begin_tag.

- `list_separator: str` *(read/write)*
  Separator char for list-of-values fields. Empty/`'\0'` means the field holds a single value (no list).

- `whitespace: str` *(read/write)*
  Characters considered whitespace when locating word
  boundaries in the user's input.

- `word_separators: str` *(read/write)*
  Characters that separate words for the purpose of matching
  the next-typed-word against the suggestion list.

- `append_replaced_text: str` *(read/write)*
  Text appended after the chosen suggestion is inserted.

- `word_start_regexp: str` *(read/write)*
  Regex that identifies the start of a word in the input
  stream. Used when matching mid-string suggestions.

### WColorPicker {#WColorPicker}

*Inherits:* `WFormWidget`

An `<input type=color>` element — the browser-native color picker.
Renders as a swatch the user clicks to open the OS / browser color
dialog.

    picker = container.add_widget(wt.WColorPicker(wt.WColor('#3366cc')))
    picker.changed.connect(lambda: apply_color(picker.color))

**Constructors**

- `__init__(self) -> None`
  Construct with the default (black) color.

- `__init__(self, color: WColor) -> None`
  Construct with `color` as the initial selection.

**Properties**

- `color: WColor` *(read/write)*
  The currently selected WColor. Assigning updates the swatch
  on the next round-trip.

- `color_input: EventSignal` *(read-only)*
  EventSignal[] — fires continuously while the user drags through the color picker. Use the inherited `changed` signal for commit-only notifications.

### WTextEdit {#WTextEdit}

*Inherits:* `WTextArea`

Rich-text editor backed by TinyMCE — a WYSIWYG widget producing
HTML. Inherits WTextArea, so `.text` reads/writes the editor
contents as an HTML string.

    editor = container.add_widget(wt.WTextEdit('<p>Hello</p>'))
    editor.set_extra_plugins('lists,advlist')
    container.add_widget(wt.WPushButton('Save')).clicked.connect(
        lambda: save_html(editor.text))

TinyMCE itself is NOT bundled with Wt — the application must serve
a TinyMCE build under /resources/tinymce/ (or wherever Wt is
configured to look). Without it the widget falls back to a plain
textarea.

**Constructors**

- `__init__(self) -> None`
  Construct an empty rich-text editor.

- `__init__(self, text: str) -> None`
  Construct with initial HTML `text` in the editor.

**Properties**

- `version: int` *(read-only)*
  TinyMCE version currently configured (3 or 4 depending on what Wt was built against and what's on disk).

- `style_sheet: str` *(read/write)*
  Comma-separated list of stylesheets applied inside the editor iframe — also drives the 'styleselect' button options.

**Methods**

- `set_extra_plugins(self, plugins: str) -> None`
  Comma-separated TinyMCE plugin names to load on top of the default 'safari' plugin.

- `set_tool_bar(self, row: int, config: str) -> None`
  Configure a single toolbar row by index (0-based). `config` is a TinyMCE 'theme_advanced_buttons_N' string, e.g. 'bold,italic,|,bullist'.

- `set_configuration_setting(self, name: str, value: 'std::any') -> None`
  Forward a setting straight to TinyMCE's init() config. `value` is anything TinyMCE accepts as JSON.
