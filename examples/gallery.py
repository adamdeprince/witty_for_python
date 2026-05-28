"""witty_for_python gallery — exercises the full binding surface.

A condensed Python port of Wt's `examples/widgetgallery/FormWidgets.C` plus a
walking tour of the rest of witty_for_python's widgets: basics, layout, table, dialogs,
and event-payload demos. Each section connects at least one signal to a
Python slot so the C++/Python signal bridge is exercised end-to-end.

Run:

    python examples/gallery.py --docroot . \\
        --http-address 127.0.0.1 --http-port 8080

Then open http://127.0.0.1:8080. Wt's static resources are bundled with the
witty_for_python wheel and located automatically; pass --resources-dir only
to override.
"""

from __future__ import annotations

import datetime
import sys

import witty_for_python as wt


# ---- Basics: WText, WBreak, WAnchor, WImage, WPushButton, clicked() ----

def make_basics_tab() -> wt.WContainerWidget:
    c = wt.WContainerWidget()
    c.add_widget("<h3>Basic widgets</h3>")
    c.add_widget("WText for inline content. WBreak below ends the line.")
    c.add_widget(wt.WBreak())

    # str → WLink is an implicit conversion, so we can pass a URL directly
    # to WAnchor / WImage. Construct an explicit wt.WLink(...) only when you
    # need a WResource, an internal path, or to tweak link properties.
    c.add_widget(wt.WAnchor("https://www.webtoolkit.eu/wt", "Wt homepage"))
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WImage("https://www.webtoolkit.eu/css/wt.png", "Wt logo"))
    c.add_widget(wt.WBreak())

    button = c.add_widget(wt.WPushButton("Press me"))
    counter = c.add_widget(" Pressed 0 time(s).")

    state = {"n": 0}

    def on_press() -> None:
        state["n"] += 1
        counter.text = f" Pressed {state['n']} time(s)."

    button.clicked.connect(on_press)
    return c


# ---- Forms: every form widget + a "submit" button that reads them all ----

def make_form_tab() -> wt.WContainerWidget:
    c = wt.WContainerWidget()
    c.add_widget("<h3>Form widgets</h3>")

    name_label = c.add_widget(wt.WLabel("Name:"))
    name = c.add_widget(wt.WLineEdit())
    name.placeholder = "Your name"
    name_label.set_buddy(name)
    # Demonstrate WFormWidget.set_validator: require 2-50 characters.
    name.set_validator(wt.WLengthValidator(2, 50))
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Email:"))
    email = c.add_widget(wt.WLineEdit())
    email.placeholder = "you@example.com"
    email.set_validator(wt.WEmailValidator())
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Birthday:"))
    birthday = c.add_widget(wt.WDateEdit())
    # Python datetime.date passes through the caster transparently — no
    # wt.WDate Python type involved.
    birthday.date = datetime.date(2000, 1, 1)
    birthday.set_validator(wt.WDateValidator(
        datetime.date(1900, 1, 1), datetime.date.today()
    ))
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Preferred time:"))
    pref_time = c.add_widget(wt.WTimeEdit())
    pref_time.time = datetime.time(9, 0)
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Notes:"))
    notes = c.add_widget(wt.WTextArea())
    notes.rows = 3
    notes.columns = 40
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Age (int):"))
    age = c.add_widget(wt.WSpinBox())
    age.set_range(0, 150)
    age.value = 30
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Weight (kg):"))
    weight = c.add_widget(wt.WDoubleSpinBox())
    weight.set_range(0.0, 500.0)
    weight.decimals = 1
    weight.value = 70.5
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Volume:"))
    volume = c.add_widget(wt.WSlider(wt.Orientation.Horizontal))
    volume.set_range(0, 100)
    volume.value = 50
    volume_lbl = c.add_widget(" (50)")

    # IntSignal: slot receives the int payload. Properties are read/written
    # like `volume_lbl.text = ...`, so the handler is a tiny named function.
    def on_volume(v: int) -> None:
        volume_lbl.text = f" ({v})"

    volume.value_changed.connect(on_volume)
    c.add_widget(wt.WBreak())

    cb = c.add_widget(wt.WCheckBox("Subscribe"))
    cb_lbl = c.add_widget(" (off)")

    # EventSignal<> with no payload — slot takes no args.
    def on_subscribe() -> None:
        cb_lbl.text = " (on)"

    def on_unsubscribe() -> None:
        cb_lbl.text = " (off)"

    cb.on_check.connect(on_subscribe)
    cb.on_uncheck.connect(on_unsubscribe)
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Tier:"))
    group = wt.WButtonGroup()
    rbs = c.add_widgets([wt.WRadioButton(l) for l in ("Bronze", "Silver", "Gold")])
    for i, rb in enumerate(rbs):
        group.add_button(rb, i)
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Color:"))
    combo = c.add_widget(wt.WComboBox())
    combo.add_items(("Red", "Green", "Blue"))
    color_lbl = c.add_widget("")

    # StringSignal: slot receives a Wt::WString as a Python str.
    def on_color(s: str) -> None:
        color_lbl.text = f"  selected: {s}"

    combo.string_activated.connect(on_color)
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Hobbies:"))
    sel = c.add_widget(wt.WSelectionBox())
    sel.add_items(("Reading", "Hiking", "Gaming", "Cooking"))
    sel.set_selection_mode(wt.SelectionMode.Extended)
    sel.vertical_size = sel.count   # show all items without scrolling
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Progress:"))
    pb = c.add_widget(wt.WProgressBar())
    pb.set_range(0.0, 100.0)
    pb.value = 0.0
    advance = c.add_widget(wt.WPushButton("+10"))

    def on_advance() -> None:
        pb.value = min(pb.value + 10.0, 100.0)

    advance.clicked.connect(on_advance)
    c.add_widget(wt.WBreak())

    submit = c.add_widget(wt.WPushButton("Submit"))
    summary = c.add_widget("")

    def on_submit() -> None:
        summary.text = (
            "<pre>"
            f"name      = {name.text!r}\n"
            f"notes     = {notes.text!r}\n"
            f"age       = {age.value}\n"
            f"weight    = {weight.value}\n"
            f"volume    = {volume.value}\n"
            f"subscribe = {cb.checked}\n"
            f"tier_id   = {group.checked_id}\n"
            f"color_idx = {combo.current_index}\n"
            f"progress  = {pb.value}\n"
            "</pre>"
        )

    submit.clicked.connect(on_submit)
    return c


