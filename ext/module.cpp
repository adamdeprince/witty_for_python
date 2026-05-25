#include "common.hpp"
#include "signal_helpers.hpp"

#include <Wt/WLink.h>

NB_MODULE(_witty_for_python, m) {
    m.doc() = "Python bindings for the Wt (Web Toolkit) C++ library.";

    // Order matters: base classes (WObject -> WWidget -> WInteractWidget ->
    // WFormWidget / WContainerWidget) must be registered before their
    // derived classes are referenced.
    pywitty::register_signals(m);
    pywitty::register_application(m);
    pywitty::register_container(m);
    pywitty::register_widgets(m);
    pywitty::register_form(m);
    pywitty::register_navigation(m);
    pywitty::register_table(m);
    pywitty::register_layout(m);
    pywitty::register_server(m);

    // Module-level helpers used by the Python atexit handler in
    // pywitty/__init__.py to drop every Python-callable connection before
    // nanobind's shutdown-time leak detector runs.
    m.def("_cleanup_all_connections",
          &pywitty::connection_registry_disconnect_all_signals,
          "Disconnect every Python-callable slot opened through pywitty. "
          "Idempotent. Called automatically at interpreter exit.");
    m.def("_live_connection_count",
          &pywitty::connection_registry_size,
          "Count of Python-callable connections currently held by pywitty.");

    // Round-trip helper for tests. Takes anything that converts to WLink and
    // returns the URL string. Used to verify str→WLink implicit conversion
    // without needing a WApplication context.
    m.def("_link_url",
          [](const Wt::WLink& l) { return l.url(); },
          nb::arg("link"),
          "Return the URL of a WLink (str auto-converts via nb::init_implicit).");
}
