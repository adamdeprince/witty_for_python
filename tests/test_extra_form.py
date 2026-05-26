"""WColor + WColorPicker + WPasswordEdit + WInPlaceEdit + WSuggestionPopup
+ WTextEdit suite.

The widgets among these (everything except WColor and the Options struct)
have constructors that touch WApplication::instance(), so we can't
instantiate them outside a session. The gallery boot test covers
construction + signal wiring inside a live session; here we verify the
binding surface and exercise the standalone-constructible value types.
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- WColor (full value type — constructible without a session) ----

def test_wcolor_default() -> None:
    c = wt.WColor()
    assert c.is_default is True


def test_wcolor_rgb_ctor() -> None:
    c = wt.WColor(160, 192, 224)
    assert c.red == 160
    assert c.green == 192
    assert c.blue == 224
    assert c.alpha == 255      # default
    assert c.is_default is False


def test_wcolor_rgba_ctor() -> None:
    c = wt.WColor(10, 20, 30, 64)
    assert c.alpha == 64


def test_wcolor_from_hex_name() -> None:
    """The CSS-name constructor parses #rrggbb to component values."""
    c = wt.WColor("#a0c0e0")
    assert c.red == 0xa0
    assert c.green == 0xc0
    assert c.blue == 0xe0


def test_wcolor_set_rgb_mutator() -> None:
    c = wt.WColor()
    c.set_rgb(255, 128, 0, 200)
    assert c.red == 255
    assert c.green == 128
    assert c.blue == 0
    assert c.alpha == 200


def test_wcolor_set_name_resets_rgb() -> None:
    """`setName` stores the CSS name *without* parsing it — RGB components
    revert to the 'not available' state (red/green/blue == 0 in our caster,
    and the stored name is what Wt uses when rendering CSS). To get parsed
    RGB from a hex name, construct a new WColor instead."""
    c = wt.WColor(10, 20, 30)
    c.set_name("#ff8000")
    # Constructor would have parsed; setName doesn't. So we check the side
    # effect — set_name dropped the previously-set RGB.
    assert c.red == 0
    assert c.green == 0
    assert c.blue == 0
    # If parsed components are wanted, recreate:
    parsed = wt.WColor("#ff8000")
    assert parsed.red == 0xff
    assert parsed.green == 0x80


# ---- PopupTrigger enum ----

def test_popup_trigger_members() -> None:
    assert wt.PopupTrigger.Editing != wt.PopupTrigger.DropDownIcon


# ---- WSuggestionPopup.Options (constructible, standalone) ----

def test_options_default_construct() -> None:
    opts = wt.WSuggestionPopup.Options()
    # Default constructor zero-initialises everything; list_separator is
    # the no-list-mode sentinel '\\0', surfaced as "" via the str caster.
    assert opts.list_separator == ""
    assert opts.highlight_begin_tag == ""
    assert opts.whitespace == ""


def test_options_fields_round_trip() -> None:
    opts = wt.WSuggestionPopup.Options()
    opts.highlight_begin_tag = "<b>"
    opts.highlight_end_tag = "</b>"
    opts.whitespace = " \n"
    opts.word_separators = " ."
    opts.append_replaced_text = ", "
    opts.list_separator = ","
    opts.word_start_regexp = r"\\s"
    assert opts.highlight_begin_tag == "<b>"
    assert opts.highlight_end_tag == "</b>"
    assert opts.whitespace == " \n"
    assert opts.word_separators == " ."
    assert opts.append_replaced_text == ", "
    assert opts.list_separator == ","
    assert opts.word_start_regexp == r"\\s"


def test_options_list_separator_empty_means_no_list() -> None:
    """Setting list_separator = '' restores the no-list-mode sentinel."""
    opts = wt.WSuggestionPopup.Options()
    opts.list_separator = ","
    opts.list_separator = ""
    assert opts.list_separator == ""


# ---- Class binding surface (widgets — no instantiation) ----

@pytest.mark.parametrize("cls,base", [
    (wt.WPasswordEdit, wt.WLineEdit),
    (wt.WColorPicker, wt.WFormWidget),
    (wt.WTextEdit, wt.WTextArea),
    (wt.WInPlaceEdit, wt.WWidget),
    (wt.WSuggestionPopup, wt.WWidget),
])
def test_widget_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base), f"{cls.__name__} must extend {base.__name__}"


@pytest.mark.parametrize("cls,attr", [
    (wt.WPasswordEdit, "min_length"),
    (wt.WPasswordEdit, "required"),
    (wt.WPasswordEdit, "pattern"),
    (wt.WPasswordEdit, "invalid_too_short_text"),
    (wt.WPasswordEdit, "invalid_no_match_text"),
    (wt.WPasswordEdit, "invalid_blank_text"),
    (wt.WPasswordEdit, "native_control"),
    (wt.WColorPicker, "color"),
    (wt.WColorPicker, "color_input"),
    (wt.WInPlaceEdit, "text"),
    (wt.WInPlaceEdit, "placeholder_text"),
    (wt.WInPlaceEdit, "line_edit"),
    (wt.WInPlaceEdit, "value_changed"),
    (wt.WInPlaceEdit, "set_buttons_enabled"),
    (wt.WSuggestionPopup, "for_edit"),
    (wt.WSuggestionPopup, "remove_edit"),
    (wt.WSuggestionPopup, "add_suggestion"),
    (wt.WSuggestionPopup, "clear_suggestions"),
    (wt.WSuggestionPopup, "filter_length"),
    (wt.WSuggestionPopup, "default_index"),
    (wt.WSuggestionPopup, "activated"),
    (wt.WTextEdit, "version"),
    (wt.WTextEdit, "style_sheet"),
    (wt.WTextEdit, "set_extra_plugins"),
    (wt.WTextEdit, "set_tool_bar"),
    (wt.WTextEdit, "set_configuration_setting"),
])
def test_widget_attribute_present(cls: type, attr: str) -> None:
    assert hasattr(cls, attr), f"{cls.__name__} missing: {attr}"


def test_int_form_widget_signal_is_exposed_via_module() -> None:
    """The Signal<int, WFormWidget*> type used by WSuggestionPopup.activated
    is bound at module scope as IntFormWidgetSignal. Reachable via the C++
    extension; we expose it for type checks and explicit references."""
    import witty_for_python._witty_for_python as ext
    assert hasattr(ext, "IntFormWidgetSignal")
    cls = ext.IntFormWidgetSignal
    assert hasattr(cls, "connect")
    assert hasattr(cls, "disconnect_all_slots")
