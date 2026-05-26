#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WLink.h>

NB_MODULE(_witty_for_python, m) {
    m.doc() = "Python bindings for the Wt (Web Toolkit) C++ library.";

    // Order matters: base classes (WObject -> WWidget -> WInteractWidget ->
    // WFormWidget / WContainerWidget) must be registered before their
    // derived classes are referenced.
    witty_for_python::register_signals(m);
    // register_application invokes register_validators internally between
    // WInteractWidget and WFormWidget (which needs the validator types).
    witty_for_python::register_application(m);
    witty_for_python::register_container(m);
    witty_for_python::register_widgets(m);
    witty_for_python::register_form(m);
    // Date/time widgets (WDateEdit, WTimeEdit) extend WLineEdit, so they
    // need bind_widgets registered first.
    witty_for_python::register_datetime(m);
    witty_for_python::register_template(m);
    witty_for_python::register_navigation(m);
    witty_for_python::register_table(m);
    witty_for_python::register_layout(m);
    witty_for_python::register_server(m);

    // Module-level helpers used by the Python atexit handler in
    // witty_for_python/__init__.py to drop every Python-callable connection before
    // nanobind's shutdown-time leak detector runs.
    m.def("_cleanup_all_connections",
          &witty_for_python::connection_registry_disconnect_all_signals,
          "Disconnect every Python-callable slot opened through witty_for_python. "
          "Idempotent. Called automatically at interpreter exit.");
    m.def("_live_connection_count",
          &witty_for_python::connection_registry_size,
          "Count of Python-callable connections currently held by witty_for_python.");

    // Round-trip helper for tests. Takes anything that converts to WLink and
    // returns the URL string. Used to verify str→WLink implicit conversion
    // without needing a WApplication context.
    m.def("_link_url",
          [](const Wt::WLink& l) { return l.url(); },
          nb::arg("link"),
          "Return the URL of a WLink (str auto-converts via nb::init_implicit).");

    // datetime caster round-trip helpers — also used by tests to verify the
    // WDate / WTime / WDateTime casters without setting up a WApplication.
    m.def("_round_trip_date",
          [](const Wt::WDate& d) { return d; }, nb::arg("date"));
    m.def("_round_trip_time",
          [](const Wt::WTime& t) { return t; }, nb::arg("time"));
    m.def("_round_trip_datetime",
          [](const Wt::WDateTime& dt) { return dt; }, nb::arg("dt"));
}
