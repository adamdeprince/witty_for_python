# Binding design rules

These rules were established through user feedback and reflect choices to preserve. Apply them when adding to or modifying `ext/`.

The most load-bearing rule is §0. Read that first.

---

## §-1. When we diverge from "obvious" Wt-equivalence, label it

Some witty_for_python bindings have no direct Wt counterpart — Python-only conveniences we added because the equivalent Wt idiom (typically a templated `addNew<T>(...)` or a manual `make_unique` + `addWidget`) doesn't translate cleanly. **Every such divergence must be labelled** in two places:

1. **In the C++ binding** — a comment immediately above the `.def(...)` block stating what Wt operation it composes from and why we added it. Example from `bind_container.cpp`:
   ```cpp
   // String overload: wraps the text in a freshly-constructed WText.
   // Python-only convenience (Wt's C++ idiom is addWidget(make_unique<WText>(s))).
   .def("add_widget",
        [](Wt::WContainerWidget& self, const Wt::WString& text) -> Wt::WText* { … },
        ...)
   ```
2. **In this doc** — listed in the "Python-only divergences" table below.

**Why**: a future maintainer (human or AI) reading Wt's C++ docs should be able to spot which witty_for_python methods are real Wt API and which are inventions. Unlabelled inventions look like Wt API that the maintainer "ought to" know about, leading to wasted hunting in Wt's source.

### Python-only divergences (current list)

| Python method | Equivalent Wt expression | Why |
|---|---|---|
| `WContainerWidget.add_widget(str)` | `addWidget(std::make_unique<WText>(str))` | `add_widget` is polymorphic on its argument type: widget instance → owned-add; str → wraps in a `WText`. Wt has no string-form of `addWidget`; we prefer this to a separate `add_text` because users shouldn't have to choose. |
| `WContainerWidget.add_widgets(iterable[widget \| str])` | `for w in ws: c.addWidget(w)` | Bulk version of `add_widget`. Returns `list[WWidget]` / `list[WText]` so callers can mutate the returned handles. Same polymorphism as the single form. |
| `WBoxLayout.add_widgets(iterable[widget])` (inherited by `WHBoxLayout`/`WVBoxLayout`) | `for w in ws: layout.addWidget(w, 0)` | Bulk version of `WBoxLayout.add_widget`. Adds each with default stretch=0; use the single form when per-widget stretch matters. |
| `WMenu.add_item(str)` | `addItem(std::make_unique<WMenuItem>(label))` | Same principle as `add_widget`: str gets wrapped in `WMenuItem` automatically. Pre-built items pass through unchanged. |
| `WComboBox.add_items(iterable[str])` (inherited by `WSelectionBox`) | `for x in xs: combo.addItem(x)` | Bulk-add ergonomic. Wt has no `addItems`. |
| `WMenu.add_items(iterable[str \| WMenuItem])` | `for x in xs: menu.addItem(...)` | Bulk version of `add_item`. Two overloads — strings get wrapped, pre-built items pass through. |

**General pattern for "single + bulk" pairs**: every `add_X(item)` should have a matching `add_Xs(iterable)` that loops the single form and returns a list of the added items (with `nb::rv_policy::reference_internal`). Both should be polymorphic over the obvious primitive (str → wrapped natural item) where it makes sense. The return-the-added-thing convention enables one-line chains: `form.add_widget(wt.WPushButton("ok")).clicked.connect(handler)`.

Add new rows as we add new Python-only conveniences. **Do not** add anything to this table that has a 1:1 Wt counterpart — those are just bindings, not divergences.

---

## §0. The wrapper improves ergonomics; it does not change Wt's semantics

This is the load-bearing principle behind every other rule. Apply it whenever a "wouldn't it be nice if the wrapper just …" thought arises.

**Allowed (ergonomic)**: changes to the *expression* of Wt's API that don't alter what happens at runtime.

- `wt.WAnchor("...")` instead of `wt.WAnchor(wt.WLink("..."))` — same runtime, prettier code (§1).
- snake_case methods, property-style attributes — same calls under the hood (§7).
- `button.clicked.connect(dlg.show)` — same C++ slot, smarter introspection (§3).
- `def on_click(evt):` over `lambda evt:` — same effect, more readable (§6).

