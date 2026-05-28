#include "common.hpp"

#include <Wt/WTimer.h>

#include <chrono>

namespace witty_for_python {

void register_timer(nb::module_& m) {
    // WTimer fires its timeout signal at fixed intervals from the application's
    // worker thread (so the slot runs under the session's update lock —
    // touching widgets is safe). For one-shot use, set single_shot = True
    // before start().
    //
    // The interval property exchanges Python `datetime.timedelta` ↔ Wt's
    // `std::chrono::milliseconds` via nanobind's chrono caster — i.e.
    //
    //   timer.interval = timedelta(seconds=2)
    //   timer.start()
    //
    // The timeout signal hands a WMouseEvent payload (per the Wt API), but
    // it carries no meaningful data for timers — it's an implementation
    // detail of how EventSignal is templated. Slots can ignore the argument.

    nb::class_<Wt::WTimer, Wt::WObject>(m, "WTimer")
        .def(heap_init<Wt::WTimer>())
        .def_prop_rw("interval",
            [](const Wt::WTimer& t) { return t.interval(); },
            [](Wt::WTimer& t, std::chrono::milliseconds v) { t.setInterval(v); },
            "Time between successive timer firings, as a datetime.timedelta. "
            "Re-assigning while the timer is active reschedules it.")
        .def_prop_ro("is_active", &Wt::WTimer::isActive,
                     "True between start() and stop() (or first timeout when "
                     "single_shot is True).")
        .def_prop_rw("single_shot",
            &Wt::WTimer::isSingleShot,
            &Wt::WTimer::setSingleShot,
            "When True, the timer fires exactly once and then deactivates.")
        .def("start", &Wt::WTimer::start,
             "Begin firing the timeout signal at every interval. No-op if "
             "the timer is already active.")
        .def("stop", &Wt::WTimer::stop,
             "Stop a running timer. Safe to call from within a timeout slot.")
        .def_prop_ro("timeout", &Wt::WTimer::timeout,
                     nb::rv_policy::reference_internal,
                     "EventSignal[WMouseEvent] — fires every interval. The "
                     "event payload is an implementation artefact; slots "
                     "typically ignore it.");
}

}  // namespace witty_for_python
