"""Confirm type stubs ship alongside the package.

A binary extension on its own gives type checkers nothing — every
attribute looks like `Unknown`. The stubs at
`src/witty_for_python/_witty_for_python/*.pyi` + the `py.typed` marker
turn that into a fully-typed surface. These tests just verify the
files are reachable and that the marker is present.

A separate `scripts/regenerate_stubs.py --check` invocation (run from
CI) catches drift between bindings and committed stubs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import witty_for_python


PKG_ROOT = Path(witty_for_python.__file__).resolve().parent
EXT_STUBS = PKG_ROOT / "_witty_for_python"


def test_py_typed_marker_present() -> None:
    """PEP 561: type checkers only consult `.pyi` files in a package
    when the package ships a `py.typed` marker (or is a `*-stubs`
    package). Without this file, all our work would be invisible."""
    assert (PKG_ROOT / "py.typed").is_file()


@pytest.mark.parametrize("name", ["__init__.pyi", "chart.pyi", "Json.pyi", "Http.pyi"])
def test_extension_stub_present(name: str) -> None:
    """Three stub files cover the bindings: the main module plus the
    chart and Json submodules created via def_submodule()."""
    path = EXT_STUBS / name
    assert path.is_file(), f"missing stub: {path}"
    # Sanity: file isn't empty / stub-skeleton.
    assert path.stat().st_size > 1_000


def test_stubs_contain_core_classes() -> None:
    """Spot-check that the generated stubs declare a few load-bearing
    classes — guards against an accidentally-zeroed regeneration."""
    main = (EXT_STUBS / "__init__.pyi").read_text(encoding="utf-8")
    for cls in ("WPushButton", "WApplication", "WStandardItemModel",
                "WPaintedWidget", "WLeafletMap"):
        assert f"class {cls}" in main, f"{cls} missing from stub"


def test_chart_stub_contains_chart_classes() -> None:
    chart = (EXT_STUBS / "chart.pyi").read_text(encoding="utf-8")
    for cls in ("WCartesianChart", "WPieChart", "WAxis", "WDataSeries"):
        assert f"class {cls}" in chart, f"{cls} missing from chart stub"


def test_json_stub_contains_json_classes() -> None:
    j = (EXT_STUBS / "Json.pyi").read_text(encoding="utf-8")
    for cls in ("Object", "Array", "Value"):
        assert f"class {cls}" in j, f"{cls} missing from Json stub"


def test_http_stub_contains_http_classes() -> None:
    h = (EXT_STUBS / "Http.pyi").read_text(encoding="utf-8")
    for cls in ("Request", "Response", "Message", "Client", "Header"):
        assert f"class {cls}" in h, f"{cls} missing from Http stub"
