"""WLength + WAnimation value-type suites.

These are pure value types — no widget instantiation, no WApplication
required — so we exercise them fully.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- LengthUnit enum -------------------------------------------------------

def test_length_unit_members_distinct() -> None:
    """Every unit in Wt's enum is bound and distinct from its neighbours."""
    for a, b in [
        (wt.LengthUnit.Pixel,          wt.LengthUnit.FontEm),
        (wt.LengthUnit.Percentage,     wt.LengthUnit.Pixel),
        (wt.LengthUnit.Inch,           wt.LengthUnit.Centimeter),
        (wt.LengthUnit.ViewportWidth,  wt.LengthUnit.ViewportHeight),
    ]:
        assert a != b


# ---- WLength ---------------------------------------------------------------

def test_wlength_default_is_auto() -> None:
    """Default-constructed WLength represents 'auto' — Wt's sentinel for
    'no explicit length'."""
    assert wt.WLength().is_auto is True


def test_wlength_value_unit_round_trip() -> None:
    px = wt.WLength(120, wt.LengthUnit.Pixel)
    assert px.value == 120
    assert px.unit == wt.LengthUnit.Pixel
    assert px.is_auto is False


def test_wlength_default_unit_is_pixel() -> None:
    """The single-arg numeric constructor defaults the unit to Pixel."""
    assert wt.WLength(50).unit == wt.LengthUnit.Pixel


def test_wlength_css_text() -> None:
    """to_css_text renders the form Wt's renderer hands to the browser."""
    assert wt.WLength(50, wt.LengthUnit.Pixel).to_css_text() == "50.0px"
    assert wt.WLength(50, wt.LengthUnit.Percentage).to_css_text() == "50.0%"


def test_wlength_parse_css() -> None:
    """The string constructor parses CSS lengths."""
    assert wt.WLength("auto").is_auto is True

    p = wt.WLength("50%")
    assert p.value == 50.0
    assert p.unit == wt.LengthUnit.Percentage


def test_wlength_to_pixels_with_em() -> None:
    """1em with default font_size=16 ⇒ 16 pixels."""
    em = wt.WLength(1, wt.LengthUnit.FontEm)
    assert em.to_pixels() == pytest.approx(16.0)
    assert em.to_pixels(font_size=24) == pytest.approx(24.0)


def test_wlength_repr() -> None:
    assert repr(wt.WLength()) == "WLength(auto)"


# ---- AnimationEffect / TimingFunction --------------------------------------

def test_animation_effect_members() -> None:
    for name in ("SlideInFromLeft", "SlideInFromRight", "SlideInFromBottom",
                 "SlideInFromTop", "Pop", "Fade"):
        assert hasattr(wt.AnimationEffect, name)


def test_timing_function_members() -> None:
    for name in ("Ease", "Linear", "EaseIn", "EaseOut", "EaseInOut",
                 "CubicBezier"):
        assert hasattr(wt.TimingFunction, name)


# ---- WAnimation ------------------------------------------------------------

def test_wanimation_default_is_empty() -> None:
    """Default-constructed WAnimation is empty — used as 'no transition'."""
    assert wt.WAnimation().empty is True


def test_wanimation_single_effect_construct() -> None:
    a = wt.WAnimation(int(wt.AnimationEffect.Fade),
                     wt.TimingFunction.EaseIn, 500)
    assert a.duration == 500
    assert a.timing_function == wt.TimingFunction.EaseIn
    assert a.empty is False


def test_wanimation_combine_effects_via_or() -> None:
    """AnimationEffect is bound is_arithmetic so callers OR bits to combine
    (typical: a slide + a fade)."""
    combined = int(wt.AnimationEffect.SlideInFromLeft) | int(wt.AnimationEffect.Fade)
    a = wt.WAnimation(combined)
    assert a.empty is False


def test_wanimation_set_duration() -> None:
    a = wt.WAnimation(int(wt.AnimationEffect.Pop))
    a.duration = 1234
    assert a.duration == 1234


def test_wanimation_set_timing() -> None:
    a = wt.WAnimation(int(wt.AnimationEffect.Pop))
    a.timing_function = wt.TimingFunction.EaseOut
    assert a.timing_function == wt.TimingFunction.EaseOut
