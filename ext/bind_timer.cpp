#include "common.hpp"

#include <Wt/WTimer.h>

#include <chrono>

namespace witty_for_python {

void register_timer(nb::module_& m) {
    // The interval property exchanges Python `datetime.timedelta` ↔ Wt's
    // `std::chrono::milliseconds` via nanobind's chrono caster. The timeout
    // signal hands a WMouseEvent payload (per the Wt API), but it carries
    // no meaningful data for timers — it's an implementation detail of how
    // EventSignal is templated. Slots can ignore the argument.

    nb::class_<Wt::WTimer, Wt::WObject>(m, "WTimer",
        "Session-bound timer that fires its `timeout` signal at a fixed\n"
        "interval. The signal is delivered on the Wt session thread under\n"
        "the application's update lock, so slots can touch widgets directly\n"
        "without going through `WServer.post` or an `UpdateLock`.\n"
        "\n"
        "    from datetime import timedelta\n"
        "    clock = wt.WTimer()\n"
        "    clock.interval = timedelta(seconds=1)\n"
        "    def tick():\n"
        "        label.text = time.strftime('%H:%M:%S')\n"
        "    clock.timeout.connect(tick)\n"
        "    clock.start()\n"
        "\n"
        "Set `single_shot = True` before `start()` to fire once and stop;\n"
        "otherwise the timer repeats until `stop()` is called. Reads of\n"
        "`interval` come back as a `datetime.timedelta`.")
        .def(heap_init<Wt::WTimer>(),
             "Construct an inactive timer with a zero interval. Set\n"
             "`interval` (and optionally `single_shot`), connect `timeout`,\n"
             "then call `start()`.")
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