**Forbidden (semantic)**: changes to runtime behavior, defaults, side-effects, or invariants that someone reading Wt's C++ docs would not predict.

- Auto-setting `WSelectionBox.vertical_size` to `count()` on every `add_item()` (would override explicit user values; diverges from Wt's documented default; doesn't generalize to `WComboBox`).
- Auto-checking the first radio button when added to a `WButtonGroup`.
- Auto-attaching a `WLabel` to the next widget the user adds.
- "Fixing" any Wt default — defaults are Wt's contract.
- Hiding ownership transfer (we make it visible via the rebind-to-return pattern, §4).

**Test for any new convenience**: would the same Python code, translated line-by-line to C++, do the same thing in a Wt program? If no, you're changing semantics — reject. If yes — ship it.

Bulk convenience methods (`add_items(iterable)` etc.) are fine as long as they're *additive* — new entrypoints that loop the existing primitives. They don't touch defaults; users opt in by calling them.

---

## §1. Implicit `primitive → wrapper` conversion

**Rule**: If a binding endpoint takes a wrapper class that has exactly *one unambiguous* "from primitive" constructor, mark that constructor with `nb::init_implicit<Primitive>()`. Users get the primitive everywhere the wrapper is expected, for free.

**Why**: Forcing `wt.WAnchor(wt.WLink("..."), "text")` over `wt.WAnchor("...", "text")` is friction with no payoff. The wrapper exists so *advanced* uses (resources, internal paths, etc.) remain available, not to make the common case verbose.

> User test (paraphrased): *"an API endpoint that accepts an object, one object type, that accepts a single str as a parameter, should automatically create that object if they get a string and it's unambiguous as to what object would be created."*

**Applied to**:

- `WLink` (`nb::init_implicit<std::string>()` in `bind_widgets.cpp`). Covers `WAnchor`/`WImage` constructors, `WAnchor.link =`, `WImage.image_link =`, `WPushButton.link =`.
- `WString` (custom `type_caster` in `ext/common.hpp`). Covers every constructor and setter taking `const WString&` — `WText("hi")`, `WPushButton("ok")`, `WLabel("name:")`, `WDialog("title")`, etc. **Do not bind WString as a Python class** — the caster does the work.

**Do not apply to**:

- Multi-argument wrappers (`WPointF(x, y)`, `WRectF`, `WBorder`) — no single primitive disambiguates.
- Enums (`Orientation`, `LayoutDirection`, `StandardButton`) — typed enums are how Python expresses these; stringly-typed alternatives are worse.
- Wrappers with multiple equally-plausible primitive forms (`WColor("red")` vs `WColor(r, g, b)`) — overload-resolution ambiguity.

There's a tiny helper `_link_url(WLink)` exposed by `module.cpp` for tests that need to verify a `WLink`-taking endpoint without setting up a `WApplication` context. Reuse this pattern when adding implicit conversions for new wrapper types.

---

## §2. Signal/slot binding pattern

**Rule**: Every `Wt::Signal<T>` / `Wt::EventSignal<T>` instantiation is a distinct C++ type and gets a distinct Python class. Wire them through the `py_connect<SigT, Args...>` helper in `signal_helpers.hpp` — never roll a new connect lambda. Required boilerplate per type:

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

`py_connect` centralises (a) Python-callable arity introspection, (b) GIL acquisition in the slot, (c) error surfacing via `PyErr_WriteUnraisable`, (d) connection registration for atexit cleanup. Bypassing it loses all four.

**Also update** `_SIGNAL_TYPES` in `src/witty_for_python/__init__.py` so the atexit walker covers your new type. Full background in [signal_slot.md](signal_slot.md).

---

## §3. Slot arity rules

`py_connect` decides at connect time how many args to forward to a Python callable:

| Callable kind | Arity treated as | Effect |
|---|---|---|
| `def f()` / `lambda: ...` | 0 | Payload dropped |
| `def f(x)` / `lambda x: ...` | 1 | Payload passed |
| `def f(*args)` / variadic | -1 | All args forwarded |
| `nanobind.nb_bound_method` (e.g. `dlg.show`) | **0** (special) | Payload dropped |
| Anything where `inspect.signature` raises | -1 | All args forwarded |

