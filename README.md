# witty_for_python

Python bindings for [Wt (Web Toolkit)](https://www.webtoolkit.eu/wt) — a C++ widget-tree web framework — generated with [nanobind](https://github.com/wjakob/nanobind) and built against C++23.

> **Independent, unofficial wrapper.** witty_for_python is a personal project by [Adam DePrince](https://adamdeprince.com). It is **not** produced by, endorsed by, sponsored by, or otherwise affiliated with Emweb bv, the authors and copyright holders of Wt. "Wt" is referenced here only in its descriptive sense — to identify the library this software wraps — and remains the property of Emweb. For Wt itself (source, official binaries, support, commercial licensing), go directly to [www.webtoolkit.eu/wt](https://www.webtoolkit.eu/wt).

## Status

Pre-alpha scaffold. Initial bindings cover:

- **Lifecycle**: `WServer`, `WApplication`, `WEnvironment`, `EntryPointType`
- **Containers**: `WContainerWidget`, plus layouts `WBoxLayout` (`WHBoxLayout` / `WVBoxLayout`), `WGridLayout`
- **Widgets**: `WText`, `WPushButton`, `WLineEdit`, `WCheckBox`, `WAnchor`, `WImage`, `WTable` (`WTableCell`, `WTableRow`, `WTableColumn`)
- **Signals**: `Signal`, `EventSignal`, `MouseEventSignal`, `KeyEventSignal` — Python callables, GIL-aware

## Requirements

- C++23 toolchain (gcc ≥ 13, clang ≥ 17, MSVC ≥ 19.36)
- CMake ≥ 3.26
- Python ≥ 3.10
- Wt ≥ 4.10 (system install)
  - Debian / Ubuntu: `sudo apt install libwt-dev libwthttp-dev`
  - macOS (Homebrew): `brew install wt`
  - From source: <https://github.com/emweb/wt>

## Build & install

```bash
pip install .
```

scikit-build-core drives CMake under the hood. For an editable install:

```bash
pip install --no-build-isolation -ve . \
    --config-settings=build-dir=build/{wheel_tag}
```

## Run the example

```bash
python examples/hello.py --docroot . --http-address 0.0.0.0 --http-port 8080
```

Then open <http://localhost:8080>.

## Project layout

```
CMakeLists.txt
pyproject.toml
ext/                    # C++ source — one bind_*.cpp per topic
  common.hpp            # nanobind includes + WString <-> str caster
  module.cpp            # NB_MODULE entrypoint
  bind_signals.cpp      # Signal, EventSignal, MouseEventSignal, KeyEventSignal
  bind_application.cpp  # WObject, WWidget, WInteractWidget, WFormWidget, WApplication, WEnvironment
  bind_container.cpp    # WContainerWidget
  bind_widgets.cpp      # WText, WPushButton, WLineEdit, WCheckBox, WAnchor, WImage, WLink
  bind_table.cpp        # WTable, WTableCell, WTableRow, WTableColumn
  bind_layout.cpp       # WLayout, WBoxLayout, WHBoxLayout, WVBoxLayout, WGridLayout
  bind_server.cpp       # WServer, EntryPointType
src/witty_for_python/            # Python package (compiled extension installed here)
examples/               # Sample Wt apps written in Python
```

## Ownership model

Wt 4 uses `std::unique_ptr` for widget ownership; the bindings mirror this:

- A widget you construct in Python is owned by Python.
- `container.add_widget(widget)` **transfers ownership** to the container. The original Python reference is invalidated — rebind to the returned non-owning handle (`widget = container.add_widget(widget)`), whose lifetime is tied to the parent.
- Returning a `WApplication` from an entry-point factory hands ownership to the Wt session manager.

## Signal binding

Signals expose a single `connect(callable)` method. The callable's positional-arg count is inspected once at connect time:

- **0 args** → the slot is invoked with no arguments and any payload is dropped.
- **1+ args** → the payload is forwarded through `nb::cast` with `rv_policy::copy`, so the Python object survives outside the synchronous slot call.

```python
# Both forms work — witty_for_python introspects each callable.
button.clicked.connect(lambda: print("clicked"))
button.clicked.connect(lambda evt: print(evt.widget.x, evt.widget.y))
```

The same `connect` works for `Signal[<T>]` payloads (`IntSignal`, `BoolSignal`, `DoubleSignal`, `StringSignal`, `DialogCodeSignal`, `StandardButtonSignal`, `MenuItemSignal`) and `EventSignal` types (`EventSignal`, `MouseEventSignal`, `KeyEventSignal`). Slot exceptions are surfaced via `PyErr_WriteUnraisable` rather than swallowed.

## Shutdown warnings

If you ever see this on interpreter exit:

```
nanobind: leaked N instances!
nanobind: leaked M types!
nanobind: leaked K functions!
...
nanobind: this is likely caused by a reference counting issue in the binding code.
```

it is **cosmetic** — the OS reclaims the memory normally; nothing actually leaks at runtime. It is nanobind's *liveness check at module finalization*: any bound C++ instance still alive when its module is torn down is reported. The root cause is structural: Wt signals hold Python callables (via `std::shared_ptr<nb::object>` in the connection slot lambdas), and that holder chain keeps both the callables and any bound widgets they capture alive past the point where nanobind takes its census.

To prevent the warning, the bindings maintain a process-wide registry of every connection opened through witty_for_python's `connect()` and expose two helpers:

```python
witty_for_python._live_connection_count()   # diagnostic — how many slot holders we keep
witty_for_python._cleanup_all_connections() # disconnect every one of them
```

`witty_for_python/__init__.py` registers `_cleanup_all_connections()` as an `atexit` handler, so under normal interpreter shutdown the connection registry is flushed *before* nanobind's finalizer runs. The slot lambdas are destroyed, their `shared_ptr<nb::object>` holders drop their references to the Python callables, Python's module-clear pass then reclaims the bound wrappers, and the leak check finds nothing.

In practice this means: under a clean `sys.exit(0)` or end-of-script termination, **the warning does not appear**. It can still surface if you crash hard, call `os._exit()` (which skips `atexit`), or unregister our handler. You can verify the cleanup is wired up by inspecting `witty_for_python._live_connection_count()` in your own atexit handler.

You may also call `witty_for_python._cleanup_signal_slots()` directly between tests, or call `signal.disconnect_all_slots()` on an individual signal — both go through the same registry.

## License

witty_for_python is dual-licensed, mirroring Wt's own dual license:

- **GPL path** — if you use Wt under its GNU GPL Version 2 license, witty_for_python is also available to you under the GNU GPL Version 2 (only). The full text is in [LICENSE](LICENSE). Wt specifies "Other versions of the GPL do not apply" and witty_for_python follows the same restriction.

- **Commercial path** — if you use Wt under [Emweb's commercial license](https://www.webtoolkit.eu/wt/license), you must obtain a separate commercial license for witty_for_python from [Adam DePrince](https://adamdeprince.com) — contact information is at that site.

  **The two commercial licenses are independent.** A Wt commercial license from Emweb does **not** grant you any commercial rights to witty_for_python. A witty_for_python commercial license from Adam DePrince does **not** grant you any commercial rights to Wt. To ship a closed-source product on top of this stack you need *both* commercial licenses; either one alone is insufficient. The two licenses are negotiated separately with their respective copyright holders.

When you redistribute witty_for_python you choose one of these two options (GPL or commercial) and obey its terms. Your choice doesn't need to match what downstream users of your software do; each redistributor makes their own choice.

Copyright (C) 2026 Adam DePrince. All rights reserved.
