"""TinyMCE is bundled with the wheel and reachable at the path Wt
expects.

Wt's WTextEdit walks the configured `tinyMCEURL` / `tinyMCEBaseURL` plus
the default `tinymce/` folder under `relativeResourcesUrl()` to find
TinyMCE assets — for our wheel that resolves to
``<package>/_wt_resources/tinymce/``. These tests just confirm the
expected files are in that path so a user's first run of `WTextEdit`
finds them.

Disabled when ``WITTY_FOR_PYTHON_BUILD_TINYMCE=OFF`` was used at build time
(see CMakeLists.txt) — but we don't have a runtime flag for that, so the
test simply skips if the bundle is missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import witty_for_python as wt


TINYMCE_DIR = Path(wt.resources_dir) / "tinymce"

skip_unless_built = pytest.mark.skipif(
    not TINYMCE_DIR.exists(),
    reason="TinyMCE wasn't built (WITTY_FOR_PYTHON_BUILD_TINYMCE=OFF).",
)


@skip_unless_built
def test_tinymce_directory_exists() -> None:
    """The bundle landed at <resources>/tinymce/, which is the default
    Wt asks Wt::WTextEdit to look in."""
    assert TINYMCE_DIR.is_dir()


@skip_unless_built
def test_tinymce_min_js_present() -> None:
    """`tinymce.min.js` is the canonical entry point Wt loads from
    JavaScript."""
    f = TINYMCE_DIR / "tinymce.min.js"
    assert f.is_file()
    # The minified bundle is hundreds of KB — sanity-check that we didn't
    # somehow ship an empty placeholder.
    assert f.stat().st_size > 100_000


@skip_unless_built
def test_tinymce_supporting_dirs_present() -> None:
    """A working TinyMCE install needs models/themes/skins/plugins
    alongside the core JS."""
    for sub in ("models", "themes", "skins", "plugins", "icons"):
        assert (TINYMCE_DIR / sub).is_dir(), f"missing TinyMCE subtree: {sub}"


@skip_unless_built
def test_tinymce_license_bundled() -> None:
    """The MIT license text rides along with the binary inside the wheel —
    required for attribution and matched up against
    THIRD_PARTY_LICENSES.md."""
    license_file = TINYMCE_DIR / "license.txt"
    assert license_file.is_file()
    text = license_file.read_text(encoding="utf-8", errors="replace")
    assert "MIT" in text
