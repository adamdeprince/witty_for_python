"""Misc UI: WIcon, WIconPair, WPopupWidget, WNotification,
WLoadingIndicator family + the new JSignal0 type.

WIcon / WIconPair / WPopupWidget / loading indicators all touch
WApplication::instance() in their constructors so we only check the
binding surface; the gallery boot test exercises real instantiation in
a session. WNotification is constructible standalone (it's a WObject,
not a widget).
"""

from __future__ import annotations

import pytest
import witty_for_python as wt


# ---- JSignal0 -------------------------------------------------------------

def test_jsignal0_exposed_and_signal_shape() -> None:
    assert isinstance(wt.JSignal0, type)
    assert hasattr(wt.JSignal0, "connect")
    assert hasattr(wt.JSignal0, "disconnect_all_slots")


# ---- Inheritance ----------------------------------------------------------

@pytest.mark.parametrize("cls,base", [
    (wt.WIcon,                      wt.WInteractWidget),
    (wt.WIconPair,                  wt.WWidget),
    (wt.WPopupWidget,               wt.WWidget),
    (wt.WLoadingIndicator,          wt.WWidget),
    (wt.WDefaultLoadingIndicator,   wt.WLoadingIndicator),
    (wt.WOverlayLoadingIndicator,   wt.WLoadingIndicator),
    (wt.WNotification,              wt.WObject),
])
def test_misc_ui_inheritance(cls: type, base: type) -> None:
    assert issubclass(cls, base)


# ---- Method surface -------------------------------------------------------

@pytest.mark.parametrize("cls,attr", [
    (wt.WIcon,         "name"),
    (wt.WIcon,         "size"),
    (wt.WIcon,         "load_icon_font"),
    (wt.WIconPair,     "state"),
    (wt.WIconPair,     "show_icon1"),
    (wt.WIconPair,     "show_icon2"),
    (wt.WIconPair,     "icon1_clicked"),
    (wt.WIconPair,     "icon2_clicked"),
    (wt.WPopupWidget,  "set_anchor_widget"),
    (wt.WPopupWidget,  "transient"),
    (wt.WPopupWidget,  "set_transient"),
    (wt.WPopupWidget,  "hidden_signal"),
    (wt.WPopupWidget,  "shown_signal"),
    (wt.WNotification, "set_title"),
    (wt.WNotification, "set_body"),
    (wt.WNotification, "set_icon"),
    (wt.WNotification, "set_badge"),
    (wt.WNotification, "send"),
    (wt.WNotification, "close"),
    (wt.WNotification, "clicked"),
    (wt.WNotification, "closed"),
    (wt.WNotification, "shown"),
    (wt.WNotification, "error"),
    (wt.WNotification, "silent"),
    (wt.WNotification, "require_interaction"),
    (wt.WLoadingIndicator, "set_message"),
])
def test_misc_ui_attribute_present(cls: type, attr: str) -> None:
    assert hasattr(cls, attr), f"{cls.__name__} missing: {attr}"


# ---- WNotification (constructible without a session) ----------------------

def test_wnotification_default_construct() -> None:
    n = wt.WNotification()
    # No accessor for title/body — just confirm construction succeeds.
    assert n is not None


def test_wnotification_construct_with_title_and_body() -> None:
    n = wt.WNotification("Heads up", "Something happened.")
    assert n is not None


def test_wnotification_silent_round_trip() -> None:
    n = wt.WNotification()
    n.silent = True
    assert n.silent is True
    n.silent = False
    assert n.silent is False


def test_wnotification_permission_enum_members() -> None:
    for name in ("Default", "Granted", "Denied"):
        assert hasattr(wt.NotificationPermission, name)


# ---- IconType enum --------------------------------------------------------

def test_icon_type_enum_members() -> None:
    assert wt.IconType.URI != wt.IconType.IconName
