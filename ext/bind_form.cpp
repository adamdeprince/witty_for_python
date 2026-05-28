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

    nb::enum_<Wt::Orientation>(m, "Orientation", nb::is_arithmetic())
        .value("Horizontal", Wt::Orientation::Horizontal)
        .value("Vertical", Wt::Orientation::Vertical);

    nb::enum_<Wt::SelectionMode>(m, "SelectionMode")
        .value("None_", Wt::SelectionMode::None)
        .value("Single", Wt::SelectionMode::Single)
        .value("Extended", Wt::SelectionMode::Extended);

    // ---- WLabel: a text or image label, optionally bound to a form widget ----

    nb::class_<Wt::WLabel, Wt::WInteractWidget>(m, "WLabel")
        .def(heap_init<Wt::WLabel>())
        .def(heap_init<Wt::WLabel, const Wt::WString&>(), "text"_a)
        .def_prop_rw("text",
            [](const Wt::WLabel& w) { return w.text(); },
            [](Wt::WLabel& w, const Wt::WString& t) { w.setText(t); })
        .def("set_buddy", &Wt::WLabel::setBuddy, "buddy"_a)
        .def_prop_rw("word_wrap",
            [](const Wt::WLabel& w) { return w.wordWrap(); },
            [](Wt::WLabel& w, bool b) { w.setWordWrap(b); })
        .def("set_image",
            [](Wt::WLabel& w, nb::object py_img) {
                auto img = nb::cast<std::unique_ptr<Wt::WImage>>(py_img);
                w.setImage(std::move(img));
                nb::inst_set_state(py_img, /*ready*/ true,
                                   /*destruct*/ false);
            },
            "image"_a);

    // ---- WBreak: a <br> element ----
    // Inherits WWebWidget in C++ but the closest type Python knows about is
    // WWidget — that is enough for parent-pointer compatibility.

    nb::class_<Wt::WBreak, Wt::WWidget>(m, "WBreak")
        .def(heap_init<Wt::WBreak>());

    // ---- WTextArea: multi-line text input ----

    nb::class_<Wt::WTextArea, Wt::WFormWidget>(m, "WTextArea")
        .def(heap_init<Wt::WTextArea>())
        .def(heap_init<Wt::WTextArea, const Wt::WString&>(), "text"_a)
        .def_prop_rw("text",
            [](const Wt::WTextArea& w) { return w.text(); },
            [](Wt::WTextArea& w, const Wt::WString& t) { w.setText(t); })
        .def_prop_rw("rows",
            [](const Wt::WTextArea& w) { return w.rows(); },
            [](Wt::WTextArea& w, int n) { w.setRows(n); })
        .def_prop_rw("columns",
            [](const Wt::WTextArea& w) { return w.columns(); },
            [](Wt::WTextArea& w, int n) { w.setColumns(n); })
        .def_prop_rw("placeholder",
            [](const Wt::WTextArea& w) { return w.placeholderText(); },
            [](Wt::WTextArea& w, const Wt::WString& t) { w.setPlaceholderText(t); })
        .def_prop_ro("selection_start", &Wt::WTextArea::selectionStart)
        .def_prop_ro("has_selected_text", &Wt::WTextArea::hasSelectedText)
        .def_prop_ro("cursor_position", &Wt::WTextArea::cursorPosition);

    // ---- Spin boxes: integer + double ----
    // Both inherit WLineEdit via WAbstractSpinBox; the intermediate is elided
    // on the Python side since we don't expose its methods.

    nb::class_<Wt::WSpinBox, Wt::WLineEdit>(m, "WSpinBox")
        .def(heap_init<Wt::WSpinBox>())
        .def_prop_rw("value",
            [](const Wt::WSpinBox& w) { return w.value(); },
            [](Wt::WSpinBox& w, int v) { w.setValue(v); })
        .def_prop_rw("minimum",
            [](const Wt::WSpinBox& w) { return w.minimum(); },
            [](Wt::WSpinBox& w, int v) { w.setMinimum(v); })
        .def_prop_rw("maximum",
            [](const Wt::WSpinBox& w) { return w.maximum(); },
            [](Wt::WSpinBox& w, int v) { w.setMaximum(v); })
        .def_prop_rw("single_step",
            [](const Wt::WSpinBox& w) { return w.singleStep(); },
            [](Wt::WSpinBox& w, int v) { w.setSingleStep(v); })
        .def("set_range", &Wt::WSpinBox::setRange, "minimum"_a, "maximum"_a)
        .def_prop_rw("wrap_around",
            [](const Wt::WSpinBox& w) { return w.wrapAroundEnabled(); },
            [](Wt::WSpinBox& w, bool b) { w.setWrapAroundEnabled(b); })
        .def_prop_ro("value_changed", &Wt::WSpinBox::valueChanged,
                     nb::rv_policy::reference_internal);

    nb::class_<Wt::WDoubleSpinBox, Wt::WLineEdit>(m, "WDoubleSpinBox")
        .def(heap_init<Wt::WDoubleSpinBox>())
        .def_prop_rw("value",
            [](const Wt::WDoubleSpinBox& w) { return w.value(); },
            [](Wt::WDoubleSpinBox& w, double v) { w.setValue(v); })
        .def_prop_rw("minimum",
            [](const Wt::WDoubleSpinBox& w) { return w.minimum(); },
            [](Wt::WDoubleSpinBox& w, double v) { w.setMinimum(v); })
        .def_prop_rw("maximum",
            [](const Wt::WDoubleSpinBox& w) { return w.maximum(); },
            [](Wt::WDoubleSpinBox& w, double v) { w.setMaximum(v); })
        .def_prop_rw("single_step",
            [](const Wt::WDoubleSpinBox& w) { return w.singleStep(); },
            [](Wt::WDoubleSpinBox& w, double v) { w.setSingleStep(v); })
        .def_prop_rw("decimals",
            [](const Wt::WDoubleSpinBox& w) { return w.decimals(); },
            [](Wt::WDoubleSpinBox& w, int n) { w.setDecimals(n); })
        .def("set_range", &Wt::WDoubleSpinBox::setRange,
             "minimum"_a, "maximum"_a)
        .def_prop_ro("value_changed", &Wt::WDoubleSpinBox::valueChanged,
                     nb::rv_policy::reference_internal);

    // ---- WSlider ----

    nb::class_<Wt::WSlider, Wt::WFormWidget>(m, "WSlider")
        .def(heap_init<Wt::WSlider>())
        .def(heap_init<Wt::WSlider, Wt::Orientation>(), "orientation"_a)
        .def_prop_rw("value",
            [](const Wt::WSlider& w) { return w.value(); },
            [](Wt::WSlider& w, int v) { w.setValue(v); })
        .def_prop_rw("minimum",
            [](const Wt::WSlider& w) { return w.minimum(); },
            [](Wt::WSlider& w, int v) { w.setMinimum(v); })
        .def_prop_rw("maximum",
            [](const Wt::WSlider& w) { return w.maximum(); },
            [](Wt::WSlider& w, int v) { w.setMaximum(v); })
        .def_prop_rw("step",
            [](const Wt::WSlider& w) { return w.step(); },
            [](Wt::WSlider& w, int v) { w.setStep(v); })
        .def_prop_rw("tick_interval",
            [](const Wt::WSlider& w) { return w.tickInterval(); },
            [](Wt::WSlider& w, int v) { w.setTickInterval(v); })
        .def("set_range", &Wt::WSlider::setRange, "minimum"_a, "maximum"_a)
        .def("set_orientation", &Wt::WSlider::setOrientation, "orientation"_a)
        .def_prop_ro("value_changed", &Wt::WSlider::valueChanged,
                     nb::rv_policy::reference_internal);

    // ---- WComboBox + WSelectionBox ----

    nb::class_<Wt::WComboBox, Wt::WFormWidget>(m, "WComboBox")
        .def(heap_init<Wt::WComboBox>())
        .def("add_item", &Wt::WComboBox::addItem, "text"_a)
        // Python-only bulk variant of add_item. Loops the single-item form;
        // additive (rule §0) — no default behavior changes. Mirrors the
        // pattern `for x in xs: combo.add_item(x)`.
        .def("add_items",
             [](Wt::WComboBox& self, const std::vector<Wt::WString>& items) {
                 for (const auto& s : items) self.addItem(s);
             },
             "items"_a)
        .def("insert_item", &Wt::WComboBox::insertItem, "index"_a, "text"_a)
        .def("remove_item", &Wt::WComboBox::removeItem, "index"_a)
        .def_prop_ro("count", &Wt::WComboBox::count)
        .def("item_text", &Wt::WComboBox::itemText, "index"_a)
        .def("set_item_text", &Wt::WComboBox::setItemText, "index"_a, "text"_a)
        .def_prop_rw("current_index",
            [](const Wt::WComboBox& w) { return w.currentIndex(); },
            [](Wt::WComboBox& w, int i) { w.setCurrentIndex(i); })
        .def("clear", &Wt::WComboBox::clear)
        .def_prop_ro("activated", &Wt::WComboBox::activated,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("string_activated", &Wt::WComboBox::sactivated,
                     nb::rv_policy::reference_internal);

    nb::class_<Wt::WSelectionBox, Wt::WComboBox>(m, "WSelectionBox")
        .def(heap_init<Wt::WSelectionBox>())
        .def_prop_rw("vertical_size",
            [](const Wt::WSelectionBox& w) { return w.verticalSize(); },
            [](Wt::WSelectionBox& w, int n) { w.setVerticalSize(n); })
        .def("set_selection_mode", &Wt::WSelectionBox::setSelectionMode,
             "mode"_a)
        .def("set_selected_indexes", &Wt::WSelectionBox::setSelectedIndexes,
             "selection"_a)
        .def("clear_selection", &Wt::WSelectionBox::clearSelection);

    // ---- WRadioButton + WButtonGroup ----
    //
    // WButtonGroup is owned by shared_ptr (Wt's API takes std::shared_ptr).
    // nanobind's shared_ptr caster keeps the Python wrapper alive while any
    // C++ buttons hold the group.

    // To put a radio button into a group, call group.add_button(button) on
    // the Python side — WRadioButton::setGroup() is private in Wt 4.13.
    nb::class_<Wt::WRadioButton, Wt::WFormWidget>(m, "WRadioButton")
        .def(heap_init<Wt::WRadioButton>())
        .def(heap_init<Wt::WRadioButton, const Wt::WString&>(), "text"_a)
        .def_prop_rw("checked",
            [](const Wt::WRadioButton& w) { return w.isChecked(); },
            [](Wt::WRadioButton& w, bool c) { w.setChecked(c); })
        .def_prop_ro("on_check",
            [](Wt::WRadioButton& w) -> Wt::EventSignal<>& {
                return w.checked();
            },
            nb::rv_policy::reference_internal)
        .def_prop_ro("on_uncheck",
            [](Wt::WRadioButton& w) -> Wt::EventSignal<>& {
                return w.unChecked();
            },
            nb::rv_policy::reference_internal);

    // WButtonGroup is special: its `addButton` calls `shared_from_this()`
    // internally, so the group MUST already live inside a std::shared_ptr
    // before any button is added. Construct via `make_shared` and return
    // it as shared_ptr — nanobind's shared_ptr from_cpp path stashes the
    // shared_ptr in keep_alive, so `weak_from_this()` resolves later.
    nb::class_<Wt::WButtonGroup, Wt::WObject>(m, "WButtonGroup")
        .def(nb::new_([]() { return std::make_shared<Wt::WButtonGroup>(); }))
        .def("add_button",
             nb::overload_cast<Wt::WRadioButton*, int>(&Wt::WButtonGroup::addButton),
             "button"_a, "id"_a = -1)
        .def("remove_button", &Wt::WButtonGroup::removeButton, "button"_a)
        .def_prop_ro("count", &Wt::WButtonGroup::count)
        .def_prop_ro("checked_id", &Wt::WButtonGroup::checkedId)
        .def_prop_rw("selected_button_index",
            [](const Wt::WButtonGroup& g) { return g.selectedButtonIndex(); },
            [](Wt::WButtonGroup& g, int i) { g.setSelectedButtonIndex(i); });

    // ---- WProgressBar ----

    nb::class_<Wt::WProgressBar, Wt::WInteractWidget>(m, "WProgressBar")
        .def(heap_init<Wt::WProgressBar>())
        .def_prop_rw("value",
            [](const Wt::WProgressBar& w) { return w.value(); },
            [](Wt::WProgressBar& w, double v) { w.setValue(v); })
        .def_prop_rw("minimum",
            [](const Wt::WProgressBar& w) { return w.minimum(); },
            [](Wt::WProgressBar& w, double v) { w.setMinimum(v); })
        .def_prop_rw("maximum",
            [](const Wt::WProgressBar& w) { return w.maximum(); },
            [](Wt::WProgressBar& w, double v) { w.setMaximum(v); })
        .def("set_range", &Wt::WProgressBar::setRange,
             "minimum"_a, "maximum"_a)
        .def("set_format", &Wt::WProgressBar::setFormat, "format"_a)
        .def_prop_ro("value_changed", &Wt::WProgressBar::valueChanged,
                     nb::rv_policy::reference_internal);
}

}  // namespace witty_for_python
