# Instructions for AI assistants working on witty_for_python

This file is the entry point for any AI tool (Codex, Claude Code, Cursor, Aider, etc.) working in this repo. The same content is useful to humans; nothing here is tool-specific.

## What this project is

witty_for_python is a nanobind-based Python binding for [Wt](https://www.webtoolkit.eu/wt) — Emweb's C++ widget-tree web framework. The Python package is named `witty_for_python` and is conventionally imported as `wt`:

```python
import witty_for_python as wt
```

See [docs/overview.md](docs/overview.md) for the full picture.

## Read these before changing anything

| Concern | Doc |
|---|---|
| Project goals, scope, build stack, source layout | [docs/overview.md](docs/overview.md) |
| **The rules for adding to or changing the bindings** — read this first | [docs/binding_design.md](docs/binding_design.md) |
| Signal/slot architecture; arity introspection; connection registry; shutdown leak handling | [docs/signal_slot.md](docs/signal_slot.md) |
| Threading model; cross-thread APIs; Wt's per-signal serialisation constraint; free-threaded Python 3.14t status | [docs/threading.md](docs/threading.md) |
| How Wt is vendored at `extern/wt` and built as part of `pip install` | [docs/building_wt.md](docs/building_wt.md) |

## The single load-bearing rule

> **The wrapper improves ergonomics; it does not change Wt's semantics.**

(`binding_design.md` §0.) Any "wouldn't it be nice if the wrapper just …" idea must pass the line-by-line-translation test: would the same Python code, written in C++ with Wt directly, do the same thing? If no, you're changing semantics — reject. If yes — ship it.

Things this rule already vetoed: auto-setting `WSelectionBox.vertical_size` on `add_item`; auto-checking the first radio button added to a `WButtonGroup`; "fixing" any Wt default. Things this rule allows: implicit `str → WLink` conversion, snake_case + property style, the arity-introspecting `connect()`.

## Build / run

Wt is vendored as a git submodule at `extern/wt` and built as part of `pip install`. No separate Wt install needed.

```bash
git clone --recursive ...      # or: git submodule update --init --recursive
/path/to/python -m pip install --no-build-isolation -e .
```

System build deps (Boost dev headers, zlib dev) and toolchain expectations are in [docs/building_wt.md](docs/building_wt.md). Run pip from the repo root. The build auto-detects free-threaded Python (`t`-ABI) and switches nanobind to its free-threaded mode accordingly.

## Demo

```bash
python examples/gallery.py \
    --docroot . \
    --http-address 127.0.0.1 --http-port 8080 \
    --resources-dir "$HOME/.local/share/Wt/resources"
```

Open <http://127.0.0.1:8080>. The gallery exercises every bound widget and signal type — it's the closest thing to a regression test we have.

## File layout

```
ext/                          C++ binding source (one bind_<topic>.cpp per concern)
  common.hpp                  nanobind includes, WString caster, namespace decls
  signal_helpers.hpp          py_connect, python_arity, connection registry
  module.cpp                  NB_MODULE entrypoint
  bind_signals.cpp            signals, events, registry impl
  bind_application.cpp        WObject through WApplication, UpdateLock
  bind_container.cpp          WContainerWidget
  bind_widgets.cpp            basic widgets
  bind_form.cpp               form widgets
  bind_navigation.cpp         tabs, dialogs, menus, panels
  bind_table.cpp              WTable
  bind_layout.cpp             layouts
  bind_server.cpp             WServer, post/post_all
src/witty_for_python/         Python package (compiled extension installs here)
examples/                     Sample apps (gallery.py is the canonical demo)
docs/                         Design documentation (this file points to it)
CMakeLists.txt
pyproject.toml
README.md
```

## Style notes for code you generate or edit

- **Don't write code comments for the sake of it.** Comments earn their place by explaining *why*, *non-obvious constraints*, or *gotchas* — not by restating what the code does.
- **Demos must be exemplary.** `setattr` inside a lambda is a code smell; use a named `def` (see binding_design.md §6). No magic numbers tied to content count — query the collection.
- **Properties for behaviorless getters**, methods for verbs (see binding_design.md §7).
- **`str → wrapper` implicit conversion** where the wrapper has a single unambiguous primitive constructor (see binding_design.md §1).
- **Snake_case** Python names: `setText` → `set_text` method *or* `text` property; `currentIndex` → `current_index` property.

## When you discover something new

If you find a new Wt gotcha, design constraint, or non-obvious convention worth preserving:

- Code-level fix → comment at the binding site, referencing which doc rule it follows.
- Cross-cutting → update the relevant `docs/*.md`. Don't create new top-level files unless a topic genuinely doesn't fit anywhere.
- Python-only divergence from Wt API → also add a row to the "Python-only divergences" table in [docs/binding_design.md](docs/binding_design.md) §-1.

This entrypoint should stay short; it's a router. The detail belongs in `docs/`.