# ---- Layout & containers: WGroupBox, WPanel, WHBoxLayout ----

def make_layout_tab() -> wt.WContainerWidget:
    c = wt.WContainerWidget()
    c.add_widget("<h3>Layouts and groupings</h3>")

    gb = c.add_widget(wt.WGroupBox("Group box"))
    gb.add_widget("WGroupBox renders as &lt;fieldset&gt; + &lt;legend&gt;.")
    c.add_widget(wt.WBreak())

    panel = c.add_widget(wt.WPanel())
    panel.title = "Collapsible panel"
    panel.set_title_bar(True)
    panel.collapsible = True
    inner = wt.WContainerWidget()
    inner.add_widget("Click the title bar to collapse/expand.")
    panel.set_central_widget(inner)
    c.add_widget(wt.WBreak())

    # A horizontal box layout inside a fresh container.
    row_container = c.add_widget(wt.WContainerWidget())
    row = wt.WHBoxLayout()
    row.add_widgets([wt.WPushButton(label) for label in ("A", "B", "C")])
    row_container.set_layout(row)
    return c


# ---- WTable ----

def make_table_tab() -> wt.WContainerWidget:
    c = wt.WContainerWidget()
    c.add_widget("<h3>WTable</h3>")

    table = c.add_widget(wt.WTable())
    headers = ("Symbol", "Last", "Change")
    for col, label in enumerate(headers):
        table.element_at(0, col).add_widget(f"<b>{label}</b>")
    rows = [
        ("AAPL", "$170.12", "+0.45"),
        ("GOOG", "$140.99", "-1.20"),
        ("TSLA", "$180.34", "+3.10"),
    ]
    for r, row in enumerate(rows, start=1):
        for col, val in enumerate(row):
            table.element_at(r, col).add_widget(val)
    return c


# ---- Dialogs: WDialog with finished() signal, WMessageBox ----

def make_dialog_tab() -> wt.WContainerWidget:
    c = wt.WContainerWidget()
    c.add_widget("<h3>Dialogs</h3>")

    log = c.add_widget("<i>(no dialog opened yet)</i>")
    c.add_widget(wt.WBreak())

    # Custom WDialog. Bound methods like `dlg.accept` can be passed directly
    # to `connect()` — witty_for_python detects nanobind bound methods and invokes
    # them with no arguments, so the click payload is dropped automatically.
    open_dlg = c.add_widget(wt.WPushButton("Open custom dialog"))
    dlg = c.add_widget(wt.WDialog("A demo dialog"))
    dlg.modal = True
    dlg.closable = True
    dlg.contents.add_widget("Click Accept or Reject.")
    ok = dlg.footer.add_widget(wt.WPushButton("Accept"))
    cancel = dlg.footer.add_widget(wt.WPushButton("Reject"))
    ok.clicked.connect(dlg.accept)
    cancel.clicked.connect(dlg.reject)

    # DialogCodeSignal: slot receives a DialogCode enum.
    def on_dialog_finished(code: wt.DialogCode) -> None:
        log.text = f"dialog finished: <b>{code}</b>"

    dlg.finished.connect(on_dialog_finished)
    open_dlg.clicked.connect(dlg.show)
    c.add_widget(wt.WBreak())

    # Standard WMessageBox
    open_msg = c.add_widget(wt.WPushButton("Open message box"))
    mbox = c.add_widget(wt.WMessageBox())
    mbox.window_title = "Confirm"
    mbox.text = "Proceed with the demo?"
    mbox.set_standard_buttons(wt.StandardButton.Ok | wt.StandardButton.Cancel)

    # StandardButtonSignal: slot receives a StandardButton enum.
    def on_message_clicked(btn: wt.StandardButton) -> None:
        log.text = f"message box → <b>{btn}</b>"

    mbox.button_clicked.connect(on_message_clicked)
    open_msg.clicked.connect(mbox.show)
    return c


# ---- Events: WMouseEvent and WKeyEvent payloads ----

def make_events_tab() -> wt.WContainerWidget:
    c = wt.WContainerWidget()
    c.add_widget("<h3>Event payloads</h3>")
    c.add_widget(
        "<p>Slot signatures are introspected at connect time: 0 args drops "
        "the payload, 1+ args receives it. Try both buttons below.</p>")

    target = c.add_widget(wt.WPushButton("Click — slot wants the WMouseEvent"))
    info = c.add_widget(" (no click yet)")

    def on_click(evt: wt.WMouseEvent) -> None:
        info.text = (
            f" button={evt.button}, "
            f"widget=({evt.widget.x},{evt.widget.y}), "
            f"document=({evt.document.x},{evt.document.y}), "
            f"modifiers={evt.modifiers}"
        )

    target.clicked.connect(on_click)
    c.add_widget(wt.WBreak())

    bumper = c.add_widget(wt.WPushButton("Click — slot ignores payload"))
    bump_lbl = c.add_widget(" 0")
    state = {"n": 0}

    def bump() -> None:
        state["n"] += 1
        bump_lbl.text = f" {state['n']}"

    bumper.clicked.connect(bump)
    c.add_widget(wt.WBreak())

    c.add_widget(wt.WLabel("Type here:"))
    keyfield = c.add_widget(wt.WLineEdit())
    key_lbl = c.add_widget(" (no key yet)")

    def on_key(evt: wt.WKeyEvent) -> None:
        key_lbl.text = f" key={evt.key} char={evt.char_code}"

    keyfield.key_pressed.connect(on_key)
    return c


# ---- Templates: XML layout with bound variables/widgets ----

