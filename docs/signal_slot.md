# Signal/slot architecture

witty_for_python connects Python callables to Wt signals via a single `connect(callable)` entrypoint per signal type. The implementation lives in `ext/signal_helpers.hpp` (`py_connect`, `python_arity`) and `ext/bind_signals.cpp` (the connection registry).

This doc explains *why* the design looks the way it does. For the rule that summarises it, see [binding_design.md](binding_design.md) §2 and §3.

## The contract

The callable's positional-arg count is inspected once at connect time, stashed in the lambda holder, and then on every fire we dispatch with no args (arity 0) or with the payload forwarded via `nb::cast(args, nb::rv_policy::copy)` (arity ≥ 1). Variadic / un-introspectable callables fall through to "pass payload".

| Callable | Arity treated as | Effect |
|---|---|---|
| `def f()` / `lambda: ...` | 0 | Payload dropped |
| `def f(x)` / `lambda x: ...` | 1 | Payload passed (copied) |
| `def f(*args)` / variadic | -1 | All args forwarded |
| `nanobind.nb_bound_method` (e.g. `dlg.show`) | **0** (special) | Payload dropped |
| Anything where `inspect.signature` raises | -1 | All args forwarded |

## Why arity introspection instead of `connect_void` / `connect_event`

The user wanted *"basically pass a signal slot C++ function consumer a python function and have it work."* That required the binding to absorb the impedance mismatch, not the user.

Always-pass-payload was rejected because `button.clicked.connect(lambda: print("clicked"))` is the common case and forcing `lambda _: print(...)` everywhere is ugly. Always-drop-payload was rejected because users *do* sometimes want the `WMouseEvent`. Introspecting once at connect time gives the right behaviour in both cases at zero per-fire cost.

## Why the `nb_bound_method` special case

nanobind exposes its bound methods as `(*args, **kwargs)` to `inspect.signature` (because they may have C++ overloads). Without the special case, `clicked.connect(dlg.show)` would be classed as variadic, the slot would try `dlg.show(WMouseEvent)`, the underlying C++ method (which takes no args) would reject, and the resulting `TypeError` would silently land in `PyErr_WriteUnraisable`. The user would just see "the button doesn't open the dialog" with no obvious cause.

So we sniff for `type(cb).__name__ == "nb_bound_method"` and force arity to 0. The Qt-style `button.clicked.connect(dialog.show)` works the way users expect.

If someone *does* want a bound method to receive payload, they wrap explicitly: `sig.connect(lambda x: obj.method(x))`. That's rare enough that the explicit form is acceptable.

(We use `type(cb).__name__` rather than `PyTypeObject::tp_name` because the stable ABI we use hides `tp_name`.)

## Payload copy semantics

Payloads are forwarded via `nb::cast(args, nb::rv_policy::copy)` — *copied*, not referenced. Wt event objects (`WMouseEvent`, `WKeyEvent`) are stack-allocated within the slot dispatch call; if we passed them by reference, Python objects holding the reference would dangle once the slot returned. Copy semantics make the Python objects independent.

This matters for `WMouseEvent` / `WKeyEvent` / `Coordinates`. For `int`, `bool`, `double`, `std::string`, `Wt::WString` it's a no-op (those casters produce fresh Python objects anyway).

When binding a new event type with `py_connect`, the type must be copyable. Wt's event types all are.

## Error surfacing

Slot exceptions are surfaced via `PyErr_WriteUnraisable` (with `e.restore()` first) rather than re-thrown. Wt's slot dispatcher *swallows* exceptions silently — if we let them escape, the user gets no signal at all that their handler raised. Routing through `WriteUnraisable` at least makes the error appear on stderr.

Preserve this when extending `py_connect`. Don't blanket-catch and discard.

## Connection holder lifetime

The Python callable is captured in a `std::shared_ptr<nb::object>` held by the connection's lambda. When the C++ signal is destroyed, the lambda is destroyed, the shared_ptr drops its ref, the `nb::object` runs its destructor, which `Py_DECREF`s the Python callable.

nanobind's leak detector reports those holders (and the Signal wrappers themselves) as "leaked" if any are still alive when the module finalizer runs at interpreter shutdown. Mitigation: a process-wide connection registry.

## The connection registry

Every `py_connect` adds its returned `Wt::Signals::connection` to a global map keyed by the signal's address:

```cpp
std::unordered_map<const void*, std::vector<Wt::Signals::connection>>
```

Protected by `std::mutex`. Two operations:

- `connection_registry_disconnect_all(&sig)` — exposed per signal type as `sig.disconnect_all_slots()`.
- `connection_registry_disconnect_all_signals()` — exposed at module scope as `_cleanup_all_connections`.

`witty_for_python/__init__.py` registers `_cleanup_all_connections` as an `atexit` handler. Under clean shutdown the registry is flushed, all `shared_ptr<nb::object>` holders drop, and nanobind's leak detector finds nothing.

**Do not** revert to enumerating signals via `gc.get_objects()` from Python — nanobind-bound instances are not GC-tracked, and they are not `weakref`-able either. The C++ side has to drive the cleanup. The registry is also useful for diagnostics: `_live_connection_count()` is exposed.

## Re-entrancy in `disconnect_all_for`

When a connection is destroyed, its `~shared_ptr<nb::object>` runs `Py_DECREF`, which can run arbitrary Python code (e.g. the callable's own destructor). If we were holding the registry mutex while that happened, and the destructor (somehow) called another binding method that touched the registry, we'd deadlock.

So `disconnect_all_for` moves the connection vector out under the lock, *releases* the lock, then disconnects. This is in `bind_signals.cpp` — preserve the pattern.

## Wt-side inheritance for signals

Wt's signals (`Wt::Signal<T>`, `Wt::EventSignal<T>`) live in `Wt::Signals` — Wt's in-house lightweight signal impl, NOT boost::signals2. Read [threading.md](threading.md) for why this matters: Wt's signal impl is **not safe under concurrent same-signal emit**. Wt's session lock serialises it; cross-thread emits go through `WServer.post()`. We don't fight that.

## Required boilerplate for adding a new `Signal<T>` type

```cpp
nb::class_<Wt::Signal<T>>(m, "TSignal")
    .def("connect", [](Wt::Signal<T>& s, nb::callable cb) {
        return py_connect<Wt::Signal<T>, T>(s, std::move(cb));
    }, nb::arg("callable"))
    .def("emit", &Wt::Signal<T>::emit)
    .def("disconnect_all_slots", [](Wt::Signal<T>& s) {
        connection_registry_disconnect_all(&s);
    });
```

Then add `TSignal` to `_SIGNAL_TYPES` in `src/witty_for_python/__init__.py` so the atexit walker covers it.
