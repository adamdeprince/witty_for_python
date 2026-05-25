# Multi-threading in witty_for_python

A summary of the threading work and what's safe to do in user code. Read this
before writing anything that touches Wt from a non-Wt thread.

## TL;DR

- **Wt's threading model is "session-as-unit-of-concurrency".** Each session
  has an *update lock*; one thread at a time holds it for a given session.
  All signal emits and widget mutations for that session happen on the
  thread that holds the lock.
- **You don't manage that lock by hand.** Wt acquires it when dispatching
  browser requests, slot fires, posted callbacks, etc. Your widget code in
  those callbacks always runs lock-held.
- **For cross-thread work, use `server.post(session_id, fn)`.** It marshals
  `fn` onto the session's worker thread with the lock already held.
- **Free-threaded Python 3.13t / 3.14t works.** Verified end-to-end against
  `pyenv 3.14.0a6t` on 2026-05-26. The build auto-detects the free-threaded
  ABI and switches nanobind accordingly. Multiple sessions can now run Python
  truly in parallel (no GIL contention between them).
- **Do not emit the same `wt.Signal()` from two threads simultaneously.**
  Wt's signal impl isn't thread-safe; you'll get heap corruption. Doesn't
  matter under standard CPython (GIL hid it); matters immediately under
  3.14t. Detailed below.

## What I built (the binding layer)

| API | What it does | When you'd use it |
|---|---|---|
| `WServer.post(session_id, fn, fallback=None)` | Schedule `fn` to run on the session's worker thread. Wt takes the session lock before calling. Returns immediately. | Background Python thread wants to update widgets in session X. **The canonical cross-thread API.** |
| `WServer.post_all(fn)` | Same, fanned out across every live session. | Broadcast updates (e.g. push a "server going down in 30s" banner). |
| `WApplication.trigger_update()` | Tell the connected browser to fetch the latest DOM. Pair with `post()`. | After a `post()`-delivered mutation, push it to the client. |
| `widget.bind_safe(fn)` | Wrap `fn` so it becomes a no-op if `widget` was destroyed before fire. Inherited from `Wt::Core::observable` — every `WObject` has it. | Wrap any callback you hand to `post()` that touches widget state. Defends against the widget being torn down between schedule and fire. |
| `UpdateLock(app)` + `update_lock(app)` context manager | RAII grab of the session lock from *your* thread. Lower-level escape hatch when `post()` doesn't fit. | Rare. Prefer `post()`. |
| `WApplication.session_id` | The string you pass to `post()`. | Get this inside your factory and stash it for later background work. |

## What I did NOT do

- **Did not patch Wt.** `~/.local/lib/libwt.so` and `libwthttp.so` are stock
  Wt 4.13.2 built from the upstream tarball. Verified with `diff` against
  the source.
- **Did not add Python-side locks around signal emit.** A wrapper-level lock
  would (a) defeat the whole point of free-threading by serialising emits
  that Wt's session lock has already serialised, and (b) silently diverge
  from Wt's documented concurrency model — which violates the rule "the
  wrapper improves ergonomics; it does not change Wt's semantics".

## The hard finding

`Wt::Signal<T>::emit()` is **not safe under concurrent calls on the same
signal**. Source: `Wt/Signals/signals.hpp` — Wt's in-house signal impl uses
non-atomic linked-list pointers and a non-atomic `connected_` flag, with no
mutex anywhere. Wt's design assumes the session update lock serialises
per-session signal access.

I found this by writing a stress test that hammered one signal from four
threads. Under standard CPython the GIL happens to serialise the emits and
the bug is invisible. Under free-threaded 3.14t the GIL is gone and you get
`double free or corruption (out)` immediately — within a couple hundred
emissions.

**This is a Wt-level constraint, not a witty_for_python bug.** The same C++
code emitting `wt::Signal` from two threads has the same problem. We can't
silently fix it without forking Wt.

The supported way to emit from a non-worker thread is `WServer.post()`,
which routes the call onto the worker thread *with the session lock held*
and so satisfies the per-signal serialisation requirement for free.

## Concurrency cheat sheet