def make_template_tab() -> wt.WContainerWidget:
    c = wt.WContainerWidget()
    c.add_widget("<h3>WTemplate</h3>")
    c.add_widget(
        "<p>The card below is a single <code>WTemplate</code> with the layout "
        "in an HTML string. <code>${name}</code> is a bound string, "
        "<code>${count}</code> a bound int (re-bound on each click), and "
        "<code>${button}</code> is a bound <code>WPushButton</code> — the "
        "same Python widget you'd add to any container, just slotted into the "
        "template's named placeholder.</p>")

    card = c.add_widget(wt.WTemplate("""
        <div style="padding:1em;border:1px solid #888;border-radius:6px;
                    background:#f4f6f8; max-width:32em;">
          <h4 style="margin-top:0;">Hello, ${name}!</h4>
          <p>You have clicked the button <b>${count}</b> time(s).</p>
          <p>${button}</p>
          ${<if-celebrate>}
            <p style="color:#0a7;"><b>10+ clicks. Nice.</b></p>
          ${</if-celebrate>}
        </div>
    """))

    card.bind_string("name", "world")
    state = {"n": 0}
    card.bind_int("count", 0)

    btn = card.bind_widget("button", wt.WPushButton("Click me"))

    def on_click() -> None:
        state["n"] += 1
        card.bind_int("count", state["n"])
        card.set_condition("celebrate", state["n"] >= 10)

    btn.clicked.connect(on_click)
    return c


def make_resources_tab() -> wt.WContainerWidget:
    """Server-side resources — content the browser fetches by URL.

    A ``WMemoryResource`` stores bytes the server hands out on demand.
    Wrapping it in a ``WAnchor`` (or ``WImage`` for binary image data) gives
    the user a clickable link. Mutating ``resource.data`` then calling
    ``resource.set_changed()`` invalidates any browser-side cache so the next
    fetch reflects the new content — useful for download buttons whose
    payload depends on UI state.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>WResource — dynamic CSV download</h3>")
    c.add_widget(
        "<p>The link below points at a <code>WMemoryResource</code>. Click "
        "<b>Regenerate</b> to rewrite its byte payload server-side and "
        "invalidate the browser cache — the next download then sees the "
        "fresh content with a new timestamp.</p>")

    csv = wt.WMemoryResource("text/csv")
    csv.suggest_file_name("export.csv")
    csv.set_disposition_type(wt.ContentDisposition.Attachment)

    def regenerate() -> None:
        now = datetime.datetime.now().isoformat(timespec="seconds")
        rows = [b"row,value,generated_at"]
        for i in range(5):
            rows.append(f"{i},{i * i},{now}".encode("utf-8"))
        csv.data = b"\n".join(rows) + b"\n"
        csv.set_changed()

    regenerate()  # initial payload so the link is non-empty on first load

    # WAnchor accepts a WResource directly via WLink's implicit constructor
    # — same ergonomic shortcut the str → WLink path provides.
    c.add_widget(wt.WAnchor(csv, "Download export.csv"))
    c.add_widget("<br>")
    c.add_widget(wt.WPushButton("Regenerate")).clicked.connect(regenerate)

    return c


def make_upload_tab() -> wt.WContainerWidget:
    """File uploads from the browser via WFileUpload.

    The widget exposes a file-picker button. We connect to `changed` (fires
    when the user picks a file) to kick off the upload immediately, then to
    `uploaded` (fires when the bytes arrive server-side) to read the spool
    file and surface basic metadata. The `multiple` knob switches between
    single- and many-file modes.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>WFileUpload</h3>")
    c.add_widget(
        "<p>Pick a file; it's auto-uploaded and metadata about the spool "
        "file appears below. Wt manages the temp file lifecycle — read it "
        "in the <code>uploaded</code> slot, before the request returns.</p>")

    upload = c.add_widget(wt.WFileUpload())
    upload.set_filters(".csv,.txt,.json,image/*")
    upload_btn = c.add_widget(wt.WPushButton("Upload"))
    log = c.add_widget(wt.WText("<i>(no upload yet)</i>"))

    def on_changed() -> None:
        # Modern browsers auto-trigger upload after pick, but call it
        # explicitly so the no-JS fallback works too.
        upload.upload()
        upload_btn.disable()

    def on_uploaded() -> None:
        upload_btn.enable()
        if upload.empty:
            log.text = "<i>upload finished but nothing arrived</i>"
            return
        files = upload.uploaded_files
        if not files:
            # Single-file path: uploaded_files is empty unless multiple=True.
            log.text = (
                f"received: spool=<code>{upload.spool_file_name}</code>")
            return
        lines = [f"received {len(files)} file(s):<ul>"]
        for f in files:
            lines.append(
                f"<li><b>{f.client_file_name}</b> ({f.content_type}) "
                f"&rarr; <code>{f.spool_file_name}</code></li>")
        lines.append("</ul>")
        log.text = "".join(lines)

    upload.changed.connect(on_changed)
    upload.uploaded.connect(on_uploaded)
    return c


