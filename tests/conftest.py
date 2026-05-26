"""Shared fixtures.

Every test starts with the C++ connection registry cleared so
`_live_connection_count()` reflects only what the test itself opens.
"""

from __future__ import annotations

import os
import socket
from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _fresh_connection_registry() -> Iterator[None]:
    """Flush the process-wide connection registry around each test.

    The registry is global C++ state. Without this, connections opened by
    earlier tests linger as detached entries and skew `_live_connection_count`.
    """
    import witty_for_python as wt

    wt._cleanup_signal_slots()
    yield
    wt._cleanup_signal_slots()


@pytest.fixture
def wt_resources_dir() -> Path:
    """Path to Wt's static resources (CSS, JS, themes).

    Resolves to the resources directory the wheel bundles alongside the
    extension — `witty_for_python.resources_dir`. No external install needed.
    """
    import witty_for_python as wt

    path = Path(wt.resources_dir)
    if not path.is_dir():
        pytest.skip(
            f"Bundled Wt resources missing at {path} — rebuild with "
            "`pip install --no-build-isolation -e .`"
        )
    return path


@pytest.fixture
def free_port() -> int:
    """Pick an ephemeral TCP port that's currently free.

    Race-prone in theory (something could grab the port between this call
    and the server bind), but fine in practice for a quiet test run.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def docroot(tmp_path: Path) -> Path:
    """A throwaway docroot for the wthttpd server. Wt requires the dir to exist."""
    d = tmp_path / "docroot"
    d.mkdir()
    return d