**Why the bound-method special case**: nanobind exposes bound methods as `(*args, **kwargs)` to `inspect.signature`, so without the special case `clicked.connect(dlg.show)` would attempt `dlg.show(WMouseEvent)` and silently `PyErr_WriteUnraisable`. The Qt-style `button.clicked.connect(dialog.show)` is the dominant pattern users want; we explicitly support it. If someone genuinely wants a bound method to *receive* payload, they wrap: `sig.connect(lambda x: obj.method(x))`.

Detection: `type(cb).__name__ == "nb_bound_method"`. Don't use `PyTypeObject::tp_name` directly — it's hidden under the limited ABI we use.

---

## §4. Ownership transfer

Wt 4 owns its widget tree via `std::unique_ptr`. Mirror that in the binding:

```cpp
.def("add_widget",
     [](Wt::WContainerWidget& self, std::unique_ptr<Wt::WWidget> w) -> Wt::WWidget* {
         Wt::WWidget* raw = w.get();
         self.addWidget(std::move(w));
         return raw;
     },
     nb::arg("widget"),
     nb::rv_policy::reference_internal)
```

Two important details:

- The non-template `addWidget(unique_ptr<WWidget>)` returns `void`. Snapshot the raw pointer **before** moving (the templated `addWidget<Widget>(unique_ptr<Widget>)` returns the pointer, but you can't instantiate it generically here).
- Use `nb::rv_policy::reference_internal` so the returned wrapper is non-owning and its lifetime is tied to the parent.

After `add_widget`, the *caller's* original Python wrapper is invalidated by nanobind's `unique_ptr` ownership transfer. Examples and demos must rebind to the return:

```python
button = root.add_widget(wt.WPushButton("ok"))  # original wrapper invalidated
button.text = "clicked"                          # safe — non-owning handle
```

**Application factories** for `add_entry_point` should be typed as `std::function<std::unique_ptr<Wt::WApplication>(const Wt::WEnvironment&)>` so nanobind's std::function caster handles the Python→C++ ownership transfer when the factory returns its `WApplication`.

---

## §5. Inheritance — only register a base that is *actually* a base

`nb::class_<T, Base>` requires `Base` to be a direct or indirect C++ base of `T`. Get it wrong and compilation fails with the cryptic `static_assert ... (1 == 0)` deep in `nb_class.h`. Verified Wt 4.13 chains:

- `WWidget → WWebWidget → WInteractWidget → WFormWidget` → `WLineEdit`, `WCheckBox` (via `WAbstractToggleButton`), `WRadioButton`, `WSpinBox`/`WDoubleSpinBox` (via `WAbstractSpinBox` then `WLineEdit`), `WSlider`, `WComboBox`, `WPushButton`, `WTextArea`
- `WInteractWidget → WContainerWidget` → `WAnchor`, `WTableCell`, `WMenuItem`, `WGroupBox`, `WStackedWidget`
- `WInteractWidget` (direct) → `WText`, `WImage`, `WLabel`, `WTable`, `WProgressBar`
- **`WWidget → WCompositeWidget` (skips WInteractWidget)** → `WTabWidget`, `WMenu`, `WPanel`, `WPopupWidget → WDialog → WMessageBox`. These take **`WWidget` as their Python-visible base**, not `WInteractWidget`.

**Other Wt 4.13 gotchas already burned in**:

- `WRadioButton::setGroup()` is **private**. Put buttons into a group from the group side: `group.add_button(rb, id=-1)`.
- `WEnvironment::sessionId()` doesn't exist as a getter (despite naming convention) — don't try to bind it. (`WApplication::sessionId()` *does* exist and is bound as a property.)
- `Wt::LayoutDirection` is a top-level enum in `WGlobal.h`, not nested inside `WBoxLayout`.
- `WTable::insertRow(int, unique_ptr<WTableRow> = nullptr)` and `insertColumn` have two parameters; if you only bind the int form, wrap in a lambda that supplies the default.
- `WContainerWidget::addWidget(unique_ptr<WWidget>)` returns `void` (the templated `Widget* addWidget<Widget>(unique_ptr<Widget>)` overload returns the pointer).
- `WApplication::bind()` doesn't exist despite being referenced in `WServer.h`'s docstring — the real primitive is one layer down, on `Wt::Core::observable::bindSafe`, which `WObject` inherits. Bound as `widget.bind_safe(fn)`.

---

## §6. Demos must be exemplary — readers infer "wrapper quality" from `examples/`

Demos are advertising. A reader who sees ugly code in `examples/gallery.py` concludes the wrapper itself is awkward, even if the binding is fine.

**6a. `def` over `lambda` for any assignment**:

```python
# Wrong — looks hostile, suggests the wrapper is awkward
button.clicked.connect(lambda v: setattr(label, "text", f"{v}"))

# Right — named handler, natural attribute syntax
def on_click(v: int) -> None:
    label.text = f"{v}"

button.clicked.connect(on_click)
```

Python lambdas can only contain *expressions*; `obj.attr = value` is a *statement*. `setattr(...)` in a lambda is a language workaround that screams "this binding is hard to use" — exactly the opposite of what a demo is for. Named `def` handlers read better *and* are idiomatic Python anyway.

**6b. Pass bound methods directly when possible** — `button.clicked.connect(dlg.show)` works (§3). Wrap in `lambda: dlg.show()` only when the slot needs to compose with non-callable logic.

**6c. No magic numbers that have to be inferred from context**. If a number is "the count of items I just typed", *query* it; don't hard-code it.

```python
# Wrong — reader has to count to realize "ah, 4 == number of items"
sel.vertical_size = 4

# Right — the intent is plain
sel.vertical_size = sel.count
```

Same principle applies to `WTable` headers/rows (use `len(rows)` not the literal), spin-box ranges that match a list length, etc. If the constant isn't tied to content, name it (`MAX_AGE = 150`). If it is tied to content, query the wrapper or the source collection.

**6d. Type annotations on signal handlers** so the reader sees the slot's expected payload:

```python
def on_volume(v: int) -> None: ...
def on_finished(code: wt.DialogCode) -> None: ...
def on_click(evt: wt.WMouseEvent) -> None: ...
```

This is how the demo teaches readers what the signal carries — better than a comment.

---

## §7. Property vs method style

**Rule**: behaviorless getters (pure data access, no observable side effect, idempotent) are exposed as **read-only properties** via `def_prop_ro`. Getter/setter pairs become **read-write properties** via `def_prop_rw`. Only methods that *do* something (verbs: act, mutate, emit, request) stay as methods.

```cpp
// Property (no side effect)
.def_prop_ro("count", &Wt::WContainerWidget::count)
.def_prop_ro("contents", &Wt::WDialog::contents, nb::rv_policy::reference_internal)
.def_prop_rw("hidden",
    [](const Wt::WWidget& w) { return w.isHidden(); },
    [](Wt::WWidget& w, bool h) { w.setHidden(h); })

// Method (action)
.def("clear", &Wt::WContainerWidget::clear)
.def("accept", &Wt::WDialog::accept)
.def("set_focus", nb::overload_cast<>(&Wt::WFormWidget::setFocus))
```

**Why**: Python users expect `dlg.contents.add_widget(...)` (attribute), not `dlg.contents().add_widget(...)` (method call). The empty `()` reads as "we're doing something" — false signal when the call is just a getter. Properties also collapse `isX()`/`setX()` pairs into a single `x` attribute, which is closer to what the C++ semantics actually mean.

**What counts as "behaviorless"**: a getter is behaviorless if calling it twice in a row is observably the same as calling it once. Lazy-created stable objects (e.g. `WDialog::contents()` which creates the container on first access then returns it forever) qualify — multiple calls return the same object.

**What stays a method**: anything verb-like — `add_widget`, `clear`, `emit`, `accept`, `reject`, `collapse`, `expand`, `show`, `select`, `set_focus`, `set_range`, etc. Setters that don't pair with a same-named getter (e.g. `set_range(min, max)`) also stay as methods.

C++ naming → Python naming:

- `isX()` / `hasX()` → property `x` / `has_x`.
- `setX()` + `X()` pair → single property `x` (rw).
- Pure getter without setter → `def_prop_ro("x", ...)`.
- Verb method (`setText` on its own, `addWidget`, etc.) → `def("snake_case_name", ...)` — `setBuddy` → `set_buddy`, `currentIndex` → property `current_index`.

---

## §8. File layout

| File | Contents |
|---|---|
| `ext/common.hpp` | nanobind includes, `WString` ↔ `str` caster, namespace + `register_*` declarations |
| `ext/signal_helpers.hpp` | `py_connect` template, `python_arity`, connection registry interface |
| `ext/module.cpp` | `NB_MODULE` entrypoint; `register_*` calls in **base-classes-first order**; module-level helpers (`_cleanup_all_connections`, `_live_connection_count`, `_link_url`) |
| `ext/bind_signals.cpp` | Signal/EventSignal types, `WMouseEvent`, `WKeyEvent`, `Coordinates`, event-related enums (Key, MouseButton, KeyboardModifier), connection registry impl |
| `ext/bind_application.cpp` | Core inheritance chain: WObject, WWidget, WInteractWidget, WFormWidget, WApplication, WEnvironment, UpdateLock |
| `ext/bind_container.cpp` | WContainerWidget |
| `ext/bind_widgets.cpp` | Basic widgets: WText, WPushButton, WLineEdit, WCheckBox, WAnchor, WImage, WLink |
| `ext/bind_form.cpp` | WSpinBox, WDoubleSpinBox, WTextArea, WSlider, WComboBox, WSelectionBox, WRadioButton, WButtonGroup, WProgressBar, WLabel, WBreak; Orientation, SelectionMode enums |
| `ext/bind_navigation.cpp` | WTabWidget, WMenu, WMenuItem, WStackedWidget, WPanel, WGroupBox, WDialog, WMessageBox; DialogCode, StandardButton enums |
| `ext/bind_table.cpp` | WTable, WTableCell, WTableRow, WTableColumn |
| `ext/bind_layout.cpp` | WLayout, WBoxLayout, WHBoxLayout, WVBoxLayout, WGridLayout; LayoutDirection enum |
| `ext/bind_server.cpp` | WServer, EntryPointType, post/post_all |

When you add a new binding source: append it to `PYWITTY_SOURCES` in `CMakeLists.txt`, add a `register_xxx` declaration in `ext/common.hpp` *inside the `witty_for_python` namespace*, call it from `NB_MODULE` in `ext/module.cpp` after its base classes are registered, then re-export new public names from `src/witty_for_python/__init__.py` (both the `from ._witty_for_python import (...)` block *and* the `__all__` list).

---

## §9. Stable ABI is on (when GIL is on) — design for it

`CMakeLists.txt` builds the extension with `STABLE_ABI` (defining `Py_LIMITED_API=0x030C0000`) on standard CPython, and switches to `FREE_THREADED` for the `t`-ABI builds. They are mutually exclusive — nanobind enforces this. Consequences:

- `PyTypeObject` is opaque under stable ABI. Access `tp_name` etc. via Python: `nb::handle(reinterpret_cast<PyObject*>(Py_TYPE(obj.ptr()))).attr("__name__")`.
- Use only the limited-API subset of Python's C API.
- The standard-ABI compiled `.so` works across CPython 3.12+ without recompilation.
- Free-threaded builds get a fresh `.so` per Python version (no stable ABI for `t` builds yet upstream).

---

## §10. Shutdown leak warnings — don't break the atexit cleanup

`src/witty_for_python/__init__.py` registers `_cleanup_signal_slots` (which calls `_cleanup_all_connections` from C++) as an `atexit` handler. The C++ side maintains a process-wide registry of every connection opened through `py_connect`. Under clean shutdown nanobind's "leaked instances" diagnostic disappears entirely.

**Do not** revert to enumerating signals via `gc.get_objects()` from Python — nanobind-bound instances are not GC-tracked, and they are not `weakref`-able either. The C++ side has to drive the cleanup. Full reasoning in [signal_slot.md](signal_slot.md).

---

## §11. Build environment

`CMAKE_PREFIX_PATH=$HOME/.local` because Wt 4.13.x is built from source into the user prefix (see [building_wt.md](building_wt.md)). The extension's RPATH is `$HOME/.local/lib` (set via `CMAKE_INSTALL_RPATH_USE_LINK_PATH`), so `import witty_for_python` works without `LD_LIBRARY_PATH`.

```bash
CMAKE_PREFIX_PATH="$HOME/.local" \
  /path/to/python -m pip install --no-build-isolation -e .
```

Run from the repo root — scikit-build-core's discovery breaks if you run from `ext/`.