def make_filedrop_tab() -> wt.WContainerWidget:
    """Drag-and-drop file uploads via WFileDropWidget.

    The widget shows a styled dropzone; drag a file (or several) onto it
    and the browser starts uploading sequentially. We connect to ``drop``
    (fires with the list of newly-introduced ``File`` entries) and
    ``uploaded`` (fires per file when the bytes finish landing) to keep a
    log of what's happening.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>WFileDropWidget</h3>")
    c.add_widget(
        "<p>Drag files into the dashed area below. Each drop triggers the "
        "<code>drop</code> signal with a list of <code>File</code> entries; "
        "each individual byte-transfer completion triggers <code>uploaded</code> "
        "with a single <code>File</code> reference. Clicking the widget "
        "opens the native file picker as a fallback.</p>")

    drop = c.add_widget(wt.WFileDropWidget())
    drop.set_filters(".csv,.txt,.json,image/*")
    drop.add_widget("<i>Drop files here</i>")
    # Visual cue — the default CSS class is 'Wt-filedropzone'; we add a
    # dashed border so the dropzone is obviously a target without the
    # Bootstrap theme having to know about us.
    drop.style_class = "Wt-filedropzone"

    log = c.add_widget(wt.WText("<i>(waiting for a drop)</i>"))
    state = {"received": 0}

    def on_drop(files: list) -> None:
        names = ", ".join(f.client_file_name for f in files)
        log.text = f"queued {len(files)} file(s): <b>{names}</b>"

    def on_uploaded(f) -> None:
        state["received"] += 1
        log.text = (
            f"uploaded <b>{f.client_file_name}</b> "
            f"({f.size}&nbsp;bytes, {f.mime_type}); "
            f"{state['received']} total this session")

    def on_too_large(f, size: int) -> None:
        log.text = (
            f"rejected <b>{f.client_file_name}</b>: "
            f"{size}&nbsp;bytes exceeds server limit")

    def on_upload_failed(f) -> None:
        log.text = f"upload failed for <b>{f.client_file_name}</b>"

    drop.drop.connect(on_drop)
    drop.uploaded.connect(on_uploaded)
    drop.too_large.connect(on_too_large)
    drop.upload_failed.connect(on_upload_failed)
    return c


def make_extras_tab() -> wt.WContainerWidget:
    """Form widgets that didn't make the first pass.

    Each row shows one widget plus a live readout — picking a color, typing
    in the password edit, accepting an in-place edit, or selecting from the
    autocomplete popup updates the readout via the widget's signal.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>Extra form widgets</h3>")

    # ---- WColorPicker ----
    c.add_widget("<h4>WColorPicker</h4>")
    picker = c.add_widget(wt.WColorPicker(wt.WColor(0, 128, 196)))
    color_log = c.add_widget(wt.WText("initial color set"))

    def on_color_changed() -> None:
        col = picker.color
        color_log.text = (
            f"color now rgb(<b>{col.red}</b>, <b>{col.green}</b>, "
            f"<b>{col.blue}</b>) alpha=<b>{col.alpha}</b>")
    picker.changed.connect(on_color_changed)

    # ---- WPasswordEdit ----
    c.add_widget("<h4>WPasswordEdit (min length 8, must include a digit)</h4>")
    pwd = c.add_widget(wt.WPasswordEdit())
    pwd.min_length = 8
    pwd.required = True
    pwd.pattern = r".*\d.*"
    pwd.invalid_too_short_text = "at least 8 chars please"
    pwd.invalid_no_match_text = "include at least one digit"
    pwd.invalid_blank_text = "password is required"

    # ---- WInPlaceEdit ----
    c.add_widget("<h4>WInPlaceEdit (click the text below)</h4>")
    ipe = c.add_widget(wt.WInPlaceEdit("click to edit me"))
    ipe.placeholder_text = "type something…"
    ipe_log = c.add_widget(wt.WText(""))

    def on_ipe_changed(new_text: str) -> None:
        ipe_log.text = f"new value: <b>{new_text}</b>"
    ipe.value_changed.connect(on_ipe_changed)

    # ---- WSuggestionPopup wired to a WLineEdit ----
    c.add_widget("<h4>WSuggestionPopup (autocomplete — type 'b')</h4>")
    target = c.add_widget(wt.WLineEdit())
    target.placeholder = "fruit name…"

    opts = wt.WSuggestionPopup.Options()
    opts.highlight_begin_tag = "<b>"
    opts.highlight_end_tag = "</b>"
    opts.whitespace = " \n"
    opts.word_separators = " "
    opts.list_separator = ""

    popup = c.add_widget(wt.WSuggestionPopup(opts))
    for fruit in ("apple", "banana", "blackberry", "blueberry",
                  "cherry", "grape", "kiwi", "mango", "orange",
                  "pear", "raspberry", "strawberry"):
        popup.add_suggestion(fruit)
    popup.for_edit(target)
    suggest_log = c.add_widget(wt.WText(""))

    def on_suggestion_picked(row: int, edit) -> None:
        # `edit` is whichever WFormWidget the popup was for_edit'd against
        # (we have only one here, but a single popup can serve many edits).
        del edit
        suggest_log.text = f"picked row <b>{row}</b>"
    popup.activated.connect(on_suggestion_picked)

    # ---- WTextEdit (rich text — backed by the bundled TinyMCE) ----
    c.add_widget("<h4>WTextEdit (rich text)</h4>")
    c.add_widget(
        "<p>The editor below is a <code>WTextEdit</code>, which wraps "
        "TinyMCE. The JS + skins ship inside the wheel under "
        "<code>witty_for_python._wt_resources/tinymce/</code>.</p>")
    rich = c.add_widget(wt.WTextEdit("<p>Try editing this <b>rich</b> text.</p>"))
    rich.set_extra_plugins("lists,advlist,link")
    rich.set_tool_bar(0, "bold italic underline | bullist numlist | link unlink")

    return c


def make_timer_tab() -> wt.WContainerWidget:
    """WTimer — a periodic server-side tick that drives a Python slot.

    Each fire of `timeout` lands in the worker thread under the session's
    update lock, so widget mutations are safe. We display a counter that
    increments while the timer is running, plus start/stop buttons.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>WTimer</h3>")
    c.add_widget(
        "<p>Click <b>Start</b> to begin a server-side timer firing every "
        "500&nbsp;ms. Each tick mutates the counter widget below — exercising "
        "the slot-on-worker-thread path. <b>Stop</b> cancels it.</p>")

    counter = c.add_widget(wt.WText("ticks: <b>0</b>"))

    timer = wt.WTimer()
    timer.interval = datetime.timedelta(milliseconds=500)
    # The timer is kept alive across the function boundary by the bound-
    # method references stored in the connection registry below
    # (`timer.start`, `timer.stop`, `timer.timeout.connect(on_tick)`).
    # Nanobind bound methods hold a strong ref to `self`, and the registry
    # keeps the connection until the session ends.

    state = {"n": 0}

    def on_tick(_e: wt.WMouseEvent) -> None:
        state["n"] += 1
        counter.text = f"ticks: <b>{state['n']}</b>"
    timer.timeout.connect(on_tick)

    btn_start = c.add_widget(wt.WPushButton("Start"))
    btn_stop = c.add_widget(wt.WPushButton("Stop"))
    btn_start.clicked.connect(timer.start)
    btn_stop.clicked.connect(timer.stop)
    return c


def make_modelview_tab() -> wt.WContainerWidget:
    """Model/view: a WStandardItemModel rendered through a WTableView.

    The model holds a few rows of mock contact data; the view renders
    them with sortable columns. Clicking a cell logs the (row, column)
    via the view's ``clicked`` signal — a ``ModelIndexMouseSignal``
    delivering a ``WModelIndex`` + ``WMouseEvent`` pair into Python.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>Model/view: WTableView over WStandardItemModel</h3>")
    c.add_widget(
        "<p>Click any cell to see the model index land in a Python slot. "
        "Click a column header to sort.</p>")

    model = wt.WStandardItemModel(0, 3)
    model.set_header_data(0, "Name")
    model.set_header_data(1, "Role")
    model.set_header_data(2, "City")

    rows = [
        ("Alice",   "Engineer",  "Brooklyn"),
        ("Bob",     "Designer",  "Portland"),
        ("Carol",   "PM",        "Berlin"),
        ("Dan",     "Engineer",  "Tokyo"),
        ("Eve",     "Researcher", "Cambridge"),
        ("Frank",   "Engineer",  "Brooklyn"),
    ]
    for name, role, city in rows:
        model.append_row([
            wt.WStandardItem(name),
            wt.WStandardItem(role),
            wt.WStandardItem(city),
        ])

    # Slot a sort/filter proxy between the model and the view. Typing in
    # the filter box below mutates the proxy's regex, immediately reducing
    # the visible rows (dynamic_sort_filter=True). Click maps go through
    # the proxy to find the original row in the underlying model.
    proxy = wt.WSortFilterProxyModel()
    proxy.dynamic_sort_filter = True
    proxy.source_model = model
    proxy.filter_key_column = 1   # filter by Role

    c.add_widget(
        "<p>Filter on the Role column (regex, full-string match — wrap "
        "with <code>.*</code> for substring):</p>")
    filter_edit = c.add_widget(wt.WLineEdit())
    filter_edit.placeholder = ".*Engineer.*"

    def on_filter_changed() -> None:
        proxy.set_filter_regexp(filter_edit.text)
    filter_edit.text_input.connect(on_filter_changed)

    table = c.add_widget(wt.WTableView())
    table.model = proxy
    table.sorting_enabled = True
    table.column_resize_enabled = True
    table.selection_mode = wt.SelectionMode.Single
    table.selection_behavior = wt.SelectionBehavior.SelectRows

    log = c.add_widget(wt.WText("<i>(click a cell)</i>"))

    def on_click(proxy_idx: wt.WModelIndex, _event: wt.WMouseEvent) -> None:
        if not proxy_idx.is_valid:
            log.text = "<i>(invalid index)</i>"
            return
        # Click coordinates are in the proxy's frame; map back to the
        # source to fetch the underlying item.
        source_idx = proxy.map_to_source(proxy_idx)
        value = model.display_data(source_idx)
        log.text = (
            f"clicked proxy row=<b>{proxy_idx.row}</b> → source row="
            f"<b>{source_idx.row}</b>, col=<b>{source_idx.column}</b>: "
            f"<code>{value}</code>")
    table.clicked.connect(on_click)

    return c


