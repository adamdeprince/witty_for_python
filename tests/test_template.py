"""WTemplate suite.

WTemplate is unusual among Wt widgets in that its purely-data operations
(setting the template text, binding strings/ints, evaluating conditions)
work *without* a WApplication context — they don't touch the per-session
state. Widget-binding paths do still need the application, so we exercise
that in the gallery boot test.
"""

from __future__ import annotations

import witty_for_python as wt


# ---- enums ----------------------------------------------------------------

def test_text_format_enum() -> None:
    assert wt.TextFormat.XHTML != wt.TextFormat.Plain
    assert wt.TextFormat.UnsafeXHTML != wt.TextFormat.XHTML


def test_template_widget_id_mode_enum() -> None:
    # `None` is reserved in Python; bound as `None_` per project convention.
    assert wt.TemplateWidgetIdMode.None_ != wt.TemplateWidgetIdMode.SetId


# ---- template text + property round-trip ----------------------------------

def test_template_text_round_trip() -> None:
    t = wt.WTemplate("Hello ${name}")
    assert t.template_text == "Hello ${name}"
    t.template_text = "Goodbye ${name}"
    assert t.template_text == "Goodbye ${name}"


def test_template_text_default_empty() -> None:
    t = wt.WTemplate()
    assert t.template_text == ""


def test_set_template_text_with_format() -> None:
    """set_template_text takes an optional format. Plain-text format escapes
    HTML, so the literal `${name}` stays as a literal, not a placeholder."""
    t = wt.WTemplate()
    t.set_template_text("Hello ${name}", wt.TextFormat.Plain)
    assert t.template_text == "Hello ${name}"


# ---- bind_string / bind_int -----------------------------------------------

def test_bind_string_and_int_dont_throw() -> None:
    """Pure data-binding paths run without a WApplication.

    Templates accumulate (name → value) bindings; verification that the
    bindings *render* correctly requires an active session and is covered
    by the gallery boot test."""
    t = wt.WTemplate("${greeting}, ${count} items")
    t.bind_string("greeting", "hello")
    t.bind_int("count", 42)
    # No exception = success
    t.bind_string("greeting", "renamed")  # rebinds previous value
    t.bind_empty("count")                 # removes the previous int


def test_bind_string_accepts_format() -> None:
    t = wt.WTemplate("${x}")
    t.bind_string("x", "<b>bold</b>", wt.TextFormat.Plain)
    t.bind_string("x", "<b>bold</b>", wt.TextFormat.XHTML)
    t.bind_string("x", "<b>bold</b>", wt.TextFormat.UnsafeXHTML)


# ---- conditions -----------------------------------------------------------

def test_condition_default_false() -> None:
    t = wt.WTemplate("${<if-x>}yes${</if-x>}")
    assert t.condition_value("x") is False


def test_condition_set_and_read() -> None:
    t = wt.WTemplate("${<if-x>}yes${</if-x>}")
    t.set_condition("x", True)
    assert t.condition_value("x") is True
    t.set_condition("x", False)
    assert t.condition_value("x") is False


# ---- widget_id_mode property ----------------------------------------------

def test_widget_id_mode_default_is_none() -> None:
    t = wt.WTemplate()
    assert t.widget_id_mode == wt.TemplateWidgetIdMode.None_


def test_widget_id_mode_assignable() -> None:
    t = wt.WTemplate()
    t.widget_id_mode = wt.TemplateWidgetIdMode.SetObjectName
    assert t.widget_id_mode == wt.TemplateWidgetIdMode.SetObjectName


# ---- class surface --------------------------------------------------------

def test_template_is_a_winteract_widget() -> None:
    """WTemplate inherits WInteractWidget upstream; so a `set_validator`
    couldn't accept it but `add_widget` on a container can. We check the
    class hierarchy only — actually *using* the inherited signals like
    `.clicked` requires an app context (covered by the gallery boot test)."""
    t = wt.WTemplate()
    assert isinstance(t, wt.WInteractWidget)
