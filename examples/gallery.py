"""witty_for_python gallery — exercises the full binding surface.

A condensed Python port of Wt's `examples/widgetgallery/FormWidgets.C` plus a
walking tour of the rest of witty_for_python's widgets: basics, layout, table, dialogs,
and event-payload demos. Each section connects at least one signal to a
Python slot so the C++/Python signal bridge is exercised end-to-end.

Run:

    python examples/gallery.py --docroot . \\
        --http-address 127.0.0.1 --http-port 8080 \\
        --resources-dir ~/.local/share/Wt/resources

Then open http://127.0.0.1:8080.
"""

from __future__ import annotations

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
    return app


def main(argv: list[str]) -> int:
    server = wt.WServer()
    server.set_server_configuration(argv)
    server.add_entry_point(wt.EntryPointType.Application, create_app)
    return server.run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
