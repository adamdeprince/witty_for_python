"""Signal/slot suite.

Covers:
  - void Signal + 0-arg slot
  - typed signals (Int, Bool, Double, String) with arg-receiving slots
  - mixed-arity slots on one signal (some receive payload, some drop it)
  - disconnect() removes one slot; disconnect_all_slots() removes all
  - bound nanobind methods as slots (the `clicked.connect(dlg.show)` pattern)
  - exceptions inside a slot don't crash the dispatcher
  - the connection registry reflects open connections accurately
"""

from __future__ import annotations

import witty_for_python as wt


# ---- void signal ------------------------------------------------------------

def test_void_signal_zero_arg_slot() -> None:
    sig = wt.Signal()
    calls = []
    sig.connect(lambda: calls.append("fired"))
    sig.emit()
    sig.emit()
    assert calls == ["fired", "fired"]


# ---- typed payload signals --------------------------------------------------

def test_int_signal_passes_payload() -> None:
    sig = wt.IntSignal()
    got = []
    sig.connect(lambda v: got.append(v))
    sig.emit(7)
    sig.emit(42)
    assert got == [7, 42]


def test_int_signal_zero_arg_slot_drops_payload() -> None:
    """0-arg slot on a 1-arg signal: payload is silently dropped."""
    sig = wt.IntSignal()
    n = [0]

    def bump() -> None:
        n[0] += 1

    sig.connect(bump)
    sig.emit(99)
    sig.emit(100)
    assert n[0] == 2


def test_string_signal_yields_python_str() -> None:
    """Wt::WString payload arrives as a Python str via the type_caster."""
    sig = wt.StringSignal()
    seen = []
    sig.connect(lambda s: seen.append(s))
    sig.emit("hello")
    sig.emit("world")
    assert seen == ["hello", "world"]
    assert all(isinstance(s, str) for s in seen)


def test_bool_signal() -> None:
    sig = wt.BoolSignal()
    got = []
    sig.connect(lambda b: got.append(b))
    sig.emit(True)
    sig.emit(False)
    assert got == [True, False]


def test_double_signal() -> None:
    sig = wt.DoubleSignal()
    got = []
    sig.connect(lambda x: got.append(x))
    sig.emit(3.14)
    sig.emit(2.71)
    assert got == [3.14, 2.71]


# ---- mixed-arity slots on one signal ---------------------------------------

def test_multiple_slots_mixed_arity() -> None:
    """Each connection's arity is detected separately at connect time."""
    sig = wt.IntSignal()
    events = []
    sig.connect(lambda v: events.append(("with_arg", v)))
    sig.connect(lambda: events.append(("no_arg",)))
    sig.emit(5)
    assert events == [("with_arg", 5), ("no_arg",)]


# ---- disconnect -------------------------------------------------------------

def test_disconnect_stops_one_slot() -> None:
    sig = wt.IntSignal()
    hits = []
    conn = sig.connect(lambda v: hits.append(v))
    sig.emit(1)
    conn.disconnect()
    sig.emit(2)  # not delivered
    assert hits == [1]
    assert not conn.is_connected()


def test_disconnect_all_slots() -> None:
    sig = wt.IntSignal()
    hits = []
    sig.connect(lambda v: hits.append(("a", v)))
    sig.connect(lambda v: hits.append(("b", v)))
    sig.emit(1)
    sig.disconnect_all_slots()
    sig.emit(2)
    assert hits == [("a", 1), ("b", 1)]


# ---- bound-method as slot (nb_bound_method special case) -------------------

def test_bound_nanobind_method_is_zero_arg_slot() -> None:
    """`button.clicked.connect(dlg.show)` — the Qt-style pattern.

    nanobind exposes bound methods as `(*args, **kwargs)` to inspect.signature.
    py_connect special-cases `type(cb).__name__ == "nb_bound_method"` to treat
    the slot as zero-arg. Otherwise an IntSignal would call `target.emit(99)`
    on a zero-arg method and silently fail.
    """
    payload_sig = wt.IntSignal()
    target = wt.Signal()
    fired = []
    target.connect(lambda: fired.append(1))

    payload_sig.connect(target.emit)  # bound method, no args (besides self)

    payload_sig.emit(99)
    payload_sig.emit(100)
    assert len(fired) == 2  # both fires reached target


# ---- exception handling -----------------------------------------------------

def test_slot_exception_does_not_crash_dispatcher() -> None:
    """A raising slot doesn't take down the process; the exception flows
    through PyErr_WriteUnraisable → sys.unraisablehook (so it's observable
    and not silently lost). Subsequent slots on the same signal still fire —
    Wt's dispatcher continues past the exception.
    """
    import sys

    sig = wt.IntSignal()
    later_fired = []
    captured: list = []

    def boom(v: int) -> None:
        raise RuntimeError(f"bang on {v}")

    sig.connect(boom)
    sig.connect(lambda v: later_fired.append(v))

    saved_hook = sys.unraisablehook
    sys.unraisablehook = captured.append
    try:
        sig.emit(42)
    finally:
        sys.unraisablehook = saved_hook

    # The dispatcher continued past `boom`'s raise.
    assert later_fired == [42], "second slot must fire despite the first raising"

    # The exception surfaced via the unraisable hook, not silently dropped.
    assert len(captured) == 1, f"expected 1 unraisable, got {len(captured)}"
    assert isinstance(captured[0].exc_value, RuntimeError)
    assert "bang on 42" in str(captured[0].exc_value)


# ---- connection registry ----------------------------------------------------

def test_live_connection_count_tracks_connects(_fresh_connection_registry) -> None:
    """The C++ registry counts every connection opened via py_connect."""
    assert wt._live_connection_count() == 0

    sig_a = wt.IntSignal()
    sig_b = wt.Signal()
    sig_a.connect(lambda v: None)
    sig_a.connect(lambda: None)
    sig_b.connect(lambda: None)
    assert wt._live_connection_count() == 3

    sig_a.disconnect_all_slots()
    assert wt._live_connection_count() == 1  # sig_b's still there

    wt._cleanup_signal_slots()
    assert wt._live_connection_count() == 0


def test_per_signal_disconnect_all_does_not_affect_other_signals() -> None:
    """disconnect_all_slots() is per-signal — adjacent signals are untouched."""
    a = wt.IntSignal()
    b = wt.IntSignal()
    a_hits, b_hits = [], []
    a.connect(lambda v: a_hits.append(v))
    b.connect(lambda v: b_hits.append(v))
    a.disconnect_all_slots()
    a.emit(1)
    b.emit(2)
    assert a_hits == []
    assert b_hits == [2]
