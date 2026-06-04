#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WCalendar.h>
#include <Wt/WDate.h>
#include <Wt/WDateEdit.h>
#include <Wt/WDateTime.h>
#include <Wt/WDateValidator.h>
#include <Wt/WLineEdit.h>
#include <Wt/WRegExpValidator.h>
#include <Wt/WTime.h>
#include <Wt/WTimeEdit.h>
#include <Wt/WTimeValidator.h>

namespace witty_for_python {

void register_datetime(nb::module_& m) {
    // Wt::WDate flows through the datetime_caster as Python datetime.date,
    // so a slot connected here receives a `datetime.date` (or `None` for
    // an invalid/empty Wt::WDate).
    nb::class_<Wt::Signal<Wt::WDate>>(m, "DateSignal",
        "Signal that emits a date payload. Wt::WDate is bridged through\n"
        "the datetime caster, so slots receive a Python `datetime.date`\n"
        "(or `None` for an invalid date). Same connect/emit shape as the\n"
        "other Signal subclasses.")
        .def(nb::init<>(),
             "Construct a free-standing date signal. Useful for tests or\n"
             "ad-hoc signal/slot wiring outside the Wt widget tree.")
        .def("connect",
            [](Wt::Signal<Wt::WDate>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::WDate>,
                                  Wt::WDate>(s, std::move(cb));
            }, "callable"_a,
            "Subscribe `callable(date)` to this signal. Returns a\n"
            "Connection — call `.disconnect()` on it to unsubscribe.")
        .def("emit", &Wt::Signal<Wt::WDate>::emit,
             "Fire the signal with the given date. Each connected slot\n"
             "runs synchronously in turn.")
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WDate>& s) {
                connection_registry_disconnect_all(&s);
            },
            "Disconnect every slot connected through this binding.\n"
            "Releases the Python callable references the connections hold.");

    // ---- WDateEdit (inherits WLineEdit) ----

    nb::class_<Wt::WDateEdit, Wt::WLineEdit>(m, "WDateEdit",
        "Line-edit specialised for picking a date. Reads/writes its value\n"
        "as a Python `datetime.date` via the `date` property, and shows a\n"
        "calendar popup for date selection. Inherits all of WLineEdit's\n"
        "text-field plumbing (validators, `changed` signal, etc.).\n"
        "\n"
        "    picker = container.add_widget(wt.WDateEdit())\n"
        "    picker.date = date.today()\n"
        "    picker.bottom = date(2020, 1, 1)\n"
        "    picker.changed.connect(lambda: log(picker.date))")
        .def(heap_init<Wt::WDateEdit>(),
             "Construct an empty date edit with no selected date.")
        .def_prop_rw("date",
            [](const Wt::WDateEdit& w) { return w.date(); },
            [](Wt::WDateEdit& w, const Wt::WDate& d) { w.setDate(d); },
            "The selected date as a `datetime.date`, or `None` if the\n"
            "field is empty / unparseable.")
        .def_prop_rw("bottom",
            [](const Wt::WDateEdit& w) { return w.bottom(); },
            [](Wt::WDateEdit& w, const Wt::WDate& d) { w.setBottom(d); },
            "Earliest accepted date. Dates before this are rejected by\n"
            "the built-in validator and the popup grays them out.")
        .def_prop_rw("top",
            [](const Wt::WDateEdit& w) { return w.top(); },
            [](Wt::WDateEdit& w, const Wt::WDate& d) { w.setTop(d); },
            "Latest accepted date. Companion to `bottom`.")
        .def("set_format", &Wt::WDateEdit::setFormat, "format"_a,
             "Set the display / parse format string for the date\n"
             "(Wt-style format letters, e.g. 'yyyy-MM-dd').")
        .def("format", &Wt::WDateEdit::format,
             "The current display / parse format string.");

    // ---- WTimeEdit (inherits WLineEdit) ----

    nb::class_<Wt::WTimeEdit, Wt::WLineEdit>(m, "WTimeEdit",
        "Line-edit specialised for picking a time of day. Mirror of\n"
        "WDateEdit on the time side — reads/writes a Python `datetime.time`\n"
        "via the `time` property and inherits the WLineEdit surface.\n"
        "\n"
        "    picker = container.add_widget(wt.WTimeEdit())\n"
        "    picker.time = time(9, 30)\n"
        "    picker.changed.connect(lambda: log(picker.time))")
        .def(heap_init<Wt::WTimeEdit>(),
             "Construct an empty time edit with no selected time.")
        .def_prop_rw("time",
            [](const Wt::WTimeEdit& w) { return w.time(); },
            [](Wt::WTimeEdit& w, const Wt::WTime& t) { w.setTime(t); },
            "The selected time as a `datetime.time`, or `None` if the\n"
            "field is empty / unparseable.")
        .def_prop_rw("bottom",
            [](const Wt::WTimeEdit& w) { return w.bottom(); },
            [](Wt::WTimeEdit& w, const Wt::WTime& t) { w.setBottom(t); },
            "Earliest accepted time. Values before this fail validation.")
        .def_prop_rw("top",
            [](const Wt::WTimeEdit& w) { return w.top(); },
            [](Wt::WTimeEdit& w, const Wt::WTime& t) { w.setTop(t); },
            "Latest accepted time. Companion to `bottom`.")
        .def("set_format", &Wt::WTimeEdit::setFormat, "format"_a,
             "Set the display / parse format string for the time\n"
             "(e.g. 'HH:mm:ss').");

    // ---- WCalendar (inherits WCompositeWidget → WWidget) ----

    nb::class_<Wt::WCalendar, Wt::WWidget>(m, "WCalendar",
        "Standalone month calendar — a navigable grid that lets the user\n"
        "select dates and walk through months/years. Use as a top-level\n"
        "calendar widget; for date-picker behaviour embedded in a text\n"
        "field, prefer WDateEdit.\n"
        "\n"
        "    cal = container.add_widget(wt.WCalendar())\n"
        "    cal.bottom = date(2020, 1, 1)\n"
        "    cal.activated.connect(lambda d: log('picked', d))\n"
        "\n"
        "`selection_changed` fires on any change to the selection set;\n"
        "`activated` fires when the user double-clicks (or otherwise\n"
        "commits) a single day; `clicked` fires on every single-day click.")
        .def(heap_init<Wt::WCalendar>(),
             "Construct an empty calendar showing the current month.")
        // select() is overloaded — we expose only the single-date form;
        // multi-select use cases are rare and the std::set<WDate> form
        // can come back later if needed.
        .def("select",
             nb::overload_cast<const Wt::WDate&>(&Wt::WCalendar::select),
             "date"_a,
             "Add `date` to the selection. In Single selection mode this\n"
             "replaces the previous selection; in Extended mode it adds\n"
             "to the set.")
        .def("set_selection_mode", &Wt::WCalendar::setSelectionMode,
             "mode"_a,
             "Set the selection model (SelectionMode.Single, .Extended,\n"
             "or .None_).")
        .def("browse_to_previous_month", &Wt::WCalendar::browseToPreviousMonth,
             "Scroll the visible month back by one.")
        .def("browse_to_next_month",     &Wt::WCalendar::browseToNextMonth,
             "Scroll the visible month forward by one.")
        .def("browse_to_previous_year",  &Wt::WCalendar::browseToPreviousYear,
             "Scroll the visible year back by one.")
        .def("browse_to_next_year",      &Wt::WCalendar::browseToNextYear,
             "Scroll the visible year forward by one.")
        .def_prop_ro("current_month", &Wt::WCalendar::currentMonth,
             "The month (1–12) currently displayed.")
        .def_prop_ro("current_year",  &Wt::WCalendar::currentYear,
             "The year currently displayed.")
        .def_prop_rw("bottom",
            [](const Wt::WCalendar& w) { return w.bottom(); },
            [](Wt::WCalendar& w, const Wt::WDate& d) { w.setBottom(d); },
            "Earliest selectable date. Dates before this are rendered\n"
            "as un-pickable.")
        .def_prop_rw("top",
            [](const Wt::WCalendar& w) { return w.top(); },
            [](Wt::WCalendar& w, const Wt::WDate& d) { w.setTop(d); },
            "Latest selectable date. Companion to `bottom`.")
        .def_prop_ro("selection_changed", &Wt::WCalendar::selectionChanged,
                     nb::rv_policy::reference_internal,
                     "Fires whenever the set of selected dates changes\n"
                     "(no-arg signal). Read `selection()` for the new state.")
        .def_prop_ro("activated", &Wt::WCalendar::activated,
                     nb::rv_policy::reference_internal,
                     "DateSignal — fires when the user commits a date\n"
                     "(typically a double-click). Payload is the activated\n"
                     "`datetime.date`.")
        .def_prop_ro("clicked", &Wt::WCalendar::clicked,
                     nb::rv_policy::reference_internal,
                     "DateSignal — fires on each single-day click,\n"
                     "regardless of whether the selection changed.");

    // ---- WDateValidator (inherits WValidator) ----

    nb::class_<Wt::WDateValidator, Wt::WValidator>(m, "WDateValidator",
        "WValidator that accepts dates within an optional [bottom, top]\n"
        "range, parsed against a configurable format string. Attach to a\n"
        "WLineEdit (or any WFormWidget) when you want server-side date\n"
        "validation independent of WDateEdit.\n"
        "\n"
        "    v = wt.WDateValidator(date(2020, 1, 1), date(2030, 12, 31))\n"
        "    edit.set_validator(v)\n"
        "    edit.validated.connect(lambda r: log(r.state))")
        .def(heap_init<Wt::WDateValidator>(),
             "Construct a validator with no range constraints and the\n"
             "default date format.")
        .def(heap_init<Wt::WDateValidator, const Wt::WDate&, const Wt::WDate&>(),
             "bottom"_a, "top"_a,
             "Construct a validator that requires the parsed date to lie\n"
             "between `bottom` and `top` (inclusive).")
        .def(heap_init<Wt::WDateValidator, const Wt::WString&>(), "format"_a,
             "Construct a validator using `format` as the parse format\n"
             "(Wt-style letters, e.g. 'yyyy-MM-dd').")
        .def_prop_rw("bottom",
            [](const Wt::WDateValidator& v) { return v.bottom(); },
            [](Wt::WDateValidator& v, const Wt::WDate& d) { v.setBottom(d); },
            "Earliest accepted date (inclusive).")
        .def_prop_rw("top",
            [](const Wt::WDateValidator& v) { return v.top(); },
            [](Wt::WDateValidator& v, const Wt::WDate& d) { v.setTop(d); },
            "Latest accepted date (inclusive).")
        .def("set_format", &Wt::WDateValidator::setFormat, "format"_a,
             "Set the format string used to parse / display dates.")
        .def("format", &Wt::WDateValidator::format,
             "The current parse format string.");

    // ---- WTimeValidator (inherits WRegExpValidator, not WValidator directly) ----

    nb::class_<Wt::WTimeValidator, Wt::WRegExpValidator>(m, "WTimeValidator",
        "WValidator that accepts time-of-day values within an optional\n"
        "[bottom, top] range, parsed against a configurable format string.\n"
        "Inherits the regex-validator surface internally but the public\n"
        "knobs you usually care about are `format`, `bottom`, and `top`.\n"
        "\n"
        "    v = wt.WTimeValidator('HH:mm', time(9, 0), time(17, 0))\n"
        "    edit.set_validator(v)")
        .def(heap_init<Wt::WTimeValidator>(),
             "Construct a validator with no range constraints and the\n"
             "default time format.")
        .def(heap_init<Wt::WTimeValidator, const Wt::WString&>(), "format"_a,
             "Construct a validator using `format` as the parse format\n"
             "(e.g. 'HH:mm:ss').")
        .def(heap_init<Wt::WTimeValidator, const Wt::WString&,
                       const Wt::WTime&, const Wt::WTime&>(),
             "format"_a, "bottom"_a, "top"_a,
             "Construct a validator using `format` and a [bottom, top]\n"
             "time range (both inclusive).")
        .def_prop_rw("bottom",
            [](const Wt::WTimeValidator& v) { return v.bottom(); },
            [](Wt::WTimeValidator& v, const Wt::WTime& t) { v.setBottom(t); },
            "Earliest accepted time (inclusive).")
        .def_prop_rw("top",
            [](const Wt::WTimeValidator& v) { return v.top(); },
            [](Wt::WTimeValidator& v, const Wt::WTime& t) { v.setTop(t); },
            "Latest accepted time (inclusive).")
        .def("set_format", &Wt::WTimeValidator::setFormat, "format"_a,
             "Set the format string used to parse / display times.")
        .def("format", &Wt::WTimeValidator::format,
             "The current parse format string.");
}

}  // namespace witty_for_python
