# witty_for_python

**witty_for_python** wraps the [Wt (Web Toolkit)](https://www.webtoolkit.eu/wt) C++ widget framework as a Python library. You build server-side web apps the way you'd build a desktop app — widget trees (`WContainerWidget`, `WPushButton`), signal/slot wiring, MVC models, validators, painting, charts — and Wt handles every browser round-trip transparently: DOM diffs over the wire, progressive JavaScript enhancement, real-time server push. There are no HTML templates to maintain, no separate JavaScript client to keep in sync, and no manual WebSocket plumbing for live updates. Reach for it when you want real per-session server state without cookie-and-Redis stitching, type-checked Python all the way to the browser boundary, and a single-wheel deploy — Wt 4.13 is bundled inside the wheel, no system install required.

Built with [nanobind](https://github.com/wjakob/nanobind). You write a Python factory that returns a `WApplication`; Wt's session manager owns the widget tree from that point on.

> **Independent, unofficial wrapper.** witty_for_python is a personal project by [Adam DePrince](https://adamdeprince.com). It is **not** produced by, endorsed by, sponsored by, or otherwise affiliated with Emweb bv, the authors and copyright holders of Wt. "Wt" is referenced here only in its descriptive sense — to identify the library this software wraps — and remains the property of Emweb. For Wt itself (source, official binaries, support, commercial licensing), go directly to [www.webtoolkit.eu/wt](https://www.webtoolkit.eu/wt).

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

- **Wt acquisition** — vendored as a git submodule at `extern/wt`, currently pinned to release 4.13.2. `CMakeLists.txt` uses `add_subdirectory(extern/wt EXCLUDE_FROM_ALL)` after pre-setting Wt's CMake options. The wheel bundles `libwt.so` + `libwthttp.so` (in `_libs/`) and Wt's static resources (in `_wt_resources/`). No system Wt install required. Pinning a specific commit gives us GPL source traceability — every binary we produce links a known Wt source tree. See [building_wt.md](building_wt.md).
- **TinyMCE acquisition** — vendored as a git submodule at `extern/tinymce`, pinned to tag `tinymce@6.8.4` (MIT-licensed at that tag). `CMakeLists.txt` runs `yarn install` + `yarn build` against the submodule and installs the built `js/tinymce/` tree to `_wt_resources/tinymce/`, where Wt's `WTextEdit` looks for it by default. Same forensic story as Wt: the gitlink in our history is the source-traceability anchor. Set `-DWITTY_FOR_PYTHON_BUILD_TINYMCE=OFF` to skip — useful for dev cycles where you don't need rich text and want to avoid the ~5-minute Node-side build.
- **Ownership** — Wt 4 is `std::unique_ptr`-based. `add_widget` / `set_layout` take `std::unique_ptr<T>` and *invalidate the Python wrapper on the caller side*; callers must rebind to the returned non-owning handle. Factory callbacks for `add_entry_point` use `std::function<unique_ptr<WApplication>(const WEnvironment&)>` so the returned Python `WApplication` ownership transfers cleanly to Wt.
- **Strings** — `Wt::WString` is bound transparently to Python `str` via a custom `nb::type_caster` in `ext/common.hpp`. Do not bind `WString` as a distinct Python type; just use it in C++ signatures and the caster handles the conversion.
- **Signals** — Python callables are wrapped in `std::shared_ptr<nb::object>` held by the connection. Slot fires acquire the GIL (or no-op under free-threading). See [signal_slot.md](signal_slot.md).
- **Source layout**: C++ lives in `ext/` (one `bind_<topic>.cpp` per concern, with `common.hpp` shared); the Python package is in `src/witty_for_python/`. scikit-build-core installs the compiled `_witty_for_python` extension into `witty_for_python/`.

## What else lives in `docs/`

- [binding_design.md](binding_design.md) — the rules for adding to or changing the bindings. Read before touching `ext/`.
- [signal_slot.md](signal_slot.md) — signal/slot architecture, arity introspection, connection registry, bound-method detection.
- [threading.md](threading.md) — threading model, cross-thread APIs, free-threaded Python 3.14t status, Wt's per-signal serialisation constraint.
- [building_wt.md](building_wt.md) — how Wt is vendored at `extern/wt`, the CMake options we set on it, the wheel layout, and how to bump the pin.

## Build command (TL;DR)

```bash
git clone --recursive ...   # or `git submodule update --init --recursive`
/path/to/python -m pip install --no-build-isolation -e .
```

Run from the repo root — scikit-build-core's discovery breaks if you run from `ext/`.

The compiled `.so` has an RPATH baked in pointing at `$ORIGIN/_libs` (the bundled Wt libraries), so `import witty_for_python` works without `LD_LIBRARY_PATH` and without any system Wt install.