def make_chrome_tab() -> wt.WContainerWidget:
    """Navigation chrome: WNavigationBar, WToolBar, WPopupMenu, WSplitButton,
    WBadge.

    The nav-bar at the top hosts a title link plus a menu and a search
    field. Below it, a toolbar lined with WPushButtons and a WSplitButton
    demonstrates the chrome surface. The split button's dropdown is a
    WPopupMenu wired to a log line. A WBadge counts dropdown selections.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>Navigation chrome</h3>")

    # ---- WNavigationBar ----
    nav = c.add_widget(wt.WNavigationBar())
    nav.set_title("witty_for_python", wt.WLink("https://adamdeprince.com"))
    nav.set_responsive(True)

    # The nav-bar's menu needs a WStackedWidget so item selection can swap
    # an associated contents pane. Here we keep the menu purely decorative
    # — the stack is empty.
    contents = c.add_widget(wt.WStackedWidget())
    contents.hidden = True   # we don't actually show items
    nav_menu = nav.add_menu(wt.WMenu(contents))
    nav_menu.add_item("Home")
    nav_menu.add_item("Docs")
    nav_menu.add_item("About")

    search = nav.add_search(wt.WLineEdit(), wt.AlignmentFlag.Right)
    search.placeholder = "search…"

    # ---- WToolBar ----
    c.add_widget("<h4>WToolBar</h4>")
    tools = c.add_widget(wt.WToolBar())

    log = c.add_widget(wt.WText("<i>(no toolbar action yet)</i>"))
    counter_badge = c.add_widget(wt.WBadge("0"))

    state = {"hits": 0}

    def hit(label: str) -> None:
        state["hits"] += 1
        counter_badge.text = str(state["hits"])
        log.text = f"clicked <b>{label}</b>"

    for label in ("Save", "Reload"):
        btn = tools.add_button(wt.WPushButton(label))
        btn.clicked.connect(lambda label=label: hit(label))

    tools.add_separator()

    # ---- WSplitButton with a WPopupMenu dropdown ----
    split = tools.add_button(wt.WSplitButton("Export"))
    split.action_button.clicked.connect(lambda: hit("Export (default)"))

    menu = wt.WPopupMenu()
    for fmt in ("CSV", "JSON", "PDF", "XLSX"):
        item = menu.add_item(fmt)
        # MenuItem.triggered is a per-item click; we use the menu-level
        # triggered signal below for the generic case.
        del item
    def on_menu_pick(item: wt.WMenuItem) -> None:
        hit(f"Export → {item.text}")
    menu.triggered.connect(on_menu_pick)
    split.set_menu(menu)

    return c


def make_leaflet_tab() -> wt.WContainerWidget:
    """WLeafletMap fed an OpenStreetMap tile layer.

    Demonstrates the wt.Json bridge: tile-layer options are built from
    a Python dict + handed to add_tile_layer as a Json.Object. No API
    key required — OpenStreetMap's public tiles are free for low-volume
    use (the gallery, in this case).
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>WLeafletMap (OpenStreetMap)</h3>")
    c.add_widget(
        "<p>An interactive Leaflet map fed an OpenStreetMap tile layer. "
        "The tile-layer options are a Python dict, marshalled to "
        "<code>wt.Json.Object</code> by the binding. "
        "Drag to pan, scroll to zoom.</p>")

    map_opts = wt.Json.Object({
        "center": [40.7128, -74.0060],   # New York
        "zoom": 11,
    })
    osm_opts = wt.Json.Object({
        "maxZoom": 19,
        "attribution":
            '&copy; <a href="https://www.openstreetmap.org/copyright">'
            'OpenStreetMap</a> contributors',
    })

    leaflet = c.add_widget(wt.WLeafletMap(map_opts))
    leaflet.add_tile_layer(
        "https://tile.openstreetmap.org/{z}/{x}/{y}.png", osm_opts)
    leaflet.set_width(500)
    leaflet.set_height(400)

    # ---- markers + popups + tooltip ----
    log = c.add_widget(wt.WText("<i>zoom: 11</i>"))

    # Three landmarks. Each gets a popup (click) + tooltip (hover).
    landmarks = [
        (40.7484, -73.9857, "Empire State Building",
         "Art Deco icon, opened 1931."),
        (40.6892, -74.0445, "Statue of Liberty",
         "Gift from France, 1886."),
        (40.7128, -74.0060, "New York City",
         "Pop. ~8.3 million."),
    ]
    for lat, lon, title, body in landmarks:
        marker = leaflet.add_marker(
            wt.WLeafletMap.LeafletMarker(
                wt.WLeafletMap.Coordinate(lat, lon)))
        marker.add_popup(
            wt.WLeafletMap.Popup(f"<b>{title}</b><br>{body}"))
        marker.add_tooltip(
            wt.WLeafletMap.Tooltip(title))
        # Mark the marker as interactive so its clicked signal fires.
        # (Default Leaflet markers are interactive; we wire the signal
        # to update the log.)
        def make_handler(t: str = title) -> "callable":
            def handler() -> None:
                log.text = f"clicked: <b>{t}</b>"
            return handler
        marker.clicked.connect(make_handler())

    def on_zoom_change(level: int) -> None:
        log.text = f"zoom: <b>{level}</b>"
    leaflet.zoom_level_changed.connect(on_zoom_change)
    return c


