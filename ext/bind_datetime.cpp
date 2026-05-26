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
    // ---- Signal<WDate> for WCalendar::activated / clicked ----
    //
    // Wt::WDate flows through the datetime_caster as Python datetime.date,
    // so a slot connected here receives a `datetime.date` (or `None` for
    // an invalid/empty Wt::WDate).
    nb::class_<Wt::Signal<Wt::WDate>>(m, "DateSignal")
        .def(nb::init<>())
        .def("connect",
            [](Wt::Signal<Wt::WDate>& s, nb::callable cb) {
                return py_connect<Wt::Signal<Wt::WDate>,
                                  Wt::WDate>(s, std::move(cb));
            }, "callable"_a)
        .def("emit", &Wt::Signal<Wt::WDate>::emit)
        .def("disconnect_all_slots",
            [](Wt::Signal<Wt::WDate>& s) {
                connection_registry_disconnect_all(&s);
            });

    // ---- WDateEdit (inherits WLineEdit) ----

    nb::class_<Wt::WDateEdit, Wt::WLineEdit>(m, "WDateEdit")
        .def(nb::init<>())
        .def_prop_rw("date",
            [](const Wt::WDateEdit& w) { return w.date(); },
            [](Wt::WDateEdit& w, const Wt::WDate& d) { w.setDate(d); })
        .def_prop_rw("bottom",
            [](const Wt::WDateEdit& w) { return w.bottom(); },
            [](Wt::WDateEdit& w, const Wt::WDate& d) { w.setBottom(d); })
        .def_prop_rw("top",
            [](const Wt::WDateEdit& w) { return w.top(); },
            [](Wt::WDateEdit& w, const Wt::WDate& d) { w.setTop(d); })
        .def("set_format", &Wt::WDateEdit::setFormat, "format"_a)
        .def("format", &Wt::WDateEdit::format);

    // ---- WTimeEdit (inherits WLineEdit) ----

    nb::class_<Wt::WTimeEdit, Wt::WLineEdit>(m, "WTimeEdit")
        .def(nb::init<>())
        .def_prop_rw("time",
            [](const Wt::WTimeEdit& w) { return w.time(); },
            [](Wt::WTimeEdit& w, const Wt::WTime& t) { w.setTime(t); })
        .def_prop_rw("bottom",
            [](const Wt::WTimeEdit& w) { return w.bottom(); },
            [](Wt::WTimeEdit& w, const Wt::WTime& t) { w.setBottom(t); })
        .def_prop_rw("top",
            [](const Wt::WTimeEdit& w) { return w.top(); },
            [](Wt::WTimeEdit& w, const Wt::WTime& t) { w.setTop(t); })
        .def("set_format", &Wt::WTimeEdit::setFormat, "format"_a);

    // ---- WCalendar (inherits WCompositeWidget → WWidget) ----

    nb::class_<Wt::WCalendar, Wt::WWidget>(m, "WCalendar")
        .def(nb::init<>())
        // select() is overloaded — we expose only the single-date form;
        // multi-select use cases are rare and the std::set<WDate> form
        // can come back later if needed.
        .def("select",
             nb::overload_cast<const Wt::WDate&>(&Wt::WCalendar::select),
             "date"_a)
        .def("set_selection_mode", &Wt::WCalendar::setSelectionMode,
             "mode"_a)
        .def("browse_to_previous_month", &Wt::WCalendar::browseToPreviousMonth)
        .def("browse_to_next_month",     &Wt::WCalendar::browseToNextMonth)
        .def("browse_to_previous_year",  &Wt::WCalendar::browseToPreviousYear)
        .def("browse_to_next_year",      &Wt::WCalendar::browseToNextYear)
        .def_prop_ro("current_month", &Wt::WCalendar::currentMonth)
        .def_prop_ro("current_year",  &Wt::WCalendar::currentYear)
        .def_prop_rw("bottom",
            [](const Wt::WCalendar& w) { return w.bottom(); },
            [](Wt::WCalendar& w, const Wt::WDate& d) { w.setBottom(d); })
        .def_prop_rw("top",
            [](const Wt::WCalendar& w) { return w.top(); },
            [](Wt::WCalendar& w, const Wt::WDate& d) { w.setTop(d); })
        .def_prop_ro("selection_changed", &Wt::WCalendar::selectionChanged,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("activated", &Wt::WCalendar::activated,
                     nb::rv_policy::reference_internal)
        .def_prop_ro("clicked", &Wt::WCalendar::clicked,
                     nb::rv_policy::reference_internal);

    // ---- WDateValidator (inherits WValidator) ----

    nb::class_<Wt::WDateValidator, Wt::WValidator>(m, "WDateValidator")
        .def(nb::init<>())
        .def(nb::init<const Wt::WDate&, const Wt::WDate&>(),
             "bottom"_a, "top"_a)
        .def(nb::init<const Wt::WString&>(), "format"_a)
        .def_prop_rw("bottom",
            [](const Wt::WDateValidator& v) { return v.bottom(); },
            [](Wt::WDateValidator& v, const Wt::WDate& d) { v.setBottom(d); })
        .def_prop_rw("top",
            [](const Wt::WDateValidator& v) { return v.top(); },
            [](Wt::WDateValidator& v, const Wt::WDate& d) { v.setTop(d); })
        .def("set_format", &Wt::WDateValidator::setFormat, "format"_a)
        .def("format", &Wt::WDateValidator::format);

    // ---- WTimeValidator (inherits WRegExpValidator, not WValidator directly) ----

    nb::class_<Wt::WTimeValidator, Wt::WRegExpValidator>(m, "WTimeValidator")
        .def(nb::init<>())
        .def(nb::init<const Wt::WString&>(), "format"_a)
        .def(nb::init<const Wt::WString&, const Wt::WTime&, const Wt::WTime&>(),
             "format"_a, "bottom"_a, "top"_a)
        .def_prop_rw("bottom",
            [](const Wt::WTimeValidator& v) { return v.bottom(); },
            [](Wt::WTimeValidator& v, const Wt::WTime& t) { v.setBottom(t); })
        .def_prop_rw("top",
            [](const Wt::WTimeValidator& v) { return v.top(); },
            [](Wt::WTimeValidator& v, const Wt::WTime& t) { v.setTop(t); })
        .def("set_format", &Wt::WTimeValidator::setFormat, "format"_a)
        .def("format", &Wt::WTimeValidator::format);
}

}  // namespace witty_for_python
