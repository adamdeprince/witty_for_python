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
    panel.set_collapsible(True)
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
    dlg.set_modal(True)
    dlg.set_closable(True)
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
    target.placeholder_text = "fruit name…"

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
    search.placeholder_text = "search…"

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