def make_niches_tab() -> wt.WContainerWidget:
    """Small niches: WQrCode + a WPaintedWidget demo with gradients/shadow.

    Doesn't include WGoogleMap because that needs a `google_api_key`
    config property which the gallery doesn't ship. The QR code is fully
    standalone.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>Niches</h3>")

    # ---- WQrCode ----
    c.add_widget("<h4>WQrCode</h4>")
    qr = c.add_widget(wt.WQrCode("https://adamdeprince.com",
                                 wt.ErrorCorrectionLevel.Medium, 6.0))
    qr.brush = wt.WBrush(wt.WColor(0x20, 0x40, 0x80))
    c.add_widget("<p>QR code encoded with medium ECL, painted in a "
                 "custom blue. Scan it to land on the author's site.</p>")

    # ---- WPaintedWidget driven by gradients + shadow ----
    c.add_widget("<h4>Gradient + shadow demo</h4>")

    def paint(p: wt.WPainter) -> None:
        # Drop shadow under everything.
        p.set_shadow(wt.WShadow(4.0, 4.0, wt.WColor(0, 0, 0, 80), 6.0))

        # Gradient-filled rectangle.
        g1 = wt.WGradient()
        g1.set_linear_gradient(0, 0, 200, 0)
        g1.add_color_stop(0.0, wt.WColor(0xff, 0x40, 0x40))
        g1.add_color_stop(1.0, wt.WColor(0x40, 0x40, 0xff))
        p.set_brush(wt.WBrush(g1))
        p.set_pen(wt.WPen())   # no stroke
        p.draw_rect(20, 20, 200, 100)

        # Radial-gradient circle.
        g2 = wt.WGradient()
        g2.set_radial_gradient(330, 70, 50, 320, 60)
        g2.add_color_stop(0.0, wt.WColor(0xff, 0xff, 0xff))
        g2.add_color_stop(1.0, wt.WColor(0xc0, 0x40, 0x80))
        p.set_brush(wt.WBrush(g2))
        p.draw_ellipse(280, 20, 100, 100)

        # Clear shadow so the label doesn't blur.
        p.set_shadow(wt.WShadow())
        p.set_brush(wt.WBrush(wt.WColor(0, 0, 0)))
        center = int(wt.AlignmentFlag.Center) | int(wt.AlignmentFlag.Middle)
        p.draw_text(20, 140, 360, 30, center,
                    "linear & radial gradients, with drop-shadow")

    canvas = c.add_widget(wt.WPaintedWidget(paint))
    canvas.set_width(400)
    canvas.set_height(200)
    return c


def make_chart_tab() -> wt.WContainerWidget:
    """WCartesianChart + WPieChart over a small in-memory dataset.

    The cartesian chart is fed a 6-row WStandardItemModel where the
    first column is X (month names) and the next three are Y values
    (different series). The pie chart shares the same model, slicing
    by month.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>Charts</h3>")
    c.add_widget(
        "<p>Two charts driven by the same <code>WStandardItemModel</code>. "
        "Painting subsystem under the hood — each chart subclasses "
        "<code>WPaintedWidget</code> in C++.</p>")

    # ---- Build a small model -------------------------------------------
    model = wt.WStandardItemModel(6, 4)
    model.set_header_data(0, "Month")
    model.set_header_data(1, "Apples")
    model.set_header_data(2, "Oranges")
    model.set_header_data(3, "Pears")
    data = [
        ("Jan", 12, 18, 8),
        ("Feb", 16, 14, 11),
        ("Mar", 22, 13, 17),
        ("Apr", 30, 11, 20),
        ("May", 28, 19, 22),
        ("Jun", 19, 24, 14),
    ]
    for r, (m, a, o, p) in enumerate(data):
        model.set_item(r, 0, wt.WStandardItem(m))
        model.set_item(r, 1, wt.WStandardItem(str(a)))
        model.set_item(r, 2, wt.WStandardItem(str(o)))
        model.set_item(r, 3, wt.WStandardItem(str(p)))

    # ---- Bar chart -----------------------------------------------------
    c.add_widget("<h4>WCartesianChart (bar)</h4>")
    bar = c.add_widget(wt.chart.WCartesianChart(wt.chart.ChartType.Category))
    bar.set_model(model)
    bar.x_series_column = 0
    bar.legend_enabled = True
    bar.set_title("Sales by fruit")
    for col, series_color in [
        (1, wt.WColor(0xc0, 0x40, 0x40)),
        (2, wt.WColor(0xe0, 0x90, 0x20)),
        (3, wt.WColor(0x40, 0x80, 0xc0)),
    ]:
        s = wt.chart.WDataSeries(col, wt.chart.SeriesType.Bar)
        s.set_brush(wt.WBrush(series_color))
        bar.add_series(s)
    bar.set_width(500)
    bar.set_height(300)

    # ---- Pie chart -----------------------------------------------------
    c.add_widget("<h4>WPieChart (apples only)</h4>")
    pie = c.add_widget(wt.chart.WPieChart())
    pie.set_model(model)
    pie.set_labels_column(0)   # month names
    pie.set_data_column(1)     # apples column
    pie.set_display_labels(
        int(wt.chart.LabelOption.Outside)
        | int(wt.chart.LabelOption.TextLabel)
        | int(wt.chart.LabelOption.TextPercentage))
    pie.set_perspective_enabled(True, 0.4)
    pie.set_shadow_enabled(True)
    pie.set_width(400)
    pie.set_height(300)
    return c


