"""WTimer suite.

WTimer cannot be constructed outside an active WApplication session — its
constructor creates an internal WTimerWidget that touches session state.
The end-to-end behaviour (start/stop, timeout firing, interval round-trip)
is exercised by the gallery boot test, which spins up a real session.

Here we only verify the *binding* surface: the class is exposed with the
expected attributes, the right inheritance, and the right constructor
arity.
"""

from __future__ import annotations

import witty_for_python as wt


def test_wtimer_class_is_exposed() -> None:
    assert wt.WTimer is not None
    assert isinstance(wt.WTimer, type)


def test_wtimer_inherits_wobject() -> None:
    """WTimer extends WObject upstream — needed so it participates in the
    same lifetime machinery as widgets."""
    assert issubclass(wt.WTimer, wt.WObject)


def test_wtimer_method_surface() -> None:
    """Listed methods + properties must be present so user code that touches
    them doesn't AttributeError. We can't call them without a session, but
    we can verify they're bound."""
    for attr in ("start", "stop", "interval", "is_active", "single_shot",
                 "timeout"):
        assert hasattr(wt.WTimer, attr), f"missing attribute: {attr}"


def test_wtimer_init_docstring_signature() -> None:
    """nanobind exposes the C++ overload signature in the __init__ docstring.
    inspect.signature() doesn't work on bound C++ methods (they look variadic
    to Python introspection), so we read the docstring directly. The C++
    WTimer constructor takes no arguments."""
    doc = wt.WTimer.__init__.__doc__ or ""
    # nanobind formats it as 'name(self) -> None' for a no-arg ctor.
    assert "(self)" in doc or "(self, /)" in doc, (
        f"unexpected ctor signature in docstring: {doc!r}")
