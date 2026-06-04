#include "common.hpp"

#include <Wt/WBreak.h>
#include <Wt/WButtonGroup.h>
#include <Wt/WComboBox.h>
#include <Wt/WDoubleSpinBox.h>
#include <Wt/WFormWidget.h>
#include <Wt/WGlobal.h>      // Wt::Orientation, Wt::SelectionMode
#include <Wt/WImage.h>
#include <Wt/WLabel.h>
#include <Wt/WLineEdit.h>
#include <Wt/WProgressBar.h>
#include <Wt/WRadioButton.h>
#include <Wt/WSelectionBox.h>
#include <Wt/WSlider.h>
#include <Wt/WSpinBox.h>
#include <Wt/WTextArea.h>

#include <memory>
#include <set>
#include <string>

namespace witty_for_python {

void register_form(nb::module_& m) {
    // ---- Enums used by form widgets ----

    nb::enum_<Wt::Orientation>(m, "Orientation", nb::is_arithmetic(),
        "Layout axis. `Horizontal` lays things out left-to-right;\n"
        "`Vertical` lays things out top-to-bottom. Used by WSlider and\n"
        "other widgets that have a natural axis.")
        .value("Horizontal", Wt::Orientation::Horizontal)
        .value("Vertical", Wt::Orientation::Vertical);

    nb::enum_<Wt::SelectionMode>(m, "SelectionMode",
        "Selection policy for list-style widgets. `None_` disables\n"
        "selection entirely, `Single` allows one selected row at a time,\n"
        "and `Extended` lets the user pick multiple rows with Ctrl/Shift.")
        .value("None_", Wt::SelectionMode::None)
        .value("Single", Wt::SelectionMode::Single)
        .value("Extended", Wt::SelectionMode::Extended);

    // ---- WLabel: a text or image label, optionally bound to a form widget ----

    nb::class_<Wt::WLabel, Wt::WInteractWidget>(m, "WLabel",
        "An HTML `<label>` element. Renders short text (or an image) that\n"
        "describes a sibling form input; clicking the label transfers\n"
        "focus to the buddy.\n"
        "\n"
        "    edit = container.add_widget(wt.WLineEdit())\n"
        "    label = container.add_widget(wt.WLabel('Email:'))\n"
        "    label.set_buddy(edit)")
        .def(heap_init<Wt::WLabel>(),
             "Construct an empty label with no text or image.")
        .def(heap_init<Wt::WLabel, const Wt::WString&>(), "text"_a,
             "Construct a label displaying `text`.")
        .def_prop_rw("text",
            [](const Wt::WLabel& w) { return w.text(); },
            [](Wt::WLabel& w, const Wt::WString& t) { w.setText(t); },
            "The label's text. Assigning replaces the current content.")
        .def("set_buddy", &Wt::WLabel::setBuddy, "buddy"_a,
             "Associate the label with a form widget. Clicking the label\n"
             "then forwards focus to `buddy` (the HTML `for` attribute is\n"
             "wired to the buddy's id).")
        .def_prop_rw("word_wrap",
            [](const Wt::WLabel& w) { return w.wordWrap(); },
            [](Wt::WLabel& w, bool b) { w.setWordWrap(b); },
            "Whether long text wraps to multiple lines. When False the\n"
            "label is rendered on a single line.")
        .def("set_image",
            [](Wt::WLabel& w, nb::object py_img) {
                auto img = nb::cast<std::unique_ptr<Wt::WImage>>(py_img);
                w.setImage(std::move(img));
                nb::inst_set_state(py_img, /*ready*/ true,
                                   /*destruct*/ false);
            },
            "image"_a,
            "Display a WImage in place of (or alongside) the label text.\n"
            "Takes ownership of `image`; the Python wrapper is re-armed\n"
            "as a non-owning alias.");

    // ---- WBreak: a <br> element ----
    // Inherits WWebWidget in C++ but the closest type Python knows about is
    // WWidget — that is enough for parent-pointer compatibility.

    nb::class_<Wt::WBreak, Wt::WWidget>(m, "WBreak",
        "A line break — renders as `<br>`. Drop one into a container to\n"
        "force the following widget onto a new line.\n"
        "\n"
        "    container.add_widget(wt.WText('First line'))\n"
        "    container.add_widget(wt.WBreak())\n"
        "    container.add_widget(wt.WText('Second line'))")
        .def(heap_init<Wt::WBreak>(),
             "Construct a line break.");

    // ---- WTextArea: multi-line text input ----

    nb::class_<Wt::WTextArea, Wt::WFormWidget>(m, "WTextArea",
        "Multi-line text input — renders as `<textarea>`. Use for longer\n"
        "free-form input that wouldn't fit on a single line.\n"
        "\n"
        "    notes = container.add_widget(wt.WTextArea())\n"
        "    notes.rows = 8\n"
        "    notes.columns = 60\n"
        "    notes.placeholder = 'Add notes…'")
        .def(heap_init<Wt::WTextArea>(),
             "Construct an empty text area.")
        .def(heap_init<Wt::WTextArea, const Wt::WString&>(), "text"_a,
             "Construct a text area pre-filled with `text`.")
        .def_prop_rw("text",
            [](const Wt::WTextArea& w) { return w.text(); },
            [](Wt::WTextArea& w, const Wt::WString& t) { w.setText(t); },
            "The current input value. Reads what the user has typed;\n"
            "assigning replaces the contents.")
        .def_prop_rw("rows",
            [](const Wt::WTextArea& w) { return w.rows(); },
            [](Wt::WTextArea& w, int n) { w.setRows(n); },
            "Visible row count — the HTML `rows` attribute.")
        .def_prop_rw("columns",
            [](const Wt::WTextArea& w) { return w.columns(); },
            [](Wt::WTextArea& w, int n) { w.setColumns(n); },
            "Visible column count — the HTML `cols` attribute.")
        .def_prop_rw("placeholder",
            [](const Wt::WTextArea& w) { return w.placeholderText(); },
            [](Wt::WTextArea& w, const Wt::WString& t) { w.setPlaceholderText(t); },
            "Greyed-out hint shown when the field is empty.")
        .def_prop_ro("selection_start", &Wt::WTextArea::selectionStart,
            "Character index where the current text selection begins, or\n"
            "-1 if there is no selection.")
        .def_prop_ro("has_selected_text", &Wt::WTextArea::hasSelectedText,
            "True if the user currently has text selected.")
        .def_prop_ro("cursor_position", &Wt::WTextArea::cursorPosition,
            "Character index of the caret, as of the last client update.");

    // ---- Spin boxes: integer + double ----
    // Both inherit WLineEdit via WAbstractSpinBox; the intermediate is elided
    // on the Python side since we don't expose its methods.

    nb::class_<Wt::WSpinBox, Wt::WLineEdit>(m, "WSpinBox",
        "Integer-valued numeric input with up/down stepper buttons.\n"
        "\n"
        "    qty = container.add_widget(wt.WSpinBox())\n"
        "    qty.set_range(1, 99)\n"
        "    qty.single_step = 1\n"
        "    qty.value_changed.connect(lambda v: print('picked', v))")
        .def(heap_init<Wt::WSpinBox>(),
             "Construct a spin box at value 0.")
        .def_prop_rw("value",
            [](const Wt::WSpinBox& w) { return w.value(); },
            [](Wt::WSpinBox& w, int v) { w.setValue(v); },
            "The current integer value.")
        .def_prop_rw("minimum",
            [](const Wt::WSpinBox& w) { return w.minimum(); },
            [](Wt::WSpinBox& w, int v) { w.setMinimum(v); },
            "Lower bound on `value` enforced by the stepper buttons.")
        .def_prop_rw("maximum",
            [](const Wt::WSpinBox& w) { return w.maximum(); },
            [](Wt::WSpinBox& w, int v) { w.setMaximum(v); },
            "Upper bound on `value` enforced by the stepper buttons.")
        .def_prop_rw("single_step",
            [](const Wt::WSpinBox& w) { return w.singleStep(); },
            [](Wt::WSpinBox& w, int v) { w.setSingleStep(v); },
            "Amount the stepper buttons add or subtract per click.")
        .def("set_range", &Wt::WSpinBox::setRange, "minimum"_a, "maximum"_a,
             "Set `minimum` and `maximum` in a single call.")
        .def_prop_rw("wrap_around",
            [](const Wt::WSpinBox& w) { return w.wrapAroundEnabled(); },
            [](Wt::WSpinBox& w, bool b) { w.setWrapAroundEnabled(b); },
            "Whether stepping past the maximum loops back to the minimum\n"
            "(and vice-versa).")
        .def_prop_ro("value_changed", &Wt::WSpinBox::valueChanged,
                     nb::rv_policy::reference_internal,
                     "Fires with the new int value whenever the user\n"
                     "commits a change.");

    nb::class_<Wt::WDoubleSpinBox, Wt::WLineEdit>(m, "WDoubleSpinBox",
        "Floating-point spin box. Same surface as WSpinBox but the value\n"
        "is a double and `decimals` controls display precision.\n"
        "\n"
        "    price = container.add_widget(wt.WDoubleSpinBox())\n"
        "    price.set_range(0.0, 1000.0)\n"
        "    price.decimals = 2\n"
        "    price.single_step = 0.05")
        .def(heap_init<Wt::WDoubleSpinBox>(),
             "Construct a spin box at value 0.0.")
        .def_prop_rw("value",
            [](const Wt::WDoubleSpinBox& w) { return w.value(); },
            [](Wt::WDoubleSpinBox& w, double v) { w.setValue(v); },
            "The current double value.")
        .def_prop_rw("minimum",
            [](const Wt::WDoubleSpinBox& w) { return w.minimum(); },
            [](Wt::WDoubleSpinBox& w, double v) { w.setMinimum(v); },
            "Lower bound on `value`.")
        .def_prop_rw("maximum",
            [](const Wt::WDoubleSpinBox& w) { return w.maximum(); },
            [](Wt::WDoubleSpinBox& w, double v) { w.setMaximum(v); },
            "Upper bound on `value`.")
        .def_prop_rw("single_step",
            [](const Wt::WDoubleSpinBox& w) { return w.singleStep(); },
            [](Wt::WDoubleSpinBox& w, double v) { w.setSingleStep(v); },
            "Amount the stepper buttons add or subtract per click.")
        .def_prop_rw("decimals",
            [](const Wt::WDoubleSpinBox& w) { return w.decimals(); },
            [](Wt::WDoubleSpinBox& w, int n) { w.setDecimals(n); },
            "Number of decimal places shown when formatting `value`.")
        .def("set_range", &Wt::WDoubleSpinBox::setRange,
             "minimum"_a, "maximum"_a,
             "Set `minimum` and `maximum` in a single call.")
        .def_prop_ro("value_changed", &Wt::WDoubleSpinBox::valueChanged,
                     nb::rv_policy::reference_internal,
                     "Fires with the new double value whenever the user\n"
                     "commits a change.");

    // ---- WSlider ----

    nb::class_<Wt::WSlider, Wt::WFormWidget>(m, "WSlider",
        "Integer slider — a draggable handle along a track. Orientation\n"
        "can be horizontal (default) or vertical.\n"
        "\n"
        "    vol = container.add_widget(wt.WSlider(wt.Orientation.Horizontal))\n"
        "    vol.set_range(0, 100)\n"
        "    vol.tick_interval = 10\n"
        "    vol.value_changed.connect(lambda v: mixer.set_volume(v))")
        .def(heap_init<Wt::WSlider>(),
             "Construct a horizontal slider at value 0.")
        .def(heap_init<Wt::WSlider, Wt::Orientation>(), "orientation"_a,
             "Construct a slider with the given orientation.")
        .def_prop_rw("value",
            [](const Wt::WSlider& w) { return w.value(); },
            [](Wt::WSlider& w, int v) { w.setValue(v); },
            "The current integer position along the track.")
        .def_prop_rw("minimum",
            [](const Wt::WSlider& w) { return w.minimum(); },
            [](Wt::WSlider& w, int v) { w.setMinimum(v); },
            "Value at the leftmost (or bottom-most) end of the track.")
        .def_prop_rw("maximum",
            [](const Wt::WSlider& w) { return w.maximum(); },
            [](Wt::WSlider& w, int v) { w.setMaximum(v); },
            "Value at the rightmost (or top-most) end of the track.")
        .def_prop_rw("step",
            [](const Wt::WSlider& w) { return w.step(); },
            [](Wt::WSlider& w, int v) { w.setStep(v); },
            "Smallest increment the handle snaps to as the user drags.")
        .def_prop_rw("tick_interval",
            [](const Wt::WSlider& w) { return w.tickInterval(); },
            [](Wt::WSlider& w, int v) { w.setTickInterval(v); },
            "Spacing between visible tick marks along the track. Zero\n"
            "disables tick rendering.")
        .def("set_range", &Wt::WSlider::setRange, "minimum"_a, "maximum"_a,
             "Set `minimum` and `maximum` in a single call.")
        .def("set_orientation", &Wt::WSlider::setOrientation, "orientation"_a,
             "Switch between Horizontal and Vertical layouts.")
        .def_prop_ro("value_changed", &Wt::WSlider::valueChanged,
                     nb::rv_policy::reference_internal,
                     "Fires with the new int value when the user moves\n"
                     "the handle.");

    // ---- WComboBox + WSelectionBox ----

    nb::class_<Wt::WComboBox, Wt::WFormWidget>(m, "WComboBox",
        "Drop-down list — renders as `<select>` with one row visible.\n"
        "Populate via `add_item` / `add_items` and observe selection\n"
        "changes through `activated` or `string_activated`.\n"
        "\n"
        "    cb = container.add_widget(wt.WComboBox())\n"
        "    cb.add_items(['Red', 'Green', 'Blue'])\n"
        "    cb.string_activated.connect(lambda s: print('picked', s))")
        .def(heap_init<Wt::WComboBox>(),
             "Construct an empty combo box.")
        .def("add_item", &Wt::WComboBox::addItem, "text"_a,
             "Append a new item with the given label to the end of the\n"
             "drop-down list.")
        // Python-only bulk variant of add_item. Loops the single-item form;
        // additive (rule §0) — no default behavior changes.
        .def("add_items",
             [](Wt::WComboBox& self, const std::vector<Wt::WString>& items) {
                 for (const auto& s : items) self.addItem(s);
             },
             "items"_a,
             "Bulk version of `add_item`. Appends each label in order.")
        .def("insert_item", &Wt::WComboBox::insertItem, "index"_a, "text"_a,
             "Insert a new item at position `index`; existing items at\n"
             "and after that position shift down.")
        .def("remove_item", &Wt::WComboBox::removeItem, "index"_a,
             "Remove the item at position `index`.")
        .def_prop_ro("count", &Wt::WComboBox::count,
            "Number of items currently in the drop-down.")
        .def("item_text", &Wt::WComboBox::itemText, "index"_a,
             "Return the label of the item at position `index`.")
        .def("set_item_text", &Wt::WComboBox::setItemText, "index"_a, "text"_a,
             "Replace the label of the item at position `index`.")
        .def_prop_rw("current_index",
            [](const Wt::WComboBox& w) { return w.currentIndex(); },
            [](Wt::WComboBox& w, int i) { w.setCurrentIndex(i); },
            "Index of the selected item, or -1 if none is selected.\n"
            "Assigning programmatically does NOT fire `activated`.")
        .def("clear", &Wt::WComboBox::clear,
             "Remove every item; the combo box ends up empty.")
        .def_prop_ro("activated", &Wt::WComboBox::activated,
                     nb::rv_policy::reference_internal,
                     "Fires with the int index of the newly-selected item\n"
                     "when the user picks something.")
        .def_prop_ro("string_activated", &Wt::WComboBox::sactivated,
                     nb::rv_policy::reference_internal,
                     "Fires with the WString label of the newly-selected\n"
                     "item. Convenient when you don't need the index.");

    nb::class_<Wt::WSelectionBox, Wt::WComboBox>(m, "WSelectionBox",
        "Multi-row list-box — renders as `<select size=N>` showing several\n"
        "items at once. Inherits the populate / query surface from\n"
        "WComboBox; adds vertical sizing and multi-select.\n"
        "\n"
        "    sb = container.add_widget(wt.WSelectionBox())\n"
        "    sb.add_items(['Apples', 'Pears', 'Plums'])\n"
        "    sb.vertical_size = 6\n"
        "    sb.set_selection_mode(wt.SelectionMode.Extended)")
        .def(heap_init<Wt::WSelectionBox>(),
             "Construct an empty selection box.")
        .def_prop_rw("vertical_size",
            [](const Wt::WSelectionBox& w) { return w.verticalSize(); },
            [](Wt::WSelectionBox& w, int n) { w.setVerticalSize(n); },
            "Number of rows visible without scrolling — the HTML `size`\n"
            "attribute.")
        .def("set_selection_mode", &Wt::WSelectionBox::setSelectionMode,
             "mode"_a,
             "Choose between Single and Extended selection (see\n"
             "SelectionMode).")
        .def("set_selected_indexes", &Wt::WSelectionBox::setSelectedIndexes,
             "selection"_a,
             "Replace the current selection with the given set of int\n"
             "indices. Only meaningful in Extended mode.")
        .def("clear_selection", &Wt::WSelectionBox::clearSelection,
             "Deselect every item.");

    // ---- WRadioButton + WButtonGroup ----
    //
    // WButtonGroup is owned by shared_ptr (Wt's API takes std::shared_ptr).
    // nanobind's shared_ptr caster keeps the Python wrapper alive while any
    // C++ buttons hold the group.

    // To put a radio button into a group, call group.add_button(button) on
    // the Python side — WRadioButton::setGroup() is private in Wt 4.13.
    nb::class_<Wt::WRadioButton, Wt::WFormWidget>(m, "WRadioButton",
        "A single radio button. On its own, a radio acts like a checkbox\n"
        "with a different glyph; the mutual-exclusion behavior comes from\n"
        "adding several to the same WButtonGroup.\n"
        "\n"
        "    group = wt.WButtonGroup()\n"
        "    red = container.add_widget(wt.WRadioButton('Red'))\n"
        "    grn = container.add_widget(wt.WRadioButton('Green'))\n"
        "    group.add_button(red)\n"
        "    group.add_button(grn)\n"
        "    red.on_check.connect(lambda: print('red'))")
        .def(heap_init<Wt::WRadioButton>(),
             "Construct an unlabelled radio button in the unchecked state.")
        .def(heap_init<Wt::WRadioButton, const Wt::WString&>(), "text"_a,
             "Construct a labelled radio; `text` renders next to the dot.")
        .def_prop_rw("checked",
            [](const Wt::WRadioButton& w) { return w.isChecked(); },
            [](Wt::WRadioButton& w, bool c) { w.setChecked(c); },
            "The current boolean state. Assigning programmatically does\n"
            "NOT fire `on_check`/`on_uncheck`.")
        .def_prop_ro("on_check",
            [](Wt::WRadioButton& w) -> Wt::EventSignal<>& {
                return w.checked();
            },
            nb::rv_policy::reference_internal,
            "Fires when the user selects this radio.")
        .def_prop_ro("on_uncheck",
            [](Wt::WRadioButton& w) -> Wt::EventSignal<>& {
                return w.unChecked();
            },
            nb::rv_policy::reference_internal,
            "Fires when this radio loses its selected state because a\n"
            "sibling in the same group was picked.");

    // WButtonGroup is special: its `addButton` calls `shared_from_this()`
    // internally, so the group MUST already live inside a std::shared_ptr
    // before any button is added. Construct via `make_shared` and return
    // it as shared_ptr — nanobind's shared_ptr from_cpp path stashes the
    // shared_ptr in keep_alive, so `weak_from_this()` resolves later.
    nb::class_<Wt::WButtonGroup, Wt::WObject>(m, "WButtonGroup",
        "Mutual-exclusion group for a set of WRadioButtons. Adding a\n"
        "radio to a group makes it part of the same logical choice — at\n"
        "most one button in the group can be checked at a time. The\n"
        "group itself is not a widget; it's a coordinator.\n"
        "\n"
        "    group = wt.WButtonGroup()\n"
        "    for label in ['Free', 'Pro', 'Enterprise']:\n"
        "        rb = container.add_widget(wt.WRadioButton(label))\n"
        "        group.add_button(rb)")
        .def(nb::new_([]() { return std::make_shared<Wt::WButtonGroup>(); }),
             "Construct an empty button group. Add WRadioButtons via\n"
             "`add_button`.")
        .def("add_button",
             nb::overload_cast<Wt::WRadioButton*, int>(&Wt::WButtonGroup::addButton),
             "button"_a, "id"_a = -1,
             "Enroll `button` in the group. `id` is an optional integer\n"
             "tag returned by `checked_id` — pass -1 (the default) to\n"
             "auto-assign.")
        .def("remove_button", &Wt::WButtonGroup::removeButton, "button"_a,
             "Detach `button` from the group. The button keeps existing\n"
             "as an independent radio.")
        .def_prop_ro("count", &Wt::WButtonGroup::count,
            "Number of buttons currently in the group.")
        .def_prop_ro("checked_id", &Wt::WButtonGroup::checkedId,
            "The `id` of the currently-selected button (the value passed\n"
            "to `add_button`), or -1 if none is selected.")
        .def_prop_rw("selected_button_index",
            [](const Wt::WButtonGroup& g) { return g.selectedButtonIndex(); },
            [](Wt::WButtonGroup& g, int i) { g.setSelectedButtonIndex(i); },
            "Position in insertion order of the selected button, or -1\n"
            "if none is selected. Assigning programmatically toggles the\n"
            "corresponding radio's state.");

    // ---- WProgressBar ----

    nb::class_<Wt::WProgressBar, Wt::WInteractWidget>(m, "WProgressBar",
        "A horizontal progress indicator. Set `value` between `minimum`\n"
        "and `maximum` to render the fill, optionally annotate with a\n"
        "format string for the percentage label.\n"
        "\n"
        "    bar = container.add_widget(wt.WProgressBar())\n"
        "    bar.set_range(0, 100)\n"
        "    bar.value = 42")
        .def(heap_init<Wt::WProgressBar>(),
             "Construct a progress bar with range 0..100 and value 0.")
        .def_prop_rw("value",
            [](const Wt::WProgressBar& w) { return w.value(); },
            [](Wt::WProgressBar& w, double v) { w.setValue(v); },
            "The current fill amount. Should sit between `minimum` and\n"
            "`maximum`.")
        .def_prop_rw("minimum",
            [](const Wt::WProgressBar& w) { return w.minimum(); },
            [](Wt::WProgressBar& w, double v) { w.setMinimum(v); },
            "Value corresponding to an empty bar.")
        .def_prop_rw("maximum",
            [](const Wt::WProgressBar& w) { return w.maximum(); },
            [](Wt::WProgressBar& w, double v) { w.setMaximum(v); },
            "Value corresponding to a full bar.")
        .def("set_range", &Wt::WProgressBar::setRange,
             "minimum"_a, "maximum"_a,
             "Set `minimum` and `maximum` in a single call.")
        .def("set_format", &Wt::WProgressBar::setFormat, "format"_a,
             "Format string used to render the percentage label inside\n"
             "the bar — e.g. `'%.0f%%'`. Pass an empty WString to hide\n"
             "the label.")
        .def_prop_ro("value_changed", &Wt::WProgressBar::valueChanged,
                     nb::rv_policy::reference_internal,
                     "Fires with the new `value` whenever it changes.");
}

}  // namespace witty_for_python