def make_pdf_tab() -> wt.WContainerWidget:
    """WPdfImage — generate a PDF in-memory and serve it via a link.

    The WPdfImage is a WResource subclass, so we just point a WAnchor
    at it. Wt's wthttpd serves the PDF bytes when the user clicks; no
    intermediate file lands on disk.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>WPdfImage — paint into a PDF</h3>")
    c.add_widget(
        "<p>A small PDF generated on demand by libharu, with content "
        "drawn through the same <code>WPainter</code> API used for "
        "screen rendering. Click the link to download.</p>")

    # A4 in PDF points (1/72 inch).
    pdf = wt.WPdfImage(
        wt.WLength(595, wt.LengthUnit.Point),
        wt.WLength(842, wt.LengthUnit.Point))
    pdf.suggest_file_name("witty_demo.pdf")
    pdf.set_disposition_type(wt.ContentDisposition.Attachment)

    # Paint into the PDF using the bound WPainter API.
    p = wt.WPainter(pdf)
    p.set_brush(wt.WBrush(wt.WColor(0xa0, 0xc0, 0xe0)))
    p.set_pen(wt.WPen())
    p.draw_rect(50, 50, 200, 100)
    p.set_brush(wt.WBrush(wt.WColor(0, 0, 0)))
    title_font = wt.WFont(wt.FontFamily.SansSerif)
    title_font.set_size(wt.WLength(20))
    p.set_font(title_font)
    align = int(wt.AlignmentFlag.Left) | int(wt.AlignmentFlag.Top)
    p.draw_text(50, 180, 495, 30, align,
                "Generated by witty_for_python")
    body_font = wt.WFont(wt.FontFamily.Serif)
    body_font.set_size(wt.WLength(12))
    p.set_font(body_font)
    p.draw_text(50, 220, 495, 100, align,
                "This PDF was rendered server-side by libharu via Wt's "
                "WPainter API, then served as a WResource through the "
                "session's wthttpd connector.")
    # Releasing the painter flushes its operations to the device.
    del p

    c.add_widget(wt.WAnchor(pdf, "Download witty_demo.pdf"))
    return c


def make_painting_tab() -> wt.WContainerWidget:
    """WPaintedWidget driven by a Python paint callback.

    Demonstrates the value-types (WPointF, WRectF, WBrush, WPen), the
    builder-style WPainterPath, and stateful WPainter operations
    (save/restore, translate/rotate). The Redraw button calls
    widget.update() to schedule a fresh paintEvent — useful when the
    paint callback closes over Python state that has changed.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>WPaintedWidget</h3>")
    c.add_widget(
        "<p>The shape below is rendered every paint event by a Python "
        "callback that receives a <code>WPainter</code>. The button "
        "rotates the shape one step and triggers a redraw.</p>")

    state = {"angle": 0.0}

    def paint(p: wt.WPainter) -> None:
        # Filled shape with a translucent stroke.
        p.set_brush(wt.WBrush(wt.WColor(0xa0, 0xc0, 0xe0)))
        pen = wt.WPen(wt.WColor(0x20, 0x40, 0x80))
        pen.set_width(wt.WLength(2))
        p.set_pen(pen)

        # Translate to centre + rotate by the current state-angle, then
        # draw a path so the rotation is visible.
        p.save()
        p.translate(150, 150)
        p.rotate(state["angle"])

        path = wt.WPainterPath()
        path.move_to(0, -80)
        path.line_to(70, 50)
        path.line_to(-70, 50)
        path.close_sub_path()
        p.draw_path(path)

        # Add a label inside the shape; centred via Center | Middle.
        p.set_brush(wt.WBrush(wt.WColor(0xff, 0xff, 0xff)))
        center_align = int(wt.AlignmentFlag.Center) | int(wt.AlignmentFlag.Middle)
        p.draw_text(-40, -20, 80, 40, center_align,
                    f"{int(state['angle']) % 360}°")
        p.restore()

        # A reference grid (unrotated, around the shape).
        grid_pen = wt.WPen(wt.WColor(200, 200, 200))
        grid_pen.set_style(wt.PenStyle.DashLine)
        p.set_pen(grid_pen)
        for i in range(0, 300, 30):
            p.draw_line(0, i, 300, i)
            p.draw_line(i, 0, i, 300)

    canvas = c.add_widget(wt.WPaintedWidget(paint))
    canvas.set_width(300)
    canvas.set_height(300)
    canvas.set_preferred_method(wt.RenderMethod.HtmlCanvas)

    btn = c.add_widget(wt.WPushButton("Rotate 15°"))
    def rotate() -> None:
        state["angle"] += 15.0
        canvas.update()
    btn.clicked.connect(rotate)
    return c


