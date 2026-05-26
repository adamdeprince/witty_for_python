"""WTheme hierarchy suite.

Theme classes are pure-value: no widgets get touched during construction,
no WApplication is required. So we test full construction + accessors.
"""

from __future__ import annotations

import witty_for_python as wt


def test_css_theme_name_round_trip() -> None:
    """WCssTheme takes a name and exposes it via the inherited `name()`
    method. 'polished' and 'default' are Wt's built-in styles."""
    assert wt.WCssTheme("polished").name() == "polished"
    assert wt.WCssTheme("default").name() == "default"


def test_css_theme_arbitrary_name_accepted() -> None:
    """Custom theme names round-trip — Wt doesn't validate against a fixed
    list; it just expects a CSS file at <resources>/themes/<name>/wt.css."""
    assert wt.WCssTheme("my-custom-theme").name() == "my-custom-theme"


def test_bootstrap5_theme_name() -> None:
    assert wt.WBootstrap5Theme().name() == "bootstrap5"


def test_theme_resources_url() -> None:
    """WTheme.resources_url is what the rendered HTML refers to when
    loading the theme's static assets. Default is empty (use the app's
    resources-dir); we just check it returns a string."""
    assert isinstance(wt.WCssTheme("polished").resources_url(), str)
    assert isinstance(wt.WBootstrap5Theme().resources_url(), str)


def test_inheritance_chain() -> None:
    """Both concrete themes inherit WTheme (the abstract base)."""
    assert issubclass(wt.WCssTheme, wt.WTheme)
    assert issubclass(wt.WBootstrap5Theme, wt.WTheme)


def test_wtheme_is_abstract() -> None:
    """The base class is bound non-constructible — concrete subclasses
    are what applications attach via WApplication.theme."""
    import pytest
    with pytest.raises(TypeError):
        wt.WTheme()
