# witty_for_python — overview

A nanobind-based Python binding for [Wt](https://www.webtoolkit.eu/wt) — Emweb's C++ widget-tree web framework. You write a Python factory that returns a `WApplication`; Wt's session manager owns the widget tree from that point on.

## Why this project exists

The user wanted to write Wt apps in Python without giving up Wt's session-per-thread server model. Alternatives considered and rejected:

- **Qt-for-Python (PySide6)**: desktop, not web.
- **Streamlit / Dash**: not stateful widget-tree per session; very different model.
- **Wt's own Java bindings**: not Python.

The choice of Wt was deliberate: it gives us per-session state, a real widget tree, server-side rendering with progressive JS enhancement, and a thread-pool model that maps well onto free-threaded Python.

## Build stack

| Component | Version |
|---|---|
| nanobind | ≥ 2.4 (2.12 in use) |
| scikit-build-core | ≥ 0.10 |
| CMake | ≥ 3.26 |
| C++ standard | C++23 |
| Python | ≥ 3.10 (free-threaded 3.13t / 3.14t supported, see [threading.md](threading.md)) |
| Wt | 4.13.x, built from source — see [building_wt.md](building_wt.md) |

## Initial binding scope

The user picked "broader widget set up-front" over a minimal hello-world, so the initial surface covers:

- **Lifecycle**: `WServer`, `WApplication`, `WEnvironment`, `EntryPointType`
- **Containers + layouts**: `WContainerWidget`, `WBoxLayout` (`WHBoxLayout`, `WVBoxLayout`), `WGridLayout`
- **Widgets**: `WText`, `WPushButton`, `WLineEdit`, `WCheckBox`, `WAnchor`, `WImage`, `WLink`, `WTextArea`, `WSpinBox`, `WDoubleSpinBox`, `WSlider`, `WComboBox`, `WSelectionBox`, `WRadioButton`, `WButtonGroup`, `WProgressBar`, `WLabel`, `WBreak`, `WTable` (and cells/rows/columns)
- **Navigation**: `WTabWidget`, `WMenu`, `WMenuItem`, `WStackedWidget`, `WPanel`, `WGroupBox`
- **Dialogs**: `WDialog`, `WMessageBox`
- **Signals**: `Signal`, `IntSignal`, `BoolSignal`, `DoubleSignal`, `StringSignal`, `EventSignal`, `MouseEventSignal`, `KeyEventSignal`, plus payload variants for `DialogCode`, `StandardButton`, `WMenuItem*`
- **Threading**: `WServer.post`/`post_all`, `WApplication.trigger_update`, `UpdateLock`, `update_lock(app)` context manager, `widget.bind_safe(fn)` — see [threading.md](threading.md)

## Architectural conventions

- **Wt acquisition** — `find_package(Wt REQUIRED COMPONENTS Wt HTTP)` against a system install at `~/.local`. **Do not switch to FetchContent**: Wt is large; a vendored build is too slow. Both-with-fallback was offered and rejected.
- **Ownership** — Wt 4 is `std::unique_ptr`-based. `add_widget` / `set_layout` take `std::unique_ptr<T>` and *invalidate the Python wrapper on the caller side*; callers must rebind to the returned non-owning handle. Factory callbacks for `add_entry_point` use `std::function<unique_ptr<WApplication>(const WEnvironment&)>` so the returned Python `WApplication` ownership transfers cleanly to Wt.
- **Strings** — `Wt::WString` is bound transparently to Python `str` via a custom `nb::type_caster` in `ext/common.hpp`. Do not bind `WString` as a distinct Python type; just use it in C++ signatures and the caster handles the conversion.
- **Signals** — Python callables are wrapped in `std::shared_ptr<nb::object>` held by the connection. Slot fires acquire the GIL (or no-op under free-threading). See [signal_slot.md](signal_slot.md).
- **Source layout**: C++ lives in `ext/` (one `bind_<topic>.cpp` per concern, with `common.hpp` shared); the Python package is in `src/witty_for_python/`. scikit-build-core installs the compiled `_witty_for_python` extension into `witty_for_python/`.

## What else lives in `docs/`

- [binding_design.md](binding_design.md) — the rules for adding to or changing the bindings. Read before touching `ext/`.
- [signal_slot.md](signal_slot.md) — signal/slot architecture, arity introspection, connection registry, bound-method detection.
- [threading.md](threading.md) — threading model, cross-thread APIs, free-threaded Python 3.14t status, Wt's per-signal serialisation constraint.
- [building_wt.md](building_wt.md) — apt deps and CMake flags to build Wt 4.13.x from source into `~/.local`.

## Build command (TL;DR)

```bash
CMAKE_PREFIX_PATH="$HOME/.local" \
  /path/to/python -m pip install --no-build-isolation -e .
```

Run from the repo root — scikit-build-core's discovery breaks if you run from `ext/`.

The compiled `.so` has an RPATH baked in pointing at `~/.local/lib`, so `import witty_for_python` works without `LD_LIBRARY_PATH`.