def make_media_tab() -> wt.WContainerWidget:
    """WAudio + WVideo + WMediaPlayer.

    No actual media is bundled with the gallery — we point the widgets
    at the canonical sample-content URLs Mozilla hosts publicly. If
    you're running this without internet access the players will show
    their fallback (alternative-content) UI instead.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>Media</h3>")
    c.add_widget(
        "<p>Three media widgets. <b>WAudio</b> and <b>WVideo</b> use "
        "the browser's native &lt;audio&gt;/&lt;video&gt; controls; "
        "<b>WMediaPlayer</b> renders Wt-skinned controls via jPlayer "
        "(slightly more setup, more uniform look).</p>")

    # ---- WAudio ----
    c.add_widget("<h4>WAudio</h4>")
    audio = c.add_widget(wt.WAudio())
    audio.add_source(wt.WLink(
        "https://archive.org/download/testmp3testfile/mpthreetest.mp3"),
        "audio/mpeg")
    audio.set_options(int(wt.PlayerOption.Controls))
    audio.set_preload_mode(wt.MediaPreloadMode.Metadata)
    audio.set_alternative_content(
        wt.WText("<i>(your browser can't play this audio)</i>"))

    audio_log = c.add_widget(wt.WText(""))

    def on_audio_start() -> None:
        audio_log.text = "playing…"
    def on_audio_pause() -> None:
        audio_log.text = "paused"
    def on_audio_end() -> None:
        audio_log.text = "finished"
    audio.playback_started.connect(on_audio_start)
    audio.playback_paused.connect(on_audio_pause)
    audio.ended.connect(on_audio_end)

    # ---- WVideo ----
    c.add_widget("<h4>WVideo</h4>")
    video = c.add_widget(wt.WVideo())
    video.add_source(wt.WLink(
        "https://archive.org/download/BigBuckBunny_124/Content/big_buck_bunny_720p_surround.mp4"),
        "video/mp4")
    video.set_options(int(wt.PlayerOption.Controls))
    video.set_preload_mode(wt.MediaPreloadMode.Metadata)
    video.set_poster(
        "https://upload.wikimedia.org/wikipedia/commons/c/c5/Big_buck_bunny_poster_big.jpg")
    video.set_alternative_content(
        wt.WText("<i>(your browser can't play this video)</i>"))
    return c


def make_quick_wins_tab() -> wt.WContainerWidget:
    """Bits from the 'quick wins' bundle: WLength, WIcon, WIconPair,
    WBorderLayout in a small demo, and an animated show/hide on a
    container using WAnimation.
    """
    c = wt.WContainerWidget()
    c.add_widget("<h3>Quick wins</h3>")

    # ---- WIcon + WIconPair ----
    c.add_widget("<h4>WIcon + WIconPair</h4>")
    row = c.add_widget(wt.WContainerWidget())
    row.add_widget("Inline icon: ")
    row.add_widget(wt.WIcon("play"))
    row.add_widget("&nbsp;&nbsp;Togglable pair (click an icon): ")
    pair = row.add_widget(wt.WIconPair("play", "pause", True))
    pair.set_icons_type(wt.IconType.IconName)
    pair_log = c.add_widget(wt.WText("(state 0 — first icon)"))

    def on_pair_changed(_e: wt.WMouseEvent) -> None:
        pair_log.text = f"state {pair.state} — icon{pair.state + 1} visible"
    pair.icon1_clicked.connect(on_pair_changed)
    pair.icon2_clicked.connect(on_pair_changed)

    # ---- WLength: explicit units on a sized box ----
    c.add_widget("<h4>WLength sizing</h4>")
    sized = c.add_widget(wt.WContainerWidget())
    sized.style_class = "Wt-filedropzone"   # reuse Bootstrap-styled border
    # Width / height accept native units; we wrap an explicit WLength.
    sized.add_widget(
        "<p style='padding:0.5em;'>This container is fixed at "
        f"<code>{wt.WLength(20, wt.LengthUnit.FontEm).to_css_text()}</code> "
        "wide. WLength values render to CSS via "
        "<code>to_css_text()</code>.</p>")

    # ---- WAnimation: animated show/hide ----
    c.add_widget("<h4>WAnimation</h4>")
    c.add_widget(
        "<p>Click <b>Toggle</b> to animate the box below in / out.</p>")
    target = c.add_widget(wt.WContainerWidget())
    target.style_class = "Wt-filedropzone"
    target.add_widget(
        "<p style='padding:0.5em;'>Hello — I appear with a "
        "<b>SlideInFromLeft + Fade</b> effect.</p>")

    anim = wt.WAnimation(
        int(wt.AnimationEffect.SlideInFromLeft) | int(wt.AnimationEffect.Fade),
        wt.TimingFunction.EaseOut,
        400)

    btn = c.add_widget(wt.WPushButton("Toggle"))
    state = {"shown": True}
    def toggle() -> None:
        if state["shown"]:
            target.animate_hide(anim)
        else:
            target.animate_show(anim)
        state["shown"] = not state["shown"]
    btn.clicked.connect(toggle)

    return c


# ---- Application factory + server bootstrap ----

def create_app(env: wt.WEnvironment) -> wt.WApplication:
    app = wt.WApplication(env)
    app.title = "witty_for_python gallery"

    root = app.root
    root.add_widget("<h2>witty_for_python gallery</h2>")
    root.add_widget(
        "<p>Each tab exercises a section of the bound API. Signals connect "
        "Python slots across the C++/Python boundary &mdash; payloads "
        "(<code>WMouseEvent</code>, enums, ints, strings) flow through "
        "<code>nb::cast</code> with copy semantics.</p>")

    tabs = root.add_widget(wt.WTabWidget())
    tabs.add_tab(make_basics_tab(), "Basics")
    tabs.add_tab(make_form_tab(), "Form widgets")
    tabs.add_tab(make_layout_tab(), "Layout")
    tabs.add_tab(make_table_tab(), "Table")
    tabs.add_tab(make_dialog_tab(), "Dialogs")
    tabs.add_tab(make_events_tab(), "Events")
    tabs.add_tab(make_template_tab(), "Template")
    tabs.add_tab(make_resources_tab(), "Resources")
    tabs.add_tab(make_upload_tab(), "Upload")
    tabs.add_tab(make_filedrop_tab(), "Drop zone")
    tabs.add_tab(make_extras_tab(), "Extras")
    tabs.add_tab(make_chrome_tab(), "Chrome")
    tabs.add_tab(make_modelview_tab(), "Data")
    tabs.add_tab(make_quick_wins_tab(), "Quick wins")
    tabs.add_tab(make_media_tab(), "Media")
    tabs.add_tab(make_painting_tab(), "Painting")
    tabs.add_tab(make_pdf_tab(), "PDF")
    tabs.add_tab(make_chart_tab(), "Charts")
    tabs.add_tab(make_niches_tab(), "Niches")
    tabs.add_tab(make_leaflet_tab(), "Map")
    tabs.add_tab(make_timer_tab(), "Timer")

    # Apply Bootstrap5 theme so the gallery looks modern. The theme is owned
    # via shared_ptr; assigning it to `app.theme` hands ownership to the app.
    app.theme = wt.WBootstrap5Theme()
    return app


def main(argv: list[str]) -> int:
    # Default --resources-dir to the path bundled with witty_for_python. Wt
    # needs it to serve its built-in CSS/JS/themes; the user no longer has to
    # know where those live on disk. If they pass --resources-dir explicitly,
    # we leave their value alone.
    if not any(a == "--resources-dir" or a.startswith("--resources-dir=")
               for a in argv[1:]):
        argv = argv + ["--resources-dir", wt.resources_dir]

    server = wt.WServer()
    server.set_server_configuration(argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)
    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
