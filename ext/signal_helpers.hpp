#pragma once

#include "common.hpp"

#include <Wt/WSignal.h>

#include <memory>

namespace witty_for_python {

// Inspect a Python callable to find out how many positional args it accepts.
// Returns 0 (no args), N (exact positional count), or -1 (variadic or
// introspection failed — e.g. C built-in callable). Callers pass payloads
// when arity != 0.
int python_arity(nb::handle callable) noexcept;

// Per-signal registry of `boost::signals2::connection`s. The python-callable
// holders captured inside each slot lambda keep Python objects alive. If the
// owning C++ signal outlives the call to nanobind's leak detector, those
// holders show up as "leaked" at interpreter shutdown.
//
// To break the chain, every signal we bind exposes a `disconnect_all_slots()`
// method that calls `connection_registry_disconnect_all(&sig)`; the Python
// __init__.py registers an atexit handler that walks gc.get_objects() and
// calls it on every live Signal/EventSignal instance before the finalizer
// runs.
void connection_registry_add(const void* signal_ptr,
                             Wt::Signals::connection conn);
void connection_registry_disconnect_all(const void* signal_ptr) noexcept;

// Disconnect *every* connection opened through py_connect. Invoked by the
// Python atexit handler. nanobind-bound instances are not GC-trackable, so
// the Python side cannot enumerate live signals on its own — we walk the
// registry from C++ instead.
void connection_registry_disconnect_all_signals() noexcept;
std::size_t connection_registry_size() noexcept;

// Connect a Python callable to a Wt signal whose slot takes `Args...`.
// Forwards every signal argument through nb::cast (rv_policy::copy for
// class types) only if the callable wanted them. See python_arity().
template <typename SigT, typename... Args>
Wt::Signals::connection py_connect(SigT& sig, nb::callable cb) {
    int arity = python_arity(cb);
    auto holder = std::make_shared<nb::object>(std::move(cb));
    Wt::Signals::connection conn = sig.connect([holder, arity](Args... args) {
        nb::gil_scoped_acquire gil;
        try {
            if (arity == 0) {
                (*holder)();
            } else {
                (*holder)(nb::cast(args, nb::rv_policy::copy)...);
            }
        } catch (nb::python_error& e) {
            e.restore();
            PyErr_WriteUnraisable(holder->ptr());
        }
    });
    connection_registry_add(static_cast<const void*>(&sig), conn);
    return conn;
}

}  // namespace witty_for_python