| You're doing… | What to do |
|---|---|
| Connecting a slot inside a factory or a normal handler | Just `signal.connect(fn)`. No locks. |
| Connecting / disconnecting from a background thread | Just `signal.connect(fn)` / `conn.disconnect()`. The connection registry has its own `std::mutex`; safe across threads. |
| Reacting to a browser event in a slot | Just write the slot. Wt holds the lock; you can mutate widgets freely. |
| Background Python work that needs to push UI updates | `server.post(session_id, widget.bind_safe(fn))`. The `bind_safe` defends against the widget being gone. Follow up with `app.trigger_update()` *inside* `fn` to push to the client. |
| Several sessions running in the same process | Nothing extra. Free-threaded Python lets them actually run in parallel; under standard CPython the GIL serialises Python execution between them but Wt request handling is still parallel. |
| Standalone `wt.Signal()` outside any Wt session | Treat as single-threaded. If you must share across threads, you wrap your own `threading.Lock()` around `emit()`. Wt won't help here. |
| Emitting the same `wt.Signal()` from two threads simultaneously | **Don't.** Heap corruption under 3.14t. |

## What's verified

End-to-end on 2026-05-26 against `pyenv 3.14.0a6t`:

1. Build flips to `FREE_THREADED` mode: `Building witty_for_python for free-threaded Python (cpython-314t-x86_64-linux-gnu)`. Wheel tag `cp314-cp314t`.
2. Full signal/slot suite (10 cases incl. arity introspection, bound-method-as-slot, disconnect/reconnect) — all green.
3. Multi-threaded stress, **disjoint signals** per thread (the supported pattern): 4 threads × 5000 emits × own `IntSignal` → 20 000 emits, zero losses, ~4M emits/sec. No GIL contention.
4. Multi-threaded stress, **shared signal** (violating Wt's contract): heap corruption within ~200 emits. Documented as a known unsafe pattern.

## CMake mechanics

The relevant chunk of `CMakeLists.txt`:

```cmake
if(Python_SOABI MATCHES "t$" OR Python_SOABI MATCHES "t-")
  message(STATUS "Building witty_for_python for free-threaded Python (${Python_SOABI})")
  nanobind_add_module(_witty_for_python FREE_THREADED NB_STATIC ${PYWITTY_SOURCES})
else()
  nanobind_add_module(_witty_for_python STABLE_ABI NB_STATIC ${PYWITTY_SOURCES})
endif()
```

`STABLE_ABI` (the "abi3" build that works across CPython 3.12+ without
recompile) and `FREE_THREADED` are mutually exclusive in nanobind — pick one
per build based on the host interpreter's ABI tag. The detection key is the
`t` suffix in `Python_SOABI`, which CPython sets only for free-threaded
builds.

## Open gaps

- **No CI yet** for the free-threaded build. Manually verified once; will
  silently regress if nanobind 2.12+ or Wt 4.13+ change their thread model.
  Adding `pyenv 3.14.0a6t` and a few stress tests to a CI job is the obvious
  next step.
- **nanobind 2.12 free-threaded support is still labelled experimental** by
  upstream. Even with our binding correct, a free-threaded edge case in
  nanobind itself could surface. If you hit one, bisect against nanobind
  before blaming witty_for_python.
- **No `WApplication::bind`** in Wt 4.13 — the docstring in `WServer.h`
  references it but it doesn't exist. The real primitive is one layer
  down, on `Wt::Core::observable::bindSafe`, which `WObject` inherits.
  That's what `widget.bind_safe(fn)` exposes.

## Files I touched (no Wt patches; pure wrapper-side changes)

- `ext/bind_server.cpp` — `WServer.post`, `post_all`
- `ext/bind_application.cpp` — `UpdateLock`, `trigger_update`, `session_id`, `bind_safe` on `WObject`
- `src/witty_for_python/__init__.py` — `update_lock(app)` context manager
- `CMakeLists.txt` — free-threaded ABI detection + nanobind flag switch
- `ext/signal_helpers.hpp`, `ext/bind_signals.cpp` — connection registry + `gil_scoped_acquire` in slot lambda (these were already there from earlier work; reviewed for correctness)

That's the entire surface area.
