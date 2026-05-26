"""Validator suite.

Covers each concrete validator's:
  - constructor (default and convenience two-arg)
  - range / length / pattern setters as properties
  - validate(text) round-trip with valid + invalid + boundary inputs
  - the `mandatory` flag affecting empty-input handling
  - WStackedValidator composing multiple validators

Validators don't need a WApplication context — they're value types, safe to
construct + exercise directly in unit tests.
"""

from __future__ import annotations

import witty_for_python as wt


# ---- module surface --------------------------------------------------------

def test_validation_state_enum() -> None:
    assert wt.ValidationState.Valid != wt.ValidationState.Invalid
    assert wt.ValidationState.InvalidEmpty != wt.ValidationState.Valid


def test_validation_result_constructible_and_inspectable() -> None:
    r = wt.ValidationResult(wt.ValidationState.Valid, "ok")
    assert r.state == wt.ValidationState.Valid
    assert r.message == "ok"

    # default and state-only constructors
    assert wt.ValidationResult().state == wt.ValidationState.Invalid
    assert wt.ValidationResult(wt.ValidationState.Valid).state == wt.ValidationState.Valid


# ---- WIntValidator ---------------------------------------------------------

def test_int_validator_basic_range() -> None:
    v = wt.WIntValidator(0, 100)
    assert v.validate("42").state == wt.ValidationState.Valid
    assert v.validate("0").state == wt.ValidationState.Valid
    assert v.validate("100").state == wt.ValidationState.Valid
    assert v.validate("-1").state == wt.ValidationState.Invalid
    assert v.validate("101").state == wt.ValidationState.Invalid
    assert v.validate("abc").state == wt.ValidationState.Invalid


def test_int_validator_range_property_setters() -> None:
    v = wt.WIntValidator()
    v.set_range(10, 20)
    assert v.bottom == 10
    assert v.top == 20
    assert v.validate("5").state == wt.ValidationState.Invalid
    assert v.validate("15").state == wt.ValidationState.Valid
    # Direct property setters too
    v.bottom = 0
    v.top = 50
    assert v.validate("25").state == wt.ValidationState.Valid


def test_int_validator_empty_not_mandatory_is_valid() -> None:
    """Default (non-mandatory) validator accepts empty input."""
    v = wt.WIntValidator(0, 100)
    assert v.validate("").state == wt.ValidationState.Valid


def test_int_validator_empty_mandatory_is_invalid_empty() -> None:
    v = wt.WIntValidator(0, 100)
    v.mandatory = True
    assert v.validate("").state == wt.ValidationState.InvalidEmpty


# ---- WDoubleValidator ------------------------------------------------------

def test_double_validator_range() -> None:
    v = wt.WDoubleValidator(0.0, 1.0)
    assert v.validate("0.5").state == wt.ValidationState.Valid
    assert v.validate("1.5").state == wt.ValidationState.Invalid
    assert v.validate("hello").state == wt.ValidationState.Invalid


# ---- WLengthValidator ------------------------------------------------------

def test_length_validator() -> None:
    v = wt.WLengthValidator(3, 10)
    assert v.validate("hi").state == wt.ValidationState.Invalid
    assert v.validate("hello").state == wt.ValidationState.Valid
    assert v.validate("verylongstring").state == wt.ValidationState.Invalid
    # Properties round-trip
    v.minimum_length = 1
    v.maximum_length = 5
    assert v.validate("hi").state == wt.ValidationState.Valid
    assert v.validate("hello").state == wt.ValidationState.Valid
    assert v.validate("hello!").state == wt.ValidationState.Invalid


# ---- WRegExpValidator ------------------------------------------------------

def test_regexp_validator() -> None:
    v = wt.WRegExpValidator(r"^[a-z]+$")
    assert v.validate("hello").state == wt.ValidationState.Valid
    assert v.validate("Hello").state == wt.ValidationState.Invalid
    assert v.validate("hello123").state == wt.ValidationState.Invalid
    # Property round-trip
    v.pattern = r"^\d{3}$"
    assert v.pattern == r"^\d{3}$"
    assert v.validate("123").state == wt.ValidationState.Valid
    assert v.validate("12").state == wt.ValidationState.Invalid


# ---- WEmailValidator -------------------------------------------------------

def test_email_validator_basic() -> None:
    v = wt.WEmailValidator()
    assert v.validate("user@example.com").state == wt.ValidationState.Valid
    assert v.validate("not an email").state == wt.ValidationState.Invalid


def test_email_validator_multiple_flag() -> None:
    v = wt.WEmailValidator()
    assert v.multiple is False
    v.multiple = True
    assert v.multiple is True
    # When multiple=True Wt accepts comma-separated emails
    assert v.validate("a@b.com,c@d.com").state == wt.ValidationState.Valid


# ---- WStackedValidator -----------------------------------------------------

def test_stacked_validator_combines_validators() -> None:
    v = wt.WStackedValidator()
    v.add_validator(wt.WLengthValidator(5, 50))
    v.add_validator(wt.WRegExpValidator(r"^[a-z]+$"))
    assert v.size == 2
    # Valid: passes both
    assert v.validate("hello").state == wt.ValidationState.Valid
    # Fails length
    assert v.validate("hi").state == wt.ValidationState.Invalid
    # Fails regex
    assert v.validate("HELLO").state == wt.ValidationState.Invalid


def test_stacked_validator_clear() -> None:
    v = wt.WStackedValidator()
    v.add_validator(wt.WIntValidator(0, 100))
    assert v.size == 1
    v.clear()
    assert v.size == 0


# ---- WValidator base flags -------------------------------------------------

def test_invalid_blank_text_round_trip() -> None:
    v = wt.WIntValidator()
    v.invalid_blank_text = "please enter a number"
    assert v.invalid_blank_text == "please enter a number"


def test_validator_subclass_inheritance() -> None:
    """Every concrete validator IS-A WValidator (for shared_ptr<WValidator>)."""
    for cls in (
        wt.WIntValidator, wt.WDoubleValidator, wt.WLengthValidator,
        wt.WRegExpValidator, wt.WEmailValidator, wt.WStackedValidator,
    ):
        v = cls()
        assert isinstance(v, wt.WValidator), f"{cls.__name__} not a WValidator"
