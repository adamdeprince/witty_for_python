"""Date/time value-type caster + widget bindings.

`WDate`, `WTime`, and `WDateTime` are exposed as Python `datetime.date`,
`datetime.time`, and `datetime.datetime` via custom `nb::type_caster`s in
`ext/datetime_caster.hpp` — they are *not* bound as their own Python types
(same convention as `WString` ↔ `str`).

The caster round-trip is tested via three module-level helpers:
`_round_trip_date`, `_round_trip_time`, `_round_trip_datetime`. The
date/time validators (which take `WDate`/`WTime` as range bounds) are
also exercised here because they roundtrip the casters in real binding
endpoints.
"""

from __future__ import annotations

import datetime

import witty_for_python as wt
from witty_for_python._witty_for_python import (
    _round_trip_date,
    _round_trip_datetime,
    _round_trip_time,
)


# ---- caster round-trips ----------------------------------------------------

def test_date_round_trip() -> None:
    d = datetime.date(2026, 5, 26)
    assert _round_trip_date(d) == d
    assert isinstance(_round_trip_date(d), datetime.date)


def test_time_round_trip_to_millisecond_precision() -> None:
    t = datetime.time(14, 30, 15, 250_000)  # 250 ms expressed as μs
    assert _round_trip_time(t) == t


def test_time_loses_sub_millisecond_precision() -> None:
    """Wt::WTime is ms-resolution; Python time is μs-resolution.
    Documented contract: the trip truncates μs → ms × 1000."""
    lossy = datetime.time(0, 0, 0, 250_999)  # 250.999 ms
    assert _round_trip_time(lossy) == datetime.time(0, 0, 0, 250_000)


def test_datetime_round_trip() -> None:
    dt = datetime.datetime(2026, 5, 26, 12, 34, 56)
    assert _round_trip_datetime(dt) == dt


def test_datetime_passed_as_date_drops_time() -> None:
    """datetime.datetime is a subclass of datetime.date in stdlib. Passing
    one to a WDate-taking endpoint extracts year/month/day; the time
    component is silently dropped (intended — matches Python semantics)."""
    out = _round_trip_date(datetime.datetime(2026, 1, 2, 3, 4, 5))
    assert out == datetime.date(2026, 1, 2)
    assert isinstance(out, datetime.date)


# ---- WDateValidator --------------------------------------------------------

def test_date_validator_range_round_trip() -> None:
    bottom = datetime.date(2026, 1, 1)
    top = datetime.date(2026, 12, 31)
    v = wt.WDateValidator(bottom, top)
    assert v.bottom == bottom
    assert v.top == top


def test_date_validator_validates_strings() -> None:
    """Validators take a *string* and return ValidationResult — the
    range bounds are WDate but the input parses through Wt's format."""
    v = wt.WDateValidator(datetime.date(2026, 1, 1), datetime.date(2026, 12, 31))
    assert v.validate("2026-06-15").state == wt.ValidationState.Valid
    assert v.validate("2027-06-15").state == wt.ValidationState.Invalid
    assert v.validate("not a date").state == wt.ValidationState.Invalid


def test_date_validator_bottom_top_assignable() -> None:
    v = wt.WDateValidator()
    v.bottom = datetime.date(2020, 1, 1)
    v.top = datetime.date(2030, 12, 31)
    assert v.bottom == datetime.date(2020, 1, 1)
    assert v.top == datetime.date(2030, 12, 31)


def test_date_validator_is_a_wvalidator() -> None:
    assert isinstance(wt.WDateValidator(), wt.WValidator)


# ---- WTimeValidator --------------------------------------------------------

def test_time_validator_range_round_trip() -> None:
    v = wt.WTimeValidator()
    v.bottom = datetime.time(9, 0)
    v.top = datetime.time(17, 0)
    assert v.bottom == datetime.time(9, 0)
    assert v.top == datetime.time(17, 0)


def test_time_validator_is_a_regexp_validator() -> None:
    """WTimeValidator inherits from WRegExpValidator in Wt (it implements
    its range check via a regex). Verify the inheritance chain works."""
    v = wt.WTimeValidator()
    assert isinstance(v, wt.WRegExpValidator)
    assert isinstance(v, wt.WValidator)


# ---- DateSignal binding (Signal<WDate>) ------------------------------------

def test_date_signal_round_trips_datetime_date() -> None:
    """DateSignal slots receive a `datetime.date` payload via the caster.
    Emit a date from Python; the slot sees a date — full round-trip without
    touching any C++ `Wt::WDate` object in user code."""
    sig = wt.DateSignal()
    seen: list = []
    sig.connect(lambda d: seen.append(d))
    sig.emit(datetime.date(2026, 5, 26))
    sig.emit(datetime.date(2030, 1, 1))
    assert seen == [datetime.date(2026, 5, 26), datetime.date(2030, 1, 1)]


def test_date_signal_no_arg_slot_drops_payload() -> None:
    """Arity introspection still works for DateSignal: a 0-arg slot is
    invoked with no args even though the signal carries a date payload."""
    sig = wt.DateSignal()
    fired = [0]

    def bump() -> None:
        fired[0] += 1

    sig.connect(bump)
    sig.emit(datetime.date(2026, 5, 26))
    sig.emit(datetime.date(2026, 5, 27))
    assert fired[0] == 2
